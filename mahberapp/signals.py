from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attendance, Penalty, PenaltyRule


@receiver(post_save, sender=Attendance)
def auto_create_penalty(sender, instance, created, **kwargs):
    """
    Automatically creates or updates a penalty when attendance is saved as
    'late' or 'absent'. Removes the penalty if status is changed to
    'present' or 'excused'.
    """
    penalizable = [Attendance.STATUS_LATE, Attendance.STATUS_ABSENT]

    if instance.status in penalizable:
        rule = PenaltyRule.get_active()
        amount = (
            rule.late_penalty_amount
            if instance.status == Attendance.STATUS_LATE
            else rule.absent_penalty_amount
        )
        reason = (
            Penalty.REASON_LATE
            if instance.status == Attendance.STATUS_LATE
            else Penalty.REASON_ABSENT
        )

        # Create or update — if the attendance record is edited, update the penalty.
        # Filter to only auto-generated penalties (late/absent), not custom ones.
        Penalty.objects.update_or_create(
            member=instance.member,
            meeting=instance.meeting,
            reason=reason,
            defaults={
                'amount': amount,
                'description': f"Auto-generated: {instance.get_status_display()} at {instance.meeting}",
            }
        )
        # Clean up the other auto type in case status changed (e.g. late → absent)
        other_reason = Penalty.REASON_ABSENT if reason == Penalty.REASON_LATE else Penalty.REASON_LATE
        Penalty.objects.filter(
            member=instance.member,
            meeting=instance.meeting,
            reason=other_reason
        ).delete()

    else:
        # Member was present or excused — remove any auto-generated penalty for this meeting
        Penalty.objects.filter(
            member=instance.member,
            meeting=instance.meeting,
            reason__in=[Penalty.REASON_LATE, Penalty.REASON_ABSENT]
        ).delete()
