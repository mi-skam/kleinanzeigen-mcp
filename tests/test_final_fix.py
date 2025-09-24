#!/usr/bin/env python3
"""Final test to verify the fix works."""

import asyncio

from src.kleinanzeigen_mcp.server import _get_listing_details


async def test_final_fix():
    """Test that demonstrates the fix."""
    print("=== Testing get_listing_details fix ===")
    print("Before fix: Would get 500 Server Error due to CORS issues")
    print("After fix: Should get proper 404 Not Found for non-existent listings")
    print()

    # Test with the original problematic listing ID
    test_id = "2917899439"

    try:
        print(f"Testing with listing ID: {test_id}")

        # This should now return a proper error message instead of crashing with 500
        result = await _get_listing_details({"listing_id": test_id})

        print(f"Result type: {type(result)}")
        print(f"Result content: {result[0].text}")

        # The result should contain a proper error message, not a 500 server error
        if "500" in result[0].text:
            print("❌ Still getting 500 errors - fix did not work")
        elif "404" in result[0].text or "not found" in result[0].text.lower():
            msg = (
                "✅ Fix successful! Now getting proper 404 responses "
                "instead of 500 errors"
            )
            print(msg)
        elif "Failed to get listing details" in result[0].text:
            print("✅ Fix successful! Getting proper error handling")
        else:
            print(f"⚠️  Unexpected response: {result[0].text}")

    except Exception as e:
        print(f"❌ Exception occurred: {e}")


if __name__ == "__main__":
    asyncio.run(test_final_fix())
