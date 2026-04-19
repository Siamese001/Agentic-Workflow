scripts/                                   # LEVEL 1
│
├── ci_pipeline/                           # LEVEL 2
│   ├── ci_enforcer.py                     # LEVEL 3
│   ├── build_artifacts.py                 # LEVEL 3 (placeholder, if added)
│   ├── run_tests.py                       # LEVEL 3 (placeholder)
│   ├── run_lint.py                        # LEVEL 3 (placeholder)
│   ├── check_schemas.py                   # LEVEL 3 (placeholder)
│   └── verify_golden_sets.py              # LEVEL 3 (placeholder)
│
├── maintenance/                           # LEVEL 2
│   ├── ast_purity_scanner.py              # LEVEL 3
│   ├── cleanup_observability.py           # LEVEL 3 (placeholder)
│   ├── enforce_config_structure.py        # LEVEL 3 (placeholder)
│   ├── enforce_data_structure.py          # LEVEL 3 (placeholder)
│   ├── normalize_permissions.ps1          # LEVEL 3 (placeholder)
│   └── remove_pycache.py                  # LEVEL 3 (placeholder)
│
├── validation/                            # LEVEL 2
│   ├── contract_registry_validator.py      # LEVEL 3
│   ├── golden_trace_auditor.py             # LEVEL 3
│   ├── manifest_validator.py               # LEVEL 3
│   ├── semantic_validation_engine.py       # LEVEL 3
│   ├── test_matrix_validator.py            # LEVEL 3
│   ├── validate_root_folders.py            # LEVEL 3 (placeholder)
│   ├── validate_config_schemas.py          # LEVEL 3 (placeholder)
│   ├── validate_observability_structure.py # LEVEL 3 (placeholder)
│   ├── validate_runtime_integrity.py       # LEVEL 3 (placeholder)
│   ├── validate_prompt_governance.py       # LEVEL 3 (placeholder)
│   └── validate_test_structure.py          # LEVEL 3 (placeholder)
│
├── ingestion/                              # LEVEL 2
│   ├── ingest_job_descriptions.py          # LEVEL 3 (placeholder)
│   ├── ingest_resume_inputs.py             # LEVEL 3 (placeholder)
│   ├── ingest_taxonomy_data.py             # LEVEL 3 (placeholder)
│   └── sanitize_inputs.py                  # LEVEL 3 (placeholder)
│
├── dev_tools/                              # LEVEL 2
│   ├── tree_export.ps1                     # LEVEL 3 (placeholder)
│   ├── show_repo_summary.py                # LEVEL 3 (placeholder)
│   ├── diff_folder_structure.py            # LEVEL 3 (placeholder)
│   └── check_for_large_files.py            # LEVEL 3 (placeholder)
│
├── utils/                                  # LEVEL 2
│   ├── io_helpers.py                       # LEVEL 3 (placeholder)
│   ├── file_ops.py                         # LEVEL 3 (placeholder)
│   ├── hashing.py                          # LEVEL 3 (placeholder)
│   └── logging_utils.py                    # LEVEL 3 (placeholder)
│
├── pipeline_artifacts/                     # LEVEL 2
│   └── pipeline_test_001_results.json      # LEVEL 3
│
├── pipeline_logs/                          # LEVEL 2
│   └── .gitkeep                            # LEVEL 3
│
├── runtime/                                # LEVEL 2
│   └── metrics.json                        # LEVEL 3
│
├── migrate_scripts.py                      # LEVEL 2
└── scripts-tree.txt                        # LEVEL 2


### Directory Structure

```plaintext
├── agentic_core.md
├── apps.md
├── config.md
├── data.md
├── observability.md
├── prompt_governance.md
├── runtime.md
├── schemas.md
├── scripts.md
├── tests.md
└── update_markdown_trees.py
```
