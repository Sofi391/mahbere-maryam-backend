from django.contrib import admin
from .models import Member, Meeting, Attendance, PenaltyRule, Contribution, Penalty, Expense, Announcement, ManualPayment


@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = ['reason', 'amount', 'date', 'meeting', 'notes', 'created_at']
    list_filter = ['meeting']
    search_fields = ['reason']
    ordering = ['-date']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'join_date', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['full_name', 'phone']
    ordering = ['full_name']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date', 'ethiopian_month', 'ethiopian_year']
    ordering = ['-date']


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0


class ContributionInline(admin.TabularInline):
    model = Contribution
    extra = 0


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['member', 'meeting', 'status', 'recorded_at']
    list_filter = ['status', 'meeting']
    search_fields = ['member__full_name']


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['member', 'meeting', 'amount', 'is_paid', 'paid_date']
    list_filter = ['is_paid', 'meeting']
    search_fields = ['member__full_name']


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ['member', 'meeting', 'reason', 'amount', 'is_paid', 'paid_date']
    list_filter = ['reason', 'is_paid', 'meeting']
    search_fields = ['member__full_name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'meeting']
    list_filter = ['meeting']
    search_fields = ['description']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'meeting', 'created_at']
    list_filter = ['is_published']
    search_fields = ['title']


@admin.register(PenaltyRule)
class PenaltyRuleAdmin(admin.ModelAdmin):
    list_display = ['late_penalty_amount', 'absent_penalty_amount', 'default_contribution_amount', 'is_active', 'updated_at']
