from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'name', 'family_name', 'last_name', 'is_active', 'is_staff', 'is_superuser',
        'phone_number', 'birthdate'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name', 'family_name', 'last_name', 'document_number', 'phone_number')
    readonly_fields = ('id',)  # id is from UUIDBasedModel

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': (
                'code', 'name', 'family_name', 'last_name', 'address', 
                'document_number', 'phone_number', 'birthdate', 'photo'
            )
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ()}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

