"""apps_rg profile builder — W0.5C migration target.

Builds AppRuntimeProfile for apps_rg and provides parse_payload as the
canonical payload normalizer.  The profile is consumed by AppIngressRunner
via the profile= kwarg; AppIngressRunner computes proof fields (profile_digest,
binding_digest_map) before any dispatch occurs.

No app-specific logic may be added to agentic_core in exchange for this file.
This module is the boundary: everything apps_rg-specific lives here or in
apps_rg.runtime.dispatch / apps_rg.runtime.bindings.
"""
from __future__ import annotations

from typing import Any, Mapping

from agentic_core.runtime.entry.app_ingress_runner import AppRuntimeProfile
from apps_rg.runtime.dispatch import (
    APPS_RG_REQUIRED_FIELDS,
    apps_rg_dispatch,
    apps_rg_parse,
)


def parse_payload(payload: Mapping[str, Any]) -> Any | None:
    """Thin re-export of apps_rg_parse for profile consumers.

    Signature matches AppRuntimeProfile.parse:
        (payload: Mapping[str, Any]) -> RequestEnvelope | None
    """
    return apps_rg_parse(payload)


def build_app_runtime_contract() -> AppRuntimeProfile:
    """Construct and return the canonical AppRuntimeProfile for apps_rg.

    AppIngressRunner will populate profile_digest and binding_digest_map
    before dispatch; do not pre-populate those fields here.

    profile.dispatch is set to apps_rg_dispatch so that
    AppIngressRunner(profile=profile).run(payload) needs no separate dispatch= kwarg.

    Returns
    -------
    AppRuntimeProfile
        Ready to pass as AppIngressRunner(profile=profile).run(payload).
    """
    return AppRuntimeProfile(
        app_id="apps_rg",
        required_fields=APPS_RG_REQUIRED_FIELDS,
        parse=parse_payload,
        dispatch=apps_rg_dispatch,
        profile_version="1",
    )


__all__ = [
    "build_app_runtime_contract",
    "parse_payload",
]
