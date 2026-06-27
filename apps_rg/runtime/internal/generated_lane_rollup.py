from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
    )


import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping

from apps_rg.runtime.disposition_authority import (
    EXIT_DISPOSITION_RECEIPT_ARTIFACT,
    resolve_lane_x3_from_artifact_refs,
)
from apps_rg.runtime.runtime_proof_layout import (
    is_accepted_real_llm_provider_bundle,
    load_latest_pointer,
    load_latest_successful_real_pointer,
    resolve_accepted_real_rollup_run_dir,
    resolve_rollup_run_dir,
)
from apps_rg.runtime.section_judge_policy import REQUIRED_JUDGE_PROVIDER_KEYS

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_PROOFS = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs"
ROLLUP_DIR = RUNTIME_PROOFS / "generated_lane_rollup"

# Canonical user-facing invocation (documentation only — does not execute).
CANONICAL_QWEN_JUDGES_FLAGS: str = (
    f"--provider external_claude --x1d-judges {','.join(REQUIRED_JUDGE_PROVIDER_KEYS)} "
    "--allow-non-allow-exit-zero"
)
COMPETENCIES_CANONICAL_QWEN_JUDGES_FLAGS: str = (
    "--provider external_claude --x1d-judges openai_chatgpt --allow-non-allow-exit-zero"
)


def canonical_lane_command(lane: str) -> str:
    flags = (
        COMPETENCIES_CANONICAL_QWEN_JUDGES_FLAGS
        if str(lane or "").strip().lower() == "competencies"
        else CANONICAL_QWEN_JUDGES_FLAGS
    )
    return f"python -m apps_rg --section {lane} {flags}"


def _mtime_iso_utc(path: Path) -> str | None:
    if not path.is_file():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _collect_freshness(lane: str, base: Path, l2: Mapping[str, Any]) -> dict[str, Any]:
    """Read-only artifact freshness (mtimes, provider_request, run_id). No wall-clock snapshot."""
    pr: dict[str, Any] = {}
    pr_path = base / "provider_request.json"
    if pr_path.is_file():
        try:
            pr = _load_json(pr_path)
            if not isinstance(pr, dict):
                pr = {}
        except (json.JSONDecodeError, OSError):
            pr = {}
    mtimes: dict[str, str | None] = {}
    for name in REQUIRED_RELATIVE:
        mtimes[name] = _mtime_iso_utc(base / name)
    l2p = base / "l2_output.json"
    return {
        "generated_at_utc": _mtime_iso_utc(l2p),
        "canonical_command": canonical_lane_command(lane),
        "provider_requested": pr.get("provider_requested"),
        "provider_attempted": pr.get("provider_attempted"),
        "runtime_generation_status": str(l2.get("runtime_generation_status", "")),
        "l2_run_id": l2.get("run_id"),
        "artifact_mtimes_utc": mtimes,
    }


# Canonical serial EXECUTION order (dependency-ordered).
#
# Proof flows upstream -> downstream:
#   1. upstream proof-bearing sections (competencies, unify_bullets, ibm_bullets) generate first;
#   2. narratives consume their finalized selected bullets;
#   3. executive_summary synthesizes finalized bullets + narratives + competencies;
#   4. headline is FINAL positioning and must not run before upstream proof / exec_summary finalize.
#
# This ordering is consumed as the serial Phase-1 loop in modular_resume_generation.py and as
# SECTION_ORDER in lane_batch.py. The rollup readers (build_rollup / build_modular_lane_rollup)
# aggregate by set membership, so order only affects display, not status. The parallel wave DAG
# lives in workflow_manifest.resume_sections.v1.yaml and mirrors this dependency order.
GENERATED_LANES: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
    "executive_summary",
    "headline",
)

