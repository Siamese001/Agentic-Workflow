---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\core-addition-author-gate-governance-f3b9e2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\core-addition-author-gate-governance-f3b9e2.md'
source_sha256: 3036a4b11ba1dfc7e516ad7ec9aed674bf46fe084f64679f8729cbe1efa9a094
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: core-addition-author-gate-governance-f3b9e2
plan_type: governance_only
authored_at: 2026-05-12
last_updated: 2026-05-12
patch_applied: 2026-05-12-w7-complete
status: Completed
dod_exempt: false
touches_agentic_core: false
core_addition_author_gate_required: false
---

# Core Addition Author-Gate Governance

Harden the `agentic_core` / `apps_*` boundary with a formal static-analysis + pre-commit enforcement stack that **prevents app-specific meaning from entering core** at the moment of authoring — not at runtime.

---

## Design Recommendation: Why NOT Cascade HITL Author-Gate

> This section answers the user's direct question: *"Plan says Author Gate but I am not convinced."*

**The prompt's use of "Author-Gate" means author-time governance — static, pre-commit, pre-write.
It does NOT mean the Cascade Author-Gate HITL packet flow (ask_user_question + DECISION_CAPTURED).**

### Decision Table

| Mechanism | Good for | Bad for | Verdict |
|---|---|---|---|
| **Cascade Author-Gate (HITL packet)** | Ambiguous design decisions where human judgment resolves genuine uncertainty (e.g., refactor scope, deletion strategy) | Deterministic policy violations that have one correct answer | ❌ Wrong tool — boundary violations have zero ambiguity |
| **always_on Rule** | Guiding Cascade behavior in every turn | Enforcing repo state — Cascade can be bypassed or hallucinated | ⚠️ Necessary but not sufficient |
| **pre_write hook (Windsurf)** | Blocking writes at the moment Cascade attempts them | Git CLI or IDE direct edits that bypass Cascade | ✅ Best first-defense for AI-authored code |
| **Pre-commit gate (.pre-commit-config.yaml)** | Blocking human + AI commits with git history as enforcement surface | Rapid iteration speed (adds latency) | ✅ Best backstop for all authors |
| **CI scanner (GitHub Actions)** | Drift detection, advisory reporting, audit trail | Blocking force-pushes or already-merged leakage | ✅ Best audit surface + golden signal |
| **JSON receipt schema** | Machine-verifiable proof that a human reviewed a platform-core change | Lightweight refactors that don't need ceremony | ✅ Required ONLY for `platform_core_change` plan type |

### Recommended Stack (Defense in Depth)

```
Author intent
    │
    ▼
[1] always_on RULE — guides Cascade, loads on every turn
    │  (cognitive pre-flight: classify before edit)
    ▼
[2] pre_write hook — blocks Cascade writes to agentic_core/ unless
    │  CoreAdditionAuthorGateReceipt exists + is PASS
    ▼
[3] pre-commit gate (check_agentic_core_addition.py) — blocks git commit
    │  for human + AI edits; runs literal scan + receipt proof
    ▼
[4] CI scanner (GOV-3 gate) — fail-closed on PR/push for agentic_core diffs
    │  emits JSON artifact; advisory only via explicit local/dev override
    ▼
[5] Receipt schema (CoreAdditionAuthorGateReceipt.schema.json)
    │  consumed by [2], [3], [4] as the single proof object
    ▼
PASS: agentic_core edit with valid receipt + clean scan
FAIL: any layer catches violation → block + diagnostic
```

**Why not Cascade Author-Gate?** Because a boundary violation is not an ambiguous decision — it has one correct answer: move the app-specific logic to `apps_*/config/domain_contract/`. The Author-Gate HITL packet is designed for *genuine design ambiguity*, not for *catching policy violations*. Static checks (hooks + CI) are faster, cheaper, bypass-resistant, and auditable via git history.

**What Author-Gate IS used for here (narrowly)**: When a developer believes a proposed core addition *genuinely is* generic spine infrastructure and wants to claim `plan_type=platform_core_change`, they invoke the Author-Gate decision flow to produce the `CoreAdditionAuthorGateReceipt`. That receipt is then consumed by the static checks. The Author-Gate produces the receipt; it does not *replace* the static checks.

---

## Context (SCQA)

- **Situation** — `agentic_core/` is the spine substrate for all apps. Rules `agentic-core-static.md`, `boundary-audit-required.md`, `agentic-core-glob-lock.md`, CI gate `check_agentic_core_static_boundary.py`, and governance test `test_agentic_core_static_boundary.py` exist. The pre-write hook (`pre_write_gate.py`) exists but does NOT check for app leakage or CoreAdditionAuthorGateReceipt.
- **Complication** — The current enforcement is advisory or model-guided only. A developer (or Cascade) can claim "this is generic" and write app-specific meaning into core without any machine-verifiable proof. The `check_agentic_core_static_boundary.py` gate has an advisory sunset and wraps pytest, but there is no pre-write blocking, no receipt schema, no plan-type validation, and no plug-in proof requirement.
- **Question** — How do we make it mechanically impossible to add app-specific meaning to `agentic_core/` at author time, without slowing down legitimate generic core improvements?
- **Answer** — Layer five enforcement tiers: an updated always_on rule, a pre-write hook that checks receipt presence, a plan-metadata validator, a receipt JSON schema, and a hardened CI gate — all feeding from a single `CoreAdditionAuthorGateReceipt` proof object.

---

## Inventory: What Already Exists (W0 Discovery)

