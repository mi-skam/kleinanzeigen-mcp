#!/usr/bin/env python3
"""Detailed test to understand API responses."""

import asyncio
import json

import httpx


async def test_search_endpoint():
    """Test search endpoint with detailed logging."""
    headers = {
        "ads_key": "",
        "Content-Type": "application/json",
        "Origin": "https://kleinanzeigen-agent.de",
        "User-Agent": "Mozilla/5.0 (compatible; KleinanzeigenMCP/1.0)",
    }

    url = "https://api.kleinanzeigen-agent.de/ads/v1/kleinanzeigen/search?query=laptop&limit=5"

    async with httpx.AsyncClient(
        timeout=30.0, follow_redirects=True, headers=headers
    ) as client:
        try:
            print(f"Testing URL: {url}")
            print(f"Headers: {headers}")

            response = await client.get(url)

            print(f"Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response content: {response.text[:1000]}...")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON data: {json.dumps(data, indent=2)[:1000]}...")
                except:
                    print("Could not parse as JSON")

        except Exception as e:
            print(f"Error: {e}")


async def test_listing_detail_endpoint():
    """Test listing detail endpoint with detailed logging."""
    headers = {
        "ads_key": "",
        "Content-Type": "application/json",
        "Origin": "https://kleinanzeigen-agent.de",
        "User-Agent": "Mozilla/5.0 (compatible; KleinanzeigenMCP/1.0)",
    }

    listing_id = "2917899439"
    url = f"https://api.kleinanzeigen-agent.de/ads/v1/kleinanzeigen/ad/{listing_id}"

    async with httpx.AsyncClient(
        timeout=30.0, follow_redirects=True, headers=headers
    ) as client:
        try:
            print(f"\nTesting detail URL: {url}")
            print(f"Headers: {headers}")

            response = await client.get(url)

            print(f"Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response content: {response.text[:1000]}...")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_search_endpoint())
    asyncio.run(test_listing_detail_endpoint())
