# 🛡️ Sovereign Compliance Report: prompt_governance
**Date:** 2026-01-29 13:03:59 | **Status:** NON-COMPLIANT

## 📊 Executive Summary

* **Confidence Score:** 48.4%
* **Violations Detected:** 8
* **Integrity Drift:** 0
* **Violations Fixed:** 0

## 📁 Scan Scope

* **Total Files Scanned:** 78
* **Files Compliant:** 72
* **Files with Violations:** 8
* **Compliance Rate:** 92.3%

### File Types Analyzed

* **.backup:** 1 files
* **.jinja:** 51 files
* **.json:** 2 files
* **.py:** 24 files

## 🚨 Violations Detected

| # | Type | File | Issue | Severity | LLM | Confidence | Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | LOCATION | `.sovereign_healing_backup` | .sovereign_healing_backup | medium | No | 79.2% | Create directory: .sovereign_h... |
| 2 | LOCATION | `DashboardTestSuite.py` | Forbidden keyword | medium | No | 79.2% | Move DashboardTestSuite.py to ... |
| 3 | LOCATION | `SovereignPromptRenderer.py` | Forbidden keyword | medium | No | 79.2% | Move SovereignPromptRenderer.p... |
| 4 | LOCATION | `tests_golden_state_test_datasets.py` | Forbidden keyword | medium | No | 79.2% | Move tests_golden_state_test_d... |
| 5 | LOCATION | `audit_registry_linkages.py` | Forbidden extension .py for destination docs/reports | medium | No | 79.2% | RENAME: 'audit_registry_linkag... |
| 6 | LOCATION | `registry.json` | Forbidden keyword | medium | No | 96.8% | Fix location/naming issue: ART... |
| 7 | LOCATION | `registry.json.backup` | BROKEN BACKUP FILE: Remove stale backup file | medium | No | 79.2% | Fix location/naming issue: BRO... |
| 8 | ILLEGAL_CACHE_DIR | `.pytest_cache` | Illegal cache directory '.pytest_cache' in project... | low | No | 60.0% | Add .pytest_cache to .gitignor... |

## 🧠 AI Governance Log

| Decision Context | Confidence | LLM Triggered | Outcome |
| :--- | :--- | :--- | :--- |

### 📂 Affected Files

* `C:\Git\Agentic-Workflow\.pytest_cache`
* `C:\Git\Agentic-Workflow\.sovereign_healing_backup`
* `C:\Git\Agentic-Workflow\agentic_core\prompt_governance\agents\DashboardTestSuite.py`
* `C:\Git\Agentic-Workflow\agentic_core\prompt_governance\agents\SovereignPromptRenderer.py`
* `C:\Git\Agentic-Workflow\agentic_core\prompt_governance\meta_prompts\tests_golden_state_test_datasets.py`
* `C:\Git\Agentic-Workflow\agentic_core\prompt_governance\registry\registry.json.backup`
* `C:\Git\Agentic-Workflow\agentic_core\prompt_governance\scripts\audit_registry_linkages.py`
* `C:\Git\Agentic-Workflow\agentic_core\prompt_governance\version_registry\registry.json`
