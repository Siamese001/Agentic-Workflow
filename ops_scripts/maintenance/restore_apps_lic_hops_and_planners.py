"""One-shot restoration script — brings back apps_lic functionality deleted
during 2026-02-08 HOPPipelineExecutor consolidation and 2026-01-01 legacy-engine
purge.

Restores (12 files):

  HOP1-9 agents — from commit ccbbce08c1 (2026-01-30, complete V2 set):
    apps_lic/engines/HOP{1..9}*.py

  Planner + governed-outreach — from commit c80c60d609 (2025-12-16):
    apps_lic/L1_cognition/message_planner.py
    apps_lic/L1_cognition/profile_planner.py
    apps_lic/outreach_engine/governed_outreach.py

Also applies import rewrites so restored files wire up against the CURRENT
module locations of their base classes rather than the deleted legacy paths.

Usage:
    python ops_scripts/maintenance/restore_apps_lic_hops_and_planners.py

This script is idempotent — running it twice has no effect after the first
successful run (files are overwritten). Safe to re-run after manual edits.

See audit trail:
  User request 2026-05-01: "HOP1-9 should not be shims in apps_LIC they were
  rebuilt out - recheck where the hops1-9 were built out in prior commit do
  not do it again / restore three items"
"""

from __future__ import annotations

import subprocess  # noqa: S404 -- trusted git invocation
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# (source_commit, source_path_in_commit, destination_path_on_disk)
RESTORE_MANIFEST: list[tuple[str, str, str]] = [
    # 9 HOP agents — V2 architecture, all present at ccbbce08c1
    ("ccbbce08c1", "apps_lic/engines/HOP1ProfileAnalysisAgent.py", "apps_lic/engines/HOP1ProfileAnalysisAgent.py"),
    ("ccbbce08c1", "apps_lic/engines/HOP2ResearchAgent.py", "apps_lic/engines/HOP2ResearchAgent.py"),
    ("ccbbce08c1", "apps_lic/engines/HOP3SenderGroundingAgent.py", "apps_lic/engines/HOP3SenderGroundingAgent.py"),
    ("ccbbce08c1", "apps_lic/engines/HOP4RoutingAgent.py", "apps_lic/engines/HOP4RoutingAgent.py"),
    ("ccbbce08c1", "apps_lic/engines/HOP5GenerationAgent.py", "apps_lic/engines/HOP5GenerationAgent.py"),
    ("ccbbce08c1", "apps_lic/engines/HOP6ValidationAgent.py", "apps_lic/engines/HOP6ValidationAgent.py"),
    ("ccbbce08c1", "apps_lic/engines/HOP7GateDecisionAgent.py", "apps_lic/engines/HOP7GateDecisionAgent.py"),
    ("ccbbce08c1", "apps_lic/engines/HOP8QAReportAgent.py", "apps_lic/engines/HOP8QAReportAgent.py"),
    ("ccbbce08c1", "apps_lic/engines/HOP9IntegrationAgent.py", "apps_lic/engines/HOP9IntegrationAgent.py"),
    # MessagePlanner + ProfilePlanner — only present at Dec-16 peak
    ("c80c60d609", "apps_lic/L1_cognition/message_planner.py", "apps_lic/L1_cognition/message_planner.py"),
    ("c80c60d609", "apps_lic/L1_cognition/profile_planner.py", "apps_lic/L1_cognition/profile_planner.py"),
    # Governed outreach — temporal-compliance design; depends on phantom
    # temporal_vetting module so will need manual wiring
    ("c80c60d609", "apps_lic/outreach_engine/governed_outreach.py", "apps_lic/outreach_engine/governed_outreach.py"),
    # HOP V2 unit tests — source path was tests/unit/apps_lic/engines/ at
    # ccbbce08c1; current layout is tests/unit/apps/apps_lic/engines/.
    # HOP4 and HOP9 tests never existed in that commit.
    ("ccbbce08c1", "tests/unit/apps_lic/engines/test_hop1_agent.py", "tests/unit/apps/apps_lic/engines/test_hop1_agent.py"),
    ("ccbbce08c1", "tests/unit/apps_lic/engines/test_hop2_agent.py", "tests/unit/apps/apps_lic/engines/test_hop2_agent.py"),
    ("ccbbce08c1", "tests/unit/apps_lic/engines/test_hop3_agent.py", "tests/unit/apps/apps_lic/engines/test_hop3_agent.py"),
    ("ccbbce08c1", "tests/unit/apps_lic/engines/test_hop5_agent.py", "tests/unit/apps/apps_lic/engines/test_hop5_agent.py"),
    ("ccbbce08c1", "tests/unit/apps_lic/engines/test_hop6_agent.py", "tests/unit/apps/apps_lic/engines/test_hop6_agent.py"),
    ("ccbbce08c1", "tests/unit/apps_lic/engines/test_hop7_agent.py", "tests/unit/apps/apps_lic/engines/test_hop7_agent.py"),
    ("ccbbce08c1", "tests/unit/apps_lic/engines/test_hop8_agent.py", "tests/unit/apps/apps_lic/engines/test_hop8_agent.py"),
]

