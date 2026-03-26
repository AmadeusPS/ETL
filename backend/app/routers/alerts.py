from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import AlertRead
from app.routers.deps import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertRead])
def list_alerts(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Alert).filter(Alert.user_id == current_user.id)
    if unread_only:
        q = q.filter(Alert.is_read == False)  # noqa: E712
    return q.order_by(Alert.created_at.desc()).limit(limit).all()


@router.patch("/{alert_id}/read", response_model=AlertRead)
def mark_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = db.query(Alert).filter(
        Alert.id == alert_id, Alert.user_id == current_user.id
    ).first()
    if alert:
        alert.is_read = True
        db.commit()
        db.refresh(alert)
    return alert
