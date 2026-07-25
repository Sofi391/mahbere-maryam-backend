from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Member(models.Model):
    """
    Represents a Mahber member.
    No member ID is shown to users — identified by name/phone internally by DB id.
    """
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    join_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Meeting(models.Model):
    """
    One Meeting = one monthly Mahber cycle.
    Attendance and contributions are tied to a specific meeting.
    """
    ETHIOPIAN_MONTHS = [
        (1,  'Meskerem'),   # September
        (2,  'Tikimit'),    # October
        (3,  'Hidar'),      # November
        (4,  'Tahsas'),     # December
        (5,  'Tir'),        # January
        (6,  'Yekatit'),    # February
        (7,  'Megabit'),    # March
        (8,  'Miazia'),     # April
        (9,  'Ginbot'),     # May
        (10, 'Sene'),       # June
        (11, 'Hamle'),      # July
        (12, 'Nehase'),     # August
        (13, 'Pagume'),     # Extra month
    ]

    date = models.DateField()
    ethiopian_month = models.IntegerField(choices=ETHIOPIAN_MONTHS)
    ethiopian_year = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['ethiopian_month', 'ethiopian_year']
        indexes = [
            models.Index(fields=['ethiopian_year']),
            models.Index(fields=['ethiopian_month', 'ethiopian_year']),
        ]

    def __str__(self):
        month_name = dict(self.ETHIOPIAN_MONTHS).get(self.ethiopian_month, '')
        return f"{month_name} {self.ethiopian_year} ({self.date})"

    @property
    def ethiopian_month_name(self):
        return dict(self.ETHIOPIAN_MONTHS).get(self.ethiopian_month, '')


class Attendance(models.Model):
    """
    Each member gets one attendance record per meeting.
    Late and Absent statuses automatically trigger penalty creation.
    """
    STATUS_PRESENT = 'present'
    STATUS_LATE = 'late'
    STATUS_ABSENT = 'absent'
    STATUS_EXCUSED = 'excused'

    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_LATE,    'Late'),
        (STATUS_ABSENT,  'Absent'),
        (STATUS_EXCUSED, 'Excused'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    notes = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-meeting__date']
        unique_together = ['member', 'meeting']
        indexes = [
            models.Index(fields=['meeting']),
            models.Index(fields=['member']),
        ]

    def __str__(self):
        return f"{self.member.full_name} — {self.meeting} — {self.get_status_display()}"


class PenaltyRule(models.Model):
    """
    Configurable penalty amounts for attendance statuses.
    Admin can update these. Only one active rule set is expected.
    """
    late_penalty_amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=Decimal('50.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    absent_penalty_amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    default_contribution_amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=Decimal('30.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Penalty Rule'

    def __str__(self):
        return (
            f"Late: {self.late_penalty_amount} ETB | "
            f"Absent: {self.absent_penalty_amount} ETB | "
            f"Contribution: {self.default_contribution_amount} ETB"
        )

    @classmethod
    def get_active(cls):
        """Returns the active rule, or creates a default one."""
        rule = cls.objects.filter(is_active=True).first()
        if not rule:
            rule = cls.objects.create(is_active=True)
        return rule


class Contribution(models.Model):
    """
    Monthly contribution (payment) for each member per meeting.
    """
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='contributions')
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=Decimal('30.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-meeting__date']
        unique_together = ['member', 'meeting']
        indexes = [
            models.Index(fields=['meeting', 'is_paid']),
            models.Index(fields=['member']),
        ]

    def __str__(self):
        status = '✔ Paid' if self.is_paid else '✖ Unpaid'
        return f"{self.member.full_name} — {self.meeting} — {status}"


class Penalty(models.Model):
    """
    Penalties for members. Can be auto-generated from attendance or manually added.
    """
    REASON_LATE = 'late'
    REASON_ABSENT = 'absent'
    REASON_CUSTOM = 'custom'

    REASON_CHOICES = [
        (REASON_LATE,   'Late to Meeting'),
        (REASON_ABSENT, 'Absent from Meeting'),
        (REASON_CUSTOM, 'Custom'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='penalties')
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='penalties', blank=True, null=True)
    reason = models.CharField(max_length=10, choices=REASON_CHOICES)
    description = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['member']),
            models.Index(fields=['meeting', 'is_paid']),
        ]

    def __str__(self):
        status = 'Paid' if self.is_paid else 'Outstanding'
        return f"{self.member.full_name} — {self.get_reason_display()} — {self.amount} ETB ({status})"


class Expense(models.Model):
    """
    Tracks Mahber spending. Tied to a meeting or standalone.
    """
    meeting = models.ForeignKey(
        Meeting, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='expenses'
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.description} — {self.amount} ETB ({self.date})"


class Announcement(models.Model):
    """
    Committee posts visible to everyone (no login required).
    """
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    meeting = models.ForeignKey(
        Meeting, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ManualPayment(models.Model):
    """
    Manual payments recorded by admin that are not tied to specific members.
    Optionally linked to a meeting so they appear in monthly/yearly reports.
    """
    meeting = models.ForeignKey(
        Meeting, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='manual_payments'
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    reason = models.CharField(max_length=255)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['meeting']),
        ]

    def __str__(self):
        return f"{self.reason} — {self.amount} ETB ({self.date})"
