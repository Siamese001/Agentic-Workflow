import subprocess
import sys

base = "tests/unit/agentic_core/L0_routing/scripts"

files_classes = [
    (
        "test_sovereign_decision_engine.py",
        [
            "TestCheckHealingBudget",
            "TestCalculateHealingConfidence",
            "TestShouldProceedWithHealing",
            "TestClassifyViolationType",
            "TestComputeRoutingDecision",
            "TestAdvisoryBoundaryEnforcement",
        ],
    ),
    (
        "test_execute_ssot_healing_routing_fixes.py",
        [
            "TestQwenExceptionHandling",
            "TestGeminiBoundaryCondition",
            "TestSSOTModelConstants",
        ],
    ),
    (
        "test_execute_ssot_routing_matrix.py",
        [
            "TestMatrixDeterministic",
            "TestMatrixQwen",
            "TestMatrixGemini",
            "TestMatrixFailClosed",
            "TestMatrixReplayMode",
            "TestMatrixEdgeCases",
        ],
    ),
]

for fname, classes in files_classes:
    print(f"=== {fname} ===")
    for cls in classes:
        path = f"{base}/{fname}::{cls}"
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", path, "--tb=no", "-q", "--no-header"],
                capture_output=True,
                text=True,
                timeout=12,
                cwd="C:/Git/Agentic-Workflow",
            )
            out = (r.stdout + r.stderr).strip().split("\n")
            summary = [
                l for l in out if "passed" in l or "failed" in l or "error" in l or "no tests" in l.lower()
            ]
            print(f"  {cls}: {summary[-1] if summary else 'no summary'}")
        except (TimeoutError, ValueError, TypeError, RuntimeError):
            print(f"  {cls}: TIMEOUT (HANGS)")
