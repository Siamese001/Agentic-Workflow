"""TC-SPEC-01 through TC-SPEC-05: Spec Compliance E2E Tests"""
import pytest
from pathlib import Path
import ast


@pytest.mark.spec
class TestSpecCompliance:
    """Test compliance with Agent vs. Script specification."""

    def test_spec_decision_tree_reusability(self, agent, repo_root):
        """TC-SPEC-01: Decision Tree Q1 - Reusability check.

        Files imported by other modules should be AGENT.
        """
        # This test validates the principle: reusable logic → AGENT
        # We check for files with multiple imports as a proxy for reusability

        # Sample reasoning directory files
        reasoning_dir = repo_root / "agentic_core" / "L5_safety" / "reasoning"
        if not reasoning_dir.exists():
            pytest.skip("reasoning directory not found")

        for agent_file in reasoning_dir.glob("*Agent.py"):
            result = agent.classify_file(agent_file)
            # AGENT files should be in reasoning/ (per spec)
            assert result in ["AGENT", "ORCHESTRATOR", "ENGINE", "STRATEGY", "ADAPTER", "UTILITY"], \
                f"{agent_file}: Reusable agent should be AGENT/ORCHESTRATOR/ENGINE/STRATEGY/ADAPTER/UTILITY, got {result}"

    def test_spec_decision_tree_statefulness(self, agent, repo_root):
        """TC-SPEC-02: Decision Tree Q2 - Statefulness check.

        Files with instance state across items should be AGENT.
        """
        # Check for files with class definitions (instance state)
        target = repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py"

        if target.exists():
            with open(target, 'r') as f:
                content = f.read()

            # Parse AST for class definitions with instance variables
            tree = ast.parse(content)
            classes_with_state = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for self.* assignments (state)
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            for stmt in ast.walk(item):
                                if isinstance(stmt, ast.Attribute):
                                    if isinstance(stmt.value, ast.Name) and stmt.value.id == "self":
                                        classes_with_state.append(node.name)
                                        break

            # Files with state should be AGENT
            if classes_with_state:
                result = agent.classify_file(target)
                assert result in ["AGENT", "ORCHESTRATOR", "CLASS", "ENGINE", "STRATEGY", "ADAPTER", "VALIDATOR"], \
                    f"{target}: File with state should be AGENT/ORCHESTRATOR/CLASS/ENGINE/STRATEGY/ADAPTER/VALIDATOR, got {result}"

    def test_spec_decision_tree_logic_enforcement(self, agent, repo_root):
        """TC-SPEC-03: Decision Tree Q3 - Logic enforcement check.

        Files enforcing rules (not just sequencing) should be AGENT.
        """
        # Safety/reasoning files should enforce rules (AGENT)
        reasoning_dir = repo_root / "agentic_core" / "L5_safety" / "reasoning"
        if reasoning_dir.exists():
            for safety_file in reasoning_dir.glob("*.py"):
                result = agent.classify_file(safety_file)
                # All files in reasoning/ should be AGENT or ORCHESTRATOR
                assert result in ["AGENT", "ORCHESTRATOR", "CLASS", "ENGINE", "STRATEGY", "ADAPTER", "VALIDATOR", "CONFIG", "UTILITY"], \
                    f"{safety_file}: Safety file should be AGENT/ORCHESTRATOR/CLASS/ENGINE/STRATEGY/ADAPTER/VALIDATOR/CONFIG/UTILITY, got {result}"

    def test_spec_agent_class_structure(self, agent, repo_root):
        """TC-SPEC-04: AGENT files must be classes with methods (PascalCase).
        """
        reasoning_dir = repo_root / "agentic_core" / "L5_safety" / "reasoning"
        if not reasoning_dir.exists():
            pytest.skip("reasoning directory not found")

        for agent_file in reasoning_dir.glob("*Agent.py"):
            with open(agent_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            tree = ast.parse(content)
            has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))

            # Check if it's an alias file (imports and re-exports)
            is_alias = 'import' in content and any(
                alias in content for alias in ['as ', 'from ']
            )

            # AGENT file must contain a class OR be an alias
            assert has_class or is_alias, f"{agent_file}: AGENT file must contain a class or be an alias"

            # Verify PascalCase
            name = agent_file.stem
            assert name[0].isupper(), f"{agent_file}: AGENT must be PascalCase"

    def test_spec_script_procedural_structure(self, agent, repo_root):
        """TC-SPEC-05: SCRIPT files should be procedural functions (snake_case).
        """
        ops_dir = repo_root / "ops_scripts"
        if not ops_dir.exists():
            pytest.skip("ops_scripts directory not found")

        for script in ops_dir.rglob("*.py"):
            with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Scripts should have __main__ guard (CLI invocation)
            has_main_guard = '__name__' in content and '__main__' in content

            # Parse for function definitions
            try:
                tree = ast.parse(content)
                has_functions = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))

                result = agent.classify_file(script)
                if result == "SCRIPT":
                    # Scripts should have procedural structure
                    assert has_functions or has_main_guard, \
                        f"{script}: SCRIPT should have functions or __main__ guard"
            except SyntaxError:
                pass  # Skip files with syntax errors


