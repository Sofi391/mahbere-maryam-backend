from django.db.models import QuerySet
from ..models import Member, Contribution


def get_active_members(search: str = None) -> QuerySet:
    qs = Member.objects.filter(is_active=True).order_by('full_name')
    if search:
        qs = qs.filter(full_name__icontains=search)
    return qs


def get_all_members(search: str = None) -> QuerySet:
    qs = Member.objects.all().order_by('full_name')
    if search:
        qs = qs.filter(full_name__icontains=search)
    return qs


def get_paid_member_ids_for_meeting(meeting) -> set:
    """Returns a set of member IDs who have paid for the given meeting."""
    if not meeting:
        return set()
    return set(
        Contribution.objects.filter(meeting=meeting, is_paid=True)
        .values_list('member_id', flat=True)
    )


def deactivate_member(member: Member) -> Member:
    member.is_active = False
    member.save()
    return member


def reactivate_member(member: Member) -> Member:
    member.is_active = True
    member.save()
    return member
