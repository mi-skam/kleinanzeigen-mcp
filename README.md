# Kleinanzeigen MCP Server

An MCP (Model Context Protocol) server that provides access to eBay Kleinanzeigen listings through a standardized interface.

## Features

- **Search Listings**: Search for listings with flexible parameters including query, location, price range, and radius
- **Get Listing Details**: Retrieve detailed information for specific listings
- **Configurable**: Environment variable configuration for API endpoints and limits

## Installation

### Option 1: Nix Flake

```bash
# Clone and enter development shell
git clone <repository-url>
cd kleinanzeigen-mcp
nix develop

# Set up uv environment and install dependencies
setup-env

# Run linting
lint-fix
```

### Option 2: Virtual Environment (venv)

```bash
# Clone this repository
git clone <repository-url>
cd kleinanzeigen-mcp

# Quick setup (automated)
./setup-dev.sh

# Manual setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Or install in development mode with all dependencies
pip install -e ".[dev]"

# Run linting
./scripts/lint.sh --fix

# Run the MCP server
python -m src.kleinanzeigen_mcp.server
```

### Option 3: Standard Python Installation

```bash
# Clone this repository
git clone <repository-url>
cd kleinanzeigen-mcp

# Install the package
pip install -e .
```

## Usage

### As MCP Server

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "kleinanzeigen": {
      "command": "python",
      "args": ["-m", "kleinanzeigen_mcp.server"],
      "env": {
        "KLEINANZEIGEN_API_URL": "https://api.kleinanzeigen-agent.de",
        "KLEINANZEIGEN_API_KEY": "YOUR-KEY"
      }
    }
  }
}
```

### Available Tools

#### search_listings

Search for listings on eBay Kleinanzeigen.

**Parameters:**

- `query` (string, optional): Search term for listings
- `location` (string, optional): Location to search in (e.g., '10178' for Berlin postal code)
- `radius` (integer, optional): Search radius in kilometers (1-200)
- `min_price` (integer, optional): Minimum price filter in euros
- `max_price` (integer, optional): Maximum price filter in euros
- `page_count` (integer, optional): Number of result pages to fetch (1-20, default: 1)

**Example:**

```json
{
  "name": "search_listings",
  "arguments": {
    "query": "fahrrad",
    "location": "10178",
    "radius": 5,
    "min_price": 50,
    "max_price": 500,
    "page_count": 2
  }
}
```

#### get_listing_details

Get detailed information for a specific listing.

**Parameters:**

- `listing_id` (string, required): ID of the listing to fetch details for

**Example:**

```json
{
  "name": "get_listing_details", 
  "arguments": {
    "listing_id": "12345"
  }
}
```

## Configuration

Environment variables for configuration:

- `KLEINANZEIGEN_API_URL`: Base URL for the API (default: "<https://kleinanzeigen-agent.de>")
- `KLEINANZEIGEN_TIMEOUT`: Request timeout in seconds (default: 30.0)
- `KLEINANZEIGEN_MAX_RESULTS`: Maximum results per page (default: 50)
- `KLEINANZEIGEN_MAX_PAGES`: Maximum number of pages (default: 20)

## Development

### Setup Development Environment

#### Option 1: Virtual Environment (Recommended)

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Or install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Lint and format code (auto-detects tools)
./scripts/lint.sh --fix

# Check code without fixing (CI mode)
./scripts/lint.sh --check-only
```

#### Option 2: Nix Environment

```bash
# Enter Nix development shell
nix develop

# Set up environment
setup-env

# Run linting
lint-fix
```

### Project Structure

```
src/kleinanzeigen_mcp/
├── __init__.py          # Package initialization
├── server.py            # MCP server implementation
├── client.py            # HTTP client for Kleinanzeigen API
├── models.py            # Pydantic data models
└── config.py            # Configuration handling
```

## Dependencies

This MCP server relies on the [ebay-kleinanzeigen-api](https://github.com/DanielWTE/ebay-kleinanzeigen-api) service for scraping Kleinanzeigen listings. The default configuration points to the hosted version at `kleinanzeigen-agent.de`, but you can also run your own instance.

## License

MIT License
