# factorial_hr/apps/auth/api/serializers.py
from rest_framework import serializers
from django.conf import settings


class ExternalLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    provider = serializers.ChoiceField(
        choices=[], 
        required=False,
        help_text="Proveedor OAuth (google, microsoft, github). Si no se especifica, se usa el proveedor por defecto."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener proveedores disponibles dinámicamente
        oauth_config = getattr(settings, 'OAUTH_PROVIDERS', {})
        available_providers = [
            (name, config.get('display_name', name.title()))
            for name, config in oauth_config.items()
            if config.get('enabled', False)
        ]
        self.fields['provider'].choices = available_providers

    def validate_provider(self, value):
        if value:
            oauth_config = getattr(settings, 'OAUTH_PROVIDERS', {})
            if value not in oauth_config:
                raise serializers.ValidationError(f"Proveedor '{value}' no está configurado")
            if not oauth_config[value].get('enabled', False):
                raise serializers.ValidationError(f"Proveedor '{value}' está deshabilitado")
        return value


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class ProviderListSerializer(serializers.Serializer):
    """Serializer para listar proveedores disponibles"""
    name = serializers.CharField()
    display_name = serializers.CharField()
    well_known_url = serializers.URLField()
