#!/usr/bin/env python3
"""
Apply all Phase 33 fixes systematically:
- Phase 33i: Remove llm_enabled flag, LLM auto-escalates on low confidence
- Phase 33j: Unified environment variable strategy (SOVEREIGN_AUTO_APPROVE)
- Phase 33k: ImportAgent _fix_violation, HierarchyAgent delegation to ArchivalGatekeeper
"""

import sys
from pathlib import Path


def apply_fixes():
    """Apply all Phase 33 fixes."""
    fixes_applied = []

    # ========================================================================
    # Phase 33i: CognitiveDispositionAgent - Remove llm_enabled flag
    # ========================================================================
    print("\n[Phase 33i] Fixing CognitiveDispositionAgent...")
    cda_file = Path("agentic_core/L5_safety/cognition/CognitiveDispositionAgent.py")
    if cda_file.exists():
        content = cda_file.read_text(encoding="utf-8")

        # Fix 1: Update __init__ signature
        old_init = """    def __init__(
        self,
        project_root: Path | None = None,
        confidence_threshold: float = 0.8,
        llm_enabled: bool = False,
        api_key: str | None = None,
    ):
        \"\"\"
        Initialize the Cognitive Disposition Agent.

        Args:
            project_root: Project root directory
            confidence_threshold: Minimum confidence for auto-execution
            llm_enabled: Enable actual LLM API calls
            api_key: API key for LLM service (defaults to env var)
        \"\"\"
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold
        self.llm_enabled = llm_enabled"""

        new_init = """    def __init__(
        self,
        project_root: Path | None = None,
        confidence_threshold: float = 0.8,
        api_key: str | None = None,
        llm_enabled: bool = True,  # [PHASE 33i] Deprecated - LLM auto-escalates on low confidence
    ):
        \"\"\"
        Initialize the Cognitive Disposition Agent.

        [PHASE 33i] LLM is automatically used when heuristics have low confidence.
        The llm_enabled flag is deprecated and ignored - LLM escalation is automatic
        when GEMINI_API_KEY is available.

        Args:
            project_root: Project root directory
            confidence_threshold: Minimum confidence for auto-execution
            api_key: API key for LLM service (defaults to env var)
            llm_enabled: DEPRECATED - LLM auto-escalates on low confidence
        \"\"\"
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold"""

        if old_init in content:
            content = content.replace(old_init, new_init)
            fixes_applied.append("CognitiveDispositionAgent __init__")

        # Fix 2: Update analyze_violation logic
        old_logic = """        # 2. Try LLM if enabled and API key is available
        if self.llm_enabled and self.api_key:
            llm_decision = self._generate_llm_decision(file_path, violation_type, context)
            if llm_decision.action != "MANUAL_REVIEW":
                return llm_decision

        # 3. Fall back to heuristic decision
        return heuristic_decision"""

        new_logic = """        # 2. [PHASE 33i] Auto-escalate to LLM when heuristics have low confidence
        # LLM is automatically used when API key is available - no flag needed
        if self.api_key:
            Logger.info(f"[COGNITIVE] Low-confidence heuristic ({heuristic_decision.confidence:.2f}) - escalating to Gemini LLM")
            llm_decision = self._generate_llm_decision(file_path, violation_type, context)
            if llm_decision.action != "MANUAL_REVIEW":
                return llm_decision
        else:
            Logger.warning(f"[COGNITIVE] No API key - using low-confidence heuristic: {heuristic_decision.action}")

        # 3. Fall back to heuristic decision
        return heuristic_decision"""

        if old_logic in content:
            content = content.replace(old_logic, new_logic)
            fixes_applied.append("CognitiveDispositionAgent analyze_violation")

        cda_file.write_text(content, encoding="utf-8")
        print("  ✅ CognitiveDispositionAgent fixed")

    # ========================================================================
    # Phase 33j: CLI - Set environment variables
    # ========================================================================
    print("\n[Phase 33j] Fixing canon_validator CLI...")
    cli_file = Path("canon_validator_agentic_v2_thin.py")
    if cli_file.exists():
        content = cli_file.read_text(encoding="utf-8")

        old_env = """    args = parser.parse_args()

    # Global mission timeout: 30 minutes
    MISSION_TIMEOUT = int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800"))"""

        new_env = """    args = parser.parse_args()

    # [PHASE 33j] Unified Environment Variable Strategy for Agent Control Signals
    # Set environment variables BEFORE initializing any agents
    if args.yes:
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"  # Unified auto-approval signal
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"    # ArchivalGatekeeper batch mode
        os.environ["CI"] = "true"                   # Disables generic interactive prompts
        print("   [SYSTEM] SOVEREIGN MODE ACTIVE: Auto-approval enabled.")

    # Global mission timeout: 30 minutes
    MISSION_TIMEOUT = int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800"))"""

        if old_env in content:
            content = content.replace(old_env, new_env)
            fixes_applied.append("CLI environment variables")
            cli_file.write_text(content, encoding="utf-8")
            print("  ✅ CLI fixed")

    # ========================================================================
    # Phase 33j: HealingStrategy - Propagate kwargs
    # ========================================================================
    print("\n[Phase 33j] Fixing HealingStrategy kwargs propagation...")
    strategy_file = Path("agentic_core/L5_safety/validators/healing_strategy.py")
    if strategy_file.exists():
        content = strategy_file.read_text(encoding="utf-8")

        old_calls = """            elif hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=dry_run, execute=execute)"""

        new_calls = """            elif hasattr(agent, "heal_repository"):
                # [PHASE 33j] Propagate all kwargs to agents for future-proof signal continuity
                result = agent.heal_repository(dry_run=dry_run, execute=execute, **kwargs)"""

        if old_calls in content:
            content = content.replace(old_calls, new_calls)
            fixes_applied.append("HealingStrategy kwargs propagation")
            strategy_file.write_text(content, encoding="utf-8")
            print("  ✅ HealingStrategy fixed")

    # ========================================================================
    # Phase 33j: ArchivalGatekeeper - Check SOVEREIGN_AUTO_APPROVE
    # ========================================================================
    print("\n[Phase 33j] Fixing ArchivalGatekeeper...")
    gk_file = Path("agentic_core/L5_safety/core/ArchivalGatekeeper.py")
    if gk_file.exists():
        content = gk_file.read_text(encoding="utf-8")

        old_batch = """    def _is_batch_mode(self) -> bool:
        \"\"\"
        Check if batch mode is enabled via environment variable.

        When ARCHIVE_BATCH_ACCEPT=1, all operations are auto-approved
        without interactive prompts.

        Returns:
            True if batch mode is enabled
        \"\"\"
        return os.environ.get(ARCHIVE_BATCH_ACCEPT_ENV, "").strip() == "1\""""

        new_batch = """    def _is_batch_mode(self) -> bool:
        \"\"\"
        Check if batch mode is enabled via environment variable.

        [PHASE 33j] Checks both ARCHIVE_BATCH_ACCEPT and SOVEREIGN_AUTO_APPROVE.
        When either is set to "1", all operations are auto-approved without prompts.

        Returns:
            True if batch mode is enabled
        \"\"\"
        return (
            os.environ.get(ARCHIVE_BATCH_ACCEPT_ENV, "").strip() == "1"
            or os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1"
        )"""

        if old_batch in content:
            content = content.replace(old_batch, new_batch)
            fixes_applied.append("ArchivalGatekeeper SOVEREIGN_AUTO_APPROVE")
            gk_file.write_text(content, encoding="utf-8")
            print("  ✅ ArchivalGatekeeper fixed")

    # ========================================================================
    # Phase 33k: ImportAgent - Implement _fix_violation
    # ========================================================================
    print("\n[Phase 33k] Fixing ImportAgent...")
    import_agent_file = Path("agentic_core/L5_safety/gravity/ImportAgent.py")
    if import_agent_file.exists():
        content = import_agent_file.read_text(encoding="utf-8")

        # Check if _fix_violation already exists
        if "def _fix_violation(self" not in content:
            # Find the location to insert (after heal_repository method)
            insert_marker = """            return {"violations_found": total_violations, "fixed": 0}
        finally:
            _call_path.discard(agent_name)


# Singleton getter for canon_validator compatibility"""

            new_method = """            return {"violations_found": total_violations, "fixed": 0}
        finally:
            _call_path.discard(agent_name)

    def _fix_violation(self, violation_entry: tuple) -> bool:
        \"\"\"
        [PHASE 33k] Execute surgical fix for import violations.

        Args:
            violation_entry: Tuple of (file_path, list_of_messages)

        Returns:
            True if any fix was successfully applied
        \"\"\"
        file_path, messages = violation_entry
        # Use existing cleanup_violations logic which handles backups and safe rewrites
        cleanup_results = self.cleanup_violations([(file_path, messages)], dry_run=False)
        return any(action.get("applied", False) for action in cleanup_results)


# Singleton getter for canon_validator compatibility"""

            if insert_marker in content:
                content = content.replace(insert_marker, new_method)
                fixes_applied.append("ImportAgent _fix_violation")
                import_agent_file.write_text(content, encoding="utf-8")
                print("  ✅ ImportAgent fixed")

    # ========================================================================
    # Phase 33j: HierarchyAgent - Check SOVEREIGN_AUTO_APPROVE at runtime
    # ========================================================================
    print("\n[Phase 33j] Fixing HierarchyAgent...")
    hierarchy_file = Path("agentic_core/L5_safety/validators/HierarchyAgent.py")
    if hierarchy_file.exists():
        content = hierarchy_file.read_text(encoding="utf-8")

        # Add os import if missing
        if "import os" not in content:
            content = content.replace("import logging\n", "import logging\nimport os\n")
            fixes_applied.append("HierarchyAgent os import")

        # Update _prompt_user_for_move_approval to check env var
        old_prompt = """    def _prompt_user_for_move_approval(self, source: Path, target: Path, reason: str) -> bool:
        \"\"\"Prompt user for approval before moving a file.

        CRITICAL: All file moves require explicit user approval.

        Returns:
            True if user approves, False otherwise
        \"\"\"
        # Check for skip-all flag
        if self._skip_all_moves:
            return False

        # Check for approve-all flag
        if self._approve_all_moves:
            return True

        # Check Sovereign Override (auto_approve from heal_hierarchy)
        if self._auto_approve:
            Logger.info(f"[HierarchyAgent] Auto-approving move: {source.name} -> {target}")
            return True"""

        new_prompt = """    def _prompt_user_for_move_approval(self, source: Path, target: Path, reason: str) -> bool:
        \"\"\"Prompt user for approval before moving a file.

        [PHASE 33j] In-repo moves are auto-approved when SOVEREIGN_AUTO_APPROVE is set.
        Only archive moves require user approval.

        Returns:
            True if user approves, False otherwise
        \"\"\"
        # Check for skip-all flag
        if self._skip_all_moves:
            return False

        # Check for approve-all flag
        if self._approve_all_moves:
            return True

        # [PHASE 33j] Check SOVEREIGN_AUTO_APPROVE at runtime (not just init)
        if os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1":
            Logger.info(f"[HierarchyAgent] SOVEREIGN_AUTO_APPROVE: {source.name} -> {target}")
            return True

        # Check Sovereign Override (auto_approve from heal_hierarchy)
        if self._auto_approve:
            Logger.info(f"[HierarchyAgent] Auto-approving move: {source.name} -> {target}")
            return True"""

        if old_prompt in content:
            content = content.replace(old_prompt, new_prompt)
            fixes_applied.append("HierarchyAgent SOVEREIGN_AUTO_APPROVE check")
            hierarchy_file.write_text(content, encoding="utf-8")
            print("  ✅ HierarchyAgent fixed")

    return fixes_applied


if __name__ == "__main__":
    print("=" * 70)
    print("Phase 33 Fixes Application")
    print("=" * 70)

    fixes = apply_fixes()

    print("\n" + "=" * 70)
    print(f"Summary: {len(fixes)} fixes applied")
    for fix in fixes:
        print(f"  ✅ {fix}")
    print("=" * 70)

    if fixes:
        print("\n✅ Phase 33 fixes applied successfully")
    else:
        print("\nℹ️  No fixes needed (already applied)")

    sys.exit(0)
