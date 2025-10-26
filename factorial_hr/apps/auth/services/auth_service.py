# factorial_hr/apps/auth/services/auth_service.py
from typing import Optional, Tuple
from django.contrib.auth import authenticate
from factorial_hr.apps.users.repositories.user_repository import UserRepository
from factorial_hr.apps.auth.repositories import token_repositories as token_providers

class AuthService:
    """
    Servicio encargado de manejar la autenticación de usuarios,
    generación de tokens y registro de IP.
    """

    @staticmethod
    def login(email: str, password: str, ip_address: str) -> Tuple[Optional[object], Optional[str]]:
        """
        Autentica un usuario, genera un token y registra su IP.

        Args:
            email (str): Email del usuario.
            password (str): Contraseña del usuario.
            ip_address (str): Dirección IP del cliente.

        Returns:
            Tuple[Optional[User], Optional[str]]: Usuario y token si es válido, None si falla.
        """
        user = authenticate(username=email, password=password)
        if user:
            token = token_providers.remove_token_by_user_uuid(
                user_uuid=str(user.uuid), generate_new_token=True
            )
            UserRepository.add_ip_address_by_user(user=user, ip_address=ip_address)
            return user, token.key
        return None, None