| Asset | Location | Status | Gap |
|---|---|---|---|
| Core arch law rule | `.windsurf/rules/agentic-core-static.md` | ✅ exists, always_on | Missing formal `Core Addition Author-Gate` section |
| Glob-lock rule | `.windsurf/rules/agentic-core-glob-lock.md` | ✅ exists, model_decision | No pre-write hook enforcement of receipt |
| Boundary audit rule | `.windsurf/rules/boundary-audit-required.md` | ✅ exists | No plan_type metadata validation |
| Pre-write hook | `.windsurf/scripts/pre_write_gate.py` | ✅ exists + extended (W3) | `check_core_addition_receipt()` added; 27 tests green |
| Boundary CI gate | `ops_scripts/ci/check_agentic_core_static_boundary.py` | ✅ exists (advisory) | Advisory only; no receipt proof; sunset 2026-06-15 |
| Governance test | `tests/governance/test_agentic_core_static_boundary.py` | ✅ exists | Missing plug-in proof, negative controls for plan_type |
| Plan template | `.windsurf/templates/execution-plan-template.md` | ✅ updated (W1) | `touches_agentic_core`, `core_addition_author_gate_required`, `author_gate_receipt_ref` added |
| Receipt schema | `.windsurf/schemas/CoreAdditionAuthorGateReceipt.schema.json` | ✅ created (W2) | 19 schema validation tests green |
| SSOT folder check | `.windsurf/scripts/_ssot_folder_check.py` | ✅ exists | Not applicable |
| App literal list | `tests/governance/test_agentic_core_static_boundary.py` | ✅ partial | Missing newer literals (company_brief, interview_card, recruiter, etc.) |

---

## Wave Structure

| Wave | Scope | Metric | Tokens | Status |
|------|-------|--------|--------|--------|
| W0 | Discovery + inventory | Zero writes | ~200 | ✅ DONE |
| W1 | Rule update + plan template metadata | Rule + template updated; 1,074 bytes headroom | ~800 | ✅ DONE |
| W2 | Receipt schema + schema validation tests | Schema created; 19 tests green | ~600 | ✅ DONE |
| W3 | Pre-write hook + core write guard | Hook blocks writes; 27 tests green | ~700 | ✅ DONE |
| W4 | CI scanner / no-app-literal proof hardening | GOV-3 gate; 19+3 literals; pre-commit wired; 1,074 bytes headroom | ~600 | ✅ DONE |
| W5 | Negative-control test suite | 24 tests green | ~800 | ✅ DONE |
| W6 | Plug-in proof (future apps_foo fixture) | apps_foo registers without core edit | ~400 | ✅ DONE |
| W7 | Integration + evidence bundle | All gates green; receipt example | ~400 | ✅ DONE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Rule: Core Addition Author-Gate section | `agentic-core-static.md` | Must not exceed always_on token budget (§33) | ~400 | ✅ DONE |
| W1.P2 | Plan template: new metadata fields | `execution-plan-template.md` | Backward compat with 400+ existing plans | ~400 | ✅ DONE |
| W2.P1 | Receipt schema definition | `.windsurf/schemas/CoreAdditionAuthorGateReceipt.schema.json` | Field coverage without redundancy to glob-lock receipt | ~300 | ✅ DONE |
| W2.P2 | Schema validation + negative control tests | `tests/governance/test_core_addition_receipt_schema.py` | JSON Schema draft-7 vs draft-2020 compatibility | ~300 | ✅ DONE |
| W3.P1 | Pre-write hook: agentic_core receipt check | `.windsurf/scripts/pre_write_gate.py` (extend) | Hook already has multiple checks; must not regress | ~400 | ✅ DONE |
| W3.P2 | Hook fail-closed tests | `tests/unit/windsurf_scripts/test_pre_write_gate_core_guard.py` | Must test malformed/missing/expired receipt paths | ~300 | ✅ DONE |
| W4.P1 | Extend forbidden literal list | `tests/governance/test_agentic_core_static_boundary.py` | Add ~12 missing literals; validate allowlist still works | ~300 | ✅ DONE |
| W4.P2 | GOV-3 CI gate (hardened, fail-closed capable) | `ops_scripts/ci/check_agentic_core_addition.py` (NEW) | Replaces advisory wrapper; emits JSON artifact | ~300 | ✅ DONE |
| W5.P1 | Negative control test suite | `tests/governance/test_core_addition_negative_controls.py` (NEW) | 24 tests; covers all 10 forbidden semantic categories + W4B regression | ~800 | ✅ DONE |
| W6.P1 | Plug-in proof fixture | `tests/governance/fixtures/apps_foo_stub/` (NEW) | 4 tests; zero core edits proven by SHA-256 snapshot | ~400 | ✅ DONE |
| W7.P1 | Integration run + receipt example | `artifacts/governance/core_addition_example_receipt.json` | Schema validated; evidence bundle written | ~400 | ✅ DONE |

---

## Target Files

### Inspect (read-only during W0)
- `.windsurf/rules/agentic-core-static.md`
- `.windsurf/rules/agentic-core-glob-lock.md`
- `.windsurf/rules/boundary-audit-required.md`
- `.windsurf/scripts/pre_write_gate.py`
- `.windsurf/scripts/_ssot_folder_check.py` (pattern reference)
- `ops_scripts/ci/check_agentic_core_static_boundary.py`
- `tests/governance/test_agentic_core_static_boundary.py`
- `.windsurf/templates/execution-plan-template.md`
- `.windsurf/hooks.json`
- `ops_scripts/ci/run_contract_gates.py`
- `.pre-commit-config.yaml` — pre-commit hook registration target for GOV-3 gate

### Modify
- `.windsurf/rules/agentic-core-static.md` — add `## Core Addition Author-Gate` section
- `.windsurf/templates/execution-plan-template.md` — add `plan_type`, `touches_agentic_core`, `core_addition_author_gate_required`, `author_gate_receipt_ref` fields
- `.windsurf/scripts/pre_write_gate.py` — extend with `check_core_addition_receipt()`
- `tests/governance/test_agentic_core_static_boundary.py` — extend literal list
- `ops_scripts/ci/run_contract_gates.py` — register GOV-3 gate
- `.pre-commit-config.yaml` — add `check_agentic_core_addition.py` as pre-commit hook (fail-closed, runs on `agentic_core/**` diffs)

