"""Cross-app contract test fixtures.

This module defines shared fixtures that any apps_* contract test can import
to exercise the platform-wide invariants without duplicating boilerplate.

Platform contract (every domain app MUST satisfy):
  1. Request type round-trips through Pydantic (model_dump → model_validate).
  2. Config type round-trips through Pydantic.
  3. Result type round-trips AND exposes a `gate_violations: list[str]` field.

Usage:
    from tests._apps_contract.fixtures import APP_CONTRACT_REGISTRY
    import pytest

    @pytest.mark.parametrize(
        "app_id,request_kwargs,config_kwargs",
        APP_CONTRACT_REGISTRY.parametrize_minimal(),
    )
    def test_minimal_round_trip(app_id, request_kwargs, config_kwargs):
        ...

The registry is the single source of truth for "what minimal-valid input
each app accepts" — adding a new app means adding a row here, not writing
a new test from scratch.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (W4.4)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AppContract:
    """Declarative contract for a single domain app.

    Identifies the import path of the app's Request/Config/Result types and
    the minimal-valid kwargs required to construct each. This lets any
    cross-app contract test exercise every app uniformly.
    """

    app_id: str
    request_module: str  # e.g. "apps_eval.types"
    request_class: str   # e.g. "EvalRequest"
    config_module: str
    config_class: str
    result_module: str
    result_class: str
    request_kwargs: dict[str, Any] = field(default_factory=dict)
    config_kwargs: dict[str, Any] = field(default_factory=dict)
    result_kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class _Registry:
    contracts: tuple[AppContract, ...]

    def by_app(self, app_id: str) -> AppContract:
        for c in self.contracts:
            if c.app_id == app_id:
                return c
        raise KeyError(f"no contract registered for app_id={app_id!r}")

    def parametrize_minimal(self) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
        """Return a pytest.mark.parametrize-friendly tuple list."""
        return [
            (c.app_id, c.request_kwargs, c.config_kwargs)
            for c in self.contracts
        ]


APP_CONTRACT_REGISTRY = _Registry(
    contracts=(
        AppContract(
            app_id="apps_eval",
            request_module="apps_eval.types",
            request_class="EvalRequest",
            config_module="apps_eval.types",
            config_class="EvalConfig",
            result_module="apps_eval.types",
            result_class="EvalResult",
        ),
        AppContract(
            app_id="apps_research",
            request_module="apps_research.types",
            request_class="ResearchRequest",
            config_module="apps_research.types",
            config_class="ResearchConfig",
            result_module="apps_research.types",
            result_class="ResearchResult",
            request_kwargs={"topic": "platform engineering invariants"},
        ),
        AppContract(
            app_id="apps_lic",
            request_module="apps_lic.types",
            request_class="CampaignRequest",
            config_module="apps_lic.types",
            config_class="CampaignConfig",
            result_module="apps_lic.types",
            result_class="CampaignResult",
            request_kwargs={
                "campaign_id": "contract-test-001",
                # `config` is filled in resolve(); the framework constructs
                # the config first and threads it into request_kwargs at
                # parametrize time.
                "_config_required": True,
            },
            config_kwargs={
                "name": "contract-test",
                "target_audience": "engineering_leaders",
            },
        ),
    )
)


def import_class(module_path: str, class_name: str) -> type:
    """Import the named class from a module path; small wrapper for clarity."""
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


def build_request(contract: AppContract) -> Any:
    """Construct a minimal-valid Request instance for the given app.

    For apps that require a Config inside their Request (e.g. apps_lic),
    builds the config first and threads it in.
    """
    request_cls = import_class(contract.request_module, contract.request_class)
    kwargs = dict(contract.request_kwargs)
    if kwargs.pop("_config_required", False):
        config_cls = import_class(contract.config_module, contract.config_class)
        kwargs["config"] = config_cls(**contract.config_kwargs)
    return request_cls(**kwargs)


def build_config(contract: AppContract) -> Any:
    """Construct a minimal-valid Config instance for the given app."""
    config_cls = import_class(contract.config_module, contract.config_class)
    return config_cls(**contract.config_kwargs)


def build_result(contract: AppContract) -> Any:
    """Construct a minimal-valid Result instance for the given app."""
    result_cls = import_class(contract.result_module, contract.result_class)
    return result_cls(**contract.result_kwargs)


__all__ = [
    "APP_CONTRACT_REGISTRY",
    "AppContract",
    "build_config",
    "build_request",
    "build_result",
    "import_class",
]
