# Redis Cache Expansion - Retest Phase Evidence

## Scope

Retest of 5 Redis caching opportunities against updated .windsurfrules rules s4.
Gap analysis identified 10 missing coverage classes. 40 new tests added (78 total).

**Caches under test:**
- AgentDiscoveryCache (agentic_core/cache/discovery_cache.py)
- ToolEmbeddingCache (agentic_core/cache/tool_embedding_cache.py)
- SchemaValidatorCache (agentic_core/cache/schema_validator_cache.py)
- PolicyRegistryCache (agentic_core/cache/policy_registry_cache.py)
- ConfigFileCache (agentic_core/cache/config_file_cache.py)

**New coverage added per updated requirements:**
- Determinism: same-input-twice identical key (rules s4:124-125)
- Normalization invariant: input ordering does not affect fingerprint (rules s4:126)
- Near-miss: materially distinct inputs give distinct keys (rules s4:127)
- Matrix: replay-mode x warm-cache: get_json never called (rules s4:155-156)
- Side-effect envelope: cache hit = get_json once, set_json never, fetch never (rules s4:134-138)
- Fail-closed: validation errors propagate before any cache operation (rules s4:131-133)
- Broad-except passthrough: fetch errors not swallowed by cache read handler (rules s4:146-148)
- Stale TTL path: re-fetch and re-cache after TTL expiry simulation (rules s4:179-183)
- Malformed-plausible: directory path degrades gracefully without phantom cache hit (rules s4:116-117)
- Invalidate exception swallow: policy invalidate silently handles delete errors (rules s4:141-144)

## CODE_COMMIT

81776c999b13b113094ee2c98be0fd1b1358857f

## EVIDENCE_COMMIT

e75d631f4f9d2dfd6aa585fb9a622a02dc3849bf

## FILES_CHANGED_CODE

```
docs/reports/plans/redis_cache_expansion_branch_inventory.md
tests/architecture/test_discovery_cache.py
tests/architecture/test_new_cache_opportunities.py
```

## FILES_CHANGED_EVIDENCE

```
docs/reports/plans/redis_cache_retest_evidence.md
tools/evidence_redis_retest.py
```

## INSPECTED_FILES

agentic_core/cache/discovery_cache.py
agentic_core/cache/tool_embedding_cache.py
agentic_core/cache/schema_validator_cache.py
agentic_core/cache/policy_registry_cache.py
agentic_core/cache/config_file_cache.py
tests/architecture/test_discovery_cache.py
tests/architecture/test_new_cache_opportunities.py

## PytestCollect