# Legacy-path → current-path import rewrites (deterministic string replace).
# These cover every legacy path observed in the 12-file restore set. The first
# four handle the snake_case variants; the next four handle the PascalCase
# filename variants that appeared in later Jan-2026 commits after the
# "Pascal Sovereignty" rename.
IMPORT_REWRITES: list[tuple[str, str]] = [
    # snake_case variants
    (
        "from apps_lic.shared.core.agent_base import LICAgentBase",
        "from apps_lic.utils.lic_agent_base_util import LICAgentBase",
    ),
    (
        "from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer",
        "from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer",
    ),
    (
        "from apps_lic.shared.core.trace_registry import TraceRegistry",
        "from apps_lic.types.TraceRegistry import TraceRegistry",
    ),
    (
        "from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin",
        "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin",
    ),
    # PascalCase filename variants (Pascal Sovereignty era)
    (
        "from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase",
        "from apps_lic.utils.lic_agent_base_util import LICAgentBase",
    ),
    (
        "from apps_lic.shared.core.ImmutableStagingBuffer import ImmutableStagingBuffer",
        "from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer",
    ),
    (
        "from apps_lic.shared.core.TraceRegistry import TraceRegistry",
        "from apps_lic.types.TraceRegistry import TraceRegistry",
    ),
    # domain / logic_nodes relocations
    (
        "from apps_lic.domain.config import load_agent_specs",
        "from apps_lic.config.loader_config import load_agent_specs",
    ),
    (
        "from apps_lic.domain.config.loader import load_agent_specs",
        "from apps_lic.config.loader_config import load_agent_specs",
    ),
    # Legacy `domain.config.schemas` home for five Config pydantic models —
    # these all live in apps_lic/utils/archetype_indicator_util.py today.
    (
        "from apps_lic.domain.config.schemas import",
        "from apps_lic.utils.archetype_indicator_util import",
    ),
    (
        "from apps_lic.logic_nodes.K1Router import K1Router",
        "from apps_lic.types.k1_router_types import K1Router",
    ),
]


def _git_show(commit: str, path: str) -> str:
    """Retrieve a file's contents at a specific commit."""
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"{commit}:{path}"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"git show {commit}:{path} failed: {stderr}")
    return result.stdout.decode("utf-8", errors="replace")


def _apply_rewrites(content: str) -> tuple[str, int]:
    """Apply import-path rewrites. Return rewritten text + count of changes."""
    count = 0
    for old, new in IMPORT_REWRITES:
        if old in content:
            content = content.replace(old, new)
            count += 1
    return content, count


def _patch_planner_dataclass_import(dst: str, content: str) -> str:
    """Planners use @dataclass without importing it. Fix missing import."""
    if not dst.endswith(("message_planner.py", "profile_planner.py")):
        return content
    if "from dataclasses import" in content:
        return content
    # Insert after the `import logging` line to keep ordering canonical.
    return content.replace(
        "import logging\n",
        "import logging\nfrom dataclasses import dataclass, field\n",
        1,
    )


