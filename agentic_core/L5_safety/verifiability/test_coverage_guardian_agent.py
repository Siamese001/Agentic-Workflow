#!/usr/bin/env python3
"""
Test Coverage Guardian Agent
Ultimate verification agent: Enforces comprehensive test coverage with branch, mutation, and property testing.
- Coverage: line + branch
- Mutation score: killed / total mutants
- Auto-stubs for coverage gaps
- Hint generation for surviving mutants
- Property testing: Hypothesis skeleton generation
"""
import importlib
import inspect
import json
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestCoverageGuardianAgent:
    """
    Ultimate verification agent: Enforces comprehensive test coverage with branch, mutation, and property testing.
    - Coverage: line + branch
    - Mutation score: killed / total mutants
    - Auto-stubs for coverage gaps
    - Hint generation for surviving mutants
    - Property testing: Hypothesis skeleton generation
    """

    def __init__(self, project_root: Path, ctx):
        self.project_root = Path(project_root)
        self.ctx = ctx
        self.min_line_coverage = 95
        self.min_branch_coverage = 90
        self.min_mutation_score = 95
        self.test_dir = self.project_root / "tests"
        self.html_report_dir = self.project_root / "htmlcov"
        self.history_file = self.project_root / "coverage_history.json"
        self.auto_generate = True
        self.mutation_hints = True
        self.property_testing_enabled = True

    def _load_history(self) -> List[Dict]:
        """Load coverage history from JSON file."""
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def _save_history(self, entry: Dict):
        """Save coverage history entry (keep last 30)."""
        history = self._load_history()
        history.append(entry)
        # Keep only last 30 entries
        self.history_file.write_text(
            json.dumps(history[-30:], indent=2), encoding="utf-8"
        )

    def _run_advanced_coverage(self) -> Dict[str, Any]:
        """Run pytest with branch coverage and generate reports."""
        try:
            # Run coverage with branch analysis
            subprocess.run(
                [
                    "coverage",
                    "run",
                    "--branch",
                    "-m",
                    "pytest",
                    str(self.project_root / "agentic_core"),
                    "--quiet",
                ],
                check=True,
                cwd=self.project_root,
                capture_output=True,
            )
            
            # Generate JSON report
            subprocess.run(
                ["coverage", "json", "-o", "coverage.json"], cwd=self.project_root
            )
            
            # Generate HTML report
            subprocess.run(
                ["coverage", "html", "-d", str(self.html_report_dir)],
                cwd=self.project_root,
            )

            # Read JSON report
            report_file = self.project_root / "coverage.json"
            if report_file.exists():
                return json.loads(report_file.read_text(encoding="utf-8"))

        except FileNotFoundError:
            if hasattr(self.ctx, "report"):
                self.ctx.report(
                    "TestCoverageGuardianAgent", 0, False, "coverage not installed"
                )
        except Exception as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report(
                    "TestCoverageGuardianAgent", 0, False, f"Advanced coverage failed: {e}"
                )
        return {"files": {}}

    def _discover_property_candidates(self) -> List[Dict]:
        """Scan agentic_core for functions suitable for property testing."""
        candidates = []
        core_path = self.project_root / "agentic_core"
        for py_file in core_path.rglob("*.py"):
            if "__init__" in str(py_file):
                continue
            rel_path = py_file.relative_to(self.project_root)
            module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if (inspect.isfunction(obj) or inspect.isclass(obj)) and not name.startswith("_"):
                        try:
                            sig = inspect.signature(obj)
                            params = [
                                p
                                for p in sig.parameters.values()
                                if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
                            ]
                            if params:
                                candidates.append(
                                    {
                                        "file": str(rel_path),
                                        "module": module_name,
                                        "name": name,
                                        "params": [p.name for p in params],
                                        "param_types": [
                                            str(p.annotation)
                                            for p in params
                                            if p.annotation != p.empty
                                        ],
                                    }
                                )
                        except ValueError:
                            continue
            except Exception:
                continue
        return candidates

    def _generate_property_test(self, candidate: Dict) -> tuple:
        """Generate Hypothesis property test skeleton with strategy mapping."""
        rel = Path(candidate["file"]).relative_to("agentic_core")
        test_name = f"test_property_{rel.with_suffix('').as_posix().replace('/', '_')}_{candidate['name']}.py"
        test_path = self.test_dir / test_name

        imports = [
            "from hypothesis import given, strategies as st, assume, settings, HealthCheck",
            f"from {candidate['module']} import {candidate['name']}",
        ]

        strategies = []
        for i, param in enumerate(candidate["params"]):
            # Basic type-to-strategy mapping logic
            p_type = candidate["param_types"][i] if i < len(candidate["param_types"]) else ""
            if "str" in p_type.lower():
                strategies.append(f"{param}=st.text(min_size=1)")
            elif "int" in p_type.lower():
                strategies.append(f"{param}=st.integers()")
            elif "float" in p_type.lower():
                strategies.append(f"{param}=st.floats(allow_nan=False)")
            elif "bool" in p_type.lower():
                strategies.append(f"{param}=st.booleans()")
            else:
                strategies.append(f"{param}=st.text() | st.integers()")

        header = "@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])"
        decorator = "@given(" + ", ".join(strategies) + ")"
        body = textwrap.dedent(
            f"""
            def test_property_{candidate['name']}({', '.join(candidate['params'])}):
                \"\"\"Invariant: {candidate['name']} should handle all valid inputs without crashing\"\"\"
                # assume(is_valid({candidate['params'][0]})) 
                result = {candidate['name']}({', '.join(candidate['params'])})
                assert result is not None
        """
        )
        return test_path, "\n".join(imports) + "\n\n" + header + "\n" + decorator + "\n" + body

    def _run_mutmut(self) -> Dict[str, Any]:
        """Run mutation testing using mutmut."""
        try:
            # Run mutmut
            result = subprocess.run(
                ["mutmut", "run", "--paths-to-mutate", "agentic_core/"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            
            # Get results
            results_output = subprocess.run(
                ["mutmut", "results"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            
            # Parse mutation score (simplified)
            # Format: "Survived: X, Killed: Y, Timeout: Z"
            killed = 0
            total = 0
            if results_output.returncode == 0:
                output = results_output.stdout
                # Simple parsing - in production, use proper JSON output
                import re
                killed_match = re.search(r"Killed:\s*(\d+)", output)
                survived_match = re.search(r"Survived:\s*(\d+)", output)
                if killed_match:
                    killed = int(killed_match.group(1))
                if survived_match:
                    survived = int(survived_match.group(1))
                    total = killed + survived
            
            score = (killed / total * 100) if total > 0 else 0
            return {"score": score, "survived": total - killed, "examples": []}
            
        except FileNotFoundError:
            if hasattr(self.ctx, "report"):
                self.ctx.report("TestCoverageGuardianAgent", 0, False, "mutmut not installed")
            return {"score": 0, "survived": 0, "examples": []}
        except Exception as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report("TestCoverageGuardianAgent", 0, False, f"Mutation testing failed: {e}")
            return {"score": 0, "survived": 0, "examples": []}

    async def execute(self) -> Dict:
        """Ultimate verification: coverage, mutation, and property testing."""
        print("   [SOVEREIGN VERIFICATION] Running coverage, mutation, and property discovery...")

        # 1. Run Core Coverage & Mutation logic
        cov_report = self._run_advanced_coverage()
        line_cov = cov_report.get("totals", {}).get("percent_covered", 0)
        branch_cov = cov_report.get("totals", {}).get("percent_covered_display", 0)
        mut_result = self._run_mutmut()
        mut_score = mut_result.get("score", 0)

        # 2. Discover Property Candidates
        prop_gen = 0
        if self.property_testing_enabled:
            candidates = self._discover_property_candidates()
            for cand in candidates[:10]:  # Incremental discovery
                p_path, p_content = self._generate_property_test(cand)
                if not p_path.exists():
                    p_path.parent.mkdir(parents=True, exist_ok=True)
                    p_path.write_text(p_content, encoding="utf-8")
                    prop_gen += 1

        # 3. Sovereignty check
        passed = (
            line_cov >= self.min_line_coverage
            and branch_cov >= self.min_branch_coverage
            and mut_score >= self.min_mutation_score
            and (prop_gen > 0 or list(self.test_dir.glob("test_property_*.py")))
        )

        # Save history
        self._save_history(
            {
                "timestamp": datetime.now().isoformat(),
                "line_coverage": round(line_cov, 1),
                "branch_coverage": round(branch_cov, 1) if isinstance(branch_cov, (int, float)) else 0,
                "mutation_score": round(mut_score, 1),
                "property_tests": prop_gen,
            }
        )

        print(
            f"   [METRICS] Line: {line_cov:.1f}% | Branch: {branch_cov if isinstance(branch_cov, (int, float)) else 'N/A'} | Mutation: {mut_score:.1f}% | Props Gen: {prop_gen}"
        )

        return {
            "line_coverage": line_cov,
            "branch_coverage": branch_cov if isinstance(branch_cov, (int, float)) else 0,
            "mutation_score": mut_score,
            "property_tests_generated": prop_gen,
            "passed_sovereignty": passed,
        }