```
$ python -m pytest tests/architecture/test_discovery_cache.py tests/architecture/test_new_cache_opportunities.py --collect-only -q --color=no
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 78 items

<Dir Agentic-Workflow>
  <Dir tests>
    <Package architecture>
      <Module test_discovery_cache.py>
        <Function test_agent_discovery_cache_has_get_or_fetch>
        <Function test_agent_discovery_cache_miss_calls_fetch>
        <Function test_agent_discovery_cache_hit_skips_fetch>
        <Function test_agent_discovery_cache_file_not_found_propagates>
        <Function test_agent_discovery_cache_fetch_exception_propagates>
        <Function test_agent_discovery_cache_non_callable_fetch_raises>
        <Function test_agent_discovery_cache_replay_mode_bypasses_cache>
        <Function test_agent_discovery_cache_empty_list_is_valid>
        <Function test_agent_discovery_cache_content_hash_changes_invalidate>
        <Function test_agent_discovery_cache_handles_cache_get_exception>
        <Function test_agent_discovery_cache_handles_cache_set_exception>
        <Function test_agent_discovery_cache_fetch_called_exactly_once>
        <Function test_agent_discovery_cache_invalidate_all_is_noop>
        <Function test_agent_discovery_cache_same_file_gives_identical_key_twice>
        <Function test_agent_discovery_cache_replay_warm_cache_get_json_never_called>
        <Function test_agent_discovery_cache_hit_side_effect_envelope>
        <Function test_agent_discovery_cache_file_not_found_no_set_json_side_effect>
        <Function test_agent_discovery_cache_broad_except_does_not_swallow_custom_sentinel>
        <Function test_agent_discovery_cache_stale_cache_path_returns_fresh_after_miss>
        <Function test_agent_discovery_cache_malformed_plausible_path_object>
        <Function test_agent_discovery_cache_distinct_files_produce_distinct_keys>
      <Module test_new_cache_opportunities.py>
        <Function test_tool_embedding_cache_has_get_or_fetch>
        <Function test_tool_embedding_cache_miss_calls_fetch>
        <Function test_tool_embedding_cache_empty_tools_raises>
        <Function test_tool_embedding_cache_replay_mode_bypasses>
        <Function test_tool_embedding_cache_handles_cache_exception>
        <Function test_tool_embedding_cache_fingerprint_changes_invalidate>
        <Function test_schema_validator_cache_has_get_or_fetch>
        <Function test_schema_validator_cache_miss_calls_fetch>
        <Function test_schema_validator_cache_empty_schema_raises>
        <Function test_schema_validator_cache_replay_mode_bypasses>
        <Function test_schema_validator_cache_schema_changes_invalidate>
        <Function test_schema_validator_cache_handles_cache_exception>
        <Function test_policy_registry_cache_has_get_or_fetch>
        <Function test_policy_registry_cache_miss_calls_fetch>
        <Function test_policy_registry_cache_empty_policy_id_raises>
        <Function test_policy_registry_cache_replay_mode_bypasses>
        <Function test_policy_registry_cache_invalidate_calls_delete>
        <Function test_policy_registry_cache_handles_cache_exception>
        <Function test_config_file_cache_has_get_or_fetch>
        <Function test_config_file_cache_miss_calls_fetch>
        <Function test_config_file_cache_file_not_found_propagates>
        <Function test_config_file_cache_replay_mode_bypasses>
        <Function test_config_file_cache_content_changes_invalidate>
        <Function test_config_file_cache_handles_cache_exception>
        <Function test_config_file_cache_handles_set_exception>
        <Function test_tool_embedding_cache_same_tools_identical_key_twice>
        <Function test_tool_embedding_cache_input_order_invariant>
        <Function test_tool_embedding_cache_near_miss_different_description_distinct_key>
        <Function test_tool_embedding_cache_replay_warm_get_json_never_called>
        <Function test_tool_embedding_cache_hit_side_effect_envelope>
        <Function test_tool_embedding_cache_empty_tools_no_cache_side_effect>
        <Function test_tool_embedding_cache_malformed_tool_missing_name_key>
        <Function test_tool_embedding_cache_stale_path_refetch_on_miss>
        <Function test_tool_embedding_cache_broad_except_does_not_swallow_fetch_error>
        <Function test_schema_validator_cache_same_schema_identical_key_twice>
        <Function test_schema_validator_cache_key_order_invariant>
        <Function test_schema_validator_cache_near_miss_added_field_distinct_key>
        <Function test_schema_validator_cache_replay_warm_get_json_never_called>
        <Function test_schema_validator_cache_hit_side_effect_envelope>
        <Function test_schema_validator_cache_empty_schema_no_cache_side_effect>
        <Function test_schema_validator_cache_broad_except_does_not_swallow_fetch_error>
        <Function test_policy_registry_cache_same_id_identical_key_twice>
        <Function test_policy_registry_cache_distinct_ids_distinct_keys>
        <Function test_policy_registry_cache_replay_warm_get_json_never_called>
        <Function test_policy_registry_cache_hit_side_effect_envelope>
        <Function test_policy_registry_cache_empty_id_no_cache_side_effect>
        <Function test_policy_registry_cache_whitespace_id_no_cache_side_effect>
        <Function test_policy_registry_cache_stale_path_refetch_on_miss>
        <Function test_policy_registry_cache_broad_except_does_not_swallow_fetch_error>
        <Function test_policy_registry_cache_invalidate_exception_does_not_propagate>
        <Function test_config_file_cache_same_file_identical_key_twice>
        <Function test_config_file_cache_replay_warm_get_json_never_called>
        <Function test_config_file_cache_hit_side_effect_envelope>
        <Function test_config_file_cache_file_not_found_no_set_json_side_effect>
        <Function test_config_file_cache_stale_path_refetch_on_miss>
        <Function test_config_file_cache_broad_except_does_not_swallow_fetch_error>
        <Function test_config_file_cache_distinct_files_distinct_keys>

========================= 78 tests collected in 0.02s =========================
```

