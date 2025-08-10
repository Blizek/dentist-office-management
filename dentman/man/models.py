from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from dentman.app.mixins import CreatedUpdatedMixin
from dentman.storage import CustomFileSystemStorage
from dentman.utils import get_upload_path
from dentman.app.models import Metrics

User = get_user_model()
storage = CustomFileSystemStorage()
pdf_extension_validator = FileExtensionValidator(["pdf"])

class Worker(CreatedUpdatedMixin):
    """
    TODO: Add model describing comment
    TODO: Add admin view
    """
    user = models.OneToOneField(User, verbose_name="User", on_delete=models.CASCADE)
    since_when = models.DateField("Since when", help_text="Date since this user is a worker", default=date.today)
    to_when = models.DateField("To when", help_text="Date until this user is a worker", null=True, blank=True)
    is_active = models.BooleanField("Is active", default=True, editable=False)

    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"

    def __str__(self):
        return f"Worker {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        # if value `to_when` is set that means that worker is still active
        if not self.to_when:
            self.is_active = False

        super().save(*args, **kwargs)


class DentistStaff(CreatedUpdatedMixin):
    """
    TODO: Add model describing comment
    TODO: Add admin view
    """
    worker = models.OneToOneField(Worker, verbose_name="Worker", on_delete=models.CASCADE)
    is_dentist = models.BooleanField("Is dentist", default=False,
                                     help_text="If worker is a dentist check the checkbox, otherwise means that worker is dentist assistant"
    )

    class Meta:
        verbose_name = "dentist staff"
        verbose_name_plural = "dentist staffs"

    def __str__(self):
        position = "dentist"
        if not self.is_dentist:
            position = "dentist assistant"

        return f"{self.worker.user.get_full_name()} at position {position}"


class ManagementStaff(CreatedUpdatedMixin):
    """
    TODO: Add model describing comment
    TODO: Add admin view
    """
    worker = models.OneToOneField(Worker, verbose_name="Worker", on_delete=models.CASCADE)
    is_hr = models.BooleanField("Is HR", default=False,
                                help_text="If worker can employ and lay off other workers (which don't have hr role) select the checkbox"
    )
    is_financial = models.BooleanField("Is financial", default=False,
                                       help_text="If worker can manage finance, get access to financial summaries select the checkbox"
    )

    class Meta:
        verbose_name = "management staff"
        verbose_name_plural = "management staffs"

    def __str__(self):
        roles = []
        if self.is_hr: roles.append("HR")
        if self.is_financial: roles.append("Financial")
        roles_as_text = ", ".join(role for role in roles)

        return f"{self.worker.user.get_full_name()} with {roles_as_text} permissions"


class WorkersAvailability(CreatedUpdatedMixin):
    """
    TODO: Add model describing comment
    TODO: Add admin view
    """
    WEEKDAYS = (
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    )

    worker = models.ForeignKey(Worker, verbose_name="Worker", on_delete=models.CASCADE)
    weekday = models.SmallIntegerField("Weekday", choices=WEEKDAYS, null=False, blank=False)
    since = models.TimeField("Since when", blank=False, help_text="Time since when worker is available that day")
    until = models.TimeField("Until when", blank=False, help_text="Time until worker is available that day")

    class Meta:
        verbose_name = "worker's availability"
        verbose_name_plural = "workers' availabilities"

    def __str__(self):
        return f"{self.worker.user.get_full_name()} availability on {self.get_weekday_display()} since {self.since} to {self.until}"


class SpecialAvailability(CreatedUpdatedMixin):
    """
    TODO: Add model describing comment
    TODO: Add admin view
    """
    worker = models.ForeignKey(Worker, verbose_name="Worker", on_delete=models.CASCADE)
    date = models.DateField("Date of availability", null=False, blank=False)
    since = models.TimeField("Since when", blank=False, help_text="Time since when worker is available that day")
    until = models.TimeField("Until when", blank=False, help_text="Time until worker is available that day")
    reason = models.TextField("Reason", blank=True)

    class Meta:
        verbose_name = "special availability"
        verbose_name_plural = "special availabilities"

    def __str__(self):
        return f"{self.worker.user.get_full_name()} special availability at {self.date} since {self.since} to {self.until}"


class Inaccessibility(CreatedUpdatedMixin):
    """
    TODO: Add model describing comment
    TODO: Add admin view
    """
    worker = models.ForeignKey(Worker, verbose_name="Worker", on_delete=models.CASCADE)
    date = models.DateField("Date of inaccessibility", null=False, blank=False)
    is_whole_day = models.BooleanField("Is whole day", default=False,
                                       help_text="Select checkbox if worker is inaccessible whole day"
    )
    since = models.TimeField("Since when", blank=True, null=True,
                             help_text="Time since when worker is inaccessible that day (type only inaccessibility is not for whole day)"
    )
    until = models.TimeField("Until when", blank=True, null=True,
                             help_text="Time until worker is inaccessible that day (type only inaccessibility is not for whole day)"
    )

    class Meta:
        verbose_name = "inaccessibility"
        verbose_name_plural = "unavailability"

    def __str__(self):
        if self.is_whole_day:
            return f"{self.worker.user.get_full_name()} inaccessible at {self.date}"
        return f"{self.worker.user.get_full_name()} inaccessible at {self.date} since {self.since} to {self.until}"

    def save(self, *args, **kwargs):
        # if flag `is_whole_day` is not selected and both `since` and `until` are empty raise error
        if not self.is_whole_day and not self.since and not self.until:
            raise ValidationError("If inaccessibility is not for whole day please type since when util when is inaccessibility")
        # if flag `is_whole_day` is not selected and `since` is empty raise error
        if not self.is_whole_day and not self.since:
            raise ValidationError("Please type until when is inaccessibility")
        # if flag `is_whole_day` is not selected and `until` is empty raise error
        if not self.is_whole_day and not self.until:
            raise ValidationError("Please type until when is inaccessibility")

        super().save(*args, **kwargs)


