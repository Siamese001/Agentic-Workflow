import pytest
import sys
from pathlib import Path

# Add the path to import structure_blueprint
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L5_safety" / "validators")
)
from structure_blueprint import ARTIFACT_ROUTING_MAP


# ============================================================================
# MOCK ROUTING ENGINE (The Logic under test)
# ============================================================================
def simulate_routing_decision(filename: str, content: str):
    """
    Simulates the 'Ultra-Hardened' routing logic to validate the Blueprint definitions.
    Returns: (best_destination, score, rejection_reasons)
    """
    best_dest = None
    best_score = 0.0
    rejections = []

    for destination, rules in ARTIFACT_ROUTING_MAP.items():
        score = 0.0

        # --- RULE 1: FORBIDDEN EXTENSIONS (The Iron Gate) ---
        if any(filename.endswith(ext) for ext in rules.get("forbidden_extensions", [])):
            rejections.append(f"{destination}: Forbidden Extension")
            continue

        # --- RULE 2: FORBIDDEN CONTENT (The Poison Pill) ---
        # fast fail if any forbidden keyword exists
        forbidden_hits = [k for k in rules.get("forbidden_keywords", []) if k in content]
        if forbidden_hits:
            rejections.append(f"{destination}: Forbidden Keywords {forbidden_hits}")
            continue

        # --- RULE 3: POSITIVE MATCHING ---

        # Extension Match
        if any(filename.endswith(ext) for ext in rules["file_extensions"]):
            score += 0.2
        else:
            continue  # Wrong extension type for this category

        # Naming Pattern Match
        if any(p.match(filename) for p in rules.get("naming_patterns", [])):
            score += 0.3

        # Content Signals
        signals = rules.get("content_signals", {})

        # Keywords
        hits = sum(1 for k in signals.get("keywords", []) if k in content)
        score += hits * 0.1

        # Headers/Keys
        headers = sum(1 for h in signals.get("headers", []) if h in content)
        score += headers * 0.2

        json_keys = sum(1 for k in signals.get("json_keys", []) if k in content)
        score += json_keys * 0.2

        if score > best_score:
            best_score = score
            best_dest = destination

    return best_dest, min(best_score, 1.0), rejections