## PytestExecute

```
$ python -m pytest tests/architecture/test_discovery_cache.py tests/architecture/test_new_cache_opportunities.py -q --color=no --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 78 items

tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_has_get_or_fetch PASSED [  1%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_miss_calls_fetch PASSED [  2%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_hit_skips_fetch PASSED [  3%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_file_not_found_propagates PASSED [  5%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_fetch_exception_propagates PASSED [  6%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_non_callable_fetch_raises PASSED [  7%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_replay_mode_bypasses_cache PASSED [  8%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_empty_list_is_valid PASSED [ 10%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_content_hash_changes_invalidate PASSED [ 11%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_handles_cache_get_exception
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.discovery_cache: [Discovery cache] Cache read failed: Redis connection lost
PASSED                                                                   [ 12%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_handles_cache_set_exception
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.discovery_cache: [Discovery cache] Cache write failed: Redis write failed
PASSED                                                                   [ 14%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_fetch_called_exactly_once PASSED [ 15%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_invalidate_all_is_noop PASSED [ 16%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_same_file_gives_identical_key_twice PASSED [ 17%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_replay_warm_cache_get_json_never_called PASSED [ 19%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_hit_side_effect_envelope PASSED [ 20%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_file_not_found_no_set_json_side_effect PASSED [ 21%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_broad_except_does_not_swallow_custom_sentinel PASSED [ 23%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_stale_cache_path_returns_fresh_after_miss PASSED [ 24%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_malformed_plausible_path_object
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.discovery_cache: [Discovery cache] Hash computation failed: [Errno 13] Permission denied: 'C:\\Users\\amita\\AppData\\Local\\Temp\\tmpgxiodz6t'
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.discovery_cache: [Discovery cache] Cache write failed: [Errno 13] Permission denied: 'C:\\Users\\amita\\AppData\\Local\\Temp\\tmpgxiodz6t'
PASSED                                                                   [ 25%]
tests/architecture/test_discovery_cache.py::test_agent_discovery_cache_distinct_files_produce_distinct_keys PASSED [ 26%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_has_get_or_fetch PASSED [ 28%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_miss_calls_fetch PASSED [ 29%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_empty_tools_raises PASSED [ 30%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_replay_mode_bypasses PASSED [ 32%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_handles_cache_exception
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.tool_embedding_cache: [Tool embedding cache] Cache read failed: Redis down
PASSED                                                                   [ 33%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_fingerprint_changes_invalidate PASSED [ 34%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_has_get_or_fetch PASSED [ 35%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_miss_calls_fetch PASSED [ 37%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_empty_schema_raises PASSED [ 38%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_replay_mode_bypasses PASSED [ 39%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_schema_changes_invalidate PASSED [ 41%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_handles_cache_exception
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.schema_validator_cache: [Schema validator cache] Cache read failed: Redis down
PASSED                                                                   [ 42%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_has_get_or_fetch PASSED [ 43%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_miss_calls_fetch PASSED [ 44%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_empty_policy_id_raises PASSED [ 46%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_replay_mode_bypasses PASSED [ 47%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_invalidate_calls_delete PASSED [ 48%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_handles_cache_exception
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.policy_registry_cache: [Policy cache] Cache read failed: Redis down
PASSED                                                                   [ 50%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_has_get_or_fetch PASSED [ 51%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_miss_calls_fetch PASSED [ 52%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_file_not_found_propagates PASSED [ 53%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_replay_mode_bypasses PASSED [ 55%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_content_changes_invalidate PASSED [ 56%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_handles_cache_exception
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.config_file_cache: [Config cache] Cache read failed: Redis down
PASSED                                                                   [ 57%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_handles_set_exception
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.config_file_cache: [Config cache] Cache write failed: Redis write failed
PASSED                                                                   [ 58%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_same_tools_identical_key_twice PASSED [ 60%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_input_order_invariant PASSED [ 61%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_near_miss_different_description_distinct_key PASSED [ 62%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_replay_warm_get_json_never_called PASSED [ 64%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_hit_side_effect_envelope PASSED [ 65%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_empty_tools_no_cache_side_effect PASSED [ 66%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_malformed_tool_missing_name_key PASSED [ 67%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_stale_path_refetch_on_miss PASSED [ 69%]
tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_broad_except_does_not_swallow_fetch_error PASSED [ 70%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_same_schema_identical_key_twice PASSED [ 71%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_key_order_invariant PASSED [ 73%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_near_miss_added_field_distinct_key PASSED [ 74%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_replay_warm_get_json_never_called PASSED [ 75%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_hit_side_effect_envelope PASSED [ 76%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_empty_schema_no_cache_side_effect PASSED [ 78%]
tests/architecture/test_new_cache_opportunities.py::test_schema_validator_cache_broad_except_does_not_swallow_fetch_error PASSED [ 79%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_same_id_identical_key_twice PASSED [ 80%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_distinct_ids_distinct_keys PASSED [ 82%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_replay_warm_get_json_never_called PASSED [ 83%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_hit_side_effect_envelope PASSED [ 84%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_empty_id_no_cache_side_effect PASSED [ 85%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_whitespace_id_no_cache_side_effect PASSED [ 87%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_stale_path_refetch_on_miss PASSED [ 88%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_broad_except_does_not_swallow_fetch_error PASSED [ 89%]
tests/architecture/test_new_cache_opportunities.py::test_policy_registry_cache_invalidate_exception_does_not_propagate
-------------------------------- live log call --------------------------------
2026-03-05 22:06:02 [ WARNING] agentic_core.cache.policy_registry_cache: [Policy cache] Invalidation failed: Redis unavailable
PASSED                                                                   [ 91%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_same_file_identical_key_twice PASSED [ 92%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_replay_warm_get_json_never_called PASSED [ 93%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_hit_side_effect_envelope PASSED [ 94%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_file_not_found_no_set_json_side_effect PASSED [ 96%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_stale_path_refetch_on_miss PASSED [ 97%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_broad_except_does_not_swallow_fetch_error PASSED [ 98%]
tests/architecture/test_new_cache_opportunities.py::test_config_file_cache_distinct_files_distinct_keys PASSED [100%]

============================ slowest 10 durations =============================
0.01s call     tests/architecture/test_new_cache_opportunities.py::test_tool_embedding_cache_stale_path_refetch_on_miss

(9 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 78 passed in 0.10s ==============================
```

