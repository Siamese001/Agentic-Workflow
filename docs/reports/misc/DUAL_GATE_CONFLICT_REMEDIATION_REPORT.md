# Dual-Gate Conflict Remediation Report

**Date:** 2026-01-22
**Issue:** Redundant terminal prompts caused by both agent-level and Gatekeeper-level approval checks
**Root Cause:** Multiple agents implement their own `_prompt_user_for_*_approval` methods while also calling `ArchivalGatekeeper.safe_move/safe_archive/safe_delete` which has its own approval mechanism

---

## Executive Summary

The `ArchivalGatekeeper` is designed to be the **Single Point of Approval** for all destructive file operations. However, 4 agents have implemented their own approval methods, creating a "Dual-Gate Conflict" where:

1. The agent prompts the user for approval
2. Then calls the Gatekeeper, which prompts again (unless env vars are set)

This leads to:
- Redundant terminal prompts in interactive mode
- Inconsistent behavior when `--yes` flag is passed
- Potential for one gate being open while the other is closed

---

## Affected Agents

| Agent | File | Dual-Gate Methods | Severity |
|-------|------|-------------------|----------|
| **LocationHealerAgent** | `L5_safety/validators/LocationHealerAgent.py` | `_prompt_user_for_archive_approval` | HIGH |
| **FilesystemSSOTReconcilerAgent** | `L5_safety/validators/FilesystemSSOTReconcilerAgent.py` | `_prompt_user_for_archive_approval` | HIGH |
| **GovernanceAgent** | `L5_safety/validators/GovernanceAgent.py` | `_prompt_user_for_move_approval` | MEDIUM |
| **SSOTRelocator** | `L5_safety/validators/ssot_relocator.py` | `_prompt_user_for_move_approval` | HIGH |

---

## Detailed Analysis

### 1. LocationHealerAgent.py

**Location:** `agentic_core/L5_safety/validators/LocationHealerAgent.py`

**Problem:** Lines 521-544 implement `_prompt_user_for_archive_approval` which checks `SOVEREIGN_AUTO_APPROVE` and `ARCHIVE_BATCH_ACCEPT`, then calls a non-existent `gatekeeper.safe_operation()` method.

**Dual-Gate Pattern:**
```python
# Line 506: Agent checks approval first
approval = self._prompt_user_for_archive_approval(file_path, target_path, msg)
if not approval:
    return {...}

# Line 514: Then calls Gatekeeper which checks approval again
move_result = self.safe_move(file_path, target_path, dry_run=dry_run)
```

**Additional Issues:**
- Line 544 calls `self.gatekeeper.safe_operation("archive", ...)` which doesn't exist
- Lines 682-688 have raw `input()` calls in `_heal_void_violation`
- Lines 746-747 have raw `input()` calls in `_relocate_to_existing_subfolder`
- Lines 783 have raw `input()` calls in `_create_new_subfolder_and_update_ssot`

---

### 2. FilesystemSSOTReconcilerAgent.py

**Location:** `agentic_core/L5_safety/validators/FilesystemSSOTReconcilerAgent.py`

**Problem:** Lines 759-806 implement `_prompt_user_for_archive_approval` with raw `input()` calls.

**Dual-Gate Pattern:**
```python
# Line 736: Agent checks approval first
if not self._prompt_user_for_archive_approval(source, target, prop.get("reason", ...)):
    applied_logs.append(f"SKIPPED: {prop['source']} (user declined)")
    continue

# Line 744: Then calls Gatekeeper which checks approval again
gk_result = self.gatekeeper.safe_move(source, target, self.agent_name, "Archive unauthorized folder")
```

**Additional Issues:**
- Uses raw `input()` at line 796 instead of delegating to Gatekeeper
- Has `_skip_all_archives` flag at line 768 that duplicates Gatekeeper's batch mode

---

### 3. GovernanceAgent.py

**Location:** `agentic_core/L5_safety/validators/GovernanceAgent.py`

**Problem:** Lines 493-520 implement `_prompt_user_for_move_approval` which checks env vars, then calls non-existent `gatekeeper.safe_operation()`.

**Dual-Gate Pattern:**
```python
# Line 493-520: Agent has its own approval method
def _prompt_user_for_move_approval(self, source: Path, target: Path, reason: str) -> bool:
    if os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1":
        return True
    if os.environ.get("ARCHIVE_BATCH_ACCEPT") == "1":
        return True
    return self.gatekeeper.safe_operation("move", f"{source} -> {target}")  # DOESN'T EXIST!
```

