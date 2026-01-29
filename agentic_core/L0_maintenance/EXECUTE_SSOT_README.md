# Execute SSOT: Autonomous Governance Engine

**Version:** 2.0 (Enhanced Safety & Telemetry)  
**Scope:** `agentic_core` & `apps_*`  
**Status:** Production Ready

---

## 1. Overview

The `execute_ssot.py` script is the sovereign enforcement engine for the Agentic Workflow architecture. It autonomously detects, reconciles, and validates deviations from the Single Source of Truth (SSOT).

### Core Capabilities
* **Phase 1 (Discovery):** Scans territory for violations (Naming, Import, Hierarchy).
* **Phase 2 (Reconciliation):** Autonomously fixes violations using registered `HealerAgents`.
* **Phase 3 (Validation):** Audits fixes using AST analysis to ensure code integrity.

---

## 2. Usage Guide

### Basic Command
Run a dry-run scan on a specific territory (Safe Mode).
```bash
python agentic_core/L0_maintenance/scripts/execute_ssot.py \
    --territory agentic_core \
    --dry-run

```

### Critical Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--territory <name>` | **Required.** Target folder to scan (e.g., `agentic_core`, `apps_private`). | N/A |
| `--dry-run` | Simulation mode. Logs planned actions but modifies nothing. | `False` (if omitted) |
| `--max-budget <int>` | Safety limit on number of files to fix in one run. | `100` |
| `--enable-llm` | Enables semantic healing (costs money, higher risk). | `False` |
| `--disable-llm` | Disable LLM for low-confidence decisions (default enabled). | `False` |
| `--domains` | Scan all major domains (Multi-Domain Mode). | `False` |
| `--agent <name>` | Run specific agent directly. | N/A |
| `--list-agents` | List discoverable agents. | `False` |
| `--enable-cda` | Enable CognitiveDispositionAgent for enhanced AI-powered violation analysis. | `False` |
| `--interactive` | Enable human-in-the-loop prompts (Default: Auto-Approve). | `False` |
| `--manual` | Disable autonomous mode (legacy). | `False` |
| `--validate` | Run in validation-only mode (CI/Dry-Run Mode). | `False` |
| `--capture-baseline` | Capture new Golden Baseline. | `False` |

---

## 3. Operator Runbook (Standard Procedure)

Follow this procedure for all maintenance operations to ensure safety.

### Step 1: Simulation (Dry Run)

Always start with a dry run to generate a manifest of potential changes.

```bash
python agentic_core/L0_maintenance/scripts/execute_ssot.py \
    --territory agentic_core \
    --dry-run

```

*Output:* `ssot_report_<TIMESTAMP>.json` 

### Step 2: Impact Analysis

Use the verification tool to audit the blast radius of the proposed changes.

```bash
python agentic_core/L0_maintenance/scripts/verify_manifest.py \
    ssot_report_<TIMESTAMP>.json

```

**Stop if you see:**

* `🚨 MASS DELETION RISK` 
* `🚨 HIGH BLAST RADIUS` 

### Step 3: Execution (Live Run)

If analysis passes, execute the live run with a defined budget.

```bash
python agentic_core/L0_maintenance/scripts/execute_ssot.py \
    --territory agentic_core \
    --max-budget 50

```

### Step 4: Verification

Check the final output summary:

* **Phase 3 Status:** Must be `clean`.
* **Failed Fixes:** Review logs for actions blocked by safety gates.

---

## 4. Safety Architecture (Hard Gates)

The engine enforces strict safety protocols that **cannot be overridden** by arguments.

### A. The Budget Gate

* **Mechanism:** Global counter of healing operations.
* **Trigger:** If `operations > max_budget`.
* **Result:** Immediate abort of subsequent fixes.
* **Log:** `blocked_by_safety: Budget exceeded`.

### B. The Cycle Gate

* **Mechanism:** Call-stack tracking for agents.
* **Trigger:** If Agent A tries to heal File X, which triggers Agent A again.
* **Result:** Operation blocked to prevent infinite recursion loops.
* **Log:** `blocked_by_safety: Cycle detected`.

### C. The Confidence Gate

* **Mechanism:** Weighted scoring (0.0 - 1.0) based on violation type and territory trust.
* **Trigger:** Score < 0.5 (or < 0.75 without LLM override).
* **Result:** Fix skipped. Manual intervention required.

---

## 5. Developer Guide: Creating Healer Agents

New agents must adhere to the `HealerProtocol` to be loaded by the engine.

### Standard Interface

Your agent must implement the `heal` method accepting a dictionary and returning a `HealResult`.

```python
from typing import Dict, Any

class MyNewFixer:
    def heal(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            violation: {
                'file': str,
                'type': str,
                ...
            }
        
        Returns:
            {
                'status': 'success' | 'failed' | 'skipped',
                'details': 'Fixed import on line 10',
                'artifacts': ['/path/to/file.py'],
                'errors': []
            }
        """
        # ... logic ...

```

### Legacy Support

Legacy agents (e.g., `fix(path)`) are automatically wrapped by the `LegacyAgentAdapter`. However, they should be refactored to the standard interface when possible for better telemetry.

---

## 6. Troubleshooting

**Issue:** "My fix was skipped."

* **Check:** Did you hit the `--max-budget`?
* **Check:** Was the confidence score too low? (Run with `--enable-llm` to boost semantic confidence if appropriate).

**Issue:** "Agent not found."

* **Check:** Does your agent class name contain `Agent` or `Validator`?
* **Check:** Is it in `agentic_core` or `apps_*`?
* **Check:** Does it implement a recognizable heal method (`heal`, `fix`, `run`, `resolve`)?