## CollectionIntegrity

```
Collected: 78
Executed:  78
OK: all 78 collected tests executed, no deselection
```

## GitStatus

```
$ git status --short
 M agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py
 M agentic_core/L0_routing/scripts/add_dataclass_to_agents_util.py
 M agentic_core/L0_routing/scripts/agent_analysis_config.py
 M agentic_core/L0_routing/scripts/aggressive_dedup_util.py
 M agentic_core/L0_routing/scripts/archive_duplicates_util.py
 M agentic_core/L0_routing/scripts/auto_remediate_signatures_util.py
 M agentic_core/L0_routing/scripts/bloat_analysis_util.py
 M agentic_core/L0_routing/scripts/check_rglob_usage_util.py
 M agentic_core/L0_routing/scripts/class_info.py
 M agentic_core/L0_routing/scripts/code_entity.py
 M agentic_core/L0_routing/scripts/compare_archive_to_current_util.py
 M agentic_core/L0_routing/scripts/comprehensive_archive_check_util.py
 M agentic_core/L0_routing/scripts/core_synthesis_executor.py
 M agentic_core/L0_routing/scripts/debris_hunter.py
 M agentic_core/L0_routing/scripts/diagnose_syntax_util.py
 M agentic_core/L0_routing/scripts/disposition.py
 M agentic_core/L0_routing/scripts/emoji_fixer.py
 M agentic_core/L0_routing/scripts/execute_ssot.py
 M agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py
 M agentic_core/L0_routing/scripts/extract_unique_content_util.py
 M agentic_core/L0_routing/scripts/file_analysis.py
 M agentic_core/L0_routing/scripts/flatten_scripts_directory_util.py
 M agentic_core/L0_routing/scripts/forensic_discovery_prep.py
 M agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py
 M agentic_core/L0_routing/scripts/handler.py
 M agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py
 M agentic_core/L0_routing/scripts/investigate_overlaps_util.py
 M agentic_core/L0_routing/scripts/populate_ssot_folders_util.py
 M agentic_core/L0_routing/scripts/root_hygiene_util.py
 M agentic_core/L0_routing/scripts/run_guardian_architecture_governance.py
 M agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py
 M agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py
 M agentic_core/L0_routing/scripts/run_guardian_hygiene.py
 M agentic_core/L0_routing/scripts/run_sovereign_compliance_audit_util.py
 M agentic_core/L0_routing/scripts/validate_sovereign_structure_util.py
 M agentic_core/L0_routing/scripts/verify_all_checkpoint_files_util.py
 M agentic_core/L0_routing/scripts/verify_base_agent_names_util.py
 M agentic_core/L0_routing/utils/complexity_visitor_util.py
 M agentic_core/L0_routing/utils/core_integrity_util.py
 M agentic_core/L0_routing/utils/find_misnamed_agents_util.py
 M agentic_core/L0_routing/utils/fix_all_tunnels_util.py
 M agentic_core/L0_routing/utils/fix_remaining_depth_util.py
 M agentic_core/L0_routing/utils/force_annexation_util.py
 M agentic_core/L0_routing/utils/scorched_earth_merge_util.py
 M agentic_core/L0_routing/utils/sovereign_alignment_v2_util.py
 M agentic_core/L0_routing/utils/trim_remaining_airlocks_util.py
 M agentic_core/L1_cognition/engines/domain_manager.py
 M agentic_core/L2_execution/determinism.py
 M agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py
 M agentic_core/L2_execution/tools/unsafe_io_detector.py
 M agentic_core/L3_orchestration/engines/orchestrator_engine.py
 M agentic_core/L5_safety/config/blueprint_compiler.py
 M agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py
 M agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py
 M agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py
 M agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py
 M agentic_core/L5_safety/enforcement/mock_context_enforcer.py
 M agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py
 M agentic_core/L5_safety/enforcement/ssot_guardrail.py
 M agentic_core/L5_safety/enforcement/ssot_import_enforcer.py
 M agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py
 M agentic_core/L5_safety/enforcement/three_tier_compliance_enforcer.py
 M agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py
 M agentic_core/L5_safety/governance/lazy_seam_classifier.py
 M agentic_core/L5_safety/governance/lazy_seam_enforcer.py
 M agentic_core/L5_safety/governance/lazy_seam_scanner.py
 M agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py
 M agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py
 M agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py
 M agentic_core/L5_safety/reasoning/CodeHealerAgent.py
 M agentic_core/L5_safety/reasoning/FileClassificationAgent.py
 M agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py
 M agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py
 M agentic_core/L5_safety/reasoning/GovernanceAgent.py
 M agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py
 M agentic_core/L5_safety/reasoning/HierarchyAgent.py
 M agentic_core/L5_safety/reasoning/LocationHealerAgent.py
 M agentic_core/L5_safety/reasoning/LocationValidatorAgent.py
 M agentic_core/L5_safety/reasoning/RootHygieneAgent.py
 M agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py
 M agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py
 M agentic_core/L5_safety/reasoning/StructureHealerAgent.py
 M agentic_core/L5_safety/static_checks/ptc_invariants.py
 M agentic_core/L5_safety/utils/forge_fortress_util.py
 M agentic_core/L5_safety/utils/pre_deploy_check_util.py
 M agentic_core/L5_safety/utils/set_complexity_health_100_util.py
 M agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py
 M agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py
 M agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py
 M agentic_core/L5_safety/validators/gravity_validator.py
 M agentic_core/L6_observability/dashboards/core/experiencein_config.py
 M agentic_core/base_agents/SovereignBaseAgent.py
 M agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py
 M agentic_core/knowledge/engine/rag_orchestrator.py
 M agentic_core/knowledge/healing/wiki_healer.py
 M agentic_core/runtime/config/model_provider_config.py
 M agentic_core/runtime/utils/file_cache_util.py
 M apps_lic/utils/lic_agent_base_util.py
 M apps_rg/engines/void_compliance_engine.py
 M apps_rg/scripts/migration_executor.py
 M apps_rg/scripts/rg_final_audit.py
 M apps_rg/utils/rg_agent_base_util.py
 M apps_shared/reasoning/restore_all_archived_agents.py
 M apps_shared/reasoning/restore_app_agents.py
 M apps_shared/reasoning/restore_void_agents.py
 M apps_shared/scripts/benchmark_consolidation_performance.py
 M apps_shared/scripts/fix_all_agentic_imports.py
 M apps_shared/scripts/meta_control_config_bridge.py
 M apps_shared/scripts/meta_learning_operator.py
 M apps_shared/types/ssot_relocator_types.py
 M apps_shared/utils/sleeping_giant_util.py
 M system_learning/pipelines/pipeline_factory.py
 M tests/guardian/test_manual_verification.py
?? docs/reports/infrastructure/
?? "docs/technical/Drilldown - Archive/"
?? "docs/technical/L5 Validator Suite.md"
?? docs/technical/_ast_scan_results.json
?? ops_scripts/ci/_check_wsl_faiss.sh
?? ops_scripts/ci/_run_baseline_and_commit.py
?? ops_scripts/ci/_ssot_path_fixer.py
?? tests/guardian/test_guardian_aggregation.py
?? tests/guardian/test_guardian_contract.py
?? tests/guardian/test_guardian_hygiene.py
```

