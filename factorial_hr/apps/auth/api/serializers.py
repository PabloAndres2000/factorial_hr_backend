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


class RegisterSerializer(serializers.Serializer):
    """Serializer para registro de usuarios locales"""
    name = serializers.CharField(
        required=True,
        max_length=100,
        error_messages={
            'required': 'El nombre es requerido',
            'blank': 'El nombre no puede estar vacío',
            'max_length': 'El nombre no puede exceder los 100 caracteres'
        }
    )
    last_name = serializers.CharField(
        required=True,
        max_length=100,
        error_messages={
            'required': 'El apellido es requerido',
            'blank': 'El apellido no puede estar vacío',
            'max_length': 'El apellido no puede exceder los 100 caracteres'
        }
    )
    family_name = serializers.CharField(
        required=True,
        max_length=100,
        error_messages={
            'required': 'El apellido familiar es requerido',
            'blank': 'El apellido familiar no puede estar vacío',
            'max_length': 'El apellido familiar no puede exceder los 100 caracteres'
        }
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'El email es requerido',
            'invalid': 'El email no tiene un formato válido',
            'blank': 'El email no puede estar vacío'
        }
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        error_messages={
            'required': 'La contraseña es requerida',
            'blank': 'La contraseña no puede estar vacía',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )
    password_confirmation = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'La confirmación de contraseña es requerida',
            'blank': 'La confirmación de contraseña no puede estar vacía'
        }
    )

    def validate_email(self, value):
        """Valida que el email no esté ya registrado"""
        from factorial_hr.apps.users.models import User
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este email ya está registrado')
        return value.lower()

    def validate(self, data):
        """Valida que las contraseñas coincidan"""
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')
        
        if password != password_confirmation:
            raise serializers.ValidationError({
                'password_confirmation': 'Las contraseñas no coinciden'
            })
        
        return data

    def create(self, validated_data):
        """Crea un nuevo usuario"""
        from factorial_hr.apps.users.models import User
        
        # Remover password_confirmation ya que no es parte del modelo
        validated_data.pop('password_confirmation')
        
        # Crear el usuario
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            last_name=validated_data['last_name'],
            family_name=validated_data['family_name']
        )
        
        return user
