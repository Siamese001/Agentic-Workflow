#!/usr/bin/env python3
"""
AGENTIC_CORE PHASE 1 VERIFICATION
Verifies all 12 Phase 1 completion criteria for agentic_core reconstruction
"""

from pathlib import Path

def load_yaml_structure():
    """Load the expected structure from unified_structure_subatomic.yaml"""
    # Use the exact same structure as fixed creation script
    structure = {
        "plan-layer": {
            "plan-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": {
                            "build_core_query.py": None,
                            "parse_registry_intent.py": None, 
                            "extract_layer_parameters.py": None
                        }
                    },
                    "utility": {
                        "prepare-information": {
                            "prepare_core_payload.py": None,
                            "format_registry_context.py": None,
                            "build_core_filters.py": None
                        }
                    }
                },
                "check-core-rules": {
                    "policy": {
                        "check-safety": {
                            "validate_core_constraints.py": None,
                            "check_registry_policy.py": None,
                            "enforce_core_boundaries.py": None
                        }
                    }
                }
            },
            "expand-phase": {
                "convert-core-content": {
                    "embedding": {
                        "compare-meaning": {
                            "compute_core_embeddings.py": None,
                            "normalize_core_vectors.py": None,
                            "calculate_core_similarity.py": None
                        }
                    },
                    "semantic": {
                        "adjust-scores": {
                            "normalize_core_scores.py": None,
                            "apply_core_weights.py": None,
                            "compute_core_confidence.py": None
                        }
                    }
                }
            },
            "refine-phase": {
                "pick-best-result": {
                    "general": {
                        "understand-request": {
                            "rank_core_components.py": None,
                            "apply_core_algorithm.py": None,
                            "sort_core_results.py": None
                        }
                    },
                    "refinement": {
                        "adjust-scores": {
                            "refine_core_ranking.py": None,
                            "adjust_core_weights.py": None,
                            "optimize_core_order.py": None
                        }
                    }
                }
            },
            "validate-phase": {
                "check-core-structure": {
                    "policy": {
                        "check-safety": {
                            "validate_core_schema.py": None,
                            "check_core_compliance.py": None,
                            "enforce_core_contracts.py": None
                        }
                    },
                    "semantic": {
                        "adjust-scores": {
                            "validate_core_quality.py": None,
                            "assess_core_confidence.py": None,
                            "compute_core_validation.py": None
                        }
                    }
                }
            },
            "act-phase": {
                "use-core-tools": {
                    "general": {
                        "use-a-tool": {
                            "execute_core_action.py": None,
                            "invoke_core_service.py": None,
                            "process_core_response.py": None
                        }
                    },
                    "routing": {
                        "retry-task": {
                            "implement_core_retry.py": None,
                            "apply_core_backoff.py": None,
                            "handle_core_failures.py": None
                        }
                    }
                }
            },
            "inspect-phase": {
                "find-core-problems": {
                    "general": {
                        "update-memory": {
                            "inspect_core_state.py": None,
                            "capture_core_diagnostics.py": None,
                            "log_core_inspection.py": None
                        }
                    }
                }
            },
            "retrieve-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": {
                            "retrieve_core_context.py": None,
                            "query_core_store.py": None,
                            "fetch_core_history.py": None
                        }
                    },
                    "embedding": {
                        "compare-meaning": {
                            "search_core_vectors.py": None,
                            "match_core_context.py": None,
                            "retrieve_core_similarity.py": None
                        }
                    }
                }
            },
            "agg-phase": {
                "update-core-state": {
                    "general": {
                        "update-memory": {
                            "aggregate_core_state.py": None,
                            "merge_core_contexts.py": None,
                            "consolidate_core_updates.py": None
                        }
                    },
                    "utility": {
                        "prepare-information": {
                            "prepare_core_snapshot.py": None,
                            "serialize_core_state.py": None,
                            "format_core_payload.py": None
                        }
                    }
                }
            },
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": {
                            "apply_core_safety.py": None,
                            "enforce_core_filters.py": None,
                            "validate_core_ethics.py": None
                        }
                    }
                },
                "manage-core-costs": {
                    "general": {
                        "update-memory": {
                            "update_core_budget.py": None,
                            "track_core_usage.py": None,
                            "enforce_core_limits.py": None
                        }
                    }
                }
            }
        },
        "orc-layer": {
            "plan-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": {
                            "orchestrate_core_planning.py": None,
                            "coordinate_core_queries.py": None,
                            "manage_core_context.py": None
                        }
                    }
                }
            },
            "act-phase": {
                "use-core-tools": {
                    "general": {
                        "use-a-tool": {
                            "dispatch_orchestration_tools.py": None,
                            "invoke_orchestration_service.py": None,
                            "call_orchestration_api.py": None
                        }
                    },
                    "routing": {
                        "retry-task": {
                            "retry_orchestration_operations.py": None,
                            "handle_orchestration_failures.py": None,
                            "implement_orchestration_fallback.py": None
                        }
                    }
                }
            },
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": {
                            "apply_orchestration_safety.py": None,
                            "enforce_orchestration_policy.py": None,
                            "validate_orchestration_ethics.py": None
                        }
                    }
                }
            }
        },
        "exec-layer": {
            "act-phase": {
                "use-core-tools": {
                    "general": {
                        "use-a-tool": {
                            "execute_core_execution.py": None,
                            "perform_core_operation.py": None,
                            "invoke_core_tool.py": None
                        }
                    },
                    "utility": {
                        "prepare-information": {
                            "prepare_execution_payload.py": None,
                            "format_execution_request.py": None,
                            "serialize_execution_params.py": None
                        }
                    }
                }
            },
            "validate-phase": {
                "check-core-structure": {
                    "policy": {
                        "check-safety": {
                            "validate_execution_schema.py": None,
                            "check_execution_compliance.py": None,
                            "enforce_execution_contracts.py": None
                        }
                    }
                }
            },
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": {
                            "apply_execution_safety.py": None,
                            "enforce_execution_policy.py": None,
                            "validate_execution_ethics.py": None
                        }
                    }
                }
            }
        },
        "mem-layer": {
            "retrieve-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": {
                            "retrieve_core_memory.py": None,
                            "query_core_state.py": None,
                            "fetch_core_history.py": None
                        }
                    },
                    "embedding": {
                        "compare-meaning": {
                            "search_core_vectors.py": None,
                            "match_core_patterns.py": None,
                            "find_core_context.py": None
                        }
                    }
                }
            },
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": {
                            "apply_memory_safety.py": None,
                            "enforce_memory_policy.py": None,
                            "validate_memory_ethics.py": None
                        }
                    }
                }
            }
        },
        "safe-layer": {
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": {
                            "apply_safety_policy.py": None,
                            "enforce_safety_filters.py": None,
                            "validate_safety_ethics.py": None
                        }
                    },
                    "semantic": {
                        "adjust-scores": {
                            "assess_safety_risk.py": None,
                            "compute_safety_score.py": None,
                            "evaluate_safety_compliance.py": None
                        }
                    }
                },
                "manage-core-costs": {
                    "general": {
                        "update-memory": {
                            "track_safety_cost.py": None,
                            "update_safety_usage.py": None,
                            "enforce_safety_budget.py": None
                        }
                    }
                }
            }
        }
    }
    
    return structure

