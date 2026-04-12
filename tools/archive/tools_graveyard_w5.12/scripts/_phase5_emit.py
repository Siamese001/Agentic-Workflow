import json
from pathlib import Path

repairs = [
    {
        "cluster_id": "A",
        "file": "agentic_core/L0_routing/scripts/execute_ssot.py",
        "line": 7369,
        "change": "Added RuntimeError to except clause in run_pipeline subphase dispatcher",
        "old": "except (ImportError, AttributeError, TypeError, ValueError) as exc:",
        "new": "except (ImportError, AttributeError, TypeError, ValueError, RuntimeError) as exc:",
        "adg_justification": "TestFailClosedOnException mocks adapter.validate.side_effect=RuntimeError; run_pipeline must catch it fail-closed",
        "tests_fixed": 7,
        "category": "API_DRIFT",
    },
    {
        "cluster_id": "B",
        "file": "tests/invariants/test_gap_a_b_wire_in.py",
        "line": "10-18",
        "change": "Added missing imports: AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR from path_constants",
        "old": "import json",
        "new": "import json\nfrom agentic_core.L0_routing.config.path_constants import (AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR)",
        "adg_justification": "ADG chain: test_gap_a_b_wire_in -> path_constants (first-ring); constants used bare at lines 23 and 50",
        "tests_fixed": 2,
        "category": "IMPORT_PATH_ERROR",
    },
    {
        "cluster_id": "C",
        "file": "agentic_core/L0_routing/scripts/execute_ssot.py",
        "line": 267,
        "change": "Replaced bare 'decision_engine' name with state_mgr.state.get('routing_decisions', [])",
        "old": "for _dec in getattr(decision_engine, 'decisions_made', []):",
        "new": "_routing_decisions = state_mgr.state.get('routing_decisions', []) ...; for _dec in _routing_decisions:",
        "adg_justification": "_fire_meta_learning_intake is a top-level function; decision_engine not in scope; callers pass (state_mgr, now_utc) only",
        "tests_fixed": 1,
        "category": "API_DRIFT",
    },
    {
        "cluster_id": "D_pythonpath",
        "file": "agentic_core/L0_routing/scripts/execute_ssot.py",
        "line": "1902-1918",
        "change": "Inject PYTHONPATH={repo_root_wsl}:$PYTHONPATH into WSL bash command",
        "old": 'f"{WSL_PYTHON} {script_wsl}..."',
        "new": 'f"PYTHONPATH={repo_root_wsl}:$PYTHONPATH {WSL_PYTHON} {script_wsl}..."',
        "adg_justification": "_arbiter launches qwen_vllm_inference.py in WSL without PYTHONPATH; agentic_core not importable",
        "tests_fixed": 1,
        "category": "IMPORT_PATH_ERROR",
    },
    {
        "cluster_id": "D_qwen_deny",
        "file": "agentic_core/L0_routing/scripts/execute_ssot.py",
        "line": "2323-2342",
        "change": "QWEN tier: when qwen_approved=False, return (False, reason) without adding to _call_path",
        "old": "Unconditionally adds agent_name to _call_path and returns True",
        "new": "if qwen_approved: return True+add_to_path; else: return False without add_to_path",
        "adg_justification": "test_e2e_05 expects Agent3 not in _call_path when Qwen denies; _call_path tracks approved ops only",
        "tests_fixed": 1,
        "category": "API_DRIFT",
    },
    {
        "cluster_id": "E_enable_llm",
        "file": "agentic_core/L0_routing/scripts/execute_ssot.py",
        "line": "2344-2352",
        "change": "GEMINI tier: when enable_llm=False, return (False, 'Manual Review Required: ...')",
        "old": "GEMINI tier unconditionally returns True",
        "new": "if not self.enable_llm: return False with Manual Review Required message",
        "adg_justification": "test_e2e_08 uses engine(enable_llm=False), confidence=0.4 -> GEMINI tier; expects False",
        "tests_fixed": 1,
        "category": "API_DRIFT",
    },
    {
        "cluster_id": "E_save",
        "file": "tests/e2e/agentic_core/L0_maintenance/misc/test_ssot_e2e_reporting.py",
        "line": 126,
        "change": "Added monkeypatch.setenv('AGENTIC_ALLOW_MUTATION_FOR_TESTS', '1') in test_e2e_03",
        "old": "def test_e2e_03_state_persistence_crash_recovery(self, tmp_path):",
        "new": "def test_e2e_03_state_persistence_crash_recovery(self, tmp_path, monkeypatch): + monkeypatch.setenv(...)",
        "adg_justification": "RuntimeStateManager.save() blocked by G-12-1 mutation prohibition; AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 is the documented test override",
        "tests_fixed": 1,
        "category": "ASSERTION_MISMATCH",
    },
]

total_fixed = sum(r["tests_fixed"] for r in repairs)
out = Path("artifacts/execute_ssot_repair_log.json")
out.write_text(
    json.dumps(
        {
            "repairs": repairs,
            "total_fixed": total_fixed,
            "total_failures_before": 15,
            "remaining": 15 - total_fixed,
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(f"PHASE 5 artifact written. {total_fixed} tests fixed across {len(repairs)} repairs.")
