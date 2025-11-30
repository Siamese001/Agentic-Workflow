"""
Resume Engine Rate Limiting Middleware
LEVEL 5 - API rate limiting and throttling protection
"""

from fastapi import HTTPException, status, Request, Response
from typing import Dict, Optional
import time
import asyncio
from collections import defaultdict, deque

class RateLimiter:
    """In-memory rate limiter for API endpoints"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_window = defaultdict(deque)
        self.hour_window = defaultdict(deque)
        self.cleanup_interval = 300  # Clean up every 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove expired request timestamps"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        # Clean minute window
        cutoff_minute = current_time - 60
        for key, requests in list(self.minute_window.items()):
            while requests and requests[0] < cutoff_minute:
                requests.popleft()
            if not requests:
                del self.minute_window[key]
        
        # Clean hour window
        cutoff_hour = current_time - 3600
        for key, requests in list(self.hour_window.items()):
            while requests and requests[0] < cutoff_hour:
                requests.popleft()
            if not requests:
                del self.hour_window[key]
        
        self.last_cleanup = current_time
    
    def is_allowed(self, client_id: str) -> tuple[bool, Dict[str, int]]:
        """Check if request is allowed based on rate limits"""
        self._cleanup_old_requests()
        current_time = time.time()
        
        # Check minute limit
        minute_requests = self.minute_window[client_id]
        while minute_requests and minute_requests[0] < current_time - 60:
            minute_requests.popleft()
        
        # Check hour limit
        hour_requests = self.hour_window[client_id]
        while hour_requests and hour_requests[0] < current_time - 3600:
            hour_requests.popleft()
        
        if len(minute_requests) >= self.requests_per_minute:
            return False, {
                "remaining_minute": 0,
                "remaining_hour": max(0, self.requests_per_hour - len(hour_requests)),
                "reset_time_minute": int(minute_requests[0] + 60 - current_time),
                "reset_time_hour": int(hour_requests[0] + 3600 - current_time)
            }
        
        if len(hour_requests) >= self.requests_per_hour:
            return False, {
                "remaining_minute": max(0, self.requests_per_minute - len(minute_requests)),
                "remaining_hour": 0,
                "reset_time_minute": int(minute_requests[0] + 60 - current_time),
                "reset_time_hour": int(hour_requests[0] + 3600 - current_time)
            }
        
        # Record this request
        minute_requests.append(current_time)
        hour_requests.append(current_time)
        
        return True, {
            "remaining_minute": self.requests_per_minute - len(minute_requests),
            "remaining_hour": self.requests_per_hour - len(hour_requests),
            "reset_time_minute": int(60 - (current_time - minute_requests[0])),
            "reset_time_hour": int(3600 - (current_time - hour_requests[0]))
        }

class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        self.app = app
        self.rate_limiter = rate_limiter or RateLimiter()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        client_id = self._get_client_id(request)
        
        is_allowed, rate_info = self.rate_limiter.is_allowed(client_id)
        
        if not is_allowed:
            response = Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
            response.headers["X-RateLimit-Remaining-Minute"] = str(rate_info["remaining_minute"])
            response.headers["X-RateLimit-Remaining-Hour"] = str(rate_info["remaining_hour"])
            response.headers["X-RateLimit-Reset-Minute"] = str(rate_info["reset_time_minute"])
            response.headers["X-RateLimit-Reset-Hour"] = str(rate_info["reset_time_hour"])
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier for rate limiting"""
        # Use API key if available, otherwise IP address
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Fallback to client IP
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

# Global rate limiter instance
rate_limiter = RateLimiter()

__all__ = ["RateLimiter", "RateLimitMiddleware", "rate_limiter"]
