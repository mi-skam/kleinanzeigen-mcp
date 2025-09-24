"""HTTP client for Kleinanzeigen API."""

from typing import Optional
from urllib.parse import urlencode

import httpx

from .config import config
from .models import (
    CategoriesResponse,
    Category,
    Listing,
    ListingDetailResponse,
    SearchParams,
    SearchResponse,
)


class KleinanzeigenClient:
    """HTTP client for interacting with Kleinanzeigen API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize client with base URL."""
        self.base_url = (base_url or config.api_base_url).rstrip("/")
        headers = {
            "ads_key": config.api_key,
            "Content-Type": "application/json",
            "Origin": "https://kleinanzeigen-agent.de",
            "User-Agent": "Mozilla/5.0 (compatible; KleinanzeigenMCP/1.0)",
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

    async def search_listings(self, params: SearchParams) -> SearchResponse:
        """Search for listings with given parameters."""
        try:
            # Build query parameters for the API
            query_params = {}
            if params.query:
                query_params["query"] = params.query

            # Set limit based on page_count and max_results_per_page
            # API has a maximum limit of 10
            limit = min(10, config.max_results_per_page)
            if params.page_count:
                limit = min(
                    10,  # API maximum
                    params.page_count * 10,  # Respect API limit per page
                    config.max_pages * 10,
                )
            query_params["limit"] = str(limit)

            # Add location if specified
            if params.location:
                query_params["location"] = params.location

            # Add price filters if specified
            if params.min_price:
                query_params["min_price"] = str(params.min_price)
            if params.max_price:
                query_params["max_price"] = str(params.max_price)

            # Add radius if specified
            if params.radius:
                query_params["radius"] = str(params.radius)

            url = f"{self.base_url}/ads/v1/kleinanzeigen/search"
            if query_params:
                url += f"?{urlencode(query_params)}"

            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()

            # Parse listings from response
            listings = []
            if data.get("success") and data.get("data") and data["data"].get("ads"):
                for i, item in enumerate(data["data"]["ads"]):
                    try:
                        # Map API response fields to our model
                        location_text = ""
                        if item.get("location"):
                            loc = item["location"]
                            city = loc.get("city", "")
                            state = loc.get("state", "")
                            location_text = f"{city}, {state}"

                        price_text = ""
                        if item.get("price"):
                            price_val = item["price"]
                            if price_val == "0" or price_val == 0:
                                price_text = "Auf Anfrage"
                            else:
                                price_text = f"€ {price_val}"

                        seller_text = ""
                        if item.get("seller"):
                            seller_text = item["seller"].get("name", "")

                        # Convert to Kleinanzeigen URL format
                        adid = item.get("adid", "")
                        ad_url = f"https://www.kleinanzeigen.de/s-anzeige/{adid}"

                        # Convert image URLs to ListingImage objects
                        image_objects = []
                        for img_url in item.get("images", []):
                            from .models import ListingImage

                            image_objects.append(ListingImage(url=img_url))

                        # Convert shipping boolean to string
                        shipping_text = ""
                        if item.get("shipping"):
                            shipping_text = (
                                "Versand möglich"
                                if item["shipping"]
                                else "Nur Abholung"
                            )

                        listing = Listing(
                            id=item.get("adid", ""),
                            title=item.get("title", ""),
                            price=price_text,
                            location=location_text,
                            date=item.get("upload_date"),
                            url=ad_url,
                            description=item.get("description"),
                            images=image_objects,
                            seller=seller_text,
                            shipping=shipping_text,
                        )
                        listings.append(listing)
                    except Exception as e:
                        print(f"Error processing item {i}: {e}")
                        # Skip failed items instead of breaking the whole search

            return SearchResponse(
                success=data.get("success", False),  # Success based on API response
                data=listings,
                total_results=len(listings),
                page=1,
            )

        except httpx.HTTPError:
            return SearchResponse(success=False, data=[], total_results=0, page=1)
        except Exception:
            return SearchResponse(success=False, data=[], total_results=0, page=1)

    async def get_listing_details(self, listing_id: str) -> ListingDetailResponse:
        """Get detailed information for a specific listing."""
        try:
            url = f"{self.base_url}/ads/v1/kleinanzeigen/ad/{listing_id}"
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()

            if data.get("success") and data.get("data"):
                item = data["data"]

                # Map API response fields to our model
                location_text = ""
                if item.get("location"):
                    loc = item["location"]
                    location_text = f"{loc.get('city', '')}, {loc.get('state', '')}"

                price_text = ""
                if item.get("price"):
                    price_val = item["price"]
                    if price_val == "0" or price_val == 0:
                        price_text = "Auf Anfrage"
                    else:
                        price_text = f"€ {price_val}"

                seller_text = ""
                if item.get("seller"):
                    seller_text = item["seller"].get("name", "")

                # Convert to Kleinanzeigen URL format
                adid = item.get("adid", listing_id)
                ad_url = f"https://www.kleinanzeigen.de/s-anzeige/{adid}"

                # Convert image URLs to ListingImage objects
                image_objects = []
                for img_url in item.get("images", []):
                    from .models import ListingImage

                    image_objects.append(ListingImage(url=img_url))

                # Convert shipping boolean to string
                shipping_text = ""
                if item.get("shipping"):
                    shipping_text = (
                        "Versand möglich" if item["shipping"] else "Nur Abholung"
                    )

                listing = Listing(
                    id=item.get("adid", listing_id),
                    title=item.get("title", ""),
                    price=price_text,
                    location=location_text,
                    date=item.get("upload_date"),
                    url=ad_url,
                    description=item.get("description"),
                    images=image_objects,
                    seller=seller_text,
                    shipping=shipping_text,
                )

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

    async def get_categories(self) -> CategoriesResponse:
        """Get all available categories."""
        try:
            url = f"{self.base_url}/ads/v1/kleinanzeigen/categories"
            response = await self.client.get(url)
            response.raise_for_status()

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
