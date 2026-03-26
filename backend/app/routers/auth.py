"""
Auth router – handles post-Cognito registration sync (create local user record).
Login/logout are handled entirely by Cognito Hosted UI / Amplify SDK.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, PlanTier
from app.schemas.user import UserCreate, UserRead
from app.services.cognito import verify_cognito_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    """
    Called by the frontend after Cognito signup.
    Creates the local user + default 'basic' subscription.
    """
    claims = verify_cognito_token(credentials.credentials)
    cognito_sub = claims["sub"]
    email = claims.get("email", "")

    existing = db.query(User).filter(User.cognito_sub == cognito_sub).first()
    if existing:
        return existing

    user = User(cognito_sub=cognito_sub, email=email)
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
    claims = verify_cognito_token(credentials.credentials)
    user = db.query(User).filter(User.cognito_sub == claims["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not registered")
    return user
