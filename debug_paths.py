#!/usr/bin/env python3
"""
DEBUG PATH COMPARISON
Compare expected vs actual paths to identify mismatch issues
"""

from pathlib import Path

def get_actual_paths():
    """Get actual filesystem paths"""
    base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow/agentic_core")
    files = set()
    dirs = set()
    
    for item in base_path.rglob("*"):
        relative_path = item.relative_to(base_path)
        path_str = str(relative_path).replace("\\", "/")
        
        if item.is_dir():
            dirs.add(path_str)
        elif item.is_file():
            files.add(path_str)
    
    return files, dirs

def get_expected_paths():
    """Get expected paths from structure"""
    # Same structure as creation script
    structure = {
        "plan-layer": {
            "plan-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": [
                            "build_core_query.py",
                            "parse_registry_intent.py", 
                            "extract_layer_parameters.py"
                        ]
                    },
                    "utility": {
                        "prepare-information": [
                            "prepare_core_payload.py",
                            "format_registry_context.py",
                            "build_core_filters.py"
                        ]
                    }
                },
                "check-core-rules": {
                    "policy": {
                        "check-safety": [
                            "validate_core_constraints.py",
                            "check_registry_policy.py",
                            "enforce_core_boundaries.py"
                        ]
                    }
                }
            },
            "expand-phase": {
                "convert-core-content": {
                    "embedding": {
                        "compare-meaning": [
                            "compute_core_embeddings.py",
                            "normalize_core_vectors.py",
                            "calculate_core_similarity.py"
                        ]
                    },
                    "semantic": {
                        "adjust-scores": [
                            "normalize_core_scores.py",
                            "apply_core_weights.py",
                            "compute_core_confidence.py"
                        ]
                    }
                }
            },
            "refine-phase": {
                "pick-best-result": {
                    "general": {
                        "understand-request": [
                            "rank_core_components.py",
                            "apply_core_algorithm.py",
                            "sort_core_results.py"
                        ]
                    },
                    "refinement": {
                        "adjust-scores": [
                            "refine_core_ranking.py",
                            "adjust_core_weights.py",
                            "optimize_core_order.py"
                        ]
                    }
                }
            },
            "validate-phase": {
                "check-core-structure": {
                    "policy": {
                        "check-safety": [
                            "validate_core_schema.py",
                            "check_core_compliance.py",
                            "enforce_core_contracts.py"
                        ]
                    },
                    "semantic": {
                        "adjust-scores": [
                            "validate_core_quality.py",
                            "assess_core_confidence.py",
                            "compute_core_validation.py"
                        ]
                    }
                }
            },
            "act-phase": {
                "use-core-tools": {
                    "general": {
                        "use-a-tool": [
                            "execute_core_action.py",
                            "invoke_core_service.py",
                            "process_core_response.py"
                        ]
                    },
                    "routing": {
                        "retry-task": [
                            "implement_core_retry.py",
                            "apply_core_backoff.py",
                            "handle_core_failures.py"
                        ]
                    }
                }
            },
            "inspect-phase": {
                "find-core-problems": {
                    "general": {
                        "update-memory": [
                            "inspect_core_state.py",
                            "capture_core_diagnostics.py",
                            "log_core_inspection.py"
                        ]
                    }
                }
            },
            "retrieve-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": [
                            "retrieve_core_context.py",
                            "query_core_store.py",
                            "fetch_core_history.py"
                        ]
                    },
                    "embedding": {
                        "compare-meaning": [
                            "search_core_vectors.py",
                            "match_core_context.py",
                            "retrieve_core_similarity.py"
                        ]
                    }
                }
            },
            "agg-phase": {
                "update-core-state": {
                    "general": {
                        "update-memory": [
                            "aggregate_core_state.py",
                            "merge_core_contexts.py",
                            "consolidate_core_updates.py"
                        ]
                    },
                    "utility": {
                        "prepare-information": [
                            "prepare_core_snapshot.py",
                            "serialize_core_state.py",
                            "format_core_payload.py"
                        ]
                    }
                }
            },
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": [
                            "apply_core_safety.py",
                            "enforce_core_filters.py",
                            "validate_core_ethics.py"
                        ]
                    }
                },
                "manage-core-costs": {
                    "general": {
                        "update-memory": [
                            "update_core_budget.py",
                            "track_core_usage.py",
                            "enforce_core_limits.py"
                        ]
                    }
                }
            }
        },
        "orc-layer": {
            "plan-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": [
                            "orchestrate_core_planning.py",
                            "coordinate_core_queries.py",
                            "manage_core_context.py"
                        ]
                    }
                }
            },
            "act-phase": {
                "use-core-tools": {
                    "general": {
                        "use-a-tool": [
                            "dispatch_orchestration_tools.py",
                            "invoke_orchestration_service.py",
                            "call_orchestration_api.py"
                        ]
                    },
                    "routing": {
                        "retry-task": [
                            "retry_orchestration_operations.py",
                            "handle_orchestration_failures.py",
                            "implement_orchestration_fallback.py"
                        ]
                    }
                }
            },
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": [
                            "apply_orchestration_safety.py",
                            "enforce_orchestration_policy.py",
                            "validate_orchestration_ethics.py"
                        ]
                    }
                }
            }
        },
        "exec-layer": {
            "act-phase": {
                "use-core-tools": {
                    "general": {
                        "use-a-tool": [
                            "execute_core_execution.py",
                            "perform_core_operation.py",
                            "invoke_core_tool.py"
                        ]
                    },
                    "utility": {
                        "prepare-information": [
                            "prepare_execution_payload.py",
                            "format_execution_request.py",
                            "serialize_execution_params.py"
                        ]
                    }
                }
            },
            "validate-phase": {
                "check-core-structure": {
                    "policy": {
                        "check-safety": [
                            "validate_execution_schema.py",
                            "check_execution_compliance.py",
                            "enforce_execution_contracts.py"
                        ]
                    }
                }
            },
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": [
                            "apply_execution_safety.py",
                            "enforce_execution_policy.py",
                            "validate_execution_ethics.py"
                        ]
                    }
                }
            }
        },
        "mem-layer": {
            "retrieve-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": [
                            "retrieve_core_memory.py",
                            "query_core_state.py",
                            "fetch_core_history.py"
                        ]
                    },
                    "embedding": {
                        "compare-meaning": [
                            "search_core_vectors.py",
                            "match_core_patterns.py",
                            "find_core_context.py"
                        ]
                    }
                }
            },
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": [
                            "apply_memory_safety.py",
                            "enforce_memory_policy.py",
                            "validate_memory_ethics.py"
                        ]
                    }
                }
            }
        },
        "safe-layer": {
            "safety-phase": {
                "check-core-rules": {
                    "policy": {
                        "check-safety": [
                            "apply_safety_policy.py",
                            "enforce_safety_filters.py",
                            "validate_safety_ethics.py"
                        ]
                    },
                    "semantic": {
                        "adjust-scores": [
                            "assess_safety_risk.py",
                            "compute_safety_score.py",
                            "evaluate_safety_compliance.py"
                        ]
                    }
                },
                "manage-core-costs": {
                    "general": {
                        "update-memory": [
                            "track_safety_cost.py",
                            "update_safety_usage.py",
                            "enforce_safety_budget.py"
                        ]
                    }
                }
            }
        }
    }
    
    files = set()
    dirs = set()
    
    def extract_paths(structure, current_path=""):
        for key, value in structure.items():
            new_path = f"{current_path}/{key}" if current_path else key
            
            if isinstance(value, dict):
                dirs.add(new_path)
                extract_paths(value, new_path)
            elif isinstance(value, list):
                for filename in value:
                    file_path = f"{new_path}/{filename}"
                    files.add(file_path)
    
    extract_paths(structure)
    return files, dirs

