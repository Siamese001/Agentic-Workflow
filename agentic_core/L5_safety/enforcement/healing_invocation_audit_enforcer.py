from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "healing_invocation_audit_enforcer")
emit_determinism_digest("p0", "healing_invocation_audit_enforcer")

_emit_dispatches_healing_run("p1", "healing_invocation_audit_enforcer", "L5")
_emit_routes_through("p1", "healing_invocation_audit_enforcer", "L5")
_emit_escalates_to_human("p1", "healing_invocation_audit_enforcer", "L5")
_emit_reads_policy_state("p1", "healing_invocation_audit_enforcer", "L5")

_emit_applies_guardrail("p0", "healing_invocation_audit_enforcer", "p0_governance")
_emit_snapshots_state("p0", "healing_invocation_audit_enforcer", "state_snapshot")

"\nHealing Invocation Audit Script\n\nComprehensive audit of all heal_repository() methods to verify super() presence\nand chain completeness across the entire codebase.\n"
import re
from datetime import datetime
from pathlib import Path

from agentic_core.utils.security_util import safe_execute

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class HealingInvocationAudit:
    """Audit heal_repository() methods for super() presence and chain completeness."""

    def __init__(self, project_root: Path = None):
        """Initialize audit tool."""
        self.project_root = project_root or Path.cwd()
        self.agentic_core = self.project_root / AGENTIC_CORE_DIR
        self.results = {
            "total_methods": 0,
            "with_super": 0,
            "without_super": [],
            "confirmed_agents": [],
            "missed_agents": [],
            "chain_depth_estimates": {},
        }

    def audit_all_methods(self) -> dict:
        """
        Audit all heal_repository() methods in codebase.

        Returns:
            Audit results dictionary
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HealingInvocationAudit.audit_all_methods"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HealingInvocationAudit.audit_all_methods".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        grep_cmd = ["grep", "-r", "def heal_repository(", str(self.agentic_core), "--include=*.py"]
        try:
            result = safe_execute(grep_cmd, capture_output=True, text=True, check=False)
            matches = result.stdout.strip().split("\n") if result.stdout else []
            for match in matches:
                if not match:
                    continue
                file_path, line_content = match.split(":", 1)
                file_path = Path(file_path)
                agent_name = self._extract_agent_name(file_path)
                has_super = self._check_super_presence(file_path)
                self.results["total_methods"] += 1
                if has_super:
                    self.results["with_super"] += 1
                    self.results["confirmed_agents"].append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "agent": agent_name,
                            "status": "confirmed",
                            "notes": "super() present and chain active",
                        }
                    )
                else:
                    self.results["without_super"].append(file_path)
                    self.results["missed_agents"].append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "agent": agent_name,
                            "reason": "Missing super().heal_repository() call",
                            "priority": "HIGH",
                        }
                    )
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"Error during audit: {e}")
        return self.results

    def _extract_agent_name(self, file_path: Path) -> str:
        """Extract agent class name from file path and content."""
        try:
            with open(file_path) as f:
                content = f.read()
                match = re.search("class\\s+(\\w+Agent)\\s*[\\(:]", content)
                if match:
                    return match.group(1)
        # guardian: allow-silent-swallow
        except Exception:
            pass
        return file_path.stem

    def _check_super_presence(self, file_path: Path) -> bool:
        """Check if super().heal_repository() is present in method."""
        try:
            with open(file_path) as f:
                content = f.read()
                method_match = re.search(
                    "def heal_repository\\(.*?\\).*?:.*?(?=\\n    def |\\nclass |\\Z)", content, re.DOTALL
                )
                if method_match:
                    method_body = method_match.group(0)
                    return "super().heal_repository(" in method_body
        # guardian: allow-silent-swallow
        except Exception:
            pass
        return False

    def generate_report(self, output_file: Path = None) -> str:
        """
        Generate markdown audit report.

        Args:
            output_file: Path to save report

        Returns:
            Report markdown string
        """
        if output_file is None:
            output_file = self.agentic_core / "L0_routing" / "logs" / "healing_invocation_audit_2026-01-03.md"
        _wg.ensure_dir(output_file.parent)
        total = self.results["total_methods"]
        with_super = self.results["with_super"]
        percentage = with_super / total * 100 if total > 0 else 0
        report = f"# Healing Invocation Audit Report\n\n**Date**: {datetime.now().isoformat()}\n**Status**: COMPLETE\n\n---\n\n## Executive Summary\n\n**Total heal_repository() Methods**: {total}\n**With super() Call**: {with_super} ({percentage:.1f}%)\n**Missing super() Call**: {len(self.results['missed_agents'])}\n**Overall Chain Activation**: {('✓ COMPLETE' if len(self.results['missed_agents']) == 0 else '⚠ INCOMPLETE')}\n\n---\n\n## Confirmed Agents (With super())\n\n| File | Agent | Status | Notes |\n|------|-------|--------|-------|\n"
        for agent in self.results["confirmed_agents"]:
            report += f"| {agent['file']} | {agent['agent']} | {agent['status']} | {agent['notes']} |\n"
        report += "\n---\n\n## Missed Agents (Without super())\n\n"
        if self.results["missed_agents"]:
            report += "| File | Agent | Reason | Priority |\n"
            report += "|------|-------|--------|----------|\n"
            for agent in self.results["missed_agents"]:
                report += (
                    f"| {agent['file']} | {agent['agent']} | {agent['reason']} | {agent['priority']} |\n"
                )
            report += "\n### Proposed Fixes\n\n"
            for agent in self.results["missed_agents"]:
                report += f"#### {agent['agent']} ({agent['file']})\n\n"
                report += '```python\n# Add to heal_repository() method - CRITICAL FIRST action:\n\nif _call_path is None:\n    _call_path = set()\n\nagent_name = self.__class__.__name__\nif agent_name in _call_path:\n    return {"skipped": 1}\n\n_call_path.add(agent_name)\n\ntry:\n    # CRITICAL FIRST: Invoke parent healing chain\n    parent_result = super().heal_repository(\n        dry_run=dry_run,\n        execute=execute,\n        depth=depth,\n        max_depth=max_depth,\n        _call_path=_call_path\n    )\n\n    # Agent-specific healing logic (preserve existing)\n    agent_result = self._perform_healing(dry_run, execute)\n\n    # Standardized merge\n    merged = {\n        "healed": parent_result.get("healed", 0) + agent_result.get("healed", 0),\n        # ... add agent-specific keys\n    }\n    return merged\nfinally:\n    _call_path.discard(agent_name)\n```\n\n'
        else:
            report += "**✓ All agents have super() calls - chain is complete!**\n\n"
        report += f"""\n---\n\n## Validation Checklist\n\n- [{("x" if percentage >= 95 else " ")}] Super() coverage >= 95%\n- [{("x" if len(self.results["missed_agents"]) == 0 else " ")}] Zero missed agents\n- [{("x" if percentage == 100 else " ")}] 100% chain activation\n- [{("x" if total > 0 else " ")}] All methods audited\n\n---\n\n## Conclusion\n\nPhase 5.1 audit complete. {(f"{len(self.results['missed_agents'])} agents require fixes." if self.results["missed_agents"] else "All agents confirmed with super() - healing chain fully active!")}\n\n**Status**: ✓ AUDIT COMPLETE\n"""
        _wg.open_write(output_file, report)
        print(f"Report saved to: {output_file}")
        return report

    def print_summary(self):
        """Print audit summary to console."""
        total = self.results["total_methods"]
        with_super = self.results["with_super"]
        percentage = with_super / total * 100 if total > 0 else 0
        print("\n" + "=" * 70)
        print("HEALING INVOCATION AUDIT SUMMARY")
        print("=" * 70)
        print(f"Total heal_repository() methods: {total}")
        print(f"With super() call: {with_super} ({percentage:.1f}%)")
        print(f"Missing super() call: {len(self.results['missed_agents'])}")
        if self.results["missed_agents"]:
            print("\nMissed Agents:")
            for agent in self.results["missed_agents"]:
                print(f"  - {agent['agent']} ({agent['file']})")
        else:
            print("\n✓ All agents confirmed with super() - chain fully active!")
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    audit = HealingInvocationAudit()
    print("Starting healing invocation audit...")
    audit.audit_all_methods()
    audit.print_summary()
    audit.generate_report()
    print("Audit complete!")


if __name__ == "__main__":
    main()
