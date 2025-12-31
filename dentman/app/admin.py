from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from dentman.app.models import Attachment, AttachmentEntity, Metrics
from dentman.app.forms import AttachmentAdminForm

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'is_active', 'is_patient', 'is_worker', 'is_adult')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_active', 'is_patient', 'is_adult', 'is_worker', 'is_dentist_staff', 'is_dentist', 'is_dentist_assistant', 'is_management_staff', 'is_hr', 'is_financial')
    ordering = ('-id', )
    list_per_page = 30
    readonly_fields = BaseUserAdmin.readonly_fields + ('eid', )

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional information", {
            "fields": ("eid", "birth_date", "phone_number", "profile_photo", "is_patient", "is_worker")
        }),
        ("Dentist staff information", {
            "fields": ("is_dentist_staff", "is_dentist", "is_dentist_assistant")
        }),
        ("Management staff information", {
            "fields": ("is_management_staff", "is_hr", "is_financial")
        }),
    )

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    form = AttachmentAdminForm
    readonly_fields = ["file_link"]
    fieldsets = [
        (
            'File', {
                'fields': ['file', 'file_link']
        }
        ),
        (
            'Additional information', {
                'fields': ['is_active', 'additional_info']
        }
        )
    ]

    def file_link(self, obj: Attachment) -> str:
        if obj and obj.pk:
            return format_html(f'<a href="https://dentman.pl/storage/{obj.file.name}" target="_blank">Click here</a>')
        return "-"

    file_link.short_description = "Show file"


@admin.register(AttachmentEntity)
class AttachmentEntityAdmin(admin.ModelAdmin):
    pass

@admin.register(Metrics)
class MetricsAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

