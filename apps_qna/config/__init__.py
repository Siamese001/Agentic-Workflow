"""apps_qna config layer."""

from __future__ import annotations

from apps_qna.config.build_config import QnaBuildConfig
from apps_qna.config.route_registry import Route, RouteRegistry, load_route_registry

__all__ = ["QnaBuildConfig", "Route", "RouteRegistry", "load_route_registry"]
