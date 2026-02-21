# Git HEAD
```ed78c0af90c1e71662a55eb038c86552ad653efb```

# Git Status
``````

# Assembly Stage Tests
```[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 12 items

tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_assemble_creates_governed_payload [32mPASSED[0m[32m [  8%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_same_inputs_produce_identical_manifest_hash [32mPASSED[0m[32m [ 16%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_changing_any_slot_changes_manifest_hash [32mPASSED[0m[32m [ 25%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_manifest_hash_is_sha256_hex [32mPASSED[0m[32m [ 33%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_payload_is_immutable [32mPASSED[0m[32m [ 41%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_d0_injections_default_and_custom [32mPASSED[0m[32m [ 50%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_sanitization_changes_text_and_sets_flag [32mPASSED[0m[32m [ 58%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_sanitization_no_op_sets_flag_false [32mPASSED[0m[32m [ 66%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_sanitization_changes_hash [32mPASSED[0m[32m [ 75%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_shred_produces_stable_sorted_check_ids [32mPASSED[0m[32m [ 83%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_shred_fallback_to_single_check_id [32mPASSED[0m[32m [ 91%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_shred_handles_empty_and_whitespace_lines [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m12 passed[0m[32m in 0.05s[0m[32m ==============================[0m
```

# All L0 Routing Tests
```[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 12 items

tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_assemble_creates_governed_payload [32mPASSED[0m[32m [  8%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_same_inputs_produce_identical_manifest_hash [32mPASSED[0m[32m [ 16%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_changing_any_slot_changes_manifest_hash [32mPASSED[0m[32m [ 25%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_manifest_hash_is_sha256_hex [32mPASSED[0m[32m [ 33%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_payload_is_immutable [32mPASSED[0m[32m [ 41%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_d0_injections_default_and_custom [32mPASSED[0m[32m [ 50%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_sanitization_changes_text_and_sets_flag [32mPASSED[0m[32m [ 58%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_sanitization_no_op_sets_flag_false [32mPASSED[0m[32m [ 66%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_sanitization_changes_hash [32mPASSED[0m[32m [ 75%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_shred_produces_stable_sorted_check_ids [32mPASSED[0m[32m [ 83%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_shred_fallback_to_single_check_id [32mPASSED[0m[32m [ 91%][0m
tests/unit/L0_routing/test_assembly_stage.py::TestAssemblyStage::test_shred_handles_empty_and_whitespace_lines [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m12 passed[0m[32m in 0.04s[0m[32m ==============================[0m
```

# Wall-Clock Token Scan
```No forbidden wall-clock tokens found```

# Git Show --stat
```commit ed78c0af90c1e71662a55eb038c86552ad653efb
Author: Siamese001 <siamese001@users.noreply.github.com>
Date:   Sat Feb 21 08:42:38 2026 -0500

    docs: phase2 Assembly Stage evidence bundle (Phase 2.3)

 .../plans/phase2_assembly_stage_evidence.md        |  76 ++++++++++++
 tools/evidence/phase2_assembly_stage_evidence.py   | 133 +++++++++++++++++++++
 2 files changed, 209 insertions(+)
```