### Create (New Files)
- `.windsurf/schemas/CoreAdditionAuthorGateReceipt.schema.json`
- `ops_scripts/ci/check_agentic_core_addition.py` — GOV-3 CI gate (replaces advisory wrapper)
- `tests/governance/test_core_addition_receipt_schema.py` — schema validation tests
- `tests/governance/test_core_addition_negative_controls.py` — 20 negative control tests
- `tests/governance/fixtures/apps_foo_stub/` — plug-in proof fixture
- `artifacts/governance/core_addition_example_receipt.json` — reference receipt

---

## W1 — Rule + Plan Template

### W1.P1 — `agentic-core-static.md`: New Section

Add after `## Receipt Required`:

```markdown
## Core Addition Author-Gate

> ⛔ Any edit to `agentic_core/` that adds new mechanism, layer, contract, 
> or capability MUST carry a `CoreAdditionAuthorGateReceipt` with verdict=PASS 
> before the write is permitted.

### Canonical Rule

- `agentic_core` is spine substrate, not app behavior.
- Core owns reusable mechanisms. Apps own meaning.
- `agentic_core` edits require `plan_type: platform_core_change`.
- `agentic_core` edits require `CoreAdditionAuthorGateReceipt`.
- Missing receipt → fail closed.
- App literals in `agentic_core` → fail.
- App-specific branches / defaults / route choices / validation rules /
  graph semantics / prompt behavior / writeback behavior / eval thresholds
  in `agentic_core` → fail.
- Future `apps_*` MUST be able to use any new mechanism via app-owned
  config only — zero `agentic_core` edits required.

### Plan Metadata Required

Plans that `touches_agentic_core: true` MUST declare:
  plan_type: platform_core_change
  core_addition_author_gate_required: true
  author_gate_receipt_ref: artifacts/governance/<receipt>.json

### Enforcement Chain

| Layer | Component | Blocks |
|---|---|---|
| 1 | this rule (always_on) | Cascade edits |
| 2 | `pre_write_gate.py` `check_core_addition_receipt()` | Cascade writes |
| 3 | `check_agentic_core_addition.py` (GOV-3) | git commits (pre-commit + CI) |
| 4 | `test_core_addition_negative_controls.py` | CI test suite |
```

**Token budget note**: The addition is ~300 bytes. Current rule is ~3KB. Always-on budget gate (§33) must pass — validate after W1.P1.

### W1.P2 — Plan Template Metadata Fields

Add to frontmatter block of `execution-plan-template.md`:

```yaml
# Core addition governance (required when touches_agentic_core: true)
touches_agentic_core: false          # true | false
core_addition_author_gate_required: false  # auto-set true when touches_agentic_core: true
author_gate_receipt_ref: ""          # path to CoreAdditionAuthorGateReceipt JSON; required when touches_agentic_core: true
# plan_type taxonomy extended:
#   platform_core_change → REQUIRES author_gate_receipt_ref + CoreAdditionAuthorGateReceipt.verdict=PASS
```

Existing plan_type values are preserved. The three new fields default to `false`/`""` for backward compatibility — existing plans do not need updates.

---

## W2 — Receipt Schema

### CoreAdditionAuthorGateReceipt Schema

File: `.windsurf/schemas/CoreAdditionAuthorGateReceipt.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "CoreAdditionAuthorGateReceipt",
  "title": "CoreAdditionAuthorGateReceipt",
  "description": "Author-time proof that an agentic_core addition is generic spine substrate.",
  "type": "object",
  "required": [
    "receipt_type", "receipt_version", "plan_id", "plan_type",
    "author", "created_at", "changed_paths", "governed_object",
    "decision", "tests", "artifacts", "fail_closed_conditions", "signature"
  ],
  "properties": {
    "receipt_type": {"const": "CoreAdditionAuthorGateReceipt"},
    "receipt_version": {"type": "string", "pattern": "^\\d+\\.\\d+$"},
    "plan_id": {"type": "string", "minLength": 1},
    "plan_type": {"const": "platform_core_change"},
    "author": {"type": "string", "minLength": 1},
    "created_at": {"type": "string", "format": "date-time"},
    "changed_paths": {
      "type": "array",
      "items": {"type": "string", "pattern": "^agentic_core/"},
      "minItems": 1
    },
    "governed_object": {
      "type": "object",
      "required": ["object_type", "object_ref", "object_digest"],
      "properties": {
        "object_type": {"enum": ["module", "class", "function", "contract", "layer"]},
        "object_ref": {"type": "string"},
        "object_digest": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"}
      }
    },
    "decision": {
      "type": "object",
      "required": ["verdict", "decisive_reason", "core_rule"],
      "properties": {
        "verdict": {"enum": ["PASS", "FAIL"]},
        "decisive_reason": {"type": "string", "minLength": 20},
        "core_rule": {"type": "string"}
      }
    },
    "tests": {
      "type": "object",
      "required": [
        "spine_substrate_test", "any_app_capability_test", "app_owned_meaning_test",
        "no_app_literal_test", "plugin_test", "negative_control_test",
        "platform_approval_test", "boundary_preservation_test",
        "contract_compatibility_test", "runtime_proof_compatibility_test"
      ],
      "additionalProperties": false,
      "properties": {
        "spine_substrate_test":              {"$ref": "#/$defs/testResult"},
        "any_app_capability_test":           {"$ref": "#/$defs/testResult"},
        "app_owned_meaning_test":            {"$ref": "#/$defs/testResult"},
        "no_app_literal_test":               {"$ref": "#/$defs/testResult"},
        "plugin_test":                       {"$ref": "#/$defs/testResult"},
        "negative_control_test":             {"$ref": "#/$defs/testResult"},
        "platform_approval_test":            {"$ref": "#/$defs/testResult"},
        "boundary_preservation_test":        {"$ref": "#/$defs/testResult"},
        "contract_compatibility_test":       {"$ref": "#/$defs/testResult"},
        "runtime_proof_compatibility_test":  {"$ref": "#/$defs/testResult"}
      }
    },
    "$defs": {
      "testResult": {
        "type": "object",
        "required": ["result", "evidence"],
        "additionalProperties": false,
        "properties": {
          "result":               {"enum": ["PASS", "FAIL"]},
          "evidence":            {"type": "string", "minLength": 1},
          "not_applicable_reason": {"type": "string", "minLength": 10},
          "deciding_authority":  {"type": "string"},
          "policy_ref":          {"type": "string"}
        }
      }
    },
    "artifacts": {
      "type": "object",
      "required": [
        "no_app_literal_scan_ref", "strict_scan_ref",
        "negative_control_results_ref", "plugin_proof_ref",
        "boundary_scan_ref", "contract_schema_scan_ref"
      ],
      "additionalProperties": {
        "type": "object",
        "required": ["path", "digest", "verdict", "plan_id", "freshness_ts"],
        "properties": {
          "path": {"type": "string"},
          "digest": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
          "verdict": {"enum": ["PASS", "FAIL"]},
          "plan_id": {"type": "string"},
          "freshness_ts": {"type": "string", "format": "date-time"},
          "changed_paths_covered": {"type": "boolean"}
        }
      }
    },
    "fail_closed_conditions": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 3
    },
    "signature": {
      "type": "object",
      "required": ["receipt_digest"],
      "properties": {
        "receipt_digest": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
        "hmac_sig": {"type": "string"}
      }
    }
  },
  "additionalProperties": false
}
```

