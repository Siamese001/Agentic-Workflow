"""Route registry — the SSOT mirror of `01_ROUTING_MANIFEST.md`.

Both the builder and the linter consume this YAML. If the routing manifest
evolves, this YAML changes first, then the templates.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class Route(BaseModel):
    """One primary route from the routing manifest."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    """Stable identifier, e.g. `executive_fit`."""

    number: int
    """Display number 1-9 from the routing manifest."""

    name: str
    """Human-readable name."""

    triggers: list[str] = Field(default_factory=list)
    """Phrase fragments that activate this route in the runtime."""

    answer_shape: list[str] = Field(default_factory=list)
    """Ordered list of answer-section labels."""

    primary_card: str
    """Filename of the primary card that owns this route. Required."""

    optional_specialists: list[str] = Field(default_factory=list)
    """Specialist cards that may also load (≤2 enforced by linter)."""


class RouteRegistry(BaseModel):
    """All 9 routes from the routing manifest, plus tie-breaker rules."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str = "v1"
    routes: list[Route] = Field(default_factory=list)
    tie_breaker_rules: list[str] = Field(default_factory=list)


_DEFAULT_REGISTRY_PATH = Path(__file__).parent / "route_registry.yaml"


def load_route_registry(path: Path | None = None) -> RouteRegistry:
    """Load the route registry from a YAML file.

    Args:
        path: Override path. Defaults to the bundled
            `apps_qna/config/route_registry.yaml`.

    Returns:
        A validated `RouteRegistry`.

    Raises:
        FileNotFoundError: the YAML file is missing.
        pydantic.ValidationError: the YAML is malformed.
    """
    target = path or _DEFAULT_REGISTRY_PATH
    if not target.is_file():
        raise FileNotFoundError(f"Route registry YAML not found: {target}")
    with target.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return RouteRegistry.model_validate(data)
