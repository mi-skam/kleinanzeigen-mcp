"""Configuration handling for Kleinanzeigen MCP."""

import os

from pydantic import BaseModel


class MCPConfig(BaseModel):
    """Configuration for MCP server."""

    api_base_url: str = "https://api.kleinanzeigen-agent.de"
    api_key: str = ""
    timeout: float = 30.0
    max_results_per_page: int = 50
    max_pages: int = 20

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
