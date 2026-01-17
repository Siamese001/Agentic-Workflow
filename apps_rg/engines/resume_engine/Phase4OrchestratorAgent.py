from __future__ import annotations
"""
GitOps & Advanced Mutation Module - Phase 4 Implementation

This module provides advanced mutation and GitOps capabilities:
- GitOpsManager: Healing branches, file backups, rollback
- ResilientMutator: Diff mode, AST validation, confidence-based retry
- ImportPatcher: Automatic import path updates
- ConversationalRepair: Multi-agent collective intelligence (AutoGen-style)
"""
from typing import Any, Optional, Protocol, Dict, List
from enum import Enum, auto
import time


import ast
import asyncio
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .context import ResumeEngineContext
from .learning import ConfidenceScorer
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin


class MutationMode(Enum):
    """Mutation output modes."""
    FULL_CODE = "full_code"
    UNIFIED_DIFF = "unified_diff"
    JSON_PATCH = "json_patch"


@dataclass
class FileBackup:
    """
    Backup of a file for rollback.
    
    Attributes:
        path: File path
        content: File content snapshot
        hash: Content hash for verification
        timestamp: ISO timestamp of backup creation
    """
    path: str
    content: str
    hash: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MutationResult:
    """
    Result of a mutation operation.
    
    Attributes:
        success: Whether mutation succeeded
        original_content: Original file content
        mutated_content: Mutated file content
        attempts: Number of attempts made
        confidence: Confidence score (0-1)
        mode: Mutation mode used
        error: Optional error message
        diff_applied: Whether diff was successfully applied
    """
    success: bool
    original_content: str
    mutated_content: str
    attempts: int
    confidence: float
    mode: MutationMode
    error: Optional[str] = None
    diff_applied: bool = False


@dataclass
class RepairProposal:
    """
    A proposed repair from collective intelligence.
    
    Attributes:
        agent_name: Name of proposing agent
        proposal: Repair proposal text
        confidence: Confidence score (0-1)
        reasoning: Reasoning for the proposal
    """
    agent_name: str
    proposal: str
    confidence: float
    reasoning: str
    votes: int = 0


