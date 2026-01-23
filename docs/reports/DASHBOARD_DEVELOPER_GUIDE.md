# Dashboard Developer Guide

**Last Updated:** January 20, 2026

This guide documents the consolidated dashboard pipeline for developers working with the Agentic Workflow dashboard system.

## Quick Start

```bash
# Regenerate dashboard data (data files only)
python scripts/regenerate_dashboard.py --data-only

# Regenerate full dashboard (HTML + data)
python scripts/regenerate_dashboard.py --full

# Verify dashboard (quick check)
python scripts/verify_dashboard.py --quick

# Verify dashboard (full validation)
python scripts/verify_dashboard.py --full

# Run dashboard tests
pytest tests/dashboard/
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CONSOLIDATED PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ Agent Discovery  │───▶│ Dashboard SSOT   │───▶│ Dashboard Gen    │  │
│  │ full_agent_      │    │ dashboard_ssot   │    │ regenerate_      │  │
│  │ discovery.py     │    │ .yaml            │    │ dashboard.py     │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘  │
│           │                      │                        │             │
│           ▼                      ▼                        ▼             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ agent_discovery_ │    │ dashboard_ssot   │    │ autonomy_        │  │
│  │ full.json        │    │ _definitions.py  │    │ dashboard.html   │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘  │
│                                                           │             │
│                                                           ▼             │
│                                            ┌─────────────────────────┐ │
│                                            │   Unified Test Suite    │ │
│                                            │   tests/dashboard/      │ │
│                                            └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Canonical Scripts

### Regeneration

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/regenerate_dashboard.py` | **Consolidated entry point** | `--full` or `--data-only` |
| `agentic_core/L0_maintenance/scripts/regenerate_dashboard_full.py` | Full regeneration implementation | Called by wrapper |

### Verification

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/verify_dashboard.py` | **Consolidated entry point** | `--quick`, `--full`, or `--deployment` |

### SSOT Generation

| Script | Purpose | Usage |
|--------|---------|-------|
| `agentic_core/L0_maintenance/scripts/generate_dashboard_ssot.py` | Generate Python/JS constants from YAML | Run after editing YAML |

## SSOT Configuration

The Single Source of Truth (SSOT) for dashboard constants is:

```
agentic_core/L0_maintenance/scripts/config/dashboard_ssot.yaml
```

This YAML file defines:
- Column names for dashboard tables
- Field names for agent discovery
- Metric thresholds
- Health score formula weights
- Code quality formula weights

### Updating Constants

1. Edit `dashboard_ssot.yaml`
2. Run: `python agentic_core/L0_maintenance/scripts/generate_dashboard_ssot.py`
3. Run: `python scripts/regenerate_dashboard.py --full`
4. Run: `pytest tests/dashboard/`

## Test Suite

The unified test suite is located at `tests/dashboard/`:

| Module | Purpose | Tests |
|--------|---------|-------|
| `test_telemetry.py` | Runtime state and telemetry | Phase 1-2 |
| `test_frontend.py` | JavaScript components | Phase 3-4 |
| `test_ui_layout.py` | HTML structure and CSS | Phase 5 |
| `test_integration.py` | Backend/frontend integration | Phase 6 |
| `test_documentation.py` | Documentation validation | Phase 7 |
| `test_e2e.py` | End-to-end tests | E2E |

### Running Tests

```bash
# Run all dashboard tests
pytest tests/dashboard/

# Run specific test module
pytest tests/dashboard/test_telemetry.py

# Run with verbose output
pytest tests/dashboard/ -v

# Run tests matching pattern
pytest tests/dashboard/ -k "telemetry"

# Skip slow/browser tests
pytest tests/dashboard/ -m "not slow"
```

## File Locations

### Core Files

| File | Location |
|------|----------|
| Dashboard HTML | `agentic_core/L6_observability/dashboards/autonomy_dashboard.html` |
| Dashboard Data | `agentic_core/L6_observability/dashboards/data/dashboard_data.js` |
| Agent Discovery | `agent_discovery_full.json` |
| SSOT YAML | `agentic_core/L0_maintenance/scripts/config/dashboard_ssot.yaml` |
| SSOT Python | `agentic_core/L5_safety/validators/dashboard_ssot_definitions.py` |

### JavaScript Components

| Component | Location |
|-----------|----------|
| Meta-Learning Panel | `dashboards/js/components/meta-learning-panel.js` |
| Redis Monitor | `dashboards/js/components/redis-monitor.js` |
| Pinecone Monitor | `dashboards/js/components/pinecone-monitor.js` |
| Execution Flow | `dashboards/js/components/execution-flow.js` |
| Controller | `dashboards/js/controllers/meta-learning-controller.js` |

## Deprecated Scripts

The following scripts have been deprecated and archived to `archives/deprecated_dashboard/`:

- `regenerate_dashboard_from_discovery.py` → Use `regenerate_dashboard.py --full`
- `regenerate_dashboard_complete.py` → Use `regenerate_dashboard.py --full`
- `generate_modular_dashboard_data.py` → Use `regenerate_dashboard.py --data-only`
- `generate_dashboard_ssot_WRAPPER.py` → Use `generate_dashboard_ssot.py` directly

**Do not restore these scripts.** Use the consolidated entry points instead.

## Common Tasks

### Regenerate After Agent Changes

```bash
# 1. Run agent discovery
python scripts/full_agent_discovery.py

# 2. Regenerate dashboard
python scripts/regenerate_dashboard.py --full

# 3. Verify
python scripts/verify_dashboard.py --quick

# 4. Run tests
pytest tests/dashboard/
```

### Update Dashboard Constants

```bash
# 1. Edit YAML
# Edit: agentic_core/L0_maintenance/scripts/config/dashboard_ssot.yaml

# 2. Generate constants
python agentic_core/L0_maintenance/scripts/generate_dashboard_ssot.py

# 3. Regenerate dashboard
python scripts/regenerate_dashboard.py --full

# 4. Run tests
pytest tests/dashboard/
```

### Start Dashboard Server

```bash
# Start HTTP server
python -m http.server 8765 --directory agentic_core/L6_observability/dashboards

# Open in browser
# http://localhost:8765/autonomy_dashboard.html
```

## Troubleshooting

### Dashboard Shows Stale Data

1. Clear browser cache (Ctrl+Shift+R)
2. Restart HTTP server
3. Run `python scripts/regenerate_dashboard.py --full`

### Tests Fail with Path Errors

The test suite uses `disable_path_shield` to access real files. If tests fail with path errors:

1. Ensure you're running from project root
2. Check that dashboard files exist
3. Run `python scripts/verify_dashboard.py --quick` to diagnose

### SSOT Mismatch Errors

If you see "SSOT Weight mismatch" errors:

1. Check that weights in `dashboard_ssot.yaml` sum to 1.0
2. Regenerate: `python agentic_core/L0_maintenance/scripts/generate_dashboard_ssot.py`
