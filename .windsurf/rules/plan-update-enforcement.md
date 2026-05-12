---
trigger: always_on
---

> See `.windsurf/RULES_INDEX.md#always-on-discipline` for shared retrieval / enforcement guidance.

# Plan Update Enforcement — Scope Expansion Authorization

## Core Principle

> **Documentation ≠ Authorization.** A plan update filed after work completes is retroactive permission, not governance.

Plans are living documents **with explicit authorization gates**. Scope discovered during execution MUST pass through a four-step authorization protocol before execution continues. This prevents "plan update" from becoming an excuse for uncontrolled scope drift.

## Scope Expansion Authorization Protocol

### The Four-Step Discipline (mandatory)

```
Step 1: DISCOVERED_SCOPE marker   — Document what was found (before any new work)
Step 2: AUTHORIZATION_DECISION     — Explicit verdict: ACCEPTED / DEFERRED / SPLIT_TO_NEW_PLAN / REJECTED
Step 3: Plan file updates          — If ACCEPTED: update all tables (see Required Updates below)
Step 4: SCOPE_EXPANSION marker     — Execution proceeds only after Step 3 complete
```

**Critical invariant**: No new work (file writes, edits, tests) on discovered scope until AUTHORIZATION_DECISION is emitted AND (if ACCEPTED) plan file updates are complete.

### Step 1 — DISCOVERED_SCOPE Marker Grammar

Emitted immediately when new scope is identified, **before any work begins**:

```
DISCOVERED_SCOPE: plan=<slug-6hex> wave=<N> phase=<M> gap="<description>" impact="<severity>"
```

Examples:
```
DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12 cache invalidation race in L2 receipts" impact="High — corrupts provenance chain"
DISCOVERED_SCOPE: plan=bar-def456 wave=2 phase=3 gap="Missing DoD smoke-run row for executable surface" impact="Medium — plan could pass without working code"
```

### Step 2 — AUTHORIZATION_DECISION Marker Grammar

Emitted in the **same response** as DISCOVERED_SCOPE, after assessment:

```
AUTHORIZATION_DECISION: plan=<slug-6hex> decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<justification>"
```

Decision semantics:

| Decision | When to use | Plan Update Required | Execution Continues? |
|---|---|---|---|
| **ACCEPTED** | Scope is critical path, in-charter, and absorbable | Yes — complete all Required Updates | Yes, on expanded scope |
| **DEFERRED** | Scope is valid but time/volume gated (e.g., "needs 30d maturity") | No — emit `DEFERRED_SCOPE:` marker | Yes, on original scope only |
| **SPLIT_TO_NEW_PLAN** | Scope is valid but too large for current plan | No — create new plan, link to this one | Yes, on original scope only |
| **REJECTED** | Scope is gold-plating, off-charter, or low priority | No | Yes, on original scope only |

Examples:
```
AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical path blocker — G24 hardening depends on this gap fix"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=DEFERRED authorized_by=author_gate decisive_reason="30-day time-gated; needs production log volume for calibration"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=SPLIT_TO_NEW_PLAN authorized_by=user decisive_reason="Scope too large — creates plan apps-rg-g22-diagnostics-d9f4a2"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=REJECTED authorized_by=user decisive_reason="Gold-plating; G22 diagnostics not required for v1 release"
```

### Step 3 — Required Updates (if ACCEPTED)

Must complete ALL before emitting SCOPE_EXPANSION marker:

- [ ] **Refresh `last_updated`** — current date in frontmatter
- [ ] **Add/modify Wave Structure row** — new wave if needed, or modify existing
- [ ] **Add/modify Phase-Level Summary row** — new phase(s) with 🔲 TODO status
- [ ] **Add/modify Gap Register row** — document the discovered gap
- [ ] **Add/modify DoD criterion** — if new deliverables required
- [ ] **Append to Scope Expansion Authorization Log** — inline documentation

### Step 4 — SCOPE_EXPANSION Marker Grammar

Emitted only after all Required Updates complete:

```
SCOPE_EXPANSION: plan=<slug-6hex> reason="<summary>" added="<waves/phases/gaps>" authorized="yes"
```

The `authorized="yes"` attribute confirms Step 2 was ACCEPTED and Step 3 is complete.

Examples:
```
SCOPE_EXPANSION: plan=foo-abc123 reason="W3 revealed G22 diagnostics gap requiring new phases" added="W5.P8 (G22 diagnostics), W5.P9 (G28 receipt ordering), GAP-12" authorized="yes"
```

Captured by `post_cascade_scope_drift_detector.py` → `artifacts/windsurf/scope_expansion.jsonl`.