def main():
    print("=== PATH COMPARISON DEBUG ===")
    
    actual_files, actual_dirs = get_actual_paths()
    expected_files, expected_dirs = get_expected_paths()
    
    print(f"Actual files: {len(actual_files)}")
    print(f"Expected files: {len(expected_files)}")
    print(f"Actual dirs: {len(actual_dirs)}")
    print(f"Expected dirs: {len(expected_dirs)}")
    
    missing_files = expected_files - actual_files
    extra_files = actual_files - expected_files
    missing_dirs = expected_dirs - actual_dirs
    extra_dirs = actual_dirs - expected_dirs
    
    print(f"\nMissing files: {len(missing_files)}")
    if missing_files:
        for f in sorted(list(missing_files))[:5]:  # Show first 5
            print(f"  - {f}")
        if len(missing_files) > 5:
            print(f"  ... and {len(missing_files) - 5} more")
    
    print(f"\nExtra files: {len(extra_files)}")
    if extra_files:
        for f in sorted(list(extra_files))[:5]:  # Show first 5
            print(f"  - {f}")
        if len(extra_files) > 5:
            print(f"  ... and {len(extra_files) - 5} more")
    
    print(f"\nMissing dirs: {len(missing_dirs)}")
    if missing_dirs:
        for d in sorted(list(missing_dirs))[:5]:
            print(f"  - {d}")
    
    print(f"\nExtra dirs: {len(extra_dirs)}")
    if extra_dirs:
        for d in sorted(list(extra_dirs))[:5]:
            print(f"  - {d}")

if __name__ == "__main__":
    main()
