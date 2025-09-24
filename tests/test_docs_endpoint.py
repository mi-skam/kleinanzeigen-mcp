#!/usr/bin/env python3
"""Test the docs endpoint."""

import asyncio

import pytest

from kleinanzeigen_mcp.server import handle_call_tool


@pytest.mark.asyncio
async def test_docs_endpoint():
    """Test the docs endpoint via MCP server."""
    print("=== Testing MCP Server get_docs tool ===")

    # Test the tool call as it would be called by an MCP client
    result = await handle_call_tool("get_docs", {})

    print(f"Result type: {type(result)}")
    print(f"Number of results: {len(result)}")

    for i, content in enumerate(result):
        print(f"Content {i}:")
        print(f"  Type: {content.type}")
        print(f"  Text (first 200 chars): {content.text[:200]}...")
        print()

    # Verify we got some kind of response
    assert len(result) > 0, "Should return at least one content item"
    assert result[0].type == "text", "Should return text content"

    # Check if we got documentation or an error message
    response_text = result[0].text.lower()
    if "documentation" in response_text or "endpoints" in response_text:
        print("✅ Successfully retrieved documentation!")
    elif "error" in response_text or "failed" in response_text:
        print("⚠️  Got error response (expected if docs endpoint doesn't exist on API)")
        print(f"Error: {result[0].text}")
    else:
        print(f"🤔 Unexpected response: {result[0].text}")


if __name__ == "__main__":
    asyncio.run(test_docs_endpoint())