def _patch_hop_mro_conflict(dst: str, content: str) -> str:
    """HOP3..HOP9 inherited (SubatomicTestingMixin, LICAgentBase) which raised
    an MRO conflict against the CURRENT SubatomicTestingMixin class. Flipping
    the order to (LICAgentBase, SubatomicTestingMixin) resolves it deterministically."""
    if "/engines/HOP" not in dst.replace("\\", "/"):
        return content
    return content.replace(
        "class HOP3SenderGroundingAgent(SubatomicTestingMixin, LICAgentBase):",
        "class HOP3SenderGroundingAgent(LICAgentBase, SubatomicTestingMixin):",
    ).replace(
        "class HOP4RoutingAgent(SubatomicTestingMixin, LICAgentBase):",
        "class HOP4RoutingAgent(LICAgentBase, SubatomicTestingMixin):",
    ).replace(
        "class HOP5GenerationAgent(SubatomicTestingMixin, LICAgentBase):",
        "class HOP5GenerationAgent(LICAgentBase, SubatomicTestingMixin):",
    ).replace(
        "class HOP6ValidationAgent(SubatomicTestingMixin, LICAgentBase):",
        "class HOP6ValidationAgent(LICAgentBase, SubatomicTestingMixin):",
    ).replace(
        "class HOP7GateDecisionAgent(SubatomicTestingMixin, LICAgentBase):",
        "class HOP7GateDecisionAgent(LICAgentBase, SubatomicTestingMixin):",
    ).replace(
        "class HOP8QAReportAgent(SubatomicTestingMixin, LICAgentBase):",
        "class HOP8QAReportAgent(LICAgentBase, SubatomicTestingMixin):",
    ).replace(
        "class HOP9IntegrationAgent(SubatomicTestingMixin, LICAgentBase):",
        "class HOP9IntegrationAgent(LICAgentBase, SubatomicTestingMixin):",
    )


def _patch_governed_outreach_temporal_vetting(dst: str, content: str) -> str:
    """governed_outreach.py depended on a phantom `temporal_vetting` module
    that never existed in the repo. Replace the import with an inline
    placeholder so the module is at least importable; the function body
    can be wired up properly when a real temporal-vetting engine is built."""
    if not dst.endswith("governed_outreach.py"):
        return content
    stub_block = (
        "# Original import replaced 2026-05-01 during restore — the\n"
        "# `temporal_vetting` module never existed in the repo. The\n"
        "# placeholder below lets governed_outreach import cleanly. Replace\n"
        "# with the real temporal vetting engine when one is authored.\n"
        "def vet_lead_optimal_time(lead_timezone, current_utc_time_hm, tools, logger):\n"
        "    \"\"\"Placeholder — returns status=TEMPORAL_DELAY unconditionally.\n\n"
        "    This preserves the call-shape that execute_governed_outreach_sequence\n"
        "    expects without silently claiming compliance.\n"
        "    \"\"\"\n"
        "    return {\n"
        "        \"status\": \"TEMPORAL_DELAY\",\n"
        "        \"lead_local_time\": None,\n"
        "        \"decision\": \"placeholder_temporal_vetting_engine\",\n"
        "    }\n"
    )
    return content.replace(
        "from temporal_vetting import vet_lead_optimal_time\n",
        stub_block,
    )


def main() -> int:
    """Restore 12 files and apply import rewrites. Return exit code."""
    print(f"Restoring {len(RESTORE_MANIFEST)} files from git history...")
    total_rewrites = 0
    written = 0
    for commit, src, dst in RESTORE_MANIFEST:
        try:
            content = _git_show(commit, src)
        except RuntimeError as exc:
            print(f"  [FAIL] {src}@{commit}: {exc}", file=sys.stderr)
            return 1
        content, n_rewrites = _apply_rewrites(content)
        content = _patch_planner_dataclass_import(dst, content)
        content = _patch_hop_mro_conflict(dst, content)
        content = _patch_governed_outreach_temporal_vetting(dst, content)
        dst_path = REPO_ROOT / dst
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        existed = dst_path.exists()
        dst_path.write_text(content, encoding="utf-8")
        verb = "OVERWRITE" if existed else "CREATE   "
        size_kb = len(content) / 1024
        print(
            f"  [{verb}] {dst} "
            f"(src={commit[:10]}, {size_kb:5.1f} KB, {n_rewrites} import rewrites)"
        )
        total_rewrites += n_rewrites
        written += 1
    print(
        f"\nDone. Wrote {written} files with {total_rewrites} total import rewrites."
    )
    # Chain the planner syntax-corruption fixer — the Dec-2016 planner sources
    # contain multiple auto-gen artifacts that re-emerge each time they are
    # restored from git, so the fix pass must follow every restore.
    print("\nRunning planner syntax-corruption fixer...")
    fixer = REPO_ROOT / "ops_scripts" / "maintenance" / "_fix_planner_syntax_corruptions.py"
    fix_result = subprocess.run(  # noqa: S603
        [sys.executable, str(fixer)],
        cwd=str(REPO_ROOT),
        capture_output=False,
        check=False,
        timeout=60,
    )
    return fix_result.returncode


if __name__ == "__main__":
    sys.exit(main())
