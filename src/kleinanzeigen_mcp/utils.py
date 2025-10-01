"""Utility functions for Kleinanzeigen MCP."""

import logging
from typing import List, Optional

from .models import Listing, ListingImage

logger = logging.getLogger(__name__)


def parse_location(location_data: dict) -> str:
    """Parse location data into formatted string."""
    if not location_data:
        return ""

    city = location_data.get("city", "")
    state = location_data.get("state", "")

    if city and state:
        return f"{city}, {state}"
    return city or state or ""


def parse_price(price_value) -> str:
    """Parse price value into formatted string."""
    if price_value is None or price_value == "":
        return ""

    if price_value == "0" or price_value == 0:
        return "Auf Anfrage"

    return f"€ {price_value}"


def parse_seller(seller_data: dict) -> str:
    """Parse seller data into name string."""
    if not seller_data:
        return ""
    return seller_data.get("name", "")


def parse_shipping(shipping_value: bool) -> str:
    """Parse shipping boolean into German text."""
    if shipping_value is None:
        return ""
    return "Versand möglich" if shipping_value else "Nur Abholung"


def parse_images(image_urls: List[str]) -> List[ListingImage]:
    """Convert image URLs to ListingImage objects."""
    return [ListingImage(url=url) for url in (image_urls or [])]


def build_kleinanzeigen_url(adid: str) -> str:
    """Build Kleinanzeigen URL from ad ID."""
    if not adid:
        return ""
    return f"https://www.kleinanzeigen.de/s-anzeige/{adid}"


def parse_listing_from_api(item: dict, listing_id: Optional[str] = None) -> Listing:
    """Parse API response item into Listing model.

    Args:
        item: API response item dictionary
        listing_id: Optional listing ID to use if not in item

    Returns:
        Parsed Listing object
    """
    try:
        adid = item.get("adid", listing_id or "")

        return Listing(
            id=adid,
            title=item.get("title", ""),
            price=parse_price(item.get("price")),
            location=parse_location(item.get("location")),
            date=item.get("upload_date"),
            url=build_kleinanzeigen_url(adid),
            description=item.get("description"),
            images=parse_images(item.get("images", [])),
            seller=parse_seller(item.get("seller")),
            shipping=parse_shipping(item.get("shipping")),
        )
    except Exception as e:
        logger.error(f"Error parsing listing from API: {e}", exc_info=True)
        raise


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length with ellipsis."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + "..."