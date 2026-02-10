"""
Phase 33d: Global Healing Capability Audit

Scans agentic_core for all healer agents and generates an "Impotence Report"
identifying agents that detect violations but cannot fix them.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentAuditResult:
    """Audit result for a single agent."""

    class_name: str
    file_path: str
    has_heal_repository: bool = False
    has_fix_violation: bool = False
    has_fix_violations: bool = False
    has_perform_surgery: bool = False
    auto_fixable_true_count: int = 0
    auto_fixable_false_count: int = 0
    violation_types: list = field(default_factory=list)

    @property
    def verdict(self) -> str:
        """Determine agent status."""
        if not self.has_heal_repository:
            return "GHOST"
        has_fix_logic = self.has_fix_violation or self.has_fix_violations or self.has_perform_surgery
        if self.auto_fixable_true_count > 0 and (not has_fix_logic):
            return "IMPOTENT"
        if has_fix_logic:
            return "HARDENED"
        return "PASSIVE"


def audit_agent_file(py_file: Path, agentic_core: Path) -> list[AgentAuditResult]:
    """Audit a single Python file for healer agents."""
    results = []
    try:
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    # guardian: allow-silent-swallow
    except Exception:
        return results
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        result = AgentAuditResult(class_name=node.name, file_path=str(py_file.relative_to(agentic_core)))
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef):
                if item.name == "heal_repository":
                    result.has_heal_repository = True
                elif item.name == "_fix_violation":
                    result.has_fix_violation = True
                elif item.name == "_fix_violations":
                    result.has_fix_violations = True
                elif item.name == "_perform_code_surgery":
                    result.has_perform_surgery = True
            if isinstance(item, ast.keyword):
                if item.arg == "auto_fixable":
                    if isinstance(item.value, ast.Constant):
                        if item.value.value:
                            result.auto_fixable_true_count += 1
                        else:
                            result.auto_fixable_false_count += 1
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Attribute) and target.attr == "violation_type":
                        if isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
                            result.violation_types.append(item.value.value)
        if result.has_heal_repository:
            results.append(result)
    return results


def main():
    """Run the global healing capability audit."""
    agentic_core = Path("C:/Git/Agentic-Workflow/agentic_core")
    exclude_dirs = {"archives", "legacy_code", "__pycache__", ".sovereign_healing_backup"}
    all_results = []
    for py_file in agentic_core.rglob("*.py"):
        if any(ex in str(py_file) for ex in exclude_dirs):
            continue
        results = audit_agent_file(py_file, agentic_core)
        all_results.extend(results)
    verdict_order = {"IMPOTENT": 0, "GHOST": 1, "PASSIVE": 2, "HARDENED": 3}
    all_results.sort(key=lambda x: (verdict_order.get(x.verdict, 99), x.file_path))
    verdicts = {}
    for r in all_results:
        verdicts[r.verdict] = verdicts.get(r.verdict, 0) + 1
    for _v, _count in sorted(verdicts.items(), key=lambda x: verdict_order.get(x[0], 99)):
        pass
    for r in all_results:
        fix_logic = []
        if r.has_fix_violation:
            fix_logic.append("_fix_v")
        if r.has_fix_violations:
            fix_logic.append("_fix_vs")
        if r.has_perform_surgery:
            fix_logic.append("surgery")
        ",".join(fix_logic) if fix_logic else "NONE"
    impotent = [r for r in all_results if r.verdict == "IMPOTENT"]
    if impotent:
        for r in impotent:
            pass
    import_agents = [r for r in all_results if "Import" in r.class_name]
    for r in import_agents:
        pass


if __name__ == "__main__":
    main()
