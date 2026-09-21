from django.contrib import admin
from .models import Employee, Department, EmploymentStatus


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'department', 'employment_status', 'created_at')
    list_filter = ('department', 'employment_status', 'created_at')
    search_fields = ('employee_id', 'first_name', 'last_name', 'department')
    ordering = ('employee_id',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_id', 'first_name', 'last_name')
        }),
        ('Employment Details', {
            'fields': ('department', 'employment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )