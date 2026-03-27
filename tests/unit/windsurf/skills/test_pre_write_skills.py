#!/usr/bin/env python3
"""
Test suite for pre-write hooks skills.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest


class TestPreWriteSkills:
    """Test all pre-write hooks skills."""

    @pytest.fixture
    def skills_dir(self):
        """Get the skills directory."""
        return Path(".windsurf/skills")

    @pytest.fixture
    def all_skills(self, skills_dir):
        """Get all available skills."""
        skills = []
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "main.py").exists():
                skills.append(skill_dir.name)
        return skills

    def test_skill_directories_exist(self, skills_dir, all_skills):
        """Test that all skill directories exist and have required files."""
        for skill_name in all_skills:
            skill_dir = skills_dir / skill_name

            # Check main.py exists
            main_script = skill_dir / "main.py"
            assert main_script.exists(), f"{skill_name}: main.py missing"

            # Check skill.yaml exists
            config_file = skill_dir / "skill.yaml"
            assert config_file.exists(), f"{skill_name}: skill.yaml missing"

    def test_skill_syntax_valid(self, skills_dir, all_skills):
        """Test that all skills have valid Python syntax."""
        for skill_name in all_skills:
            main_script = skills_dir / skill_name / "main.py"

            result = subprocess.run(
                ["python", "-m", "py_compile", str(main_script)], capture_output=True, text=True, timeout=10
            )

            assert result.returncode == 0, f"{skill_name}: Syntax error - {result.stderr}"

    def test_skill_help_command(self, skills_dir, all_skills):
        """Test that all skills respond to --help or similar."""
        for skill_name in all_skills:
            main_script = skills_dir / skill_name / "main.py"

            # Try --help first
            result = subprocess.run(
                ["python", str(main_script), "--help"], capture_output=True, text=True, timeout=5
            )

            # If --help doesn't work, try -h or no args
            if result.returncode not in [0, 1]:
                result = subprocess.run(
                    ["python", str(main_script), "-h"], capture_output=True, text=True, timeout=5
                )

            if result.returncode not in [0, 1]:
                result = subprocess.run(
                    ["python", str(main_script)], capture_output=True, text=True, timeout=5
                )

            # Should either succeed (0) or fail gracefully (1)
            assert result.returncode in [0, 1], f"{skill_name}: Should handle help/invalid args gracefully"

    def test_skill_has_guardian_exemptions(self, skills_dir, all_skills):
        """Test that skills have guardian exemptions where needed."""
        for skill_name in all_skills:
            main_script = skills_dir / skill_name / "main.py"
            content = main_script.read_text(encoding="utf-8")

            # Skills that likely need exemptions
            skills_needing_exemptions = {
                "powershell-guard",
                "repair-gate-validator",
                "agent-deletion-guard",
                "hitl-decision-validator",
                "guardian-exemption-validator",
                "pre-write-orchestrator",
                "skill-status-dashboard",
                "performance-monitor",
                "ci-integration",
            }

            if skill_name in skills_needing_exemptions:
                assert "# guardian: allow-" in content, f"{skill_name}: Should have guardian exemptions"

    @pytest.mark.parametrize(
        "skill_name",
        [
            "powershell-guard",
            "repair-gate-validator",
            "agent-deletion-guard",
            "hitl-decision-validator",
            "guardian-exemption-validator",
        ],
    )
    def test_phase2_skills_functionality(self, skills_dir, skill_name):
        """Test Phase 2 critical gap skills functionality."""
        main_script = skills_dir / skill_name / "main.py"

        if skill_name == "powershell-guard":
            # Test PowerShell detection
            result = subprocess.run(
                ["python", str(main_script), "powershell.exe Get-Process", "test.py"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert result.returncode != 0, "Should reject PowerShell command"
            assert "PowerShell" in result.stdout or "PowerShell" in result.stderr

            # Test Python subprocess approval
            result = subprocess.run(
                ["python", str(main_script), "python script.py", "test.py"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert result.returncode == 0, "Should approve Python subprocess"

        elif skill_name == "repair-gate-validator":
            # Test with mock file (will fail gates but should run)
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
                f.write(b"# test file")
                temp_file = f.name

            try:
                result = subprocess.run(
                    ["python", str(main_script), temp_file, "edit"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                # Should run (even if gates fail)
                assert result.returncode in [0, 1], "Should execute validation"
            finally:
                Path(temp_file).unlink(missing_ok=True)

        elif skill_name == "agent-deletion-guard":
            # Test non-agent file
            result = subprocess.run(
                ["python", str(main_script), "regular_file.py"], capture_output=True, text=True, timeout=10
            )
            assert result.returncode == 0, "Should allow non-agent file deletion"

            # Test agent file
            result = subprocess.run(
                ["python", str(main_script), "TestAgent.py"], capture_output=True, text=True, timeout=10
            )
            assert result.returncode != 0, "Should block agent file deletion without authorization"

        elif skill_name == "hitl-decision-validator":
            # Test single option (no HITL required)
            result = subprocess.run(
                ["python", str(main_script), "test decision", "1"], capture_output=True, text=True, timeout=10
            )
            assert result.returncode == 0, "Should allow single option"

            # Test multiple options (requires HITL)
            result = subprocess.run(
                ["python", str(main_script), "test decision", "3"], capture_output=True, text=True, timeout=10
            )
            assert result.returncode != 0, "Should require HITL for multiple options"

        elif skill_name == "guardian-exemption-validator":
            # Test invalid format
            result = subprocess.run(
                ["python", str(main_script), "# guardian: allow-something", "test.py"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert result.returncode != 0, "Should reject invalid format"

            # Test valid format
            result = subprocess.run(
                [
                    "python",
                    str(main_script),
                    "# guardian: allow-silent-swallower -- Specific justification for exception handling in test validation",
                    "test.py",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert result.returncode == 0, "Should accept valid format with specific justification"

    def test_orchestrator_dependency_resolution(self, skills_dir):
        """Test pre-write orchestrator dependency resolution."""
        orchestrator_main = skills_dir / "pre-write-orchestrator" / "main.py"

        if not orchestrator_main.exists():
            pytest.skip("pre-write-orchestrator not found")

        # Test status command
        result = subprocess.run(
            ["python", str(orchestrator_main), "test.py", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, "Should support status command"

        # Should output JSON with skill registry
        try:
            import json

            data = json.loads(result.stdout)
            assert "skill_status" in data, "Should include skill status"
        except json.JSONDecodeError:
            pytest.fail("Should output valid JSON for status")

    def test_performance_monitoring(self, skills_dir):
        """Test performance monitoring functionality."""
        perf_main = skills_dir / "performance-monitor" / "main.py"

        if not perf_main.exists():
            pytest.skip("performance-monitor not found")

        # Test summary command
        result = subprocess.run(
            ["python", str(perf_main), "summary", "1"], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0, "Should support summary command"

        # Test alerts command
        result = subprocess.run(
            ["python", str(perf_main), "alerts"], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0, "Should support alerts command"

    def test_skill_status_dashboard(self, skills_dir):
        """Test skill status dashboard functionality."""
        dashboard_main = skills_dir / "skill-status-dashboard" / "main.py"

        if not dashboard_main.exists():
            pytest.skip("skill-status-dashboard not found")

        # Test table output
        result = subprocess.run(
            ["python", str(dashboard_main), "table"], capture_output=True, text=True, timeout=15
        )

        assert result.returncode == 0, "Should support table output"
        assert "Skill Status Dashboard" in result.stdout, "Should include dashboard header"

        # Test JSON output
        result = subprocess.run(
            ["python", str(dashboard_main), "json"], capture_output=True, text=True, timeout=15
        )

        assert result.returncode == 0, "Should support JSON output"

        try:
            import json

            data = json.loads(result.stdout)
            assert "summary" in data, "Should include summary in JSON"
        except json.JSONDecodeError:
            pytest.fail("Should output valid JSON")

    def test_ci_integration(self, skills_dir):
        """Test CI integration functionality."""
        ci_main = skills_dir / "ci-integration" / "main.py"

        if not ci_main.exists():
            pytest.skip("ci-integration not found")

        # Test health check
        result = subprocess.run(
            ["python", str(ci_main), "health-check"], capture_output=True, text=True, timeout=15
        )

        assert result.returncode in [0, 1], "Should support health check"
        assert "System Health:" in result.stdout, "Should include health status"

        # Test validate command
        result = subprocess.run(
            ["python", str(ci_main), "validate"], capture_output=True, text=True, timeout=20
        )

        assert result.returncode in [0, 1], "Should support validate command"
        assert "Compliance Results:" in result.stdout, "Should include compliance results"


class TestSkillIntegration:
    """Test skill integration scenarios."""

    def test_orchestrator_with_all_skills(self):
        """Test orchestrator can coordinate all skills."""
        skills_dir = Path(".windsurf/skills")
        orchestrator_main = skills_dir / "pre-write-orchestrator" / "main.py"

        if not orchestrator_main.exists():
            pytest.skip("pre-write-orchestrator not found")

        # Test with a simple file operation
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"# test file for orchestrator")
            temp_file = f.name

        try:
            result = subprocess.run(
                ["python", str(orchestrator_main), temp_file, "write", "test context"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should run and provide output
            assert result.returncode in [0, 1], "Should execute orchestrator"
            assert "Starting pre-write validation" in result.stdout, "Should show validation start"
        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_performance_monitoring_with_orchestrator(self):
        """Test performance monitoring works with orchestrator."""
        skills_dir = Path(".windsurf/skills")
        perf_main = skills_dir / "performance-monitor" / "main.py"
        orchestrator_main = skills_dir / "pre-write-orchestrator" / "main.py"

        if not perf_main.exists() or not orchestrator_main.exists():
            pytest.skip("Required skills not found")

        # Start monitoring
        start_result = subprocess.run(
            ["python", str(perf_main), "start", "test_operation"], capture_output=True, text=True, timeout=5
        )

        assert start_result.returncode == 0, "Should start monitoring"

        # Run orchestrator
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"# test file")
            temp_file = f.name

        try:
            subprocess.run(
                ["python", str(orchestrator_main), temp_file, "write"],
                capture_output=True,
                text=True,
                timeout=15,
            )
        finally:
            Path(temp_file).unlink(missing_ok=True)

        # Stop monitoring
        stop_result = subprocess.run(
            ["python", str(perf_main), "stop"], capture_output=True, text=True, timeout=5
        )

        assert stop_result.returncode == 0, "Should stop monitoring"
        assert "Performance Results" in stop_result.stdout, "Should show performance results"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