**Note:** This agent already delegates to Gatekeeper in `_sanitize_root_file` (lines 479-491) correctly. The `_prompt_user_for_move_approval` method appears to be dead code but should be removed for clarity.

---

### 4. SSOTRelocator (ssot_relocator.py)

**Location:** `agentic_core/L5_safety/validators/ssot_relocator.py`

**Problem:** Lines 122-174 implement `_prompt_user_for_move_approval` with raw `input()` calls and `_skip_all_moves`/`_approve_all_moves` flags.

**Dual-Gate Pattern:**
```python
# Lines 119-120: Agent has its own approval flags
self._skip_all_moves = False
self._approve_all_moves = False

# Line 122-174: Agent has its own approval method with raw input()
def _prompt_user_for_move_approval(self, source: Path, target: Path, reason: str) -> bool:
    if self._approve_all_moves:
        return True
    if self._skip_all_moves:
        return False
    # ... raw input() call at line 161
```

**Note:** The `_relocate_file` and `_relocate_folder` methods (lines 318-436) already correctly delegate to Gatekeeper and check `gk_result.approval_status == "DENIED"`. The `_prompt_user_for_move_approval` method is **dead code** and should be removed.

---

## Implementation Plan

### Phase 1: Remove Dead Code (Low Risk)

Remove unused `_prompt_user_for_*_approval` methods and related flags from agents that already correctly delegate to Gatekeeper.

| Agent | Action | Risk |
|-------|--------|------|
| SSOTRelocator | Delete `_prompt_user_for_move_approval`, `_skip_all_moves`, `_approve_all_moves` | LOW |
| GovernanceAgent | Delete `_prompt_user_for_move_approval` | LOW |

### Phase 2: Refactor Active Dual-Gates (Medium Risk)

Update agents that actively use dual-gate patterns to delegate entirely to Gatekeeper.

| Agent | Action | Risk |
|-------|--------|------|
| LocationHealerAgent | Remove `_prompt_user_for_archive_approval`, update `_heal_via_archiving` | MEDIUM |
| FilesystemSSOTReconcilerAgent | Remove `_prompt_user_for_archive_approval`, update `_apply_filesystem_alignment` | MEDIUM |

### Phase 3: Fix Raw input() Calls (High Risk)

Replace raw `input()` calls with Gatekeeper delegation or proper non-interactive handling.

| Agent | Location | Action |
|-------|----------|--------|
| LocationHealerAgent | `_heal_void_violation` (line 683) | Add env var check before input() |
| LocationHealerAgent | `_relocate_to_existing_subfolder` (line 747) | Add env var check before input() |
| LocationHealerAgent | `_create_new_subfolder_and_update_ssot` (line 783) | Add env var check before input() |

---

## File Diffs

### 1. SSOTRelocator (ssot_relocator.py)

```diff
@@ -115,56 +115,6 @@
         # Initialize ArchivalGatekeeper for safe file operations
         self.gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)

-        # Approval flags (deprecated - now handled by ArchivalGatekeeper)
-        self._skip_all_moves = False
-        self._approve_all_moves = False
-
-    def _prompt_user_for_move_approval(self, source: Path, target: Path, reason: str) -> bool:
-        """Prompt user for approval before moving a file/folder.
-
-        CRITICAL: All moves require explicit user approval.
-
-        Returns:
-            True if user approves, False otherwise
-        """
-        # Check for approve-all flag
-        if self._approve_all_moves:
-            return True
-
-        # Check for skip-all flag
-        if self._skip_all_moves:
-            return False
-
-        # Check if we're in a non-interactive environment
-        import sys
-
-        if not sys.stdin.isatty():
-            logger.warning(f"[SSOTRelocator] Non-interactive mode - skipping move: {source.name}")
-            return False
-
-        try:
-            rel_source = source.relative_to(self.project_root)
-            rel_target = target.relative_to(self.project_root)
-        except ValueError:
-            rel_source = source
-            rel_target = target
-
-        print(f"\n{'=' * 60}")
-        print("MOVE APPROVAL REQUIRED")
-        print(f"{'=' * 60}")
-        print(f"Source: {rel_source}")
-        print(f"Target: {rel_target}")
-        print(f"Reason: {reason}")
-        print(f"{'=' * 60}")
-
-        try:
-            response = input("Approve? [y/n/a(ll)/s(kip all)]: ").strip().lower()
-            if response == "y":
-                return True
-            elif response == "a":
-                self._approve_all_moves = True
-                return True
-            elif response == "s":
-                self._skip_all_moves = True
-                return False
-            else:
-                return False
-        except (EOFError, KeyboardInterrupt):
-            print("\nMove cancelled by user")
-            return False
-
     def relocate_orphans(self, drift_violations: list[Any]) -> EnforcementReport:
```

