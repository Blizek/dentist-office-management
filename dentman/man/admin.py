from django.contrib import admin
from django.utils.html import format_html

from dentman.man.models import (Worker, DentistStaff, ManagementStaff, WorkersAvailability, SpecialAvailability,
                                Inaccessibility, Employment, Bonus, Resource, ResourcesUpdate)
from dentman.man.forms import EmploymentAdminForm


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    def worker_name(self, obj: Worker) -> str:
        return f"Worker {obj.user.get_full_name()}"
    worker_name.short_description = "Worker name"

    list_per_page = 30
    list_display = ("worker_name", "since_when", "to_when", "is_active", )
    list_filter = ("is_active", )
    search_fields = ("user__first_name", "user__last_name", )
    readonly_fields = ("is_active", )
    fieldsets = [
        ('', {
            'fields': ['user', 'since_when', 'to_when', 'is_active' ],
        }),
    ]

@admin.register(DentistStaff)
class DentistStaffAdmin(admin.ModelAdmin):
    def dentist_name(self, obj: DentistStaff) -> str:
        role = ""
        if obj.is_dentist: role = "Dentist"
        if obj.is_dentist_assistant: role = "Dentist Assistant"
        return f"{role} {obj.worker.user.get_full_name()}"
    dentist_name.short_description = "Name"

    def dentist_role(self, obj: DentistStaff) -> str:
        if obj.is_dentist: return "Dentist"
        if obj.is_dentist_assistant: return "Dentist Assistant"
        return ""
    dentist_role.short_description = "Role"

    list_display = ("dentist_name", "worker", "dentist_role")
    list_filter = ("is_dentist", "is_dentist_assistant")
    search_fields = ("worker__user__first_name", "worker__user__last_name")
    fieldsets = [
        ('', {
            'fields': ['worker', ],
        }),
        ('Roles', {
            'fields': ('is_dentist', 'is_dentist_assistant' ),
        })
    ]

@admin.register(ManagementStaff)
class ManagementStaffAdmin(admin.ModelAdmin):
    def management_name(self, obj: ManagementStaff) -> str:
        return obj.worker.user.get_full_name()
    management_name.short_description = "Name"

    def management_roles(self, obj: ManagementStaff) -> str:
        roles = []
        if obj.is_hr: roles.append("HR")
        if obj.is_financial: roles.append("Financial")
        return ", ".join(roles)
    management_roles.short_description = "Roles"

    list_display = ("management_name", "worker", "management_roles", "is_hr", "is_financial", )
    list_filter = ("is_hr", "is_financial", )
    search_fields = ("worker__user__first_name", "worker__user__last_name", )
    fieldsets = [
        ('', {
            'fields': ['worker', ],
        }), (
            'Roles', {
            'fields': ('is_hr', 'is_financial', )
        })
    ]

@admin.register(WorkersAvailability)
class WorkersAvailabilityAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = ("worker", "weekday", "since", "until", )
    list_filter = ("weekday", )
    search_fields = ("worker__user__first_name", "worker__user__last_name", )
    fieldsets = [
        ('', {
            'fields': ['worker', ],
        }),
        ('Date and time', {
            'fields': ['weekday', 'since', 'until'],
        })
    ]

@admin.register(SpecialAvailability)
class SpecialAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("worker", "date", "since", "until", )
    search_fields = ("worker__user__first_name", "worker__user__last_name", )
    fieldsets = [
        ('', {
            'fields': ['worker', ],
        }),
        ("Details", {
            'fields': ('date', 'since', 'until', 'reason', ),
        })
    ]

@admin.register(Inaccessibility)
class InaccessibilityAdmin(admin.ModelAdmin):
    list_display = ("worker", "date", "is_whole_day", "since", "until", )
    list_filter = ("is_whole_day", )
    search_fields = ("worker__user__first_name", "worker__user__last_name",)
    fieldsets = [
        ('', {
            'fields': ['worker', ],
        }),
        ('Details', {
            'fields': ('date', 'is_whole_day', 'since', 'until', )
        })
    ]

@admin.register(Employment)
class EmploymentAdmin(admin.ModelAdmin):
    def employee_contract(self, obj: Employment) -> str:
        return f"{obj.new_employee.user.get_full_name()}'s contract"
    employee_contract.short_description = "Employee's contract"

    def actual_contract(self, obj: Employment) -> str:
        if obj and obj.pk:
            return format_html(f'<a href="{obj.contract_scan.url}" target="_blank">Click here</a>')
        return "-"
    actual_contract.short_description = "Actual contract"

    form = EmploymentAdminForm
    list_display = ("employee_contract", "new_employee", "representative", "type_of_employment", "salary", "is_active", )
    list_filter = ("type_of_employment", "is_active", "is_for_limited_time", )
    search_fields = ("new_employee__user__first_name", "new_employee__user__last_name", "representative__worker__user__first_name",
                     "representative__worker__user__last_name")
    readonly_fields = ("actual_contract", )
    fieldsets = [
        ('', {
            'fields': ['new_employee', "representative", "type_of_employment", "is_for_limited_time", "salary", "is_active",]
        }),
        ('Dates', {
            'fields': ['agreement_date', 'since_when', 'until_when'],
        }),
        ('Contract', {
            'fields': ('actual_contract', 'contract_scan', )
        })
    ]

@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    def bonus_name(self, obj: Bonus) -> str:
        return f"{obj.worker.user.get_full_name()}'s bonus at {obj.bonus_date}"
    bonus_name.short_description = "Overview"

    list_per_page = 50
    list_display = ("bonus_name", "worker", "management_staff", "bonus_amount", "bonus_date", )
    search_fields = ("worker__user__first_name", "worker__user__last_name",
                     "management_staff__worker__user__first_name",
                     "management_staff__worker__user__last_name")
    fieldsets = [
        ('', {
            'fields': ['worker', 'management_staff', ],
        }),
        ('Details', {
            'fields': ('bonus_amount', 'bonus_date', 'bonus_reason', )
        })
    ]

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("resource_name", "default_metric", "actual_amount", )
    search_fields = ("resource_name", )

@admin.register(ResourcesUpdate)
class ResourcesUpdateAdmin(admin.ModelAdmin):
    def overview(self, obj: ResourcesUpdate) -> str:
        status = "removed"
        if obj.is_newly_delivered:
            status = "added"
        return f"Updated {obj.resource.resource_name} {status} {obj.amount_change} ({obj.metric.measurement_name_shortcut})"
    overview.short_description = "Overview"

    list_display = ("overview", "resource", "amount_change", "is_newly_delivered", )
    list_filter = ("is_newly_delivered", )
    search_fields = ("resource__resource_name", )
    fieldsets = [
        ('', {
            'fields': ['resource', 'is_newly_delivered', ],
        }),
        ('Amount details', {
            'fields': ('amount_change', 'metric', 'update_datetime')
        })
    ]