# ============================================================================
# TEST SUITE
# ============================================================================
class TestArtifactRoutingLogic:
    # === SCENARIO 1: The "Trojan Horse" (Code masquerading as Log) ===
    def test_python_script_with_error_string_is_not_routed_to_logs(self):
        """
        CRITICAL: A Python script containing the string 'error' must NOT go to logs.
        It must go to scripts/ or stay put.
        """
        filename = "PascalSovereigntyFixer.py"
        content = """
        import sys
        def main():
            try:
                print("Fixing sovereignty...")
            except Exception as error:
                print(f"Critical error found: {error}")
        if __name__ == "__main__":
            main()
        """
        dest, score, rejections = simulate_routing_decision(filename, content)

        # Assert it definitely did NOT go to logs
        assert dest != "agentic_core/L0_maintenance/logs", (
            "FATAL: Python script leaked into Logs via 'error' keyword!"
        )

        # Assert it DID go to scripts
        assert dest == "agentic_core/L0_maintenance/scripts", (
            f"Expected scripts, got {dest}. Rejections: {rejections}"
        )

    # === SCENARIO 2: The "False Report" (Code named like a report) ===
    def test_audit_script_is_not_routed_to_docs(self):
        """
        A script named 'audit_report.py' should not go to docs/reports.
        """
        filename = "audit_report.py"
        content = "import pandas\ndef generate_audit(): pass"

        dest, score, rejections = simulate_routing_decision(filename, content)

        assert dest != "docs/reports", "FATAL: Code file routed to docs/reports based on filename!"
        assert "docs/reports: Forbidden Extension" in rejections

    # === SCENARIO 3: Strict Separation of Trace vs Debug Logs ===
    def test_trace_vs_debug_log_separation(self):
        """
        Verifies that 'Mission Traces' stay at Root (logs/)
        while 'Runtime Errors' go to Core (agentic_core/L0_maintenance/logs/).
        """
        # Case A: Mission Trace (Allowed in Root)
        trace_file = "trace_mission_alpha.jsonl"
        trace_content = '{"mission_id": "123", "step_count": 1, "agent_action": "think"}'

        dest_trace, _, _ = simulate_routing_decision(trace_file, trace_content)
        assert dest_trace == "logs", f"Mission Trace misrouted to {dest_trace}"

        # Case B: Runtime Error (Must go to Core)
        error_file = "app_crash.log"
        error_content = "ERROR: StackTrace\nException: NullPointer..."

        dest_err, _, _ = simulate_routing_decision(error_file, error_content)
        assert dest_err == "agentic_core/L0_maintenance/logs", f"Debug Log misrouted to {dest_err}"

    # === SCENARIO 4: Test Contamination Prevention ===
    def test_unit_tests_are_rejected_from_maintenance_scripts(self):
        """
        A file named 'test_healing.py' should NOT be grabbed by L0_maintenance/scripts.
        It belongs in tests/ (which is outside this map, so it should return None/No Route).
        """
        filename = "test_healing.py"
        content = "import pytest\ndef test_healing_logic(): assert True"

        dest, _, rejections = simulate_routing_decision(filename, content)

        # It should NOT match 'agentic_core/L0_maintenance/scripts' because of 'def test_' or 'import pytest'
        assert dest != "agentic_core/L0_maintenance/scripts", (
            "FATAL: Unit Test captured as Maintenance Script!"
        )

    # === SCENARIO 5: Core Agent Protection ===
    def test_core_agents_are_rejected_from_scripts(self):
        """
        A Sovereign Agent class definition should not be treated as a utility script.
        """
        filename = "SovereignHealer.py"
        content = "class SovereignHealer(CanonBaseAgent):\n    def heal(self): pass"

        dest, _, _ = simulate_routing_decision(filename, content)

        assert dest != "agentic_core/L0_maintenance/scripts", (
            "FATAL: Core Agent Class captured as Script!"
        )

    # === SCENARIO 6: Data vs Config ===
    def test_dataset_vs_config(self):
        """
        A JSON dataset should go to data/processed.
        A JSON config file (forbidden keywords) should stay put.
        """
        # Valid Dataset
        data_file = "sales_processed.json"
        data_content = '{"dataset_version": "1.0", "record_count": 500}'
        dest, _, _ = simulate_routing_decision(data_file, data_content)
        assert dest == "data/processed"

        # Config File (Should be rejected)
        config_file = "secrets.json"
        config_content = '{"api_key": "sk-123", "secret": "hidden"}'
        dest, _, _ = simulate_routing_decision(config_file, config_content)
        assert dest != "data/processed", "FATAL: Secrets/Config routed to Public Dataset folder!"

    # === SCENARIO 7: JavaScript Hardening ===
    def test_javascript_files_rejected_from_reports(self):
        """
        JavaScript files should not be routed to docs/reports even with report-like content.
        """
        filename = "audit_report.js"
        content = "function generateReport() { return '# Assessment'; }"

        dest, _, rejections = simulate_routing_decision(filename, content)

        assert dest != "docs/reports", "FATAL: JavaScript file routed to docs/reports!"
        assert "docs/reports: Forbidden Extension" in rejections

    # === SCENARIO 8: Shell Script Protection ===
    def test_shell_script_with_error_in_name(self):
        """
        Shell scripts containing 'error' should not go to maintenance logs.
        """
        filename = "error_handler.sh"
        content = "#!/bin/bash\necho 'Handling error...'"

        dest, _, rejections = simulate_routing_decision(filename, content)

        # Should not route to logs due to forbidden extension
        assert dest != "agentic_core/L0_maintenance/logs", (
            "FATAL: Shell script routed to maintenance logs!"
        )

    # === SCENARIO 9: Python Bytecode Exclusion ===
    def test_python_bytecode_files_excluded(self):
        """
        Compiled Python files (.pyc, .pyo) should be excluded from logs.
        """
        for ext in [".pyc", ".pyo"]:
            filename = f"module{ext}"
            content = "Bytecode content"

            dest, _, rejections = simulate_routing_decision(filename, content)

            assert dest != "agentic_core/L0_maintenance/logs", (
                f"FATAL: {ext} file routed to maintenance logs!"
            )

    # === SCENARIO 10: Mission Trace Integrity ===
    def test_mission_traces_reject_debug_content(self):
        """
        Mission traces should not contain debug/exception content.
        """
        filename = "trace_mission_beta.jsonl"
        content = '{"mission_id": "456", "Traceback": "Exception occurred"}'

        dest, _, rejections = simulate_routing_decision(filename, content)

        # Should be rejected from logs/ due to forbidden keyword "Traceback"
        assert dest != "logs", "FATAL: Mission trace with debug content not rejected!"

    # === SCENARIO 11: Argparse Script Detection ===
    def test_argparse_script_routing(self):
        """
        Scripts using argparse should be correctly routed to maintenance/scripts.
        """
        filename = "data_migrator.py"
        content = """
        import argparse
        def main():
            parser = argparse.ArgumentParser()
            args = parser.parse_args()
        if __name__ == "__main__":
            main()
        """

        dest, score, rejections = simulate_routing_decision(filename, content)

        assert dest == "agentic_core/L0_maintenance/scripts", (
            f"Argparse script not routed to maintenance: {dest}"
        )

    # === SCENARIO 12: Click/Typer Script Detection ===
    def test_click_script_routing(self):
        """
        Scripts using Click or Typer should be correctly routed.
        """
        for framework in ["click", "typer"]:
            filename = f"tool_{framework}.py"
            content = f"import {framework}\ndef cli(): pass"

            dest, _, _ = simulate_routing_decision(filename, content)

            assert dest == "agentic_core/L0_maintenance/scripts", (
                f"{framework} script not routed to maintenance"
            )

    # === SCENARIO 13: Report Content Without Code ===
    def test_valid_report_routing(self):
        """
        Valid reports (no code signals) should route correctly.
        """
        filename = "security_audit.md"
        content = """
        # Assessment
        ## Findings
        CRITICAL FAILURE: Authentication bypass
        ## Recommendations
        Fix the authentication layer
        """

        dest, score, _ = simulate_routing_decision(filename, content)

        assert dest == "docs/reports", f"Valid report not routed correctly: {dest}"
        assert score > 0.5, f"Report routing score too low: {score}"

    # === SCENARIO 14: Dataset Schema Validation ===
    def test_dataset_with_schema_version(self):
        """
        Datasets with schema_version should route correctly.
        """
        filename = "customer_data_processed.json"
        content = """
        {
            "dataset_version": "2.1",
            "record_count": 1000,
            "processed_at": "2026-01-27",
            "schema_version": "v1.0"
        }
        """

        dest, score, _ = simulate_routing_decision(filename, content)

        assert dest == "data/processed", f"Dataset not routed correctly: {dest}"
        assert score > 0.6, f"Dataset routing score too low: {score}"

    # === SCENARIO 15: Edge Case - Empty Content ===
    def test_empty_content_handling(self):
        """
        Files with empty content should rely on extension and name only.
        """
        # Empty Python file should still route to scripts
        filename = "empty_script.py"
        content = ""

        dest, score, _ = simulate_routing_decision(filename, content)

        # Should route to scripts based on .py extension and naming pattern
        assert dest == "agentic_core/L0_maintenance/scripts", (
            "Empty Python file not routed to scripts"
        )

    # === SCENARIO 16: Multiple Forbidden Signals ===
    def test_multiple_forbidden_signals(self):
        """
        Files with multiple forbidden signals should be rejected from all categories.
        """
        filename = "test_agent.py"
        content = """
        import pytest
        class TestAgent:
            def test_method(self):
                pass
        """

        dest, score, rejections = simulate_routing_decision(filename, content)

        # Should not route to scripts due to multiple forbidden signals
        assert dest != "agentic_core/L0_maintenance/scripts", (
            "File with multiple test signals routed to scripts!"
        )

        # Check that rejections were recorded
        assert any("Forbidden Keywords" in r for r in rejections), (
            "No forbidden keyword rejections recorded"
        )