### 2. GovernanceAgent.py

```diff
@@ -490,32 +490,6 @@
             except Exception as e:
                 LOGGER.error(f"Failed to move {file_path}: {e}")
                 return "FAILED to move"
-
-    def _prompt_user_for_move_approval(self, source: Path, target: Path, reason: str) -> bool:
-        """
-        Prompt user for approval before moving a file.
-
-        [BATCH 1 REMEDIATION] Delegates to ArchivalGatekeeper which respects
-        SOVEREIGN_AUTO_APPROVE and ARCHIVE_BATCH_ACCEPT environment variables.
-
-        Args:
-            source: Source file path
-            target: Target file path
-            reason: Reason for the move
-
-        Returns:
-            True if user approves, False otherwise
-        """
-        import os
-
-        # [REMEDIATION] Check sovereign auto-approve first
-        if os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1":
-            LOGGER.info(f"[GovernanceAgent] Auto-approved move: {source.name}")
-            return True
-
-        if os.environ.get("ARCHIVE_BATCH_ACCEPT") == "1":
-            LOGGER.info(f"[GovernanceAgent] Batch-approved move: {source.name}")
-            return True
-
-        # Delegate to gatekeeper for consistent approval handling
-        return self.gatekeeper.safe_operation("move", f"{source} -> {target}")

     def check_depth_law(self, file_path: str) -> str | None:
```

### 3. LocationHealerAgent.py

```diff
@@ -503,43 +503,17 @@
         subfolder = next(
             (sf for pattern, sf in ARCHIVE_SUBFOLDERS.items() if pattern in msg),
             DEFAULT_ARCHIVE_SUBFOLDER,
         )
         target_path = archives_root / subfolder / file_path.name

-        # SSOT COMPLIANCE: Archiving requires user approval
-        if not dry_run:
-            approval = self._prompt_user_for_archive_approval(file_path, target_path, msg)
-            if not approval:
-                return {
-                    "applied": False,
-                    "action_taken": "SKIPPED: User declined archive operation",
-                    "requires_approval": True,
-                }
-
+        # [PHASE 33j] Gatekeeper is Single Point of Approval
         move_result = self.safe_move(file_path, target_path, dry_run=dry_run)
         if "MOVED" in move_result.get("action_taken", ""):
             move_result["action_taken"] = move_result["action_taken"].replace("MOVED", "ARCHIVED")
+        if move_result.get("applied") is False and "DENIED" in str(move_result.get("error", "")):
+            move_result["action_taken"] = "SKIPPED: User declined archive operation"
+            move_result["requires_approval"] = True
         if move_result.get("applied") and not dry_run:
             affected_paths.extend([file_path, target_path])
         return move_result
-
-    def _prompt_user_for_archive_approval(
-        self, file_path: Path, target_path: Path, reason: str
-    ) -> bool:
-        """Prompt user for approval before archiving a file.
-
-        [BATCH 1 REMEDIATION] Delegates to ArchivalGatekeeper which respects
-        SOVEREIGN_AUTO_APPROVE and ARCHIVE_BATCH_ACCEPT environment variables.
-
-        Returns:
-            True if user approves, False otherwise
-        """
-        import os
-
-        # [REMEDIATION] Check sovereign auto-approve first
-        if os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1":
-            Logger.info(f"[LocationHealerAgent] Auto-approved archive: {file_path.name}")
-            return True
-
-        if os.environ.get("ARCHIVE_BATCH_ACCEPT") == "1":
-            Logger.info(f"[LocationHealerAgent] Batch-approved archive: {file_path.name}")
-            return True
-
-        # Delegate to gatekeeper for consistent approval handling
-        return self.gatekeeper.safe_operation("archive", f"{file_path} -> {target_path}")
```

### 4. FilesystemSSOTReconcilerAgent.py

