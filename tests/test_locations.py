"""Test locations endpoint functionality."""

from unittest.mock import AsyncMock, patch

import pytest

from kleinanzeigen_mcp.client import KleinanzeigenClient


@pytest.mark.asyncio
async def test_search_locations_success():
    """Test successful locations search."""
    mock_response_data = {
        "success": True,
        "message": "Locations found",
        "data": {
            "meta": {"query": "Berlin"},
            "locations": [
                {
                    "id": "1",
                    "city": "Berlin",
                    "state": "Berlin",
                    "zip": "10117",
                    "latitude": 52.5200,
                    "longitude": 13.4050,
                },
                {
                    "id": "2",
                    "city": "Berlin-Mitte",
                    "state": "Berlin",
                    "zip": "10178",
                    "latitude": 52.5170,
                    "longitude": 13.3888,
                },
            ],
        },
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response

        async with KleinanzeigenClient() as client:
            response = await client.search_locations("Berlin", limit=10)

        assert response.success is True
        assert len(response.data) == 2
        assert response.data[0].city == "Berlin"
        assert response.data[0].state == "Berlin"
        assert response.data[0].zip == "10117"
        assert response.data[0].latitude == 52.5200
        assert response.data[0].longitude == 13.4050


@pytest.mark.asyncio
async def test_search_locations_no_results():
    """Test locations search with no results."""
    mock_response_data = {
        "success": True,
        "message": "No locations found",
        "data": {"meta": {"query": "nonexistent"}, "locations": []},
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response

        async with KleinanzeigenClient() as client:
            response = await client.search_locations("nonexistent")

        assert response.success is True
        assert len(response.data) == 0


@pytest.mark.asyncio
async def test_search_locations_api_error():
    """Test locations search API error handling."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("API Error")

        async with KleinanzeigenClient() as client:
            response = await client.search_locations("Berlin")

        assert response.success is False
        assert "Unexpected error" in response.error