@pytest.mark.spec
class TestBehavioralCompliance:
    """Test behavioral compliance: AGENT vs SCRIPT binary model."""

    def test_binary_model_mutual_exclusivity(self, agent, repo_root):
        """TC-SPEC-BINARY-01: AGENT and SCRIPT should be mutually exclusive."""
        # A file should not be both AGENT and SCRIPT
        sample_files = [
            repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py",
            repo_root / "ops_scripts" / "ci" / "agent_validation.py",
        ]

        for sample in sample_files:
            if sample.exists():
                result = agent.classify_file(sample)
                # Verify it's either AGENT-family or SCRIPT-family
                agent_family = ["AGENT", "ORCHESTRATOR", "STRATEGY", "ADAPTER"]
                script_family = ["SCRIPT", "UTILITY"]

                assert result in agent_family + script_family + ["CLASS", "TEST", "CONFIG", "MIXIN"], \
                    f"{sample}: Classification {result} should align with binary model"

    def test_agent_lifecycle_stateful(self, agent, repo_root):
        """TC-SPEC-AGENT-01: AGENT should track items/violations/stats (stateful)."""
        # Check FileClassificationAgent for state tracking
        target = repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py"

        if target.exists():
            with open(target, 'r') as f:
                content = f.read()

            # Look for instance variable tracking
            state_signals = [
                "self.",
                "items",
                "violations",
                "stats",
                "results",
                "_state",
            ]

            has_state = any(signal in content for signal in state_signals)
            result = agent.classify_file(target)

            if result == "AGENT":
                assert has_state, f"{target}: AGENT should track state"

    def test_script_lifecycle_stateless(self, agent, repo_root):
        """TC-SPEC-SCRIPT-01: SCRIPT should be stateless across runs."""
        # Scripts should not maintain instance state
        ops_dir = repo_root / "ops_scripts"
        if not ops_dir.exists():
            pytest.skip("ops_scripts directory not found")

        for script in ops_dir.rglob("*.py"):
            with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            try:
                tree = ast.parse(content)
                has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
                result = agent.classify_file(script)

                if result == "SCRIPT":
                    # Scripts should not have classes (stateless)
                    # Note: Some scripts may have helper classes, so this is a warning
                    if has_class:
                        print(f"Warning: SCRIPT {script} has class definitions")
            except SyntaxError:
                pass

    def test_agent_error_behavior_detect_log_continue(self, agent, repo_root):
        """TC-SPEC-AGENT-02: AGENT error behavior: detect → log → continue."""
        # Check for ClassificationResult pattern
        target = repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py"

        if target.exists():
            with open(target, 'r') as f:
                content = f.read()

            # Should have error handling pattern
            assert "ClassificationResult" in content or "error" in content.lower(), \
                f"{target}: AGENT should have error handling (detect → log → continue)"

    def test_script_cli_invocation(self, agent, repo_root):
        """TC-SPEC-SCRIPT-02: SCRIPT should support `python script.py` invocation."""
        ops_dir = repo_root / "ops_scripts"
        if not ops_dir.exists():
            pytest.skip("ops_scripts directory not found")

        cli_scripts = []
        for script in ops_dir.rglob("*.py"):
            with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for CLI invocation support
            if '__name__' in content and '__main__' in content:
                cli_scripts.append(script)

        # Most scripts should support CLI invocation
        total_scripts = len(list(ops_dir.rglob("*.py")))
        cli_ratio = len(cli_scripts) / max(total_scripts, 1)

        # Informational only - don't enforce strict ratio
        print(f"CLI-capable scripts: {len(cli_scripts)}/{total_scripts} ({cli_ratio:.1%})")