### Fail-Closed Conditions (required in every receipt)

Minimum three entries:
1. `"plan_type != platform_core_change → BLOCK"`
2. `"no_app_literal_scan_ref missing → BLOCK"`
3. `"decision.verdict != PASS → BLOCK"`

### Test A/B/C/D/E/F/G/H/I/J — PASS/FAIL Criteria

| Test | PASS condition | FAIL condition |
|---|---|---|
| **A. spine_substrate_test** | Change implements a generic spine mechanism reusable by any `apps_*` via config | Change implements behavior specific to one app's domain meaning |
| **B. any_app_capability_test** | Any app can elect to use the capability class via app-owned profile/config — no core edit | App must edit `agentic_core/` to use it |
| **C. app_owned_meaning_test** | ALL app meaning lives in `apps_*/` profiles, manifests, adapters, contracts, prompts, rubrics, schemas, evals, or configs | Any meaning is hardcoded in `agentic_core/` |
| **D. no_app_literal_test** | Zero forbidden literals in changed paths (see literal list in W4) | ANY forbidden literal present |
| **E. plugin_test** | A simulated `apps_foo` fixture can register/use the capability using only `apps_foo/config/` — zero `agentic_core/` edits needed | `apps_foo` must touch `agentic_core/` to use the capability |
| **F. negative_control_test** | CI proves app behavior injected into core makes `test_core_addition_negative_controls.py` fail | Negative controls are absent or trivially pass |
| **G. platform_approval_test** | `plan_type=platform_core_change` + receipt present + `verdict=PASS` | Either field missing |
| **H. boundary_preservation_test** | No spine layer gains authority it does not own per layer contract (`L0`, `L1`, `L2`, `L3`, `Exit`, `UWG`, `L4`, `L5`, `L6`) | Any layer's authority expands without contract update |
| **I. contract_compatibility_test** | All signed contract handoffs remain intact; no loose objects; no implicit authority | Unsigned contract, loose object, or implicit authority added |
| **J. runtime_proof_compatibility_test** | `99` proof/audit layer can verify and audit the new mechanism without bypass or new exemption | New mechanism requires bypass or new guardian exemption to pass proof |

---

## W3 — Pre-Write Hook Extension

### Extension to `pre_write_gate.py`

Add function `check_core_addition_receipt(file_path: str, new_string: str) -> str | None`:

```python
def check_core_addition_receipt(file_path: str, new_string: str) -> str | None:
    """
    Block writes to agentic_core/ unless CoreAdditionAuthorGateReceipt exists and passes.
    Returns block reason string or None if allowed.
    Fail policy: CLOSED — missing/malformed receipt → block.
    """
    from pathlib import Path
    import json, os, re

    if "agentic_core/" not in file_path.replace("\\", "/"):
        return None  # not a core write

    bypass = os.environ.get("CORE_ADDITION_GATE_BYPASS")
    if bypass:
        # Bypass is local-write only. Log an audit event; CI will fail if this
        # event exists without an emergency_approval_receipt_ref in the record.
        _log_bypass_event(file_path, "CORE_ADDITION_GATE_BYPASS")
        return None

    # Locate receipt from current plan metadata — NOT by scanning latest file.
    # The active plan frontmatter must declare author_gate_receipt_ref explicitly.
    plan_meta = _load_active_plan_metadata()  # reads current plan frontmatter
    receipt_ref = plan_meta.get("author_gate_receipt_ref", "").strip()
    if not receipt_ref:
        return (
            "CORE_WRITE_BLOCKED: active plan has no author_gate_receipt_ref in frontmatter. "
            "Declare author_gate_receipt_ref: artifacts/governance/<receipt>.json and "
            "set plan_type: platform_core_change before editing agentic_core/."
        )

    receipt_path = repo_root / receipt_ref
    if not receipt_path.exists():
        return f"CORE_WRITE_BLOCKED: author_gate_receipt_ref path does not exist: {receipt_ref}"

    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"CORE_WRITE_BLOCKED: Receipt parse error: {exc}. Fail closed."

    # Validate receipt fields against active plan and proposed write
    current_plan_id = plan_meta.get("plan_id", "")
    if receipt.get("receipt_type") != "CoreAdditionAuthorGateReceipt":
        return "CORE_WRITE_BLOCKED: receipt_type mismatch. Expected CoreAdditionAuthorGateReceipt."
    if receipt.get("plan_type") != "platform_core_change":
        return "CORE_WRITE_BLOCKED: receipt.plan_type must be platform_core_change."
    if receipt.get("plan_id") != current_plan_id:
        return (
            f"CORE_WRITE_BLOCKED: receipt.plan_id '{receipt.get('plan_id')}' "
            f"does not match active plan_id '{current_plan_id}'."
        )
    if receipt.get("decision", {}).get("verdict") != "PASS":
        return "CORE_WRITE_BLOCKED: receipt.decision.verdict is not PASS."
    # Verify the attempted file path is covered by receipt.changed_paths
    norm_path = file_path.replace("\\", "/")
    covered = any(
        norm_path.endswith(cp.replace("\\", "/")) or cp.replace("\\", "/") in norm_path
        for cp in receipt.get("changed_paths", [])
    )
    if not covered:
        return (
            f"CORE_WRITE_BLOCKED: '{norm_path}' is not listed in receipt.changed_paths. "
            "Add this path to the receipt before writing."
        )
    # Validate receipt_digest is present (full HMAC validation deferred to CI)
    if not receipt.get("signature", {}).get("receipt_digest", "").startswith("sha256:"):
        return "CORE_WRITE_BLOCKED: receipt.signature.receipt_digest is missing or malformed."

    # Literal scan on new_string
    FORBIDDEN = [
        "apps_rg", "apps_lic", "apps_research", "apps_qna",
        "resume_generator", "outreach", "company_brief", "interview_card",
        "recruiter", "JD-specific", "resume-specific", "LIC-specific",
        "RG-specific", "QNA-specific", "research-specific",
    ]
    for lit in FORBIDDEN:
        if lit in new_string:
            return f"CORE_WRITE_BLOCKED: Forbidden app literal '{lit}' in agentic_core/ write."

    return None  # all checks pass
```

