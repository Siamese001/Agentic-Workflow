# Phase 2 - Unsafe I/O and Subprocess Hardening Baseline

**Date:** 2026-02-22
**Phase:** Deterministic Mutation-Safety Hardening (Post-Fence Coverage Expansion)
**Wave:** 1 of 3 - Repo-Wide Detection + Baseline Evidence

---

## Executive Summary

This document provides the baseline evidence for unsafe I/O and subprocess usage detection in agent-executed code paths. The goal is to identify and remediate direct file I/O and subprocess primitives that could bypass the mutation fence and write to protected roots.

---

## Detector Design

### What It Flags

**File Write Operations:**
- `open(..., "w"/"a"/"x")` - Direct file writes
- `Path.write_text()` / `Path.write_bytes()` - Path-based writes
- `os.remove()` / `os.unlink()` - File deletions
- `os.rename()` / `os.replace()` - File moves/renames
- `shutil.rmtree()` - Directory deletions
- `shutil.move()` - Directory moves

**Subprocess Operations:**
- `subprocess.run()` - General subprocess execution
- `subprocess.call()` - Simple subprocess call
- `subprocess.check_call()` - Subprocess with error checking
- `subprocess.check_output()` - Subprocess with output capture
- `subprocess.Popen()` - Subprocess process creation

### What It Ignores

- Read-only operations (`open(..., "r")`, `Path.read_text()`)
- Path existence checks (`Path.exists()`, `os.path.exists()`)
- Safe string operations and data processing
- Import statements and function definitions

### Scope Coverage

The detector scans these scoped areas:
- `agentic_core/*/reasoning/**` - Agent execution code
- `agentic_core/*/tools/**` - Agent-invoked tool wrappers
- `agentic_core/*/scripts/**` - SSOT/entrypoints

---

## Baseline Findings

### Summary Statistics
- **Total Files Scanned:** 6 directories
- **Total Unsafe Patterns Found:** 69

### Detailed Findings by File

#### agentic_core/L0_routing/reasoning/ (2 findings)
```
RootCustomsAgent.py:564 - shutil_move
SSOTFolderCleanupAgent.py:411 - path_write_text
```

#### agentic_core/L2_execution/reasoning/ (4 findings)
```
ToolsmithAgent.py:355 - open_write
ToolsmithAgent.py:359 - open_write
ToolsmithAgent.py:362 - open_write
ToolsmithAgent.py:500 - path_write_text
```

