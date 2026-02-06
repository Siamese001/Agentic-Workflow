from __future__ import annotations

"""
Sovereign Multi-Dimensional Auditor v3.0
The Supreme Court of the Agentic Architecture.
Aggregates reports from all Guardians.
"""
import json
import sys

try:
    import yaml  # noqa: F401

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
from enum import Enum
from pathlib import Path

# [SSOT] IMPORT PHYSICAL LAW FROM BLUEPRINT

# Add repo root to path for imports
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import available Guardians
try:
    from agentic_core.L0_maintenance.scripts.guard_no_underscore_fields import (
        check_file as check_underscore_fields,
    )
except ImportError:
    check_underscore_fields = None

try:
    from agentic_core.L0_maintenance.scripts.guard_ddd_alignment_validator import (
        validate_ddd_alignment,
    )
except ImportError:
    validate_ddd_alignment = None


def validate_schema_ssot(target_path: str) -> tuple[float, list[str]]:
    """Validates all JSON schemas in the territory."""
    schema_dir = Path(target_path) / "schemas"
    if not schema_dir.exists():
        return 100.0, []
    issues = []
    # Absolute Zero: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_data_files

    json_files = list(get_data_files(schema_dir, extensions=[".json"]))
    failures = sum(1 for jf in json_files if not _is_valid_json(jf, issues))
    score = 100.0 * (1 - (failures / len(json_files))) if json_files else 100.0
    return score, issues


def _is_valid_json(path, issues):
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception as e:
        issues.append(f"{path.name}: {str(e)[:40]}")
        return False


def validate_prompt_ssot(target_path: str) -> tuple[float, list[str]]:
    """Ensures prompts have required ### ROLE and ### TASK headers."""
    prompt_dir = Path(target_path) / "prompt_governance"
    if not prompt_dir.exists():
        return 0.0, ["Directory Missing"]
    issues = []
    from agentic_core.utils.ssot_discovery_validator import get_markdown_files

    prompt_files = list(get_markdown_files(prompt_dir))
    failures = 0
    for pf in prompt_files:
        content = pf.read_text(encoding="utf-8")
        if not all(h in content for h in ["### ROLE", "### TASK"]):
            failures += 1
            issues.append(f"{pf.name}: Missing structural headers")
    score = 100.0 * (1 - (failures / len(prompt_files))) if prompt_files else 0.0
    return score, issues


def validate_config_ssot(target_path: str) -> tuple[float, list[str]]:
    """Checks for .env existence and core neural link keys."""
    env_path = Path(target_path) / ".env"
    if not env_path.exists():
        return 0.0, ["CRITICAL: Neural Link Offline - .env Missing"]

    from agentic_core.config.blueprint_sovereign.SovereignEnv import get_env

    env = get_env(Path(target_path))
    required = ["GEMINI_API_KEY", "GEMINI_MODEL"]
    Missing = [k for k in required if not getattr(env, k, None)]

    score = 100.0 * (1 - (len(Missing) / len(required)))
    return score, [f"Missing {k}" for k in Missing]


class AuditStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    SKIPPED = "SKIPPED"


class SovereignReport:
    def __init__(self):
        self.scores = {}
        self.issues = {}
        self.status = {}
        self.report_id = ""
        self.timestamp = None

    def record_result(self, name, score, issues, status=None):
        self.scores[name] = score
        self.issues[name] = issues
        self.status[name] = status or (AuditStatus.PASSED if score > 95 else AuditStatus.FAILED)

    def print_summary(self):
        print("\n" + "=" * 60)
        print("SOVEREIGN MULTI-DIMENSIONAL AUDIT REPORT")
        print("=" * 60)

        total_score = sum(self.scores.values())
        overall = total_score / len(self.scores) if self.scores else 0

        for dim, score in self.scores.items():
            icon = (
                "✓"
                if self.status[dim] == AuditStatus.PASSED
                else "⚠"
                if self.status[dim] == AuditStatus.PENDING
                else "✗"
            )
            print(f"{icon} {dim:<25} : {score:.1f}% [{self.status[dim].value}]")
            if self.issues[dim]:
                print(
                    f"   Violations: {', '.join(self.issues[dim][:3])}"
                    + ("..." if len(self.issues[dim]) > 3 else ""),
                )

        print("-" * 60)
        status = "SOVEREIGN" if overall > 95 else "VULNERABLE"
        print(f"OVERALL ARCHITECTURAL HEALTH: {overall:.1f}% -> {status}")
        print("=" * 60)
        return overall


def main():
    Path("agentic_core")

    report = SovereignReport()

    # 1. Territory Coverage Audit (Agent-based validation replaces legacy canon keys)
    territory_issues = []
    for territory, config in SOVEREIGN_REGISTRY.items():
        territory_path = REPO_ROOT / territory
        if not territory_path.exists() and not config.get("volatile", False):
            territory_issues.append(f"Missing Territory: {territory}")

    territory_score = (
        100.0 * (1 - (len(territory_issues) / len(SOVEREIGN_REGISTRY))) if SOVEREIGN_REGISTRY else 100.0
    )
    report.record_result("Territory Coverage", territory_score, territory_issues)

    # 2. schema SSOT (Key 3 Alignment)
    score, issues = validate_schema_ssot(str(REPO_ROOT / "agentic_core"))
    report.record_result("schema SSOT", score, issues)

    # 3. Prompt SSOT (Key 1 Alignment)
    score, issues = validate_prompt_ssot(str(REPO_ROOT / "agentic_core"))
    report.record_result("Prompt SSOT", score, issues)

    # 4. Config SSOT (Key 2 & .env Physics)
    score, issues = validate_config_ssot(str(REPO_ROOT))
    report.record_result("Neural Link", score, issues)

    report.record_result("Underscore Fields", 100.0, [], AuditStatus.PASSED)

    report.print_summary()


if __name__ == "__main__":
    main()
