#!/usr/bin/env python3
"""Test the MCP server directly."""

import asyncio

import pytest

from kleinanzeigen_mcp.server import handle_call_tool


@pytest.mark.asyncio
async def test_mcp_server():
    """Test the MCP server get_listing_details tool directly."""
    print("=== Testing MCP Server get_listing_details tool ===")

    # Test the tool call as it would be called by an MCP client
    result = await handle_call_tool("get_listing_details", {"listing_id": "2917899439"})

    print(f"Result type: {type(result)}")
    print(f"Number of results: {len(result)}")

    for i, content in enumerate(result):
        print(f"Content {i}:")
        print(f"  Type: {content.type}")
        print(f"  Text: {content.text[:200]}...")
        print()

    # Verify we're getting the right type of error (404 instead of 500)
    error_text = result[0].text.lower()
    if "500" in error_text or "internal server error" in error_text:
        print("❌ Still getting 500 errors")
    elif "404" in error_text or "not found" in error_text:
        print("✅ Getting proper 404 errors - fix successful!")
    else:
        print(f"⚠️  Unexpected error type: {result[0].text}")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
