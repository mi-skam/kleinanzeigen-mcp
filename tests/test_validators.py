"""Unit tests for input validators."""

import pytest

from kleinanzeigen_mcp.validators import (
    ValidationError,
    validate_category,
    validate_listing_id,
    validate_location,
    validate_page_count,
    validate_price,
    validate_query,
    validate_radius,
    validate_sort,
)


class TestValidateQuery:
    """Test query validation."""

    def test_valid_query(self):
        """Test valid queries."""
        assert validate_query("iPhone 12") == "iPhone 12"
        assert validate_query("  multiple   spaces  ") == "multiple spaces"
        assert validate_query(None) is None
        assert validate_query("") is None

    def test_query_too_long(self):
        """Test query length validation."""
        with pytest.raises(ValidationError, match="Query too long"):
            validate_query("x" * 501)

    def test_xss_prevention(self):
        """Test XSS attack prevention."""
        with pytest.raises(ValidationError, match="Invalid characters"):
            validate_query("<script>alert('XSS')</script>")
        with pytest.raises(ValidationError, match="Invalid characters"):
            validate_query("javascript:void(0)")
        with pytest.raises(ValidationError, match="Invalid characters"):
            validate_query('onclick="alert(1)"')


class TestValidateLocation:
    """Test location validation."""

    def test_valid_location(self):
        """Test valid locations."""
        assert validate_location("Berlin") == "Berlin"
        assert validate_location("10178") == "10178"
        assert validate_location("Berlin, Germany") == "Berlin, Germany"
        assert validate_location("München") == "München"
        assert validate_location("Frankfurt-am-Main") == "Frankfurt-am-Main"
        assert validate_location(None) is None

    def test_location_too_long(self):
        """Test location length validation."""
        with pytest.raises(ValidationError, match="Location too long"):
            validate_location("x" * 101)

    def test_invalid_location_format(self):
        """Test invalid location formats."""
        with pytest.raises(ValidationError, match="Invalid location format"):
            validate_location("<script>alert(1)</script>")
        with pytest.raises(ValidationError, match="Invalid location format"):
            validate_location("Berlin@#$%^&*()")


class TestValidatePrice:
    """Test price validation."""

    def test_valid_price(self):
        """Test valid prices."""
        assert validate_price(100) == 100
        assert validate_price(0) == 0
        assert validate_price(999999999) == 999999999
        assert validate_price(None) is None

    def test_invalid_price_range(self):
        """Test price range validation."""
        with pytest.raises(ValidationError, match="must be between"):
            validate_price(-1)
        with pytest.raises(ValidationError, match="must be between"):
            validate_price(1000000000)

    def test_invalid_price_type(self):
        """Test price type validation."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_price("100")
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_price(100.50)


class TestValidateRadius:
    """Test radius validation."""

    def test_valid_radius(self):
        """Test valid radius values."""
        assert validate_radius(50) == 50
        assert validate_radius(1) == 1
        assert validate_radius(200) == 200
        assert validate_radius(None) is None

    def test_invalid_radius_range(self):
        """Test radius range validation."""
        with pytest.raises(ValidationError, match="must be between"):
            validate_radius(0)
        with pytest.raises(ValidationError, match="must be between"):
            validate_radius(201)

    def test_invalid_radius_type(self):
        """Test radius type validation."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_radius("50")


class TestValidatePageCount:
    """Test page count validation."""

    def test_valid_page_count(self):
        """Test valid page counts."""
        assert validate_page_count(5) == 5
        assert validate_page_count(1) == 1
        assert validate_page_count(20) == 20
        assert validate_page_count(None) == 1  # Default value

    def test_invalid_page_count_range(self):
        """Test page count range validation."""
        with pytest.raises(ValidationError, match="must be between"):
            validate_page_count(0)
        with pytest.raises(ValidationError, match="must be between"):
            validate_page_count(21)

    def test_invalid_page_count_type(self):
        """Test page count type validation."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_page_count("5")


class TestValidateSort:
    """Test sort option validation."""

    def test_valid_sort(self):
        """Test valid sort options."""
        assert validate_sort("newest") == "newest"
        assert validate_sort("oldest") == "oldest"
        assert validate_sort("price_asc") == "price_asc"
        assert validate_sort("price_desc") == "price_desc"
        assert validate_sort(None) == "newest"  # Default
        assert validate_sort("") == "newest"  # Default

    def test_invalid_sort(self):
        """Test invalid sort options."""
        with pytest.raises(ValidationError, match="Sort must be one of"):
            validate_sort("invalid")
        with pytest.raises(ValidationError, match="Sort must be one of"):
            validate_sort("random")


class TestValidateListingId:
    """Test listing ID validation."""

    def test_valid_listing_id(self):
        """Test valid listing IDs."""
        assert validate_listing_id("123456789") == "123456789"
        assert validate_listing_id(" 987654321 ") == "987654321"  # Trimmed
        assert validate_listing_id("1") == "1"

    def test_invalid_listing_id(self):
        """Test invalid listing IDs."""
        with pytest.raises(ValidationError, match="Listing ID is required"):
            validate_listing_id("")
        with pytest.raises(ValidationError, match="Listing ID is required"):
            validate_listing_id(None)
        with pytest.raises(ValidationError, match="Invalid listing ID format"):
            validate_listing_id("abc123")
        with pytest.raises(ValidationError, match="Invalid listing ID format"):
            validate_listing_id("123-456")


class TestValidateCategory:
    """Test category validation."""

    def test_valid_category(self):
        """Test valid category IDs."""
        assert validate_category("123") == "123"
        assert validate_category("123,456") == "123,456"
        assert validate_category(" 123 , 456 ") == "123,456"  # Trimmed
        assert validate_category(None) is None

    def test_invalid_category(self):
        """Test invalid category IDs."""
        with pytest.raises(ValidationError, match="Invalid category ID"):
            validate_category("abc")
        with pytest.raises(ValidationError, match="Invalid category ID"):
            validate_category("123,abc")
        with pytest.raises(ValidationError, match="Invalid category ID"):
            validate_category("123;456")