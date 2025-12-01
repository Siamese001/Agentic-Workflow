#!/usr/bin/env python3
"""
AGENTIC_CORE STRUCTURE CREATOR - FIXED VERSION
Phase 1: Create exact directory structure as specified in unified_structure_subatomic.yaml
Uses dictionaries with None values to match YAML format exactly
"""

import os
from pathlib import Path

def create_agentic_core_structure():
    """Create the exact agentic_core structure from YAML"""
    
    base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow/agentic_core")
    
    # Create base directory
    base_path.mkdir(exist_ok=True)
    
    # Define exact structure from YAML using dictionaries with None values
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
    
    def create_directory_structure(structure, current_path):
        """Recursively create directories and files"""
        for key, value in structure.items():
            if isinstance(value, dict):
                # This is a directory
                new_path = current_path / key
                new_path.mkdir(exist_ok=True)
                print(f"Created directory: {new_path.relative_to(base_path)}")
                create_directory_structure(value, new_path)
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
