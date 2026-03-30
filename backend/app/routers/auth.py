"""
Auth router – handles post-B2C registration sync (create local user record).
Login/logout are handled entirely by Azure AD B2C / MSAL SDK on the frontend.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, PlanTier
from app.schemas.user import UserCreate, UserRead
from app.services.cognito import verify_b2c_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    """
    Called by the frontend after B2C signup redirect.
    Creates the local user record + default 'basic' subscription.
    B2C 'oid' claim is used as the stable user identifier (stored in cognito_sub column).
    """
    claims = verify_b2c_token(credentials.credentials)
    # B2C uses 'oid' (object ID) as the stable unique identifier across policies
    b2c_sub = claims.get("oid") or claims["sub"]
    # B2C returns email in 'emails' array or 'email' claim depending on user flow version
    emails = claims.get("emails", [])
    email = emails[0] if emails else claims.get("email", "")

    existing = db.query(User).filter(User.cognito_sub == b2c_sub).first()
    if existing:
        return existing

    user = User(cognito_sub=b2c_sub, email=email)
    db.add(user)
    db.flush()

    subscription = Subscription(user_id=user.id, plan=PlanTier.basic, status="active")
    db.add(subscription)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserRead)
def me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    claims = verify_b2c_token(credentials.credentials)
    b2c_sub = claims.get("oid") or claims["sub"]
    user = db.query(User).filter(User.cognito_sub == b2c_sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not registered")
    return user
