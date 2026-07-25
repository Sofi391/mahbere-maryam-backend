from rest_framework import serializers
from .models import Member, Meeting, Attendance, Contribution, Penalty, PenaltyRule, Expense, Announcement, ManualPayment


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'full_name', 'phone', 'join_date', 'is_active', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class MemberListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (home page + admin members table)."""
    paid_this_month = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'full_name', 'phone', 'join_date', 'is_active', 'paid_this_month']

    def get_paid_this_month(self, obj):
        paid_ids = self.context.get('paid_member_ids', set())
        return obj.id in paid_ids


# ─── Meeting ──────────────────────────────────────────────────────────────────

class MeetingSerializer(serializers.ModelSerializer):
    ethiopian_month_name = serializers.ReadOnlyField()

    class Meta:
        model = Meeting
        fields = ['id', 'date', 'ethiopian_month', 'ethiopian_month_name', 'ethiopian_year', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at', 'ethiopian_month_name']


# ─── Attendance ───────────────────────────────────────────────────────────────

class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.ReadOnlyField(source='member.full_name')
    meeting_label = serializers.ReadOnlyField(source='meeting.__str__')

    class Meta:
        model = Attendance
        fields = ['id', 'member', 'member_name', 'meeting', 'meeting_label', 'status', 'notes', 'recorded_at']
        read_only_fields = ['id', 'recorded_at', 'member_name', 'meeting_label']


class BulkAttendanceSerializer(serializers.Serializer):
    """
    Records attendance for multiple members in one request.
    Expected payload:
    {
        "meeting": 1,
        "records": [
            {"member": 1, "status": "present"},
            {"member": 2, "status": "late"},
            ...
        ]
    }
    """
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())
    records = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )

    def validate_records(self, records):
        valid_statuses = [s[0] for s in Attendance.STATUS_CHOICES]
        for record in records:
            if 'member' not in record or 'status' not in record:
                raise serializers.ValidationError("Each record must have 'member' and 'status'.")
            if record['status'] not in valid_statuses:
                raise serializers.ValidationError(f"Invalid status: {record['status']}")
        return records


# ─── Contribution ─────────────────────────────────────────────────────────────

class ContributionSerializer(serializers.ModelSerializer):
    member_name = serializers.ReadOnlyField(source='member.full_name')
    meeting_label = serializers.ReadOnlyField(source='meeting.__str__')

    class Meta:
        model = Contribution
        fields = ['id', 'member', 'member_name', 'meeting', 'meeting_label',
                  'amount', 'is_paid', 'paid_date', 'notes', 'recorded_at', 'updated_at']
        read_only_fields = ['id', 'recorded_at', 'updated_at', 'member_name', 'meeting_label']


class BulkContributionSerializer(serializers.Serializer):
    """
    Mark multiple members as paid for a meeting in one shot.
    {
        "meeting": 1,
        "records": [
            {"member": 1, "amount": 30, "paid_date": "2024-01-15"},
            ...
        ]
    }
    """
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())
    records = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )


# ─── Penalty ──────────────────────────────────────────────────────────────────

class PenaltySerializer(serializers.ModelSerializer):
    member_name = serializers.ReadOnlyField(source='member.full_name')
    meeting_label = serializers.ReadOnlyField(source='meeting.__str__')
    reason_display = serializers.ReadOnlyField(source='get_reason_display')

    class Meta:
        model = Penalty
        fields = ['id', 'member', 'member_name', 'meeting', 'meeting_label',
                  'reason', 'reason_display', 'description', 'amount',
                  'is_paid', 'paid_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'member_name', 'meeting_label', 'reason_display']


# ─── PenaltyRule ──────────────────────────────────────────────────────────────

class PenaltyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenaltyRule
        fields = ['id', 'late_penalty_amount', 'absent_penalty_amount', 'default_contribution_amount', 'is_active', 'updated_at']
        read_only_fields = ['id', 'updated_at']


# ─── Expense ──────────────────────────────────────────────────────────────────

class ExpenseSerializer(serializers.ModelSerializer):
    meeting_label = serializers.ReadOnlyField(source='meeting.__str__')

    class Meta:
        model = Expense
        fields = ['id', 'meeting', 'meeting_label', 'description', 'amount', 'date', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at', 'meeting_label']


# ─── Announcement ─────────────────────────────────────────────────────────────

class AnnouncementSerializer(serializers.ModelSerializer):
    meeting_label = serializers.ReadOnlyField(source='meeting.__str__')

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'body', 'is_published', 'meeting', 'meeting_label', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'meeting_label']


# ─── Manual Payment ─────────────────────────────────────────────────────────────

class ManualPaymentSerializer(serializers.ModelSerializer):
    meeting_label = serializers.ReadOnlyField(source='meeting.__str__')

    class Meta:
        model = ManualPayment
        fields = ['id', 'meeting', 'meeting_label', 'amount', 'reason', 'date', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'meeting_label']


# ─── Report serializers (read-only, computed) ─────────────────────────────────

class MonthlyReportSerializer(serializers.Serializer):
    meeting = MeetingSerializer()
    expected_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    collected_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    penalty_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    manual_payment_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_count = serializers.IntegerField()
    unpaid_count = serializers.IntegerField()
    unpaid_members = MemberSerializer(many=True)


class YearlyReportSerializer(serializers.Serializer):
    ethiopian_year = serializers.IntegerField()
    total_contributions = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_penalties = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_manual_payments = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    overall_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_meetings = serializers.IntegerField()


# ─── Member detail (full profile for public view) ─────────────────────────────

class MemberDetailSerializer(serializers.ModelSerializer):
    contributions = ContributionSerializer(many=True, read_only=True)
    attendances = AttendanceSerializer(many=True, read_only=True)
    penalties = PenaltySerializer(many=True, read_only=True)
    outstanding_balance = serializers.SerializerMethodField()
    outstanding_penalties = serializers.SerializerMethodField()
    outstanding_contributions = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'full_name', 'phone', 'join_date', 'is_active',
                  'contributions', 'attendances', 'penalties',
                  'outstanding_balance', 'outstanding_penalties', 'outstanding_contributions']

    def get_outstanding_penalties(self, obj):
        from django.db.models import Sum
        return obj.penalties.filter(is_paid=False).aggregate(t=Sum('amount'))['t'] or 0

    def get_outstanding_contributions(self, obj):
        from django.db.models import Sum
        return obj.contributions.filter(is_paid=False).aggregate(t=Sum('amount'))['t'] or 0

    def get_outstanding_balance(self, obj):
        return self.get_outstanding_penalties(obj) + self.get_outstanding_contributions(obj)
