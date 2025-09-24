#!/usr/bin/env python3
"""Test various listing IDs to see if any work."""

import asyncio

from src.kleinanzeigen_mcp.client import KleinanzeigenClient


async def test_various_ids():
    """Test various listing IDs to see if any exist."""
    # Try some different ID patterns that might exist
    test_ids = [
        "2917899439",  # Original
        "123456789",  # Simple
        "1",  # Very simple
        "test",  # Text
        "2917899440",  # Close to original
        "9999999",  # Different format
    ]

    async with KleinanzeigenClient() as client:
        for test_id in test_ids:
            print(f"Testing listing ID: {test_id}")

            try:
                response = await client.get_listing_details(test_id)
                print(f"  Success: {response.success}")

                if response.success and response.data:
                    print(f"  Found working ID! Title: {response.data.title}")
                    break
                elif response.error:
                    print(f"  Error: {response.error}")
                else:
                    print(f"  No data returned")

            except Exception as e:
                print(f"  Exception: {e}")

            print()


if __name__ == "__main__":
    asyncio.run(test_various_ids())
