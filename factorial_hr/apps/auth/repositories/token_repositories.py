
from typing import Optional

from rest_framework.authtoken.models import Token
from factorial_hr.apps.users.repositories.user_repository import UserRepository

def remove_token_by_user_uuid(
    user_uuid: str, generate_new_token=False
) -> Optional[Token]:
    """
    Method for generate token by user uuid

    Parameters:
        user_uuid (str): The UUID of the user.
        generate_new_token (bool): token generator

    Returns:
        Optional[Token]: returns the token instance if found, otherwise None.
    """
    user = UserRepository.get_user_by_uuid(uuid=user_uuid)
    if not user:
        return None

    if Token.objects.filter(user=user):
        user.auth_token.delete()
    if generate_new_token:
        token = Token.objects.create(user=user)
        return token
    return None


def remove_token_on_logout(user_uuid: str) -> bool:
    """
    Remove the user's token on logout.

    Parameters:
        user_uuid (str): The UUID of the user.

    Returns:
        bool: True if the token was successfully removed, False otherwise.
    """
    user = UserRepository.get_user_by_uuid(uuid=user_uuid)

    if user:
        tokens = Token.objects.filter(user=user)

        if tokens:
            tokens.delete()
            return True

    return False
