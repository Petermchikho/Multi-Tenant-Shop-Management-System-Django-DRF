from django.contrib import admin
from django_use_email_as_username.admin import BaseUserAdmin
from .models import User,Profile

# Extend the BaseUserAdmin and add custom fields
class CustomUserAdmin(BaseUserAdmin):
    # Add custom fields to list_display (which fields you want to display in the admin list view)
    list_display = ['email', 'phone_number', 'date_of_birth', 'is_active', 'is_staff','role','shop','merchant']
    
    # Modify the fieldsets to add custom fields (these fields will appear when editing a user)
    fieldsets = (
        (None, {'fields': ('email', 'password','username','first_name','last_name')}),
        ('Personal info', {'fields': ('phone_number', 'date_of_birth')}),
        ('Role info', {'fields': ('role', 'shop','merchant')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Define the fields to be shown when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'date_of_birth', 'password1', 'password2')}
        ),
    )

    # Filterable fields in the admin list view
    list_filter = ['is_active', 'is_staff']
    
    # Searchable fields
    search_fields = ['email', 'phone_number']

    ordering = ['email']

# Register the custom user admin
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
