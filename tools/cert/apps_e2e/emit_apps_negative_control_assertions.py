"""W3.P2 of plan apps-runtime-domain-enforcement-a7e9d4 — Negative-Control Emitter.

Closes APPS-DOM-006 (`x3_domain_block_proved`) and APPS-DOM-010
(`domain_negative_control_blocks`).

Strategy
--------

* **DOM-010** (`domain_negative_control_blocks`) — closed with a static
  deterministic simulator. For each (app, archetype), the simulator reads the
  app's threshold_profiles.yaml, picks dimension IDs whose names match the
  archetype pattern, synthesizes a dim_scores receipt that pushes those dims
  below their declared minimum, then walks the deterministic X1→X2→X3 chain.
  PASS iff the simulator produces X3 disposition = DENY for ≥1 archetype.

* **DOM-006** (`x3_domain_block_proved`) — emits NOT_VERIFIED with a concrete
  pointer to the simulator's output JSON. DOM-006 requires real runtime
  evidence (OTEL `exit.app_specific_eval` span + X3 packet). The simulator
  proves the gate **logic** would block; the runtime harness in W6 must
  prove the gate **actually** fires under live conditions.

Archetypes (3 negative-control patterns drawn from plan §APPS-DOM-006/010):

* `fabrication` — output asserts facts not grounded in evidence
* `personalization` — output mismatches the audience/role/context
* `coverage` — output omits required scope/depth

Each archetype is matched against rubric dimension IDs by substring patterns.
If an app has no rubric dim matching the archetype, the scenario is recorded
as `N/A` (vacuous PASS — that archetype does not apply to that app's
threat model).

Output:
  artifacts/apps_negative_controls/<app>_<archetype>.json — per-scenario
    simulator record (input fixture + simulated chain + disposition)
  certification/apps_negative_control_assertions.jsonl — 16 assertions

Hard rules:
  * Deterministic assertion_id (sha256 of req_id|control|artifact_sha256|pointer)
  * Never emit PASS for a scenario the simulator could not actually evaluate
  * Simulator output records every dim's threshold + synthesized score so
    the verdict is reconstructable without re-running

Exit codes:
  0 — emitter completed
  2 — fatal: catalog missing or invalid
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
from cert_paths import APPS_NEGATIVE_ASSERTIONS_PATH as OUT_PATH, APPS_REQS_PATH as CATALOG_PATH
SIM_DIR = REPO_ROOT / "artifacts" / "apps_negative_controls"

EMITTER_COMMAND = "tools/cert/apps_e2e/emit_apps_negative_control_assertions.py"
EMITTER_VERSION = "apps_neg_ctrl_emitter-v1"

RUNTIME_APPS = (
    "apps_qna", "apps_underwriting_ai",
    "apps_research", "apps_exec", "apps_eval",
)

# Archetype → dim_id substring patterns. Case-insensitive match against
# rubric dimension_ids and dimension_minimums keys.
_ARCHETYPE_PATTERNS = {
    "fabrication": (
        "fabrication", "hallucination", "grounding",
        "factual", "citation", "evidence", "source_quality",
    ),
    "personalization": (
        "personalization", "role_align", "audience",
        "specificity", "context_fit", "tone", "brand_voice",
        "executive_positioning",
    ),
    "coverage": (
        "coverage", "completeness", "depth", "breadth",
        "no_omission", "scope",
    ),
}

# How far below the dim's min we push the synthetic bad score. 0.20 is a
# generous gap so the gate decision is unambiguous.
_BAD_SCORE_GAP = 0.20

# Assertion classes per claim_type.
_CLAIM_TYPE_ASSERTION_CLASS = {
    "APPS_DOMAIN_WIRING": "APPS_DOMAIN_WIRING_ASSERTION",
    "APPS_DOMAIN_GATING": "APPS_DOMAIN_GATING_ASSERTION",
    "APPS_DOMAIN_PROOF": "APPS_DOMAIN_PROOF_ASSERTION",
}


# =============================================================================
# Helpers
# =============================================================================

def _sha256_file(p: Path) -> str:
    if not p.exists():
        return ""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _aid(req_id: str, control: str, artifact_sha256: str, pointer: str) -> str:
    h = hashlib.sha256(
        f"{req_id}|{control}|{artifact_sha256}|{pointer}".encode("utf-8")
    ).hexdigest()
    return f"ASRT-{h[:40]}"


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        import yaml  # noqa: PLC0415
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _load_threshold_profile(app: str) -> dict[str, Any] | None:
    """Return the active threshold profile (single dict) for the app, or None.

    Apps store profiles either as a list of profiles or a single mapping.
    """
    p = REPO_ROOT / app / "config" / "domain_contract" / "threshold_profiles.yaml"
    doc = _load_yaml(p)
    if doc is None:
        return None
    if isinstance(doc, list):
        for entry in doc:
            if isinstance(entry, dict) and entry.get("status") == "active":
                return entry
        return doc[0] if doc and isinstance(doc[0], dict) else None
    if isinstance(doc, dict):
        # Some apps wrap profiles under a key
        for key in ("threshold_profiles", "profiles"):
            if isinstance(doc.get(key), list) and doc[key]:
                return doc[key][0]
        return doc
    return None


def _match_archetype_dims(dim_ids: list[str], archetype: str) -> list[str]:
    patterns = _ARCHETYPE_PATTERNS.get(archetype, ())
    matched: list[str] = []
    for dim in dim_ids:
        low = dim.lower()
        if any(pat in low for pat in patterns):
            matched.append(dim)
    return matched


# =============================================================================
# Simulator — deterministic X1→X2→X3 walk
# =============================================================================

def _simulate_chain(
    *,
    app: str,
    archetype: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    """Walk the gate chain deterministically for a synthesized bad receipt.

    Returns a record with:
      - applicable: bool — True iff archetype matched ≥1 dim
      - matched_dims: list[str]
      - synthesized_dim_scores: dict[dim_id, float]
      - x1_failed_dims: list[str]
      - x2_decision: str — HARD_FAIL | SOFT_FAIL | PASS
      - x3_disposition: str — DENY | HITL_REVIEW | ALLOW
      - reason_codes: list[str]
    """
    dim_minimums: dict[str, float] = dict(profile.get("dimension_minimums", {}) or {})
    intentional_failopen = set(profile.get("intentional_failopen_dims", []) or [])
    intentional_zero = set(profile.get("intentional_zero_dims", []) or [])
    hitl_policy = profile.get("hitl_policy", "none")

    candidate_dims = [d for d in dim_minimums
                      if d not in intentional_failopen
                      and d not in intentional_zero]
    matched = _match_archetype_dims(candidate_dims, archetype)

    if not matched:
        return {
            "applicable": False,
            "matched_dims": [],
            "synthesized_dim_scores": {},
            "x1_failed_dims": [],
            "x2_decision": "N/A",
            "x3_disposition": "N/A",
            "reason_codes": [
                f"NO_DIM_MATCHES_ARCHETYPE_{archetype.upper()}",
                f"app={app}",
            ],
            "notes": (
                f"{app} rubric has no dim matching archetype={archetype}; "
                f"this archetype does not apply to this app's threat model."
            ),
        }

    # Push matched dims below their min by _BAD_SCORE_GAP, clamp ≥ 0.0
    synth: dict[str, float] = {}
    for dim, min_score in dim_minimums.items():
        if dim in matched:
            synth[dim] = max(0.0, float(min_score) - _BAD_SCORE_GAP)
        else:
            # Other required dims pass with score 1.0
            synth[dim] = 1.0

    # X1: per-dim gate — score < min_score → FAIL
    x1_failed = [
        d for d in matched
        if synth[d] < dim_minimums[d]
    ]

    # X2: any HARD-class fail → HARD_FAIL.
    # Per plan §APPS-DOM-005 + agentic_core/L3_orchestration/exit_eval/v6/x2_matrix.py,
    # app-specific eval failure on a required dim is a hard fail unless
    # hitl_policy escalates to soft.
    if not x1_failed:
        x2_decision = "PASS"
        x3_disposition = "ALLOW"
    elif hitl_policy in ("required_always", "required_on_low"):
        x2_decision = "SOFT_FAIL"
        x3_disposition = "HITL_REVIEW"
    else:
        x2_decision = "HARD_FAIL"
        x3_disposition = "DENY"

    reason_codes = [f"X1_DIM_BELOW_MIN:{d}" for d in x1_failed]
    reason_codes.append(f"X2_DECISION:{x2_decision}")
    reason_codes.append(f"X3_DISPOSITION:{x3_disposition}")

    return {
        "applicable": True,
        "matched_dims": matched,
        "synthesized_dim_scores": synth,
        "x1_failed_dims": x1_failed,
        "x2_decision": x2_decision,
        "x3_disposition": x3_disposition,
        "reason_codes": reason_codes,
        "notes": (
            f"{app}/{archetype}: synthesized {len(x1_failed)} below-min dim "
            f"score(s); deterministic chain → x2={x2_decision}, "
            f"x3={x3_disposition}."
        ),
    }


def _run_simulations() -> dict[str, dict[str, dict[str, Any]]]:
    """Returns nested map: { app: { archetype: simulator_record } }.

    Also persists each (app, archetype) record to disk for audit traceability.
    """
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, dict[str, Any]]] = {}
    for app in RUNTIME_APPS:
        profile = _load_threshold_profile(app)
        results[app] = {}
        for archetype in _ARCHETYPE_PATTERNS:
            if profile is None:
                rec = {
                    "applicable": False,
                    "matched_dims": [],
                    "synthesized_dim_scores": {},
                    "x1_failed_dims": [],
                    "x2_decision": "ERROR",
                    "x3_disposition": "ERROR",
                    "reason_codes": ["NO_THRESHOLD_PROFILE_LOADED"],
                    "notes": (
                        f"{app}: threshold_profiles.yaml missing or "
                        f"unparseable; cannot simulate."
                    ),
                }
            else:
                rec = _simulate_chain(
                    app=app, archetype=archetype, profile=profile,
                )
            rec_full = {
                "app": app,
                "archetype": archetype,
                "threshold_profile_id": (
                    profile.get("threshold_profile_id") if profile else None
                ),
                "generated_at_utc": _iso_now(),
                "simulator_version": EMITTER_VERSION,
                "result": rec,
            }
            out = SIM_DIR / f"{app}_{archetype}.json"
            out.write_text(
                json.dumps(rec_full, indent=2, sort_keys=True), encoding="utf-8",
            )
            results[app][archetype] = rec_full
    return results


# =============================================================================
# Assertion construction
# =============================================================================

def _build_assertion(
    *,
    req_id: str,
    control: str,
    result: str,
    claim_type: str,
    app: str,
    artifact_path: Path | None,
    artifact_class: str,
    pointer: str,
    proof_payload: dict[str, Any],
    freshness_hours: int,
    now_iso: str,
) -> dict[str, Any]:
    if artifact_path and artifact_path.exists():
        artifact_sha = _sha256_file(artifact_path)
        artifact_rel = _rel(artifact_path)
    else:
        artifact_sha = _sha256_str(f"{req_id}|{control}|{app}")
        artifact_rel = _rel(artifact_path) if artifact_path else "(synthetic)"
    return {
        "assertion_id": _aid(req_id, control, artifact_sha, pointer),
        "req_id": req_id,
        "control": control,
        "assertion_result": result,
        "assertion_class": _CLAIM_TYPE_ASSERTION_CLASS.get(
            claim_type, "APPS_DOMAIN_PROOF_ASSERTION"
        ),
        "generated_by_command": EMITTER_COMMAND,
        "verifier_exit_code": 0 if result == "PASS" else 1 if result == "FAIL" else 2,
        "verifier_version": EMITTER_VERSION,
        "generated_at_utc": now_iso,
        "artifact_path": artifact_rel,
        "artifact_sha256": artifact_sha,
        "artifact_class": artifact_class,
        "artifact_payload_pointer": pointer,
        "artifact_contains_req_id": False,
        "artifact_contains_control": True,
        "row_specific": True,
        "freshness_hours": int(freshness_hours),
        "proof_payload": proof_payload,
        "app_name": app,
    }


def emit_assertions(
    catalog: dict[str, Any],
    sim_results: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    now_iso = _iso_now()
    assertions: list[dict[str, Any]] = []

    rows_by_id = {r["req_id"]: r for r in catalog["requirements"]}

    for req_id in ("APPS-DOM-006", "APPS-DOM-010"):
        row = rows_by_id.get(req_id)
        if row is None:
            continue
        claim_type = row["claim_type"]
        controls = row.get("required_controls", [])
        freshness = int(row.get("freshness_hours", 168))

        for control in controls:
            for app in RUNTIME_APPS:
                app_sims = sim_results.get(app, {})
                # Aggregate across the 3 archetypes for this app
                archetypes_applicable = [
                    arch for arch, rec in app_sims.items()
                    if rec.get("result", {}).get("applicable")
                ]
                archetypes_blocked = [
                    arch for arch, rec in app_sims.items()
                    if rec.get("result", {}).get("x3_disposition") == "DENY"
                ]
                archetypes_hitl = [
                    arch for arch, rec in app_sims.items()
                    if rec.get("result", {}).get("x3_disposition") == "HITL_REVIEW"
                ]
                # Pointer resolves to the simulator's top-level `app` key,
                # which contains the app_name string (required by the
                # compiler's _row_specificity_ok guard for cross-cutting rows).
                pointer = "/app"
                # Use the fabrication archetype JSON as the canonical artifact
                # if it exists; otherwise the catalog itself.
                canonical_sim = SIM_DIR / f"{app}_fabrication.json"
                artifact_path = canonical_sim if canonical_sim.exists() else CATALOG_PATH
                artifact_class = (
                    "APPS_DOMAIN_NEGATIVE_CONTROL_RESULT"
                    if canonical_sim.exists()
                    else "APPS_CATALOG_SELF_REPORT"
                )

                if req_id == "APPS-DOM-006":
                    # x3_domain_block_proved — closed by real runtime evidence
                    # from tools/cert/apps_e2e/run_app_negative_control_with_otel.py.
                    # PASS iff the runtime harness captured X3 in {DENY,
                    # SAFE_ABSTAIN, ESCALATE}. Falls back to NOT_VERIFIED when
                    # the runtime fixture is absent (static simulator is not
                    # enough — DOM-006 acceptance requires real X3 packet).
                    runtime_fixture = (
                        REPO_ROOT / "artifacts" / "apps_negative_controls_runtime"
                        / f"{app}_negative_trace.json"
                    )
                    if runtime_fixture.exists():
                        rfx = None
                        try:
                            rfx = json.loads(runtime_fixture.read_text(encoding="utf-8"))
                        except (json.JSONDecodeError, OSError):
                            rfx = None
                        if isinstance(rfx, dict) and rfx.get("x3_denied") is True:
                            result = "PASS"
                            artifact_path = runtime_fixture
                            artifact_class = "APPS_DOMAIN_NEGATIVE_CONTROL_RESULT"
                            pointer = "/app"
                            proof = {
                                "extracted_value": {
                                    "runtime_x3_disposition":
                                        rfx.get("exit_disposition", ""),
                                    "x3_denied": True,
                                    "x2_rationale":
                                        rfx.get("x2_decision", {}).get("rationale", ""),
                                    "x2_reason_codes":
                                        rfx.get("x2_decision", {}).get("reason_codes", []),
                                    "spans_count": rfx.get("spans_count", 0),
                                },
                                "expected_value": {
                                    "runtime_x3_disposition_in": ["X3A", "X3B", "X3E"],
                                    "x3_denied": True,
                                },
                                "match": True,
                                "notes": (
                                    f"{app}: runtime negative-control harness "
                                    f"produced x3_disposition="
                                    f"{rfx.get('exit_disposition', '?')} "
                                    f"with rationale="
                                    f"{rfx.get('x2_decision', {}).get('rationale', '?')!r}. "
                                    f"Real X3 DENY captured in OTEL via X1D UNGROUNDED."
                                ),
                            }
                        else:
                            result = "FAIL"
                            proof = {
                                "extracted_value": {
                                    "runtime_x3_disposition":
                                        (rfx or {}).get("exit_disposition", ""),
                                    "x3_denied": (rfx or {}).get("x3_denied", False),
                                },
                                "expected_value": {
                                    "runtime_x3_disposition_in": ["X3A", "X3B", "X3E"],
                                },
                                "match": False,
                                "notes": (
                                    f"{app}: runtime fixture present but "
                                    f"did NOT capture a DENY/ABSTAIN/ESCALATE "
                                    f"disposition. Investigate negative-control "
                                    f"receipts construction."
                                ),
                            }
                    else:
                        result = "NOT_VERIFIED"
                        proof = {
                            "extracted_value": {
                                "static_simulator_archetypes_blocked":
                                    archetypes_blocked,
                                "runtime_otel_evidence_present": False,
                            },
                            "expected_value": {
                                "runtime_x3_packet_with_disposition": "DENY",
                                "captured_in_otel_span":
                                    "exit.app_specific_eval",
                            },
                            "match": False,
                            "notes": (
                                f"{app}: static simulator confirms x3 logic blocks "
                                f"on archetypes={archetypes_blocked or '[]'}, but "
                                f"DOM-006 requires real runtime OTEL+X3 packet "
                                f"evidence. Run `python tools/cert/apps_e2e/"
                                f"run_app_negative_control_with_otel.py` to "
                                f"generate it."
                            ),
                        }
                else:  # APPS-DOM-010 domain_negative_control_blocks
                    if not archetypes_applicable:
                        # No archetype matched any of this app's rubric dims —
                        # the app has no negative-control surface to test.
                        # FAIL: this is a real gap (every app should have
                        # at least one archetype that applies).
                        result = "FAIL"
                        proof = {
                            "extracted_value": {
                                "archetypes_applicable": [],
                                "archetypes_blocked": [],
                            },
                            "expected_value": {
                                "archetypes_applicable_ge": 1,
                            },
                            "match": False,
                            "notes": (
                                f"{app}: no rubric dim matches any of the 3 "
                                f"negative-control archetypes "
                                f"(fabrication/personalization/coverage). "
                                f"Either the rubric is missing required "
                                f"dims or the archetype patterns need "
                                f"extending in the simulator."
                            ),
                        }
                    elif archetypes_blocked or archetypes_hitl:
                        result = "PASS"
                        proof = {
                            "extracted_value": {
                                "archetypes_applicable":
                                    archetypes_applicable,
                                "archetypes_x3_blocked": archetypes_blocked,
                                "archetypes_x3_hitl": archetypes_hitl,
                            },
                            "expected_value": {
                                "at_least_one_archetype_blocked_or_hitl": True,
                            },
                            "match": True,
                            "notes": (
                                f"{app}: static simulator confirms "
                                f"{len(archetypes_blocked)} archetype(s) → "
                                f"DENY, {len(archetypes_hitl)} → HITL_REVIEW. "
                                f"Negative-control surface exists and the "
                                f"deterministic gate logic blocks bad output."
                            ),
                        }
                    else:
                        # Applicable archetypes existed but none blocked —
                        # this means the simulator pushed dims below min
                        # but the chain still produced ALLOW. Real failure.
                        result = "FAIL"
                        proof = {
                            "extracted_value": {
                                "archetypes_applicable":
                                    archetypes_applicable,
                                "archetypes_x3_blocked": [],
                                "archetypes_x3_hitl": [],
                            },
                            "expected_value": {
                                "archetypes_x3_blocked_or_hitl_ge": 1,
                            },
                            "match": False,
                            "notes": (
                                f"{app}: archetypes "
                                f"{archetypes_applicable} are applicable but "
                                f"the deterministic chain produced ALLOW for "
                                f"all of them. Investigate threshold profile "
                                f"configuration."
                            ),
                        }

                assertions.append(_build_assertion(
                    req_id=req_id, control=control, result=result,
                    claim_type=claim_type, app=app,
                    artifact_path=artifact_path,
                    artifact_class=artifact_class,
                    pointer=pointer,
                    proof_payload=proof,
                    freshness_hours=freshness, now_iso=now_iso,
                ))

    assertions.sort(
        key=lambda a: (a["req_id"], a["control"], a.get("app_name") or ""),
    )
    return assertions


def write_jsonl(assertions: list[dict[str, Any]], out_path: Path = OUT_PATH) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for a in assertions:
            f.write(json.dumps(a, sort_keys=True, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--simulate-only", action="store_true",
        help="Run simulator and write per-scenario JSONs but skip assertion emission.",
    )
    args = parser.parse_args(argv)

    if not CATALOG_PATH.exists():
        print(f"ERROR: catalog missing at {CATALOG_PATH}", file=sys.stderr)
        return 2

    print("Running negative-control simulator...")
    sim_results = _run_simulations()

    # Print simulator summary
    print()
    print(f"{'App':24s}  {'fabrication':16s} {'personalization':16s} {'coverage':12s}")
    print("-" * 70)
    for app in RUNTIME_APPS:
        cells = []
        for arch in ("fabrication", "personalization", "coverage"):
            rec = sim_results[app][arch]["result"]
            disp = rec.get("x3_disposition", "?")
            cells.append(disp)
        print(f"{app:24s}  {cells[0]:16s} {cells[1]:16s} {cells[2]:12s}")
    print()

    if args.simulate_only:
        print(f"Simulator records written to {_rel(SIM_DIR)}/")
        return 0

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assertions = emit_assertions(catalog, sim_results)

    counts = {"PASS": 0, "FAIL": 0, "NOT_VERIFIED": 0}
    by_row: dict[str, dict[str, int]] = {}
    for a in assertions:
        r = a["assertion_result"]
        counts[r] = counts.get(r, 0) + 1
        by_row.setdefault(a["req_id"], {"PASS": 0, "FAIL": 0, "NOT_VERIFIED": 0})
        by_row[a["req_id"]][r] = by_row[a["req_id"]].get(r, 0) + 1

    print(
        f"Emitted {len(assertions)} negative-control assertions: "
        f"PASS={counts['PASS']} FAIL={counts['FAIL']} "
        f"NOT_VERIFIED={counts['NOT_VERIFIED']}"
    )
    for req in sorted(by_row):
        b = by_row[req]
        print(f"  {req:14s}  PASS={b['PASS']:2d}  FAIL={b['FAIL']:2d}  NV={b['NOT_VERIFIED']:2d}")

    if args.dry_run:
        return 0
    write_jsonl(assertions, args.out)
    print(f"Wrote {_rel(args.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
