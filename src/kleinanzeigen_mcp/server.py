"""MCP server for Kleinanzeigen API."""

import asyncio
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    TextContent,
    Tool,
    Prompt,
    PromptMessage,
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
                    "sort": {
                        "type": "string",
                        "description": (
                            "Sort order for results "
                            "(newest, oldest, price_asc, price_desc)"
                        ),
                        "default": "newest",
                    },
                    "category": {
                        "type": "string",
                        "description": "Comma-separated category IDs to filter by",
                    },
                    "location_id": {
                        "type": "integer",
                        "description": (
                            "Location ID for radius-based search "
                            "(alternative to text location)"
                        ),
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
        Tool(
            name="get_categories",
            description="Get all available categories from eBay Kleinanzeigen",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_docs",
            description="Get API documentation and available endpoints",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    """List available prompts."""
    return [
        Prompt(
            name="verify_listing_availability",
            title="Verify Listing Availability",
            description=(
                "System instructions for verifying that search results are still active "
                "by checking individual listing details"
            ),
        ),
        Prompt(
            name="kleinanzeigen_assistant",
            title="Kleinanzeigen Assistant Instructions",
            description=(
                "Complete system instructions for using the Kleinanzeigen MCP tools effectively"
            ),
        ),
    ]


@app.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> PromptMessage:
    """Get a specific prompt."""
    if name == "verify_listing_availability":
        return PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=(
                    "Please follow these important instructions when helping me search for listings:\n\n"
                    "When using the Kleinanzeigen MCP tools, many listings returned by "
                    "`search_listings` may no longer be active. To ensure accuracy:\n\n"
                    "1. **Always verify listings**: After using `search_listings`, use "
                    "`get_listing_details` for each listing I'm interested in to "
                    "verify it's still available.\n\n"
                    "2. **Check for availability indicators**: If `get_listing_details` returns "
                    "an error or the listing appears to be inactive, let me know that the "
                    "listing is no longer available.\n\n"
                    "3. **Batch verification**: For multiple listings, verify the top results "
                    "to ensure they're still active before presenting them to me.\n\n"
                    "This verification step is crucial because listings on Kleinanzeigen can be "
                    "removed quickly, and the search index may contain outdated results."
                ),
            ),
        )
    elif name == "kleinanzeigen_assistant":
        return PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=(
                    "I need help finding items on eBay Kleinanzeigen. "
                    "Please follow these guidelines:\n\n"
                    "**Available Tools:**\n"
                    "- `search_listings`: Search for listings with various filters\n"
                    "- `get_listing_details`: Get detailed information about a specific listing\n"
                    "- `search_locations`: Find location IDs for cities and postal codes\n"
                    "- `get_categories`: List all available categories\n"
                    "- `get_docs`: Get API documentation\n\n"
                    "**Important: Verify Listing Availability**\n"
                    "Many listings in search results may no longer be active. Always:\n"
                    "1. Use `get_listing_details` to verify listings before recommending them\n"
                    "2. If a listing returns an error or appears inactive, mark it as unavailable\n"
                    "3. Only present verified, active listings to me\n\n"
                    "**Search Tips:**\n"
                    "- Use location IDs from `search_locations` for more accurate radius searches\n"
                    "- Apply price filters to narrow down results\n"
                    "- Use category IDs from `get_categories` to filter by type\n"
                    "- Sort by 'newest' to find recently posted items\n\n"
                    "**Best Practices:**\n"
                    "- Start with broad searches and refine based on my needs\n"
                    "- Always verify top results are still available\n"
                    "- Provide direct links to active listings\n"
                    "- Inform me promptly if listings are no longer available"
                ),
            ),
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")


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
        elif name == "get_categories":
            return await _get_categories(arguments or {})
        elif name == "get_docs":
            return await _get_docs(arguments or {})
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _search_listings(arguments: dict[str, Any]) -> list[TextContent]:
    """Search for listings."""
    params = SearchParams(
        query=arguments.get("query"),
        location=arguments.get("location"),
        location_id=arguments.get("location_id"),
        radius=arguments.get("radius"),
        min_price=arguments.get("min_price"),
        max_price=arguments.get("max_price"),
        sort=arguments.get("sort", "newest"),
        category=arguments.get("category"),
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


async def _get_categories(arguments: dict[str, Any]) -> list[TextContent]:
    """Get all available categories."""
    async with KleinanzeigenClient() as client:
        response = await client.get_categories()

        if response.success and response.data:
            result_text = f"Found {len(response.data)} categories:\n\n"

            for category in response.data:
                result_text += f"**{category.name}** (ID: {category.id})\n"

            return [TextContent(type="text", text=result_text)]
        else:
            error_msg = response.error or "Categories not found or API error"
            return [
                TextContent(type="text", text=f"Failed to get categories: {error_msg}")
            ]


async def _get_docs(arguments: dict[str, Any]) -> list[TextContent]:
    """Get API documentation and available endpoints."""
    async with KleinanzeigenClient() as client:
        response = await client.get_docs()

        if response.success and response.data:
            return [TextContent(type="text", text=response.data)]
        else:
            error_msg = response.error or "Documentation not available"
            return [
                TextContent(
                    type="text", text=f"Failed to get documentation: {error_msg}"
                )
            ]


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
