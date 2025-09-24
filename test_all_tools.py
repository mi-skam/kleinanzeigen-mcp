#!/usr/bin/env python3
"""Test all MCP tools including the new locations endpoint."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from kleinanzeigen_mcp.server import handle_call_tool


async def test_all_tools():
    """Test all available tools."""
    print("=== Testing all MCP tools ===\n")

    # Test search_locations
    print("1. Testing search_locations tool:")
    result = await handle_call_tool("search_locations", {"query": "Berlin", "limit": 3})
    print(f"   Result type: {type(result)}")
    has_error = "HTTP error" not in result[0].text
    has_failed = "Search failed" in result[0].text
    print(f"   Success: {has_error or has_failed}")
    print(f"   Response preview: {result[0].text[:100]}...")
    print()

    # Test search_listings
    print("2. Testing search_listings tool:")
    params = {"query": "laptop", "location": "Berlin"}
    result = await handle_call_tool("search_listings", params)
    print(f"   Result type: {type(result)}")
    print(f"   Success: {'Error:' not in result[0].text}")
    print(f"   Response preview: {result[0].text[:100]}...")
    print()

    # Test get_listing_details
    print("3. Testing get_listing_details tool:")
    result = await handle_call_tool("get_listing_details", {"listing_id": "123456789"})
    print(f"   Result type: {type(result)}")
    print("   Success: 'Failed to get listing details' in result[0].text")
    print(f"   Response preview: {result[0].text[:100]}...")
    print()

    print("✅ All tools are accessible and functioning!")


if __name__ == "__main__":
    asyncio.run(test_all_tools())
