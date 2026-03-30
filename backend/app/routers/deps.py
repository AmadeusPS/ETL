"""
FastAPI dependency injection: current user extraction from Azure AD B2C JWT.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.cognito import verify_b2c_token

bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    claims = verify_b2c_token(credentials.credentials)
    # B2C uses 'oid' (object ID) as the stable user identifier
    b2c_sub = claims.get("oid") or claims.get("sub")

    user = db.query(User).filter(User.cognito_sub == b2c_sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user