```diff
@@ -731,19 +731,17 @@
             elif prop["action"] == "ARCHIVE_UNAUTHORIZED":
                 source = Path(prop["source"])
                 target = Path(prop["target"])
                 if source.exists():
-                    # SSOT COMPLIANCE: Archiving requires user approval
-                    if not self._prompt_user_for_archive_approval(
-                        source, target, prop.get("reason", "Unauthorized folder")
-                    ):
-                        applied_logs.append(f"SKIPPED: {prop['source']} (user declined)")
-                        Logger.info(f"Skipped archive (user declined): {prop['source']}")
-                        continue
-
+                    # [PHASE 33j] Gatekeeper is Single Point of Approval
                     target.parent.mkdir(parents=True, exist_ok=True)
                     gk_result = self.gatekeeper.safe_move(
                         source, target, self.agent_name, "Archive unauthorized folder"
                     )
                     if gk_result.success:
                         applied_logs.append(f"ARCHIVED: {prop['source']} -> {prop['target']}")
                         Logger.info(
                             f"Archived unauthorized folder: {prop['source']} -> {prop['target']}"
                         )
+                    elif gk_result.approval_status == "DENIED":
+                        applied_logs.append(f"SKIPPED: {prop['source']} (user declined)")
+                        Logger.info(f"Skipped archive (user declined): {prop['source']}")
                     else:
                         applied_logs.append(f"FAILED: {prop['source']} - {gk_result.error}")
                         Logger.error(f"Failed to archive: {prop['source']} - {gk_result.error}")
@@ -756,49 +754,6 @@
         Logger.info(f"Filesystem alignment complete: {len(applied_logs)} actions applied")
         return applied_logs

-    def _prompt_user_for_archive_approval(self, source: Path, target: Path, reason: str) -> bool:
-        """Prompt user for approval before archiving a folder.
-
-        CRITICAL: Archiving requires explicit user approval.
-
-        Returns:
-            True if user approves, False otherwise
-        """
-        # Check for skip-all flag
-        if getattr(self, "_skip_all_archives", False):
-            return False
-
-        # Check if we're in a non-interactive environment
-        import sys
-
-        if not sys.stdin.isatty():
-            Logger.warning(
-                f"[FilesystemSSOTReconcilerAgent] Non-interactive mode - skipping archive: {source}"
-            )
-            return False
-
-        try:
-            rel_source = source.relative_to(self.project_root)
-            rel_target = target.relative_to(self.project_root)
-        except ValueError:
-            rel_source = source
-            rel_target = target
-
-        print(f"\n{'=' * 60}")
-        print("ARCHIVE APPROVAL REQUIRED")
-        print(f"{'=' * 60}")
-        print(f"Folder: {rel_source}")
-        print(f"Target: {rel_target}")
-        print(f"Reason: {reason}")
-        print(f"{'=' * 60}")
-
-        try:
-            response = input("Approve archive? [y/n/s(kip all)]: ").strip().lower()
-            if response == "y":
-                return True
-            elif response == "s":
-                self._skip_all_archives = True
-                return False
-            else:
-                return False
-        except (EOFError, KeyboardInterrupt):
-            print("\nArchive cancelled by user")
-            return False
-
     def _backup_blueprint(self) -> Path:
```

---

## Test Cases

### Test 1: Verify Single Prompt with --yes Flag

