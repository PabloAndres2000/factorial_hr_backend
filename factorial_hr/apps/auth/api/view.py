# factorial_hr/apps/auth/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import uuid
from factorial_hr.apps.auth.services.oauth_provider_client import OAuthProviderFactory, OAuthProviderClient
from factorial_hr.apps.auth.services.token_verifier import TokenVerifier
from factorial_hr.apps.users.repositories.user_repository import UserRepository
from factorial_hr.apps.auth.models import RefreshToken, EmailVerificationToken
from factorial_hr.apps.auth.api.serializers import (
    ExternalLoginSerializer, 
    RefreshSerializer, 
    ProviderListSerializer,
    RegisterSerializer
)

from factorial_hr.utils.ip import get_client_ip
from factorial_hr.apps.auth.services.auth_service import AuthService
from factorial_hr.apps.auth.services.email_service import EmailService
from factorial_hr.constants.api import (
    DATA_NOT_FOUND,
    NOT_FILLED_FIELDS,
    WRONG_CREDENTIALS,
)

from factorial_hr.apps.auth.repositories import token_repositories as token_providers
# Configuración de autenticación
REFRESH_TTL_DAYS = getattr(settings, "AUTH_REFRESH_TTL_DAYS", 7)
DEFAULT_PROVIDER = getattr(settings, "DEFAULT_OAUTH_PROVIDER", "google")

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='external-login',  permission_classes=[AllowAny] )
    def external_login(self, request):
        serializer = ExternalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_token = serializer.validated_data["access_token"]
        provider_name = serializer.validated_data.get("provider", DEFAULT_PROVIDER)

        try:
            # Crear instancia del proveedor OAuth
            provider = OAuthProviderFactory.create_provider(provider_name)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        jwks_uri = provider.get_jwks_uri()

        try:
            # Valida el token externo y obtiene claims
            payload = TokenVerifier.verify_token(access_token, jwks_uri, provider.audience)
        except Exception as e:
            return Response({"detail": f"Invalid external token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

        # Extraer datos del usuario usando el proveedor específico
        user_data = provider.extract_user_data(payload)
        email = user_data.get('email')
        name = user_data.get('name')

        if not email:
            # Fallback: intenta userinfo
            try:
                userinfo = provider.get_userinfo(access_token)
                user_data = provider.extract_user_data(userinfo)
                email = user_data.get('email')
                name = user_data.get('name')
            except Exception:
                return Response({"detail": "No email available in token and userinfo failed"}, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({"detail": "No email available from OAuth provider"}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear usuario local
        user = UserRepository.get_or_create_user_by_email(email=email, name=name)

        # Token DRF (access)
        token_obj, _ = Token.objects.get_or_create(user=user)

        # Crear refresh token propio
        refresh_key = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(days=REFRESH_TTL_DAYS)
        refresh_obj = RefreshToken.objects.create(user=user, key=refresh_key, expires_at=expires_at)

        return Response({
            "token": token_obj.key,
            "refresh": refresh_obj.key,
            "user": {
                "id": user.pk,
                "email": user.email,
                "name": user.name,       # tu campo 'name'
                "last_name": user.family_name, # opcional, si quieres
                "full_name": user.user_full_name,
            },
            "provider": provider.get_provider_name(),
            "external_claims": payload
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_key = serializer.validated_data["refresh"]

        try:
            refresh_obj = RefreshToken.objects.get(key=refresh_key, revoked=False)
        except RefreshToken.DoesNotExist:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        if refresh_obj.is_expired():
            return Response({"detail": "Refresh token expired"}, status=status.HTTP_401_UNAUTHORIZED)

        # Optional: rotate refresh token — crear uno nuevo y revocar el anterior
        refresh_obj.revoke()
        new_key = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(days=REFRESH_TTL_DAYS)
        new_refresh = RefreshToken.objects.create(user=refresh_obj.user, key=new_key, expires_at=expires_at)

        # Obtener/crear token DRF (access)
        token_obj, _ = Token.objects.get_or_create(user=refresh_obj.user)

        return Response({
            "token": token_obj.key,
            "refresh": new_refresh.key
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='providers')
    def list_providers(self, request):
        """Lista los proveedores OAuth disponibles y habilitados"""
        try:
            available_providers = OAuthProviderFactory.get_available_providers()
            providers_data = []
            
            for name, config in available_providers.items():
                providers_data.append({
                    'name': name,
                    'display_name': config['display_name'],
                    'well_known_url': config['well_known_url']
                })
            
            serializer = ProviderListSerializer(providers_data, many=True)
            return Response({
                "providers": serializer.data,
                "default_provider": DEFAULT_PROVIDER
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": f"Error retrieving providers: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='external-login/(?P<provider_name>[^/.]+)')
    def external_login_with_provider(self, request, provider_name=None):
        """Login OAuth con proveedor especificado en la URL"""
        if not provider_name:
            return Response({"detail": "Provider name is required in URL"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear un serializer con el proveedor predefinido
        data = request.data.copy()
        data['provider'] = provider_name
        
        serializer = ExternalLoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        access_token = serializer.validated_data["access_token"]

        try:
            # Crear instancia del proveedor OAuth
            provider = OAuthProviderFactory.create_provider(provider_name)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        jwks_uri = provider.get_jwks_uri()

        try:
            # Valida el token externo y obtiene claims
            payload = TokenVerifier.verify_token(access_token, jwks_uri, provider.audience)
        except Exception as e:
            return Response({"detail": f"Invalid external token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

        # Extraer datos del usuario usando el proveedor específico
        user_data = provider.extract_user_data(payload)
        email = user_data.get('email')
        name = user_data.get('name')

        if not email:
            # Fallback: intenta userinfo
            try:
                userinfo = provider.get_userinfo(access_token)
                user_data = provider.extract_user_data(userinfo)
                email = user_data.get('email')
                name = user_data.get('name')
            except Exception:
                return Response({"detail": "No email available in token and userinfo failed"}, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({"detail": "No email available from OAuth provider"}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear usuario local
        user = UserRepository.get_or_create_user_by_email(email=email, name=name)

        # Token DRF (access)
        token_obj, _ = Token.objects.get_or_create(user=user)

        # Crear refresh token propio
        refresh_key = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(days=REFRESH_TTL_DAYS)
        refresh_obj = RefreshToken.objects.create(user=user, key=refresh_key, expires_at=expires_at)

        return Response({
            "token": token_obj.key,
            "refresh": refresh_obj.key,
            "user": {
                "id": user.pk,
                "email": getattr(user, "email", None),
                "first_name": getattr(user, "first_name", None),
            },
            "provider": provider.get_provider_name(),
            "external_claims": payload
        }, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["POST"],
        url_name="login_with_email_password",
        url_path="login",
        permission_classes=[AllowAny],
    )
    def login_with_email_password(self, request):
        """
        Autenticación de usuario local con email y password.
        """
        email = request.data.get("email")
        password = request.data.get("password")
        ip_address = get_client_ip(request=request)

        if not email or not password:
            return Response(data=NOT_FILLED_FIELDS, status=status.HTTP_400_BAD_REQUEST)
        user, token = AuthService.login(
            email=email, password=password, ip_address=ip_address
        )
        if not user or not token:
            return Response(data=WRONG_CREDENTIALS, status=status.HTTP_400_BAD_REQUEST)
       
        return Response({
            "user": user.email,
            "token": token
        })
    
    @action(
        detail=False,
        methods=["POST"],
        url_name="logout",
        url_path="logout",
    )
    def logout(self, request):
        user = request.user
        if not user:
            return Response(DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        user.ip_addresses.pop(get_client_ip(request), None)
        user.save(update_fields=["ip_addresses"])
        if token_providers.remove_token_on_logout(user.uuid):
            return Response(
                {"detail": "Logout exitoso. Token invalidado."},
                status=status.HTTP_200_OK,
            )

    @action(
        detail=False,
        methods=["POST"],
        url_name="register",
        url_path="register",
        permission_classes=[AllowAny],
    )
    def register(self, request):
        """
        Registro de usuario local.
        Requiere: name, last_name, family_name, email, password, password_confirmation
        """
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "detail": "Error en los datos proporcionados",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Crear el usuario
            user = serializer.save()
            
            # Crear token de verificación de email
            verification_token = EmailVerificationToken.objects.create(user=user)
            
            # Enviar correo de bienvenida con link de verificación
            email_sent = EmailService.send_welcome_email(
                user_email=user.email,
                user_name=user.name,
                verification_token=verification_token.token
            )
            
            # Crear token de autenticación para el usuario
            token_obj, _ = Token.objects.get_or_create(user=user)
            
            # Crear refresh token
            refresh_key = uuid.uuid4().hex
            expires_at = timezone.now() + timedelta(days=REFRESH_TTL_DAYS)
            refresh_obj = RefreshToken.objects.create(
                user=user,
                key=refresh_key,
                expires_at=expires_at
            )
            
            return Response(
                {
                    "detail": "Usuario registrado exitosamente. Por favor verifica tu correo electrónico.",
                    "email_sent": email_sent,
                    "email_verified": user.email_verified,
                    "user": {
                        "id": user.pk,
                        "email": user.email,
                        "name": user.name,
                        "last_name": user.last_name,
                        "family_name": user.family_name,
                        "full_name": user.user_full_name,
                    },
                    "token": token_obj.key,
                    "refresh": refresh_obj.key,
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {
                    "detail": "Error al registrar el usuario",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(
        detail=False,
        methods=["POST"],
        url_name="verify_email",
        url_path="verify-email",
        permission_classes=[AllowAny],
    )
    def verify_email(self, request):
        """
        Verifica el email del usuario mediante el token enviado por correo
        """
        token = request.data.get("token")
        
        if not token:
            return Response(
                {"detail": "Token es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Buscar el token
            verification_token = EmailVerificationToken.objects.get(token=token)
            
            # Verificar si el token es válido
            if not verification_token.is_valid():
                if verification_token.is_used:
                    return Response(
                        {"detail": "Este token ya ha sido utilizado"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if verification_token.is_expired():
                    return Response(
                        {"detail": "Este token ha expirado. Solicita un nuevo enlace de verificación."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Marcar el email como verificado
            user = verification_token.user
            user.email_verified = True
            user.save(update_fields=['email_verified'])
            
            # Marcar el token como usado
            verification_token.mark_as_used()
            
            return Response(
                {
                    "detail": "Email verificado exitosamente",
                    "user": {
                        "id": user.pk,
                        "email": user.email,
                        "name": user.name,
                        "email_verified": user.email_verified,
                    }
                },
                status=status.HTTP_200_OK
            )
            
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"detail": "Token inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    "detail": "Error al verificar el email",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(
        detail=False,
        methods=["POST"],
        url_name="resend_verification",
        url_path="resend-verification",
        permission_classes=[AllowAny],
    )
    def resend_verification(self, request):
        """
        Reenvía el correo de verificación al usuario
        """
        email = request.data.get("email")
        
        if not email:
            return Response(
                {"detail": "Email es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Buscar el usuario
            user = UserRepository.get_user_by_email(email=email)
            
            if not user:
                return Response(
                    {"detail": "Usuario no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar si ya está verificado
            if user.email_verified:
                return Response(
                    {"detail": "Este email ya está verificado"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Invalidar tokens anteriores (opcional, marcarlos como usados)
            EmailVerificationToken.objects.filter(
                user=user, 
                is_used=False
            ).update(is_used=True)
            
            # Crear nuevo token
            verification_token = EmailVerificationToken.objects.create(user=user)
            
            # Enviar correo
            email_sent = EmailService.send_welcome_email(
                user_email=user.email,
                user_name=user.name,
                verification_token=verification_token.token
            )
            
            return Response(
                {
                    "detail": "Correo de verificación reenviado exitosamente",
                    "email_sent": email_sent
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {
                    "detail": "Error al reenviar el correo de verificación",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    