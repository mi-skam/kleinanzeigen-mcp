"""Unit tests for configuration."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from kleinanzeigen_mcp.config import MCPConfig


class TestMCPConfig:
    """Test MCP configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MCPConfig()
        assert config.api_base_url == "https://api.kleinanzeigen-agent.de"
        assert config.api_key == ""
        assert config.timeout == 30.0
        assert config.max_results_per_page == 50
        assert config.max_pages == 20

    def test_custom_config(self):
        """Test custom configuration values."""
        config = MCPConfig(
            api_base_url="https://custom.api.com",
            api_key="test-key",
            timeout=60.0,
            max_results_per_page=25,
            max_pages=10
        )
        assert config.api_base_url == "https://custom.api.com"
        assert config.api_key == "test-key"
        assert config.timeout == 60.0
        assert config.max_results_per_page == 25
        assert config.max_pages == 10

    def test_url_normalization(self):
        """Test that URLs are normalized (trailing slash removed)."""
        config = MCPConfig(api_base_url="https://api.example.com/")
        assert config.api_base_url == "https://api.example.com"

    def test_timeout_validation(self):
        """Test timeout validation."""
        # Valid timeouts
        MCPConfig(timeout=1.0)
        MCPConfig(timeout=300.0)

        # Invalid timeouts
        with pytest.raises(ValidationError):
            MCPConfig(timeout=0.5)
        with pytest.raises(ValidationError):
            MCPConfig(timeout=301.0)

    def test_max_results_validation(self):
        """Test max results validation."""
        # Valid values
        MCPConfig(max_results_per_page=1)
        MCPConfig(max_results_per_page=100)

        # Invalid values
        with pytest.raises(ValidationError):
            MCPConfig(max_results_per_page=0)
        with pytest.raises(ValidationError):
            MCPConfig(max_results_per_page=101)

    def test_max_pages_validation(self):
        """Test max pages validation."""
        # Valid values
        MCPConfig(max_pages=1)
        MCPConfig(max_pages=100)

        # Invalid values
        with pytest.raises(ValidationError):
            MCPConfig(max_pages=0)
        with pytest.raises(ValidationError):
            MCPConfig(max_pages=101)

    def test_from_env(self):
        """Test configuration from environment variables."""
        env_vars = {
            "KLEINANZEIGEN_API_URL": "https://env.api.com",
            "KLEINANZEIGEN_API_KEY": "env-key",
            "KLEINANZEIGEN_TIMEOUT": "45.0",
            "KLEINANZEIGEN_MAX_RESULTS": "30",
            "KLEINANZEIGEN_MAX_PAGES": "15"
        }

        with patch.dict(os.environ, env_vars):
            config = MCPConfig.from_env()
            assert config.api_base_url == "https://env.api.com"
            assert config.api_key == "env-key"
            assert config.timeout == 45.0
            assert config.max_results_per_page == 30
            assert config.max_pages == 15

    def test_partial_env(self):
        """Test configuration with partial environment variables."""
        env_vars = {
            "KLEINANZEIGEN_API_KEY": "partial-key",
            "KLEINANZEIGEN_TIMEOUT": "15.0"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPConfig.from_env()
            assert config.api_base_url == "https://api.kleinanzeigen-agent.de"  # Default
            assert config.api_key == "partial-key"
            assert config.timeout == 15.0
            assert config.max_results_per_page == 50  # Default
            assert config.max_pages == 20  # Default