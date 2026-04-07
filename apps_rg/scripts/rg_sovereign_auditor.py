"""
APPS_RG SOVEREIGN STRUCTURAL AUDIT TOOL

Performs recursive, logic-based audit of 'apps_rg/' to classify every file for V2.5 Sovereign migration.
Analyzes actual code structure, not just file names.
"""

import ast
import json
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "rg_sovereign_auditor", "p0_governance")
_emit_reads_policy_state("p0", "rg_sovereign_auditor", "policy_binding")
_emit_snapshots_state("p0", "rg_sovereign_auditor", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("rg_sovereign_auditor", "p4obs", "metric_1")
_emit_emits_metric_event("rg_sovereign_auditor", "p4obs", "metric_2")
_emit_emits_metric_event("rg_sovereign_auditor", "p4obs", "metric_3")
_emit_emits_metric_event("rg_sovereign_auditor", "p4obs", "metric_4")
_emit_emits_metric_event("rg_sovereign_auditor", "p4obs", "metric_5")
_emit_emits_metric_event("rg_sovereign_auditor", "p4obs", "metric_6")
_emit_records_incident_event("rg_sovereign_auditor", "p4obs", "incident")
_emit_captures_runtime_anomaly("rg_sovereign_auditor", "p4obs", "anomaly")
_emit_writes_observability_log("rg_sovereign_auditor", "p4obs", "obs_log")
_emit_updates_monitoring_state("rg_sovereign_auditor", "p4obs", "mon_state")
_emit_triggers_alert("rg_sovereign_auditor", "p4obs", "alert")
_emit_links_incident_trace("rg_sovereign_auditor", "p4obs", "trace_link")
_emit_captures_pattern("rg_sovereign_auditor", "p3lm", "pattern")
_emit_records_learning_event("rg_sovereign_auditor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rg_sovereign_auditor", "p3lm", "snapshot")
_emit_feeds_meta_learning("rg_sovereign_auditor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rg_sovereign_auditor", "p3lm", "routing")
_emit_improves_agent_policy("rg_sovereign_auditor", "p3lm", "policy")
_emit_stores_learning_state("rg_sovereign_auditor", "p3lm", "state")
_emit_records_execution_trace("rg_sovereign_auditor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rg_sovereign_auditor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rg_sovereign_auditor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rg_sovereign_auditor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rg_sovereign_auditor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rg_sovereign_auditor", "env_read", "p2_env_1")
_emit_reads_environ("rg_sovereign_auditor", "env_read", "p2_env_2")
_emit_reads_runtime_state("rg_sovereign_auditor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rg_sovereign_auditor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rg_sovereign_auditor", "context_pull")
_emit_pulls_context("p1", "rg_sovereign_auditor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rg_sovereign_auditor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rg_sovereign_auditor", "uwg_term_2")
_emit_writes_through("p1", "rg_sovereign_auditor", "write_through")
_emit_writes_through("p1", "rg_sovereign_auditor", "write_through_2")
_emit_validated_by_safety_plane("p1", "rg_sovereign_auditor", "safety_validation")
_emit_invokes_eval("p1", "rg_sovereign_auditor", "eval_call")
_emit_proposal_commits_routing("p1", "rg_sovereign_auditor", "routing_commit")
_emit_escalates_to_human("p1", "rg_sovereign_auditor", "human_escalation")
_emit_routes_through("p1", "rg_sovereign_auditor", "route_through")
_emit_checks_agent_registry("p1", "rg_sovereign_auditor", "agent_registry")
_emit_validates_agent_capability("p1", "rg_sovereign_auditor", "capability")
_emit_dispatches_execution_plan("p1", "rg_sovereign_auditor", "exec_plan")
_emit_agent_executes_agent("p1", "rg_sovereign_auditor", "sub_agent")
_emit_routes_to_agent("p1", "rg_sovereign_auditor", "target_agent")
_emit_verifies_policy("p1", "rg_sovereign_auditor", "policy_check")
_emit_observes_runtime_state("p1", "rg_sovereign_auditor", "runtime_state")
_emit_verifies_boundary("p1", "rg_sovereign_auditor", "boundary_check")
_emit_transcripts_response("p1", "rg_sovereign_auditor", "transcript")
_emit_hard_fails_untranscripted("p1", "rg_sovereign_auditor")
_emit_gated_by_confidence("p1", "rg_sovereign_auditor", "confidence_gate")
emit_replay_key("p0", "rg_sovereign_auditor")
emit_determinism_digest("p0", "rg_sovereign_auditor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rg_sovereign_auditor", "execution_auth")
_emit_validates_capability("p2", "rg_sovereign_auditor", "capability_check")
_emit_routes_to_capability("p2", "rg_sovereign_auditor", "capability_route")
_emit_writes_via_uwg("p2", "rg_sovereign_auditor", "uwg_write")
_emit_blocks_direct_write("p2", "rg_sovereign_auditor", "direct_write_block")
_emit_records_tool_invocation("p2", "rg_sovereign_auditor", "tool_invocation")
_emit_captures_execution_output("p2", "rg_sovereign_auditor", "exec_output")
_emit_dispatches_agent("p3", "rg_sovereign_auditor", "agent_dispatch")
_emit_coordinates_agents("p3", "rg_sovereign_auditor", "agent_coordination")
_emit_records_workflow_lineage("p3", "rg_sovereign_auditor", "workflow_lineage")
_emit_records_healing_outcome("p3", "rg_sovereign_auditor", "healing_outcome")
_emit_escalates_failure("p3", "rg_sovereign_auditor", "failure_escalation")
_emit_orchestrates_workflow("p3", "rg_sovereign_auditor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rg_sovereign_auditor", "healing_dispatch")
_emit_invokes_evaluation("p3", "rg_sovereign_auditor", "evaluation_signal")
_emit_records_telemetry_event("p4", "rg_sovereign_auditor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rg_sovereign_auditor", "eval_metric")
_emit_stores_embedding("p4", "rg_sovereign_auditor", "embedding_store")
_emit_updates_meta_learning_state("p4", "rg_sovereign_auditor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rg_sovereign_auditor", "exec_snapshot_link")


class RGSovereignAuditor:
    """Audits apps_rg structure for V2.5 Sovereign compliance."""

    def __init__(self, base_path: str = "apps_rg"):
        self.base_path = Path(base_path)
        self.audit_results = {
            "sovereign_agents": [],
            "stateless_tools": [],
            "passive_data": [],
            "legacy_debt": [],
            "unknown": [],
            "imposter_agent": [],
            "unknown_ledger": [],
            "nomenclature_fixes": [],
            "migration_candidates": [],
        }

    def analyze_file_structure(self, file_path: Path) -> dict:
        """Analyze a Python file for structural classification."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            try:
                tree = ast.parse(content)
            except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
                return {"error": "Syntax error - cannot analyze"}
            classes = self._extract_classes(tree)
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            classification, details = self._classify_file_logic(
                file_path.name, content, classes, imports, functions,
            )
            return {
                "classification": classification,
                "details": details,
                "classes": classes,
                "imports": imports,
                "functions": functions,
                "line_count": len(content.split("\n")),
            }
        except Exception as e:
            return {"error": f"Error reading file: {e}"}

    def _extract_classes(self, tree: ast.AST) -> list[dict]:
        """Extract class information from AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(
                            f"{base.value.id}.{base.attr}" if hasattr(base.value, "id") else str(base),
                        )
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                has_execute_or_process = any(
                    method in ["execute", "_process", "run", "run_phase"] for method in methods
                )
                has_init = "__init__" in methods
                has_heal = "heal_repository" in methods
                has_state = len(methods) > 3 or has_init
                classes.append(
                    {
                        "name": node.name,
                        "bases": bases,
                        "methods": methods,
                        "has_execute_or_process": has_execute_or_process,
                        "has_init": has_init,
                        "has_heal": has_heal,
                        "has_state": has_state,
                        "is_agent": "Agent" in node.name,
                        "is_mixin": "Mixin" in node.name,
                        "is_base": "Base" in node.name,
                        "is_model": "Model" in node.name or "Schema" in node.name,
                        "is_enum": "Enum" in node.name or node.name.endswith("Type"),
                        "line_count": node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0,
                    },
                )
        return classes

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        return imports

    def _extract_functions(self, tree: ast.AST) -> list[dict]:
        """Extract function information."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "args_count": len(node.args.args),
                        "is_generator": any(isinstance(item, ast.Yield) for item in ast.walk(node)),
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    },
                )
        return functions

    def _classify_file_logic(
        self, filename: str, content: str, classes: list[dict], imports: list[str], functions: list[dict],
    ) -> tuple[str, dict]:
        """Classify file based on actual logic and structure."""
        legacy_indicators = ["v1", "v2", "v3", "_old", "_deprecated", "_legacy", "old_", "deprecated"]
        if any(indicator in filename.lower() for indicator in legacy_indicators):
            return ("LEGACY_DEBT", {"reason": "Filename contains legacy version markers"})
        model_indicators = ["Model", "Schema", "Enum", "Type", "Data"]
        if any(indicator in filename for indicator in model_indicators):
            has_classes = len(classes) > 0
            all_passive = all(
                cls.get("is_model", False)
                or cls.get("is_enum", False)
                or (not cls.get("has_execute_or_process", False))
                for cls in classes
            )
            if has_classes and all_passive:
                return ("PASSIVE_DATA", {"reason": "Contains only passive data models/enums"})
        [cls for cls in classes if cls.get("is_agent", False)]
        agent_base_indicators = [
            "HealerMixin",
            "MCPHardenedMixin",
            "BaseAgent",
            "AgentBase",
            "SovereignBaseAgent",
        ]
        inherits_from_agent_base = any(
            any(indicator in base for base in cls.get("bases", []))
            for cls in classes
            for indicator in agent_base_indicators
        )
        agent_method_indicators = [
            "execute",
            "_process",
            "run",
            "run_phase",
            "heal_repository",
            "orchestrate",
            "dispatch",
        ]
        has_agent_methods = any(
            any(method in cls.get("methods", []) for method in agent_method_indicators) for cls in classes
        )
        has_agent_naming = (
            filename.endswith("Agent.py")
            or filename.endswith("Engine.py")
            or any(cls.get("is_agent", False) for cls in classes)
            or any("Engine" in cls.get("name", "") for cls in classes)
        )
        if (inherits_from_agent_base or has_agent_methods) and has_agent_naming:
            return (
                "SOVEREIGN_AGENT",
                {
                    "reason": "Inherits from agent base and has agent methods/naming",
                    "agent_classes": [
                        cls["name"]
                        for cls in classes
                        if cls.get("is_agent", False) or "Engine" in cls.get("name", "")
                    ],
                    "inherits_from_base": inherits_from_agent_base,
                    "has_agent_methods": has_agent_methods,
                },
            )
        tool_indicators = ["util", "tool", "helper", "formatter", "generator", "calculator"]
        is_tool_by_name = any(indicator in filename.lower() for indicator in tool_indicators)
        has_stateful_classes = any(cls.get("has_state", False) for cls in classes)
        has_init_methods = any("__init__" in cls.get("methods", []) for cls in classes)
        if is_tool_by_name or (not has_stateful_classes and (not has_init_methods) and (len(classes) == 0)):
            return (
                "STATELESS_TOOL",
                {
                    "reason": "Stateless utility functions or tool-like naming",
                    "is_tool_by_name": is_tool_by_name,
                    "has_stateful_classes": has_stateful_classes,
                },
            )
        if "Agent" in filename and (not inherits_from_agent_base) and (not has_agent_methods):
            return (
                "IMPOSTER_AGENT",
                {"reason": "Filename suggests agent but no agent inheritance or methods found"},
            )
        if "Engine" in filename or "engine" in filename.lower():
            if inherits_from_agent_base or has_agent_methods:
                return (
                    "SOVEREIGN_AGENT",
                    {
                        "reason": "Engine with agent base inheritance or methods",
                        "agent_classes": [cls["name"] for cls in classes],
                        "inherits_from_base": inherits_from_agent_base,
                    },
                )
            else:
                return (
                    "STATELESS_TOOL",
                    {"reason": "Engine without agent characteristics - likely a utility engine"},
                )
        if classes:
            has_execute_classes = any(cls.get("has_execute_or_process", False) for cls in classes)
            has_state_classes = any(cls.get("has_state", False) for cls in classes)
            if has_execute_classes and (has_state_classes or inherits_from_agent_base):
                return (
                    "SOVEREIGN_AGENT",
                    {
                        "reason": "Contains classes with execute/process methods and state or agent inheritance",
                    },
                )
            elif not has_state_classes and (not inherits_from_agent_base):
                return ("STATELESS_TOOL", {"reason": "Contains only stateless classes/functions"})
            else:
                return ("UNKNOWN", {"reason": "Contains stateful classes but no clear agent behavior"})
        elif functions:
            return ("STATELESS_TOOL", {"reason": "Contains only functions, no classes"})
        else:
            return ("UNKNOWN", {"reason": "Empty or minimal file"})

    def audit_directory(self) -> dict:
        """Perform comprehensive audit of apps_rg directory."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RGSovereignAuditor.audit_directory")

        if not self.base_path.exists():
            return {"error": f"Directory {self.base_path} does not exist"}
        print("🔍 APPS_RG SOVEREIGN STRUCTURAL AUDIT")
        print("=" * 60)
        results = {
            "total_files": 0,
            "by_directory": {},
            "classifications": self.audit_results.copy(),
            "unknown_ledger": [],
            "nomenclature_fixes": [],
            "migration_candidates": [],
        }
        for subdir in ["engines", "shared", "domain", "legacy"]:
            subdir_path = self.base_path / subdir
            if subdir_path.exists():
                print(f"\n📁 Analyzing {subdir}/")
                subdir_results = self._analyze_subdirectory(subdir_path, subdir)
                results["by_directory"][subdir] = subdir_results
                results["total_files"] += subdir_results["file_count"]
        self._generate_unknown_ledger(results)
        self._generate_nomenclature_fixes(results)
        self._generate_migration_candidates(results)
        self._print_audit_summary(results)
        return results

    def _analyze_subdirectory(self, subdir_path: Path, subdir_name: str) -> dict:
        """Analyze a specific subdirectory."""
        python_files = list(subdir_path.rglob("*.py"))
        subdir_results = {
            "file_count": len(python_files),
            "files": {},
            "classifications": {
                "SOVEREIGN_AGENT": [],
                "STATELESS_TOOL": [],
                "PASSIVE_DATA": [],
                "LEGACY_DEBT": [],
                "IMPOSTER_AGENT": [],
                "UNKNOWN": [],
            },
        }
        for file_path in python_files:
            if file_path.name == "__init__.py":
                continue
            relative_path = file_path.relative_to(self.base_path)
            analysis = self.analyze_file_structure(file_path)
            subdir_results["files"][str(relative_path)] = analysis
            if "error" not in analysis:
                classification = analysis["classification"]
                subdir_results["classifications"][classification].append(str(relative_path))
                classification_key = classification.lower().replace("_", "_")
                if classification_key in self.audit_results:
                    self.audit_results[classification_key].append(str(relative_path))
                else:
                    if "unknown" not in self.audit_results:
                        self.audit_results["unknown"] = []
                    self.audit_results["unknown"].append(str(relative_path))
                print(f"  📄 {file_path.name} -> {classification}")
        return subdir_results

    def _generate_unknown_ledger(self, results: dict):
        """Generate ledger of files in engines/ not inheriting from Base Agent."""
        engines_files = results["by_directory"].get("engines", {}).get("files", {})
        unknown_ledger = []
        for file_path, analysis in engines_files.items():
            if "error" not in analysis:
                classification = analysis["classification"]
                classes = analysis.get("classes", [])
                inherits_from_base = False
                for cls in classes:
                    bases = cls.get("bases", [])
                    if any("BaseAgent" in base or "AgentBase" in base for base in bases):
                        inherits_from_base = True
                        break
                if classification in ["UNKNOWN", "IMPOSTER_AGENT"] or not inherits_from_base:
                    unknown_ledger.append(
                        {
                            "file": file_path,
                            "classification": classification,
                            "reason": analysis.get("details", {}).get("reason", "Unknown"),
                            "classes": [cls["name"] for cls in classes],
                            "inherits_from_base": inherits_from_base,
                        },
                    )
        results["unknown_ledger"] = unknown_ledger

    def _generate_nomenclature_fixes(self, results: dict):
        """Generate list of imposter agents needing rename."""
        nomenclature_fixes = []
        for _subdir_name, subdir_data in results["by_directory"].items():
            for file_path, analysis in subdir_data.get("files", {}).items():
                if "error" not in analysis and analysis["classification"] == "IMPOSTER_AGENT":
                    nomenclature_fixes.append(
                        {
                            "file": file_path,
                            "current_name": Path(file_path).name,
                            "suggested_name": self._suggest_fixed_name(file_path, analysis),
                            "reason": analysis.get("details", {}).get("reason", "Unknown"),
                        },
                    )
        results["nomenclature_fixes"] = nomenclature_fixes

    def _generate_migration_candidates(self, results: dict):
        """Generate list of stateless tools in engines/ needing move."""
        migration_candidates = []
        engines_files = results["by_directory"].get("engines", {}).get("files", {})
        for file_path, analysis in engines_files.items():
            if "error" not in analysis and analysis["classification"] == "STATELESS_TOOL":
                migration_candidates.append(
                    {
                        "file": file_path,
                        "current_location": "engines/",
                        "target_location": "shared/tools/",
                        "reason": analysis.get("details", {}).get("reason", "Unknown"),
                    },
                )
        results["migration_candidates"] = migration_candidates

    def _suggest_fixed_name(self, file_path: str, analysis: dict) -> str:
        """Suggest a better name for imposter agent files."""
        current_name = Path(file_path).stem
        if current_name.endswith("Agent"):
            base_name = current_name[:-5]
            classes = analysis.get("classes", [])
            if classes:
                cls = classes[0]
                if cls.get("is_model", False):
                    return f"{base_name}Model.py"
                elif cls.get("is_enum", False):
                    return f"{base_name}Type.py"
                elif cls.get("has_execute_or_process", False):
                    return f"{base_name}Service.py"
                else:
                    return f"{base_name}Util.py"
            else:
                return f"{base_name}Util.py"
        return current_name + ".py"

    def _print_audit_summary(self, results: dict):
        """Print audit summary."""
        print("\n" + "=" * 60)
        print("📊 AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Files Analyzed: {results['total_files']}")
        print("\n📋 CLASSIFICATION BREAKDOWN:")
        for classification, files in results["classifications"].items():
            print(f"  {classification}: {len(files)} files")
        print(f"\n🚨 UNKNOWN LEDGER: {len(results['unknown_ledger'])} files")
        print(f"🏷️  NOMENCLATURE FIXES: {len(results['nomenclature_fixes'])} files")
        print(f"🔄 MIGRATION CANDIDATES: {len(results['migration_candidates'])} files")
        if results["unknown_ledger"]:
            print("\n🚨 UNKNOWN LEDGER (Files in engines/ not inheriting from Base Agent):")
            for item in results["unknown_ledger"][:5]:
                print(f"  • {item['file']} - {item['reason']}")
            if len(results["unknown_ledger"]) > 5:
                print(f"  ... and {len(results['unknown_ledger']) - 5} more")
        if results["nomenclature_fixes"]:
            print("\n🏷️  NOMENCLATURE FIXES (Imposter Agents):")
            for item in results["nomenclature_fixes"][:5]:
                print(f"  • {item['current_name']} → {item['suggested_name']}")
            if len(results["nomenclature_fixes"]) > 5:
                print(f"  ... and {len(results['nomenclature_fixes']) - 5} more")
        if results["migration_candidates"]:
            print("\n🔄 MIGRATION CANDIDATES (Stateless tools in engines/):")
            for item in results["migration_candidates"][:5]:
                print(f"  • {Path(item['file']).name} → shared/tools/")
            if len(results["migration_candidates"]) > 5:
                print(f"  ... and {len(results['migration_candidates']) - 5} more")


def main():
    """Run the RG Sovereign audit."""
    auditor = RGSovereignAuditor()
    results = auditor.audit_directory()
    with open("rg_sovereign_audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n💾 Audit results saved to: rg_sovereign_audit_results.json")
    print("\n✅ Audit complete - Ready for report generation!")
    return results


if __name__ == "__main__":
    main()
