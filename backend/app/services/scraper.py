"""
Web scraping service.
Uses requests + BeautifulSoup for simple HTML pages.
Falls back to Playwright for JS-rendered pages.
"""
import re
import time
import logging
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


@dataclass
class ScrapedProduct:
    url: str
    name: Optional[str]
    price: Optional[float]
    currency: str
    in_stock: Optional[bool]
    image_url: Optional[str]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def scrape_url(url: str, use_playwright: bool = False) -> ScrapedProduct:
    """
    Scrape a single product URL and return structured data.
    Set use_playwright=True for JS-heavy sites.
    """
    if use_playwright:
        return _scrape_with_playwright(url)
    return _scrape_with_requests(url)


def _scrape_with_requests(url: str) -> ScrapedProduct:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    return _parse_product(url, soup)


def _scrape_with_playwright(url: str) -> ScrapedProduct:
    """Playwright scraping for JS-rendered pages (e.g. React/Vue storefronts)."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30_000)
            page.wait_for_load_state("networkidle", timeout=15_000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "lxml")
        return _parse_product(url, soup)
    except Exception as exc:
        logger.warning("Playwright failed for %s: %s – falling back to requests", url, exc)
        return _scrape_with_requests(url)


def _parse_product(url: str, soup: BeautifulSoup) -> ScrapedProduct:
    """
    Generic parser – reads common meta tags and schema.org JSON-LD.
    Extend with site-specific selectors as needed.
    """
    name = _extract_name(soup)
    price, currency = _extract_price(soup)
    in_stock = _extract_stock(soup)
    image_url = _extract_image(soup)

    return ScrapedProduct(
        url=url,
        name=name,
        price=price,
        currency=currency,
        in_stock=in_stock,
        image_url=image_url,
    )


def _extract_name(soup: BeautifulSoup) -> Optional[str]:
    for selector in [
        'meta[property="og:title"]',
        'h1[itemprop="name"]',
        "h1.product-title",
        "h1",
    ]:
        el = soup.select_one(selector)
        if el:
            return (el.get("content") or el.get_text()).strip()
    return None


def _extract_price(soup: BeautifulSoup) -> tuple[Optional[float], str]:
    # Try schema.org price
    price_el = soup.select_one('[itemprop="price"]')
    if price_el:
        raw = price_el.get("content") or price_el.get_text()
        price = _parse_price_string(raw)
        if price:
            return price, "EUR"

    # Try og:price
    for meta in soup.select('meta[property^="product:price"]'):
        raw = meta.get("content", "")
        price = _parse_price_string(raw)
        if price:
            currency = soup.select_one('meta[property="product:price:currency"]')
            cur = currency.get("content", "EUR") if currency else "EUR"
            return price, cur

    # Fallback: first element with "price" in class
    for el in soup.select('[class*="price"]'):
        price = _parse_price_string(el.get_text())
        if price:
            return price, "EUR"

    return None, "EUR"


def _parse_price_string(text: str) -> Optional[float]:
    match = re.search(r"[\d]+[.,]?\d*", text.replace(",", "."))
    if match:
        try:
            return float(match.group())
        except ValueError:
            pass
    return None


def _extract_stock(soup: BeautifulSoup) -> Optional[bool]:
    availability = soup.select_one('[itemprop="availability"]')
    if availability:
        content = (availability.get("content") or availability.get_text()).lower()
        return "instock" in content or "in stock" in content
    return None


def _extract_image(soup: BeautifulSoup) -> Optional[str]:
    og_image = soup.select_one('meta[property="og:image"]')
    if og_image:
        return og_image.get("content")
    img = soup.select_one('img[itemprop="image"], img.product-image, img.main-image')
    if img:
        return img.get("src")
    return None