REQUIRED_RELATIVE = (
    "l2_output.json",
    "x2_gate_outputs.json",
    "x1d_llm_judge_outputs.json",
    "x3_disposition.json",
    "l6_shadow_eval_package.json",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(p.resolve()).replace("\\", "/")


def _normalize_x1d_judges(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return list(raw)
    if isinstance(raw, dict) and isinstance(raw.get("judges"), list):
        return list(raw["judges"])
    return []


def _judge_provider_status(judge: Mapping[str, Any]) -> str:
    return str(
        judge.get("provider_status")
        or judge.get("evaluator_mode")
        or "UNKNOWN"
    )


def _normalize_blocked_soft(x3: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    blocked = list(x3.get("blocked_judges") or [])
    soft = list(x3.get("soft_failed_judges") or [])
    if blocked or soft or "blocked_judges" in x3 or "soft_failed_judges" in x3:
        return blocked, soft
    refs = x3.get("llm_judge_refs")
    if not isinstance(refs, list):
        return [], []
    b: list[str] = []
    s: list[str] = []
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        pk = ref.get("provider_key")
        if not pk:
            continue
        mode = str(ref.get("evaluator_mode", ""))
        if ref.get("provider_blocked") or "BLOCKED" in mode:
            b.append(str(pk))
        elif ref.get("decisive_failure"):
            continue
        elif ref.get("pass") is False:
            s.append(str(pk))
    return b, s


def _normalize_x2(raw: Any) -> dict[str, Any]:
    """Return gates list + tallies + failed ids (from pass flags and artifact fields)."""
    if isinstance(raw, list):
        gates = list(raw)
        failed_from_pass = [g["gate_id"] for g in gates if isinstance(g, dict) and not g.get("pass", True)]
        total = len(gates)
        passed = sum(1 for g in gates if isinstance(g, dict) and g.get("pass", True))
        return {
            "gates": gates,
            "failed_gate_ids": failed_from_pass,
            "x2_passed": passed,
            "x2_failed": len(failed_from_pass),
            "total_x2_gates": total,
            "artifact_failed_gates": [],
        }
    if isinstance(raw, dict):
        gates = list(raw.get("gates") or [])
        failed_from_pass = [g["gate_id"] for g in gates if isinstance(g, dict) and not g.get("pass", True)]
        explicit = list(raw.get("failed_gates") or [])
        artifact_failed = explicit if explicit else failed_from_pass
        total = int(raw.get("total_x2_gates", len(gates)))
        x2_passed = raw.get("x2_passed")
        x2_failed = raw.get("x2_failed")
        if x2_passed is None:
            x2_passed = sum(1 for g in gates if isinstance(g, dict) and g.get("pass", True))
        if x2_failed is None:
            x2_failed = len(failed_from_pass)
        return {
            "gates": gates,
            "failed_gate_ids": failed_from_pass,
            "x2_passed": int(x2_passed),
            "x2_failed": int(x2_failed),
            "total_x2_gates": total,
            "artifact_failed_gates": explicit,
        }
    return {
        "gates": [],
        "failed_gate_ids": [],
        "x2_passed": 0,
        "x2_failed": 0,
        "total_x2_gates": 0,
        "artifact_failed_gates": [],
    }


def _output_summary(l2: Mapping[str, Any], lane: str) -> dict[str, Any]:
    if lane == "headline":
        return {"kind": "headline_line", "text": l2.get("headline_line", "")}
    if lane == "executive_summary":
        t = str(l2.get("resume_display_text", ""))
        return {"kind": "resume_display_text", "preview": t[:400], "char_len": len(t)}
    if lane == "competencies":
        cats = l2.get("competencies")
        n = len(cats) if isinstance(cats, list) else 0
        return {"kind": "competencies", "category_count": n}
    if lane in {"unify_bullets", "ibm_bullets"}:
        bullets = l2.get("bullets")
        n = len(bullets) if isinstance(bullets, list) else 0
        return {"kind": "bullets", "bullet_count": n}
    if lane in {"unify_narrative", "ibm_narrative"}:
        sent = str(l2.get("narrative_sentence", ""))
        return {"kind": "narrative_sentence", "preview": sent[:400], "char_len": len(sent)}
    return {"kind": "unknown", "lane": lane}


def _judge_triple(judges: list[dict[str, Any]]) -> dict[str, str]:
    out = {"gemini_pro": "MISSING", "openai_chatgpt": "MISSING", "anthropic_claude": "MISSING"}
    for j in judges:
        pk = j.get("provider_key")
        if pk in out:
            out[str(pk)] = _judge_provider_status(j)
    return out


@dataclass(frozen=True)
class LanePaths:
    lane: str
    base: Path

    def p(self, name: str) -> Path:
        return self.base / name


def _lane_pointer_fields(repo: Path, lane: str) -> dict[str, Any]:
    real = load_latest_pointer(repo, lane, "real")
    mock = load_latest_pointer(repo, lane, "mock")
    successful = load_latest_successful_real_pointer(repo, lane)
    rid = real.get("run_id") if real else None
    rstat = str(real.get("runtime_generation_status", "")) if real else ""
    return {
        "latest_real_run_id": rid,
        "latest_real_generated_at_utc": real.get("generated_at_utc") if real else None,
        "latest_real_artifact_path": real.get("run_dir") if real else None,
        "latest_real_attempt_run_id": rid,
        "latest_real_attempt_runtime_generation_status": rstat or None,
        "latest_successful_real_run_id": successful.get("run_id") if successful else None,
        "latest_successful_real_generated_at_utc": successful.get("generated_at_utc") if successful else None,
        "latest_successful_real_artifact_path": successful.get("run_dir") if successful else None,
        "latest_successful_real_runtime_generation_status": (
            str(successful.get("runtime_generation_status", "")) if successful else None
        ),
        "latest_mock_run_id": mock.get("run_id") if mock else None,
        "latest_mock_generated_at_utc": mock.get("generated_at_utc") if mock else None,
        "latest_mock_artifact_path": mock.get("run_dir") if mock else None,
    }


def collect_lane(
    lane: str,
    *,
    repo: Path | None = None,
    rollup_artifact_mode: Literal["real", "mock"] = "real",
) -> dict[str, Any]:
    root = repo or REPO_ROOT
    accepted_real_evidence_resolution: str | None = None
    if rollup_artifact_mode == "mock":
        base = resolve_rollup_run_dir(root, lane, artifact_mode="mock")
        accepted_real_evidence_resolution = "latest_mock_run.json"
    else:
        base, accepted_real_evidence_resolution = resolve_accepted_real_rollup_run_dir(root, lane)
    if base is None:
        real_attempt = load_latest_pointer(root, lane, "real") if rollup_artifact_mode == "real" else None
        attempt_tail = ""
        if real_attempt:
            attempt_tail = (
                f" latest_real_attempt: run_id={real_attempt.get('run_id')!r} "
                f"runtime_generation_status={real_attempt.get('runtime_generation_status')!r} "
                f"(not used as accepted real evidence)."
            )
        raise FileNotFoundError(
            f"Lane {lane!r}: missing_successful_real_run — no accepted REAL_LLM live-provider bundle "
            f"(latest_successful_real_run.json, migration scan of real/*, and legacy flat exhausted) "
            f"under {_rel(RUNTIME_PROOFS / lane)}.{attempt_tail}"
        )
    missing = [n for n in REQUIRED_RELATIVE if not (base / n).is_file()]
    if missing:
        raise FileNotFoundError(f"Lane {lane!r} missing artifacts under {_rel(base)}: {missing}")

    lp = LanePaths(lane=lane, base=base)
    l2 = _load_json(lp.p("l2_output.json"))
    x2_raw = _load_json(lp.p("x2_gate_outputs.json"))
    x1d_raw = _load_json(lp.p("x1d_llm_judge_outputs.json"))
    x3 = _load_json(lp.p("x3_disposition.json"))
    l6 = _load_json(lp.p("l6_shadow_eval_package.json"))

    x2n = _normalize_x2(x2_raw)
    judges = _normalize_x1d_judges(x1d_raw)
    blocked, soft = _normalize_blocked_soft(x3)
    triple = _judge_triple(judges)

    artifact_refs = {n: _rel(lp.p(n)) for n in REQUIRED_RELATIVE}
    if (base / EXIT_DISPOSITION_RECEIPT_ARTIFACT).is_file():
        artifact_refs[EXIT_DISPOSITION_RECEIPT_ARTIFACT] = _rel(
            base / EXIT_DISPOSITION_RECEIPT_ARTIFACT
        )
    x3_auth = resolve_lane_x3_from_artifact_refs(
        artifact_refs=artifact_refs,
        repo_root=root,
    )
    pointers = _lane_pointer_fields(root, lane)

    section_id = str(l2.get("section_id") or lane)
    runtime_gen = str(
        l2.get("runtime_generation_status") or x3.get("runtime_generation_status") or "UNKNOWN"
    )
    rollup_x3_code = str(x3_auth.get("x3_code") or x3.get("x3_code", ""))

    return {
        "lane_key": lane,
        "section_id": section_id,
        "rollup_source_run_dir": _rel(base),
        "accepted_real_evidence_resolution": accepted_real_evidence_resolution,
        **pointers,
        "runtime_generation_status": runtime_gen,
        "freshness": _collect_freshness(lane, base, l2),
        "output_summary": _output_summary(l2, lane),
        "x2_total_gates": x2n["total_x2_gates"],
        "x2_passed": x2n["x2_passed"],
        "x2_failed": x2n["x2_failed"],
        "x2_failed_gate_ids": list(x2n["failed_gate_ids"]),
        "x2_artifact_failed_gates": list(x2n["artifact_failed_gates"]),
        "gemini_provider_status": triple["gemini_pro"],
        "openai_provider_status": triple["openai_chatgpt"],
        "anthropic_provider_status": triple["anthropic_claude"],
        "soft_failed_judges": soft,
        "blocked_judges": blocked,
        "x3_code": rollup_x3_code,
        "disposition_authority": str(x3_auth.get("disposition_authority") or "lane"),
        "x3_authoritative_artifact": x3_auth.get("authoritative_artifact"),
        "section_x3_mirror_only": bool(x3_auth.get("section_x3_mirror_only", True)),
        "spine_x3_claimed": bool(x3_auth.get("spine_x3_claimed", False)),
        "authorization_scope": str(x3.get("authorization_scope", "")),
        "proceed_to_runtime": bool(x3.get("proceed_to_runtime", False)),
        "l6_offline_only": bool(l6.get("offline_only", False)),
        "artifact_refs": artifact_refs,
    }


def _lane_pointer_fields_modular(base: Path, l2: Mapping[str, Any]) -> dict[str, Any]:
    """Pointer-shaped fields when rollup reads explicit modular ``sections/<lane>/`` run dirs."""
    rid = l2.get("run_id")
    return {
        "latest_real_run_id": None,
        "latest_real_generated_at_utc": None,
        "latest_real_artifact_path": None,
        "latest_real_attempt_run_id": None,
        "latest_real_attempt_runtime_generation_status": None,
        "latest_successful_real_run_id": None,
        "latest_successful_real_generated_at_utc": None,
        "latest_successful_real_artifact_path": None,
        "latest_successful_real_runtime_generation_status": None,
        "latest_mock_run_id": rid,
        "latest_mock_generated_at_utc": _mtime_iso_utc(base / "l2_output.json"),
        "latest_mock_artifact_path": _rel(base),
    }


def collect_lane_from_run_dir(lane: str, base: Path, *, repo: Path) -> dict[str, Any]:
    """Build one rollup lane row from an explicit run directory (R4 modular Phase 1+)."""
    missing = [n for n in REQUIRED_RELATIVE if not (base / n).is_file()]
    if missing:
        raise FileNotFoundError(f"Lane {lane!r} missing artifacts under {_rel(base)}: {missing}")

    lp = LanePaths(lane=lane, base=base)
    l2 = _load_json(lp.p("l2_output.json"))
    x2_raw = _load_json(lp.p("x2_gate_outputs.json"))
    x1d_raw = _load_json(lp.p("x1d_llm_judge_outputs.json"))
    x3 = _load_json(lp.p("x3_disposition.json"))
    l6 = _load_json(lp.p("l6_shadow_eval_package.json"))

    x2n = _normalize_x2(x2_raw)
    judges = _normalize_x1d_judges(x1d_raw)
    blocked, soft = _normalize_blocked_soft(x3)
    triple = _judge_triple(judges)

    artifact_refs = {n: _rel(lp.p(n)) for n in REQUIRED_RELATIVE}
    if (base / EXIT_DISPOSITION_RECEIPT_ARTIFACT).is_file():
        artifact_refs[EXIT_DISPOSITION_RECEIPT_ARTIFACT] = _rel(  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            base / EXIT_DISPOSITION_RECEIPT_ARTIFACT
        )
    x3_auth = resolve_lane_x3_from_artifact_refs(
        artifact_refs=artifact_refs,
        repo_root=repo,
    )
    pointers = _lane_pointer_fields_modular(base, l2)

    section_id = str(l2.get("section_id") or lane)
    runtime_gen = str(
        l2.get("runtime_generation_status") or x3.get("runtime_generation_status") or "UNKNOWN"
    )
    rollup_x3_code = str(x3_auth.get("x3_code") or x3.get("x3_code", ""))

    accepted_real_evidence_resolution = "modular_r4_explicit_run_dir"
    pointer_roots = (base.parent.parent, base)
    for pointer_root in pointer_roots:
        ptr_path = pointer_root / "latest_successful_real_run.json"
        if not ptr_path.is_file():
            continue
        try:
            raw_ptr = _load_json(ptr_path)
            rel = raw_ptr.get("run_dir") if isinstance(raw_ptr, dict) else None
            if isinstance(rel, str):
                ptr_base = (repo / rel).resolve()
                if ptr_base.resolve() == base.resolve() and is_accepted_real_llm_provider_bundle(base):
                    accepted_real_evidence_resolution = "latest_successful_real_run.json"
                    break
        except (json.JSONDecodeError, OSError, ValueError, TypeError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            pass

    return {
        "lane_key": lane,
        "section_id": section_id,
        "rollup_source_run_dir": _rel(base),
        "accepted_real_evidence_resolution": accepted_real_evidence_resolution,
        **pointers,
        "runtime_generation_status": runtime_gen,
        "freshness": _collect_freshness(lane, base, l2),
        "output_summary": _output_summary(l2, lane),
        "x2_total_gates": x2n["total_x2_gates"],
        "x2_passed": x2n["x2_passed"],
        "x2_failed": x2n["x2_failed"],
        "x2_failed_gate_ids": list(x2n["failed_gate_ids"]),
        "x2_artifact_failed_gates": list(x2n["artifact_failed_gates"]),
        "gemini_provider_status": triple["gemini_pro"],
        "openai_provider_status": triple["openai_chatgpt"],
        "anthropic_provider_status": triple["anthropic_claude"],
        "soft_failed_judges": soft,
        "blocked_judges": blocked,
        "x3_code": rollup_x3_code,
        "disposition_authority": str(x3_auth.get("disposition_authority") or "lane"),
        "x3_authoritative_artifact": x3_auth.get("authoritative_artifact"),
        "section_x3_mirror_only": bool(x3_auth.get("section_x3_mirror_only", True)),
        "spine_x3_claimed": bool(x3_auth.get("spine_x3_claimed", False)),
        "authorization_scope": str(x3.get("authorization_scope", "")),
        "proceed_to_runtime": bool(x3.get("proceed_to_runtime", False)),
        "l6_offline_only": bool(l6.get("offline_only", False)),
        "artifact_refs": artifact_refs,
    }


def build_modular_lane_rollup(repo: Path, lane_run_dirs: Mapping[str, Path]) -> dict[str, Any]:
    """Deterministic rollup from explicit per-lane run directories under ``modular_r4/sections``."""
    lanes: dict[str, Any] = {}
    errors: list[str] = []
    for lane in GENERATED_LANES:
        base = lane_run_dirs.get(lane)
        if base is None or not base.is_dir():
            errors.append(f"Lane {lane!r}: missing run directory")
            continue
        try:
            lanes[lane] = collect_lane_from_run_dir(lane, base, repo=repo)
        except FileNotFoundError as e:
            errors.append(str(e))
    if errors:
        raise FileNotFoundError("\n".join(errors))

    lanes_x3_allow = [k for k, v in lanes.items() if v.get("x3_code") == "X3_ALLOW"]
    lanes_x3_review = [
        k
        for k, v in lanes.items()
        if isinstance(v.get("x3_code"), str) and str(v["x3_code"]).startswith("X3_REVIEW")
    ]
    lanes_x2_failures = [k for k, v in lanes.items() if int(v.get("x2_failed") or 0) > 0]
    l6_offline_all = all(bool(v.get("l6_offline_only")) for v in lanes.values())
    lanes_real_llm = [k for k, v in lanes.items() if v.get("runtime_generation_status") == "REAL_LLM"]
    lanes_mocked = [k for k, v in lanes.items() if v.get("runtime_generation_status") == "MOCKED"]
    lanes_blocked_gen = [
        k
        for k, v in lanes.items()
        if str(v.get("runtime_generation_status", "")).upper().find("BLOCKED") >= 0
    ]
    current_mode = "modular_r4_sections"

    return {
        "rollup_id": f"modular_generated_lane_rollup_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": _rel(repo.resolve()),
        "current_rollup_artifact_mode": current_mode,
        "rollup_artifact_mode_arg": "modular_explicit",
        "artifact_isolation": {
            "layout": "modular_r4_sections",
            "run_dir_pattern": "<artifact_dir>/modular_r4/sections/<lane>/{real|mock}/<run_id>/",
            "pointer_files": ["latest_real_run.json", "latest_successful_real_run.json", "latest_mock_run.json"],
            "scoped_under_repo": True,
        },
        "evidence_pack_commands": {lane: canonical_lane_command(lane) for lane in GENERATED_LANES},
        "lanes": lanes,
        "summary": {
            "lane_keys": list(GENERATED_LANES),
            "lanes_with_x3_allow": lanes_x3_allow,
            "lanes_with_x3_review_prefix": lanes_x3_review,
            "lanes_with_x2_failures": lanes_x2_failures,
            "all_l6_offline_only": l6_offline_all,
            "lanes_runtime_generation_REAL_LLM": lanes_real_llm,
            "lanes_runtime_generation_MOCKED": lanes_mocked,
            "lanes_runtime_generation_BLOCKED_or_unknown": lanes_blocked_gen,
            "lanes_accepted_evidence_via_migration_scan": [],
            "lanes_latest_real_attempt_blocked_but_accepted_rollup_REAL_LLM": [],
        },
    }


def build_rollup(*, rollup_artifact_mode: Literal["real", "mock"] = "real") -> dict[str, Any]:
    lanes: dict[str, Any] = {}
    errors: list[str] = []
    for lane in GENERATED_LANES:
        try:
            lanes[lane] = collect_lane(lane, rollup_artifact_mode=rollup_artifact_mode)
        except FileNotFoundError as e:
            errors.append(str(e))
    if errors:
        raise FileNotFoundError("\n".join(errors))

    lanes_x3_allow = [k for k, v in lanes.items() if v.get("x3_code") == "X3_ALLOW"]
    lanes_x3_review = [
        k
        for k, v in lanes.items()
        if isinstance(v.get("x3_code"), str) and str(v["x3_code"]).startswith("X3_REVIEW")
    ]
    lanes_x2_failures = [k for k, v in lanes.items() if int(v.get("x2_failed") or 0) > 0]
    l6_offline_all = all(bool(v.get("l6_offline_only")) for v in lanes.values())
    lanes_real_llm = [k for k, v in lanes.items() if v.get("runtime_generation_status") == "REAL_LLM"]
    lanes_mocked = [k for k, v in lanes.items() if v.get("runtime_generation_status") == "MOCKED"]
    lanes_blocked_gen = [
        k
        for k, v in lanes.items()
        if str(v.get("runtime_generation_status", "")).upper().find("BLOCKED") >= 0
    ]
    lanes_accepted_via_migration = [
        k
        for k, v in lanes.items()
        if v.get("accepted_real_evidence_resolution") == "migration_real_llm_provider_scan"
    ]
    attempt_blocked_but_rollup_real_llm = [
        k
        for k, v in lanes.items()
        if str(v.get("latest_real_attempt_runtime_generation_status", "") or "").upper().find("BLOCKED")
        >= 0
        and str(v.get("runtime_generation_status", "")) == "REAL_LLM"
    ]

    evidence_pack_commands = {lane: canonical_lane_command(lane) for lane in GENERATED_LANES}

    current_mode = "mock" if rollup_artifact_mode == "mock" else "real_only"

    return {
        "rollup_id": f"generated_lane_rollup_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": _rel(REPO_ROOT),
        "current_rollup_artifact_mode": current_mode,
        "rollup_artifact_mode_arg": rollup_artifact_mode,
        "artifact_isolation": {
            "layout": "Option B",
            "run_dir_pattern": "artifacts/apps_rg/runtime_proofs/<lane>/{real|mock}/<run_id>/",
            "pointer_files": [
                "latest_real_run.json",
                "latest_successful_real_run.json",
                "latest_mock_run.json",
            ],
            "real_only_rollup_resolves": (
                "latest_successful_real_run.json, else newest eligible real/*/ (REAL_LLM+live provider), "
                "else legacy flat REAL_LLM+live provider — never latest_real_run.json alone."
            ),
        },
        "evidence_pack_commands": evidence_pack_commands,
        "lanes": lanes,
        "summary": {
            "lane_keys": list(GENERATED_LANES),
            "lanes_with_x3_allow": lanes_x3_allow,
            "lanes_with_x3_review_prefix": lanes_x3_review,
            "lanes_with_x2_failures": lanes_x2_failures,
            "all_l6_offline_only": l6_offline_all,
            "lanes_runtime_generation_REAL_LLM": lanes_real_llm,
            "lanes_runtime_generation_MOCKED": lanes_mocked,
            "lanes_runtime_generation_BLOCKED_or_unknown": lanes_blocked_gen,
            "lanes_accepted_evidence_via_migration_scan": lanes_accepted_via_migration,
            "lanes_latest_real_attempt_blocked_but_accepted_rollup_REAL_LLM": attempt_blocked_but_rollup_real_llm,
        },
    }


def _md_escape_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def render_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Generated lane rollup (read-only)")
    lines.append("")
    lines.append(f"- **rollup_id**: `{data.get('rollup_id', '')}`")
    lines.append(f"- **generated_at_utc**: {data.get('generated_at_utc', '')}")
    lines.append(f"- **current_rollup_artifact_mode**: {data.get('current_rollup_artifact_mode', '')}")
    lines.append(f"- **rollup_artifact_mode_arg**: {data.get('rollup_artifact_mode_arg', '')}")
    lines.append("")
    lines.append("## Evidence pack commands (canonical)")
    lines.append("")
    for lane in GENERATED_LANES:
        lines.append(f"- **{lane}**: `{_md_escape_cell(str(data.get('evidence_pack_commands', {}).get(lane, '')))}`")
    lines.append("")
    lines.append("## Lane status")
    lines.append("")
    header = (
        "| lane | section_id | runtime_gen | x3_code | x2 pass/fail/total | "
        "Gemini | OpenAI | Anthropic | proceed | L6 offline | blocked | soft_fail |"
    )
    sep = "|---|---|:---:|---|---:|---|---|---|:---:|---|---|---|"
    lines.append(header)
    lines.append(sep)
    for lane in GENERATED_LANES:
        row = data["lanes"][lane]
        x2s = f"{row['x2_passed']}/{row['x2_failed']}/{row['x2_total_gates']}"
        cells = [
            lane,
            row["section_id"],
            row["runtime_generation_status"],
            row["x3_code"],
            x2s,
            row["gemini_provider_status"],
            row["openai_provider_status"],
            row["anthropic_provider_status"],
            str(row["proceed_to_runtime"]),
            str(row["l6_offline_only"]),
            ",".join(row["blocked_judges"]) or "—",
            ",".join(row["soft_failed_judges"]) or "—",
        ]
        lines.append("| " + " | ".join(_md_escape_cell(str(c)) for c in cells) + " |")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    s = data.get("summary", {})
    lines.append(f"- **lanes_with_x3_allow**: {', '.join(s.get('lanes_with_x3_allow', [])) or '—'}")
    lines.append(
        f"- **lanes_with_x3_review** (prefix X3_REVIEW): "
        f"{', '.join(s.get('lanes_with_x3_review_prefix', [])) or '—'}"
    )
    lines.append(f"- **lanes_with_x2_failures**: {', '.join(s.get('lanes_with_x2_failures', [])) or '—'}")
    lines.append(f"- **all_l6_offline_only**: {s.get('all_l6_offline_only', False)}")
    lines.append(f"- **REAL_LLM lanes**: {', '.join(s.get('lanes_runtime_generation_REAL_LLM', [])) or '—'}")
    lines.append(f"- **MOCKED lanes**: {', '.join(s.get('lanes_runtime_generation_MOCKED', [])) or '—'}")
    lines.append("")
    lines.append("## Per-lane freshness (L2 mtime + provider_request)")
    lines.append("")
    for lane in GENERATED_LANES:
        fr = data["lanes"][lane].get("freshness") or {}
        lines.append(
            f"- **{lane}**: L2 `generated_at_utc`={fr.get('generated_at_utc')}, "
            f"provider_requested={fr.get('provider_requested')}, run_id={fr.get('l2_run_id')}"
        )
    lines.append("")
    return "\n".join(lines)