# ============================================================================
# INTEGRATION TESTS - Validate Blueprint Structure
# ============================================================================
class TestBlueprintStructure:
    """Test that the ARTIFACT_ROUTING_MAP blueprint itself is correctly structured."""

    def test_all_categories_have_required_fields(self):
        """Every category must have required fields."""
        required_fields = ["description", "file_extensions", "content_signals"]

        for category, rules in ARTIFACT_ROUTING_MAP.items():
            for field in required_fields:
                assert field in rules, f"Category {category} missing required field: {field}"

    def test_forbidden_signals_exist(self):
        """All categories should have forbidden_signals for hardening."""
        for category, rules in ARTIFACT_ROUTING_MAP.items():
            has_forbidden = "forbidden_extensions" in rules or "forbidden_keywords" in rules
            assert has_forbidden, (
                f"Category {category} lacks forbidden signals (hardening weakness)"
            )

    def test_no_duplicate_extensions_between_forbidden_and_allowed(self):
        """Forbidden extensions should not appear in allowed extensions."""
        for category, rules in ARTIFACT_ROUTING_MAP.items():
            allowed = set(rules.get("file_extensions", []))
            forbidden = set(rules.get("forbidden_extensions", []))

            overlap = allowed & forbidden
            assert not overlap, (
                f"Category {category} has extensions in both allowed and forbidden: {overlap}"
            )


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
