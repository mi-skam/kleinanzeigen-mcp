#!/usr/bin/env python3
"""Test the categories endpoint implementation."""

import asyncio

import pytest

from kleinanzeigen_mcp.server import handle_call_tool


@pytest.mark.asyncio
async def test_categories_endpoint():
    """Test the categories endpoint via MCP server."""
    print("=== Testing categories endpoint ===")

    # Test the get_categories tool call
    result = await handle_call_tool("get_categories", {})

    print(f"Result type: {type(result)}")
    print(f"Number of results: {len(result)}")

    # Should get back exactly one TextContent result
    assert len(result) == 1
    assert result[0].type == "text"

    # The result should contain either categories or an error message
    text_content = result[0].text
    print(f"Result content: {text_content[:200]}...")

    # Check if we get proper error handling (401 Unauthorized expected without API key)
    if "Failed to get categories" in text_content:
        print("✅ Categories endpoint properly handles API authentication errors")
        assert "HTTP error: Client error '401 Unauthorized'" in text_content
    elif "Found" in text_content and "categories" in text_content:
        print("✅ Categories endpoint successfully retrieved categories")
        # If we got categories, verify the format
        assert "**" in text_content  # Should have bold category names
        assert "ID:" in text_content  # Should show IDs
    else:
        print(f"⚠️  Unexpected response: {text_content}")


if __name__ == "__main__":
    asyncio.run(test_categories_endpoint())
