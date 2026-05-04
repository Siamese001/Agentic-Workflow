"""CI gate — apps_research FEC v1.1 field wiring (advisory).

Plan: apps-research-spine-deferred-followup-9c3e1a P4.2
Constitutional: §36 (plan registration), advisory by default.

Checks
------
1. ``apps_research.cert.fec_producer.produce_fec`` returns
   ``schema_version == "1.1"`` and all 10 v1.1 field keys present.
2. ``apps_research.integrations.governed_research_run.GovernedE2ERunRecord``
   dataclass has ``research_depth_profile`` and ``fec_run_context`` fields.
3. ``apps_research.engines.company_brief_engine`` re-exports
   ``_COVERAGE_FAMILY_CATALOG``, ``_DEPTH_PROFILES``,
   ``_PROFILE_REQUIRED_FAMILIES``, ``_resolve_depth_profile`` from
   ``query_decomposer`` (backward-compat shim intact).

Exit codes
----------
0  All checks pass (or ``APPS_RESEARCH_FEC_V11_BYPASS=1`` bypasses).
1  One or more checks failed AND ``APPS_RESEARCH_FEC_V11_FAIL_CLOSED=1``.
   Default: advisory (exit 0 with printed warnings).
"""
from __future__ import annotations

import dataclasses
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo-root on sys.path so importlib can resolve apps_research packages
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_BYPASS = os.environ.get("APPS_RESEARCH_FEC_V11_BYPASS", "").strip() in {"1", "true"}
_FAIL_CLOSED = os.environ.get("APPS_RESEARCH_FEC_V11_FAIL_CLOSED", "").strip() in {"1", "true"}

_FEC_V11_FIELDS = (
    "schema_version",
    "research_depth_profile",
    "jd_present",
    "jd_ref",
    "jd_content_hash",
    "freshness_violations",
    "unsupported_claim_count",
    "jd_unsupported_claim_count",
    "jd_to_company_evidence_map_present",
    "citation_anchor_count",
    "recruiter_outreach_overlay_present",
)

_RECORD_V11_FIELDS = ("research_depth_profile", "fec_run_context")

_SHIM_SYMBOLS = (
    "_COVERAGE_FAMILY_CATALOG",
    "_DEPTH_PROFILES",
    "_PROFILE_REQUIRED_FAMILIES",
    "_resolve_depth_profile",
)


def _check_fec_producer() -> list[str]:
    errors: list[str] = []
    try:
        from apps_research.cert.fec_producer import produce_fec
        fec = produce_fec({})
        if fec.get("schema_version") != "1.1":
            errors.append(
                f"fec_producer: schema_version={fec.get('schema_version')!r}, expected '1.1'"
            )
        missing = [k for k in _FEC_V11_FIELDS if k not in fec]
        if missing:
            errors.append(f"fec_producer: missing v1.1 keys: {missing}")
    except Exception as exc:
        errors.append(f"fec_producer import/call failed: {exc}")
    return errors


def _check_governed_e2e_record() -> list[str]:
    errors: list[str] = []
    try:
        from apps_research.integrations.governed_research_run import GovernedE2ERunRecord
        fields = {f.name for f in dataclasses.fields(GovernedE2ERunRecord)}
        missing = [f for f in _RECORD_V11_FIELDS if f not in fields]
        if missing:
            errors.append(f"GovernedE2ERunRecord: missing v1.1 fields: {missing}")
    except Exception as exc:
        errors.append(f"GovernedE2ERunRecord import failed: {exc}")
    return errors


def _check_engine_shim() -> list[str]:
    errors: list[str] = []
    try:
        import apps_research.engines.company_brief_engine as cbe
        missing = [s for s in _SHIM_SYMBOLS if not hasattr(cbe, s)]
        if missing:
            errors.append(f"company_brief_engine shim: missing re-exports: {missing}")
    except Exception as exc:
        errors.append(f"company_brief_engine import failed: {exc}")
    return errors


def main() -> int:
    if _BYPASS:
        print("WARNING: APPS_RESEARCH_FEC_V11_BYPASS=1 — gate skipped")
        return 0

    all_errors: list[str] = []
    all_errors.extend(_check_fec_producer())
    all_errors.extend(_check_governed_e2e_record())
    all_errors.extend(_check_engine_shim())

    if all_errors:
        for err in all_errors:
            print(f"ERROR: {err}")
        if _FAIL_CLOSED:
            print(
                "FAIL-CLOSED: set APPS_RESEARCH_FEC_V11_FAIL_CLOSED=0 to downgrade to advisory."
            )
            return 1
        print(
            "ADVISORY: set APPS_RESEARCH_FEC_V11_FAIL_CLOSED=1 to fail-close this gate."
        )
        return 0

    print("✅ apps_research FEC v1.1 wiring gate: all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
