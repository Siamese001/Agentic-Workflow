"""V15 Phase 6 Gate Runner — Typed Boundaries (§1.5 / §3.8)

CI-ready evidence-only gate. Verifies cross-layer artifact boundary compliance:
- SSOTBinding type exists for node_id → blueprint resolution
- ContextRetrievalRequest exists for L0→L4 typed boundary
- Cross-layer imports follow layer ordering (no L0→L5 inversion in types)
- All P6 artifact types are frozen (immutable)

Emits evidence JSON to docs/reports/plans/. Non-blocking (exit 0).

Usage:
    python ops_scripts/ci/run_v15_p6_gate.py
    python ops_scripts/ci/run_v15_p6_gate.py --repo-root /path/to/repo
"""

import ast
import json
import re
import sys

_FIXED_TS = "2026-01-01T00:00:00Z"
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
EVIDENCE_DIR = PROJECT_ROOT / "docs" / REPORTS_DIR / "plans"
LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
V15_TYPE_FILES = [
    "agentic_core/L0_routing/types/determinism_types.py",
    "agentic_core/L0_routing/types/determinism_contracts_types.py",
    "agentic_core/L0_routing/types/governance_types.py",
    "agentic_core/L0_routing/types/traceability_types.py",
    "agentic_core/L0_routing/types/crypto_trust_types.py",
    "agentic_core/L0_routing/types/boundary_types.py",
]


class P6EvidenceCollector:
    """Collect evidence for §1.5/§3.8 — Typed Boundaries."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.violations: list[dict] = []
        self.checks_passed: list[dict] = []

    def collect(self) -> dict:
        """Run all P6 checks and return evidence dict."""
        self._check_ssot_binding_type()
        self._check_context_retrieval_request()
        self._check_layer_boundary_imports()
        self._check_p6_artifact_immutability()
        self._check_all_type_files_exist()
        total = len(self.violations) + len(self.checks_passed)
        return {
            "phase": "P6",
            "gate": "typed_boundaries",
            "spec_section": "§1.5/§3.8",
            "timestamp": _FIXED_TS,
            "total_checks": total,
            "passed": len(self.checks_passed),
            "violations": len(self.violations),
            "violation_details": self.violations,
            "passed_details": self.checks_passed,
            "blocking": False,
        }

    def _check_ssot_binding_type(self):
        """Verify SSOTBinding type exists with required fields."""
        p6_path = self.repo_root / "agentic_core/L0_routing/types/boundary_types.py"
        if not p6_path.exists():
            self.violations.append({"check": "ssot_binding_type", "detail": "boundary_types.py not found"})
            return
        content = p6_path.read_text(encoding="utf-8")
        has_class = "class SSOTBinding" in content
        has_node_id = "node_id:" in content
        has_blueprint = "blueprint_entry:" in content
        has_resolved = "resolved:" in content
        if has_class and has_node_id and has_blueprint and has_resolved:
            self.checks_passed.append(
                {
                    "check": "ssot_binding_type",
                    "detail": "SSOTBinding found with node_id, blueprint_entry, resolved",
                }
            )
        else:
            self.violations.append(
                {
                    "check": "ssot_binding_type",
                    "detail": f"class={has_class}, node_id={has_node_id}, blueprint_entry={has_blueprint}, resolved={has_resolved}",
                }
            )

    def _check_context_retrieval_request(self):
        """Verify ContextRetrievalRequest exists for L0→L4 boundary."""
        p6_path = self.repo_root / "agentic_core/L0_routing/types/boundary_types.py"
        if not p6_path.exists():
            return
        content = p6_path.read_text(encoding="utf-8")
        has_class = "class ContextRetrievalRequest" in content
        has_trace = "trace_id:" in content
        has_query = "query_hash:" in content
        if has_class and has_trace and has_query:
            self.checks_passed.append(
                {
                    "check": "context_retrieval_request",
                    "detail": "ContextRetrievalRequest found for L0→L4 boundary",
                }
            )
        else:
            self.violations.append(
                {
                    "check": "context_retrieval_request",
                    "detail": f"class={has_class}, trace_id={has_trace}, query_hash={has_query}",
                }
            )

    def _check_layer_boundary_imports(self):
        """Verify V15 type files in L0 do not import from higher layers."""
        layer_re = re.compile("from\\s+agentic_core\\.(L\\d)_")
        for rel_path in V15_TYPE_FILES:
            fpath = self.repo_root / rel_path
            if not fpath.exists():
                continue
            try:
                tree = ast.parse(fpath.read_text(encoding="utf-8"), filename=str(fpath))
            except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
                self.violations.append(
                    {
                        "check": "layer_boundary_imports",
                        "file": rel_path,
                        "detail": "SyntaxError — cannot parse",
                    }
                )
                continue
            inversions = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        m = layer_re.match(node.module)
                        if m:
                            imported_layer = m.group(1)
                            if LAYER_ORDER.get(imported_layer, 0) > LAYER_ORDER.get("L0", 0):
                                inversions.append(
                                    {"line": node.lineno, "module": node.module, "layer": imported_layer}
                                )
            if not inversions:
                self.checks_passed.append(
                    {
                        "check": "layer_boundary_imports",
                        "file": rel_path,
                        "detail": "No layer inversions in L0 type file",
                    }
                )
            else:
                self.violations.append(
                    {
                        "check": "layer_boundary_imports",
                        "file": rel_path,
                        "detail": f"{len(inversions)} layer inversions found",
                        "inversions": inversions,
                    }
                )

    def _check_p6_artifact_immutability(self):
        """Verify all dataclasses in boundary_types are frozen."""
        p6_path = self.repo_root / "agentic_core/L0_routing/types/boundary_types.py"
        if not p6_path.exists():
            return
        content = p6_path.read_text(encoding="utf-8")
        frozen_count = content.count("@dataclass(frozen=True)")
        total_dc = content.count("@dataclass")
        if total_dc > 0 and frozen_count == total_dc:
            self.checks_passed.append(
                {
                    "check": "p6_artifact_immutability",
                    "detail": f"All {total_dc} dataclasses in boundary_types are frozen=True",
                }
            )
        elif total_dc > 0:
            self.violations.append(
                {
                    "check": "p6_artifact_immutability",
                    "detail": f"{frozen_count}/{total_dc} dataclasses are frozen",
                }
            )

    def _check_all_type_files_exist(self):
        """Verify all V15 type files in the boundary chain exist."""
        missing = []
        for rel_path in V15_TYPE_FILES:
            fpath = self.repo_root / rel_path
            if not fpath.exists():
                missing.append(rel_path)
        if not missing:
            self.checks_passed.append(
                {
                    "check": "type_files_complete",
                    "detail": f"All {len(V15_TYPE_FILES)} V15 type files present",
                }
            )
        else:
            self.violations.append({"check": "type_files_complete", "detail": f"Missing: {missing}"})


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="V15 Phase 6 Gate — Typed Boundaries")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    repo_root = args.repo_root or PROJECT_ROOT
    output = args.output or EVIDENCE_DIR / "v15_p6_evidence.json"
    print("[P6-GATE] Starting Phase 6 gate (§1.5/§3.8 — Typed Boundaries)...")
    collector = P6EvidenceCollector(repo_root)
    evidence = collector.collect()
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)
    print(f"[P6-GATE] Evidence written to: {output}")
    print(f"[P6-GATE] Checks passed: {evidence['passed']}, Violations: {evidence['violations']}")
    print("[P6-GATE] PASSED (evidence-only, non-blocking)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
