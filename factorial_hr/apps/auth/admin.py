from django.contrib import admin
from .models import RefreshToken

@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created_at', 'expires_at', 'revoked')
    list_filter = ('revoked', 'expires_at', 'created_at')
    search_fields = ('key', 'user__email')
    readonly_fields = ('key', 'user', 'created_at', 'expires_at')

    def has_add_permission(self, request):
        return False  # Prevent manual addition in admin

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletions if needed

