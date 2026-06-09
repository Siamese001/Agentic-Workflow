"""apps_rg-local X1D judge preflight and proof policy (no agentic_core imports).

Aligns CI proof configuration with ``REQUIRED_JUDGE_PROVIDER_KEYS`` in section judge policy and with
``run_llm_judges`` credential checks in ``executive_summary_x1d`` (same primary ``*_API_KEY`` env
names — no silent substitution of providers).

Generation uses Claude-family providers; proof X1D judges are cross-provider external LLM providers
(Gemini/OpenAI by default) and are not interchangeable with the generation provider unless explicitly
added by override.
"""

from __future__ import annotations

import os
from typing import Any, Mapping

from apps_rg.runtime.judges.executive_summary_x1d import (
    PROVIDERS as X1D_RUN_LLM_PROVIDERS,
    resolve_x1d_provider_credentials,
)
from apps_rg.runtime.section_judge_policy import REQUIRED_JUDGE_PROVIDER_KEYS

# Explicit default for CI lane-dev boundary helpers — matches section_judge_policy.
APPS_RG_E2E_DEFAULT_X1D_JUDGES = ",".join(REQUIRED_JUDGE_PROVIDER_KEYS)

_PROVIDER_TYPES: dict[str, str] = {
    "gemini_pro": "external_cloud_llm_judge",
    "openai_chatgpt": "external_cloud_llm_judge",
    "anthropic_claude": "external_cloud_llm_judge",
}


def _split_judges(raw: str) -> list[str]:
    return [p.strip() for p in (raw or "").split(",") if p.strip()]


def _env_nonempty(keys: tuple[str, ...], environ: Mapping[str, str]) -> bool:
    for k in keys:
        v = (environ.get(k) or "").strip()
        if v:
            return True
    return False


def _primary_env_for_runtime(provider_key: str) -> str | None:
    meta = X1D_RUN_LLM_PROVIDERS.get(provider_key)
    if not meta:
        return None
    return str(meta.get("env") or "")


def provider_has_credentials(provider_key: str, environ: Mapping[str, str] | None = None) -> bool:
    """True iff ``resolve_x1d_provider_credentials`` finds a non-empty credential (parity with judges)."""
    env = dict(os.environ if environ is None else environ)
    key_val, _ = resolve_x1d_provider_credentials(provider_key, env)
    return bool(key_val)


