# factorial_hr/apps/auth/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import uuid

from factorial_hr.apps.auth.services.oauth_provider_client import OAuthProviderFactory, OAuthProviderClient
from factorial_hr.apps.auth.services.token_verifier import TokenVerifier
from factorial_hr.apps.users.repositories.user_repository import UserRepository
from factorial_hr.apps.auth.models import RefreshToken
from factorial_hr.apps.auth.api.serializers import (
    ExternalLoginSerializer, 
    RefreshSerializer, 
    ProviderListSerializer
)

from factorial_hr.utils.ip import get_client_ip
from factorial_hr.apps.auth.services.auth_service import AuthService
from factorial_hr.constants.api import (
    DATA_NOT_FOUND,
    NOT_FILLED_FIELDS,
    WRONG_CREDENTIALS,
)
# Configuración de autenticación
REFRESH_TTL_DAYS = getattr(settings, "AUTH_REFRESH_TTL_DAYS", 7)
DEFAULT_PROVIDER = getattr(settings, "DEFAULT_OAUTH_PROVIDER", "google")

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='external-login')
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