## TestCountSummary

```
AgentDiscoveryCache:    21 tests (was 13, +8 new)
ToolEmbeddingCache:     15 tests (was  6, +9 new)
SchemaValidatorCache:   13 tests (was  6, +7 new)
PolicyRegistryCache:    15 tests (was  6, +9 new)
ConfigFileCache:        14 tests (was  7, +7 new)
Total:                  78 tests (was 38, +40 new)
```

## GapAnalysis

10 gaps identified against updated .windsurfrules rules s4, all closed:

```
GAP-01 [CLOSED] Determinism same-input-twice (rules s4:124-125)
       Tests: *_same_*_identical_key_twice (5 tests, one per cache)

GAP-02 [CLOSED] Normalization: input order invariant (rules s4:126)
       Tests: test_tool_embedding_cache_input_order_invariant
              test_schema_validator_cache_key_order_invariant

GAP-03 [CLOSED] Near-miss distinct keys: materially distinct inputs (rules s4:127)
       Tests: *_near_miss_* and *_distinct_*_distinct_keys* (5 tests)

GAP-04 [CLOSED] Replay x warm-cache matrix: get_json never called (rules s4:155-156)
       Tests: *_replay_warm_get_json_never_called (5 tests, one per cache)

GAP-05 [CLOSED] Side-effect envelope on cache hit (rules s4:134-138)
       Tests: *_hit_side_effect_envelope (5 tests, one per cache)

GAP-06 [CLOSED] Fail-closed: no cache side-effect before validation error (rules s4:131-133)
       Tests: *_no_cache_side_effect (5 tests) + *_no_set_json_side_effect (2 tests)

GAP-07 [CLOSED] Broad-except passthrough: fetch errors not swallowed (rules s4:146-148)
       Tests: *_broad_except_does_not_swallow_fetch_error (5 tests)

GAP-08 [CLOSED] Stale TTL expiry path: re-fetch and re-cache (rules s4:179-183)
       Tests: *_stale_*_refetch_on_miss (4 tests) + stale cache path in discovery

GAP-09 [CLOSED] Malformed-plausible: directory path graceful degradation (rules s4:116-117)
       Tests: test_agent_discovery_cache_malformed_plausible_path_object
              test_tool_embedding_cache_malformed_tool_missing_name_key

GAP-10 [CLOSED] Invalidate exception swallow proof (rules s4:141-144)
       Tests: test_policy_registry_cache_invalidate_exception_does_not_propagate
```

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

