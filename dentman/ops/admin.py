from django.contrib import admin

from dentman.ops.models import Category, Service, VisitStatus, Discount, Visit, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass

@admin.register(VisitStatus)
class VisitStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_booked', 'is_postponed', 'is_in_progress', 'is_finished', 'is_resigned_by_patient',
                    'is_resigned_by_dentist', 'is_resigned_by_office',)
    fieldsets = [
        (
            '', {
                'fields': ('name', ),
            }
        ), (
            'Booking', {
                'fields': ('is_booked', 'is_postponed', )
            }
        ), (
            "Visit's status", {
                'fields': ('is_in_progress', 'is_finished', )
            }
        ), (
            "Resignations", {
                'fields': ('is_resigned_by_patient', 'is_resigned_by_dentist', 'is_resigned_by_office', )
            }
        ), (
            'Additional information', {
                'fields': ('additional_info', )
            }
        )
    ]

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percent', 'discount_type', 'is_currently_valid', 'is_limited', 'limit_value', 'used_counter', )
    readonly_fields = ('used_counter', 'why_invalid_summary', 'is_currently_valid', )
    search_fields = ('name', 'percent', 'discount_type', )
    list_filter = ('discount_type', 'is_limited', )
    fieldsets = (
        (
            '', {
                'fields': ('name', 'description', 'percent', 'discount_type', 'promotion_code', )
            }
        ), (
            'Is valid', {
                'fields': ('is_currently_valid', 'why_invalid_summary', )
            }       
        ), (
            'Valid dates', {
                'fields': ('valid_since', 'valid_to', )
            }
        ), (
            'Limits', {
                'fields': ('is_limited', 'limit_value', 'used_counter', )
            }
        ), (
            'Additional information', {
                'fields': ('additional_info', )
            }
        )   
    )

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('eid', 'patient', 'visit_status', 'scheduled_from', 'final_price')
    list_filter = ('visit_status', 'dentists')
    filter_horizontal = ('dentists', 'discounts')
    readonly_fields = ('final_price', 'eid')
    search_fields = ('eid', )
    fieldsets = (
        (
            '', {
                'fields': ('eid', 'patient', 'dentists')
            }
        ), (
            'Date and time', {
                'fields': ('scheduled_from', 'scheduled_to', 'starting_time', 'ending_time')
            }
        ), (
            "Visit's information", {
                'fields': ('visit_status', 'visit_description')
            }
        ), (
            'Price and discounts', {
                'fields': ('price', 'discounts', 'final_price')
            }
        ), (
            'Additional information', {
                'fields': ('additional_info', )
            }
        )
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_by', 'visit_counter',)
    search_fields = ('title', 'slug', 'created_by__first_name',)
    fieldsets = (
        (
            '', {
                'fields': ('title', 'slug',)
            }
        ), (
            "Blog's content", {
                'fields': ('main_photo', 'text_html',)
            }
        ), (
            "Blog's statistics", {
                'fields': ('visit_counter', 'created_by', 'created_at', 'updated_by', 'updated_at',)
             }
        )
    )
    readonly_fields = ('visit_counter', 'created_by', 'created_at', 'updated_by', 'updated_at',)
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