def preflight_x1d_judge_policy(
    environ: Mapping[str, str] | None = None,
    *,
    configured_judge_csv: str | None = None,
    repo_dotenv_path_existed: bool = False,
    repo_dotenv_loaded: bool = False,
) -> dict[str, Any]:
    """Return judge policy summary for proof harness and whole-run Exit.

    ``quorum_satisfied`` means: configured list includes every required provider key **and**
    each required provider has the same credential env populated that ``run_llm_judges`` checks
    (``PROVIDERS[provider_key].env``). This does not guarantee runtime MODEL_BACKED_PASS (rate
    limits, soft fails, etc.).
    """
    env = dict(os.environ if environ is None else environ)
    raw = (configured_judge_csv if configured_judge_csv is not None else env.get("APPS_RG_E2E_X1D_JUDGES", "")).strip()
    if not raw:
        raw = APPS_RG_E2E_DEFAULT_X1D_JUDGES

    configured = _split_judges(raw)
    required = list(REQUIRED_JUDGE_PROVIDER_KEYS)
    valid_keys = set(X1D_RUN_LLM_PROVIDERS.keys())

    unknown = [p for p in configured if p not in valid_keys]
    malformed = not configured or bool(unknown)

    missing_vs_contract = [p for p in required if p not in configured]
    extra = [p for p in configured if p not in required]

    per_provider: dict[str, dict[str, Any]] = {}
    provider_types: dict[str, str] = {}
    env_vars_checked: dict[str, list[str]] = {}

    available: list[str] = []
    unavailable: list[str] = []
    for pk in required:
        if pk not in configured:
            continue
        pt = _PROVIDER_TYPES.get(pk, "unknown")
        provider_types[pk] = pt
        primary = _primary_env_for_runtime(pk)
        _val, consulted = resolve_x1d_provider_credentials(pk, env)
        env_list = list(consulted) if consulted else ([primary] if primary else [])
        env_vars_checked[pk] = env_list
        ok = bool(_val)
        per_provider[pk] = {
            "provider_type": pt,
            "primary_env": primary,
            "credential_env_candidates": env_list,
            "credential_env_non_empty": ok,
        }
        if ok:
            available.append(pk)
        else:
            unavailable.append(pk)

    quorum_satisfied = (
        not malformed
        and not missing_vs_contract
        and len(available) == len(required)
    )

    model_backed_judges = list(available)
    deterministic_evaluators: list[str] = []

    decisive_reason = ""
    if malformed:
        decisive_reason = f"MALFORMED_X1D_JUDGE_CONFIG: unknown_keys={unknown!r} empty={not configured}"
    elif missing_vs_contract:
        decisive_reason = (
            "CONFIGURED_JUDGES_MISSING_REQUIRED_PROVIDERS: "
            f"missing={missing_vs_contract!r}; "
            f"proof must invoke {required!r} to satisfy lane X2 gates"
        )
    elif unavailable:
        decisive_reason = (
            "REQUIRED_JUDGE_CREDENTIALS_UNAVAILABLE: "
            f"missing_env_for={unavailable!r}"
        )
    elif quorum_satisfied:
        decisive_reason = (
            "X1D_PREFLIGHT_QUORUM_SATISFIED: all required providers have a non-empty resolved credential "
            "per resolve_x1d_provider_credentials / run_llm_judges "
            "(Gemini: GOOGLE_API_KEY, then deprecated GEMINI_API_KEY alias)."
        )

    remediation_parts: list[str] = [
        "Credential resolver: apps_rg.runtime.judges.executive_summary_x1d.resolve_x1d_provider_credentials — "
        "same chain as lane judges (Gemini prefers GOOGLE_API_KEY, then deprecated GEMINI_API_KEY).",
        f"Checked env vars (non-secret): {env_vars_checked!r}",
    ]
    if unavailable:
        hints: list[str] = []
        for p in unavailable:
            cands = env_vars_checked.get(p) or [str(_primary_env_for_runtime(p) or p)]
            hints.append(f"{p}=({', '.join(str(x) for x in cands if x)})")
        remediation_parts.append("Set non-empty credential for — " + "; ".join(hints))
    if repo_dotenv_path_existed and not repo_dotenv_loaded:
        remediation_parts.append(
            "Repo .env exists but python-dotenv failed to import — install python-dotenv or export keys in the shell."
        )
    elif repo_dotenv_path_existed and repo_dotenv_loaded:
        remediation_parts.append(
            "Repo-root .env was loaded into the harness env (override=False) before preflight so it matches dispatch load_dotenv()."
        )
    elif not repo_dotenv_path_existed:
        remediation_parts.append(
            "No repo-root .env file found — export GOOGLE_API_KEY (Gemini/Google AI Studio; GEMINI_API_KEY is deprecated), "
            "OPENAI_API_KEY, ANTHROPIC_API_KEY for judges, "
            "or add them to .env at the repository root (dispatch modules call load_dotenv() at import)."
        )

    remediation_hint = " ".join(remediation_parts)

    return {
        "credential_vs_runtime_capability_disclaimer": (
            "Quorum preflight validates the same credential resolver as lane judges: "
            "resolve_x1d_provider_credentials (Gemini tries GOOGLE_API_KEY then deprecated GEMINI_API_KEY). "
            "It does not prove live quota tiers, RPM/RPD limits, billing state, OAuth/network egress, "
            "SDK availability, allowed model catalogs, or that judge HTTP calls succeed."
        ),
        "env_var_primary": "APPS_RG_E2E_X1D_JUDGES",
        "default_if_unset_csv": APPS_RG_E2E_DEFAULT_X1D_JUDGES,
        "validator_contract_required": list(required),
        "credential_resolver": (
            "apps_rg.runtime.judges.executive_summary_x1d.resolve_x1d_provider_credentials "
            "(run_llm_judges parity)"
        ),
        "repo_dotenv_path_existed": bool(repo_dotenv_path_existed),
        "repo_dotenv_loaded": bool(repo_dotenv_loaded),
        "resolver_sources_checked": [
            "executive_summary_x1d.resolve_x1d_provider_credentials",
            "apps_rg.runtime.dispatch.* load_dotenv() parity via canonical apps_rg repo .env bootstrap",
        ],
        "configured_judges": configured,
        "required_judges": required,
        "optional_judges": extra,
        "unknown_provider_keys": unknown,
        "missing_required_vs_contract": missing_vs_contract,
        "provider_types": provider_types,
        "model_backed_judges": model_backed_judges,
        "deterministic_evaluators": deterministic_evaluators,
        "env_vars_checked": env_vars_checked,
        "per_provider": per_provider,
        "available_judges": available,
        "unavailable_judges": unavailable,
        "quorum_satisfied": quorum_satisfied,
        "policy_valid": not malformed,
        "decisive_reason": decisive_reason,
        "remediation_hint": remediation_hint,
    }
