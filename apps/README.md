# Apps Directory Structure

This directory contains the application layer implementations organized in an engine-based architecture that mirrors the `agentic_core/` structure.

## Architecture Overview

```
apps/
├── resume_engine/          # Resume generation engine
│   ├── api/v1/            # REST API endpoints and schemas
│   │   ├── endpoints/     # API controllers
│   │   ├── schemas/       # Data serializers
│   │   └── middleware/    # Validation middleware
│   ├── services/          # Business logic services
│   │   ├── builders/      # Research and planning services
│   │   ├── enrichers/     # Data enrichment services
│   │   ├── generators/    # Content generation services
│   │   ├── pipelines/     # Workflow orchestration
│   │   ├── utils/         # Utility services
│   │   └── adapters/      # External system adapters
│   ├── workers/           # Background job workers
│   ├── cli/               # Command-line interfaces
│   └── tests/             # Test suites
│
├── outreach_engine/       # Outreach communication engine
│   ├── api/v1/            # REST API endpoints and schemas
│   ├── services/          # Business logic services
│   │   ├── planners/      # Campaign planning services
│   │   ├── generators/    # Content generation services
│   │   ├── enrichers/     # Data enrichment services
│   │   ├── pipelines/     # Workflow orchestration
│   │   ├── utils/         # Utility services
│   │   └── adapters/      # External system adapters
│   ├── workers/           # Background job workers
│   ├── cli/               # Command-line interfaces
│   └── tests/             # Test suites
│
└── shared/                # Shared utilities and adapters
    ├── utils/             # Common utilities and configurations
    ├── adapters/          # Shared system adapters
    └── tests/             # Shared test utilities
```

## File Mapping Logic

The migration used intelligent file categorization:

- **Controllers** → `api/v1/endpoints/` (REST API endpoints)
- **Serializers** → `api/v1/schemas/` (data validation schemas)
- **Validators** → `api/v1/middleware/` (validation middleware)
- **Adapters** → `services/adapters/` or `shared/adapters/`
- **Workflows** → `services/pipelines/`, `services/generators/`, `services/planners/`, `services/builders/`
- **CLI files** → `cli/` directories
- **Services** → `shared/utils/` or `shared/adapters/`

## Zero-Tolerance Compliance

✅ All directories contain robust implementations
✅ No empty directories, placeholders, or stubs
✅ Proper Python package structure with `__init__.py` files
✅ All 179+ files successfully migrated and organized

## Integration with Agentic Core

This apps layer integrates with the `agentic_core/` architecture:

- `apps/resume_engine/` ↔ `agentic_core/resume_engine/`
- `apps/outreach_engine/` ↔ `agentic_core/outreach_engine/`
- `apps/shared/` ↔ `agentic_core/shared/`

The clean separation ensures maintainable, scalable development following the Agentic L5 layered architecture principles.
