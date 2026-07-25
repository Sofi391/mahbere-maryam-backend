import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Member, Meeting, Attendance, Contribution, Penalty, PenaltyRule, Expense, Announcement, ManualPayment
from .permissions import IsStaffAndAuthenticated
from .serializers import (
    MemberSerializer, MemberListSerializer, MemberDetailSerializer,
    MeetingSerializer,
    AttendanceSerializer, BulkAttendanceSerializer,
    ContributionSerializer, BulkContributionSerializer,
    PenaltySerializer, PenaltyRuleSerializer,
    ExpenseSerializer,
    AnnouncementSerializer,
    ManualPaymentSerializer,
    MonthlyReportSerializer, YearlyReportSerializer,
)
from .services.member_service import (
    get_active_members, get_all_members,
    get_paid_member_ids_for_meeting,
    deactivate_member, reactivate_member,
)
from .services.attendance_service import bulk_record_attendance
from .services.contribution_service import bulk_record_contributions, initialize_contributions_for_meeting
from .services.penalty_service import mark_penalty_paid
from .services.report_service import get_monthly_report, get_yearly_report, get_dashboard_summary

logger = logging.getLogger('mahberapp')


def _latest_meeting():
    return Meeting.objects.order_by('-date').first()


# ─── Members ──────────────────────────────────────────────────────────────────

class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return MemberListSerializer
        if self.action == 'retrieve':
            return MemberDetailSerializer
        return MemberSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if self.request.user and self.request.user.is_authenticated and self.request.user.is_staff:
            return get_all_members(search)
        return get_active_members(search)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == 'list':
            context['paid_member_ids'] = get_paid_member_ids_for_meeting(_latest_meeting())
        return context

    @action(detail=True, methods=['patch'], permission_classes=[IsStaffAndAuthenticated])
    def deactivate(self, request, pk=None):
        member = self.get_object()
        try:
            deactivate_member(member)
            logger.info('Member %s deactivated by %s', member.id, request.user)
        except Exception:
            logger.exception('Failed to deactivate member %s', pk)
            return Response({'detail': 'Failed to deactivate member.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': f'{member.full_name} deactivated.'})

    @action(detail=True, methods=['patch'], permission_classes=[IsStaffAndAuthenticated])
    def reactivate(self, request, pk=None):
        member = self.get_object()
        try:
            reactivate_member(member)
            logger.info('Member %s reactivated by %s', member.id, request.user)
        except Exception:
            logger.exception('Failed to reactivate member %s', pk)
            return Response({'detail': 'Failed to reactivate member.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': f'{member.full_name} reactivated.'})


