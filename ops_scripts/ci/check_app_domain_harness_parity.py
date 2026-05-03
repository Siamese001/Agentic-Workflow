"""check_app_domain_harness_parity — apps_* eval-harness parity advisory gate.

Plan: ``.windsurf/plans/apps-eval-harness-parity-f8d4a2.md`` W5.P6.

ADVISORY-ONLY mode (as of commit-time): exit 0 regardless of findings so
pre-commit does not block while the harness is still being wired. Findings
are emitted to stdout + a JSON report at
``artifacts/ci/app_domain_harness_parity.json``. Promote to fail-closed in
a follow-up wave once all 8 apps are green.

Checks per app:
    - CONTRACT_EXISTS: app_domain_manifest.yaml exists with status field
    - RUBRIC_EXISTS: eval_rubrics.yaml exists with score_dimensions
    - THRESHOLD_EXISTS: threshold_profiles.yaml exists with hitl_policy field
    - NO_DEAD_THRESHOLDS: no dim has min_required_score == 0.0 (info only)
    - NO_FAILOPEN_LLM_JUDGE: no dim has grader_type=llm_as_judge AND
      fail_closed_if_unknown=false AND (grader_roster for the dim is empty
      OR missing entirely)
    - HITL_POLICY_VALID: hitl_policy in
      {none, required_on_low, required_always}
    - CONTRACT_STATUS_KNOWN: status in {active, draft, deprecated, retired}

Exit codes:
    0 — always (advisory)

Promotion path to fail-closed:
    Set env ``APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=1`` → findings of
    severity ERROR exit 1. Use this in a follow-up phase once the 8 apps
    are known-green.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# W4.P2 — Convention-based resolver for LLM-judge grader IDs.
# Roster IDs carry shape "<prefix>::<snake_name>::<version>" where <prefix>
# is an app short-code. We resolve to "apps_<mapped>.engines.judges.<snake_name>"
# and try to importlib.import_module the path. Missing imports become
# NO_UNIMPL_JUDGES WARNs — they are the W4.P2 implementation backlog.
_ROSTER_PREFIX_MAP: dict[str, str] = {
    "rg": "apps_rg",
    "lic": "apps_lic",
    "rfp": "apps_rfp",
    "qna": "apps_qna",
    "research": "apps_research",
    "exec": "apps_exec",
    "uw": "apps_underwriting_ai",
    "underwriting_ai": "apps_underwriting_ai",
    "eval": "apps_eval",
}


def _resolve_judge_importable(roster_id: str) -> tuple[bool, str]:
    """Return (importable, expected_path_or_reason).

    Convention: "<prefix>::<snake_name>::<version>"
      → "<apps_pkg>.engines.judges.<snake_name>"
    Examples:
      "rg::executive_positioning_judge::v1"
        → apps_rg.engines.judges.executive_positioning_judge
      "lic::response_likelihood_judge::v1"
        → apps_lic.engines.judges.response_likelihood_judge
    """
    parts = str(roster_id).split("::")
    if len(parts) < 2:
        return False, f"malformed::{roster_id}"
    prefix, name = parts[0], parts[1]
    app_pkg = _ROSTER_PREFIX_MAP.get(prefix)
    if not app_pkg:
        return False, f"unknown_prefix::{prefix}"
    mod_path = f"{app_pkg}.engines.judges.{name}"
    try:
        importlib.import_module(mod_path)
        return True, mod_path
    except ImportError:
        return False, mod_path

REPO_ROOT = Path(__file__).resolve().parents[2]

# W4.P2 / W2 — when invoked as a script (python ops_scripts/ci/<gate>.py),
# sys.path[0] is the gate's directory, not the repo root, so importlib
# cannot resolve apps_<x>.engines.judges.<name>. Prepend REPO_ROOT so the
# NO_UNIMPL_JUDGES check can import-probe apps packages under any invocation.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# W5.P6 — SSOT list of runtime apps evaluated by this gate. Consolidate
# later via a shared constants module if/when more apps are added.
RUNTIME_APPS: tuple[str, ...] = (
    "apps_rg",
    "apps_lic",
    "apps_rfp",
    "apps_qna",
    "apps_research",
    "apps_exec",
    "apps_underwriting_ai",
    "apps_eval",
)

VALID_HITL_POLICIES: frozenset[str] = frozenset(
    {"none", "required_on_low", "required_always"}
)
VALID_CONTRACT_STATUSES: frozenset[str] = frozenset(
    {"active", "draft", "deprecated", "retired"}
)

# W3.P4 — canonical Anthropic grader types (mirrors app_domain.GRADER_TYPE_VOCAB).
# Kept as a local frozenset so the gate does not fail-hard if the upstream
# vocab module is unavailable during a partial rebuild.
VALID_GRADER_TYPES: frozenset[str] = frozenset(
    {
        "deterministic", "llm_as_judge", "hybrid",
        "tool_calls", "state_check", "transcript", "trajectory_match",
    }
)

VALID_TRAJECTORY_MATCH_MODES: frozenset[str] = frozenset(
    {"strict", "unordered", "subset", "superset", "none", ""},
)

VALID_TAXONOMY_CLASSES: frozenset[str] = frozenset(
    {"capability", "regression", "tracked_metric"},
)


def _intentional_failopen_dims_for_app(thresholds: list[Any]) -> set[str]:
    """Collect the union of `intentional_failopen_dims` across an app's
    threshold profiles. Dims listed here are deliberately fail-open LLM
    judges (RAG baselines are the canonical case) and must be skipped by
    both NO_FAILOPEN_LLM_JUDGE and NO_UNIMPL_JUDGES checks until their
    producers wire real graders.
    """
    out: set[str] = set()
    for tp in thresholds:
        if not isinstance(tp, dict):
            continue
        items = tp.get("intentional_failopen_dims") or []
        if isinstance(items, list):
            out.update(str(x) for x in items)
    return out


@dataclass(slots=True)
class Finding:
    app_id: str
    check_id: str
    severity: str  # "ERROR" | "WARN" | "INFO"
    message: str
    detail: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id,
            "check_id": self.check_id,
            "severity": self.severity,
            "message": self.message,
            "detail": self.detail,
        }


def _load_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except FileNotFoundError:
        return None
    except yaml.YAMLError as exc:
        return {"__parse_error__": str(exc)}


def _as_list(doc: Any) -> list[Any]:
    if doc is None:
        return []
    if isinstance(doc, list):
        return list(doc)
    if isinstance(doc, dict):
        return [doc]
    return []


def _check_one_app(app_id: str) -> list[Finding]:
    findings: list[Finding] = []
    base = REPO_ROOT / app_id / "config" / "domain_contract"

    manifest_path = base / "app_domain_manifest.yaml"
    rubric_path = base / "eval_rubrics.yaml"
    threshold_path = base / "threshold_profiles.yaml"
    roster_path = base / "grader_roster.yaml"

    # -- CONTRACT_EXISTS --
    manifest = _load_yaml(manifest_path)
    if manifest is None:
        findings.append(Finding(
            app_id=app_id,
            check_id="CONTRACT_EXISTS",
            severity="ERROR",
            message=f"Missing {manifest_path.relative_to(REPO_ROOT)}",
        ))
        return findings

    if isinstance(manifest, dict) and "__parse_error__" in manifest:
        findings.append(Finding(
            app_id=app_id,
            check_id="CONTRACT_EXISTS",
            severity="ERROR",
            message=f"YAML parse error in manifest: {manifest['__parse_error__']}",
        ))
        return findings

    status = str(manifest.get("status", "")) if isinstance(manifest, dict) else ""
    if status not in VALID_CONTRACT_STATUSES:
        findings.append(Finding(
            app_id=app_id,
            check_id="CONTRACT_STATUS_KNOWN",
            severity="ERROR",
            message=f"Contract status {status!r} not in {sorted(VALID_CONTRACT_STATUSES)}",
            detail={"status": status},
        ))
    elif status == "draft":
        findings.append(Finding(
            app_id=app_id,
            check_id="CONTRACT_STATUS_KNOWN",
            severity="WARN",
            message="Contract status=draft — not certifiable until flipped to active",
            detail={"status": status},
        ))

    # -- RUBRIC_EXISTS --
    rubric_doc = _load_yaml(rubric_path)
    rubrics = _as_list(rubric_doc)
    if not rubrics:
        findings.append(Finding(
            app_id=app_id,
            check_id="RUBRIC_EXISTS",
            severity="ERROR",
            message=f"No rubric at {rubric_path.relative_to(REPO_ROOT)}",
        ))
        return findings

    # -- THRESHOLD_EXISTS + HITL_POLICY_VALID --
    threshold_doc = _load_yaml(threshold_path)
    thresholds = _as_list(threshold_doc)
    if not thresholds:
        findings.append(Finding(
            app_id=app_id,
            check_id="THRESHOLD_EXISTS",
            severity="ERROR",
            message=f"No threshold profile at {threshold_path.relative_to(REPO_ROOT)}",
        ))
    for tp in thresholds:
        if not isinstance(tp, dict):
            continue
        tid = str(tp.get("threshold_profile_id", "<unknown>"))
        policy = str(tp.get("hitl_policy", "none"))
        if policy not in VALID_HITL_POLICIES:
            findings.append(Finding(
                app_id=app_id,
                check_id="HITL_POLICY_VALID",
                severity="ERROR",
                message=f"{tid}: invalid hitl_policy {policy!r}",
                detail={"hitl_policy": policy, "allowed": sorted(VALID_HITL_POLICIES)},
            ))

    # -- NO_DEAD_THRESHOLDS --
    # W4.P3 (plan apps-eval-harness-parity-f8d4a2): threshold_profiles may
    # declare `intentional_zero_dims: [dim_id, ...]` to mark dims whose
    # min=0.0 is deliberate (tracked-only, not gated per-dim). Those entries
    # are excluded from WARN. Dims with min=0.0 NOT in that list remain WARN
    # so genuine misconfigurations still surface.
    for tp in thresholds:
        if not isinstance(tp, dict):
            continue
        tid = str(tp.get("threshold_profile_id", "<unknown>"))
        overall = tp.get("overall_pass_threshold")
        if isinstance(overall, (int, float)) and overall == 0.0:
            findings.append(Finding(
                app_id=app_id,
                check_id="NO_DEAD_THRESHOLDS",
                severity="WARN",
                message=f"{tid}: overall_pass_threshold=0.0 (dead threshold)",
                detail={"overall_pass_threshold": overall},
            ))
        intentional_zero = set()
        izd = tp.get("intentional_zero_dims") or []
        if isinstance(izd, list):
            intentional_zero = {str(x) for x in izd}
        dim_mins = tp.get("dimension_minimums", {})
        if isinstance(dim_mins, dict):
            for dim_id, val in dim_mins.items():
                if not isinstance(val, (int, float)) or val != 0.0:
                    continue
                if dim_id in intentional_zero:
                    continue  # annotated as deliberate — suppress WARN
                findings.append(Finding(
                    app_id=app_id,
                    check_id="NO_DEAD_THRESHOLDS",
                    severity="WARN",
                    message=f"{tid}: dimension_minimums[{dim_id}]=0.0 (dead threshold)",
                    detail={"dimension_id": dim_id},
                ))

    # -- NO_FAILOPEN_LLM_JUDGE --
    roster_doc = _load_yaml(roster_path)
    rosters = _as_list(roster_doc)
    llm_judge_graders: set[str] = set()
    for roster in rosters:
        if not isinstance(roster, dict):
            continue
        for g in roster.get("llm_judge_graders", []) or []:
            llm_judge_graders.add(str(g))

    for rubric in rubrics:
        if not isinstance(rubric, dict):
            continue
        rid = str(rubric.get("eval_rubric_id", "<unknown>"))
        for dim in rubric.get("score_dimensions", []) or []:
            if not isinstance(dim, dict):
                continue
            gtype = str(dim.get("grader_type", ""))
            dim_id = str(dim.get("dimension_id", ""))
            min_req = dim.get("min_required_score")
            fail_closed = dim.get("fail_closed_if_unknown", True)
            # W3.P4 — canonical grader-type validation
            if gtype and gtype not in VALID_GRADER_TYPES:
                findings.append(Finding(
                    app_id=app_id,
                    check_id="INVALID_GRADER_TYPE",
                    severity="ERROR",
                    message=(
                        f"{rid} dim {dim_id}: grader_type={gtype!r} not in "
                        f"{sorted(VALID_GRADER_TYPES)}"
                    ),
                    detail={"dimension_id": dim_id, "grader_type": gtype},
                ))
            # W3.P4 — optional trajectory_match_mode validation
            tmm = str(dim.get("trajectory_match_mode", "") or "")
            if tmm and tmm not in VALID_TRAJECTORY_MATCH_MODES:
                findings.append(Finding(
                    app_id=app_id,
                    check_id="INVALID_TRAJECTORY_MATCH_MODE",
                    severity="ERROR",
                    message=(
                        f"{rid} dim {dim_id}: trajectory_match_mode={tmm!r} not in "
                        f"{sorted(VALID_TRAJECTORY_MATCH_MODES - {''})}"
                    ),
                    detail={"dimension_id": dim_id, "trajectory_match_mode": tmm},
                ))
            # W5.P3 — taxonomy_class validation + coverage INFO
            taxonomy = str(dim.get("taxonomy_class", "") or "")
            if taxonomy and taxonomy not in VALID_TAXONOMY_CLASSES:
                findings.append(Finding(
                    app_id=app_id,
                    check_id="INVALID_TAXONOMY_CLASS",
                    severity="ERROR",
                    message=(
                        f"{rid} dim {dim_id}: taxonomy_class={taxonomy!r} not in "
                        f"{sorted(VALID_TAXONOMY_CLASSES)}"
                    ),
                    detail={"dimension_id": dim_id, "taxonomy_class": taxonomy},
                ))
            elif not taxonomy:
                findings.append(Finding(
                    app_id=app_id,
                    check_id="TAXONOMY_COVERAGE",
                    severity="INFO",
                    message=(
                        f"{rid} dim {dim_id}: taxonomy_class unset — annotate as "
                        f"capability / regression / tracked_metric"
                    ),
                    detail={"dimension_id": dim_id},
                ))
            # Dead threshold at dim level
            if isinstance(min_req, (int, float)) and min_req == 0.0:
                findings.append(Finding(
                    app_id=app_id,
                    check_id="NO_DEAD_THRESHOLDS",
                    severity="WARN",
                    message=f"{rid} dim {dim_id}: min_required_score=0.0 (dead threshold)",
                    detail={"dimension_id": dim_id},
                ))
            # Fail-open LLM-judge (original check: roster entirely empty)
            # apps-eval-harness-closeout-b7c9d2 W1: threshold profiles may
            # declare `intentional_failopen_dims: [dim_id, ...]` to mark
            # RAG-baseline-style dims deliberately left fail-open until
            # producers wire them. Same semantics as intentional_zero_dims.
            if gtype == "llm_as_judge" and not fail_closed and not llm_judge_graders:
                if dim_id not in _intentional_failopen_dims_for_app(thresholds):
                    findings.append(Finding(
                        app_id=app_id,
                        check_id="NO_FAILOPEN_LLM_JUDGE",
                        severity="ERROR",
                        message=(
                            f"{rid} dim {dim_id}: grader_type=llm_as_judge AND "
                            f"fail_closed_if_unknown=false AND grader_roster empty"
                        ),
                        detail={"dimension_id": dim_id, "grader_type": gtype},
                    ))

    # -- NO_UNIMPL_JUDGES (W4.P2) --
    # For every llm_as_judge dim, find the matching roster ID by name
    # convention and check whether it resolves to an importable Python
    # module. Missing imports are WARN (action-item backlog), not ERROR
    # — the W1 generic grader handles absence fail-soft per
    # fail_closed_if_unknown.
    _failopen_dims = _intentional_failopen_dims_for_app(thresholds)
    for rubric in rubrics:
        if not isinstance(rubric, dict):
            continue
        rid = str(rubric.get("eval_rubric_id", "<unknown>"))
        for dim in rubric.get("score_dimensions", []) or []:
            if not isinstance(dim, dict):
                continue
            if str(dim.get("grader_type", "")) != "llm_as_judge":
                continue
            dim_id = str(dim.get("dimension_id", ""))
            # Skip dims explicitly annotated as intentionally fail-open
            # (RAG baselines); their roster entries arrive with producer wiring.
            if dim_id in _failopen_dims:
                continue
            # Find candidate roster IDs by suffix match on "<snake>_judge" or "<snake>".
            candidates = [
                rid_s for rid_s in llm_judge_graders
                if f"::{dim_id}_judge::" in rid_s or f"::{dim_id}::" in rid_s
            ]
            if not candidates:
                findings.append(Finding(
                    app_id=app_id,
                    check_id="NO_UNIMPL_JUDGES",
                    severity="WARN",
                    message=(
                        f"{rid} dim {dim_id}: llm_as_judge but no roster entry "
                        f"matches the dimension_id — register a judge or demote"
                    ),
                    detail={"dimension_id": dim_id},
                ))
                continue
            # Check importability of at least one candidate.
            resolved: list[tuple[bool, str]] = [
                _resolve_judge_importable(c) for c in candidates
            ]
            any_importable = any(ok for ok, _ in resolved)
            if not any_importable:
                paths = [p for _, p in resolved]
                findings.append(Finding(
                    app_id=app_id,
                    check_id="NO_UNIMPL_JUDGES",
                    severity="WARN",
                    message=(
                        f"{rid} dim {dim_id}: llm_as_judge roster IDs "
                        f"{candidates} declared but no Python impl at "
                        f"expected path(s): {paths}"
                    ),
                    detail={
                        "dimension_id": dim_id,
                        "roster_ids": candidates,
                        "expected_paths": paths,
                    },
                ))

    # -- NO_CERT_EXIT_INVOCATION (W2.P3) --
    # When cert_route_registry.yaml declares invoke_exit_eval: true for a
    # route, the per-app cert entrypoint MUST adopt the
    # apps_shared.cert.exit_eval_hook.maybe_invoke_exit_eval hook. We
    # verify adoption by grepping the app package for the import. Missing
    # adoption is WARN (not ERROR) because the flag is opt-in and the
    # hook is fail-soft; the WARN drives follow-up.
    cert_registry_path = REPO_ROOT / app_id / "config" / "cert_route_registry.yaml"
    if cert_registry_path.exists():
        cert_doc = _load_yaml(cert_registry_path)
        routes = []
        if isinstance(cert_doc, dict):
            routes = list(cert_doc.get("routes") or [])
        elif isinstance(cert_doc, list):
            routes = cert_doc
        opted_in_routes = [
            r for r in routes
            if isinstance(r, dict) and bool(r.get("invoke_exit_eval", False))
        ]
        if opted_in_routes:
            app_root = REPO_ROOT / app_id
            import_hit = False
            for py_path in app_root.rglob("*.py"):
                try:
                    text = py_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if "maybe_invoke_exit_eval" in text or "apps_shared.cert" in text:
                    import_hit = True
                    break
            if not import_hit:
                findings.append(Finding(
                    app_id=app_id,
                    check_id="NO_CERT_EXIT_INVOCATION",
                    severity="WARN",
                    message=(
                        f"{len(opted_in_routes)} cert route(s) declare "
                        f"invoke_exit_eval: true but no {app_id}/ file imports "
                        f"apps_shared.cert.exit_eval_hook — adoption pending"
                    ),
                    detail={
                        "opted_in_route_ids": [str(r.get("route_id", "")) for r in opted_in_routes],
                        "expected_import": "from apps_shared.cert import maybe_invoke_exit_eval",
                    },
                ))

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="apps_* eval-harness parity advisory gate")
    parser.add_argument(
        "--report",
        default=str(REPO_ROOT / "artifacts" / "ci" / "app_domain_harness_parity.json"),
        help="Where to write the JSON findings report",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON-only to stdout (for programmatic consumption)",
    )
    args = parser.parse_args(argv)

    all_findings: list[Finding] = []
    for app_id in RUNTIME_APPS:
        all_findings.extend(_check_one_app(app_id))

    by_sev: dict[str, int] = {"ERROR": 0, "WARN": 0, "INFO": 0}
    for f in all_findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1

    report = {
        "apps_checked": list(RUNTIME_APPS),
        "counts": by_sev,
        "findings": [f.as_dict() for f in all_findings],
    }

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("=" * 72)
        print("apps_* eval-harness parity — ADVISORY REPORT")
        print("=" * 72)
        print(f"Apps checked: {len(RUNTIME_APPS)}")
        print(f"Findings: ERROR={by_sev['ERROR']}  WARN={by_sev['WARN']}  INFO={by_sev['INFO']}")
        print(f"Report: {args.report}")
        if all_findings:
            print("-" * 72)
            for f in all_findings:
                print(f"[{f.severity:5s}] {f.app_id:24s} {f.check_id:24s} {f.message}")
        else:
            print("All apps green.")
        print("=" * 72)

    fail_closed = os.environ.get("APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED") == "1"
    if fail_closed and by_sev["ERROR"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
