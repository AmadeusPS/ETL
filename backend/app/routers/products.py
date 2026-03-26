from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.competitor_product import CompetitorProduct
from app.schemas.product import (
    ProductCreate, ProductRead, ProductUpdate,
    CompetitorProductCreate, CompetitorProductRead,
)
from app.routers.deps import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRead])
def list_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Product).filter(Product.user_id == current_user.id).all()


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = Product(**payload.model_dump(), user_id=current_user.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(product)
    db.commit()


# ---------------------------------------------------------------------------
# Competitor products nested under a store (simplified endpoint)
# ---------------------------------------------------------------------------

@router.get("/competitors/", response_model=list[CompetitorProductRead])
def list_competitor_products(
    store_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(CompetitorProduct)
        .join(CompetitorProduct.store)
        .filter(CompetitorProduct.store.has(user_id=current_user.id), CompetitorProduct.store_id == store_id)
        .all()
    )


@router.post("/competitors/", response_model=CompetitorProductRead, status_code=status.HTTP_201_CREATED)
def add_competitor_product(
    payload: CompetitorProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cp = CompetitorProduct(**payload.model_dump())
    db.add(cp)
    db.commit()
    db.refresh(cp)
    return cp
