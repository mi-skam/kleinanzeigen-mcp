"""Configuration handling for Kleinanzeigen MCP."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load .env file if it exists
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


class MCPConfig(BaseModel):
    """Configuration for MCP server."""

    api_base_url: str = Field(
        default="https://api.kleinanzeigen-agent.de",
        description="Base URL for the Kleinanzeigen API"
    )
    api_key: str = Field(
        default="",
        description="API key for authentication"
    )
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Request timeout in seconds"
    )
    max_results_per_page: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum results per page"
    )
    max_pages: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of pages to fetch"
    )

    @field_validator("api_base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate and normalize API base URL."""
        if not v:
            raise ValueError("API base URL cannot be empty")
        # Ensure URL doesn't end with slash
        return v.rstrip("/")

    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Create config from environment variables."""
        return cls(
            api_base_url=os.getenv(
                "KLEINANZEIGEN_API_URL", "https://api.kleinanzeigen-agent.de"
            ),
            api_key=os.getenv("KLEINANZEIGEN_API_KEY", ""),
            timeout=float(os.getenv("KLEINANZEIGEN_TIMEOUT", "30.0")),
            max_results_per_page=int(os.getenv("KLEINANZEIGEN_MAX_RESULTS", "50")),
            max_pages=int(os.getenv("KLEINANZEIGEN_MAX_PAGES", "20")),
        )


# Global config instance
config = MCPConfig.from_env()
