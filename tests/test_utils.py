"""Unit tests for utility functions."""

import pytest

from kleinanzeigen_mcp.models import ListingImage
from kleinanzeigen_mcp.utils import (
    build_kleinanzeigen_url,
    parse_images,
    parse_listing_from_api,
    parse_location,
    parse_price,
    parse_seller,
    parse_shipping,
    truncate_text,
)


class TestParseLocation:
    """Test location parsing."""

    def test_parse_location_full(self):
        """Test parsing location with city and state."""
        location_data = {"city": "Berlin", "state": "Berlin"}
        assert parse_location(location_data) == "Berlin, Berlin"

    def test_parse_location_city_only(self):
        """Test parsing location with only city."""
        location_data = {"city": "Munich"}
        assert parse_location(location_data) == "Munich"

    def test_parse_location_state_only(self):
        """Test parsing location with only state."""
        location_data = {"state": "Bavaria"}
        assert parse_location(location_data) == "Bavaria"

    def test_parse_location_empty(self):
        """Test parsing empty location."""
        assert parse_location({}) == ""
        assert parse_location(None) == ""


class TestParsePrice:
    """Test price parsing."""

    def test_parse_price_normal(self):
        """Test parsing normal price."""
        assert parse_price(100) == "€ 100"
        assert parse_price("250") == "€ 250"

    def test_parse_price_zero(self):
        """Test parsing zero price."""
        assert parse_price(0) == "Auf Anfrage"
        assert parse_price("0") == "Auf Anfrage"

    def test_parse_price_empty(self):
        """Test parsing empty price."""
        assert parse_price(None) == ""
        assert parse_price("") == ""


class TestParseSeller:
    """Test seller parsing."""

    def test_parse_seller_with_name(self):
        """Test parsing seller with name."""
        seller_data = {"name": "John Doe"}
        assert parse_seller(seller_data) == "John Doe"

    def test_parse_seller_empty(self):
        """Test parsing empty seller."""
        assert parse_seller({}) == ""
        assert parse_seller(None) == ""
        assert parse_seller({"other": "data"}) == ""


class TestParseShipping:
    """Test shipping parsing."""

    def test_parse_shipping_true(self):
        """Test parsing shipping when true."""
        assert parse_shipping(True) == "Versand möglich"

    def test_parse_shipping_false(self):
        """Test parsing shipping when false."""
        assert parse_shipping(False) == "Nur Abholung"

    def test_parse_shipping_none(self):
        """Test parsing shipping when None."""
        assert parse_shipping(None) == ""


class TestParseImages:
    """Test image parsing."""

    def test_parse_images_multiple(self):
        """Test parsing multiple images."""
        urls = ["http://example.com/1.jpg", "http://example.com/2.jpg"]
        images = parse_images(urls)
        assert len(images) == 2
        assert all(isinstance(img, ListingImage) for img in images)
        assert images[0].url == "http://example.com/1.jpg"
        assert images[1].url == "http://example.com/2.jpg"

    def test_parse_images_empty(self):
        """Test parsing empty images."""
        assert parse_images([]) == []
        assert parse_images(None) == []


class TestBuildKleinanzeigenUrl:
    """Test URL building."""

    def test_build_url_valid(self):
        """Test building valid URL."""
        assert build_kleinanzeigen_url("123456") == "https://www.kleinanzeigen.de/s-anzeige/123456"

    def test_build_url_empty(self):
        """Test building URL with empty ID."""
        assert build_kleinanzeigen_url("") == ""
        assert build_kleinanzeigen_url(None) == ""


class TestTruncateText:
    """Test text truncation."""

    def test_truncate_short_text(self):
        """Test truncating short text."""
        text = "Short text"
        assert truncate_text(text) == "Short text"

    def test_truncate_long_text(self):
        """Test truncating long text."""
        text = "x" * 250
        truncated = truncate_text(text, 200)
        assert len(truncated) == 203  # 200 + "..."
        assert truncated.endswith("...")

    def test_truncate_exact_length(self):
        """Test truncating text at exact length."""
        text = "x" * 200
        assert truncate_text(text, 200) == text

    def test_truncate_empty_text(self):
        """Test truncating empty text."""
        assert truncate_text("") == ""
        assert truncate_text(None) == None


class TestParseListingFromApi:
    """Test parsing full listing from API."""

    def test_parse_listing_complete(self):
        """Test parsing complete listing data."""
        api_data = {
            "adid": "123456",
            "title": "Test Item",
            "price": "100",
            "location": {"city": "Berlin", "state": "Berlin"},
            "upload_date": "2024-01-01",
            "description": "Test description",
            "images": ["http://example.com/img1.jpg"],
            "seller": {"name": "Test Seller"},
            "shipping": True
        }

        listing = parse_listing_from_api(api_data)

        assert listing.id == "123456"
        assert listing.title == "Test Item"
        assert listing.price == "€ 100"
        assert listing.location == "Berlin, Berlin"
        assert listing.date == "2024-01-01"
        assert listing.url == "https://www.kleinanzeigen.de/s-anzeige/123456"
        assert listing.description == "Test description"
        assert len(listing.images) == 1
        assert listing.seller == "Test Seller"
        assert listing.shipping == "Versand möglich"

    def test_parse_listing_minimal(self):
        """Test parsing minimal listing data."""
        api_data = {
            "adid": "789",
            "title": "Minimal Item"
        }

        listing = parse_listing_from_api(api_data)

        assert listing.id == "789"
        assert listing.title == "Minimal Item"
        assert listing.price == ""
        assert listing.location == ""
        assert listing.url == "https://www.kleinanzeigen.de/s-anzeige/789"

    def test_parse_listing_with_fallback_id(self):
        """Test parsing listing with fallback ID."""
        api_data = {"title": "No ID Item"}
        listing = parse_listing_from_api(api_data, "fallback123")
        assert listing.id == "fallback123"
        assert listing.url == "https://www.kleinanzeigen.de/s-anzeige/fallback123"

    def test_parse_listing_error(self):
        """Test parsing invalid listing data."""
        # This should raise an exception that gets logged
        with pytest.raises(Exception):
            parse_listing_from_api(None)