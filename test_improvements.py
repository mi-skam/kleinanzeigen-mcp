#!/usr/bin/env python3
"""Test script to verify all improvements are working."""

import asyncio
import logging

from src.kleinanzeigen_mcp.client import KleinanzeigenClient
from src.kleinanzeigen_mcp.models import SearchParams
from src.kleinanzeigen_mcp.rate_limiter import rate_limiter
from src.kleinanzeigen_mcp.validators import (
    ValidationError,
    validate_query,
    validate_price,
)

# Set up logging to see the improvements in action
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_search_with_validation():
    """Test search with input validation."""
    print("\n🔍 Testing Search with Validation...")

    # Test valid search
    try:
        params = SearchParams(
            query="iPhone",
            location="Berlin",
            min_price=100,
            max_price=500,
            page_count=1
        )

        async with KleinanzeigenClient() as client:
            response = await client.search_listings(params)
            if response.success:
                print(f"✅ Found {len(response.data)} listings")
                if response.data:
                    listing = response.data[0]
                    print(f"  First result: {listing.title[:50]}...")
                    print(f"  Price: {listing.price}")
            else:
                print("❌ Search failed")
    except Exception as e:
        print(f"❌ Error during search: {e}")


async def test_input_validation():
    """Test input validation."""
    print("\n🛡️ Testing Input Validation...")

    # Test XSS prevention
    try:
        validate_query("<script>alert('XSS')</script>")
        print("❌ XSS validation failed - should have raised error")
    except ValidationError as e:
        print(f"✅ XSS blocked: {e}")

    # Test price validation
    try:
        validate_price(-100)
        print("❌ Price validation failed - should have raised error")
    except ValidationError as e:
        print(f"✅ Invalid price blocked: {e}")

    # Test valid inputs
    try:
        clean_query = validate_query("iPhone 12 Pro")
        print(f"✅ Valid query accepted: '{clean_query}'")

        valid_price = validate_price(500)
        print(f"✅ Valid price accepted: {valid_price}")
    except ValidationError as e:
        print(f"❌ Unexpected validation error: {e}")


async def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\n⏱️ Testing Rate Limiting...")

    # Reset rate limiter for clean test
    rate_limiter.reset()

    # Try to make 5 quick requests (should be under limit)
    print("Making 5 quick requests...")
    for i in range(5):
        success = await rate_limiter.acquire(timeout=0.1)
        if success:
            print(f"  Request {i+1}: ✅ Allowed")
        else:
            print(f"  Request {i+1}: ❌ Rate limited")

    print(f"Available requests remaining: {rate_limiter.available_requests}")


async def test_error_handling():
    """Test error handling with invalid listing ID."""
    print("\n🔧 Testing Error Handling...")

    async with KleinanzeigenClient() as client:
        # Test with invalid listing ID format
        try:
            response = await client.get_listing_details("invalid-id-format")
            if not response.success:
                print(f"✅ Invalid ID handled gracefully: {response.error}")
            else:
                print("❌ Should have failed with invalid ID")
        except Exception as e:
            print(f"✅ Exception handled: {e}")

        # Test with non-existent listing ID
        try:
            response = await client.get_listing_details("99999999999")
            if not response.success:
                print(f"✅ Non-existent ID handled: {response.error}")
            else:
                print("❌ Should have failed with non-existent ID")
        except Exception as e:
            print(f"✅ Exception handled: {e}")


async def test_logging():
    """Test that logging is working properly."""
    print("\n📝 Testing Logging Output...")

    # This will trigger logging statements
    async with KleinanzeigenClient() as client:
        # Search with intentionally problematic parameters to see logging
        params = SearchParams(
            query="test",
            min_price=10000,  # High price to likely get no results
            max_price=99999
        )

        print("Check the log output above for proper logging messages")
        response = await client.search_listings(params)

        if response.success:
            print(f"✅ Logging test complete - {len(response.data)} results")
        else:
            print("✅ Logging test complete - no results (expected)")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 TESTING KLEINANZEIGEN MCP IMPROVEMENTS")
    print("=" * 60)

    await test_input_validation()
    await test_rate_limiting()
    await test_search_with_validation()
    await test_error_handling()
    await test_logging()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())