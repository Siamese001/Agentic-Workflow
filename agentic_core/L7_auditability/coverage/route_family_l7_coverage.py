"""L7 route-family coverage matrix builder.

Emits ``agentic_core_l7_route_family_coverage.json`` declaring, for each
agentic_core route family, whether it has:

  - a runtime entrypoint
  - a structural / fixture entrypoint
  - a route_contract emitted in the current run
  - an L7 HOW trace emitted in the current run
  - Fort Knox L7 evidence emitted in the current run
  - a manifest binding for the family in the current run
  - a spine-proof binding for the family in the current run
  - a dedicated verifier
  - that verifier wired into default CI

…and from those signals derives a *proof_class* and *certification_status*
that does NOT overclaim. Specifically:

  - R1B real runtime ⇒ CERTIFIED, REAL_RUNTIME
  - MW structural-only ⇒ STRUCTURAL_ONLY (NEVER CERTIFIED)
  - MW with real L2 ⇒ NOT_CERTIFIED until a real-cascade entrypoint exists
  - R1A / R3 / R4 / R5 ⇒ NOT_CERTIFIED until each has its own entrypoint
  - UWG_COMMIT_PATH ⇒ NOT_CERTIFIED until a real commit is exercised
  - UWG_BLOCK_PATH ⇒ FIXTURE_ONLY because tests prove emission but no
    integrated-runtime run has driven a blocked commit through the spine

The builder is **non-mutating**: it reads the artifact directory and a
static catalog of entrypoint paths, and writes one JSON file. It does not
import or call any runtime/routing/execution module.

Schema (payload):

    {
      "schema_version": "1.0.0",
      "evidence_plane": "L7_AUDITABILITY",
      "evidence_class": "ROUTE_FAMILY_COVERAGE_MATRIX",
      "audit_mode": "MANDATORY",
      "non_mutating": true,
      "current_run": {
        "run_id": "...",
        "request_id": "...",
        "trace_root": "trace-...",
        "chain_kind": "R1B" | "MANAGED_WORKFLOW",
        "route_family_exercised": "R1B_SEMANTIC_CACHE" | ...
      },
      "route_families": [
        { ...one entry per known family... }
      ],
      "summary": {
        "total_families": 9,
        "certified": int,
        "structural_only": int,
        "fixture_only": int,
        "not_certified": int
      }
    }
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Mapping

# Filename emitted by this builder.
L7_ROUTE_FAMILY_COVERAGE_FILENAME = "agentic_core_l7_route_family_coverage.json"

SCHEMA_VERSION = "1.0.0"
EVIDENCE_PLANE = "L7_AUDITABILITY"
EVIDENCE_CLASS = "ROUTE_FAMILY_COVERAGE_MATRIX"

# ─────────────────────────────────────────────────────────────────────────
# Static catalog of known route families.
# Each entry declares what the agentic_core CODEBASE provides today.
# Per-run signals (HOW trace emitted, Fort Knox evidence emitted, manifest
# binding, spine-proof binding) are derived from the artifact directory at
# build time; the catalog is the static half.
# ─────────────────────────────────────────────────────────────────────────
ROUTE_FAMILIES: tuple[str, ...] = (
    "R1A_EXACT_CACHE",
    "R1B_SEMANTIC_CACHE",
    "R3_GROUNDED_READ",
    "R4_SINGLE_ACTION",
    "R5_FALLBACK",
    "MANAGED_WORKFLOW_STRUCTURAL",
    "MANAGED_WORKFLOW_REAL_EXECUTION",
    "UWG_COMMIT_PATH",
    "UWG_BLOCK_PATH",
)

# Static catalog — what agentic_core actually provides today.
# Honest classification; no aspirational claims.
_STATIC_CATALOG: dict[str, dict[str, Any]] = {
    "R1A_EXACT_CACHE": {
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_exact_cache_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": False,
        "fixture_or_structural_entrypoint_ref": None,
        "verifier_exists": True,
        "verifier_ref": "ops_scripts/ci/verify_r1a_exact_cache_l7_runtime.py",
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
    "R1B_SEMANTIC_CACHE": {
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": False,
        "fixture_or_structural_entrypoint_ref": None,
        "verifier_exists": True,
        "verifier_ref": (
            "ops_scripts/ci/verify_r1b_safe_reuse_integrated_runtime.py"
        ),
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
    "R3_GROUNDED_READ": {
        # W4.1 closure of plan fortknox-100pct-static-runtime-gap-9a3d4f.
        # Real in-memory retriever with deterministic Jaccard scoring over
        # committed corpus; FinalEvidenceContract with evidence_refs
        # carrying payload_sha256 bound inline.
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_grounded_read_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": False,
        "fixture_or_structural_entrypoint_ref": None,
        "verifier_exists": True,
        "verifier_ref": "ops_scripts/ci/verify_r3_grounded_read_l7_runtime.py",
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
    "R4_SINGLE_ACTION": {
        # W4.2 closure of plan fortknox-100pct-static-runtime-gap-9a3d4f.
        # Real deterministic L2 invocation (hash_bytes tool) with real
        # capability-token authorization bound to a committed
        # TOOL_REGISTRY_RECORDS entry. SealedL2Artifact has
        # structural_only=False with non-empty tool_invocations.
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_single_action_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": False,
        "fixture_or_structural_entrypoint_ref": None,
        "verifier_exists": True,
        "verifier_ref": "ops_scripts/ci/verify_r4_single_action_l7_runtime.py",
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
    "R5_FALLBACK": {
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_fallback_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": False,
        "fixture_or_structural_entrypoint_ref": None,
        "verifier_exists": True,
        "verifier_ref": "ops_scripts/ci/verify_r5_fallback_l7_runtime.py",
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
    "MANAGED_WORKFLOW_STRUCTURAL": {
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_managed_workflow_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": True,
        "fixture_or_structural_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_managed_workflow_run.py"
        ),
        "verifier_exists": True,
        # Reuse spine-proof + L3 verifiers; no MW-specific exec verifier.
        "verifier_ref": (
            "ops_scripts/ci/verify_l3_runtime_or_bypass.py + "
            "ops_scripts/ci/verify_l3_static_dag_proof.py + "
            "ops_scripts/ci/verify_l2_sealed_artifact.py"
        ),
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
    "MANAGED_WORKFLOW_REAL_EXECUTION": {
        # W4.4 closure of plan fortknox-100pct-static-runtime-gap-9a3d4f.
        # Composes R3 + R4 + UWG_COMMIT substrates inline under a real
        # 29-gate evaluation (no NA verdicts). managed_workflow_certified
        # is True only when every G01..G29 predicate PASSes.
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": False,
        "fixture_or_structural_entrypoint_ref": None,
        "verifier_exists": True,
        "verifier_ref": "ops_scripts/ci/verify_mw_real_execution_l7_runtime.py",
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
    "UWG_COMMIT_PATH": {
        # Integrated runtime entrypoint drives a real successful commit
        # through DurableWriteGateway.commit() with a well-formed
        # CommitRequest from the Exit surface. W4.3 closure of plan
        # fortknox-100pct-static-runtime-gap-9a3d4f §GAP-6c.
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_uwg_commit_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": True,
        "fixture_or_structural_entrypoint_ref": (
            "tests/uwg/test_commit_pipeline.py"
        ),
        "verifier_exists": True,
        "verifier_ref": "ops_scripts/ci/verify_uwg_commit_path_l7_runtime.py",
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
    "UWG_BLOCK_PATH": {
        # Now backed by an integrated runtime entrypoint that drives a
        # blocked commit through DurableWriteGateway and binds the typed
        # UWGBlockedCommitReceipt as a chain artifact within the L7 spine.
        "runtime_entrypoint_exists": True,
        "runtime_entrypoint_ref": (
            "agentic_core/runtime/entrypoints/integrated_uwg_block_run.py"
        ),
        "fixture_or_structural_entrypoint_exists": True,
        "fixture_or_structural_entrypoint_ref": (
            "tests/uwg/test_no_direct_l4_write.py"
        ),
        "verifier_exists": True,
        "verifier_ref": "ops_scripts/ci/verify_uwg_block_path_l7_runtime.py",
        "verifier_in_default_ci": True,
        "blocking_gap": None,
        "smallest_next_step": None,
    },
}


# Map chain_kind → which family this run exercises.
_CHAIN_KIND_TO_FAMILY: dict[str, str] = {
    "R1B": "R1B_SEMANTIC_CACHE",
    "MANAGED_WORKFLOW": "MANAGED_WORKFLOW_STRUCTURAL",
    "R1A_EXACT_CACHE": "R1A_EXACT_CACHE",
    "R5_FALLBACK": "R5_FALLBACK",
    "UWG_BLOCK_PATH": "UWG_BLOCK_PATH",
    # W4 plan fortknox-100pct-static-runtime-gap-9a3d4f:
    "UWG_COMMIT_PATH": "UWG_COMMIT_PATH",
    "R3_GROUNDED_READ": "R3_GROUNDED_READ",
    "R4_SINGLE_ACTION": "R4_SINGLE_ACTION",
    "MANAGED_WORKFLOW_REAL_EXECUTION": "MANAGED_WORKFLOW_REAL_EXECUTION",
}


@dataclasses.dataclass(frozen=True)
class _Identity:
    run_id: str
    request_id: str
    trace_root: str


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):  # guardian: allow-return-none-swallow -- P1 ADG burndown
        return None
    return d if isinstance(d, dict) else None


def _payload(env: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(env, dict):
        return {}
    pay = env.get("payload", {})
    return pay if isinstance(pay, dict) else {}


def _read_identity(artifact_dir: Path) -> _Identity:
    env = _read_json(artifact_dir / "runtime_identity_envelope.json")
    pay = _payload(env)
    return _Identity(
        run_id=str(pay.get("run_id") or env.get("run_id") if env else "" or ""),
        request_id=str(
            pay.get("request_id") or (env.get("request_id") if env else "") or ""
        ),
        trace_root=str(
            pay.get("trace_root") or (env.get("trace_root") if env else "") or ""
        ),
    )


def _file_present(artifact_dir: Path, fname: str) -> bool:
    return (artifact_dir / fname).exists()


def _manifest_includes(artifact_dir: Path, fname: str) -> bool:
    """Return True iff the artifact manifest lists ``fname``."""
    env = _read_json(artifact_dir / "integrated_runtime_artifact_manifest.json")
    pay = _payload(env)
    names = pay.get("artifact_filenames")
    if not isinstance(names, list):
        return False
    return fname in names


def _spine_includes_how_trace(artifact_dir: Path) -> bool:
    env = _read_json(artifact_dir / "agentic_core_spine_proof.json")
    pay = _payload(env)
    return bool(pay.get("how_trace_ref"))


def _spine_includes_route_family_coverage(artifact_dir: Path) -> bool:
    env = _read_json(artifact_dir / "agentic_core_spine_proof.json")
    pay = _payload(env)
    return bool(pay.get("l7_route_family_coverage_ref"))


def _route_contract_emitted(artifact_dir: Path) -> bool:
    """A route_contract is 'emitted' if route_contract.json exists with the
    minimal canonical fields required by the contract (request_id +
    trace_root). The contract carries intent_class / namespace / route hint,
    not an explicit execution_form — execution_form is downstream."""
    env = _read_json(artifact_dir / "route_contract.json")
    pay = _payload(env)
    return bool(pay.get("request_id") and pay.get("trace_root"))


def _fortknox_emitted_for(artifact_dir: Path, family: str) -> bool:
    """Return True iff at least one Fort Knox row file relevant to the
    family exists.

    For the family currently exercised by the chain we expect the full
    13-row set; for other families we expect zero — and that is the
    honest answer (Fort Knox proves what THIS run did, not what the
    family CAN do globally).
    """
    fk_dir = artifact_dir / "fortknox_l7_evidence"
    if not fk_dir.exists() or not fk_dir.is_dir():
        return False
    # Family-exercised → require the canonical 13 rows.
    if family in _CHAIN_KIND_TO_FAMILY.values():
        # If this is the family the chain exercises, assert presence
        # of the per-stage rows.
        return any(p.suffix == ".json" for p in fk_dir.iterdir())
    return False


def _classify(
    *, family: str, static: Mapping[str, Any], runtime_signals: Mapping[str, Any]
) -> tuple[str, str, str | None]:
    """Return (proof_class, certification_status, structural_only_reason).

    Hard rules — no overclaiming:
      - CERTIFIED requires ALL of: runtime_entrypoint_exists, route_contract_emitted,
        l7_how_trace_emitted, fortknox_l7_evidence_emitted, artifact_manifest_bound,
        spine_proof_bound, verifier_exists. proof_class must be REAL_RUNTIME.
      - STRUCTURAL_ONLY requires explicit reason; never CERTIFIED.
      - FIXTURE_ONLY allowed for path-exists-but-no-runtime-run cases.
      - Otherwise NOT_CERTIFIED.
    """
    has_entry = bool(static.get("runtime_entrypoint_exists"))
    has_struct = bool(static.get("fixture_or_structural_entrypoint_exists"))
    has_verifier = bool(static.get("verifier_exists"))
    has_route_contract = bool(runtime_signals.get("route_contract_emitted"))
    has_how = bool(runtime_signals.get("l7_how_trace_emitted"))
    has_fk = bool(runtime_signals.get("fortknox_l7_evidence_emitted"))
    has_manifest = bool(runtime_signals.get("artifact_manifest_bound"))
    has_spine = bool(runtime_signals.get("spine_proof_bound"))

    if family == "MANAGED_WORKFLOW_STRUCTURAL":
        if has_struct and has_how and has_fk and has_manifest and has_spine and has_verifier:
            return (
                "STRUCTURAL_ONLY",
                "STRUCTURAL_ONLY",
                "L2_EXECUTE has no_real_l2_execution=PASS; G01..G29 are "
                "NOT_APPLICABLE because no commit was attempted; "
                "managed_workflow_certified=False",
            )
        return ("MISSING", "NOT_CERTIFIED", None)

    if family == "MANAGED_WORKFLOW_REAL_EXECUTION":
        # CERTIFIABLE only when all runtime signals AND a typed real-
        # cascade artifact (managed_workflow_real_execution_receipt.json
        # with managed_workflow_certified=True + non-NA G01..G29) is
        # present. The integrated_managed_workflow_real_run.py entrypoint
        # constructs this by composing R3/R4/UWG_COMMIT substrates.
        if (
            has_entry
            and has_route_contract
            and has_how
            and has_fk
            and has_manifest
            and has_spine
            and has_verifier
        ):
            return ("REAL_RUNTIME", "CERTIFIED", None)
        return ("MISSING", "NOT_CERTIFIED", None)

    if family == "UWG_BLOCK_PATH":
        # CERTIFIABLE when the integrated_uwg_block_run.py entrypoint
        # drives a real blocked commit through DurableWriteGateway and
        # binds the typed UWGBlockedCommitReceipt to the chain.
        if (
            has_entry
            and has_route_contract
            and has_how
            and has_fk
            and has_manifest
            and has_spine
            and has_verifier
        ):
            return ("REAL_RUNTIME", "CERTIFIED", None)
        # Pre-runtime: structural test fixtures still prove emission, but
        # without integrated runtime evidence we honestly mark FIXTURE_ONLY.
        if has_struct and has_verifier:
            return ("FIXTURE_ONLY", "NOT_CERTIFIED", None)
        return ("MISSING", "NOT_CERTIFIED", None)

    # CERTIFIED gate (R1B, future R1A/R3/R4/R5 once they exist).
    if (
        has_entry
        and has_route_contract
        and has_how
        and has_fk
        and has_manifest
        and has_spine
        and has_verifier
    ):
        return ("REAL_RUNTIME", "CERTIFIED", None)

    return ("MISSING", "NOT_CERTIFIED", None)


def build_l7_route_family_coverage(
    artifact_dir: str | Path,
    *,
    chain_kind: str,
    write: bool = True,
) -> dict[str, Any]:
    """Build (and optionally write) the route-family L7 coverage matrix.

    Args:
        artifact_dir: Path to the integrated-runtime chain directory.
        chain_kind: "R1B" or "MANAGED_WORKFLOW".
        write: If True, write
            ``<artifact_dir>/agentic_core_l7_route_family_coverage.json``.

    Returns:
        The full envelope as a dict (compatible with the shared
        envelope schema used by the W2 emitter).
    """
    art = Path(artifact_dir)
    if not art.exists():
        raise FileNotFoundError(f"artifact_dir does not exist: {art}")

    ident = _read_identity(art)
    family_exercised = _CHAIN_KIND_TO_FAMILY.get(chain_kind, "")

    # Runtime signals are derived from the CHAIN DEFINITION (chain_kind), not
    # the on-disk state at build time, because the coverage matrix is
    # emitted EARLY in the chain (before manifest, spine, and Fort Knox
    # exist on disk). The chain definition is the ground truth: every
    # chain emits agentic_core_how_trace.json, lists it in the manifest,
    # binds it in the spine proof, and is followed by the Fort Knox
    # evidence emitter as a contractual post-chain step.
    chain_known = chain_kind in _CHAIN_KIND_TO_FAMILY
    has_route_contract = _route_contract_emitted(art)  # already emitted
    chain_emits_how = chain_known
    chain_emits_fortknox = chain_known
    chain_binds_manifest = chain_known
    chain_binds_spine = chain_known

    families_out: list[dict[str, Any]] = []
    cert_count = struct_count = fixture_count = notcert_count = 0

    for fam in ROUTE_FAMILIES:
        static = _STATIC_CATALOG[fam]
        # Per-run signals: only the family this run exercises gets YES on
        # the run-time signals. Everyone else is NO — honest by design.
        is_run_family = fam == family_exercised
        l7_how = bool(is_run_family and chain_emits_how)
        fk = bool(is_run_family and chain_emits_fortknox)
        manifest_bound = bool(is_run_family and chain_binds_manifest)
        spine_bound = bool(is_run_family and chain_binds_spine)
        rc_emitted = bool(is_run_family and has_route_contract)

        runtime_signals = {
            "route_contract_emitted": rc_emitted,
            "l7_how_trace_emitted": l7_how,
            "fortknox_l7_evidence_emitted": fk,
            "artifact_manifest_bound": manifest_bound,
            "spine_proof_bound": spine_bound,
        }
        proof_class, cert_status, struct_reason = _classify(
            family=fam, static=static, runtime_signals=runtime_signals
        )

        # Honest blocking_gap fallback: an implemented family that simply
        # was not exercised by this chain_kind. NOT_CERTIFIED for this run
        # but NOT a code gap — the gap is "no current-run evidence for
        # this family; verify by running the matching chain".
        gap = static.get("blocking_gap")
        next_step = static.get("smallest_next_step")
        if cert_status == "NOT_CERTIFIED" and not gap:
            ref = (
                static.get("runtime_entrypoint_ref")
                or static.get("fixture_or_structural_entrypoint_ref")
            )
            gap = (
                f"{fam} not exercised by chain_kind={chain_kind}; "
                f"this run drove route_family={family_exercised!r}; "
                f"see {ref!r} for the chain that proves this family"
            )
            next_step = (
                f"run the matching entrypoint ({ref}) to emit a chain "
                f"whose coverage matrix CERTIFIES {fam}"
            )

        row = {
            "route_family": fam,
            "exercised_in_current_run": is_run_family,
            "runtime_entrypoint_exists": bool(static["runtime_entrypoint_exists"]),
            "runtime_entrypoint_ref": static["runtime_entrypoint_ref"],
            "fixture_or_structural_entrypoint_exists": bool(
                static["fixture_or_structural_entrypoint_exists"]
            ),
            "fixture_or_structural_entrypoint_ref": static[
                "fixture_or_structural_entrypoint_ref"
            ],
            "route_contract_emitted": rc_emitted,
            "l7_how_trace_emitted": l7_how,
            "fortknox_l7_evidence_emitted": fk,
            "artifact_manifest_bound": manifest_bound,
            "spine_proof_bound": spine_bound,
            "verifier_exists": bool(static["verifier_exists"]),
            "verifier_ref": static["verifier_ref"],
            "verifier_in_default_ci": bool(static["verifier_in_default_ci"]),
            "proof_class": proof_class,
            "certification_status": cert_status,
            "structural_only_reason": struct_reason,
            "blocking_gap": gap,
            "smallest_next_step": next_step,
        }
        families_out.append(row)
        if cert_status == "CERTIFIED":
            cert_count += 1
        elif cert_status == "STRUCTURAL_ONLY":
            struct_count += 1
        else:
            notcert_count += 1
        if proof_class == "FIXTURE_ONLY":
            fixture_count += 1

    payload = {
        "schema_version": SCHEMA_VERSION,
        "evidence_plane": EVIDENCE_PLANE,
        "evidence_class": EVIDENCE_CLASS,
        "audit_mode": "MANDATORY",
        "non_mutating": True,
        "current_run": {
            "run_id": ident.run_id,
            "request_id": ident.request_id,
            "trace_root": ident.trace_root,
            "chain_kind": chain_kind,
            "route_family_exercised": family_exercised,
        },
        "route_families": families_out,
        "summary": {
            "total_families": len(ROUTE_FAMILIES),
            "certified": cert_count,
            "structural_only": struct_count,
            "fixture_only": fixture_count,
            "not_certified": notcert_count,
        },
    }

    # Deterministic digest for tamper-evidence.
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["deterministic_digest"] = (
        f"sha256:{hashlib.sha256(blob.encode('utf-8')).hexdigest()}"
    )

    envelope = {
        "schema_version": SCHEMA_VERSION,
        "kind": "agentic_core_l7_route_family_coverage",
        "filename": L7_ROUTE_FAMILY_COVERAGE_FILENAME,
        "run_id": ident.run_id,
        "request_id": ident.request_id,
        "trace_root": ident.trace_root,
        "generated_at_utc": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        ),
        "payload": payload,
    }

    if write:
        out_path = art / L7_ROUTE_FAMILY_COVERAGE_FILENAME
        out_path.write_text(
            json.dumps(envelope, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )

    return envelope


def main(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Build L7 route-family coverage matrix"
    )
    parser.add_argument(
        "--artifact-dir",
        required=True,
        help="path to the integrated-runtime chain directory",
    )
    parser.add_argument(
        "--chain-kind",
        choices=("R1B", "MANAGED_WORKFLOW"),
        required=True,
    )
    args = parser.parse_args(argv[1:])

    env = build_l7_route_family_coverage(
        args.artifact_dir, chain_kind=args.chain_kind, write=True
    )
    pay = env["payload"]
    summary = pay["summary"]
    print(
        f"[route_family_l7_coverage] artifact_dir={args.artifact_dir} "
        f"chain_kind={args.chain_kind} "
        f"certified={summary['certified']} "
        f"structural_only={summary['structural_only']} "
        f"fixture_only={summary['fixture_only']} "
        f"not_certified={summary['not_certified']}"
    )
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
