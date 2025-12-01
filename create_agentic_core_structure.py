#!/usr/bin/env python3
"""
AGENTIC_CORE STRUCTURE CREATOR
Phase 1: Create exact directory structure as specified in unified_structure_subatomic.yaml
"""

import os
from pathlib import Path

def create_agentic_core_structure():
    """Create the exact agentic_core structure from YAML"""
    
    base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow/agentic_core")
    
    # Create base directory
    base_path.mkdir(exist_ok=True)
    
    # Define exact structure from YAML
    structure = {
        "plan-layer": {
            "plan-phase": {
                "get-core-info": {
                    "general": {
                        "understand-request": {
                            "build_core_query.py": None,
                            "parse_registry_intent.py": None, 
                            "extract_layer_parameters.py": None
                        },
                        "use-a-tool": {
                            "execute_core_action.py": None,
                            "invoke_core_service.py": None,
                            "process_core_response.py": None
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
}

def create_directory_structure(structure, current_path):
    """Recursively create directories and files"""
    for key, value in structure.items():
        if isinstance(value, dict):
            # This is a directory
            new_path = current_path / key
            new_path.mkdir(exist_ok=True)
            print(f"Created directory: {new_path.relative_to(base_path)}")
            create_directory_structure(value, new_path)
        elif isinstance(value, list):
            # This is a list of files - create them in current directory
            for filename in value:
                file_path = current_path / filename
                file_path.touch()  # Create empty file
                print(f"Created file: {file_path.relative_to(base_path)}")
        elif value is None:
            # This is a single file with null value
            file_path = current_path / key
            file_path.touch()  # Create empty file
            print(f"Created file: {file_path.relative_to(base_path)}")

print("Creating agentic_core directory structure...")
create_directory_structure(structure, base_path)
print("Structure creation completed!")

if __name__ == "__main__":
    create_agentic_core_structure()
