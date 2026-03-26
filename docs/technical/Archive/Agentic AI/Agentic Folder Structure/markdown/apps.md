apps/
│
├── resume_engine/                         # LEVEL 1
│   │
│   ├── api/                               # LEVEL 2
│   │   ├── v1/                             # LEVEL 3
│   │   │   ├── endpoints/                  # LEVEL 4
│   │   │   │   ├── generate_resume.py      # LEVEL 5
│   │   │   │   ├── validate_resume.py
│   │   │   │   └── healthcheck.py
│   │   │   ├── schemas/                    # LEVEL 4
│   │   │   │   ├── resume_request.json      # LEVEL 5
│   │   │   │   └── resume_response.json
│   │   │   ├── middleware/                 # LEVEL 4
│   │   │   │   ├── auth.py                 # LEVEL 5
│   │   │   │   └── rate_limit.py
│   │   │   └── router.py                   # LEVEL 4
│   │   │
│   ├── services/                           # LEVEL 2
│   │   ├── builders/                       # LEVEL 3
│   │   │   ├── resume_builder.py           # LEVEL 4
│   │   │   └── ats_optimizer.py            # LEVEL 4
│   │   ├── enrichers/                      # LEVEL 3
│   │   │   ├── skill_expander.py           # LEVEL 4
│   │   │   └── job_alignment.py            # LEVEL 4
│   │   ├── generators/                     # LEVEL 3
│   │   │   ├── section_generator.py        # LEVEL 4
│   │   │   └── summary_generator.py        # LEVEL 4
│   │   ├── pipelines/                      # LEVEL 3
│   │   │   ├── resume_pipeline.py          # LEVEL 4
│   │   │   └── validation_pipeline.py      # LEVEL 4
│   │   └── utils/                          # LEVEL 3
│   │       ├── formatting.py               # LEVEL 4
│   │       └── scoring.py                  # LEVEL 4
│   │
│   ├── workers/                            # LEVEL 2
│   │   ├── job_ingest_worker.py            # LEVEL 3
│   │   ├── resume_generate_worker.py       # LEVEL 3
│   │   └── enrichment_worker.py            # LEVEL 3
│   │
│   ├── cli/                                # LEVEL 2
│   │   ├── run_resume_engine.py            # LEVEL 3
│   │   └── debug_tools.py                  # LEVEL 3
│   │
│   └── tests/                              # LEVEL 2
│       ├── unit/                           # LEVEL 3
│       │   ├── test_resume_builder.py      # LEVEL 4
│       │   └── test_skill_expander.py      # LEVEL 4
│       ├── integration/                    # LEVEL 3
│       │   ├── test_resume_pipeline.py     # LEVEL 4
│       │   └── test_api_endpoints.py       # LEVEL 4
│       └── e2e/                            # LEVEL 3
│           ├── test_full_resume_flow.py    # LEVEL 4
│           └── test_error_recovery.py      # LEVEL 4
│
├── outreach_engine/                        # LEVEL 1
│   │
│   ├── api/                                # LEVEL 2
│   │   ├── v1/                             # LEVEL 3
│   │   │   ├── endpoints/                  # LEVEL 4
│   │   │   │   ├── send_outreach.py        # LEVEL 5
│   │   │   │   ├── preview_message.py
│   │   │   │   └── healthcheck.py
│   │   │   ├── schemas/                    # LEVEL 4
│   │   │   │   ├── outreach_request.json   # LEVEL 5
│   │   │   │   └── outreach_response.json
│   │   │   ├── middleware/                 # LEVEL 4
│   │   │   │   ├── auth.py                 # LEVEL 5
│   │   │   │   └── rate_limit.py
│   │   │   └── router.py                   # LEVEL 4
│   │
│   ├── services/                           # LEVEL 2
│   │   ├── planners/                       # LEVEL 3
│   │   │   ├── message_planner.py          # LEVEL 4
│   │   │   └── cadence_planner.py          # LEVEL 4
│   │   ├── generators/                     # LEVEL 3
│   │   │   ├── outreach_generator.py       # LEVEL 4
│   │   │   └── personalization_engine.py   # LEVEL 4
│   │   ├── enrichers/                      # LEVEL 3
│   │   │   ├── contact_enricher.py         # LEVEL 4
│   │   │   └── profile_analyzer.py         # LEVEL 4
│   │   ├── pipelines/                      # LEVEL 3
│   │   │   ├── outreach_pipeline.py        # LEVEL 4
│   │   │   └── compliance_pipeline.py      # LEVEL 4
│   │   └── utils/                          # LEVEL 3
│   │       ├── scoring.py                  # LEVEL 4
│   │       └── formatting.py               # LEVEL 4
│   │
│   ├── workers/                            # LEVEL 2
│   │   ├── linkedin_send_worker.py         # LEVEL 3
│   │   ├── email_send_worker.py            # LEVEL 3
│   │   └── enrichment_worker.py            # LEVEL 3
│   │
│   ├── cli/                                # LEVEL 2
│   │   ├── run_outreach_engine.py          # LEVEL 3
│   │   └── debug_tools.py                  # LEVEL 3
│   │
│   └── tests/                              # LEVEL 2
│       ├── unit/                           # LEVEL 3
│       │   ├── test_message_planner.py     # LEVEL 4
│       │   └── test_outreach_generator.py  # LEVEL 4
│       ├── integration/                    # LEVEL 3
│       │   ├── test_outreach_pipeline.py   # LEVEL 4
│       │   └── test_api_endpoints.py       # LEVEL 4
│       └── e2e/                            # LEVEL 3
│           ├── test_full_outreach_flow.py  # LEVEL 4
│           └── test_error_recovery.py      # LEVEL 4
│
└── shared/                                 # LEVEL 1
    ├── utils/                              # LEVEL 2
    │   ├── logging.py                      # LEVEL 3
    │   ├── constants.py                    # LEVEL 3
    │   └── time.py                         # LEVEL 3
    ├── adapters/                           # LEVEL 2
    │   ├── linkedin_adapter.py             # LEVEL 3
    │   ├── email_adapter.py                # LEVEL 3
    │   └── redis_adapter.py                # LEVEL 3
    └── tests/                              # LEVEL 2
        ├── unit/                           # LEVEL 3
        ├── integration/                    # LEVEL 3
        └── e2e/                            # LEVEL 3


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
