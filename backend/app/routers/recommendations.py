from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.ai_recommendation import AIRecommendation
from app.schemas.recommendation import RecommendationRead, RecommendationAction
from app.routers.deps import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/", response_model=list[RecommendationRead])
def list_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(AIRecommendation)
        .join(AIRecommendation.product)
        .filter(AIRecommendation.product.has(user_id=current_user.id))
        .order_by(AIRecommendation.created_at.desc())
        .limit(100)
        .all()
    )


@router.patch("/{rec_id}/action", response_model=RecommendationRead)
def action_recommendation(
    rec_id: int,
    payload: RecommendationAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(AIRecommendation)
        .join(AIRecommendation.product)
        .filter(
            AIRecommendation.id == rec_id,
            AIRecommendation.product.has(user_id=current_user.id),
        )
        .first()
    )
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    rec.status = payload.status
    rec.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(rec)
    return rec
