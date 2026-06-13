# Sovereign Territories and Directory Exclusions

## Overview
This document consolidates all sovereign territories and directory exclusions from the SSOT structure blueprint configuration.

## Sovereign Territories (16 Total)

| Territory | Purpose | Depth | Volatile | No Cross-Layer Imports | Allowed Extensions | Key Subfolders |
|-----------|---------|-------|----------|------------------------|-------------------|----------------|
| **agentic_core** | Core agentic logic and safety layers | 3 | No | No | .py, .json | L0-L6 layers, adg, agents, base_agents, config, prompt_governance, runtime, mixins, seams, utils, knowledge, interfaces, evaluation, enforcement, cache |
| **apps_rg** | Resume Generation Application domain | 2 | No | No | .py, .json, .yaml | config, types, reasoning, engines, enforcement, utils, scripts, tools, validators, domain (entities/models/value_objects) |
| **apps_lic** | LinkedIn Canonical application domain | 2 | No | No | .py, .json, .yaml | config, types, reasoning, engines, enforcement, utils, scripts, tools, validators, domain (config/utils/models) |
| **apps_shared** | Global utilities and shared logic | 2 | No | No | .py, .json, .yaml | config, data, reasoning, scripts, types, utils, validators (required); agents, core_components, enforcement, tools, mixins, integration, llm, spine (optional) |
| **tests** | Universal test suites organized by Type then Domain | 2 | No | No | .py, .json, .yaml | core, goldens, helpers, misc, unit_min_deps, unit (mirror source), integration, e2e, guardian, fixtures, snapshots, behavioral, stress, performance, architecture, contracts, enforcement, governance, integration_full_deps, scripts, sovereign_hardening, ssot_equivalence, support, system_learning |
| **ops_scripts** | Standalone utility scripts | 2 | No | No | .py, .json, .yaml | ci, maintenance, security, setup, governance, hooks, simulations, general |
| **system_learning** | Adaptive learning subsystem | 2 | No | No | .py, .json, .jsonl, .md | adapters, arbitration, confidence, config, constraints, correlation, enforcement, engines, fingerprinting, pipelines, ports, runtime, snapshots, stores, types, validators |
| **tools** | Developer tooling | 2 | No | Yes | .py | evidence |
| **logs** | Runtime and audit log outputs | 2 | Yes | Yes | .log, .jsonl, .json, .txt | compliance_reports, sovereign_audit |
| **archives** | Deprecated agents and transaction artifacts | 3 | No | Yes | .py, .json, .md | deprecated, gatekeeper |
| **data** | Data storage and processing artifacts | 3 | No | Yes | .py, .json, .jsonl, .md, .yaml | external, freeze_reports, golden, golden_state, logs, manifests, output, processed, prompt_governance, raw, sdks_mcps (client_wrappers), snapshots, tasks, archives, cache |
| **docs** | Documentation and reporting | 3 | No | No | .py, .json, .md, .yaml | metrics, reports (assessments/coverage/telemetry/security/audit/missions/.migration/MCP/apps_lic/apps_rg/misc/plans/verification), architecture, contracts, plans, technical, policies, project, testing |
| **.github** | GitHub Actions workflows | 2 | Yes | No | .yml, .yaml, .md | workflows |
| **.gravity_state** | Gravity system state tracking | 2 | Yes | No | (none) | (none) |
| **.backup** | Backup and recovery artifacts | 2 | Yes | Yes | .py, .json, .md | guardian_tests, phase1, phase2 |
| **artifacts** | Build artifacts and transient outputs | 2 | Yes | Yes | .py, .json, .md | consolidation, dedup |

## Directory Exclusions and Forbidden Patterns

### Global Excluded Directories
- `__pycache__` - Python bytecode cache
- `.git` - Git metadata
- `.windsurf` - Windsurf configuration
- `.venv`, `venv` - Virtual environments
- `node_modules` - Node.js dependencies
- `.pytest_cache` - Pytest cache
- `.mypy_cache` - MyPy cache
- `.coverage` - Coverage reports
- `dist`, `build` - Build artifacts

### Territory-Specific Forbidden Patterns

#### agentic_core
- **Forbidden patterns**: `agentic_core/common`, `agentic_core/utils/core_extensions`
- **config forbidden patterns**: `^constants\.py$`, `^registry\.py$`, `^json_loader\.py$`
- **prompt_governance forbidden patterns**: `L3_`, `l3_`

#### apps_shared
- **Forbidden imports**: `apps_rg`, `apps_lic`

#### tests
- **Forbidden zones**: `misc`, `temp`, `old`, `deprecated`, `archive`, `scratch`
- **contracts forbidden patterns**: `.*Agent\.py$`, `^fake_.*\.py$`
- **support forbidden patterns**: `.*Agent\.py$`

## Special Configuration Notes

### Territories with No Cross-Layer Imports
These territories cannot import from other territories:
- **tools** - Developer tooling only
- **logs** - Output-only territory
- **archives** - Deprecated code storage
- **data** - Data artifacts only
- **.backup** - Backup storage
- **artifacts** - Build outputs

### Volatile Territories
These territories contain transient/generated content:
- **logs** - Runtime logs
- **.github** - CI/CD workflows
- **.gravity_state** - System state
- **.backup** - Backup artifacts
- **artifacts** - Build artifacts

### Territories with Restricted File Types
- **logs**: Only `.log`, `.jsonl`, `.json`, `.txt`
- **.github**: Only `.yml`, `.yaml`, `.md`
- **tools**: Only `.py`
- **data**: `.py`, `.json`, `.jsonl`, `.md`, `.yaml`

## Required vs Optional Subfolders

### apps_shared Required Subfolders
- config, data, reasoning, scripts, types, utils, validators

### data Required Subfolders
- external, freeze_reports, golden, golden_state, logs, manifests, output, processed, prompt_governance, raw, sdks_mcps, snapshots, tasks

### data Optional Subfolders
- archives, cache

### ops_scripts Required Subfolders
- ci, maintenance, security, setup, governance, hooks, simulations, general

### prompt_governance Required Subfolders
- meta_prompts, templates, scripts, security

### prompt_governance Optional Subfolders
- core, domain, optimization, registry, utils, validation

## Enforcement Levels
- **Standard**: Most territories follow standard enforcement
- **Relaxed**: artifacts territory has relaxed enforcement
- **Exclusions**: artifacts territory excluded from depth, naming, and layer validation rules

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

