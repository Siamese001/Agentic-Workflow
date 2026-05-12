"""AG-PURITY Gate: Agentic Core Purity + Apps U0 Input Contract.

Enforces the constitutional invariant that agentic_core remains app-agnostic
and apps_* domain packages enter the spine only through U0 runtime_customization_package.

Gate ID: AG-PURITY
Gate Family: agentic_core_purity
Severity: P1
Mode: advisory (CI effect: warn)

W2 Refinement: Leakage detection with exemptions + literal detection (W3 runtime checks pending).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration
__adg_consumer_mode__ = "inventory"

import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation

try:
    from tqdm import tqdm
except ImportError as exc:
    raise RuntimeError("tqdm is required for ADG CI gates; install with: pip install tqdm") from exc


@dataclass
class AGPurityViolation:
    """11-field violation artifact per AG-PURITY spec.
    
    Maps to GateViolation for base class compatibility.
    """
    # Required 11 fields
    source_path: str
    target_path: str | None
    source_line: int | None
    target_line: int | None
    relation_type: str
    leakage_type: str
    severity: str  # P1/P2/P3
    ci_effect: str  # warn/fail
    classification_reason: str
    suggested_action: str
    evidence_refs: list[str] = field(default_factory=list)
    
    # Internal tracking (not in JSON output)
    violation_id: str = ""
    in_modified_area: bool = False
    exemption_type: str | None = None  # W2: TEST_ALLOWED, DOC_ALLOWED, etc.
    
    def to_dict(self) -> dict[str, Any]:
        """Emit the 11 required fields plus violation_id."""
        return {
            "violation_id": self.violation_id,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "source_line": self.source_line,
            "target_line": self.target_line,
            "relation_type": self.relation_type,
            "leakage_type": self.leakage_type,
            "severity": self.severity,
            "ci_effect": self.ci_effect,
            "classification_reason": self.classification_reason,
            "suggested_action": self.suggested_action,
            "evidence_refs": self.evidence_refs,
            "in_modified_area": self.in_modified_area,
            "exemption_type": self.exemption_type,
        }
    
    def to_gate_violation(self) -> GateViolation:
        """Convert to base GateViolation for artifact writing."""
        return GateViolation(
            violation_id=self.violation_id,
            source_view="ag_purity_detection",
            source_node=None,
            source_edge=None,
            file=self.source_path,
            line=self.source_line,
            layer_src="agentic_core" if self.source_path.startswith("agentic_core/") else "apps",
            layer_dst="apps" if self.target_path and self.target_path.startswith("apps_") else "core",
            path_id=None,
            first_illegal_hop=f"{self.relation_type}:{self.leakage_type}",
            path_criticality=3.0 if self.severity == "P1" else (2.0 if self.severity == "P2" else 1.0),
            in_modified_area=self.in_modified_area,
            message=f"[{self.leakage_type}] {self.classification_reason}",
            extra=self.to_dict(),
            path_criticality_class="core_app_leakage",
            structured_action_required=True,
            approval_required=self.severity == "P1",
        )


class AgenticCorePurityGate(ADGGateBase):
    """AG-PURITY Gate: Detects app-specific leakage into agentic_core.
    
    Implements W1 skeleton with ADG query layer for:
    - CORE_TO_APP_IMPORT detection
    - CORE_TO_APP_CALL detection  
    - APP_TO_CORE_DIRECT_IMPORT detection (bypassing U0)
    
    W2/W3 heuristics (literal detection, thin adapter checks, etc.) pending.
    """
    
    gate_family = "agentic_core_purity"
    severity = "P1"
    gate_mode = "advisory"
    ci_effect = "warn"
    default_violation_severity = "P1"
    
    # Source views from W0 schema discovery
    source_views = [
        "nodes",
        "edges",
        "violations",
        "mv_edges_governance",
        "v_infra_violations_summary",
    ]
    
    def __init__(
        self,
        sqlite_path: Path | None = None,
        modified_files: list[str] | None = None,
        preflight_mode: bool = False,
    ):
        super().__init__(sqlite_path, modified_files, preflight_mode)
        self.purity_violations: list[AGPurityViolation] = []
        self.exempted_violations: list[AGPurityViolation] = []
        self.gate_metadata = {
            "gate_id": "AG-PURITY",
            "gate_family": self.gate_family,
            "severity": self.severity,
            "gate_mode": self.gate_mode,
            "ci_effect": self.ci_effect,
            "version": "W2-refinement",
            "schema_adaptations": {
                "nodes.body": "MISSING - use file-based literal detection",
                "edges.target_file": "MISSING - join via edges.dst_id -> nodes.id",
                "nodes.line_start": "MISSING - use nodes.span_line",
                "edges.line_no": "AVAILABLE - use for source line",
            },
        }
    
    def _execute_gate_logic(self) -> GateResult:
        """Execute AG-PURITY detection (W2 refinement)."""
        summary: dict[str, Any] = {
            "gate_metadata": self.gate_metadata,
            "total_violations": 0,
            "active_violation_count": 0,
            "exempted_count": 0,
            "by_leakage_type": {},
            "by_severity": {},
            "by_exemption_type": {},
            "in_modified_area": 0,
            "queries_executed": [],
            "w1_scope": "core_to_app_import, core_to_app_call, app_to_core_direct",
            "w2_scope": "literal_detection, exemption_classification, app_to_core_refinement",
            "w3_pending": "runtime_package_validation, thin_adapter_receipt_checks",
            "w2_refinement_applied": True,
            "top_source_paths": [],
            "top_target_paths": [],
        }
        
        if not self.conn:
            return self._empty_result(summary)
        
        self.purity_violations = []
        self.exempted_violations = []
        
        # W1/W2: Core detection queries with exemption classification
        self._detect_core_to_app_imports(summary)
        self._detect_core_to_app_calls(summary)
        self._detect_app_to_core_direct_imports(summary)
        
        # W2: Literal detection in agentic_core files
        self._detect_core_app_specific_literals(summary)
        
        # Summary aggregation - separate active vs exempted
        all_violations = self.purity_violations + self.exempted_violations
        summary["total_violations"] = len(all_violations)
        summary["active_violation_count"] = len(self.purity_violations)
        summary["exempted_count"] = len(self.exempted_violations)
        
        for v in self.purity_violations:
            summary["by_leakage_type"][v.leakage_type] = summary["by_leakage_type"].get(v.leakage_type, 0) + 1
            summary["by_severity"][v.severity] = summary["by_severity"].get(v.severity, 0) + 1
            if v.in_modified_area:
                summary["in_modified_area"] += 1
        
        # Track exemption types from exempted violations (stored in extra)
        for v in self.exempted_violations:
            exemption_type = v.to_dict().get("exemption_type", "UNKNOWN")
            summary["by_exemption_type"][exemption_type] = summary["by_exemption_type"].get(exemption_type, 0) + 1
        
        # Compute top source/target paths
        source_counts: dict[str, int] = {}
        target_counts: dict[str, int] = {}
        for v in self.purity_violations:
            source_counts[v.source_path] = source_counts.get(v.source_path, 0) + 1
            if v.target_path:
                target_counts[v.target_path] = target_counts.get(v.target_path, 0) + 1
        summary["top_source_paths"] = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        summary["top_target_paths"] = sorted(target_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Advisory mode: never blocked, always warn
        status = "warn" if self.purity_violations else "passed"
        
        # Convert to GateViolation for base class artifact writing
        gate_violations = [v.to_gate_violation() for v in self.purity_violations]
        
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=gate_violations,
            summary=summary,
            policy=self.execution_policy,
        )
    
    def _detect_core_to_app_imports(self, summary: dict[str, Any]) -> None:
        """Detect agentic_core importing from apps_* (reverse flow).
        
        Uses W0 schema: edges.src_id -> nodes.id, edges.dst_id -> nodes.id
        """
        query_name = "core_to_app_imports"
        summary["queries_executed"].append(query_name)
        
        if not self.conn:
            return
        
        try:
            # W0-adjusted query: join edges to nodes for target path
            cursor = self.conn.execute("""
                SELECT 
                    e.source_file as source_path,
                    e.line_no as source_line,
                    n_dst.resolved_path as target_path,
                    e.target_span_line as target_line,
                    e.relation_type,
                    e.symbol,
                    n_src.adg_name as source_node_name,
                    n_dst.adg_name as target_node_name
                FROM edges e
                JOIN nodes n_src ON e.src_id = n_src.id
                JOIN nodes n_dst ON e.dst_id = n_dst.id
                WHERE e.relation_type = 'imports'
                  AND e.source_file LIKE 'agentic_core/%'
                  AND n_dst.resolved_path LIKE 'apps_%/%'
                  AND e.source_file NOT LIKE '%/tests/%'
                  AND e.source_file NOT LIKE '%/docs/%'
                  AND e.source_file NOT LIKE '%/_archive/%'
            """)
            
            rows = cursor.fetchall()
            for row in tqdm(rows, desc=f"AG-PURITY {query_name}", unit="violation", disable=len(rows) < 10):
                source_path = row["source_path"]
                target_path = row["target_path"]
                
                in_mod = self._is_in_modified_area(source_path)
                
                violation = AGPurityViolation(
                    source_path=source_path,
                    target_path=target_path,
                    source_line=row["source_line"],
                    target_line=row["target_line"],
                    relation_type="imports",
                    leakage_type="CORE_TO_APP_IMPORT",
                    severity=self.default_violation_severity,
                    ci_effect=self.ci_effect,
                    classification_reason=f"agentic_core imports from {target_path.split('/')[0]} directly, bypassing U0 abstraction",
                    suggested_action="Move import to app's U0 runtime_customization_package or add TEMPORARY_THIN_ADAPTER receipt",
                    evidence_refs=[
                        f"edge:{row['source_node_name']}->{row['target_node_name']}",
                        f"symbol:{row['symbol']}",
                    ],
                    violation_id=f"core_import_{self._hash_violation(source_path, target_path, row['symbol'])}",
                    in_modified_area=in_mod,
                )
                # W2: Apply exemption classification
                exemption = self._classify_exemption(source_path, target_path)
                if exemption:
                    violation.exemption_type = exemption
                    self.exempted_violations.append(violation)
                else:
                    self.purity_violations.append(violation)
                
        except sqlite3.Error as e:
            summary[f"{query_name}_error"] = str(e)
    
    def _detect_core_to_app_calls(self, summary: dict[str, Any]) -> None:
        """Detect agentic_core calling into apps_* functions.
        
        Uses relation_type 'resolves_callsite' or semantic call detection.
        """
        query_name = "core_to_app_calls"
        summary["queries_executed"].append(query_name)
        
        if not self.conn:
            return
        
        try:
            # Look for callsite resolutions from core to apps
            cursor = self.conn.execute("""
                SELECT 
                    e.source_file as source_path,
                    e.line_no as source_line,
                    n_dst.resolved_path as target_path,
                    e.target_span_line as target_line,
                    e.relation_type,
                    e.symbol,
                    n_src.adg_name as source_node_name,
                    n_dst.adg_name as target_node_name
                FROM edges e
                JOIN nodes n_src ON e.src_id = n_src.id
                JOIN nodes n_dst ON e.dst_id = n_dst.id
                WHERE e.relation_type IN ('resolves_callsite', 'controls_flow')
                  AND e.source_file LIKE 'agentic_core/%'
                  AND n_dst.resolved_path LIKE 'apps_%/%'
                  AND e.source_file NOT LIKE '%/tests/%'
                  AND e.source_file NOT LIKE '%/docs/%'
            """)
            
            rows = cursor.fetchall()
            for row in tqdm(rows, desc=f"AG-PURITY {query_name}", unit="violation", disable=len(rows) < 10):
                source_path = row["source_path"]
                target_path = row["target_path"]
                
                in_mod = self._is_in_modified_area(source_path)
                
                violation = AGPurityViolation(
                    source_path=source_path,
                    target_path=target_path,
                    source_line=row["source_line"],
                    target_line=row["target_line"],
                    relation_type=row["relation_type"],
                    leakage_type="CORE_TO_APP_CALL",
                    severity=self.default_violation_severity,
                    ci_effect=self.ci_effect,
                    classification_reason=f"agentic_core calls into {target_path.split('/')[0]} at runtime, violating app-agnostic contract",
                    suggested_action="Refactor to U0 customization_package injection pattern or use generic interface",
                    evidence_refs=[
                        f"callsite:{row['source_node_name']}->{row['target_node_name']}",
                        f"symbol:{row['symbol']}",
                    ],
                    violation_id=f"core_call_{self._hash_violation(source_path, target_path, row['symbol'])}",
                    in_modified_area=in_mod,
                )
                # W2: Apply exemption classification
                exemption = self._classify_exemption(source_path, target_path)
                if exemption:
                    violation.exemption_type = exemption
                    self.exempted_violations.append(violation)
                else:
                    self.purity_violations.append(violation)
                
        except sqlite3.Error as e:
            summary[f"{query_name}_error"] = str(e)
    
    def _detect_app_to_core_direct_imports(self, summary: dict[str, Any]) -> None:
        """Detect apps_* importing core layers directly (bypassing U0).
        
        Allowed: apps_* -> U0 runtime_customization_package
        Blocked: apps_* -> L0/L1/L2/L3/L4/L5/L6 directly
        """
        query_name = "app_to_core_direct"
        summary["queries_executed"].append(query_name)
        
        if not self.conn:
            return
        
        try:
            cursor = self.conn.execute("""
                SELECT 
                    n_src.resolved_path as app_path,
                    n_dst.resolved_path as core_path,
                    e.relation_type,
                    e.line_no as import_line,
                    n_src.adg_name as app_node,
                    n_dst.adg_name as core_node,
                    n_dst.layer as core_layer
                FROM edges e
                JOIN nodes n_src ON e.src_id = n_src.id
                JOIN nodes n_dst ON e.dst_id = n_dst.id
                WHERE n_src.resolved_path LIKE 'apps_%/%'
                  AND n_dst.resolved_path LIKE 'agentic_core/%'
                  AND n_dst.resolved_path NOT LIKE '%/runtime/customization_package%'
                  AND n_dst.resolved_path NOT LIKE '%/runtime/entry/%'
                  AND n_dst.resolved_path NOT LIKE '%/runtime/exit/%'
                  AND e.relation_type = 'imports'
            """)
            
            rows = cursor.fetchall()
            for row in tqdm(rows, desc=f"AG-PURITY {query_name}", unit="violation", disable=len(rows) < 10):
                app_path = row["app_path"]
                core_path = row["core_path"]
                core_layer = row["core_layer"] if row["core_layer"] else "unknown"
                
                # W2: Skip allowed entrypoint/adapter imports
                if self._is_allowed_entrypoint_adapter(core_path):
                    continue
                
                # W2: Only flag internal layer imports
                if not self._is_core_internal_layer(core_path):
                    # Not an internal layer, skip
                    continue
                
                in_mod = self._is_in_modified_area(app_path)
                
                # W2: Determine leakage type based on layer severity
                if core_layer in ["L0", "L1"]:
                    leakage_type = "APP_BYPASSES_U0"
                else:
                    leakage_type = "APP_DIRECT_TO_CORE_LAYER"
                
                violation = AGPurityViolation(
                    source_path=app_path,
                    target_path=core_path,
                    source_line=row["import_line"],
                    target_line=None,
                    relation_type="imports",
                    leakage_type=leakage_type,
                    severity=self.default_violation_severity,
                    ci_effect=self.ci_effect,
                    classification_reason=f"{app_path.split('/')[0]} imports {core_layer} directly, bypassing U0 runtime_customization_package",
                    suggested_action="Route through U0 runtime_customization_package or request TEMPORARY_THIN_ADAPTER receipt",
                    evidence_refs=[
                        f"app->{core_layer}",
                        f"import:{row['app_node']}->{row['core_node']}",
                    ],
                    violation_id=f"app_direct_{self._hash_violation(app_path, core_path, row['app_node'])}",
                    in_modified_area=in_mod,
                )
                # W2: Apply exemption classification
                exemption = self._classify_exemption(app_path, core_path)
                if exemption:
                    violation.exemption_type = exemption
                    self.exempted_violations.append(violation)
                else:
                    self.purity_violations.append(violation)
                
        except sqlite3.Error as e:
            summary[f"{query_name}_error"] = str(e)
    
    def _hash_violation(self, source: str, target: str, symbol: str) -> str:
        """Generate deterministic violation ID."""
        import hashlib
        content = f"{source}:{target}:{symbol}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    # =========================================================================
    # W2 Exemption Classification
    # =========================================================================
    
    def _classify_exemption(self, source_path: str, target_path: str | None = None) -> str | None:
        """Classify if a path qualifies for exemption.
        
        Returns exemption type or None if not exempt.
        """
        path = source_path.lower()
        
        # TEST_ALLOWED: files in test directories or test-named files
        if any(p in path for p in ['/tests/', '/test_', '_test.py', 'conftest.py']):
            return "TEST_ALLOWED"
        
        # DOC_ALLOWED: documentation files and docs/ directories
        if any(p in path for p in ['/docs/', '/doc/', '.md', '.rst', '.txt']):
            return "DOC_ALLOWED"
        
        # RECEIPT_ALLOWED: governance receipt files
        if any(p in path for p in ['receipt', '/receipts/', 'migration_receipt', '_receipt.md']):
            return "RECEIPT_ALLOWED"
        
        # GENERATED_ALLOWED: generated artifacts and reports
        if any(p in path for p in [
            '/artifacts/', '/generated/', '/reports/', '/output/',
            '.json', '.yaml', '.yml'  # Config/artifact files
        ]):
            # But not source code configs
            if not path.endswith('.py'):
                return "GENERATED_ALLOWED"
        
        # MIGRATION_ALLOWED: files clearly in migration paths
        if any(p in path for p in [
            '/migration/', '/migrations/', '/archive/', '/_archive/',
            '/legacy/', '/deprecated/'
        ]):
            return "MIGRATION_ALLOWED"
        
        # Not exempt
        return None
    
    def _is_allowed_entrypoint_adapter(self, core_path: str) -> bool:
        """Check if core_path is an allowed entrypoint/adapter surface.
        
        Apps are allowed to import:
        - U0 runtime customization_package surfaces
        - Declared app entrypoints/adapters
        """
        path_lower = core_path.lower()
        
        # Allowed: runtime entry surfaces
        if '/runtime/entry/' in path_lower:
            return True
        if '/runtime/customization_package/' in path_lower:
            return True
        if '/runtime/exit/' in path_lower:
            return True
        
        # Allowed: explicit adapter surfaces (binding files)
        if 'binding' in path_lower and ('_binding.py' in path_lower or '/binding' in path_lower):
            return True
        
        # Allowed: dispatch entrypoints
        if 'dispatch' in path_lower and '_dispatch' in path_lower:
            return True
        
        return False
    
    def _is_core_internal_layer(self, core_path: str) -> bool:
        """Check if core_path is an internal layer (not U0/entry surfaces).
        
        Internal layers that should not be directly imported:
        - L0, L1, L2, L3, L4, L5, L6
        - C0, prompt governance, UWG
        """
        path_lower = core_path.lower()
        
        internal_patterns = [
            '/l0_', '/l0/', 'l0_',
            '/l1_', '/l1/', 'l1_',
            '/l2_', '/l2/', 'l2_',
            '/l3_', '/l3/', 'l3_',
            '/l4_', '/l4/', 'l4_',
            '/l5_', '/l5/', 'l5_',
            '/l6_', '/l6/', 'l6_',
            '/c0/', '/c0_',
            '/prompt_', '/prompt/',
            '/uwg/', '/uwg_',
            '/exit/', '/exit_',
        ]
        
        for pattern in internal_patterns:
            if pattern in path_lower:
                return True
        
        return False
    
    def _detect_core_app_specific_literals(self, summary: dict[str, Any]) -> None:
        """W2: Detect app-specific string literals in agentic_core files.
        
        Uses SQL + Python hybrid approach (nodes.body missing per W0).
        - Query ADG for agentic_core Python files
        - Read file contents from disk
        - Search for app-specific literal patterns
        """
        query_name = "core_app_specific_literals"
        summary["queries_executed"].append(query_name)
        
        if not self.conn:
            return
        
        # App-specific literal patterns to search for
        app_patterns = [
            r'apps_rg',
            r'apps_lic',
            r'apps_research',
            r'apps_qna',
            r'apps_rfp',
            r'apps_exec',
            r'apps_underwriting_ai',
            r'apps_architect',
            r'apps_shared',
            r'apps_[a-z_]+',  # Catch-all for apps_* pattern
        ]
        
        try:
            # Query ADG for agentic_core Python files (not tests/docs)
            cursor = self.conn.execute("""
                SELECT DISTINCT resolved_path
                FROM nodes
                WHERE resolved_path LIKE 'agentic_core/%'
                  AND resolved_path LIKE '%.py'
                  AND resolved_path NOT LIKE '%/tests/%'
                  AND resolved_path NOT LIKE '%/docs/%'
                  AND resolved_path NOT LIKE '%/_archive/%'
                  AND resolved_path NOT LIKE '%/receipts/%'
            """)
            
            core_files = [row["resolved_path"] for row in cursor.fetchall()]
            
            for file_path in tqdm(core_files, desc=f"AG-PURITY {query_name}", unit="file", disable=len(core_files) < 10):
                full_path = _REPO_ROOT / file_path
                
                # Skip if file doesn't exist or can't be read
                if not full_path.exists():
                    continue
                
                try:
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                except (OSError, UnicodeDecodeError):
                    continue
                
                # Search for app-specific literals
                for pattern in app_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Extract surrounding context (80 chars before/after)
                        start = max(0, match.start() - 40)
                        end = min(len(content), match.end() + 40)
                        context = content[start:end].replace('\n', ' ')
                        
                        in_mod = self._is_in_modified_area(file_path)
                        
                        violation = AGPurityViolation(
                            source_path=file_path,
                            target_path=None,
                            source_line=line_num,
                            target_line=None,
                            relation_type="literal_reference",
                            leakage_type="CORE_APP_SPECIFIC_LITERAL",
                            severity=self.default_violation_severity,
                            ci_effect=self.ci_effect,
                            classification_reason=f"agentic_core contains app-specific literal '{match.group()}'",
                            suggested_action="Move app-specific literal to U0 runtime_customization_package or use generic profile reference",
                            evidence_refs=[
                                f"literal:{match.group()}",
                                f"context:{context[:80]}",
                            ],
                            violation_id=f"literal_{self._hash_violation(file_path, str(line_num), match.group())}",
                            in_modified_area=in_mod,
                        )
                        # W2: Apply exemption classification
                        exemption = self._classify_exemption(file_path)
                        if exemption:
                            violation.exemption_type = exemption
                            self.exempted_violations.append(violation)
                        else:
                            self.purity_violations.append(violation)
                        
                        # Only report first match per pattern per file to avoid spam
                        break
                        
        except sqlite3.Error as e:
            summary[f"{query_name}_error"] = str(e)
    
    def _empty_result(self, summary: dict[str, Any] | None = None) -> GateResult:
        """Return empty result when connection unavailable."""
        final_summary = summary or {"gate_metadata": self.gate_metadata}
        final_summary.update({
            "total_violations": 0,
            "note": "ADG connection unavailable - no violations detected",
        })
        
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary=final_summary,
            policy=self.execution_policy,
        )
    
    def run_and_exit(self) -> int:
        """Execute gate and exit with appropriate code for CI.
        
        Advisory mode: always exits 0, prints warnings to stderr.
        """
        try:
            result = self.run(emit_artifacts=True)
            
            # Advisory mode: never block, but report
            if result.violations:
                print(f"\n[AG-PURITY] ⚠️  WARN: {len(result.violations)} purity violations detected", file=sys.stderr)
                print(f"[AG-PURITY] Mode: {self.gate_mode} (non-blocking)", file=sys.stderr)
                for v in result.violations[:5]:  # Show first 5
                    extra = v.extra
                    print(f"  - [{extra.get('leakage_type', 'UNKNOWN')}] {v.file}:{v.line or '?'}", file=sys.stderr)
                if len(result.violations) > 5:
                    print(f"  ... and {len(result.violations) - 5} more", file=sys.stderr)
                print(f"[AG-PURITY] Artifacts: artifacts/ci_gates/", file=sys.stderr)
            else:
                print(f"[AG-PURITY] ✅ PASSED: No purity violations detected")
            
            # Advisory mode: always exit 0
            return 0
            
        except (sqlite3.Error, OSError, RuntimeError) as e:
            print(f"\n[AG-PURITY] ERROR: Gate failed to execute: {e}", file=sys.stderr)
            # Advisory mode: even on error, exit 0 but report
            print(f"[AG-PURITY] Advisory mode: exiting 0 despite error", file=sys.stderr)
            return 0


def main() -> int:
    """CLI entry point."""
    gate = AgenticCorePurityGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    sys.exit(main())
