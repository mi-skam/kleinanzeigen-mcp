#!/usr/bin/env python3
"""Test script to test search functionality and see if we can get listing IDs."""

import asyncio
import os

from src.kleinanzeigen_mcp.client import KleinanzeigenClient
from src.kleinanzeigen_mcp.models import SearchParams


async def test_search_listings():
    """Test the search_listings function to get valid listing IDs."""
    print("Testing search_listings to find valid listing IDs...")

    try:
        params = SearchParams(
            query="laptop",
            location="10178",  # Berlin
            page_count=1,
        )

        async with KleinanzeigenClient() as client:
            print(f"API Base URL: {client.base_url}")

            response = await client.search_listings(params)

            print(f"Search success: {response.success}")
            print(f"Number of listings: {len(response.data)}")

            if response.success and response.data:
                for i, listing in enumerate(response.data[:3]):  # Show first 3
                    print(f"\nListing {i + 1}:")
                    print(f"  ID: {listing.id}")
                    print(f"  Title: {listing.title}")
                    print(f"  Price: {listing.price}")
                    print(f"  URL: {listing.url}")

                    # Try get_listing_details with this ID
                    print(f"\n  Testing get_listing_details with ID: {listing.id}")
                    detail_response = await client.get_listing_details(listing.id)
                    print(f"  Detail success: {detail_response.success}")
                    if not detail_response.success:
                        print(f"  Detail error: {detail_response.error}")

                    if i == 0:  # Only test first one for now
                        break
            else:
                print("No listings found or search failed")

    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_search_listings())
