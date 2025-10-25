# factorial_hr/apps/auth/services/token_verifier.py
import requests
import jwt
from jwt import decode, PyJWKClient


class TokenVerifier:
    @staticmethod
    def get_openid_config(well_known_url: str):
        resp = requests.get(well_known_url, timeout=5)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def get_jwks(jwks_uri: str):
        resp = requests.get(jwks_uri, timeout=5)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def get_public_key_for_kid(jwks_uri: str, kid: str):
        jwks = TokenVerifier.get_jwks(jwks_uri)
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # usa RSAAlgorithm desde jwt.algorithms
                return algorithms.RSAAlgorithm.from_jwk(key)
        return None

    @staticmethod
    def verify_token(token: str, jwks_uri: str, audience: str):
        jwk_client = PyJWKClient(jwks_uri)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        payload = decode(
            token,
            key=signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            options={"verify_exp": True}
        )
        return payload
