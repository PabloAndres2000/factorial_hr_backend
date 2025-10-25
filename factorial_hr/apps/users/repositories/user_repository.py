# factorial_hr/apps/auth/repositories/user_repository.py
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRepository:
    @staticmethod
    def get_or_create_user_by_email(email: str, name: str = None, family_name: str = None):
        if not email:
            raise ValueError("Email is required")
        
        defaults = {}
        if name:
            defaults["name"] = name
        if family_name:
            defaults["family_name"] = family_name
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults=defaults
        )
        return user