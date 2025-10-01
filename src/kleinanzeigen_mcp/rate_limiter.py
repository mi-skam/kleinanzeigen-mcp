"""Rate limiting implementation for Kleinanzeigen MCP."""

import asyncio
import time
from collections import deque
from typing import Optional

from .constants import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW


class RateLimiter:
    """Token bucket rate limiter for API requests."""

    def __init__(
        self,
        max_requests: int = RATE_LIMIT_REQUESTS,
        window_seconds: int = RATE_LIMIT_WINDOW
    ):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_times: deque = deque()
        self._lock = asyncio.Lock()

    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire permission to make a request.

        Args:
            timeout: Maximum time to wait for permission (seconds)

        Returns:
            True if permission granted, False if timeout exceeded
        """
        start_time = time.time()

        while True:
            async with self._lock:
                now = time.time()

                # Remove old requests outside the window
                while self.request_times and self.request_times[0] <= now - self.window_seconds:
                    self.request_times.popleft()

                # Check if we can make a request
                if len(self.request_times) < self.max_requests:
                    self.request_times.append(now)
                    return True

                # Calculate wait time
                if self.request_times:
                    oldest_request = self.request_times[0]
                    wait_time = oldest_request + self.window_seconds - now
                else:
                    wait_time = 0

            # Check timeout
            if timeout is not None and time.time() - start_time + wait_time > timeout:
                return False

            # Wait before retrying
            await asyncio.sleep(min(wait_time, 0.1))

    def reset(self):
        """Reset the rate limiter."""
        self.request_times.clear()

    @property
    def available_requests(self) -> int:
        """Get the number of available requests."""
        now = time.time()

        # Remove old requests
        while self.request_times and self.request_times[0] <= now - self.window_seconds:
            self.request_times.popleft()

        return max(0, self.max_requests - len(self.request_times))


# Global rate limiter instance
rate_limiter = RateLimiter()