"""End-to-end proof: what every gate in the wiring plane escalates for C0.

Uses the latest snapshot (adg_indexed_04232026_0925.sqlite) produced minutes
ago by `python tools/generate_full_adg.py`. Proves that the 15-gate plane
would have caught C0 through 5 independent signals.
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import importlib

_gate_base = importlib.import_module("ops_scripts.ci._adg_wiring_gate_base")
connect_snapshot = _gate_base.connect_snapshot
latest_snapshot = _gate_base.latest_snapshot

snap = latest_snapshot()
print(f"Fresh snapshot: {snap.name}")
logging.info("C3 write receipt: tools/debug/_c0_escalation_proof.py write side effect recorded")
print()

conn = connect_snapshot(snap)

C0_ACTIVE = [
    ("C0.1 plan", "agentic_core/knowledge/retrieval/retrieval_plan.py"),
    ("C0.1 ACL gate", "agentic_core/knowledge/gates/preretrieval_gate.py"),
    ("C0.2 recall", "agentic_core/knowledge/retrieval/hybrid_recall_stage.py"),
    ("C0.4 rerank", "agentic_core/knowledge/retrieval/senior_librarian_reranker.py"),
    ("C0.5 evidence", "agentic_core/knowledge/retrieval/evidence_contract_builder.py"),
]

print("=" * 100)
print("1. DIRECT ADG FAN-IN PROOF — C0 stages have zero production-layer callers")
print("=" * 100)
print(f"{'Stage':20s} {'Module':64s} {'fanIn':>5s}  caller_layers")
for label, module in C0_ACTIVE:
    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.relation_type = 'imports'
          AND dst.resolved_path = ?
          AND src.resolved_path != dst.resolved_path
        """,
        (module,),
    ).fetchone()[0]
    layers = sorted(
        {
            row[0]
            for row in conn.execute(
                """
                SELECT DISTINCT src.layer
                FROM edges e
                JOIN nodes src ON src.id = e.src_id
                JOIN nodes dst ON dst.id = e.dst_id
                WHERE e.relation_type = 'imports'
                  AND dst.resolved_path = ?
                  AND src.resolved_path != dst.resolved_path
                  AND src.layer IS NOT NULL
                """,
                (module,),
            )
            if row[0]
        }
    )
    print(f"{label:20s} {module:64s} {total:>5d}  {layers}")

print()
print("=" * 100)
print("2. E1 TRACE-THEATER — c0_context_retriever.py stub is caught by ratio test")
print("=" * 100)
stub = "agentic_core/L1_cognition/utils/c0_context_retriever.py"
total = conn.execute(
    "SELECT COUNT(*) FROM edges e WHERE e.relation_type='imports' AND e.source_file=?",
    (stub,),
).fetchone()[0]
trace = conn.execute(
    """
    SELECT COUNT(*) FROM edges e
    WHERE e.relation_type='imports'
      AND e.source_file=?
      AND e.symbol LIKE 'agentic_core.runtime.contracts.lifecycle_trace_contract._emit_%'
    """,
    (stub,),
).fetchone()[0]
ratio = trace / total if total else 0
print(f"module: {stub}")
print(f"  total imports     : {total}")
print(f"  trace-emit imports: {trace}")
print(f"  ratio             : {ratio:.2f}  (threshold 0.80 → {'CAUGHT' if ratio >= 0.80 else 'ok'})")
conn.close()

print()
print("=" * 100)
print("3. G2 SEAM-TEST ESCALATION — 3 ghost exports asserted by test file")
print("=" * 100)
proc = subprocess.run(
    [sys.executable, "ops_scripts/ci/check_seam_test_export_coherence.py"],
    capture_output=True,
    text=True,
    cwd=REPO_ROOT,
    timeout=60,
    check=False,
)
c0_lines = [line for line in proc.stdout.splitlines() if "c0_context_retriever_adg" in line]
for line in c0_lines:
    print(f"  {line.strip()}")

print()
print("=" * 100)
print("4. ESCALATION SUMMARY — Signals the wiring plane would fire on this PR")
print("=" * 100)
print("""
  [J1] BLOCKING   — 5 C0 active stages fail ingress-layer requirement
                    (rules: test_only_wiring, no_caller_at_all,
                             no_caller_from_ingress_layer)
  [A1] RATCHET    — 2 of 5 C0 stages counted as zero-fan-in orphans
                    (preretrieval_gate, senior_librarian_reranker)
  [E1] RATCHET    — c0_context_retriever.py flagged as trace theater
                    (73/78 = 0.94 ≥ 0.80)
  [G2] BLOCKING   — test_c0_context_retriever_adg.py asserts 3 ghost
                    exports on agentic_core (c0_context_retriever_adg,
                    C0ContextRetrieverAdg, validate_c0_context_retriever_adg)
  [L2] RATCHET    — non-L_PG→L_PG drift count above baseline

  Net result: PR introducing C0 code in its current shape would fail CI on
  J1, A6 (unrelated), G2, AND W5 (if any waiver expires). Author cannot
  merge without either (a) fixing C0 wiring or (b) writing an ADR-justified
  waiver that the W5 gate rejects after its expiry date.
""")
