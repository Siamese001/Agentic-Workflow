#!/usr/bin/env python3
"""ADG CI Gate — enforces §ADG-1 repair discipline.

Blocks full-suite pytest runs during PHASE 5-6 (before cluster convergence).
Run as a pre-commit hook or CI step.

Usage:
    python tools/adg_ci_gate.py check-phase          # verify current phase is valid for full suite
    python tools/adg_ci_gate.py cluster-status        # show unresolved clusters
    python tools/adg_ci_gate.py scoped-tests <module> # emit scoped test IDs for a root module
    python tools/adg_ci_gate.py litmus <cluster_id>   # run 4-question litmus check

Exit codes:
    0 = gate passes (allowed to proceed)
    1 = gate blocks (forbidden action detected)
    2 = ADG artifacts missing (rebuild required)
"""

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CLUSTERS_FILE = REPO_ROOT / "artifacts" / "adg_failure_clusters.json"
SURFACE_MAP_FILE = REPO_ROOT / "artifacts" / "adg_test_surface_map.json"
GRAPH_FILE = REPO_ROOT / "artifacts" / "adg_semantic_graph.json"
PHASE_FILE = REPO_ROOT / "artifacts" / "adg_current_phase.json"


def _artifact_error(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(2)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        _artifact_error(
            f"[ADG-GATE] MISSING ARTIFACT: {path}\n"
            "[ADG-GATE] Run: python tools/adg_semantic_builder.py --rebuild"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _artifact_error(f"[ADG-GATE] INVALID ARTIFACT: {path} ({exc})")
    if not isinstance(payload, dict):
        _artifact_error(f"[ADG-GATE] INVALID ARTIFACT SHAPE: {path} must contain a JSON object")
    return payload


def _coerce_phase(raw: Any) -> int:
    try:
        phase = int(raw)
    except (TypeError, ValueError) as exc:
        _artifact_error(f"[ADG-GATE] INVALID PHASE VALUE: {raw!r} ({exc})")
    if phase < 1:
        _artifact_error(f"[ADG-GATE] INVALID PHASE VALUE: {phase} (must be >= 1)")
    return phase


def cmd_check_phase() -> int:
    """Verify current phase allows full-suite run."""
    phase_data: dict[str, Any] = {}
    if PHASE_FILE.exists():
        phase_data = _load_json(PHASE_FILE)

    phase = _coerce_phase(phase_data.get("phase", 5))
    if phase < 7:
        print(f"[ADG-GATE] BLOCKED: Full-suite pytest is FORBIDDEN in PHASE {phase}.", file=sys.stderr)
        print(
            "[ADG-GATE] Reason: §ADG-1.2 — full suite only allowed in PHASE 7 after all clusters converge.",
            file=sys.stderr,
        )
        print(
            "[ADG-GATE] Action: Run scoped tests per cluster. Use /adg-repair-loop workflow.", file=sys.stderr
        )
        clusters = _load_json(CLUSTERS_FILE)
        top = clusters.get("top_clusters", [])
        unresolved = [c for c in top if not c.get("resolved", False)]
        print(f"[ADG-GATE] Unresolved clusters: {len(unresolved)}", file=sys.stderr)
        for c in unresolved[:5]:
            print(
                f"  - {c.get('module', c.get('root_module', '?'))} (risk={c.get('risk_score', 0)}, tests={c.get('test_surface_size', len(c.get('covering_tests', [])))})",
                file=sys.stderr,
            )
        return 1

    print(f"[ADG-GATE] PHASE {phase} — full-suite run is ALLOWED.", file=sys.stdout)
    return 0


def cmd_cluster_status() -> int:
    """Show unresolved ADG clusters and their scoped test surfaces."""
    clusters = _load_json(CLUSTERS_FILE)
    top = clusters.get("top_clusters", [])
    unresolved = [c for c in top if not c.get("resolved", False)]

    print("\n=== ADG CLUSTER STATUS ===")
    print(f"Total clusters: {len(top)}")
    print(f"Unresolved:     {len(unresolved)}")
    print()

    if not unresolved:
        print("ALL CLUSTERS GREEN — proceed to PHASE 7 full-suite validation.")
        return 0

    print("Unresolved clusters (highest priority first):")
    for i, c in enumerate(unresolved[:10]):
        root = c.get("module", c.get("root_module", "?"))
        risk = c.get("risk_score", 0)
        tests = c.get("covering_tests", [])
        surface = c.get("test_surface_size", len(tests))
        print(f"  [{i}] {root}")
        print(f"      risk={risk}  scoped_tests={surface}")
        if tests:
            print(f"      example: {tests[0]}")
    return 1


def cmd_scoped_tests(root_module: str) -> int:
    """Emit scoped test IDs covering a given root module."""
    surface = _load_json(SURFACE_MAP_FILE)
    key = f"module:{root_module}"
    tests = surface.get("symbol_to_tests", {}).get(key, [])

    if not tests:
        # Also check by module path directly
        tests = surface.get("module_to_tests", {}).get(root_module, [])

    if not tests:
        print(f"[ADG-GATE] No scoped tests found for: {root_module}", file=sys.stderr)
        print("[ADG-GATE] Tip: Check adg_test_surface_map.json for exact module key.", file=sys.stderr)
        return 1

    test_files = sorted(set(t.split("::")[0] for t in tests))
    print(f"\n=== SCOPED TESTS FOR: {root_module} ===")
    print(f"Total test IDs: {len(tests)}")
    print(f"Test files:     {len(test_files)}")
    print()
    print("pytest command:")
    print(f"  python -m pytest {' '.join(test_files[:20])} --tb=short -q --no-header")
    return 0


def cmd_litmus(cluster_id: str) -> int:
    """Run 4-question litmus gate for a cluster ID (root module path)."""
    clusters = _load_json(CLUSTERS_FILE)
    surface = _load_json(SURFACE_MAP_FILE)

    top = clusters.get("top_clusters", [])
    cluster = next((c for c in top if cluster_id in c.get("module", c.get("root_module", ""))), None)

    if not cluster:
        print(f"[ADG-GATE] Cluster not found: {cluster_id}", file=sys.stderr)
        return 1

    root_module = cluster.get("module", cluster.get("root_module", "?"))
    tests = cluster.get("covering_tests", [])
    risk = cluster.get("risk_score", 0)

    print(f"\n=== ADG 4-QUESTION LITMUS: {root_module} ===")
    print()
    print("Q1. Which ADG cluster?")
    print(f"    → {root_module}  (risk={risk})")
    print()
    print("Q2. Root definition node?")
    print(f"    → {root_module}")
    print("    → Check: does the failing symbol originate HERE (not a call site)?")
    print()
    print("Q3. Scoped tests?")
    test_files = sorted(set(t.split("::")[0] for t in tests))
    if test_files:
        for tf in test_files[:5]:
            print(f"    → {tf}")
        if len(test_files) > 5:
            print(f"    → ... and {len(test_files) - 5} more")
    else:
        print("    → WARNING: No scoped tests found in ADG surface map")
    print()
    print("Q4. Blast radius justification?")
    print("    → Trace import edges in artifacts/adg_semantic_graph.json")
    print(f"    → Find: failing_test → IMPORT_EDGE → {root_module}")
    print()
    print("Scoped test command:")
    print(f"  python -m pytest {' '.join(test_files[:10])} --tb=short -q")
    return 0


def cmd_advance_phase(phase: int) -> int:
    """Record current phase to artifacts/adg_current_phase.json."""
    phase = _coerce_phase(phase)
    PHASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PHASE_FILE.write_text(json.dumps({"phase": phase}, indent=2), encoding="utf-8")
    print(f"[ADG-GATE] Phase set to {phase}.")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    cmd = sys.argv[1]

    if cmd == "check-phase":
        return cmd_check_phase()
    if cmd == "cluster-status":
        return cmd_cluster_status()
    if cmd == "scoped-tests":
        if len(sys.argv) < 3:
            print("Usage: adg_ci_gate.py scoped-tests <root_module_path>", file=sys.stderr)
            return 1
        return cmd_scoped_tests(sys.argv[2])
    if cmd == "litmus":
        if len(sys.argv) < 3:
            print("Usage: adg_ci_gate.py litmus <cluster_id>", file=sys.stderr)
            return 1
        return cmd_litmus(sys.argv[2])
    if cmd == "advance-phase":
        if len(sys.argv) < 3:
            print("Usage: adg_ci_gate.py advance-phase <phase_number>", file=sys.stderr)
            return 1
        try:
            phase = int(sys.argv[2])
        except ValueError:
            print(f"Invalid phase number: {sys.argv[2]!r}", file=sys.stderr)
            return 1
        return cmd_advance_phase(phase)

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
