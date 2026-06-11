---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\heal-flag-standardization-460a9b.md'
original_relative_path: 'heal-flag-standardization-460a9b.md'
source_sha256: b71d2eda6a3f226a2cdbd3631bc5f7bc4d500501a99a0dab2728777f233583f8
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Healing Flag Standardization — `--heal` as Single Toggle

Introduce one canonical `--heal` flag that propagates uniformly to every agent in `execute_ssot.py`, replacing the current scatter of `dry_run`, `auto_approve`, `enable_llm`, and per-agent mutation guards that each agent independently interprets.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Problem: What's Scattered Today

| Variable | Where set | Default | Problem |
|---|---|---|---|
| `dry_run` | `_legacy_main` L3162, propagated manually | `False` | Passed positionally through 5 phase calls; Phase 3 arch validation **defaults to `True`** (L1901/1906) — never heals |
| `auto_approve` | `_legacy_main` L3163 | `not args.interactive` | Separate from `dry_run`; agents receive both independently |
| `enable_llm` | `_legacy_main` L3173 | `not dry_run` | Derived from `dry_run` but set separately in decision engine |
| `enable_cda` | `_legacy_main` L3176 | `True` | Third independent toggle into decision engine |
| `heal_repository(dry_run=...)` | Phase 1 L1767, Phase 2 L1885, Phase 2.5 L3451 | Passed through | Any missed call site = silent no-heal |
| `execute_phase3_architectural_validation(dry_run=True)` | L1901, L1906 | **Hardcoded `True`** | This phase never heals even when `dry_run=False` |
| `file_classifier.dry_run = True` | L1802 | Hardcoded | FileClassificationAgent always forced dry-run during discovery |
| `agent.heal_repository(dry_run=True)` | L3130 (direct agent mode) | Hardcoded | Direct `--agent` invocations always dry-run |

**Root cause:** `dry_run` is threaded as a positional argument through 8+ function boundaries. Any site that hardcodes or defaults differently silently breaks healing. No single enforced SSOT.

---

## Solution: `HealContext` dataclass + `--heal` flag

### Step 1 — Add `--heal` to `execute_ssot_entrypoint.py`

Explicit opt-in replaces the implicit "healing happens unless `--dry-run`" logic:

```
--heal       Enable active healing (mutations applied)
--dry-run    Scan/report only, no mutations (default if --heal omitted)
--validate   Forces scan-only (existing, unchanged)
```

### Step 2 — Introduce `HealContext` dataclass in `execute_ssot.py`

```python
@dataclass(frozen=True)
class HealContext:
    heal: bool          # True = mutations active
    auto_approve: bool  # True = no interactive prompts
    enable_llm: bool    # True = LLM arbitration
    enable_cda: bool    # True = CognitiveDispositionAgent
```

Constructed **once** in `_legacy_main`. All phase functions receive `ctx: HealContext` instead of `dry_run + auto_approve` as separate args.

### Step 3 — Fix all phase function signatures

| Function | Current params | Change |
|---|---|---|
| `execute_phase1_discovery` | `dry_run, auto_approve` | `ctx: HealContext` |
| `execute_phase1_discovery_impl` | `dry_run, auto_approve` | `ctx: HealContext` |
| `execute_phase2_reconciliation` | `dry_run` | `ctx: HealContext` |
| `execute_phase2_alignment` | `dry_run, auto_approve` | `ctx: HealContext` |
| `execute_phase2_alignment_impl` | `dry_run, auto_approve` | `ctx: HealContext` |
| `execute_phase3_architectural_validation` | `dry_run=True` **← bug** | `ctx: HealContext` |
| `execute_phase3_validation_impl` | `dry_run=True` **← bug** | `ctx: HealContext` |
| `execute_phase4_healing` | `dry_run, auto_approve` | `ctx: HealContext` |
| `execute_phase4_healing_impl` | `dry_run, auto_approve` | `ctx: HealContext` |

All internal `if dry_run:` → `if not ctx.heal:` and `heal_repository(dry_run=dry_run)` → `heal_repository(dry_run=not ctx.heal)`.

### Step 4 — Fix the 3 hardcoded `dry_run=True` bugs

- **L1901/1906** `execute_phase3_architectural_validation(dry_run=True)` → use `ctx`
- **L1802** `file_classifier.dry_run = True` → `file_classifier.dry_run = not ctx.heal`
- **L3130** `agent.heal_repository(dry_run=True)` → `dry_run=not ctx.heal`

### Step 5 — `_legacy_main` constructs `HealContext` once

```python
ctx = HealContext(
    heal=not args.dry_run,
    auto_approve=not args.interactive,
    enable_llm=not args.dry_run,
    enable_cda=not getattr(args, "no_cda", False),
)
```

All 8 call sites (L3370-3484) that currently pass `dry_run, auto_approve` replaced with `ctx`.

### Step 6 — Update runner `_run_ssot_healing.py`

```python
cmd = [sys.executable, "-m",
       "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
       "--heal", "-v"]
```

---

## Files in Scope (3 files)

| File | Lines changed (est.) |
|---|---|
| `agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py` | ~10 (add `--heal`) |
| `agentic_core/L0_routing/scripts/execute_ssot.py` | ~50 (HealContext + 9 signatures + 3 bug fixes) |
| `tools/evidence/_run_ssot_healing.py` | ~2 (add `--heal` to cmd) |

---

## Invocation Before / After

```bash
# Before (implicit, fragile — healing on by default but Phase 3 arch always dry-run)
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint -v

# After (explicit and consistent — all phases obey one flag)
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal     # full healing
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint            # scan/report only (safe default)
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --validate # scan/report only (existing alias)
```

---

## Risk Assessment

- **Low** — `HealContext` is additive; `--dry-run` kept as alias for backward compat
- **Medium** — Phase 3 arch validation bug fix will cause that phase to actually mutate for the first time; recommend verifying on `--territory prompt_governance` first
- **None** — runner, entrypoint, and decision engine all stay in sync through single `ctx` object

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

