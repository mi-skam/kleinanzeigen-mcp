"""Input validators for Kleinanzeigen MCP."""

import re
from typing import Optional

from .constants import (
    MAX_LOCATION_LENGTH,
    MAX_PAGE_COUNT,
    MAX_PRICE,
    MAX_QUERY_LENGTH,
    MAX_RADIUS,
    MIN_PAGE_COUNT,
    MIN_PRICE,
    MIN_RADIUS,
    VALID_SORT_OPTIONS,
)


class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


def validate_query(query: Optional[str]) -> Optional[str]:
    """Validate and sanitize search query.

    Args:
        query: Search query string

    Returns:
        Sanitized query or None

    Raises:
        ValidationError: If query is invalid
    """
    if not query:
        return None

    # Remove extra whitespace
    query = " ".join(query.split())

    if len(query) > MAX_QUERY_LENGTH:
        raise ValidationError(f"Query too long (max {MAX_QUERY_LENGTH} characters)")

    # Basic XSS prevention - remove script tags and dangerous characters
    if re.search(r"<script|javascript:|on\w+=", query, re.IGNORECASE):
        raise ValidationError("Invalid characters in query")

    return query


def validate_location(location: Optional[str]) -> Optional[str]:
    """Validate location string.

    Args:
        location: Location string

    Returns:
        Validated location or None

    Raises:
        ValidationError: If location is invalid
    """
    if not location:
        return None

    location = location.strip()

    if len(location) > MAX_LOCATION_LENGTH:
        raise ValidationError(f"Location too long (max {MAX_LOCATION_LENGTH} characters)")

    # Allow alphanumeric, spaces, commas, and German characters
    if not re.match(r"^[\w\s,äöüßÄÖÜ\-]+$", location):
        raise ValidationError("Invalid location format")

    return location


def validate_price(price: Optional[int], field_name: str = "price") -> Optional[int]:
    """Validate price value.

    Args:
        price: Price in euros
        field_name: Field name for error messages

    Returns:
        Validated price or None

    Raises:
        ValidationError: If price is invalid
    """
    if price is None:
        return None

    if not isinstance(price, int):
        raise ValidationError(f"{field_name} must be an integer")

    if price < MIN_PRICE or price > MAX_PRICE:
        raise ValidationError(f"{field_name} must be between {MIN_PRICE} and {MAX_PRICE}")

    return price


def validate_radius(radius: Optional[int]) -> Optional[int]:
    """Validate search radius.

    Args:
        radius: Radius in kilometers

    Returns:
        Validated radius or None

    Raises:
        ValidationError: If radius is invalid
    """
    if radius is None:
        return None

    if not isinstance(radius, int):
        raise ValidationError("Radius must be an integer")

    if radius < MIN_RADIUS or radius > MAX_RADIUS:
        raise ValidationError(f"Radius must be between {MIN_RADIUS} and {MAX_RADIUS} km")

    return radius


def validate_page_count(page_count: Optional[int]) -> int:
    """Validate page count.

    Args:
        page_count: Number of pages to fetch

    Returns:
        Validated page count

    Raises:
        ValidationError: If page count is invalid
    """
    if page_count is None:
        return MIN_PAGE_COUNT

    if not isinstance(page_count, int):
        raise ValidationError("Page count must be an integer")

    if page_count < MIN_PAGE_COUNT or page_count > MAX_PAGE_COUNT:
        raise ValidationError(f"Page count must be between {MIN_PAGE_COUNT} and {MAX_PAGE_COUNT}")

    return page_count


def validate_sort(sort: Optional[str]) -> str:
    """Validate sort option.

    Args:
        sort: Sort option

    Returns:
        Validated sort option

    Raises:
        ValidationError: If sort option is invalid
    """
    if not sort:
        return VALID_SORT_OPTIONS[0]

    if sort not in VALID_SORT_OPTIONS:
        raise ValidationError(f"Sort must be one of: {', '.join(VALID_SORT_OPTIONS)}")

    return sort


def validate_listing_id(listing_id: str) -> str:
    """Validate listing ID format.

    Args:
        listing_id: Listing ID

    Returns:
        Validated listing ID

    Raises:
        ValidationError: If listing ID is invalid
    """
    if not listing_id:
        raise ValidationError("Listing ID is required")

    # Remove any whitespace
    listing_id = listing_id.strip()

    # Listing IDs should be numeric strings
    if not re.match(r"^\d+$", listing_id):
        raise ValidationError("Invalid listing ID format")

    return listing_id


def validate_category(category: Optional[str]) -> Optional[str]:
    """Validate category IDs.

    Args:
        category: Comma-separated category IDs

    Returns:
        Validated category string or None

    Raises:
        ValidationError: If category format is invalid
    """
    if not category:
        return None

    # Category should be comma-separated numeric IDs
    category_ids = category.split(",")
    for cat_id in category_ids:
        if not re.match(r"^\d+$", cat_id.strip()):
            raise ValidationError(f"Invalid category ID: {cat_id}")

    return ",".join(cat_id.strip() for cat_id in category_ids)