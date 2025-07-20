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
    pass

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    pass

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    pass

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_by', 'visit_counter',)
    search_fields = ('title', 'slug')
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