Integrate into `_check_new_content()` pipeline immediately before the `return None` exit.

**Bypass**: `CORE_ADDITION_GATE_BYPASS=1` — logged to `artifacts/windsurf/core_addition_gate_violations.jsonl`.

### W3 vs W4/W7 Digest Validation Split

**W3 pre-write hook — lightweight receipt binding (fast-path, author-time):**
- Active plan `author_gate_receipt_ref` declared and path exists
- `receipt.plan_id` matches active plan `plan_id`
- `receipt.decision.verdict == PASS`
- Attempted file path covered in `receipt.changed_paths`
- `receipt.signature.receipt_digest` present and `sha256:` prefixed (shape check only)
- Literal scan on `new_string` clean

**W4/W7 CI gate — full proof validation (authoritative, pre-commit + CI):**
- `receipt_digest` recomputed from receipt content and verified
- All `receipt.artifacts` refs loaded from disk (not accepted as string paths)
- Each artifact `digest` recomputed and validated against stored value
- Each artifact `verdict == PASS`
- Each artifact `plan_id` matches receipt `plan_id`
- `changed_paths` covered by at least one artifact's `changed_paths_covered: true`
- `governed_object.object_digest` or `patch_digest` matches current diff

### Hook Tests (`test_pre_write_gate_core_guard.py`)

| Test name | Expected outcome |
|---|---|
| `test_no_receipt_blocks_core_write` | exit 2 + `CORE_WRITE_BLOCKED: active plan has no author_gate_receipt_ref` |
| `test_malformed_receipt_blocks_core_write` | exit 2 + `Receipt parse error` |
| `test_wrong_receipt_type_blocks` | exit 2 + `receipt_type mismatch` |
| `test_wrong_plan_type_blocks` | exit 2 + `plan_type must be platform_core_change` |
| `test_verdict_fail_blocks` | exit 2 + `verdict is not PASS` |
| `test_forbidden_literal_in_new_string_blocks` | exit 2 + `Forbidden app literal` |
| `test_valid_receipt_pass_verdict_allows` | exit 0 |
| `test_non_core_write_not_checked` | exit 0 (apps_rg/ path skips check) |
| `test_bypass_env_var_allows` | exit 0 + violation logged |
| `test_missing_changed_paths_blocks` | exit 2 + fail closed |

---

## W4 — CI Scanner / Literal Proof

### GOV-3 Gate: `check_agentic_core_addition.py`

Location: `ops_scripts/ci/check_agentic_core_addition.py`

**Replaces** `check_agentic_core_static_boundary.py` advisory wrapper over time (keep existing gate; this is a hardened companion).

Checks:
1. **Forbidden literal scan** — regex over all `.py` files in `agentic_core/` excluding allowlist
2. **app_id branch scan** — `if app_id ==`, `app_id ==`, `tenant_id ==` with apps_ values
3. **App-specific route scan** — detect app-named route behavior, app_id/app_name branches containing route choices, and app-specific defaults. Generic canonical route enums are allowlisted and MUST NOT trigger false positives:
   - `R1A_EXACT_CACHE`, `R1B_SEMANTIC_CACHE`, `R5_FALLBACK`
   - `R3_SIMPLE_GROUNDED_READ`, `R4_SINGLE_ACTION`, `R3R4_MANAGED_WORKFLOW`
   Pattern targets: route names containing app-literal prefixes (e.g. `R1_RESUME_GENERATION`, `R4_MANAGED_DRAFT`) or any route assigned inside an `if app_id ==` / `if app_name ==` branch
4. **App-specific default scan** — hardcoded app defaults in function signatures
5. **Graph-semantic scan** — app-named edge types in semantic graph code
6. **Prompt-behavior scan** — app-named prompt templates or assembly rules in core
7. **Writeback scan** — app-named writeback targets in L6/ledger code
8. **Eval-threshold scan** — numeric thresholds with app name comments/vars
9. **Receipt presence** — if any of checks 1-8 are non-zero AND no receipt → FAIL
10. **plan_type metadata** — if diff touches agentic_core/ and no receipt → FAIL

Emits: `artifacts/ci/agentic_core_addition_gate.json`

Modes: **fail-closed by default** for any diff that touches `agentic_core/`. Advisory mode is opt-in for local/dev environments only via `CORE_ADDITION_GATE_ADVISORY=1`. CI MUST NOT set this variable.

