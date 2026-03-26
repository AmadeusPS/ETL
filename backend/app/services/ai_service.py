"""
AI service – wraps Anthropic Claude for price recommendations and collection summaries.
"""
import json
import logging
from dataclasses import dataclass
from typing import Optional

import anthropic
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: Optional[anthropic.Anthropic] = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


# ---------------------------------------------------------------------------
# Price recommendation
# ---------------------------------------------------------------------------

@dataclass
class PriceRecommendation:
    suggested_price: float
    reasoning: str
    confidence: str  # low | medium | high


def recommend_price(
    product_name: str,
    current_price: float,
    target_margin: Optional[float],
    competitor_data: list[dict],
) -> PriceRecommendation:
    """
    Ask Claude to suggest an optimal price given competitive context.

    competitor_data format:
    [{"store": "...", "name": "...", "price": 19.99, "currency": "EUR"}, ...]
    """
    context = {
        "product": product_name,
        "our_current_price": current_price,
        "target_margin_pct": target_margin,
        "competitors": competitor_data,
    }

    prompt = f"""You are a pricing strategist for a Portuguese e-commerce brand.
Analyse the competitive data and recommend an optimal retail price.

Context (JSON):
{json.dumps(context, indent=2, ensure_ascii=False)}

Reply in JSON with this exact structure:
{{
  "suggested_price": <number>,
  "reasoning": "<1-2 sentence explanation in Portuguese>",
  "confidence": "low|medium|high"
}}
Only return the JSON, no other text."""

    message = get_client().messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    data = json.loads(raw)

    return PriceRecommendation(
        suggested_price=float(data["suggested_price"]),
        reasoning=data["reasoning"],
        confidence=data.get("confidence", "medium"),
    )


# ---------------------------------------------------------------------------
# New collection summary
# ---------------------------------------------------------------------------

@dataclass
class CollectionSummary:
    summary: str
    key_trends: list[str]
    item_count: int


def summarise_new_collection(store_name: str, products: list[dict]) -> CollectionSummary:
    """
    Ask Claude to summarise a competitor's new collection.

    products format: [{"name": "...", "price": 29.99, "category": "..."}, ...]
    """
    prompt = f"""You are a fashion/retail analyst for a Portuguese brand.
Summarise this new collection from competitor "{store_name}".

Products (JSON):
{json.dumps(products, indent=2, ensure_ascii=False)}

Reply in JSON:
{{
  "summary": "<2-3 sentences in Portuguese describing the collection focus>",
  "key_trends": ["trend1", "trend2", "trend3"],
  "item_count": {len(products)}
}}
Only return the JSON."""

    message = get_client().messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    data = json.loads(raw)

    return CollectionSummary(
        summary=data["summary"],
        key_trends=data.get("key_trends", []),
        item_count=data.get("item_count", len(products)),
    )
