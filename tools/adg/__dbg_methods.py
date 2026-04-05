import subprocess
import sys

base = "tests/unit/agentic_core/L0_routing/scripts/test_sovereign_decision_engine.py"
cls = "TestShouldProceedWithHealing"

methods = [
    "test_budget_blocked_returns_safety_lock",
    "test_fail_closed_routing_blocked",
    "test_deterministic_routing_approves",
    "test_deterministic_increments_healing_count",
    "test_deterministic_adds_to_call_path",
    "test_decisions_made_grows",
    "test_conf_y_override_forces_gemini",
    "test_conf_x_override_to_qwen_for_listed_agent",
    "test_llm_disabled_does_not_block_qwen_routing",
    "test_llm_disabled_qwen_arbitration_fires_not_hitl",
]

for m in methods:
    path = f"{base}::{cls}::{m}"
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", path, "--tb=no", "-q", "--no-header"],
            capture_output=True,
            text=True,
            timeout=8,
            cwd="C:/Git/Agentic-Workflow",
        )
        out = (r.stdout + r.stderr).strip().split("\n")
        summary = [l for l in out if "passed" in l or "failed" in l or "error" in l]
        print(f"  {m}: {summary[-1] if summary else 'no summary'}")
    except (ValueError, TypeError, RuntimeError):
        print(f"  {m}: TIMEOUT (HANGS)")
