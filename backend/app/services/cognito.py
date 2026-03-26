"""
AWS Cognito token verification and user info extraction.
Validates JWT tokens issued by Cognito User Pool.
"""
import json
import time
from functools import lru_cache
import httpx
from jose import jwk, jwt
from jose.utils import base64url_decode
from fastapi import HTTPException, status
from app.config import get_settings

settings = get_settings()

JWKS_URL = (
    f"https://cognito-idp.{settings.aws_region}.amazonaws.com/"
    f"{settings.cognito_user_pool_id}/.well-known/jwks.json"
)


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    response = httpx.get(JWKS_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def verify_cognito_token(token: str) -> dict:
    """
    Verify a Cognito JWT and return the decoded claims.
    Raises HTTP 401 if invalid.
    """
    try:
        jwks = _get_jwks()
        headers = jwt.get_unverified_headers(token)
        kid = headers.get("kid")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token key")

        public_key = jwk.construct(key)
        message, encoded_sig = token.rsplit(".", 1)
        decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))

        if not public_key.verify(message.encode("utf-8"), decoded_sig):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature verification failed")

        claims = jwt.get_unverified_claims(token)

        if claims.get("exp", 0) < time.time():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

        if claims.get("client_id") != settings.cognito_client_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")

        return claims

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token validation error: {exc}"
        ) from exc


def get_plan_from_claims(claims: dict) -> str:
    """Extract plan tier from Cognito custom claims or groups."""
    groups = claims.get("cognito:groups", [])
    for tier in ("enterprise", "pro", "basic"):
        if tier in groups:
            return tier
    # Fallback to custom attribute
    return claims.get("custom:plan", "basic")
