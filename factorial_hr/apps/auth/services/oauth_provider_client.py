# factorial_hr/apps/auth/services/oauth_provider_client.py
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from django.conf import settings


class OAuthProvider(ABC):
    """Interfaz base para proveedores OAuth"""
    
    def __init__(self, well_known_url: str, audience: str):
        self.well_known_url = well_known_url
        self.audience = audience
        self._config = None

    def _fetch_openid_config(self):
        if self._config is None:
            resp = requests.get(self.well_known_url, timeout=5)
            resp.raise_for_status()
            self._config = resp.json()
        return self._config

    def get_jwks_uri(self):
        return self._fetch_openid_config().get("jwks_uri")

    def get_userinfo(self, access_token: str):
        config = self._fetch_openid_config()
        userinfo_endpoint = config.get("userinfo_endpoint")
        if not userinfo_endpoint:
            raise RuntimeError("Provider does not expose userinfo_endpoint")
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(userinfo_endpoint, headers=headers, timeout=5)
        resp.raise_for_status()
        return resp.json()

    @abstractmethod
    def extract_user_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae datos del usuario del payload del token"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        pass


class GoogleOAuthProvider(OAuthProvider):
    """Proveedor OAuth para Google"""
    
    def extract_user_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'email': payload.get("email"),
            'name': payload.get("name") or payload.get("given_name"),
            'first_name': payload.get("given_name"),
            'last_name': payload.get("family_name"),
            'picture': payload.get("picture"),
        }

    def get_provider_name(self) -> str:
        return "google"


class MicrosoftOAuthProvider(OAuthProvider):
    """Proveedor OAuth para Microsoft/Outlook"""
    
    def extract_user_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'email': payload.get("email") or payload.get("upn") or payload.get("preferred_username"),
            'name': payload.get("name") or payload.get("given_name"),
            'first_name': payload.get("given_name"),
            'last_name': payload.get("family_name"),
            'picture': payload.get("picture"),
        }

    def get_provider_name(self) -> str:
        return "microsoft"


class GitHubOAuthProvider(OAuthProvider):
    """Proveedor OAuth para GitHub"""
    
    def extract_user_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'email': payload.get("email"),
            'name': payload.get("name"),
            'first_name': payload.get("given_name"),
            'last_name': payload.get("family_name"),
            'picture': payload.get("avatar_url"),
        }

    def get_provider_name(self) -> str:
        return "github"


class OAuthProviderFactory:
    """Factory para crear instancias de proveedores OAuth"""
    
    _providers = {
        'google': GoogleOAuthProvider,
        'microsoft': MicrosoftOAuthProvider,
        'github': GitHubOAuthProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: str) -> OAuthProvider:
        """Crea una instancia del proveedor especificado"""
        if provider_name not in cls._providers:
            raise ValueError(f"Proveedor OAuth no soportado: {provider_name}")
        
        oauth_config = getattr(settings, 'OAUTH_PROVIDERS', {})
        provider_config = oauth_config.get(provider_name)
        
        if not provider_config:
            raise ValueError(f"Configuración no encontrada para el proveedor: {provider_name}")
        
        if not provider_config.get('enabled', False):
            raise ValueError(f"Proveedor {provider_name} está deshabilitado")
        
        provider_class = cls._providers[provider_name]
        return provider_class(
            well_known_url=provider_config['well_known_url'],
            audience=provider_config['audience']
        )

    @classmethod
    def get_available_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna los proveedores disponibles y habilitados"""
        oauth_config = getattr(settings, 'OAUTH_PROVIDERS', {})
        available = {}
        
        for name, config in oauth_config.items():
            if config.get('enabled', False) and name in cls._providers:
                available[name] = {
                    'display_name': config.get('display_name', name.title()),
                    'well_known_url': config['well_known_url']
                }
        
        return available


# Clase de compatibilidad hacia atrás
class OAuthProviderClient(OAuthProvider):
    """Clase de compatibilidad hacia atrás"""
    
    def __init__(self, well_known_url: str, audience: str = None):
        super().__init__(well_known_url, audience or "")
    
    def extract_user_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Implementación genérica para compatibilidad
        return {
            'email': payload.get("email") or payload.get("upn") or payload.get("preferred_username"),
            'name': payload.get("name") or payload.get("given_name"),
            'first_name': payload.get("given_name"),
            'last_name': payload.get("family_name"),
        }

    def get_provider_name(self) -> str:
        return "legacy"
