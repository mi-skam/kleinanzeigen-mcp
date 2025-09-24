"""MCP server for Kleinanzeigen API."""

import asyncio
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    TextContent,
    Tool,
)

from .client import KleinanzeigenClient
from .models import SearchParams

app = Server("kleinanzeigen-mcp")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_listings",
            description="Search for listings on eBay Kleinanzeigen",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for listings",
                    },
                    "location": {
                        "type": "string",
                        "description": "Location to search in (e.g., '10178')",
                    },
                    "radius": {
                        "type": "integer",
                        "description": "Search radius in kilometers",
                        "minimum": 1,
                        "maximum": 200,
                    },
                    "min_price": {
                        "type": "integer",
                        "description": "Minimum price filter in euros",
                        "minimum": 0,
                    },
                    "max_price": {
                        "type": "integer",
                        "description": "Maximum price filter in euros",
                        "minimum": 0,
                    },
                    "page_count": {
                        "type": "integer",
                        "description": "Number of result pages to fetch (1-20)",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 1,
                    },
                },
            },
        ),
        Tool(
            name="get_listing_details",
            description="Get detailed information for a specific listing",
            inputSchema={
                "type": "object",
                "properties": {
                    "listing_id": {
                        "type": "string",
                        "description": "ID of the listing to fetch details for",
                    }
                },
                "required": ["listing_id"],
            },
        ),
        Tool(
            name="search_locations",
            description="Search for locations by city, postal code, or state",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for city, postal code, or state",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "search_listings":
            return await _search_listings(arguments or {})
        elif name == "get_listing_details":
            return await _get_listing_details(arguments or {})
        elif name == "search_locations":
            return await _search_locations(arguments or {})
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _search_listings(arguments: dict[str, Any]) -> list[TextContent]:
    """Search for listings."""
    params = SearchParams(
        query=arguments.get("query"),
        location=arguments.get("location"),
        radius=arguments.get("radius"),
        min_price=arguments.get("min_price"),
        max_price=arguments.get("max_price"),
        page_count=arguments.get("page_count", 1),
    )

    async with KleinanzeigenClient() as client:
        response = await client.search_listings(params)

        if response.success:
            # Format results nicely
            result_text = f"Found {len(response.data)} listings:\n\n"

            for i, listing in enumerate(response.data, 1):
                result_text += f"{i}. **{listing.title}**\n"
                if listing.price:
                    result_text += f"   Price: {listing.price}\n"
                if listing.location:
                    result_text += f"   Location: {listing.location}\n"
                if listing.date:
                    result_text += f"   Date: {listing.date}\n"
                result_text += f"   **🔗 View on Kleinanzeigen**: {listing.url}\n"
                result_text += f"   ID: {listing.id}\n"
                if listing.description:
                    # Truncate long descriptions
                    desc = (
                        listing.description[:200] + "..."
                        if len(listing.description) > 200
                        else listing.description
                    )
                    result_text += f"   Description: {desc}\n"
                result_text += "\n"

            return [TextContent(type="text", text=result_text)]
        else:
            return [
                TextContent(
                    type="text",
                    text="Search failed - no results found or API error",
                )
            ]


async def _get_listing_details(arguments: dict[str, Any]) -> list[TextContent]:
    """Get listing details."""
    listing_id = arguments.get("listing_id")
    if not listing_id:
        raise ValueError("listing_id is required")

    async with KleinanzeigenClient() as client:
        response = await client.get_listing_details(listing_id)

        if response.success and response.data:
            listing = response.data
            result_text = f"**{listing.title}**\n\n"

            if listing.price:
                result_text += f"**Price:** {listing.price}\n"
            if listing.location:
                result_text += f"**Location:** {listing.location}\n"
            if listing.date:
                result_text += f"**Date:** {listing.date}\n"
            if listing.seller:
                result_text += f"**Seller:** {listing.seller}\n"
            if listing.shipping:
                result_text += f"**Shipping:** {listing.shipping}\n"

            result_text += f"**URL:** {listing.url}\n"
            result_text += f"**ID:** {listing.id}\n\n"

            if listing.description:
                result_text += f"**Description:**\n{listing.description}\n\n"

            if listing.images:
                result_text += f"**Images:** {len(listing.images)} image(s)\n"
                for img in listing.images[:5]:  # Show max 5 images
                    result_text += f"- {img.url}\n"

            return [TextContent(type="text", text=result_text)]
        else:
            error_msg = response.error or "Listing not found or API error"
            return [
                TextContent(
                    type="text", text=f"Failed to get listing details: {error_msg}"
                )
            ]


async def _search_locations(arguments: dict[str, Any]) -> list[TextContent]:
    """Search for locations."""
    query = arguments.get("query")
    if not query:
        raise ValueError("query is required")

    limit = arguments.get("limit")

    async with KleinanzeigenClient() as client:
        response = await client.search_locations(query, limit)

        if response.success:
            if not response.data:
                return [TextContent(type="text", text="No locations found")]

            result_text = f"Found {len(response.data)} locations:\n\n"

            for i, location in enumerate(response.data, 1):
                result_text += f"{i}. **{location.city}**, {location.state}\n"
                result_text += f"   📍 Postal Code: {location.zip}\n"
                coords = f"{location.latitude}, {location.longitude}"
                result_text += f"   🌐 Coordinates: {coords}\n"
                result_text += f"   🆔 Location ID: {location.id}\n"
                result_text += "\n"

            return [TextContent(type="text", text=result_text)]
        else:
            error_msg = response.error or "Location search failed"
            return [TextContent(type="text", text=f"Search failed: {error_msg}")]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kleinanzeigen-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
