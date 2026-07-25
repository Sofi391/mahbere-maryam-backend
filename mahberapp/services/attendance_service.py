from ..models import Attendance, Meeting


def bulk_record_attendance(meeting: Meeting, records: list) -> dict:
    """
    Upserts attendance records for a list of dicts with 'member' and 'status'.
    Signals handle auto-penalty creation on each save.
    Returns counts of created vs updated records.
    """
    created_count = 0
    updated_count = 0

    for record in records:
        _, was_created = Attendance.objects.update_or_create(
            member_id=record['member'],
            meeting=meeting,
            defaults={
                'status': record['status'],
                'notes': record.get('notes', ''),
            }
        )
        if was_created:
            created_count += 1
        else:
            updated_count += 1

    return {'created': created_count, 'updated': updated_count}


def get_attendance_for_member(member_id: int):
    return Attendance.objects.filter(member_id=member_id).select_related('meeting').order_by('-meeting__date')


def get_attendance_for_meeting(meeting_id: int):
    return Attendance.objects.filter(meeting_id=meeting_id).select_related('member').order_by('member__full_name')
