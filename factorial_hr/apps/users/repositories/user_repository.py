# factorial_hr/apps/auth/repositories/user_repository.py
from typing import Optional
from django.contrib.auth import get_user_model
from datetime import datetime
User = get_user_model()

class UserRepository:
    @staticmethod
    def get_or_create_user_by_email(
        email: str,
        name: Optional[str] = None,
        family_name: Optional[str] = None
    ) -> User:
        """
        Obtiene o crea un usuario basado en el email. Si el usuario no existe,
        lo crea usando los datos proporcionados.

        Args:
            email (str): Correo electrónico del usuario.
            name (Optional[str]): Nombre del usuario, opcional.
            family_name (Optional[str]): Apellido(s) del usuario, opcional.

        Returns:
            User: Instancia del usuario existente o creada.
        """
        if not email:
            raise ValueError("Email is required")
        
        defaults = {}
        if name:
            defaults["name"] = name
        if family_name:
            defaults["family_name"] = family_name
        
        user, _ = User.objects.get_or_create(
            email=email,
            defaults=defaults
        )
        return user

    @staticmethod
    def get_user_by_uuid(uuid: str) -> Optional[User]:
        """
        Busca y retorna un usuario usando su UUID.

        Args:
            uuid (str): UUID del usuario.

        Returns:
            Optional[User]: Usuario si existe, de lo contrario None.
        """
        try:
            return User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            return None
    @staticmethod
    def add_ip_address_by_user(user: User, ip_address: str) -> None:
        if not user.ip_addresses.get(ip_address):
            user.ip_addresses[ip_address] = str(datetime.now())
            user.save(update_fields=["ip_addresses", "updated_at"])