Bypass: `CORE_ADDITION_GATE_BYPASS=1` — local writes only. Writes an audit JSONL event to `artifacts/windsurf/core_addition_gate_violations.jsonl`. CI fails if bypass evidence exists in that JSONL without a matching `emergency_approval_receipt_ref` field on the bypass event.

### Extended Forbidden Literal List (W4.P1)

Extend `FORBIDDEN_APP_PATTERNS` in `test_agentic_core_static_boundary.py`:

```python
# Additional literals (W4 addition)
(r'company_brief', "app-specific company brief", "HIGH"),
(r'interview_card', "app-specific interview card", "HIGH"),
(r'recruiter', "app-specific recruiter context", "MEDIUM"),
(r'resume_generator', "app-specific resume generator", "HIGH"),
(r'outreach', "app-specific outreach mode", "MEDIUM"),
(r'JD.specific', "app-specific JD semantics", "MEDIUM"),
(r'resume.specific', "app-specific resume semantics", "MEDIUM"),
(r'LIC.specific', "apps_lic specific", "HIGH"),
(r'RG.specific', "apps_rg specific", "HIGH"),
(r'QNA.specific', "apps_qna specific", "HIGH"),
(r'research.specific', "apps_research specific", "HIGH"),
(r'["\']apps_architect["\']', "hardcoded apps_architect", "HIGH"),
(r'["\']apps_eval["\']', "hardcoded apps_eval", "HIGH"),
(r'["\']apps_rfp["\']', "hardcoded apps_rfp", "HIGH"),
```

---

## W5 — Negative-Control Test Suite

File: `tests/governance/test_core_addition_negative_controls.py`

### Test Definitions

```python
# === NEGATIVE CONTROLS (must FAIL when app behavior in core) ===

def test_core_edit_without_platform_plan_type_fails():
    # Simulate plan metadata with plan_type != platform_core_change
    # Assert: receipt validator returns FAIL

def test_core_edit_without_author_gate_receipt_fails():
    # Simulate no receipt in artifacts/governance/core_addition_*.json
    # Assert: pre_write check returns block reason

def test_core_literal_apps_rg_fails():
    # Inject 'apps_rg' literal into simulated agentic_core file content
    # Assert: literal scanner flags CRITICAL

def test_core_literal_apps_lic_fails():
    # Same pattern for apps_lic

def test_core_literal_apps_research_fails():
    # Same pattern for apps_research

def test_core_literal_apps_qna_fails():
    # Same pattern for apps_qna

def test_core_app_id_branch_fails():
    # Inject: if app_id == "apps_rg":
    # Assert: scanner flags app_id branching CRITICAL

def test_core_app_specific_route_default_fails():
    # Inject: default_route = "R1_RESUME_GENERATION"
    # Assert: route scan flags HIGH

def test_core_app_specific_prompt_behavior_fails():
    # Inject app-named prompt template ref in core
    # Assert: prompt-behavior scan flags HIGH

def test_core_app_specific_graph_semantics_fails():
    # Inject app-named edge type in semantic graph code
    # Assert: graph-semantic scan flags HIGH

def test_core_app_specific_validation_rule_fails():
    # Inject app-named validation constant in core contract
    # Assert: literal scan flags

def test_core_app_specific_writeback_behavior_fails():
    # Inject app-named writeback target in L6 code
    # Assert: writeback scan flags HIGH

# === POSITIVE CONTROLS (must PASS for generic substrate) ===

def test_generic_plugin_mechanism_passes():
    # Generic resolver consuming profile ref only
    # Assert: all checks pass

def test_future_app_can_register_without_core_edit():
    # apps_foo_stub fixture: registers capability via config only
    # Assert: no agentic_core files were touched

# === RECEIPT FIELD NEGATIVE CONTROLS ===

def test_receipt_requires_negative_controls():
    # Receipt with tests.negative_control_test.result = "SKIP"  (SKIP no longer valid)
    # Assert: schema validator rejects — only PASS/FAIL allowed for required tests

def test_receipt_requires_no_app_literal_scan():
    # Receipt missing artifacts.no_app_literal_scan_ref
    # Assert: schema validator rejects (required field)

def test_receipt_requires_plugin_proof():
    # Receipt missing artifacts.plugin_proof_ref
    # Assert: schema validator rejects

def test_receipt_requires_contract_compatibility():
    # Receipt with tests.contract_compatibility_test.result = "FAIL"
    # Assert: gate blocks with FAIL verdict

def test_receipt_requires_boundary_preservation():
    # Receipt missing tests.boundary_preservation_test
    # Assert: schema validator rejects

def test_strict_scan_blocks_unknown_core_change():
    # Simulate new agentic_core/ file with no receipt in FAIL-CLOSED mode
    # Assert: GOV-3 gate exits 2
```

---

## W6 — Plug-In Proof

### Fixture: `tests/governance/fixtures/apps_foo_stub/`

```
tests/governance/fixtures/apps_foo_stub/
├── __init__.py
├── config/
│   └── domain_contract/
│       └── route_profile.yaml     # apps_foo route config — no agentic_core edit
└── test_apps_foo_can_plug_in.py   # proof: capability usable without touching core
```

`route_profile.yaml`:
```yaml
app_id: apps_foo
plan_type: apps_work
route_class: generic_spine
capability_refs:
  - agentic_core.L0_routing.generic_route_resolver
  - agentic_core.L1_cognition.generic_profile_planner
```

`test_apps_foo_can_plug_in.py`:
```python
def test_future_app_plugin_needs_no_core_edit():
    """
    PASS: apps_foo can register and use core capabilities using only
    apps_foo/config/ — zero agentic_core files touched.
    """
    core_files_before = set(Path("agentic_core").rglob("*.py"))
    _simulate_apps_foo_registration()  # reads route_profile.yaml, calls generic resolver
    core_files_after = set(Path("agentic_core").rglob("*.py"))
    assert core_files_before == core_files_after, "Core files changed — plug-in test FAIL"
```

