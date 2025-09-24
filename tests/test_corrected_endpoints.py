#!/usr/bin/env python3
"""Test the corrected API endpoints."""

import asyncio

import httpx


async def test_corrected_endpoints():
    """Test the corrected endpoints."""
    headers = {
        "ads_key": "",
        "Content-Type": "application/json",
        "Origin": "https://kleinanzeigen-agent.de",
        "User-Agent": "Mozilla/5.0 (compatible; KleinanzeigenMCP/1.0)",
    }

    # Test search endpoint
    search_url = "https://api.kleinanzeigen-agent.de/inserate?query=laptop&limit=5"
    print(f"Testing search URL: {search_url}")

    async with httpx.AsyncClient(
        timeout=30.0, follow_redirects=True, headers=headers
    ) as client:
        try:
            response = await client.get(search_url)
            print(f"Search - Status code: {response.status_code}")
            print(f"Search - Response: {response.text[:500]}...")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success") and data.get("data"):
                        print(f"Found {len(data['data'])} listings")

                        # Get first listing ID for detail test
                        if data["data"]:
                            first_listing = data["data"][0]
                            listing_id = first_listing.get("id") or first_listing.get(
                                "adid"
                            )
                            print(f"First listing ID: {listing_id}")

                            # Test detail endpoint with this ID
                            if listing_id:
                                detail_url = f"https://api.kleinanzeigen-agent.de/inserat/{listing_id}"
                                print(f"\nTesting detail URL: {detail_url}")

                                detail_response = await client.get(detail_url)
                                status_code = detail_response.status_code
                                print(f"Detail - Status code: {status_code}")
                                response_preview = detail_response.text[:500]
                                print(f"Detail - Response: {response_preview}...")
                except Exception as e:
                    print(f"JSON parsing error: {e}")

        except Exception as e:
            print(f"Request error: {e}")


if __name__ == "__main__":
    asyncio.run(test_corrected_endpoints())