## last_updated Discipline

The `last_updated` field in plan frontmatter MUST be refreshed whenever:
- Any table content changes (wave status, phase status, gap register, DoD)
- Scope expansion occurs (new waves/phases added)
- Runtime evidence section is updated with new run data

**Frontmatter format:**
```yaml
---
plan_id: my-plan-abc123
authored_at: 2026-05-01
last_updated: 2026-05-12  # <-- MUST match update date
status: In Progress
---
```

## Phase-Level Summary Updates

The Phase-Level Summary table has status cells that MUST be kept in sync:

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Original phase | `file.py` | PP-1 | ~600 | ✅ DONE |
| W2.P2 | New phase added | `new_file.py` | PP-2 | ~400 | 🔲 TODO |

Status transitions:
- 🔲 TODO → 🔄 IN PROGRESS when wave starts
- 🔄 IN PROGRESS → ✅ DONE when phase completes

The `post_cascade_wave_lifecycle_capture.py` hook auto-updates these cells when `PHASE_COMPLETE:` markers are present.

## Detection & Enforcement

### Fail-Closed Layers

| Layer | Component | Advisory Mode | Strict Mode |
|---|---|---|---|
| Post-cascade | `post_cascade_plan_scope_audit.py` | Warn when ≥3 files edited without preceding AUTHORIZATION_DECISION | **Block** (exit 2) — unauthorized scope drift |
| Post-cascade | `post_cascade_scope_drift_detector.py` | Capture all markers to JSONL | Flag missing authorized="yes" attribute |
| CI gate | `check_plan_freshness.py` | Flag plans with `last_updated` >7 days + Status active | Fail build on unauthorized expansions |
| Pre-write | `pre_write_plan_scope_gate.py` | — | Block writes outside authorized scope |

**Strict mode activation:** Set `PLAN_SCOPE_AUDIT_STRICT=1` (default: advisory)

### What Triggers Unauthorized Drift Detection

The hook detects unauthorized drift when:
1. ≥3 file operations (edit/write) detected in response
2. Active plan exists (modified within 24h)
3. **NO** preceding `AUTHORIZATION_DECISION` marker in same response
4. **OR** `AUTHORIZATION_DECISION` present but decision is DEFERRED/REJECTED/SPLIT_TO_NEW_PLAN and work proceeded anyway

### Negative-Control: Retroactive Authorization Detection

The hook specifically detects and blocks the anti-pattern where **work occurs first, then markers are added afterward**:

| Scenario | Advisory Mode | Strict Mode |
|---|---|---|
| `edit()` calls found in response text, then `DISCOVERED_SCOPE:` marker appears | `RETROACTIVE_AUTHORIZATION_DETECTED` warning | Exit 2, block response |
| `AUTHORIZATION_DECISION` marker timestamp appears after file write timestamps | `RETROACTIVE_AUTHORIZATION_DETECTED` warning | Exit 2, block response |

**Why this matters**: This is the exact failure mode the authorization protocol prevents. Without this negative-control, "update the plan" becomes a post-hoc rationalization after gold-plating. The `RETROACTIVE_AUTHORIZATION_DETECTED` error code specifically identifies this bypass attempt.

### Marker Recency Check

Authorization is valid only within `AUTH_MARKER_RECENCY_SEC` window (default: 300 seconds / 5 minutes). Work on discovered scope after this window requires fresh authorization.

## Bypass (Emergency Only)

- `SCOPE_AUTHORIZATION_BYPASS=1` — override all authorization checks (logged)
- `PLAN_SCOPE_AUDIT_BYPASS=1` — skip post-cascade hook entirely
- `PLAN_SCOPE_AUDIT_STRICT=0` — force advisory mode only
- `PLAN_FRESHNESS_BYPASS=1` — skip CI gate staleness check
- `AUTH_MARKER_RECENCY_SEC=<seconds>` — adjust authorization window (default: 300)

## Failure Precedents

**2026-05-12: `apps-rg-exit-gate-fix-g24-hardening-d7c4b1`** — Plan originally had 4 waves. W3 execution revealed G22 diagnostics and G28 receipt ordering gaps. Plan was correctly expanded to 6 waves with W5.P8, W5.P9, W6.P10. This pattern is the reference implementation of this rule.

## Related

- `.windsurf/rules/plan-location.md` — SSOT location, format requirements
- `.windsurf/rules/scope-containment.md` — scope discipline (§18)
- `.windsurf/rules/deferred-scope-capture.md` — `DEFERRED_SCOPE:` markers