---

## W7 — Integration + Evidence Bundle

### Final Acceptance Run

```bash
# 1. Run negative-control suite
pytest tests/governance/test_core_addition_negative_controls.py -v

# 2. Run schema validation suite
pytest tests/governance/test_core_addition_receipt_schema.py -v

# 3. Run pre-write hook tests
pytest tests/unit/windsurf_scripts/test_pre_write_gate_core_guard.py -v

# 4. Run hardened CI gate in fail-closed mode
python ops_scripts/ci/check_agentic_core_addition.py

# 4b. Run in advisory mode (local/dev only — CI must not use this)
CORE_ADDITION_GATE_ADVISORY=1 python ops_scripts/ci/check_agentic_core_addition.py

# 5. Run existing governance gate (must still pass)
python ops_scripts/ci/check_agentic_core_static_boundary.py

# 6. Run full governance suite
pytest tests/governance/ -v

# 7. Run contract gates
python ops_scripts/ci/run_contract_gates.py
```

### Reference Receipt: `artifacts/governance/core_addition_example_receipt.json`

```json
{
  "receipt_type": "CoreAdditionAuthorGateReceipt",
  "receipt_version": "1.0",
  "plan_id": "core-addition-author-gate-governance-f3b9e2",
  "plan_type": "platform_core_change",
  "author": "platform-engineering",
  "created_at": "2026-05-12T00:00:00Z",
  "changed_paths": ["agentic_core/L0_routing/generic_example.py"],
  "governed_object": {
    "object_type": "module",
    "object_ref": "agentic_core.L0_routing.generic_example",
    "object_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
  },
  "decision": {
    "verdict": "PASS",
    "decisive_reason": "Adds generic route resolver usable by any app via route_profile.yaml — no app literal, no app branch, no app default.",
    "core_rule": "agentic-core-static.md § Core Addition Author-Gate"
  },
  "tests": {
    "spine_substrate_test":         {"result": "PASS", "evidence": "Mechanism delegates to app profile; no hardcoded meaning."},
    "any_app_capability_test":      {"result": "PASS", "evidence": "apps_foo fixture proves registration works with app-owned config only."},
    "app_owned_meaning_test":       {"result": "PASS", "evidence": "All route names live in apps_*/config/domain_contract/route_profile.yaml."},
    "no_app_literal_test":          {"result": "PASS", "evidence": "artifacts/ci/no_app_literal_scan.json — zero findings."},
    "plugin_test":                  {"result": "PASS", "evidence": "test_apps_foo_can_plug_in.py passes; zero core files changed."},
    "negative_control_test":        {"result": "PASS", "evidence": "test_core_addition_negative_controls.py — all 20 pass."},
    "platform_approval_test":       {"result": "PASS", "evidence": "plan_type=platform_core_change confirmed; this receipt present."},
    "boundary_preservation_test":   {"result": "PASS", "evidence": "Layer authority unchanged; no new GateVerdict surfaces."},
    "contract_compatibility_test":  {"result": "PASS", "evidence": "All signed handoffs intact; no loose objects introduced."},
    "runtime_proof_compatibility_test": {"result": "PASS", "evidence": "99 audit layer validates generic mechanism without bypass."}
  },
  "artifacts": {
    "no_app_literal_scan_ref": {
      "path": "artifacts/ci/no_app_literal_scan.json",
      "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "verdict": "PASS",
      "plan_id": "core-addition-author-gate-governance-f3b9e2",
      "freshness_ts": "2026-05-12T00:00:00Z",
      "changed_paths_covered": true
    },
    "strict_scan_ref": {
      "path": "artifacts/ci/agentic_core_addition_gate.json",
      "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "verdict": "PASS",
      "plan_id": "core-addition-author-gate-governance-f3b9e2",
      "freshness_ts": "2026-05-12T00:00:00Z",
      "changed_paths_covered": true
    },
    "negative_control_results_ref": {
      "path": "artifacts/ci/negative_control_results.json",
      "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "verdict": "PASS",
      "plan_id": "core-addition-author-gate-governance-f3b9e2",
      "freshness_ts": "2026-05-12T00:00:00Z",
      "changed_paths_covered": true
    },
    "plugin_proof_ref": {
      "path": "artifacts/ci/apps_foo_plugin_proof.json",
      "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "verdict": "PASS",
      "plan_id": "core-addition-author-gate-governance-f3b9e2",
      "freshness_ts": "2026-05-12T00:00:00Z",
      "changed_paths_covered": true
    },
    "boundary_scan_ref": {
      "path": "artifacts/ci/boundary_scan.json",
      "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "verdict": "PASS",
      "plan_id": "core-addition-author-gate-governance-f3b9e2",
      "freshness_ts": "2026-05-12T00:00:00Z",
      "changed_paths_covered": true
    },
    "contract_schema_scan_ref": {
      "path": "artifacts/ci/contract_schema_scan.json",
      "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "verdict": "PASS",
      "plan_id": "core-addition-author-gate-governance-f3b9e2",
      "freshness_ts": "2026-05-12T00:00:00Z",
      "changed_paths_covered": true
    }
  },
  "fail_closed_conditions": [
    "plan_type != platform_core_change → BLOCK",
    "no_app_literal_scan_ref missing → BLOCK",
    "decision.verdict != PASS → BLOCK"
  ],
  "signature": {
    "receipt_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
  }
}
```

---

## Boundary with Runtime Gates (§8 from prompt)

| Property | Core Addition Author-Gate (THIS) | 00C Runtime Gates |
|---|---|---|
| **When** | Author-time / static / pre-commit | Current-run / dynamic / per-request |
| **What** | Prevents unsafe core edits before runtime exists | Controls routing, caching, exit, UWG at execution time |
| **Emits GateVerdict?** | ❌ No | ✅ Yes |
| **Emits X3?** | ❌ No | ✅ Yes |
| **Writes L4?** | ❌ No | ❌ No — UWG/L4 write path only (UWG enforces; L4 is written only through the UWG contract, never by 00C Runtime Gates directly) |
| **Purpose** | Keeps core pristine | Governs live-request behavior |
| **Failure action** | Block git commit / cascade write | Reject/escalate/route request |
| **Audit surface** | Receipt JSON + git history | OTEL spans + ledger events |