# ─── Meetings ─────────────────────────────────────────────────────────────────

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all().order_by('-date')
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def latest(self, request):
        meeting = _latest_meeting()
        if not meeting:
            return Response({'detail': 'No meetings yet.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MeetingSerializer(meeting).data)


# ─── Attendance ───────────────────────────────────────────────────────────────

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Attendance.objects.select_related('member', 'meeting').all()
        member_id = self.request.query_params.get('member')
        meeting_id = self.request.query_params.get('meeting')
        if member_id:
            qs = qs.filter(member_id=member_id)
        if meeting_id:
            qs = qs.filter(meeting_id=meeting_id)
        return qs

    @action(detail=False, methods=['post'], permission_classes=[IsStaffAndAuthenticated])
    def bulk_record(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.validated_data['meeting']
        try:
            result = bulk_record_attendance(meeting, serializer.validated_data['records'])
            logger.info('Bulk attendance recorded for meeting %s by %s', meeting.id, request.user)
        except Exception:
            logger.exception('Bulk attendance failed for meeting %s', meeting.id)
            return Response({'detail': 'Failed to record attendance.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': f"{result['created']} created, {result['updated']} updated for {meeting}."})


# ─── Contributions ────────────────────────────────────────────────────────────

class ContributionViewSet(viewsets.ModelViewSet):
    serializer_class = ContributionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Contribution.objects.select_related('member', 'meeting').all()
        member_id = self.request.query_params.get('member')
        meeting_id = self.request.query_params.get('meeting')
        is_paid = self.request.query_params.get('is_paid')
        if member_id:
            qs = qs.filter(member_id=member_id)
        if meeting_id:
            qs = qs.filter(meeting_id=meeting_id)
        if is_paid is not None:
            qs = qs.filter(is_paid=is_paid.lower() == 'true')
        return qs

    @action(detail=False, methods=['post'], permission_classes=[IsStaffAndAuthenticated])
    def bulk_record(self, request):
        serializer = BulkContributionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.validated_data['meeting']
        try:
            result = bulk_record_contributions(meeting, serializer.validated_data['records'])
            logger.info('Bulk contributions recorded for meeting %s by %s', meeting.id, request.user)
        except Exception:
            logger.exception('Bulk contributions failed for meeting %s', meeting.id)
            return Response({'detail': 'Failed to record contributions.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': f"{result['created']} created, {result['updated']} updated for {meeting}."})

    @action(detail=False, methods=['post'], permission_classes=[IsStaffAndAuthenticated])
    def initialize_for_meeting(self, request):
        meeting_id = request.data.get('meeting')
        if not meeting_id:
            return Response({'detail': 'meeting is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            meeting = Meeting.objects.get(id=meeting_id)
            count = initialize_contributions_for_meeting(meeting)
            logger.info('Initialized %d contributions for meeting %s by %s', count, meeting_id, request.user)
        except Meeting.DoesNotExist:
            return Response({'detail': 'Meeting not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception('Failed to initialize contributions for meeting %s', meeting_id)
            return Response({'detail': 'Failed to initialize contributions.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': f'{count} contribution records initialized for {meeting}.'})


# ─── Penalties ────────────────────────────────────────────────────────────────

class PenaltyViewSet(viewsets.ModelViewSet):
    serializer_class = PenaltySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Penalty.objects.select_related('member', 'meeting').all()
        member_id = self.request.query_params.get('member')
        meeting_id = self.request.query_params.get('meeting')
        is_paid = self.request.query_params.get('is_paid')
        if member_id:
            qs = qs.filter(member_id=member_id)
        if meeting_id:
            qs = qs.filter(meeting_id=meeting_id)
        if is_paid is not None:
            qs = qs.filter(is_paid=is_paid.lower() == 'true')
        return qs

    @action(detail=True, methods=['patch'], permission_classes=[IsStaffAndAuthenticated])
    def mark_paid(self, request, pk=None):
        penalty = self.get_object()
        try:
            updated = mark_penalty_paid(penalty, paid_date=request.data.get('paid_date'))
            logger.info('Penalty %s marked paid by %s', pk, request.user)
        except Exception:
            logger.exception('Failed to mark penalty %s as paid', pk)
            return Response({'detail': 'Failed to mark penalty as paid.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(PenaltySerializer(updated).data)


# ─── Penalty Rules ────────────────────────────────────────────────────────────

class PenaltyRuleViewSet(viewsets.ModelViewSet):
    queryset = PenaltyRule.objects.all()
    serializer_class = PenaltyRuleSerializer
    permission_classes = [IsStaffAndAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active(self, request):
        rule = PenaltyRule.get_active()
        return Response(PenaltyRuleSerializer(rule).data)


# ─── Expenses ─────────────────────────────────────────────────────────────────

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Expense.objects.select_related('meeting').all()
        meeting_id = self.request.query_params.get('meeting')
        if meeting_id:
            qs = qs.filter(meeting_id=meeting_id)
        return qs


# ─── Announcements ────────────────────────────────────────────────────────────

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Announcement.objects.all().order_by('-created_at')
        return Announcement.objects.filter(is_published=True).order_by('-created_at')


# ─── Manual Payments ───────────────────────────────────────────────────────────

class ManualPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = ManualPaymentSerializer
    permission_classes = [IsStaffAndAuthenticated]

    def get_queryset(self):
        return ManualPayment.objects.select_related('meeting').order_by('-date')


# ─── Reports ──────────────────────────────────────────────────────────────────

class MonthlyReportView(APIView):
    permission_classes = [IsStaffAndAuthenticated]

    def get(self, request, meeting_id):
        try:
            meeting = Meeting.objects.get(id=meeting_id)
            data = get_monthly_report(meeting)
        except Meeting.DoesNotExist:
            return Response({'detail': 'Meeting not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception('Monthly report failed for meeting %s', meeting_id)
            return Response({'detail': 'Failed to generate report.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(MonthlyReportSerializer(data).data)


class YearlyReportView(APIView):
    permission_classes = [IsStaffAndAuthenticated]

    def get(self, request, ethiopian_year):
        try:
            if not Meeting.objects.filter(ethiopian_year=ethiopian_year).exists():
                return Response(
                    {'detail': f'No meetings found for Ethiopian year {ethiopian_year}.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            data = get_yearly_report(ethiopian_year)
        except Exception:
            logger.exception('Yearly report failed for year %s', ethiopian_year)
            return Response({'detail': 'Failed to generate report.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(YearlyReportSerializer(data).data)


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    permission_classes = [IsStaffAndAuthenticated]

    def get(self, request):
        try:
            latest_meeting = _latest_meeting()
            data = get_dashboard_summary(latest_meeting)
            data['latest_meeting'] = MeetingSerializer(latest_meeting).data if latest_meeting else None
        except Exception:
            logger.exception('Dashboard summary failed')
            return Response({'detail': 'Failed to load dashboard.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data)
