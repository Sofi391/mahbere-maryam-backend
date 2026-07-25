from decimal import Decimal
from django.db.models import Sum
from ..models import Member, Meeting, Contribution, Penalty, Expense, PenaltyRule, ManualPayment


def get_monthly_report(meeting: Meeting) -> dict:
    rule = PenaltyRule.get_active()
    active_members = Member.objects.filter(is_active=True)

    contributions = Contribution.objects.filter(meeting=meeting)
    paid_contributions = contributions.filter(is_paid=True)
    collected_penalties = Penalty.objects.filter(meeting=meeting, is_paid=True)
    expenses = Expense.objects.filter(meeting=meeting)
    manual_payments = ManualPayment.objects.filter(meeting=meeting)

    expected_income = active_members.count() * rule.default_contribution_amount
    collected_income = paid_contributions.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    penalty_income = collected_penalties.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    manual_payment_income = manual_payments.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_expenses = expenses.aggregate(t=Sum('amount'))['t'] or Decimal('0')

    unpaid_member_ids = contributions.filter(is_paid=False).values_list('member_id', flat=True)
    unpaid_members = Member.objects.filter(id__in=unpaid_member_ids)

    return {
        'meeting': meeting,
        'expected_income': expected_income,
        'collected_income': collected_income,
        'penalty_income': penalty_income,
        'manual_payment_income': manual_payment_income,
        'total_expenses': total_expenses,
        'balance': collected_income + penalty_income + manual_payment_income - total_expenses,
        'paid_count': paid_contributions.count(),
        'unpaid_count': contributions.filter(is_paid=False).count(),
        'unpaid_members': unpaid_members,
    }


def get_yearly_report(ethiopian_year: int) -> dict:
    meetings = Meeting.objects.filter(ethiopian_year=ethiopian_year)

    contributions = Contribution.objects.filter(meeting__in=meetings, is_paid=True)
    penalties = Penalty.objects.filter(meeting__in=meetings, is_paid=True)
    expenses = Expense.objects.filter(meeting__in=meetings)
    manual_payments = ManualPayment.objects.filter(meeting__in=meetings)

    total_contributions = contributions.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_penalties = penalties.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_manual_payments = manual_payments.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_expenses = expenses.aggregate(t=Sum('amount'))['t'] or Decimal('0')

    return {
        'ethiopian_year': ethiopian_year,
        'total_contributions': total_contributions,
        'total_penalties': total_penalties,
        'total_manual_payments': total_manual_payments,
        'total_expenses': total_expenses,
        'overall_balance': total_contributions + total_penalties + total_manual_payments - total_expenses,
        'total_meetings': meetings.count(),
    }


def get_dashboard_summary(latest_meeting: Meeting | None) -> dict:
    rule = PenaltyRule.get_active()
    total_members = Member.objects.filter(is_active=True).count()

    if latest_meeting:
        contributions = Contribution.objects.filter(meeting=latest_meeting)
        paid_count = contributions.filter(is_paid=True).count()
        monthly_income = contributions.filter(is_paid=True).aggregate(
            t=Sum('amount'))['t'] or Decimal('0')
        penalty_income = Penalty.objects.filter(
            meeting=latest_meeting, is_paid=True
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        expenses_this_month = Expense.objects.filter(
            meeting=latest_meeting
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        extra_income_this_month = ManualPayment.objects.filter(
            meeting=latest_meeting,
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
    else:
        paid_count = 0
        monthly_income = penalty_income = expenses_this_month = extra_income_this_month = Decimal('0')

    all_contributions = Contribution.objects.filter(is_paid=True).aggregate(
        t=Sum('amount'))['t'] or Decimal('0')
    all_penalties = Penalty.objects.filter(is_paid=True).aggregate(
        t=Sum('amount'))['t'] or Decimal('0')
    all_manual_payments = ManualPayment.objects.aggregate(
        t=Sum('amount'))['t'] or Decimal('0')
    all_expenses = Expense.objects.aggregate(t=Sum('amount'))['t'] or Decimal('0')

    return {
        'total_members': total_members,
        'paid_this_month': paid_count,
        'unpaid_this_month': total_members - paid_count,
        'monthly_income': monthly_income,
        'penalty_income': penalty_income,
        'extra_income_this_month': extra_income_this_month,
        'expenses_this_month': expenses_this_month,
        'current_balance': all_contributions + all_penalties + all_manual_payments - all_expenses,
        'default_contribution': rule.default_contribution_amount,
    }
