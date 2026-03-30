"""
Azure AD B2C token verification and user info extraction.
Validates JWT tokens issued by Azure AD B2C user flows.

Replaces the former AWS Cognito JWT verification.
"""
import time
from functools import lru_cache
import httpx
from jose import jwk, jwt
from jose.utils import base64url_decode
from fastapi import HTTPException, status
from app.config import get_settings

settings = get_settings()


def _jwks_url() -> str:
    return (
        f"https://{settings.b2c_tenant_name}.b2clogin.com/"
        f"{settings.b2c_tenant_name}.onmicrosoft.com/"
        f"{settings.b2c_policy_name}/discovery/v2.0/keys"
    )


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    response = httpx.get(_jwks_url(), timeout=10)
    response.raise_for_status()
    return response.json()


def verify_b2c_token(token: str) -> dict:
    """
    Verify an Azure AD B2C JWT and return the decoded claims.
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

        if claims.get("aud") != settings.b2c_client_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")

        return claims

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token validation error: {exc}"
        ) from exc


def get_plan_from_claims(claims: dict) -> str:
    """
    Extract plan tier from B2C custom attribute.
    In B2C, custom attributes are surfaced as 'extension_plan' in token claims.
    """
    plan = claims.get("extension_plan", "basic")
    if plan in ("enterprise", "pro", "basic"):
        return plan
    return "basic"
