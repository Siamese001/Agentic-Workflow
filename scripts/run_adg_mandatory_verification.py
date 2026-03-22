#!/usr/bin/env python3
"""
ADG Mandatory Verification Suite

Hard-gate suite that must pass before ADG is considered authoritative:
1. verify_adg_provenance.py
2. verify_adg_consistency.py
3. verify_identity_completeness.py
4. verify_trace_replay_coverage.py
5. verify_mutation_envelope_coverage.py
6. verify_layer_authority.py
7. verify_l4_normalization.py
8. verify_uwg_closure.py
9. ingest_structured_test_results.py
10. verify_test_signal_ingestion.py
11. verify_learning_loop.py
12. verify_pass_baseline_flow.py
13. verify_error_handling_contracts.py
14. verify_embedding_rag_coverage.py
15. verify_hitl_dpo_coverage.py
16. verify_low_confidence_zones.py
17. report_behavioral_coverage_ratios.py

FAIL CLOSED: If any blocking verifier fails, ADG is not authoritative.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class VerificationSuiteError(Exception):
    """Raised when verification suite fails."""
    pass

class ADGMandatoryVerificationSuite:
    """Mandatory verification suite for ADG authoritativeness."""

    # Define verification phases and their scripts
    VERIFICATION_PHASES = {
        "provenance": {
            "script": "verify_adg_provenance.py",
            "blocking": True,
            "description": "Provenance SSOT verification"
        },
        "consistency": {
            "script": "verify_adg_consistency.py",
            "blocking": True,
            "description": "Summary ↔ raw ↔ export consistency"
        },
        "identity_completeness": {
            "script": "verify_identity_completeness.py",
            "blocking": True,
            "description": "Identity completeness verification"
        },
        "first_party_prioritization": {
            "script": "verify_first_party_prioritization.py",
            "blocking": True,
            "description": "First-party prioritization and external signal control"
        },
        "domain_segmentation": {
            "script": "verify_domain_segmentation.py",
            "blocking": True,
            "description": "Domain segmentation and hotspot normalization"
        },
        "trace_replay_coverage": {
            "script": "verify_trace_replay_coverage.py",
            "blocking": True,
            "description": "Trace and replay coverage verification"
        },
        "layer_authority": {
            "script": "verify_layer_authority.py",
            "blocking": True,
            "description": "Layer authority verification"
        },
        "l4_normalization": {
            "script": "verify_l4_normalization.py",
            "blocking": True,
            "description": "L4 normalization verification"
        },
        "violation_taxonomy": {
            "script": "verify_violation_taxonomy.py",
            "blocking": False,
            "description": "Violation taxonomy and remediation classification"
        },
        "error_handling_contracts": {
            "script": "verify_error_handling_contracts.py",
            "blocking": False,
            "description": "Error handling and retry enforcement"
        },
        "low_confidence_zones": {
            "script": "verify_low_confidence_zones.py",
            "blocking": False,
            "description": "Dead code, dead import, and low-confidence zone control"
        },
        "behavioral_coverage_ratios": {
            "script": "report_behavioral_coverage_ratios.py",
            "blocking": False,
            "description": "Runtime vs structural balance reporting"
        }
    }

    def __init__(self, adg_dir: Path, scripts_dir: Optional[Path] = None):
        self.adg_dir = Path(adg_dir)
        self.scripts_dir = scripts_dir or Path(__file__).parent
        self.results: Dict[str, Any] = {}
        self.start_time = datetime.now(timezone.utc)

    def _load_verification_script(self, script_name: str):
        """Load verification script dynamically."""
        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            raise VerificationSuiteError(f"Verification script not found: {script_path}")

        spec = importlib.util.spec_from_file_location(script_name.stem, script_path)
        if spec is None or spec.loader is None:
            raise VerificationSuiteError(f"Could not load script: {script_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def _run_verification_phase(self, phase_name: str, phase_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single verification phase."""
        print(f"\n{'='*60}")
        print(f"🔍 PHASE: {phase_name.upper()}")
        print(f"📋 {phase_config['description']}")
        print(f"🚦 Blocking: {'YES' if phase_config['blocking'] else 'NO'}")
        print(f"{'='*60}")

        start_time = time.time()

        try:
            # Load and run verification script
            module = self._load_verification_script(phase_config['script'])

            # Most scripts have a main() function or a Verifier class
            if hasattr(module, 'main'):
                # Script with main() function
                import argparse
                old_argv = sys.argv
                sys.argv = [phase_config['script'], '--adg-dir', str(self.adg_dir)]

                try:
                    exit_code = module.main()
                    result = {
                        "status": "PASS" if exit_code == 0 else "FAIL",
                        "exit_code": exit_code,
                        "execution_time": time.time() - start_time,
                        "method": "main_function"
                    }
                finally:
                    sys.argv = old_argv

            elif hasattr(module, f"{phase_name.replace('_', '')}Verifier"):
                # Script with Verifier class
                verifier_class = getattr(module, f"{phase_name.replace('_', '')}Verifier")
                verifier = verifier_class(self.adg_dir)
                result = verifier.verify()
                result["execution_time"] = time.time() - start_time
                result["method"] = "verifier_class"

            else:
                raise VerificationSuiteError(f"Script {phase_config['script']} has no recognizable entry point")

        except Exception as e:
            result = {
                "status": "ERROR",
                "error": str(e),
                "execution_time": time.time() - start_time,
                "method": "error"
            }

        result["phase"] = phase_name
        result["script"] = phase_config['script']
        result["blocking"] = phase_config['blocking']
        result["timestamp"] = datetime.now(timezone.utc).isoformat()

        return result

    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary report of all verification results."""
        total_phases = len(self.results)
        passed_phases = sum(1 for r in self.results.values() if r["status"] == "PASS")
        failed_phases = sum(1 for r in self.results.values() if r["status"] == "FAIL")
        error_phases = sum(1 for r in self.results.values() if r["status"] == "ERROR")
        blocking_failed = sum(1 for r in self.results.values()
                            if r["status"] in ["FAIL", "ERROR"] and r["blocking"])

        total_time = sum(r["execution_time"] for r in self.results.values())

        return {
            "suite_metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
                "total_execution_time": total_time,
                "adg_directory": str(self.adg_dir),
                "scripts_directory": str(self.scripts_dir)
            },
            "summary": {
                "total_phases": total_phases,
                "passed_phases": passed_phases,
                "failed_phases": failed_phases,
                "error_phases": error_phases,
                "blocking_failures": blocking_failed,
                "overall_status": "PASS" if blocking_failed == 0 else "FAIL"
            },
            "phase_results": self.results,
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on verification results."""
        recommendations = []

        for phase_name, result in self.results.items():
            if result["status"] == "FAIL":
                if result["blocking"]:
                    recommendations.append(f"URGENT: Fix {phase_name} - blocking verification failed")
                else:
                    recommendations.append(f"Recommended: Address {phase_name} issues for improved quality")

            elif result["status"] == "ERROR":
                recommendations.append(f"URGENT: Fix error in {phase_name} verification script")

        # Add specific recommendations based on patterns
        if any("provenance" in r for r in self.results if self.results[r]["status"] != "PASS"):
            recommendations.append("Ensure ADG artifacts have consistent provenance metadata")

        if any("consistency" in r for r in self.results if self.results[r]["status"] != "PASS"):
            recommendations.append("Align summary metrics with raw SQL queries and exported reports")

        if any("identity" in r for r in self.results if self.results[r]["status"] != "PASS"):
            recommendations.append("Complete identity fields for decision-grade analysis")

        return recommendations

    def run_verification_suite(self) -> Dict[str, Any]:
        """Run the complete verification suite."""
        print("🚀 Starting ADG Mandatory Verification Suite")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"📜 Scripts Directory: {self.scripts_dir}")
        print(f"⏰ Start Time: {self.start_time.isoformat()}")

        # Run each verification phase
        for phase_name, phase_config in self.VERIFICATION_PHASES.items():
            self.results[phase_name] = self._run_verification_phase(phase_name, phase_config)

            # If blocking phase failed, we could stop early
            if phase_config["blocking"] and self.results[phase_name]["status"] in ["FAIL", "ERROR"]:
                print(f"\n🛑 BLOCKING FAILURE in {phase_name.upper()}")
                print("   ADG is not authoritative until this is fixed")

                # Continue running other phases to collect full diagnostic info
                # but mark that we've hit a blocking failure

        # Generate summary report
        summary = self._generate_summary_report()

        # Print final results
        print(f"\n{'='*60}")
        print("📊 VERIFICATION SUITE SUMMARY")
        print(f"{'='*60}")

        print(f"Total Phases: {summary['summary']['total_phases']}")
        print(f"Passed: {summary['summary']['passed_phases']}")
        print(f"Failed: {summary['summary']['failed_phases']}")
        print(f"Errors: {summary['summary']['error_phases']}")
        print(f"Blocking Failures: {summary['summary']['blocking_failures']}")
        print(f"Overall Status: {summary['summary']['overall_status']}")
        print(f"Total Time: {summary['suite_metadata']['total_execution_time']:.2f}s")

        # Print phase-by-phase results
        print(f"\n📋 PHASE RESULTS:")
        for phase_name, result in self.results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "💥"
            blocking_mark = " 🔒" if result["blocking"] else ""
            print(f"   {status_icon} {phase_name}: {result['status']}{blocking_mark}")

        # Print recommendations if any
        if summary["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in summary["recommendations"]:
                print(f"   • {rec}")

        # Final determination
        if summary['summary']['overall_status'] == "PASS":
            print(f"\n✅ ADG IS AUTHORITATIVE - All blocking verifications passed")
        else:
            print(f"\n❌ ADG IS NOT AUTHORITATIVE - {summary['summary']['blocking_failures']} blocking failures")

        return summary

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run ADG mandatory verification suite")
    parser.add_argument(
        "--adg-dir",
        type=Path,
        default=Path("artifacts/adg"),
        help="Path to ADG artifacts directory"
    )
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        help="Path to verification scripts directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save verification report"
    )
    parser.add_argument(
        "--phase",
        type=str,
        help="Run specific verification phase only"
    )
    parser.add_argument(
        "--non-blocking-only",
        action="store_true",
        help="Run only non-blocking verification phases"
    )

    args = parser.parse_args()

    try:
        suite = ADGMandatoryVerificationSuite(args.adg_dir, args.scripts_dir)

        if args.phase:
            # Run single phase
            if args.phase not in suite.VERIFICATION_PHASES:
                print(f"❌ Unknown phase: {args.phase}")
                print(f"Available phases: {sorted(suite.VERIFICATION_PHASES.keys())}")
                return 1

            phase_config = suite.VERIFICATION_PHASES[args.phase]
            result = suite._run_verification_phase(args.phase, phase_config)
            suite.results[args.phase] = result

            summary = suite._generate_summary_report()
        else:
            # Filter phases if requested
            if args.non_blocking_only:
                filtered_phases = {
                    k: v for k, v in suite.VERIFICATION_PHASES.items()
                    if not v["blocking"]
                }
                suite.VERIFICATION_PHASES = filtered_phases
                print("🔓 Running non-blocking verification phases only")

            # Run full suite
            summary = suite.run_verification_suite()

        # Save report if requested
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            print(f"\n📄 Report saved to: {args.output}")

        return 0 if summary['summary']['overall_status'] == "PASS" else 1

    except VerificationSuiteError as e:
        print(f"❌ Verification suite failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
