#!/usr/bin/env python3
"""Test script to reproduce the get_listing_details 500 error."""

import asyncio
import os

import pytest

from kleinanzeigen_mcp.client import KleinanzeigenClient


@pytest.mark.asyncio
async def test_get_listing_details():
    """Test the get_listing_details function with a sample ID."""
    # Set up environment variables if needed
    if not os.getenv("KLEINANZEIGEN_API_KEY"):
        print("Warning: KLEINANZEIGEN_API_KEY not set")

    # Test with a sample listing ID
    test_listing_id = "2917899439"

    print(f"Testing get_listing_details with ID: {test_listing_id}")

    try:
        async with KleinanzeigenClient() as client:
            print(f"API Base URL: {client.base_url}")
            print(f"Headers: {client.client.headers}")

            response = await client.get_listing_details(test_listing_id)

            print(f"Response success: {response.success}")
            if response.success and response.data:
                listing = response.data
                print(f"Title: {listing.title}")
                print(f"Price: {listing.price}")
                print(f"Location: {listing.location}")
                print(f"URL: {listing.url}")
                if listing.description:
                    print(f"Description: {listing.description[:200]}...")
            else:
                print(f"Error: {response.error}")

    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_get_listing_details())