#### agentic_core/L0_routing/scripts/ (62 findings)
```
add_dataclass_to_agents_util.py:119 - path_write_text
add_subatomic_safe_util.py:128 - path_write_text
add_subatomic_testing_to_agents_util.py:113 - path_write_text
add_subatomic_tests_util.py:147 - path_write_text
agent_analysis_config.py:308 - path_write_text
agent_capability_supplement_util.py:407 - path_write_text
align_tests_structure_util.py:42 - open_write
align_tests_structure_util.py:49 - open_write
archive_duplicate_tests_util.py:58 - shutil_move
archive_duplicates_util.py:48 - shutil_move
auto_remediate_signatures_util.py:138 - open_write
bulk_hierarchy_heal_util.py:54 - open_write
bulk_hierarchy_heal_util.py:69 - open_write
bulk_hierarchy_heal_util.py:102 - shutil_move
bulk_mcp_harden_util.py:62 - path_write_text
bulk_mcp_harden_util.py:80 - path_write_text
c_c_measurement.py:179 - open_write
check_protected_files_util.py:36 - subprocess_run
class_info.py:699 - open_write
class_info.py:733 - open_write
code_entity.py:541 - path_write_text
colors.py:152 - path_write_text
core_synthesis_executor.py:100 - shutil_move
core_synthesis_executor.py:247 - path_write_text
core_synthesis_executor.py:281 - shutil_move
core_synthesis_executor.py:361 - open_write
debris_hunter.py:86 - os_remove
disposition.py:437 - open_write
disposition.py:458 - open_write
emoji_fixer.py:53 - open_write
execute_ssot.py:291 - subprocess_run
execute_ssot.py:1335 - os_replace
execute_ssot.py:1344 - os_remove
execute_ssot.py:1481 - os_replace
execute_ssot.py:1489 - os_remove
execute_ssot.py:2379 - open_write
execute_ssot.py:2384 - open_write
extract_net.py:20 - shutil_rmtree
find_real_duplicates_v2_util.py:98 - open_write
fission_executor_util.py:50 - open_write
fission_executor_util.py:74 - os_replace
fission_executor_util.py:75 - open_write
flatten_scripts_directory_util.py:58 - shutil_move
forensic_discovery_prep.py:296 - subprocess_check_output
forensic_discovery_prep.py:310 - path_write_text
forensic_discovery_prep.py:311 - os_replace
full_agent_discovery.py:130 - subprocess_check_output
gatekeeper_lock_util.py:35 - subprocess_run
generate_dashboard_ssot_util.py:399 - open_write
generate_dashboard_ssot_util.py:413 - open_write
populate_ssot_folders_util.py:162 - path_write_text
populate_ssot_folders_util.py:172 - path_write_text
root_hygiene_util.py:58 - shutil_move
root_hygiene_util.py:70 - shutil_rmtree
root_hygiene_util.py:72 - shutil_move
root_hygiene_util.py:93 - shutil_rmtree
root_hygiene_util.py:97 - shutil_move
root_hygiene_util.py:111 - shutil_move
run_hygiene_guardian_util.py:115 - shutil_rmtree
scan_testing_compliance_util.py:348 - open_write
ssot_cli.py:168 - path_write_text
verify_intentional_variants_util.py:343 - open_write
```

#### agentic_core/L2_execution/scripts/ (1 finding)
```
remediation_dispatcher.py:528 - path_write_text
```

---

## False Positives Policy

The following patterns are considered acceptable and will be explicitly allowed:

1. **Utility Scripts** - Scripts in `agentic_core/*/scripts/` that are:
   - One-time migration or remediation tools
   - Development utilities that require direct file access
   - Not part of regular agent execution flow

2. **SSOT Operations** - `execute_ssot.py` operations that:
   - Use the mutation fence for protection
   - Have explicit `allow_protected_root_mutation` flag checks
   - Are part of the core SSOT infrastructure

3. **Tool Generation** - Agents that generate code/tools:
   - ToolsmithAgent creating new tools
   - Code generation that writes to non-protected areas
   - Output generation that respects dry_run flags

---

## High-Risk Findings Priority

The following findings are considered high-risk and should be remediated in Wave 2:

### Critical - Agent Reasoning Code
1. **ToolsmithAgent.py** (4 findings) - Direct file writes in agent reasoning
   - Lines 355, 359, 362: open_write operations
   - Line 500: path_write_text operation
   - **Risk:** Agent can bypass fence when generating tools

### Medium - SSOT Entry Points
2. **execute_ssot.py** (7 findings) - Core SSOT operations
   - Lines 1335, 1344, 1481, 1489: os_replace/os_remove operations
   - Lines 2379, 2384: open_write operations
   - Line 291: subprocess_run operation
   - **Risk:** Core infrastructure needs hardening

### Low - Utility Scripts
3. **Utility scripts** (58 findings) - Development and maintenance tools
   - Various file operations in utility scripts
   - **Risk:** Lower - these are not part of regular agent execution

---

## Next Steps

Wave 2 will focus on:
1. Remediating ToolsmithAgent direct writes through write_gateway
2. Adding safe_subprocess wrapper for execute_ssot.py operations
3. Documenting acceptable uses for utility scripts

---

## Detector Implementation

The detector is implemented in:
- `agentic_core/L2_execution/tools/unsafe_io_detector.py` - Core detection logic
- `tests/unit_min_deps/test_unsafe_io_subprocess_detector.py` - Test suite

The detector uses AST parsing to identify unsafe patterns and provides detailed reporting including file paths, line numbers, and pattern types.
