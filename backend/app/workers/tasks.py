"""
Celery tasks:
  1. scrape_all_active_urls  – fan-out task that enqueues individual scrapes
  2. scrape_competitor_product – scrape one URL, detect price changes
  3. generate_price_recommendation – call Claude for a single product
  4. generate_collection_summary – call Claude for new products from a store
"""
import json
import logging
from datetime import datetime

from celery import group
from sqlalchemy.orm import Session

from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.competitor_product import CompetitorProduct
from app.models.price_snapshot import PriceSnapshot
from app.models.alert import Alert, AlertType
from app.models.ai_recommendation import AIRecommendation
from app.services.scraper import scrape_url
from app.services.ai_service import recommend_price, summarise_new_collection

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Fan-out: enqueue one scrape task per active competitor product
# ---------------------------------------------------------------------------

@celery_app.task(name="app.workers.tasks.scrape_all_active_urls")
def scrape_all_active_urls():
    """Triggered by Celery Beat or EventBridge → Lambda."""
    db: Session = SessionLocal()
    try:
        ids = [
            row.id
            for row in db.query(CompetitorProduct.id)
            .filter(CompetitorProduct.is_active == True)  # noqa: E712
            .all()
        ]
        logger.info("Enqueueing %d scrape tasks", len(ids))
        job = group(scrape_competitor_product.s(cp_id) for cp_id in ids)
        job.apply_async()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 2. Scrape one competitor product URL
# ---------------------------------------------------------------------------

@celery_app.task(
    name="app.workers.tasks.scrape_competitor_product",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def scrape_competitor_product(self, competitor_product_id: int):
    db: Session = SessionLocal()
    try:
        cp = db.query(CompetitorProduct).get(competitor_product_id)
        if not cp or not cp.is_active:
            return

        try:
            result = scrape_url(cp.url)
        except Exception as exc:
            logger.warning("Scrape failed for %s: %s", cp.url, exc)
            raise self.retry(exc=exc)

        # Save snapshot
        if result.price is not None:
            snapshot = PriceSnapshot(
                competitor_product_id=cp.id,
                price=result.price,
                currency=result.currency or cp.currency,
                scraped_at=datetime.utcnow(),
            )
            db.add(snapshot)

            old_price = cp.current_price
            cp.previous_price = old_price
            cp.current_price = result.price
            cp.last_scraped_at = datetime.utcnow()
            if result.name:
                cp.name = result.name
            if result.in_stock is not None:
                cp.in_stock = result.in_stock

            db.flush()

            # Detect price change and create alert
            if old_price and abs(old_price - result.price) / old_price > 0.01:
                alert_type = AlertType.price_drop if result.price < old_price else AlertType.price_increase
                change_pct = ((result.price - old_price) / old_price) * 100
                alert = Alert(
                    user_id=cp.store.user_id,
                    alert_type=alert_type,
                    message=(
                        f"{cp.store.name} alterou o preço de '{cp.name}': "
                        f"€{old_price:.2f} → €{result.price:.2f} ({change_pct:+.1f}%)"
                    ),
                    competitor_product_id=cp.id,
                )
                db.add(alert)

        db.commit()
        logger.info("Scraped %s – price: %s", cp.url, result.price)

    finally:
        db.close()


# ---------------------------------------------------------------------------
# 3. AI price recommendation for a client product
# ---------------------------------------------------------------------------

@celery_app.task(name="app.workers.tasks.generate_price_recommendation")
def generate_price_recommendation(product_id: int):
    from app.models.product import Product

    db: Session = SessionLocal()
    try:
        product = db.query(Product).get(product_id)
        if not product:
            return

        # Gather latest competitor prices for this product's category
        from app.models.competitor_product import CompetitorProduct as CP
        competitors = (
            db.query(CP)
            .join(CP.store)
            .filter(CP.store.has(user_id=product.user_id), CP.is_active == True)  # noqa
            .limit(20)
            .all()
        )
        competitor_data = [
            {
                "store": cp.store.name,
                "name": cp.name,
                "price": float(cp.current_price) if cp.current_price else None,
                "currency": cp.currency,
            }
            for cp in competitors
            if cp.current_price
        ]

        context_input = json.dumps(
            {
                "product": product.name,
                "our_price": float(product.current_price) if product.current_price else None,
                "target_margin": float(product.target_margin) if product.target_margin else None,
                "competitors": competitor_data,
            }
        )

        recommendation = recommend_price(
            product_name=product.name,
            current_price=float(product.current_price or 0),
            target_margin=float(product.target_margin) if product.target_margin else None,
            competitor_data=competitor_data,
        )

        rec = AIRecommendation(
            product_id=product.id,
            context_input=context_input,
            claude_output=json.dumps(
                {
                    "suggested_price": recommendation.suggested_price,
                    "reasoning": recommendation.reasoning,
                    "confidence": recommendation.confidence,
                }
            ),
            suggested_price=recommendation.suggested_price,
            reasoning=recommendation.reasoning,
        )
        db.add(rec)
        db.commit()
        logger.info("AI recommendation created for product %d: €%.2f", product_id, recommendation.suggested_price)

    finally:
        db.close()


# ---------------------------------------------------------------------------
# 4. AI collection summary when new products are detected on a store
# ---------------------------------------------------------------------------

@celery_app.task(name="app.workers.tasks.generate_collection_summary")
def generate_collection_summary(store_id: int, new_product_ids: list[int]):
    from app.models.store import Store

    db: Session = SessionLocal()
    try:
        store = db.query(Store).get(store_id)
        if not store:
            return

        products = (
            db.query(CompetitorProduct)
            .filter(CompetitorProduct.id.in_(new_product_ids))
            .all()
        )
        product_list = [
            {"name": p.name, "price": float(p.current_price) if p.current_price else None}
            for p in products
        ]

        summary = summarise_new_collection(store_name=store.name, products=product_list)

        alert = Alert(
            user_id=store.user_id,
            alert_type=AlertType.new_product,
            message=(
                f"Nova colecção detectada em {store.name} ({summary.item_count} items): "
                f"{summary.summary} Tendências: {', '.join(summary.key_trends)}."
            ),
        )
        db.add(alert)
        db.commit()
        logger.info("Collection summary created for store %d", store_id)

    finally:
        db.close()
