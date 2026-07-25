from ..models import Contribution, Member, Meeting, PenaltyRule


def bulk_record_contributions(meeting: Meeting, records: list) -> dict:
    """
    Upserts contribution records for a list of dicts.
    Each record: { member, amount (optional), is_paid, paid_date (optional), notes (optional) }
    """
    rule = PenaltyRule.get_active()
    created_count = 0
    updated_count = 0

    for record in records:
        _, was_created = Contribution.objects.update_or_create(
            member_id=record['member'],
            meeting=meeting,
            defaults={
                'amount': record.get('amount', rule.default_contribution_amount),
                'is_paid': record.get('is_paid', True),
                'paid_date': record.get('paid_date'),
                'notes': record.get('notes', ''),
            }
        )
        if was_created:
            created_count += 1
        else:
            updated_count += 1

    return {'created': created_count, 'updated': updated_count}


def initialize_contributions_for_meeting(meeting: Meeting) -> int:
    """
    Creates an unpaid contribution record for every active member for a meeting.
    Skips members who already have a record. Returns count of records created.
    """
    rule = PenaltyRule.get_active()
    members = Member.objects.filter(is_active=True)
    created_count = 0

    for member in members:
        _, was_created = Contribution.objects.get_or_create(
            member=member,
            meeting=meeting,
            defaults={
                'amount': rule.default_contribution_amount,
                'is_paid': False,
            }
        )
        if was_created:
            created_count += 1

    return created_count
