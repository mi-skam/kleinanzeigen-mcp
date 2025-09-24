#!/usr/bin/env python3
"""Manual test for the locations endpoint."""

import asyncio
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from kleinanzeigen_mcp.server import handle_call_tool


async def test_search_locations():
    """Test the search_locations tool."""
    print("=== Testing search_locations tool ===")

    # Test with Berlin query
    result = await handle_call_tool("search_locations", {"query": "Berlin", "limit": 5})

    print(f"Result type: {type(result)}")
    print(f"Number of results: {len(result)}")

    for i, content in enumerate(result):
        print(f"Content {i}:")
        print(f"  Type: {content.type}")
        print(f"  Text preview: {content.text[:200]}...")
        print()

    # Test with postal code query
    print("=== Testing with postal code ===")
    result2 = await handle_call_tool("search_locations", {"query": "10178"})

    for i, content in enumerate(result2):
        print(f"Content {i}:")
        print(f"  Type: {content.type}")
        print(f"  Text preview: {content.text[:200]}...")
        print()


if __name__ == "__main__":
    asyncio.run(test_search_locations())