class Employment(CreatedUpdatedMixin):
    """
    TODO: signal to move from temp folder into correct directory
    TODO: add replacing old file with new one
    TODO: add validating in save if `is_for_limited_time` is not set that `until_when` has to not empty
    TODO: Add model describing comment
    TODO: Add admin view
    """
    EMPLOYMENT_TYPES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('fixed_term', 'Fixed-term'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('traineeship', 'Traineeship'),
        ('volunteer', 'Volunteer'),
    )

    new_employee = models.ForeignKey(Worker, verbose_name="New employee", on_delete=models.CASCADE)
    representative = models.ForeignKey(ManagementStaff, verbose_name="Representative", on_delete=models.CASCADE)
    type_of_employment = models.PositiveSmallIntegerField("Type of employment", choices=EMPLOYMENT_TYPES, blank=False)
    is_for_limited_time = models.BooleanField("Is limited for time", default=False,
                                              help_text="If employment is set only for limited time, select the checkbox"
    )
    since_when = models.DateField("Since when", blank=False, null=False, help_text="Date since new employee starts working")
    until_when = models.DateField("Until when", blank=False, null=False,
                                  help_text="Date until new employee works (select only when job is for limited time)"
    )
    agreement_date = models.DateField("Agreement date", blank=False, null=False,
                                      help_text="Date when both sides reached an agreement"
    )
    salary = models.DecimalField("Salary", max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField("Is active", default=True, help_text="If this contract is still active, select the checkbox")
    contract_scan = models.FileField("Contract scan file", blank=False, null=False, storage=storage,
                                     upload_to=get_upload_path, validators=[pdf_extension_validator]
    )

    class Meta:
        verbose_name = "employment"
        verbose_name_plural = "employments"

    def __str__(self):
        return f"{self.new_employee.user.get_full_name()}'s employment"


class Bonus(CreatedUpdatedMixin):
    """
    TODO: Add model describing comment
    TODO: Add admin view
    """
    worker = models.ForeignKey(Worker, verbose_name="Worker", on_delete=models.CASCADE)
    management_staff = models.ForeignKey(ManagementStaff, verbose_name="Management staff", on_delete=models.CASCADE)
    bonus_amount = models.DecimalField("Bonus amount", max_digits=10, decimal_places=2, blank=False, null=False)
    bonus_date = models.DateField("Bonus date", blank=False, null=False)
    bonus_reason = models.TextField("Bonus reason", blank=True)

    class Meta:
        verbose_name = "bonus"
        verbose_name_plural = "bonuses"

    def __str__(self):
        return f"Bonus for {self.worker.user.get_full_name()} ({self.bonus_amount} PLN)"


class Resource(CreatedUpdatedMixin):
    """
    TODO: Add model describing comment
    TODO: Add admin view
    """
    resource_name = models.CharField("Resource name", max_length=255, blank=False, null=False)
    default_metric = models.ForeignKey(Metrics, verbose_name="Default metric", on_delete=models.SET_NULL, null=True)
    actual_amount = models.DecimalField("Actual amount", max_digits=20, decimal_places=7, blank=False, null=False, default=0.0)

    class Meta:
        verbose_name = "resource"
        verbose_name_plural = "resources"

    def __str__(self):
        return f"{self.resource_name} - {self.actual_amount}{self.default_metric.measurement_name_shortcut}"


class ResourcesUpdate(CreatedUpdatedMixin):
    """
    TODO: Add making update of resource after adding update record
    TODO: Add validation to not set negative amount of resource after update
    TODO: Add model describing comment
    TODO: Add admin view
    """
    resource = models.ForeignKey(Resource, verbose_name="Resource", on_delete=models.SET_NULL, null=True)
    amount_change = models.DecimalField("Amount change", max_digits=20, decimal_places=7, blank=False, null=False)
    metric = models.ForeignKey(Metrics, verbose_name="Metric", on_delete=models.SET_NULL, null=True)
    is_newly_delivered = models.BooleanField("Is newly delivered", default=True,
        help_text="If it's new resource that has been delivered, select checkbox. If it's update about used resources unselect checkbox"
    )
    update_datetime = models.DateTimeField("Update datetime", blank=False, null=False, default=timezone.now)

    class Meta:
        verbose_name = "resources update"
        verbose_name_plural = "resources updates"

    def __str__(self):
        status = "ADDED" if self.is_newly_delivered else "REMOVED"
        return f"{self.resource.resource_name}'s update: {self.amount_change}{self.metric.measurement_name_shortcut} {status}"

