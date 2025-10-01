"""HTTP client for Kleinanzeigen API."""

import asyncio
import logging
from typing import Optional
from urllib.parse import urlencode

import httpx

from .config import config
from .constants import API_MAX_LIMIT, DEFAULT_LIMIT, MAX_IMAGE_DISPLAY, MAX_RETRIES, RETRY_DELAY
from .models import (
    CategoriesResponse,
    Category,
    DocsResponse,
    Listing,
    ListingDetailResponse,
    Location,
    LocationsResponse,
    SearchParams,
    SearchResponse,
)
from .rate_limiter import rate_limiter
from .utils import parse_listing_from_api

logger = logging.getLogger(__name__)


class KleinanzeigenClient:
    """HTTP client for interacting with Kleinanzeigen API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize client with base URL."""
        self.base_url = (base_url or config.api_base_url).rstrip("/")
        headers = {
            "ads_key": config.api_key,
            "Content-Type": "application/json",
            "User-Agent": "KleinanzeigenMCP/1.0",
        }
        self.client = httpx.AsyncClient(
            timeout=config.timeout, follow_redirects=True, headers=headers
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic and rate limiting.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments for httpx request

        Returns:
            HTTP response

        Raises:
            httpx.HTTPError: If all retries fail
        """
        last_exception = None

        for attempt in range(MAX_RETRIES):
            try:
                # Apply rate limiting
                if not await rate_limiter.acquire(timeout=config.timeout):
                    raise httpx.TimeoutException("Rate limit timeout")

                # Make the request
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise
                last_exception = e
                logger.warning(f"HTTP {e.response.status_code} on attempt {attempt + 1}/{MAX_RETRIES}")

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                logger.warning(f"Connection error on attempt {attempt + 1}/{MAX_RETRIES}: {e}")

            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error on attempt {attempt + 1}/{MAX_RETRIES}: {e}")

            # Wait before retrying (exponential backoff)
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)

        # All retries failed
        raise last_exception or httpx.HTTPError("All retry attempts failed")

    async def search_listings(self, params: SearchParams) -> SearchResponse:
        """Search for listings with given parameters."""
        try:
            # Build query parameters for the API
            query_params = {}
            if params.query:
                query_params["query"] = params.query

            # Set limit based on page_count and max_results_per_page
            limit = min(API_MAX_LIMIT, config.max_results_per_page)
            if params.page_count:
                limit = min(
                    API_MAX_LIMIT,
                    params.page_count * API_MAX_LIMIT,
                    config.max_pages * API_MAX_LIMIT,
                )
            query_params["limit"] = str(limit)

            # Add location if specified (prefer location_id over text location)
            if params.location_id:
                query_params["location_id"] = str(params.location_id)
            elif params.location:
                query_params["location"] = params.location

            # Add price filters if specified
            if params.min_price:
                query_params["min_price"] = str(params.min_price)
            if params.max_price:
                query_params["max_price"] = str(params.max_price)

            # Add radius if specified
            if params.radius:
                query_params["radius"] = str(params.radius)

            # Add sort order if specified
            if params.sort:
                query_params["sort"] = params.sort

            # Add category filter if specified
            if params.category:
                query_params["category"] = params.category

            url = f"{self.base_url}/ads/v1/kleinanzeigen/search"
            if query_params:
                url += f"?{urlencode(query_params)}"

            response = await self._make_request_with_retry("GET", url)

            data = response.json()

            # Parse listings from response
            listings = []
            if data.get("success") and data.get("data") and data["data"].get("ads"):
                for i, item in enumerate(data["data"]["ads"]):
                    try:
                        listing = parse_listing_from_api(item)
                        listings.append(listing)
                    except Exception as e:
                        logger.warning(f"Error processing item {i}: {e}")
                        # Skip failed items instead of breaking the whole search

            return SearchResponse(
                success=data.get("success", False),  # Success based on API response
                data=listings,
                total_results=len(listings),
                page=1,
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during search: {e}")
            return SearchResponse(success=False, data=[], total_results=0, page=1)
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}", exc_info=True)
            return SearchResponse(success=False, data=[], total_results=0, page=1)

    async def get_listing_details(self, listing_id: str) -> ListingDetailResponse:
        """Get detailed information for a specific listing."""
        try:
            url = f"{self.base_url}/ads/v1/kleinanzeigen/inserat?id={listing_id}"
            response = await self._make_request_with_retry("GET", url)

            data = response.json()

            if data.get("success") and data.get("data"):
                item = data["data"]
                listing = parse_listing_from_api(item, listing_id)
                return ListingDetailResponse(success=True, data=listing)
            else:
                return ListingDetailResponse(
                    success=False, error="Listing not found or invalid response"
                )

        except httpx.HTTPError as e:
            return ListingDetailResponse(success=False, error=f"HTTP error: {str(e)}")
        except Exception as e:
            return ListingDetailResponse(
                success=False, error=f"Unexpected error: {str(e)}"
            )

    async def search_locations(
        self, query: str, limit: Optional[int] = None
    ) -> LocationsResponse:
        """Search for locations by query."""
        try:
            query_params = {"query": query}
            if limit:
                query_params["limit"] = str(limit)

            url = f"{self.base_url}/ads/v1/kleinanzeigen/locations"
            if query_params:
                url += f"?{urlencode(query_params)}"

            response = await self._make_request_with_retry("GET", url)

            data = response.json()

            locations = []
            has_success = data.get("success")
            has_data = data.get("data")
            has_locations = has_data and data["data"].get("locations")
            if has_success and has_data and has_locations:
                for item in data["data"]["locations"]:
                    try:
                        location = Location(
                            id=str(item.get("id", "")),
                            city=item.get("city", ""),
                            state=item.get("state", ""),
                            zip=item.get("zip", ""),
                            latitude=float(item.get("latitude", 0.0)),
                            longitude=float(item.get("longitude", 0.0)),
                        )
                        locations.append(location)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error processing location item: {e}")

            return LocationsResponse(
                success=data.get("success", False),
                data=locations,
            )

        except httpx.HTTPError as e:
            return LocationsResponse(success=False, error=f"HTTP error: {str(e)}")
        except Exception as e:
            return LocationsResponse(success=False, error=f"Unexpected error: {str(e)}")

    async def get_categories(self) -> CategoriesResponse:
        """Get all available categories."""
        try:
            url = f"{self.base_url}/ads/v1/kleinanzeigen/categories"
            response = await self._make_request_with_retry("GET", url)

            data = response.json()

            if data.get("success") and data.get("categories"):
                categories = []
                for category_data in data["categories"]:
                    category = Category(
                        id=category_data.get("id"), name=category_data.get("name", "")
                    )
                    categories.append(category)

                return CategoriesResponse(success=True, data=categories)
            else:
                return CategoriesResponse(
                    success=False, error="Categories not found or invalid response"
                )

        except httpx.HTTPError as e:
            return CategoriesResponse(success=False, error=f"HTTP error: {str(e)}")
        except Exception as e:
            return CategoriesResponse(
                success=False, error=f"Unexpected error: {str(e)}"
            )

    async def get_docs(self) -> DocsResponse:
        """Get API documentation and available endpoints."""
        try:
            url = f"{self.base_url}/docs"
            response = await self._make_request_with_retry("GET", url)

            data = response.json()

            if data.get("success"):
                if data.get("data"):
                    docs_content = data["data"]
                    if isinstance(docs_content, dict):
                        formatted_docs = self._format_docs(docs_content)
                        return DocsResponse(success=True, data=formatted_docs)
                    else:
                        return DocsResponse(success=True, data=str(docs_content))
                else:
                    # Handle case where success=true but no data
                    return DocsResponse(
                        success=True, data="No documentation data available"
                    )
            else:
                return DocsResponse(success=False, error="API returned success=false")

        except httpx.HTTPError as e:
            # If remote docs fail, provide fallback documentation
            fallback_docs = self._get_fallback_docs()
            return DocsResponse(
                success=True,
                data=f"Remote documentation unavailable ({str(e)})\n\n{fallback_docs}",
            )
        except Exception as e:
            return DocsResponse(success=False, error=f"Unexpected error: {str(e)}")

    def _get_fallback_docs(self) -> str:
        """Provide fallback documentation when remote docs are unavailable."""
        return """# Kleinanzeigen API Documentation

## API Response Format

All API endpoints return responses in the following JSON format:

```json
{
  "success": true,
  "data": [
    ...
  ]
}
```

## Available Endpoints

### Search Listings
- **Endpoint**: `/ads/v1/kleinanzeigen/search`
- **Method**: GET
- **Description**: Search for listings with various filters
- **Parameters**: query, location, radius, min_price, max_price, sort, category, etc.

### Get Listing Details
- **Endpoint**: `/ads/v1/kleinanzeigen/inserat`
- **Method**: GET
- **Description**: Get detailed information for a specific listing
- **Parameters**: id (required)

### Search Locations
- **Endpoint**: `/ads/v1/kleinanzeigen/locations`
- **Method**: GET
- **Description**: Search for locations by city, postal code, or state
- **Parameters**: query (required), limit

### Get Categories
- **Endpoint**: `/ads/v1/kleinanzeigen/categories`
- **Method**: GET
- **Description**: Get all available categories

## Documentation

API documentation is available at http://localhost:8000/docs when running locally."""

    def _format_docs(self, docs_data: dict) -> str:
        """Format documentation data into readable text."""
        formatted = "# Kleinanzeigen API Documentation\n\n"

        if "endpoints" in docs_data:
            formatted += "## Available Endpoints\n\n"
            for endpoint in docs_data["endpoints"]:
                method = endpoint.get("method", "GET")
                path = endpoint.get("path", "")
                formatted += f"### {method} {path}\n"
                if endpoint.get("description"):
                    formatted += f"{endpoint['description']}\n\n"

                if endpoint.get("parameters"):
                    formatted += "**Parameters:**\n"
                    for param in endpoint["parameters"]:
                        name = param.get("name", "")
                        param_type = param.get("type", "")
                        formatted += f"- `{name}` ({param_type})"
                        if param.get("required"):
                            formatted += " *required*"
                        if param.get("description"):
                            formatted += f": {param['description']}"
                        formatted += "\n"
                    formatted += "\n"

                if endpoint.get("example_response"):
                    formatted += "**Example Response:**\n"
                    formatted += f"```json\n{endpoint['example_response']}\n```\n\n"

                formatted += "---\n\n"

        if "info" in docs_data:
            info = docs_data["info"]
            formatted += "## API Information\n\n"
            if info.get("version"):
                formatted += f"**Version:** {info['version']}\n"
            if info.get("description"):
                formatted += f"**Description:** {info['description']}\n"
            if info.get("base_url"):
                formatted += f"**Base URL:** {info['base_url']}\n"

        return formatted
