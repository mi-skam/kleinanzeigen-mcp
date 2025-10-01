"""Unit tests for rate limiter."""

import asyncio
import time

import pytest

from kleinanzeigen_mcp.rate_limiter import RateLimiter


@pytest.mark.asyncio
class TestRateLimiter:
    """Test rate limiter functionality."""

    async def test_basic_rate_limiting(self):
        """Test basic rate limiting functionality."""
        limiter = RateLimiter(max_requests=3, window_seconds=1)

        # Should allow 3 requests immediately
        for _ in range(3):
            assert await limiter.acquire(timeout=0.1)

        # 4th request should fail with timeout
        assert not await limiter.acquire(timeout=0.1)

    async def test_window_sliding(self):
        """Test that old requests are removed from window."""
        limiter = RateLimiter(max_requests=2, window_seconds=0.5)

        # Make 2 requests
        assert await limiter.acquire()
        assert await limiter.acquire()

        # 3rd should fail immediately
        assert not await limiter.acquire(timeout=0.1)

        # Wait for window to slide
        await asyncio.sleep(0.6)

        # Should allow new request
        assert await limiter.acquire()

    async def test_concurrent_requests(self):
        """Test rate limiting with concurrent requests."""
        limiter = RateLimiter(max_requests=5, window_seconds=1)

        async def make_request():
            return await limiter.acquire(timeout=0.1)

        # Launch 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # Only 5 should succeed
        successful = sum(1 for r in results if r)
        assert successful == 5

    async def test_available_requests(self):
        """Test available requests property."""
        limiter = RateLimiter(max_requests=3, window_seconds=1)

        assert limiter.available_requests == 3

        await limiter.acquire()
        assert limiter.available_requests == 2

        await limiter.acquire()
        await limiter.acquire()
        assert limiter.available_requests == 0

    async def test_reset(self):
        """Test reset functionality."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        # Use up all requests
        await limiter.acquire()
        await limiter.acquire()
        assert limiter.available_requests == 0

        # Reset
        limiter.reset()
        assert limiter.available_requests == 2

    async def test_no_timeout_waits(self):
        """Test that acquire without timeout waits for availability."""
        limiter = RateLimiter(max_requests=1, window_seconds=0.3)

        # First request succeeds immediately
        start = time.time()
        assert await limiter.acquire()

        # Second request should wait for window
        task = asyncio.create_task(limiter.acquire())
        await asyncio.sleep(0.1)  # Let it start waiting

        # Should not be done yet
        assert not task.done()

        # Wait for window to pass
        await asyncio.sleep(0.3)
        assert await task

        # Total time should be around 0.4 seconds
        elapsed = time.time() - start
        assert 0.3 < elapsed < 0.5