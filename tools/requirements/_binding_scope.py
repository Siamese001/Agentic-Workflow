"""Shared binding scope for the 10C ledger proof-evidence pipeline.

This module is the SINGLE source of truth for two scope-sensitive artifacts:

  - ``CRITICAL_REQ_IDS`` — the canonical set of CRITICAL requirement IDs that
    are subject to the proof-evidence pipeline (5 W4d-4/W4d-5 pilot rows +
    24 Wave 1 CRITICAL rows = 29).
  - ``CRITICAL_BINDING_SCOPE`` — the pathspec tuple passed to
    ``git status --porcelain --`` to detect dirt in files that materially
    affect proof-bundle binding integrity (test sources, fixtures, the
    validator, the bundle emitter, the CI gate, the ledger CSV, the bundle
    directory, and the test generator).

Both are imported by:

  - ``tools/requirements/emit_proof_bundles.py``
  - ``tools/requirements/update_pilot_ledger.py``
  - ``ops_scripts/ci/check_10c_pilot_proof_evidence.py`` (CRITICAL_REQ_IDS only)

When extending this scope (adding Wave 2+ rows), append to BOTH tuples
deterministically and re-run ``emit_proof_bundles.py`` to refresh bundles.
"""

from __future__ import annotations

# Canonical set of CRITICAL requirement IDs covered by the proof-evidence
# pipeline. Order is meaningful for deterministic iteration in reports.
CRITICAL_REQ_IDS: tuple[str, ...] = (
    # --- W4d-4/W4d-5 pilot (5) ---
    "10C-REQ-049",  # U0 ingress invariant
    "10C-REQ-167",  # L5 policy plane
    "10C-REQ-086",  # PA.2 slot composition
    "10C-REQ-089",  # L2 sealed envelope
    "10C-REQ-122",  # UWG single-writer
    # --- Wave 1 (24) ---
    "10C-REQ-005",  # Ingest: ChunkSealedEnvelope metadata-bound-before-embedding
    "10C-REQ-064",  # L1: PlanContract no-execution
    "10C-REQ-074",  # L1: PlanContract output contract
    "10C-REQ-075",  # L0: RouteContract pre-routing gate
    "10C-REQ-099",  # Exit: X3DispositionPacket explicit dispositions
    "10C-REQ-103",  # L5: certification result chain
    "10C-REQ-116",  # L5: certification result
    "10C-REQ-119",  # L5: certification result
    "10C-REQ-140",  # UWG: CommitRequest write admission
    "10C-REQ-153",  # UWG: CommitRequest write admission
    "10C-REQ-160",  # L5: certification result
    "10C-REQ-163",  # Ingest: ChunkSealedEnvelope
    "10C-REQ-164",  # L2: ExecutionResult sealed
    "10C-REQ-165",  # OTEL: replay-key audit
    "10C-REQ-166",  # OTEL: replay-key audit
    "10C-REQ-175",  # L2: ExecutionResult sealed
    "10C-REQ-177",  # UWG: CommitRequest write admission
    "10C-REQ-182",  # L5: certification result
    "10C-REQ-185",  # UWG: CommitRequest write admission
    "10C-REQ-187",  # L5: certification result
    "10C-REQ-191",  # L6: shadow eval record
    "10C-REQ-192",  # L5: certification result
    "10C-REQ-195",  # L5: certification result
    "10C-REQ-199",  # L5: certification result
)


# Pathspec tuple for git-status scope check. Files OUTSIDE this scope can be
# dirty without invalidating the binding (per the W4d-5 binding policy).
CRITICAL_BINDING_SCOPE: tuple[str, ...] = (
    # --- Shared fixtures (all 5 pilot + 24 wave1 tests use these) ---
    "tests/fixtures/proof_evidence/",
    "tests/fixtures/__init__.py",
    # --- 5 pilot test files ---
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_049.py",
    "tests/unit/agentic_core/L1_cognition/intake/__init__.py",
    "tests/unit/agentic_core/L1_cognition/prompt_assembly/test_10c_req_086.py",
    "tests/unit/agentic_core/L1_cognition/prompt_assembly/__init__.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_089.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_122.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_167.py",
    # --- 24 Wave 1 test files ---
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_005.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_163.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/__init__.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/__init__.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_064.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_074.py",
    "tests/unit/agentic_core/L1_cognition/__init__.py",
    "tests/unit/agentic_core/L0_routing/test_10c_req_075.py",
    "tests/unit/agentic_core/L0_routing/__init__.py",
    "tests/unit/agentic_core/L5_safety/exit_control/test_10c_req_099.py",
    "tests/unit/agentic_core/L5_safety/exit_control/__init__.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_103.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_116.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_119.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_160.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_182.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_187.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_192.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_195.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_199.py",
    "tests/unit/agentic_core/L5_safety/__init__.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_140.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_153.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_177.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_185.py",
    "tests/unit/agentic_core/L4_state/__init__.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_164.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_175.py",
    "tests/unit/agentic_core/L2_execution/__init__.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_165.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_166.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_191.py",
    "tests/unit/agentic_core/L6_observability/__init__.py",
    "tests/unit/agentic_core/__init__.py",
    # --- Tooling (proof-binding pipeline) ---
    "tools/requirements/emit_proof_bundles.py",
    "tools/requirements/validate_10c_proof_ledger.py",
    "tools/requirements/update_pilot_ledger.py",
    "tools/requirements/generate_wave1_tests.py",
    "tools/requirements/_binding_scope.py",
    "ops_scripts/ci/check_10c_pilot_proof_evidence.py",
    # --- Writeback target (expected-dirty during binding) ---
    "docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv",
    "artifacts/requirements/proof_bundles/",
)