---

## Acceptance Criteria

| # | Criterion | Verification command |
|---|---|---|
| AC-1 | `agentic_core` edit without `platform_core_change` fails | `pytest tests/governance/test_core_addition_negative_controls.py::test_core_edit_without_platform_plan_type_fails` |
| AC-2 | `agentic_core` edit without receipt fails | `pytest ...::test_core_edit_without_author_gate_receipt_fails` |
| AC-3 | Receipt missing required fields fails schema validation | `pytest tests/governance/test_core_addition_receipt_schema.py` |
| AC-4 | App literal in `agentic_core` fails | `pytest ...::test_core_literal_apps_rg_fails` (+ lic/research/qna variants) |
| AC-5 | `app_id` branch in `agentic_core` fails | `pytest ...::test_core_app_id_branch_fails` |
| AC-6 | App-specific route behavior in `agentic_core` fails | `pytest ...::test_core_app_specific_route_default_fails` |
| AC-7 | App-specific prompt behavior in `agentic_core` fails | `pytest ...::test_core_app_specific_prompt_behavior_fails` |
| AC-8 | App-specific graph semantics in `agentic_core` fails | `pytest ...::test_core_app_specific_graph_semantics_fails` |
| AC-9 | App-specific writeback behavior in `agentic_core` fails | `pytest ...::test_core_app_specific_writeback_behavior_fails` |
| AC-10 | Generic substrate change with valid receipt passes | `pytest ...::test_generic_plugin_mechanism_passes` |
| AC-11 | Future app can plug in using app-owned config only | `pytest ...::test_future_app_can_register_without_core_edit` |
| AC-12 | No runtime gate semantics confused with author-time | Boundary table in this plan (§"Boundary with Runtime Gates") |
| AC-13 | All tests pass | `pytest tests/governance/ tests/unit/windsurf_scripts/test_pre_write_gate_core_guard.py -v` |
| AC-14 | Evidence bundle contains receipt + scan + neg-ctrl + plugin proof | Inspect `artifacts/governance/core_addition_example_receipt.json` |
| AC-15 | `check_always_on_token_budget.py` still passes after W1.P1 | `python ops_scripts/ci/check_always_on_token_budget.py` |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Rule addition exceeds §33 always-on token budget | Medium | High — breaks existing hooks | Run `check_always_on_token_budget.py` immediately after W1.P1; trim if needed |
| Pre-write hook extension breaks existing checks | Low | High — blocks all writes | Extend, don't replace; add to pipeline last; regression tests required |
| Receipt requirement over-gates minor core bug fixes | Medium | Medium — developer friction | `CORE_ADDITION_GATE_BYPASS=1` env var + logged; trivial bug fix receipts can be minimal |
| 400+ existing plans lack new metadata fields | Low | Low — defaults to false | New fields default to `false`/`""` — no retroactive updates needed |
| Literal list incomplete for future apps_* | Medium | Medium — new apps bypass | Literal list is pattern-based (`apps_[a-z_]+`) not static enumeration |

---

## Rollback Plan

1. Revert `agentic-core-static.md` (add only, so revert the added section)
2. Revert `pre_write_gate.py` (remove `check_core_addition_receipt()` call)
3. Revert `execution-plan-template.md` (remove three new metadata fields)
4. Remove new files: schema, GOV-3 gate, negative-control tests, fixture
5. No database state to roll back — all enforcement is file-based
6. Bypass env var `CORE_ADDITION_GATE_BYPASS=1` immediately unblocks writes if needed

---

## Definition of Done

| # | Criterion | Type |
|---|---|---|
| DoD-1 | `pytest tests/governance/test_core_addition_negative_controls.py` — all 20 pass | Functional |
| DoD-2 | `python -c "import json; json.load(open('.windsurf/schemas/CoreAdditionAuthorGateReceipt.schema.json'))"` exits 0 | Smoke-run |
| DoD-3 | `pytest tests/unit/windsurf_scripts/test_pre_write_gate_core_guard.py` — all 27 pass | Tests |
| DoD-4 | `python ops_scripts/ci/check_agentic_core_addition.py` exits 0 (fail-closed mode, zero findings on clean repo) | CI gate |
| DoD-5 | `python ops_scripts/ci/check_always_on_token_budget.py` exits 0 after W1.P1 | Budget |
| DoD-6 | `artifacts/governance/core_addition_example_receipt.json` validates against schema | Evidence |
| DoD-7 | Existing `pytest tests/governance/` suite passes (no regressions) | Regression |

### Verification-vs-Deferral

| Item | Verify in this plan | Defer |
|---|---|---|
| Migration of existing 1,292 app-specific matches in core | ❌ | Existing `agentic-core-governance-remediation-c4e8a2` plan |
| HMAC signing of receipts | ❌ | Optional field in schema; enforce in separate plan if needed |
| Notion Plans DB row registration | ✅ (at W7 completion) | — |
| ADG hotspot enforcement for core changes | ❌ | Covered by separate ADG enforcement stack |

---

## GO / NO-GO Checklist

Before beginning W1 execution:

- [ ] ADG health green (`adg_health`)
- [ ] `check_always_on_token_budget.py` baseline run recorded
- [ ] `pytest tests/governance/test_agentic_core_static_boundary.py` passes (baseline)
- [ ] `pre_write_gate.py` regression suite passes (baseline)
- [ ] Author confirms design recommendation (static enforcement stack, NOT Cascade HITL Author-Gate) — **see §"Design Recommendation" above**

**GO** when all 5 checked. **NO-GO** if any fail.
