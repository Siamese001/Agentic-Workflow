"""
Rate Limiting Middleware for Outreach Engine
LEVEL 5 - Rate limiting and throttling for outreach API endpoints
"""

from fastapi import HTTPException, status, Request
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta
import time
from collections import defaultdict, deque
import threading

class OutreachRateLimitMiddleware:
    """Handles rate limiting for outreach engine API endpoints"""
    
    def __init__(self):
        # Rate limit configurations by user tier
        self.rate_limits = {
            "trial": {
                "requests_per_minute": 5,
                "requests_per_hour": 25,
                "requests_per_day": 100,
                "outreach_per_hour": 10,
                "concurrent_tasks": 1
            },
            "basic": {
                "requests_per_minute": 20,
                "requests_per_hour": 100,
                "requests_per_day": 1000,
                "outreach_per_hour": 50,
                "concurrent_tasks": 3
            },
            "premium": {
                "requests_per_minute": 60,
                "requests_per_hour": 500,
                "requests_per_day": 5000,
                "outreach_per_hour": 200,
                "concurrent_tasks": 10
            },
            "admin": {
                "requests_per_minute": 120,
                "requests_per_hour": 1000,
                "requests_per_day": 50000,
                "outreach_per_hour": 1000,
                "concurrent_tasks": 50
            }
        }
        
        # In-memory storage for rate limiting (in production, use Redis)
        self.request_history = defaultdict(lambda: defaultdict(deque))
        self.outreach_history = defaultdict(lambda: defaultdict(deque))
        self.concurrent_tasks = defaultdict(int)
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Cleanup interval for old data
        self.cleanup_interval = 300  # 5 minutes
        self.max_history_size = 1000
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        asyncio.create_task(self._cleanup_old_data())
    
    async def _cleanup_old_data(self):
        """Clean up old rate limiting data"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                current_time = time.time()
                cutoff_time = current_time - 86400  # 24 hours ago
                
                with self.lock:
                    # Clean request history
                    for user_id in list(self.request_history.keys()):
                        for window in list(self.request_history[user_id].keys()):
                            # Remove old requests
                            while (self.request_history[user_id][window] and 
                                   self.request_history[user_id][window][0] < cutoff_time):
                                self.request_history[user_id][window].popleft()
                            
                            # Remove empty windows
                            if not self.request_history[user_id][window]:
                                del self.request_history[user_id][window]
                        
                        # Remove users with no history
                        if not self.request_history[user_id]:
                            del self.request_history[user_id]
                    
                    # Clean outreach history
                    for user_id in list(self.outreach_history.keys()):
                        for window in list(self.outreach_history[user_id].keys()):
                            while (self.outreach_history[user_id][window] and 
                                   self.outreach_history[user_id][window][0] < cutoff_time):
                                self.outreach_history[user_id][window].popleft()
                            
                            if not self.outreach_history[user_id][window]:
                                del self.outreach_history[user_id][window]
                        
                        if not self.outreach_history[user_id]:
                            del self.outreach_history[user_id]
                
            except Exception as e:
                # Log error but continue cleanup
                print(f"Rate limit cleanup error: {e}")
    
    def _get_time_window(self, timestamp: float, window_type: str) -> str:
        """Get time window identifier for timestamp"""
        dt = datetime.fromtimestamp(timestamp)
        
        if window_type == "minute":
            return dt.strftime("%Y-%m-%d %H:%M")
        elif window_type == "hour":
            return dt.strftime("%Y-%m-%d %H")
        elif window_type == "day":
            return dt.strftime("%Y-%m-%d")
        else:
            return str(int(timestamp))
    
    async def check_rate_limit(
        self,
        user_id: str,
        user_role: str,
        request_type: str = "api_request"
    ) -> Dict[str, Any]:
        """
        Check if user is within rate limits
        
        Args:
            user_id: User identifier
            user_role: User role/tier
            request_type: Type of request (api_request, outreach_generation)
            
        Returns:
            Dictionary with rate limit status and remaining quotas
        """
        limits = self.rate_limits.get(user_role, self.rate_limits["trial"])
        current_time = time.time()
        
        with self.lock:
            if request_type == "api_request":
                return await self._check_api_rate_limit(user_id, limits, current_time)
            elif request_type == "outreach_generation":
                return await self._check_outreach_rate_limit(user_id, limits, current_time)
            else:
                raise ValueError(f"Unknown request type: {request_type}")
    
    async def _check_api_rate_limit(
        self,
        user_id: str,
        limits: Dict[str, int],
        current_time: float
    ) -> Dict[str, Any]:
        """Check API request rate limits"""
        # Check minute limit
        minute_window = self._get_time_window(current_time, "minute")
        minute_requests = self.request_history[user_id][minute_window]
        
        # Remove old requests from current minute
        minute_cutoff = current_time - 60
        while minute_requests and minute_requests[0] < minute_cutoff:
            minute_requests.popleft()
        
        if len(minute_requests) >= limits["requests_per_minute"]:
            return {
                "allowed": False,
                "reason": "minute_limit_exceeded",
                "retry_after": 60 - (current_time - minute_requests[0]),
                "limits": {
                    "requests_per_minute": limits["requests_per_minute"],
                    "requests_per_hour": limits["requests_per_hour"],
                    "requests_per_day": limits["requests_per_day"]
                },
                "usage": {
                    "requests_this_minute": len(minute_requests),
                    "requests_this_hour": self._get_hourly_requests(user_id, current_time),
                    "requests_today": self._get_daily_requests(user_id, current_time)
                }
            }
        
        # Check hour limit
        hourly_requests = self._get_hourly_requests(user_id, current_time)
        if hourly_requests >= limits["requests_per_hour"]:
            return {
                "allowed": False,
                "reason": "hour_limit_exceeded",
                "retry_after": 3600,
                "limits": limits,
                "usage": {
                    "requests_this_minute": len(minute_requests),
                    "requests_this_hour": hourly_requests,
                    "requests_today": self._get_daily_requests(user_id, current_time)
                }
            }
        
        # Check day limit
        daily_requests = self._get_daily_requests(user_id, current_time)
        if daily_requests >= limits["requests_per_day"]:
            return {
                "allowed": False,
                "reason": "day_limit_exceeded",
                "retry_after": 86400,
                "limits": limits,
                "usage": {
                    "requests_this_minute": len(minute_requests),
                    "requests_this_hour": hourly_requests,
                    "requests_today": daily_requests
                }
            }
        
        # Add current request
        minute_requests.append(current_time)
        
        return {
            "allowed": True,
            "limits": limits,
            "usage": {
                "requests_this_minute": len(minute_requests),
                "requests_this_hour": hourly_requests + 1,
                "requests_today": daily_requests + 1
            },
            "remaining": {
                "requests_this_minute": limits["requests_per_minute"] - len(minute_requests),
                "requests_this_hour": limits["requests_per_hour"] - (hourly_requests + 1),
                "requests_this_day": limits["requests_per_day"] - (daily_requests + 1)
            }
        }
    
    async def _check_outreach_rate_limit(
        self,
        user_id: str,
        limits: Dict[str, int],
        current_time: float
    ) -> Dict[str, Any]:
        """Check outreach generation rate limits"""
        # Check concurrent task limit
        if self.concurrent_tasks[user_id] >= limits["concurrent_tasks"]:
            return {
                "allowed": False,
                "reason": "concurrent_task_limit_exceeded",
                "retry_after": 30,  # Check again in 30 seconds
                "limits": limits,
                "usage": {
                    "concurrent_tasks": self.concurrent_tasks[user_id],
                    "outreach_this_hour": self._get_hourly_outreach(user_id, current_time)
                }
            }
        
        # Check hourly outreach limit
        hourly_outreach = self._get_hourly_outreach(user_id, current_time)
        if hourly_outreach >= limits["outreach_per_hour"]:
            return {
                "allowed": False,
                "reason": "hourly_outreach_limit_exceeded",
                "retry_after": 3600,
                "limits": limits,
                "usage": {
                    "concurrent_tasks": self.concurrent_tasks[user_id],
                    "outreach_this_hour": hourly_outreach
                }
            }
        
        # Add current outreach task
        hour_window = self._get_time_window(current_time, "hour")
        self.outreach_history[user_id][hour_window].append(current_time)
        self.concurrent_tasks[user_id] += 1
        
        return {
            "allowed": True,
            "limits": limits,
            "usage": {
                "concurrent_tasks": self.concurrent_tasks[user_id],
                "outreach_this_hour": hourly_outreach + 1
            },
            "remaining": {
                "concurrent_tasks": limits["concurrent_tasks"] - self.concurrent_tasks[user_id],
                "outreach_this_hour": limits["outreach_per_hour"] - (hourly_outreach + 1)
            }
        }
    
    def _get_hourly_requests(self, user_id: str, current_time: float) -> int:
        """Get number of requests in current hour"""
        hour_window = self._get_time_window(current_time, "hour")
        hour_cutoff = current_time - 3600
        
        requests = self.request_history[user_id][hour_window]
        while requests and requests[0] < hour_cutoff:
            requests.popleft()
        
        return len(requests)
    
    def _get_daily_requests(self, user_id: str, current_time: float) -> int:
        """Get number of requests today"""
        day_window = self._get_time_window(current_time, "day")
        day_cutoff = current_time - 86400
        
        total_requests = 0
        for hour_data in self.request_history[user_id].values():
            for request_time in hour_data:
                if request_time >= day_cutoff:
                    total_requests += 1
        
        return total_requests
    
    def _get_hourly_outreach(self, user_id: str, current_time: float) -> int:
        """Get number of outreach generations in current hour"""
        hour_window = self._get_time_window(current_time, "hour")
        hour_cutoff = current_time - 3600
        
        outreach = self.outreach_history[user_id][hour_window]
        while outreach and outreach[0] < hour_cutoff:
            outreach.popleft()
        
        return len(outreach)
    
    def release_concurrent_task(self, user_id: str):
        """Release a concurrent task slot"""
        with self.lock:
            if self.concurrent_tasks[user_id] > 0:
                self.concurrent_tasks[user_id] -= 1
    
    def get_user_rate_limit_status(self, user_id: str, user_role: str) -> Dict[str, Any]:
        """Get current rate limit status for user"""
        limits = self.rate_limits.get(user_role, self.rate_limits["trial"])
        current_time = time.time()
        
        return {
            "user_id": user_id,
            "user_role": user_role,
            "limits": limits,
            "current_usage": {
                "requests_this_minute": len(self.request_history[user_id][self._get_time_window(current_time, "minute")]),
                "requests_this_hour": self._get_hourly_requests(user_id, current_time),
                "requests_today": self._get_daily_requests(user_id, current_time),
                "outreach_this_hour": self._get_hourly_outreach(user_id, current_time),
                "concurrent_tasks": self.concurrent_tasks[user_id]
            },
            "remaining": {
                "requests_this_minute": limits["requests_per_minute"] - len(self.request_history[user_id][self._get_time_window(current_time, "minute")]),
                "requests_this_hour": limits["requests_per_hour"] - self._get_hourly_requests(user_id, current_time),
                "requests_today": limits["requests_per_day"] - self._get_daily_requests(user_id, current_time),
                "outreach_this_hour": limits["outreach_per_hour"] - self._get_hourly_outreach(user_id, current_time),
                "concurrent_tasks": limits["concurrent_tasks"] - self.concurrent_tasks[user_id]
            }
        }
    
    def reset_user_limits(self, user_id: str):
        """Reset rate limits for a specific user (admin function)"""
        with self.lock:
            if user_id in self.request_history:
                del self.request_history[user_id]
            if user_id in self.outreach_history:
                del self.outreach_history[user_id]
            if user_id in self.concurrent_tasks:
                del self.concurrent_tasks[user_id]
    
    def get_system_rate_limit_stats(self) -> Dict[str, Any]:
        """Get system-wide rate limiting statistics"""
        with self.lock:
            total_active_users = len(self.request_history)
            total_concurrent_tasks = sum(self.concurrent_tasks.values())
            
            role_stats = {}
            for user_id in self.request_history.keys():
                # In a real implementation, you'd get user role from database
                role = "basic"  # Default for demo
                role_stats[role] = role_stats.get(role, 0) + 1
            
            return {
                "total_active_users": total_active_users,
                "total_concurrent_tasks": total_concurrent_tasks,
                "users_by_role": role_stats,
                "memory_usage": {
                    "request_history_size": sum(len(windows) for windows in self.request_history.values()),
                    "outreach_history_size": sum(len(windows) for windows in self.outreach_history.values()),
                    "concurrent_tasks_size": len(self.concurrent_tasks)
                }
            }

# Create rate limit middleware instance
rate_limit_middleware = OutreachRateLimitMiddleware()

class OutreachRateLimitUtils:
    """Utility functions for rate limiting"""
    
    @staticmethod
    def get_retry_after_message(retry_after: int, reason: str) -> str:
        """Get user-friendly retry after message"""
        if retry_after < 60:
            return f"Rate limit exceeded. Please try again in {retry_after} seconds."
        elif retry_after < 3600:
            minutes = retry_after // 60
            return f"Rate limit exceeded. Please try again in {minutes} minutes."
        else:
            hours = retry_after // 3600
            return f"Rate limit exceeded. Please try again in {hours} hours."
    
    @staticmethod
    def get_upgrade_suggestion(user_role: str, reason: str) -> Optional[str]:
        """Get upgrade suggestion based on rate limit hit"""
        upgrade_map = {
            "trial": {
                "minute_limit_exceeded": "Upgrade to Basic for 4x more requests per minute",
                "hour_limit_exceeded": "Upgrade to Basic for 4x more requests per hour",
                "day_limit_exceeded": "Upgrade to Basic for 10x more requests per day"
            },
            "basic": {
                "minute_limit_exceeded": "Upgrade to Premium for 3x more requests per minute",
                "hour_limit_exceeded": "Upgrade to Premium for 5x more requests per hour",
                "day_limit_exceeded": "Upgrade to Premium for 5x more requests per day"
            },
            "premium": {
                "minute_limit_exceeded": "Contact support for higher limits",
                "hour_limit_exceeded": "Contact support for higher limits",
                "day_limit_exceeded": "Contact support for higher limits"
            }
        }
        
        return upgrade_map.get(user_role, {}).get(reason)

__all__ = [
    "rate_limit_middleware",
    "OutreachRateLimitMiddleware",
    "OutreachRateLimitUtils"
]