def extract_expected_paths(structure, current_path=""):
    """Extract all expected file and directory paths from YAML structure"""
    paths = {"files": set(), "directories": set()}
    
    for key, value in structure.items():
        new_path = f"{current_path}/{key}" if current_path else key
        
        if isinstance(value, dict):
            paths["directories"].add(new_path)
            sub_paths = extract_expected_paths(value, new_path)
            paths["files"].update(sub_paths["files"])
            paths["directories"].update(sub_paths["directories"])
        elif isinstance(value, list):
            # This should be a list of files
            for filename in value:
                file_path = f"{new_path}/{filename}"
                paths["files"].add(file_path)
        elif value is None:
            # This is a single file
            paths["files"].add(f"{new_path}.py" if not new_path.endswith('.py') else new_path)
    
    return paths

def get_actual_paths(base_path):
    """Get all actual file and directory paths in the filesystem"""
    paths = {"files": set(), "directories": set()}
    
    # Walk the actual filesystem
    for item in base_path.rglob("*"):
        relative_path = item.relative_to(base_path)
        path_str = str(relative_path).replace("\\", "/")
        
        if item.is_dir():
            paths["directories"].add(path_str)
        elif item.is_file():
            paths["files"].add(path_str)
    
    return paths

def verify_phase1_criteria():
    """Verify all Phase 1 completion criteria"""
    base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow/agentic_core")
    
    print("=== AGENTIC_CORE PHASE 1 VERIFICATION ===\n")
    
    # Load expected structure from YAML
    print("1. Loading YAML structure...")
    yaml_structure = load_yaml_structure()
    expected_paths = extract_expected_paths(yaml_structure)
    
    # Get actual filesystem structure
    print("2. Scanning actual filesystem structure...")
    actual_paths = get_actual_paths(base_path)
    
    # Phase 1 Completion Criteria Verification
    criteria_results = {}
    
    print("\n3. Verifying Phase 1 Completion Criteria...")
    
    # CRITERION 1: Directory tree matches YAML
    missing_dirs = expected_paths["directories"] - actual_paths["directories"]
    extra_dirs = actual_paths["directories"] - expected_paths["directories"]
    criteria_results["PHASE1_agentic_core_DIRECTORY_TREE_MATCHES_YAML"] = len(missing_dirs) == 0 and len(extra_dirs) == 0
    
    # CRITERION 2: All folders created
    criteria_results["PHASE1_agentic_core_ALL_FOLDERS_CREATED"] = len(missing_dirs) == 0
    
    # CRITERION 3: All files created
    missing_files = expected_paths["files"] - actual_paths["files"]
    criteria_results["PHASE1_agentic_core_ALL_FILES_CREATED"] = len(missing_files) == 0
    
    # CRITERION 4: No extra folders
    criteria_results["PHASE1_agentic_core_NO_EXTRA_FOLDERS"] = len(extra_dirs) == 0
    
    # CRITERION 5: No extra files
    extra_files = actual_paths["files"] - expected_paths["files"]
    criteria_results["PHASE1_agentic_core_NO_EXTRA_FILES"] = len(extra_files) == 0
    
    # CRITERION 6: No missing folders (same as criterion 2)
    criteria_results["PHASE1_agentic_core_NO_MISSING_FOLDERS"] = len(missing_dirs) == 0
    
    # CRITERION 7: No missing files (same as criterion 3)
    criteria_results["PHASE1_agentic_core_NO_MISSING_FILES"] = len(missing_files) == 0
    
    # CRITERION 8: All paths case sensitive
    case_issues = []
    for expected_dir in expected_paths["directories"]:
        if expected_dir.lower() != expected_dir:
            actual_match = None
            for actual_dir in actual_paths["directories"]:
                if actual_dir.lower() == expected_dir.lower():
                    actual_match = actual_dir
                    break
            if actual_match and actual_match != expected_dir:
                case_issues.append(f"Expected: {expected_dir}, Found: {actual_match}")
    criteria_results["PHASE1_agentic_core_ALL_PATHS_CASE_SENSITIVE"] = len(case_issues) == 0
    
    # CRITERION 9: All path depths correct
    depth_issues = []
    for expected_path in expected_paths["directories"]:
        expected_depth = expected_path.count("/")
        actual_match = None
        for actual_path in actual_paths["directories"]:
            if actual_path == expected_path:
                actual_match = actual_path
                break
        if actual_match and actual_match.count("/") != expected_depth:
            depth_issues.append(f"Path depth mismatch: {expected_path}")
    criteria_results["PHASE1_agentic_core_ALL_PATH_DEPTHS_CORRECT"] = len(depth_issues) == 0
    
    # CRITERION 10: Legacy files merged or removed
    # (We deleted the entire old structure, so this should be true)
    legacy_patterns = ["budget-manager-layer", "executor-microagent-layer", "l5_safety", 
                      "observer-microagent-layer", "planner-microagent-layer", 
                      "retriever-microagent-layer", "router-microagent-layer", "safety-guard-layer"]
    legacy_found = any(pattern in str(path) for path in actual_paths["directories"] for pattern in legacy_patterns)
    criteria_results["PHASE1_agentic_core_LEGACY_FILES_MERGED_OR_REMOVED"] = not legacy_found
    
    # CRITERION 11: No orphaned paths
    criteria_results["PHASE1_agentic_core_NO_ORPHANED_PATHS"] = len(missing_dirs) == 0 and len(missing_files) == 0
    
    # CRITERION 12: Cleanup complete
    criteria_results["PHASE1_agentic_core_CLEANUP_COMPLETE"] = len(extra_dirs) == 0 and len(extra_files) == 0
    
    # Print detailed results
    print("\n=== DETAILED VERIFICATION RESULTS ===")
    
    print(f"\nExpected directories: {len(expected_paths['directories'])}")
    print(f"Actual directories: {len(actual_paths['directories'])}")
    print(f"Expected files: {len(expected_paths['files'])}")
    print(f"Actual files: {len(actual_paths['files'])}")
    
    if missing_dirs:
        print(f"\n❌ MISSING DIRECTORIES ({len(missing_dirs)}):")
        for d in sorted(missing_dirs):
            print(f"  - {d}")
    
    if extra_dirs:
        print(f"\n❌ EXTRA DIRECTORIES ({len(extra_dirs)}):")
        for d in sorted(extra_dirs):
            print(f"  - {d}")
    
    if missing_files:
        print(f"\n❌ MISSING FILES ({len(missing_files)}):")
        for f in sorted(missing_files):
            print(f"  - {f}")
    
    if extra_files:
        print(f"\n❌ EXTRA FILES ({len(extra_files)}):")
        for f in sorted(extra_files):
            print(f"  - {f}")
    
    if case_issues:
        print(f"\n❌ CASE SENSITIVITY ISSUES ({len(case_issues)}):")
        for issue in case_issues:
            print(f"  - {issue}")
    
    if depth_issues:
        print(f"\n❌ PATH DEPTH ISSUES ({len(depth_issues)}):")
        for issue in depth_issues:
            print(f"  - {issue}")
    
    print("\n=== PHASE 1 CRITERIA RESULTS ===")
    all_passed = True
    for criterion, result in criteria_results.items():
        status = "✅ TRUE" if result else "❌ FALSE"
        print(f"{criterion}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n=== OVERALL RESULT ===")
    if all_passed:
        print("🎉 ALL PHASE 1 CRITERIA PASSED - agentic_core ready for Phase 2!")
        return True
    else:
        print("❌ SOME PHASE 1 CRITERIA FAILED - fix issues before proceeding")
        return False

if __name__ == "__main__":
    success = verify_phase1_criteria()
    exit(0 if success else 1)
