from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from dentman.app.models import Attachment, AttachmentEntity
from dentman.app.forms import AttachmentAdminForm

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_patient', 'is_worker')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_active', 'is_patient', 'is_worker')
    ordering = ('-id', )
    list_per_page = 30

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional information", {
            "fields": ("phone_number", "profile_photo", "is_patient", "is_worker")
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

    def file_link(self, obj):
        if obj and obj.pk:
            return format_html(f'<a href="https://dentman.pl/storage/{obj.file.name}" target="_blank">Click here</a>')
        return "-"

    file_link.short_description = "Show file"


@admin.register(AttachmentEntity)
class AttachmentEntityAdmin(admin.ModelAdmin):
    pass
