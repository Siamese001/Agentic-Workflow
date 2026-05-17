"""RG-SMOKE-BUNDLE — golden smoke dirs must carry RUN_BUNDLE_INDEX (+ RUN_LINKS on integrated).

apps-rg-run-evidence-consolidation-d2c8e4 DoD-4 follow-up.

Only checks **pinned** writer-produced smoke bundles (not arbitrary historical runs):

  - ``artifacts/apps_rg/runs/_proof_smoke_integrated``
  - ``artifacts/apps_rg/runtime_proofs/headline/mock/_proof_smoke_lane``

Behavior:

  - If neither directory exists → exit 0 (fresh CI clone / trimmed artifacts).

  - If a directory exists but ``RUN_BUNDLE_INDEX.json`` is missing or invalid schema → exit 1.

  - If integrated dir exists → also require ``RUN_LINKS.json`` with valid schema and
    ``modular_sections_root.mode == "default"`` (regenerate smoke with modular env unset).

Bypass: ``APPS_RG_SMOKE_BUNDLE_INDEX_BYPASS=1``.

Fail-closed when smoke dirs are missing: ``APPS_RG_SMOKE_BUNDLE_INDEX_FAIL_CLOSED=1``
(exits 3 with a clear message; use only in workspaces that promise golden smoke dirs).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_REPORT_PATH = _REPO_ROOT / "artifacts" / "ci" / "apps_rg_smoke_bundle_indexes_gate.json"

# Pinned smoke bundles produced by consolidated evidence smoke emission (plan d2c8e4).
_SMOKES: tuple[tuple[str, str], ...] = (
    ("integrated", "artifacts/apps_rg/runs/_proof_smoke_integrated"),
    ("lane_headline_mock", "artifacts/apps_rg/runtime_proofs/headline/mock/_proof_smoke_lane"),
)


def _emit_report(status: str, detail: dict[str, Any]) -> None:
    payload = {"gate": "RG-SMOKE-BUNDLE", "status": status, **detail}
    try:
        _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        _REPORT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def _validate_bundle_index_json(path: Path) -> tuple[bool, str]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, str(exc)
    try:
        from apps_rg.runtime.run_bundle_index import assert_run_bundle_index_document_shape

        assert_run_bundle_index_document_shape(raw)
    except (ImportError, ValueError) as exc:
        return False, str(exc)
    return True, ""


def _validate_run_links_integrated(repo_root: Path, integrated_dir: Path) -> tuple[bool, str]:
    rl = integrated_dir / "RUN_LINKS.json"
    if not rl.is_file():
        return False, "RUN_LINKS.json missing beside integrated smoke run"
    try:
        raw = json.loads(rl.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, str(exc)
    try:
        from apps_rg.runtime.run_correlation_links import assert_run_links_document_shape

        assert_run_links_document_shape(raw)
        mod = raw.get("modular_sections_root") or {}
        if mod.get("mode") != "default":
            return False, f"expected modular_sections_root.mode default, got {mod.get('mode')!r}"
    except (ImportError, ValueError, TypeError, KeyError) as exc:
        return False, str(exc)
    env_raw = os.environ.get("APPS_RG_MODULAR_R4_SECTIONS_ROOT", "").strip()
    if env_raw:
        return False, (
            "APPS_RG_MODULAR_R4_SECTIONS_ROOT is set; regenerate smoke RUN_LINKS with that "
            "var unset so modular_sections_root records default mode"
        )
    return True, ""


def validate_smoke_roots(repo_root: Path) -> tuple[list[str], list[str]]:
    """Returns (warnings, failures). Failures imply gate should exit 1."""

    warnings: list[str] = []
    failures: list[str] = []

    any_present = False

    for tag, rel in _SMOKES:
        p = repo_root / Path(*rel.split("/"))
        if not p.is_dir():
            continue
        any_present = True
        idx = p / "RUN_BUNDLE_INDEX.json"
        if not idx.is_file():
            failures.append(f"{tag}: missing RUN_BUNDLE_INDEX.json under {rel}")
            continue
        ok, msg = _validate_bundle_index_json(idx)
        if not ok:
            failures.append(f"{tag}: invalid RUN_BUNDLE_INDEX.json — {msg}")
        # Integrated smoke also correlates manifests.
        if tag == "integrated":
            ok_links, links_msg = _validate_run_links_integrated(repo_root, p)
            if not ok_links:
                failures.append(f"{tag}: {links_msg}")

    if not any_present:
        warnings.append("No golden smoke evidence dirs present; skipping bundle index asserts.")

    return warnings, failures


def main(argv: list[str] | None = None) -> int:
    del argv

    if os.environ.get("APPS_RG_SMOKE_BUNDLE_INDEX_BYPASS", "").strip() in ("1", "true", "yes"):
        print("[RG-SMOKE-BUNDLE] BYPASS — APPS_RG_SMOKE_BUNDLE_INDEX_BYPASS=1")
        _emit_report("bypassed", {})
        return 0

    fail_closed_no_smoke = os.environ.get("APPS_RG_SMOKE_BUNDLE_INDEX_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
        "yes",
    )

    warnings, failures = validate_smoke_roots(_REPO_ROOT)

    if warnings:
        for w in warnings:
            print(f"[RG-SMOKE-BUNDLE] note — {w}")

    if failures:
        print("[RG-SMOKE-BUNDLE] FAIL:")
        for f in failures:
            print(f"  - {f}")
        _emit_report("fail", {"failures": failures, "warnings": warnings})
        return 1

    if not any((_REPO_ROOT / Path(*rel.split("/"))).is_dir() for _t, rel in _SMOKES):
        msg = (
            "Golden smoke dirs absent; nothing to validate. "
            "Set APPS_RG_SMOKE_BUNDLE_INDEX_FAIL_CLOSED=1 only if CI must retain them."
        )
        if fail_closed_no_smoke:
            print(f"[RG-SMOKE-BUNDLE] FAIL — {msg}")
            _emit_report("fail_missing_required_smoke_roots", {"message": msg, "warnings": warnings})
            return 3

        print(f"[RG-SMOKE-BUNDLE] OK — {msg}")
        _emit_report("skip_absent_roots", {"warnings": warnings})
        return 0

    print("[RG-SMOKE-BUNDLE] OK — smoke bundle indexes (+ integrated RUN_LINKS) valid")
    _emit_report("pass", {"warnings": warnings})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
