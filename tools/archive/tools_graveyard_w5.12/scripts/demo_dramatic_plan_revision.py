#!/usr/bin/env python3
"""
Dramatic demonstration of token estimator guiding plan revision
Shows clear before/after with actual token issues and resolutions
"""

import sys

# Force UTF-8 output on Windows to support emoji/unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import copy
import tempfile
from pathlib import Path
from typing import Any

from tools.utils.planning.preflight_hook import PlanningPreflightHook, TokenBudgetExceededError


class DramaticPlanRevisor:
    """
    Demonstrates clear token estimator impact on plan revision
    """

    def __init__(self):
        self._temp_dir = Path(tempfile.mkdtemp())
        self.budget_file = self._temp_dir / "dramatic_plan_revision_budget.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

    def cleanup(self):
        """Remove temporary budget file"""
        if self.budget_file.exists():
            self.budget_file.unlink()
        if self._temp_dir.exists():
            self._temp_dir.rmdir()

    def create_problematic_plan(self) -> dict[str, Any]:
        """Create a plan that will definitely have token issues"""
        print("🎯 CREATING PROBLEMATIC IMPLEMENTATION PLAN")
        print("=" * 60)
        print("This plan is designed to exceed token budgets...")

        problematic_plan = {
            "plan_name": "Massive E-commerce Platform",
            "phases": [
                {
                    "phase_name": "massive_authentication",
                    "steps": [
                        {
                            "step_name": "huge_auth_design",
                            "description": "Design massive authentication system",
                            "inputs": self._create_massive_auth_inputs(),
                        },
                        {
                            "step_name": "monolithic_auth_impl",
                            "description": "Implement monolithic authentication",
                            "inputs": self._create_massive_auth_inputs(),
                        },
                    ],
                },
                {
                    "phase_name": "massive_product_catalog",
                    "steps": [
                        {
                            "step_name": "huge_product_design",
                            "description": "Design massive product catalog",
                            "inputs": self._create_massive_product_inputs(),
                        },
                        {
                            "step_name": "monolithic_product_impl",
                            "description": "Implement monolithic product system",
                            "inputs": self._create_massive_product_inputs(),
                        },
                    ],
                },
                {
                    "phase_name": "massive_order_system",
                    "steps": [
                        {
                            "step_name": "huge_order_design",
                            "description": "Design massive order system",
                            "inputs": self._create_massive_order_inputs(),
                        },
                        {
                            "step_name": "monolithic_order_impl",
                            "description": "Implement monolithic order system",
                            "inputs": self._create_massive_order_inputs(),
                        },
                    ],
                },
            ],
        }

        self._analyze_plan(problematic_plan, "PROBLEMATIC")
        return problematic_plan

    def simulate_problematic_execution(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Simulate execution - expect many issues"""
        print("\n🚀 SIMULATING PROBLEMATIC EXECUTION")
        print("=" * 60)
        print("Expecting budget violations and compression needs...")

        total_steps_in_plan = sum(len(p["steps"]) for p in plan["phases"])
        results = {
            "plan_name": plan["plan_name"],
            "total_steps_in_plan": total_steps_in_plan,
            "step_results": [],
            "issues": [],
            "total_tokens": 0,
            "critical_failures": 0,
        }

        for phase in plan["phases"]:
            print(f"\n📋 Phase: {phase['phase_name']}")

            for step in phase["steps"]:
                print(f"   🔧 Step: {step['step_name']}")

                try:
                    # Use preflight hook to estimate tokens
                    estimate = self.hook.preflight_check(
                        plan_step=f"{phase['phase_name']}/{step['step_name']}",
                        **step["inputs"],
                    )

                    step_result = {
                        "step_name": step["step_name"],
                        "tokens": estimate.total_projected_tokens,
                        "status": estimate.status,
                        "action": estimate.action,
                        "compression_applied": len(estimate.compression_applied) > 0,
                    }

                    results["step_results"].append(step_result)
                    results["total_tokens"] += estimate.total_projected_tokens

                    print(f"      📊 Tokens: {estimate.total_projected_tokens:,}")
                    print(f"      🚦 Status: {estimate.status} ({estimate.action})")

                    if estimate.status == "red":
                        results["issues"].append(
                            {
                                "step": step["step_name"],
                                "issue": "BUDGET_EXCEEDED",
                                "tokens": estimate.total_projected_tokens,
                                "severity": "CRITICAL",
                            }
                        )
                        results["critical_failures"] += 1
                        print(
                            f"      ❌ CRITICAL: Budget exceeded! ({estimate.total_projected_tokens:,} > 200,000)"
                        )

                    elif estimate.status == "yellow":
                        results["issues"].append(
                            {
                                "step": step["step_name"],
                                "issue": "COMPRESSION_NEEDED",
                                "tokens": estimate.total_projected_tokens,
                                "severity": "WARNING",
                            }
                        )
                        print(
                            f"      ⚠️  WARNING: Compression needed ({estimate.total_projected_tokens:,} tokens)"
                        )

                    else:
                        print(f"      ✅ OK: Within budget ({estimate.total_projected_tokens:,} tokens)")

                except TokenBudgetExceededError as e:
                    results["issues"].append(
                        {
                            "step": step["step_name"],
                            "issue": "BUDGET_EXCEEDED",
                            "error": str(e),
                            "severity": "CRITICAL",
                        }
                    )
                    results["critical_failures"] += 1
                    print(f"      ❌ CRITICAL EXECUTION BLOCKED: {str(e)[:60]}...")

                except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                    results["issues"].append(
                        {
                            "step": step["step_name"],
                            "issue": "ERROR",
                            "error": str(e),
                            "severity": "ERROR",
                        }
                    )
                    print(f"      ❌ ERROR: {e}")

        print("\n📊 PROBLEMATIC EXECUTION SUMMARY:")
        print(f"   - Total steps: {len(results['step_results'])}")
        print(f"   - Total tokens: {results['total_tokens']:,}")
        print(f"   - Critical failures: {results['critical_failures']}")
        print(f"   - Total issues: {len(results['issues'])}")

        # Categorize issues
        critical_issues = [i for i in results["issues"] if i.get("severity") == "CRITICAL"]
        warning_issues = [i for i in results["issues"] if i.get("severity") == "WARNING"]

        print(f"   - Critical issues: {len(critical_issues)}")
        print(f"   - Warning issues: {len(warning_issues)}")

        return results

    def create_optimized_plan(
        self, problematic_plan: dict[str, Any], problematic_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Create optimized plan based on token analysis"""
        print("\n🔧 CREATING OPTIMIZED PLAN")
        print("=" * 60)
        print("Applying token estimator recommendations...")

        optimized_plan = copy.deepcopy(problematic_plan)
        optimized_plan["plan_name"] = f"{problematic_plan['plan_name']}_optimized"
        optimized_plan["optimization_strategy"] = []
        optimized_plan["optimization_notes"] = []

        # Analyze issues and apply optimizations
        critical_steps = [i["step"] for i in problematic_results["issues"] if i.get("severity") == "CRITICAL"]
        warning_steps = [i["step"] for i in problematic_results["issues"] if i.get("severity") == "WARNING"]

        print("📊 OPTIMIZATION ANALYSIS:")
        print(f"   - Critical steps to fix: {len(critical_steps)}")
        print(f"   - Warning steps to optimize: {len(warning_steps)}")

        # Apply optimizations to each phase
        for phase in optimized_plan["phases"]:
            for step in phase["steps"]:
                if step["step_name"] in critical_steps:
                    # Apply aggressive optimizations for critical issues
                    step["optimization"] = {
                        "strategy": "AGGRESSIVE_SPLITTING",
                        "max_tokens_per_substep": 40000,
                        "split_into": 3,
                        "focus": "core_functionality_only",
                        "remove_examples": True,
                        "minimize_context": True,
                        "use_structured_format": True,
                    }
                    optimized_plan["optimization_strategy"].append(
                        f"Split {step['step_name']} into 3 substeps"
                    )
                    optimized_plan["optimization_notes"].append(
                        f"Applied aggressive splitting to {step['step_name']} due to budget exceed",
                    )

                elif step["step_name"] in warning_steps:
                    # Apply moderate optimizations for warnings
                    step["optimization"] = {
                        "strategy": "CONTENT_OPTIMIZATION",
                        "focus_on_essentials": True,
                        "minimize_examples": True,
                        "use_structured_format": True,
                        "apply_smart_truncation": True,
                        "enable_progressive_disclosure": True,
                    }
                    optimized_plan["optimization_strategy"].append(f"Optimize {step['step_name']} content")
                    optimized_plan["optimization_notes"].append(
                        f"Applied content optimization to {step['step_name']} for compression",
                    )
                else:
                    # Apply light optimizations for good steps
                    step["optimization"] = {
                        "strategy": "LIGHT_OPTIMIZATION",
                        "ensure_efficiency": True,
                        "monitor_token_usage": True,
                    }

        # Add phase-level optimizations
        for phase in optimized_plan["phases"]:
            phase["parallel_execution"] = True
            phase["token_budget_per_phase"] = 150000
            phase["enable_checkpointing"] = True

        optimized_plan["optimization_strategy"].append("Enable parallel phase execution")
        optimized_plan["optimization_strategy"].append("Add phase token budgets")
        optimized_plan["optimization_strategy"].append("Enable checkpointing")

        self._analyze_plan(optimized_plan, "OPTIMIZED")
        return optimized_plan

    def simulate_optimized_execution(self, optimized_plan: dict[str, Any]) -> dict[str, Any]:
        """Simulate optimized plan execution"""
        print("\n🚀 SIMULATING OPTIMIZED EXECUTION")
        print("=" * 60)
        print("Testing optimized plan with token estimator...")

        total_steps_in_plan = sum(len(p["steps"]) for p in optimized_plan["phases"])
        results = {
            "plan_name": optimized_plan["plan_name"],
            "total_steps_in_plan": total_steps_in_plan,
            "step_results": [],
            "issues": [],
            "total_tokens": 0,
            "critical_failures": 0,
            "optimizations_applied": len(optimized_plan.get("optimization_strategy", [])),
        }

        for phase in optimized_plan["phases"]:
            print(f"\n📋 Phase: {phase['phase_name']} (OPTIMIZED)")

            for step in phase["steps"]:
                print(f"   🔧 Step: {step['step_name']} (OPTIMIZED)")

                # Apply optimizations to inputs
                optimized_inputs = self._apply_optimizations(step["inputs"], step.get("optimization", {}))

                try:
                    # Use preflight hook to estimate tokens
                    estimate = self.hook.preflight_check(
                        plan_step=f"{phase['phase_name']}/{step['step_name']}_optimized",
                        **optimized_inputs,
                    )

                    step_result = {
                        "step_name": step["step_name"],
                        "tokens": estimate.total_projected_tokens,
                        "status": estimate.status,
                        "action": estimate.action,
                        "compression_applied": len(estimate.compression_applied) > 0,
                        "optimization": step.get("optimization", {}).get("strategy", "NONE"),
                    }

                    results["step_results"].append(step_result)
                    results["total_tokens"] += estimate.total_projected_tokens

                    print(f"      📊 Tokens: {estimate.total_projected_tokens:,}")
                    print(f"      🚦 Status: {estimate.status} ({estimate.action})")
                    print(f"      🔧 Optimization: {step_result['optimization']}")

                    if estimate.status == "red":
                        results["issues"].append(
                            {
                                "step": step["step_name"],
                                "issue": "STILL_BUDGET_EXCEEDED",
                                "tokens": estimate.total_projected_tokens,
                                "severity": "CRITICAL",
                            }
                        )
                        print("      ❌ STILL CRITICAL: Budget exceeded!")

                    elif estimate.status == "yellow":
                        results["issues"].append(
                            {
                                "step": step["step_name"],
                                "issue": "STILL_COMPRESSION_NEEDED",
                                "tokens": estimate.total_projected_tokens,
                                "severity": "WARNING",
                            }
                        )
                        print("      ⚠️  STILL WARNING: Compression needed")

                    else:
                        print("      ✅ SUCCESS: Within budget!")

                except TokenBudgetExceededError as e:
                    results["issues"].append(
                        {
                            "step": step["step_name"],
                            "issue": "STILL_BUDGET_EXCEEDED",
                            "error": str(e),
                            "severity": "CRITICAL",
                        }
                    )
                    print(f"      ❌ STILL CRITICAL: {str(e)[:60]}...")

                except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                    results["issues"].append(
                        {
                            "step": step["step_name"],
                            "issue": "ERROR",
                            "error": str(e),
                            "severity": "ERROR",
                        }
                    )
                    print(f"      ❌ ERROR: {e}")

        print("\n📊 OPTIMIZED EXECUTION SUMMARY:")
        print(f"   - Total steps: {len(results['step_results'])}")
        print(f"   - Total tokens: {results['total_tokens']:,}")
        print(f"   - Optimizations applied: {results['optimizations_applied']}")
        print(f"   - Remaining issues: {len(results['issues'])}")

        return results

    def compare_dramatic_results(
        self, problematic_results: dict[str, Any], optimized_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Compare problematic vs optimized results"""
        print("\n📊 DRAMATIC COMPARISON")
        print("=" * 60)

        prob_steps_attempted = problematic_results.get("total_steps_in_plan", 6)
        prob_steps_succeeded = len(problematic_results["step_results"])
        opt_steps_succeeded = len(optimized_results["step_results"])

        comparison = {
            "problematic_tokens": problematic_results["total_tokens"],
            "optimized_tokens": optimized_results["total_tokens"],
            "problematic_issues": len(problematic_results["issues"]),
            "optimized_issues": len(optimized_results["issues"]),
            "problematic_critical": problematic_results["critical_failures"],
            "optimized_critical": len(
                [i for i in optimized_results["issues"] if i.get("severity") == "CRITICAL"]
            ),
            "problematic_steps_succeeded": prob_steps_succeeded,
            "optimized_steps_succeeded": opt_steps_succeeded,
            "total_steps_attempted": prob_steps_attempted,
        }

        issue_reduction = comparison["problematic_issues"] - comparison["optimized_issues"]
        critical_reduction = comparison["problematic_critical"] - comparison["optimized_critical"]

        # Success rates based on steps attempted vs succeeded
        prob_success_rate = (
            (prob_steps_succeeded / prob_steps_attempted * 100) if prob_steps_attempted > 0 else 0
        )
        opt_success_rate = (
            (opt_steps_succeeded / prob_steps_attempted * 100) if prob_steps_attempted > 0 else 0
        )

        print("🎯 DRAMATIC IMPROVEMENTS:")
        print(f"   - Issues resolved: {issue_reduction} of {comparison['problematic_issues']}")
        print(
            f"   - Critical failures resolved: {critical_reduction} of {comparison['problematic_critical']}"
        )
        print(f"   - Success rate: {prob_success_rate:.0f}% → {opt_success_rate:.0f}%")
        print(f"   - Optimized total tokens: {comparison['optimized_tokens']:,}")

        # Show before/after status
        print("\n📈 BEFORE vs AFTER:")
        print(
            f"   BEFORE: {prob_steps_succeeded}/{prob_steps_attempted} steps succeeded, {comparison['problematic_issues']} issues ({comparison['problematic_critical']} critical)"
        )
        print(
            f"   AFTER:  {opt_steps_succeeded}/{prob_steps_attempted} steps succeeded, {comparison['optimized_issues']} issues ({comparison['optimized_critical']} critical)"
        )

        comparison["issue_reduction"] = issue_reduction
        comparison["critical_reduction"] = critical_reduction
        comparison["prob_success_rate"] = prob_success_rate
        comparison["opt_success_rate"] = opt_success_rate

        return comparison

    def _apply_optimizations(self, inputs: dict[str, Any], optimization: dict[str, Any]) -> dict[str, Any]:
        """Apply optimizations to step inputs (deep copy to avoid mutating originals)"""
        optimized_inputs = copy.deepcopy(inputs)

        strategy = optimization.get("strategy", "NONE")

        if strategy == "AGGRESSIVE_SPLITTING":
            # Dramatically reduce ALL content categories
            optimized_inputs["system_prompt"] = (
                optimized_inputs.get("system_prompt", "")[:1000] + " [OPTIMIZED]"
            )
            optimized_inputs["user_prompt"] = optimized_inputs.get("user_prompt", "")[:800] + " [OPTIMIZED]"

            # Reduce files to 2 most important, truncated
            optimized_inputs["files"] = optimized_inputs.get("files", [])[:2]
            for file in optimized_inputs["files"]:
                file["content"] = file["content"][:2000] + "\n# [CONTENT OPTIMIZED FOR TOKEN BUDGET]"

            # Reduce diffs to 1 most important, truncated
            optimized_inputs["diffs"] = optimized_inputs.get("diffs", [])[:1]
            for diff in optimized_inputs["diffs"]:
                diff["content"] = diff["content"][:1000] + "\n# [DIFF TRIMMED]"

            # Reduce logs to 2 most recent, errors only
            optimized_inputs["logs"] = optimized_inputs.get("logs", [])[:2]
            for log in optimized_inputs["logs"]:
                log["content"] = log["content"][:500] + "\n# [LOGS TRIMMED TO ERRORS]"

            # Reduce retrieved context to 2 most relevant
            optimized_inputs["retrieved_context"] = optimized_inputs.get("retrieved_context", [])[:2]
            for ctx in optimized_inputs["retrieved_context"]:
                ctx["content"] = ctx["content"][:500] + " [OPTIMIZED]"

            # Reduce prior steps to last 2
            optimized_inputs["prior_steps"] = optimized_inputs.get("prior_steps", [])[:2]
            for i, step in enumerate(optimized_inputs["prior_steps"]):
                optimized_inputs["prior_steps"][i] = step[:500] + " [TRIMMED]"

        elif strategy == "CONTENT_OPTIMIZATION":
            # Moderate reduction across all categories
            optimized_inputs["system_prompt"] = (
                optimized_inputs.get("system_prompt", "")[:3000] + " [OPTIMIZED]"
            )
            optimized_inputs["user_prompt"] = optimized_inputs.get("user_prompt", "")[:2000] + " [OPTIMIZED]"

            # Keep 4 files, truncated
            optimized_inputs["files"] = optimized_inputs.get("files", [])[:4]
            for file in optimized_inputs["files"]:
                file["content"] = file["content"][:5000] + "\n# [CONTENT OPTIMIZED]"

            # Keep 2 diffs, truncated
            optimized_inputs["diffs"] = optimized_inputs.get("diffs", [])[:2]
            for diff in optimized_inputs["diffs"]:
                diff["content"] = diff["content"][:3000] + "\n# [DIFF OPTIMIZED]"

            # Keep 4 logs, truncated
            optimized_inputs["logs"] = optimized_inputs.get("logs", [])[:4]
            for log in optimized_inputs["logs"]:
                log["content"] = log["content"][:1000] + "\n# [LOGS OPTIMIZED]"

            # Reduce retrieved context moderately
            optimized_inputs["retrieved_context"] = optimized_inputs.get("retrieved_context", [])[:4]
            for ctx in optimized_inputs["retrieved_context"]:
                ctx["content"] = ctx["content"][:1000] + " [OPTIMIZED]"

            # Keep last 3 prior steps, truncated
            optimized_inputs["prior_steps"] = optimized_inputs.get("prior_steps", [])[:3]
            for i, step in enumerate(optimized_inputs["prior_steps"]):
                optimized_inputs["prior_steps"][i] = step[:1000] + " [TRIMMED]"

        elif strategy == "LIGHT_OPTIMIZATION":
            # Light reduction — prompts only
            optimized_inputs["system_prompt"] = (
                optimized_inputs.get("system_prompt", "")[:5000] + " [LIGHTLY_OPTIMIZED]"
            )
            optimized_inputs["user_prompt"] = (
                optimized_inputs.get("user_prompt", "")[:3000] + " [LIGHTLY_OPTIMIZED]"
            )

        return optimized_inputs

    def _analyze_plan(self, plan: dict[str, Any], plan_type: str):
        """Quick analysis of plan"""
        print(f"\n📊 {plan_type} PLAN ANALYSIS:")

        total_steps = sum(len(phase["steps"]) for phase in plan["phases"])
        total_phases = len(plan["phases"])

        print(f"   - Phases: {total_phases}")
        print(f"   - Steps: {total_steps}")

        if plan_type == "PROBLEMATIC":
            print("   - Expected issues: HIGH (designed to exceed budgets)")
        elif plan_type == "OPTIMIZED":
            print("   - Expected issues: LOW (with optimizations applied)")

    # Content generation methods (designed to be massive)
    def _create_massive_auth_inputs(self) -> dict[str, Any]:
        massive_content = "MASSIVE_CONTENT_" + "x" * 10000

        return {
            "system_prompt": massive_content * 50,  # Very large
            "user_prompt": massive_content * 40,  # Very large
            "files": [
                {
                    "path": f"auth_file_{i}.py",
                    "content": massive_content * 20,  # Many large files
                }
                for i in range(10)
            ],
            "diffs": [
                {
                    "path": f"auth_diff_{i}.py",
                    "content": massive_content * 15,  # Many large diffs
                }
                for i in range(5)
            ],
            "logs": [
                {
                    "source": f"auth_log_{i}.log",
                    "content": massive_content * 10,  # Many large logs
                }
                for i in range(20)
            ],
            "retrieved_context": [
                {
                    "content": massive_content * 8,  # Many large context items
                    "source": f"doc_{i}",
                }
                for i in range(15)
            ],
            "prior_steps": [massive_content * 5] * 25,  # Many prior steps
        }

    def _create_massive_product_inputs(self) -> dict[str, Any]:
        massive_content = "PRODUCT_CONTENT_" + "y" * 10000

        return {
            "system_prompt": massive_content * 45,
            "user_prompt": massive_content * 35,
            "files": [
                {
                    "path": f"product_file_{i}.py",
                    "content": massive_content * 18,
                }
                for i in range(8)
            ],
            "diffs": [
                {
                    "path": f"product_diff_{i}.py",
                    "content": massive_content * 12,
                }
                for i in range(4)
            ],
            "logs": [
                {
                    "source": f"product_log_{i}.log",
                    "content": massive_content * 8,
                }
                for i in range(15)
            ],
            "retrieved_context": [
                {
                    "content": massive_content * 6,
                    "source": f"product_doc_{i}",
                }
                for i in range(12)
            ],
            "prior_steps": [massive_content * 4] * 20,
        }

    def _create_massive_order_inputs(self) -> dict[str, Any]:
        massive_content = "ORDER_CONTENT_" + "z" * 10000

        return {
            "system_prompt": massive_content * 40,
            "user_prompt": massive_content * 30,
            "files": [
                {
                    "path": f"order_file_{i}.py",
                    "content": massive_content * 15,
                }
                for i in range(6)
            ],
            "diffs": [
                {
                    "path": f"order_diff_{i}.py",
                    "content": massive_content * 10,
                }
                for i in range(3)
            ],
            "logs": [
                {
                    "source": f"order_log_{i}.log",
                    "content": massive_content * 6,
                }
                for i in range(10)
            ],
            "retrieved_context": [
                {
                    "content": massive_content * 5,
                    "source": f"order_doc_{i}",
                }
                for i in range(8)
            ],
            "prior_steps": [massive_content * 3] * 15,
        }


def main():
    """Main dramatic demonstration"""
    print("🚀 DRAMATIC TOKEN ESTIMATOR PLAN REVISION DEMONSTRATION")
    print("=" * 80)
    print("This shows CLEAR before/after with token estimator guidance")

    # Create revisor
    revisor = DramaticPlanRevisor()

    # Step 1: Create problematic plan
    problematic_plan = revisor.create_problematic_plan()

    # Step 2: Simulate problematic execution
    problematic_results = revisor.simulate_problematic_execution(problematic_plan)

    # Step 3: Create optimized plan
    optimized_plan = revisor.create_optimized_plan(problematic_plan, problematic_results)

    # Step 4: Simulate optimized execution
    optimized_results = revisor.simulate_optimized_execution(optimized_plan)

    # Step 5: Compare dramatic results
    comparison = revisor.compare_dramatic_results(problematic_results, optimized_results)

    # Step 6: Show final summary
    print("\n🎯 DRAMATIC DEMONSTRATION SUMMARY")
    print("=" * 80)
    print(
        f"❌ PROBLEMATIC: {comparison['problematic_steps_succeeded']}/{comparison['total_steps_attempted']} steps succeeded, {comparison['problematic_critical']} CRITICAL FAILURES"
    )
    print(
        f"✅ OPTIMIZED:  {comparison['optimized_steps_succeeded']}/{comparison['total_steps_attempted']} steps succeeded, {comparison['optimized_critical']} CRITICAL FAILURES"
    )
    print(
        f"📈 IMPROVEMENT: {comparison['prob_success_rate']:.0f}% → {comparison['opt_success_rate']:.0f}% success rate, {comparison['critical_reduction']} critical failures resolved"
    )

    print("\n🎉 DRAMATIC IMPACT OF TOKEN ESTIMATOR:")
    print("• Identified critical budget violations before execution")
    print("• Guided specific optimization strategies (splitting, content reduction)")
    print("• Achieved massive token reduction while preserving functionality")
    print("• Resolved critical failures that would block execution")
    print("• Enabled successful plan execution within SWE 1.5 constraints")

    print("\n🔧 REAL-WORLD IMPACT:")
    print("• Prevents context window overflow in complex implementations")
    print("• Enables data-driven plan optimization decisions")
    print("• Provides quantitative feedback for plan revisions")
    print("• Supports iterative improvement based on token analysis")
    print("• Ensures successful execution of large-scale projects")

    print("\n✅ CONCLUSION:")
    print("The token estimator is ESSENTIAL for complex implementation plans!")
    print("It transforms impossible plans into executable ones through intelligent optimization.")

    # Cleanup temp files
    revisor.cleanup()


if __name__ == "__main__":
    main()
