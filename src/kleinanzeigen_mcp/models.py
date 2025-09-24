"""Data models for Kleinanzeigen API responses."""

from typing import List, Optional

from pydantic import BaseModel


class ListingImage(BaseModel):
    """Image associated with a listing."""

    url: str
    alt_text: Optional[str] = None


class Listing(BaseModel):
    """Kleinanzeigen listing model."""

    id: str
    title: str
    price: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    url: str
    description: Optional[str] = None
    images: List[ListingImage] = []
    seller: Optional[str] = None
    shipping: Optional[str] = None


class SearchParams(BaseModel):
    """Search parameters for Kleinanzeigen listings."""

    query: Optional[str] = None
    location: Optional[str] = None
    location_id: Optional[int] = None
    radius: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    sort: Optional[str] = "newest"
    category: Optional[str] = None
    page_count: int = 1


class SearchResponse(BaseModel):
    """Response from search operation."""

    success: bool
    data: List[Listing]
    total_results: Optional[int] = None
    page: int = 1


class Location(BaseModel):
    """Location model for Kleinanzeigen locations."""

    id: str
    city: str
    state: str
    zip: str
    latitude: float
    longitude: float


class LocationsResponse(BaseModel):
    """Response from locations search operation."""

    success: bool
    data: List[Location] = []
    error: Optional[str] = None


class ListingDetailResponse(BaseModel):
    """Response from listing detail operation."""

    success: bool
    data: Optional[Listing] = None
    error: Optional[str] = None


class Category(BaseModel):
    """Kleinanzeigen category model."""

    id: int
    name: str


class CategoriesResponse(BaseModel):
    """Response from categories operation."""

    success: bool
    data: List[Category] = []
    error: Optional[str] = None


class DocsResponse(BaseModel):
    """Response from docs operation."""

    success: bool
    data: Optional[str] = None
    error: Optional[str] = None
