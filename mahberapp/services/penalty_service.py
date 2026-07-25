from django.utils import timezone
from ..models import Penalty


def mark_penalty_paid(penalty: Penalty, paid_date=None) -> Penalty:
    penalty.is_paid = True
    penalty.paid_date = paid_date or timezone.now().date()
    penalty.save()
    return penalty
