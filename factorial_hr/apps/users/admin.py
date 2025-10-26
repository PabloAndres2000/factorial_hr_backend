from django.contrib import admin
from django.contrib.auth.hashers import make_password, identify_hasher
from .models import User
from simple_history.admin import SimpleHistoryAdmin

@admin.register(User)
class UsersAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "code",
        "document_number",
        "name",
        "last_name",
        "family_name",
        "address",
        "email",
        "phone_number",
        "birthdate",
        "photo",
        "ip_addresses",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = ["id", "email", "document_number", "phone_number", "code"]
    list_display_links = ("id", "email")
    ordering = ["id"]
    # Asumiendo que los campos de 'created_at', 'updated_at', 'deleted_at', 'changes_by' todavía existen
    exclude = ("created_at", "updated_at", "deleted_at", "changes_by")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Información Personal",
            {
                "fields": (
                    "code",
                    "name",
                    "last_name",
                    "family_name",
                    "document_number",
                    "phone_number",
                    "birthdate",
                    "address",
                    "photo",
                    "ip_addresses",
                )
            },
        ),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "code",
                    "name",
                    "last_name",
                    "family_name",
                    "document_number",
                    "phone_number",
                    "birthdate",
                    "address",
                    "photo",
                    "ip_addresses",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        # Si la contraseña fue cambiada en el admin
        password = form.cleaned_data.get("password", None)
        if password:
            # Solo la hasheamos si no parece ya hasheada
            try:
                identify_hasher(password)
                # Si no lanza excepción, ya está hasheada
            except Exception:
                obj.password = make_password(password)
        super().save_model(request, obj, form, change)