```python
# tests/unit/test_dual_gate_remediation.py

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

class TestDualGateRemediation:
    """Test that agents delegate approval to ArchivalGatekeeper without redundant prompts."""

    @pytest.fixture
    def setup_env(self):
        """Set up environment for auto-approval."""
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"
        yield
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)
        os.environ.pop("ARCHIVE_BATCH_ACCEPT", None)

    def test_hierarchy_agent_no_redundant_prompt(self, setup_env, tmp_path):
        """HierarchyAgent should not prompt when env vars are set."""
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        agent = HierarchyAgent(tmp_path, healing_enabled=True)

        # Verify no _prompt_user methods exist
        assert not hasattr(agent, '_prompt_user_for_move_approval')
        assert not hasattr(agent, '_prompt_user_for_archive_approval')

    def test_ssot_relocator_no_redundant_prompt(self, setup_env, tmp_path):
        """SSOTRelocator should not have its own approval methods."""
        from agentic_core.L5_safety.validators.ssot_relocator import SSOTRelocator

        relocator = SSOTRelocator(tmp_path, dry_run=True)

        # Verify no _prompt_user methods exist
        assert not hasattr(relocator, '_prompt_user_for_move_approval')
        assert not hasattr(relocator, '_skip_all_moves')
        assert not hasattr(relocator, '_approve_all_moves')

    def test_governance_agent_no_redundant_prompt(self, setup_env, tmp_path):
        """GovernanceAgent should not have its own approval methods."""
        from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent

        agent = GovernanceAgent(str(tmp_path))

        # Verify no _prompt_user methods exist
        assert not hasattr(agent, '_prompt_user_for_move_approval')

    def test_location_healer_no_redundant_prompt(self, setup_env, tmp_path):
        """LocationHealerAgent should not have its own approval methods."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

        agent = LocationHealerAgent(project_root=tmp_path)

        # Verify no _prompt_user methods exist
        assert not hasattr(agent, '_prompt_user_for_archive_approval')

    def test_filesystem_reconciler_no_redundant_prompt(self, setup_env, tmp_path):
        """FilesystemSSOTReconcilerAgent should not have its own approval methods."""
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
            FilesystemSSOTReconcilerAgent,
        )

        agent = FilesystemSSOTReconcilerAgent(tmp_path)

        # Verify no _prompt_user methods exist
        assert not hasattr(agent, '_prompt_user_for_archive_approval')
        assert not hasattr(agent, '_skip_all_archives')


class TestGatekeeperSinglePointOfApproval:
    """Test that ArchivalGatekeeper correctly handles approval."""

    @pytest.fixture
    def setup_env(self):
        """Set up environment for auto-approval."""
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"
        yield
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)
        os.environ.pop("ARCHIVE_BATCH_ACCEPT", None)

    def test_gatekeeper_batch_mode_with_sovereign_auto_approve(self, setup_env, tmp_path):
        """Gatekeeper should auto-approve when SOVEREIGN_AUTO_APPROVE=1."""
        from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(tmp_path)

        assert gk._is_batch_mode() is True

    def test_gatekeeper_batch_mode_with_archive_batch_accept(self, tmp_path):
        """Gatekeeper should auto-approve when ARCHIVE_BATCH_ACCEPT=1."""
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)

        from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(tmp_path)

        assert gk._is_batch_mode() is True

        os.environ.pop("ARCHIVE_BATCH_ACCEPT", None)

    def test_gatekeeper_no_batch_mode_without_env_vars(self, tmp_path):
        """Gatekeeper should require approval when no env vars set."""
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)
        os.environ.pop("ARCHIVE_BATCH_ACCEPT", None)

        from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(tmp_path)

        assert gk._is_batch_mode() is False


class TestEndToEndNoPrompts:
    """End-to-end tests verifying no prompts occur with --yes flag."""

    @pytest.fixture
    def setup_env(self):
        """Set up environment for auto-approval."""
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"
        os.environ["CI"] = "true"
        yield
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)
        os.environ.pop("ARCHIVE_BATCH_ACCEPT", None)
        os.environ.pop("CI", None)

    @patch('builtins.input')
    def test_hierarchy_agent_execute_no_input_called(self, mock_input, setup_env, tmp_path):
        """HierarchyAgent should never call input() when env vars are set."""
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

        ArchivalGatekeeper.reset_instance()

        # Create test structure
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)

        agent = HierarchyAgent(tmp_path, healing_enabled=True)
        agent.heal_hierarchy(execute=True, dry_run=False)

        # Verify input() was never called
        mock_input.assert_not_called()
```

---

## Verification Commands

After applying the fixes, run these commands to verify:

```bash
# 1. Syntax check all modified files
python -m py_compile agentic_core/L5_safety/validators/ssot_relocator.py
python -m py_compile agentic_core/L5_safety/validators/GovernanceAgent.py
python -m py_compile agentic_core/L5_safety/validators/LocationHealerAgent.py
python -m py_compile agentic_core/L5_safety/validators/FilesystemSSOTReconcilerAgent.py

# 2. Run the validator with --yes flag (should have NO prompts)
python canon_validator_agentic_v2_thin.py --agent hierarchy --execute --yes

# 3. Run the test suite
pytest tests/unit/test_dual_gate_remediation.py -v

# 4. Verify no remaining _prompt_user methods
grep -r "_prompt_user_for" agentic_core/L5_safety/validators/ --include="*.py"
```

---

## Risk Assessment

| Change | Risk Level | Rollback Plan |
|--------|------------|---------------|
| Remove dead code from SSOTRelocator | LOW | Git revert |
| Remove dead code from GovernanceAgent | LOW | Git revert |
| Refactor LocationHealerAgent | MEDIUM | Git revert, restore from backup |
| Refactor FilesystemSSOTReconcilerAgent | MEDIUM | Git revert, restore from backup |
| Fix raw input() calls | HIGH | Git revert, manual testing required |

---

## Conclusion

The Dual-Gate Conflict affects 4 agents in the codebase. The recommended approach is:

1. **Immediate:** Remove dead code from `SSOTRelocator` and `GovernanceAgent` (low risk)
2. **Short-term:** Refactor `LocationHealerAgent` and `FilesystemSSOTReconcilerAgent` to delegate entirely to Gatekeeper
3. **Medium-term:** Address raw `input()` calls in `LocationHealerAgent` interactive methods

The `ArchivalGatekeeper` already correctly implements the Single Point of Approval pattern with support for both `SOVEREIGN_AUTO_APPROVE` and `ARCHIVE_BATCH_ACCEPT` environment variables. The fix is to remove redundant approval logic from individual agents.