class GitOpsManager:
    """
    Manages Git operations for healing workflows.

    Features:
    - Healing branch creation
    - File backups with rollback
    - Compliant file writing with AST validation
    - Automatic commit on successful healing
    """

    def __init__(
        self,
        ctx: ResumeEngineContext,
        branch_prefix: str = "healing/resume",
        enable_git: bool = True,
    ):
        self.ctx = ctx
        self.branch_prefix = branch_prefix
        self.enable_git = enable_git

        # File backups for rollback
        self._backups: Dict[str, FileBackup] = {}

        # Current healing branch
        self._current_branch: Optional[str] = None
        self._original_branch: Optional[str] = None

        # Statistics
        self.files_modified = 0
        self.rollbacks_performed = 0

    def create_healing_branch(self) -> Optional[str]:
        """
        Create a new healing branch for this session.

        Returns:
            Branch name if created, None if git not available
        """
        if not self.enable_git:
            return None

        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return None

            self._original_branch = result.stdout.strip()

            # Create healing branch
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._current_branch = f"{self.branch_prefix}_{timestamp}"

            result = subprocess.run(
                ["git", "checkout", "-b", self._current_branch],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(f"   🌿 Created healing branch: {self._current_branch}")
                return self._current_branch

            return None

        except Exception as e:
            print(f"   ⚠️ Git branch creation failed: {e}")
            return None

    def backup_file(self, path: str) -> bool:
        """
        Create a backup of a file before modification.

        Args:
            path: Path to the file

        Returns:
            True if backup created
        """
        try:
            if not os.path.exists(path):
                return False

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            file_hash = hashlib.sha256(content.encode()).hexdigest()

            self._backups[path] = FileBackup(
                path=path,
                content=content,
                hash=file_hash,
            )

            return True

        except Exception:
            return False

    def rollback_file(self, path: str) -> bool:
        """
        Rollback a file to its backed up state.

        Args:
            path: Path to the file

        Returns:
            True if rollback successful
        """
        if path not in self._backups:
            return False

        try:
            backup = self._backups[path]

            with open(path, "w", encoding="utf-8") as f:
                f.write(backup.content)

            self.rollbacks_performed += 1
            print(f"   ⏪ Rolled back: {path}")

            return True

        except Exception as e:
            print(f"   ❌ Rollback failed for {path}: {e}")
            return False

    def rollback_all(self) -> int:
        """
        Rollback all backed up files.

        Returns:
            Number of files rolled back
        """
        count = 0
        for path in list(self._backups.keys()):
            if self.rollback_file(path):
                count += 1

        return count

    def write_compliant_file(
        self,
        path: str,
        content: str,
        validate_ast: bool = True,
        backup: bool = True,
    ) -> bool:
        """
        Write a file with compliance checks.

        Args:
            path: Path to write
            content: Content to write
            validate_ast: Validate Python syntax
            backup: Create backup before writing

        Returns:
            True if write successful
        """
        # Clean content
        clean_content = self._clean_llm_output(content)

        # AST validation for Python files
        if validate_ast and path.endswith(".py"):
            try:
                ast.parse(clean_content)
            except SyntaxError as e:
                print(f"   🛑 BLOCKED: Invalid syntax in {path}: {e}")
                return False

        # Create backup
        if backup and os.path.exists(path):
            self.backup_file(path)

        # Write file
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(clean_content)

            self.files_modified += 1
            return True

        except Exception as e:
            print(f"   ❌ Write failed for {path}: {e}")
            return False

    def _clean_llm_output(self, content: str) -> str:
        """Clean LLM output of markdown artifacts."""
        clean = content

        # Remove markdown code blocks
        if "```" in clean:
            clean = re.sub(r"```python\nimport logging\n\nLogger = logging.getLogger(__name__)\n", "", clean)
            clean = re.sub(r"```\n?", "", clean)

        return clean.strip()

    def commit_changes(self, message: str) -> bool:
        """
        Commit all changes on the healing branch.

        Args:
            message: Commit message

        Returns:
            True if commit successful
        """
        if not self.enable_git or not self._current_branch:
            return False

        try:
            # Stage all changes
            subprocess.run(
                ["git", "add", "-A"],
                capture_output=True,
                timeout=10,
            )

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(f"   ✅ Committed: {message}")
                return True

            return False

        except Exception:
            return False

    def merge_to_original(self) -> bool:
        """
        Merge healing branch back to original branch.

        Returns:
            True if merge successful
        """
        if not self.enable_git or not self._original_branch:
            return False

        try:
            # Checkout original
            subprocess.run(
                ["git", "checkout", self._original_branch],
                capture_output=True,
                timeout=10,
            )

            # Merge healing branch
            result = subprocess.run(
                ["git", "merge", self._current_branch],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(f"   ✅ Merged {self._current_branch} to {self._original_branch}")
                return True

            return False

        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get GitOps statistics."""
        return {
            "files_modified": self.files_modified,
            "files_backed_up": len(self._backups),
            "rollbacks_performed": self.rollbacks_performed,
            "current_branch": self._current_branch,
            "original_branch": self._original_branch,
            "git_enabled": self.enable_git,
        }


class ResilientMutator:
    """
    Resilient mutation with retry, confidence scoring, and diff support.

    Features:
    - Multiple mutation modes (full code, diff, JSON patch)
    - Confidence-based retry with logprobs
    - AST validation before applying
    - Pre-flight cleaning with formatters
    """

    def __init__(
        self,
        ctx: ResumeEngineContext,
        min_confidence: float = 0.7,
        max_attempts: int = 4,
    ):
        self.ctx = ctx
        self.min_confidence = min_confidence
        self.max_attempts = max_attempts

        self.confidence_scorer = ConfidenceScorer(min_confidence=min_confidence)

        # Statistics
        self.total_mutations = 0
        self.successful_mutations = 0
        self.failed_mutations = 0

    async def mutate(
        self,
        agent_name: str,
        Task: str,
        content: str,
        file_path: Optional[str] = None,
        mode: MutationMode = MutationMode.FULL_CODE,
    ) -> MutationResult:
        """
        Perform a resilient mutation.

        Args:
            agent_name: Name of the requesting agent
            Task: Task description for the mutation
            content: Original content to mutate
            file_path: Optional file path for context
            mode: Mutation output mode

        Returns:
            MutationResult with success status and content
        """
        self.total_mutations += 1

        # Pre-flight cleaning
        if file_path and os.path.exists(file_path):
            content = self._preflight_clean(file_path, content)

        # Build prompt based on mode
        prompt = self._build_prompt(Task, content, mode)

        best_result = None
        best_confidence = 0.0

        for attempt in range(1, self.max_attempts + 1):
            try:
                # Add retry context
                if attempt > 1:
                    prompt += f"\n[ATTEMPT {attempt}] Previous attempt failed. Fix errors."

                # Call LLM
                response = await self._call_llm(agent_name, prompt)

                if not response:
                    continue

                # Score confidence
                confidence = self.confidence_scorer.score_from_text(response)

                # Process response based on mode
                if mode == MutationMode.UNIFIED_DIFF:
                    mutated = self._apply_diff(content, response)
                    if mutated is None:
                        print(f"   [{agent_name}] ⚠️ Diff failed to apply. Retrying...")
                        continue
                else:
                    mutated = self._clean_llm_output(response)

                # AST validation for Python
                if file_path and file_path.endswith(".py"):
                    try:
                        ast.parse(mutated)
                    except SyntaxError as e:
                        print(f"   [{agent_name}] ⚠️ Syntax error: {e}. Retrying...")
                        continue

                # Track best result
                if confidence.score > best_confidence:
                    best_result = mutated
                    best_confidence = confidence.score

                # Return if confidence is high enough
                if confidence.score >= self.min_confidence:
                    self.successful_mutations += 1
                    return MutationResult(
                        success=True,
                        original_content=content,
                        mutated_content=mutated,
                        attempts=attempt,
                        confidence=confidence.score,
                        mode=mode,
                        diff_applied=mode == MutationMode.UNIFIED_DIFF,
                    )

            except Exception as e:
                print(f"   [{agent_name}] ⚠️ Attempt {attempt} error: {e}")
                if "429" in str(e):
                    await asyncio.sleep(2 ** attempt)

        # Return best result even if below threshold
        if best_result:
            self.successful_mutations += 1
            return MutationResult(
                success=True,
                original_content=content,
                mutated_content=best_result,
                attempts=self.max_attempts,
                confidence=best_confidence,
                mode=mode,
            )

        self.failed_mutations += 1
        return MutationResult(
            success=False,
            original_content=content,
            mutated_content=content,
            attempts=self.max_attempts,
            confidence=0.0,
            mode=mode,
            error="All attempts failed",
        )

    def _build_prompt(
        self,
        Task: str,
        content: str,
        mode: MutationMode,
    ) -> str:
        """Build the mutation prompt."""
        prompt = Task

        if mode == MutationMode.UNIFIED_DIFF:
            prompt += """

OUTPUT FORMAT: Unified Diff ONLY.
Headers: --- a/file
+++ b/file
Use @@ ... @@ hunks. NO MARKDOWN."""
        else:
            prompt += """

OUTPUT FORMAT: Full Python Code. NO MARKDOWN. NO BACKTICKS."""

        prompt += f"\n\nContent:\n{content[:4000]}"

        return prompt

    async def _call_llm(self, agent_name: str, prompt: str) -> Optional[str]:
        """Call the LLM for mutation."""
        if not self.ctx.intelligence_enabled:
            return None

        try:
            model = self.ctx.client.GenerativeModel(self.ctx.model_id)
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
            )
            return response.text

        except Exception as e:
            print(f"   [{agent_name}] ❌ LLM call failed: {e}")
            return None

    def _preflight_clean(self, file_path: str, content: str) -> str:
        """Run pre-flight cleaning on content."""
        try:
            # Try to run isort
            subprocess.run(
                [sys.executable, "-m", "isort", file_path, "--profile", "black"],
                capture_output=True,
                timeout=10,
            )

            # Reload content
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        except Exception:
            return content

    def _clean_llm_output(self, content: str) -> str:
        """Clean LLM output."""
        clean = content

        # Remove reasoning blocks
        clean = re.sub(r"<reasoning>.*?</reasoning>", "", clean, flags=re.DOTALL)

        # Extract from markdown code blocks
        code_match = re.search(r"```(?:python)?\n(.*?)```", clean, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # Strip backticks
        if clean.strip().startswith("```"):
            clean = clean.strip().strip("`").replace("python", "", 1).strip()

        return clean.strip()

    def _apply_diff(self, original: str, diff_text: str) -> Optional[str]:
        """Apply a unified diff to content."""
        try:
            diff_text = self._clean_llm_output(diff_text)
            diff_lines = diff_text.strip().splitlines()
            original_lines = original.splitlines(keepends=True)

            # Add headers if Missing
            if not diff_lines or not diff_lines[0].startswith("---"):
                diff_lines.insert(0, "--- a/file")
                diff_lines.insert(1, "+++ b/file")

            # Parse and apply hunks
            hunk_re = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
            new_lines = original_lines[:]
            i = 0

            # Skip headers
            while i < len(diff_lines) and not diff_lines[i].startswith("@@"):
                i += 1

            # Process hunks
            while i < len(diff_lines):
                line = diff_lines[i]
                if line.startswith("@@"):
                    m = hunk_re.match(line)
                    if not m:
                        return None

                    old_start = int(m.group(1)) - 1
                    old_len = int(m.group(2) or "1")

                    # Delete old lines
                    del new_lines[old_start:old_start + old_len]

                    # Collect additions
                    i += 1
                    added = []
                    while i < len(diff_lines) and not diff_lines[i].startswith("@@"):
                        if diff_lines[i].startswith("+"):
                            added.append(diff_lines[i][1:] + "\n")
                        i += 1

                    # Insert new lines
                    new_lines[old_start:old_start] = added
                    continue
                i += 1

            return "".join(new_lines)

        except Exception as e:
            print(f"   ❌ Diff application failed: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get mutation statistics."""
        return {
            "total_mutations": self.total_mutations,
            "successful_mutations": self.successful_mutations,
            "failed_mutations": self.failed_mutations,
            "success_rate": self.successful_mutations / max(1, self.total_mutations),
            "confidence_stats": self.confidence_scorer.get_stats(),
        }


class ImportPatcher:
    """
    Automatic import path updates after file changes.

    Features:
    - Build import dependency map
    - Patch imports after file moves
    - Handle module splits
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self._import_map: Dict[str, List[str]] = {}

    def build_import_map(self, files: List[str]) -> Dict[str, List[str]]:
        """
        Build a map of which files import which modules.

        Args:
            files: List of file paths to analyze

        Returns:
            Dict mapping module names to files that import them
        """
        import_map = {}

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module = alias.name.split(".")[0]
                            if module not in import_map:
                                import_map[module] = []
                            if file_path not in import_map[module]:
                                import_map[module].append(file_path)

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split(".")[0]
                            if module not in import_map:
                                import_map[module] = []
                            if file_path not in import_map[module]:
                                import_map[module].append(file_path)

            except Exception:
                continue

        self._import_map = import_map
        return import_map

    def get_affected_files(self, module_name: str) -> List[str]:
        """
        Get files that import a given module.

        Args:
            module_name: Name of the module

        Returns:
            List of file paths that import the module
        """
        return self._import_map.get(module_name, [])

    async def patch_imports(
        self,
        change_map: Dict[str, str],
        mutator: Optional[ResilientMutator] = None,
    ) -> int:
        """
        Patch imports after module changes.

        Args:
            change_map: Dict mapping old module paths to new paths
            mutator: Optional mutator for LLM-based patching

        Returns:
            Number of files patched
        """
        if not change_map:
            return 0

        patched = 0

        # Get all affected files
        affected_files = set()
        for old_module in change_map.keys():
            affected_files.update(self.get_affected_files(old_module))

        for file_path in affected_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = content

                # Simple string replacement for imports
                for old_module, new_module in change_map.items():
                    # Replace import statements
                    new_content = re.sub(
                        rf"from {re.escape(old_module)}",
                        f"from {new_module}",
                        new_content,
                    )
                    new_content = re.sub(
                        rf"import {re.escape(old_module)}",
                        f"import {new_module}",
                        new_content,
                    )

                if new_content != content:
                    # Validate syntax
                    try:
                        ast.parse(new_content)

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)

                        patched += 1
                        print(f"   ✅ Patched imports: {file_path}")

                    except SyntaxError:
                        print(f"   ⚠️ Skipped {file_path}: syntax error after patching")

            except Exception as e:
                print(f"   ❌ Failed to patch {file_path}: {e}")

        return patched

    def get_stats(self) -> Dict[str, Any]:
        """Get import patcher statistics."""
        return {
            "modules_tracked": len(self._import_map),
            "total_imports": sum(len(v) for v in self._import_map.values()),
        }


class ConversationalRepair:
    """
    Multi-agent conversational repair for complex issues.

    Simulates AutoGen-style group chat where multiple specialized
    agents debate and propose fixes.
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx

        # Agent personas
        self.agents = {
            "Sherlock": "Root-cause detective. Analyzes tracebacks and cross-file interactions.",
            "SafetyInspectorAgent": "Security enforcer. No eval/exec, no hardcoded secrets.",
            "DependencySentinelAgent": "Import fixer. Resolves circular dependencies and module paths.",
            "ArchitectureGovernor": "Structure enforcer. Ensures proper depth and atomicity.",
        }

        # Repair history
        self.repair_history: List[RepairProposal] = []

    async def repair(
        self,
        issue_description: str,
        affected_content: str,
        context: Optional[str] = None,
    ) -> Optional[str]:
        """
        Perform conversational repair on an issue.

        Args:
            issue_description: Description of the issue
            affected_content: Content that needs repair
            context: Additional context

        Returns:
            Repaired content or None if repair failed
        """
        if not self.ctx.intelligence_enabled:
            return None

        print(f"   🗣️ Initiating CONVERSATIONAL REPAIR...")

        proposals = []

        # Get proposals from each agent
        for agent_name, persona in self.agents.items():
            proposal = await self._get_agent_proposal(
                agent_name,
                persona,
                issue_description,
                affected_content,
                context,
            )

            if proposal:
                proposals.append(proposal)

        if not proposals:
            return None

        # Vote on proposals
        best_proposal = await self._vote_on_proposals(proposals, issue_description)

        if best_proposal:
            self.repair_history.append(best_proposal)
            return best_proposal.proposal

        return None

    async def _get_agent_proposal(
        self,
        agent_name: str,
        persona: str,
        issue: str,
        content: str,
        context: Optional[str],
    ) -> Optional[RepairProposal]:
        """Get a repair proposal from an agent."""
        try:
            prompt = f"""
Role: {agent_name} - {persona}

Issue: {issue}

Content to repair:
{content[:2000]}

{f"Context: {context}" if context else ""}

Propose a MINIMAL, SAFE fix. Return ONLY the corrected code.
No explanations, no markdown.
"""

            model = self.ctx.client.GenerativeModel(self.ctx.model_id)
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
            )

            proposal_text = response.text.strip()

            # Clean the proposal
            proposal_text = self._clean_proposal(proposal_text)

            # Validate syntax
            try:
                ast.parse(proposal_text)
            except SyntaxError:
                return None

            return RepairProposal(
                agent_name=agent_name,
                proposal=proposal_text,
                confidence=0.7,  # Default confidence
                reasoning=f"Proposed by {agent_name}",
            )

        except Exception as e:
            print(f"   [{agent_name}] ❌ Proposal failed: {e}")
            return None

    async def _vote_on_proposals(
        self,
        proposals: List[RepairProposal],
        issue: str,
    ) -> Optional[RepairProposal]:
        """Have agents vote on proposals."""
        if not proposals:
            return None

        if len(proposals) == 1:
            proposals[0].votes = 1
            return proposals[0]

        # Simple voting: each agent votes for the proposal most different from their own
        for proposal in proposals:
            # Count votes based on syntax validity and length
            try:
                ast.parse(proposal.proposal)
                proposal.votes += 1
            except SyntaxError:
                pass

            # Prefer shorter, more focused fixes
            if len(proposal.proposal) < 1000:
                proposal.votes += 1

        # Return highest voted
        proposals.sort(key=lambda p: p.votes, reverse=True)

        print(f"   🗳️ Best proposal from {proposals[0].agent_name} ({proposals[0].votes} votes)")

        return proposals[0]

    def _clean_proposal(self, content: str) -> str:
        """Clean a proposal of markdown artifacts."""
        clean = content

        # Remove markdown code blocks
        code_match = re.search(r"```(?:python)?\n(.*?)```", clean, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        if clean.startswith("```"):
            clean = clean.strip("`").replace("python", "", 1).strip()

        return clean.strip()

    def get_stats(self) -> Dict[str, Any]:
        """Get repair statistics."""
        return {
            "total_repairs": len(self.repair_history),
            "agents": list(self.agents.keys()),
            "repairs_by_agent": {
                agent: sum(1 for r in self.repair_history if r.agent_name == agent)
                for agent in self.agents
            },
        }


class Phase4OrchestratorAgent(MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin):
    """
    Orchestrates all Phase 4 components for advanced healing.

    Combines:
    - GitOps for branch management
    - Resilient mutation for code changes
    - Import patching for dependency updates
    - Conversational repair for complex issues
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx

        self.gitops = GitOpsManager(ctx)
        self.mutator = ResilientMutator(ctx)
        self.ImportPatcher = ImportPatcher(ctx)
        self.conversational = ConversationalRepair(ctx)

    async def heal_with_gitops(
        self,
        Task: str,
        content: str,
        file_path: Optional[str] = None,
        use_diff: bool = False,
        use_conversational: bool = False,
    ) -> MutationResult:
        """
        Perform healing with full GitOps support.

        Args:
            Task: Task description
            content: Content to heal
            file_path: Optional file path
            use_diff: Use diff mode
            use_conversational: Use conversational repair

        Returns:
            MutationResult
        """
        # Backup if file exists
        if file_path and os.path.exists(file_path):
            self.gitops.backup_file(file_path)

        # Try conversational repair for complex issues
        if use_conversational:
            repaired = await self.conversational.repair(
                issue_description=Task,
                affected_content=content,
            )

            if repaired:
                return MutationResult(
                    success=True,
                    original_content=content,
                    mutated_content=repaired,
                    attempts=1,
                    confidence=0.8,
                    mode=MutationMode.FULL_CODE,
                )

        # Standard mutation
        mode = MutationMode.UNIFIED_DIFF if use_diff else MutationMode.FULL_CODE

        result = await self.mutator.mutate(
            agent_name="Phase4OrchestratorAgent",
            Task=Task,
            content=content,
            file_path=file_path,
            mode=mode,
        )

        # Write if successful
        if result.success and file_path:
            if not self.gitops.write_compliant_file(file_path, result.mutated_content):
                # Rollback on write failure
                self.gitops.rollback_file(file_path)
                result.success = False
                result.error = "Write failed"

        return result

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components."""
        return {
            "gitops": self.gitops.get_stats(),
            "mutator": self.mutator.get_stats(),
            "ImportPatcher": self.ImportPatcher.get_stats(),
            "conversational": self.conversational.get_stats(),
        }

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
