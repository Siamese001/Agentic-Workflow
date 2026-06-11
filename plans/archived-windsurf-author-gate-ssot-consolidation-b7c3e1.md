---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-ssot-consolidation-b7c3e1.md'
original_relative_path: 'author-gate-ssot-consolidation-b7c3e1.md'
source_sha256: 158a2ad380c9506434e9a48360dabdc0657b9cdf63a3f264d88748feaa611ed9
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Author-Gate SSOT Consolidation

**Slug**: `author-gate-ssot-consolidation-b7c3e1`
**Status**: Completed
**Type**: Governance — single-source-of-truth consolidation
**Parent context**: 2026-05-03 RCA finding — Author-Gate enforcement vacuum on `ask_user_question`-only decisions; 8-source SSOT sprawl identified.

## Goal

Collapse the 8-source Author-Gate output sprawl into **one canonical schema file** that every consumer (skills, hooks, rules, audits) references. Close the enforcement vacuum identified in 2026-05-03 RCA where `ask_user_question` could fire without a valid `AUTHOR_GATE_PACKET:` and bypass all three audit layers.

## Scope

**In scope**
- New: `.windsurf/schemas/author_gate_packet.schema.json` (canonical SSOT, JSON Schema Draft 2020-12).
- Refactor: `.windsurf/skills/author-gate-packet-builder/{emit_packet.py,packet_template.md}`.
- Refactor: `.windsurf/skills/author-gate-ui-renderer/render_card.py`.
- Refactor: 3 audit hooks (`post_cascade_author_gate_{schema,ui,miss}_audit/_detector.py`).
- New hook: `post_cascade_ask_user_question_packet_audit.py` (closes vacuum).
- Trim: 3 rule files (`author-gate-enforcement.md`, `author-gate-decision-points.md`, `author-gate-svp-calibration.md`) — defer shape to schema; keep invariants-only.

**Out of scope**
- `author_gate_triggers.yaml` (trigger detection; orthogonal to packet shape).
- Runtime HITL gate (`agentic_core/L5_safety/`, ADR-023; different system).
- Refactor-decision-memory ledger schema (`refactor_decision_ledger.sqlite`); only the *consult* path is touched.
- Existing AUTHOR_GATE_PACKET historical data; back-compat alias `HITL_PACKET:` preserved.

## Non-Goals

- Forcing schema validation into `pre_author_gate.py` blocking path. Audit stays advisory + fail-open per current discipline.
- Replacing `ask_user_question`. The Cursor Agent-clickable envelope is generated FROM the schema; the tool stays unchanged.
- Token-budget rule trims that exceed the always-on budget gate (T7r). Trims are bounded by current budget headroom.

## Baseline (8-source sprawl)

```
1. .windsurf/rules/author-gate-enforcement.md          (when-to-fire, scoring)
2. .windsurf/rules/author-gate-decision-points.md      (categories, format)
3. .windsurf/rules/author-gate-svp-calibration.md      (SVP lens, R/Y/G)
4. .windsurf/skills/author-gate-packet-builder/packet_template.md   (shape prose)
5. .windsurf/skills/author-gate-packet-builder/emit_packet.py       (shape code)
6. .windsurf/skills/author-gate-ui-renderer/render_card.py          (UI code)
7. .windsurf/scripts/post_cascade_author_gate_schema_audit.py       (shape regex)
8. .windsurf/scripts/post_cascade_author_gate_ui_audit.py           (UI regex)
   + bug: post_cascade_author_gate_miss_detector.py treats raw ask_user_question
     as anti-signal regardless of packet presence (RCA 2026-05-03)
```

No JSON Schema file exists. Each consumer reinvents the shape.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | 1.1–1.3 | Land canonical schema + jsonschema lib pin | ~5k | jsonschema 4.26.0 already installed | ✅ DONE | Schema validates emit_packet output; 7/7 smoke tests pass |
| W2 | 2.1–2.2 | Refactor packet-builder skill to schema-first | ~6k | emit_packet.py uses shared loader | ✅ DONE | jsonschema-first validation; packet_template.md auto-generated (--check OK) |
| W3 | 3.1–3.3 | Refactor 3 existing audit hooks to share schema validator | ~7k | Hook JSONL contracts unchanged | ✅ DONE | schema_audit shares tools.author_gate.schema_loader; miss_detector contract clarified |
| W4 | 4.1–4.2 | Bug-fix miss_detector + new post_cascade_ask_user_question_packet_audit hook | ~4k | hooks.json schema-pure | ✅ DONE | New hook registered; severity=critical logged for high-density vacuum case (verified) |
| W5 | 5.1–5.3 | Trim 3 rule files to invariants-only; reference schema; verify always-on budget | ~5k | 3 author-gate rules are model_decision (not in always-on set) | ✅ DONE | All 3 rules cite canonical schema; always-on budget unchanged (570B pre-existing breach unrelated) |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| 1.1 | Author canonical schema | `.windsurf/schemas/author_gate_packet.schema.json` (new) | Field naming locked — once published, breaking changes are versioned bumps only | 2.5k | Todo |
| 1.2 | jsonschema lib pin + smoke test | `pyproject.toml` or `requirements.txt`, `tests/unit/windsurf_scripts/test_author_gate_schema_smoke.py` | Lib already present? Verify | 1.5k | Todo |
| 1.3 | Schema sample fixtures | `.windsurf/schemas/fixtures/author_gate_packet.{valid,invalid}.json` | Coverage of routing rules | 1k | Todo |
| 2.1 | emit_packet schema-first refactor | `emit_packet.py` | Drift between current code and new schema | 3k | Todo |
| 2.2 | Auto-generate packet_template.md | `tools/author_gate/render_template.py` (new), `packet_template.md` (regen) | Make template a build artifact, not source | 3k | Todo |
| 3.1 | Refactor schema_audit | `post_cascade_author_gate_schema_audit.py` | jsonschema vs current bespoke validator semantic parity | 2.5k | Todo |
| 3.2 | Refactor ui_audit | `post_cascade_author_gate_ui_audit.py` | UI prefix invariants stay in code (renderer-side) | 2k | Todo |
| 3.3 | Refactor miss_detector + bug fix | `post_cascade_author_gate_miss_detector.py` | `ask_user_question` anti-signal becomes conditional on packet presence | 2.5k | Todo |
| 4.1 | New ask_user_question packet audit | `.windsurf/scripts/post_cascade_ask_user_question_packet_audit.py` (new) + `hooks.json` entry | Avoid double-flagging with miss_detector | 2k | Todo |
| 4.2 | Wire severity ladder | hook log severity codes | Distinguish "decision-class missing packet" from "trivial question" | 2k | Todo |
| 5.1 | Trim author-gate-enforcement.md | rule file | Token budget gate (T7r) | 2k | Todo |
| 5.2 | Trim author-gate-decision-points.md | rule file | — | 1.5k | Todo |
| 5.3 | Trim author-gate-svp-calibration.md + verify CI | rule file + `ops_scripts/ci/check_always_on_token_budget.py` run | Calibration math stays | 1.5k | Todo |

## Waves — Detail

### W1 — Schema land

- **1.1**: Author `author_gate_packet.schema.json` per spec in plan parent-context (RCA-driven design). Required top-level: `version`, `trigger`, `decision`, `options[2..4]`, `routing`, `context`, `telemetry`. Each option requires `id`, `label` (≤80c), `description`, `confidence` (0..1), `pros[≥1]`, `cons[≥1]`, `recommended` (bool), optional `blast_radius`, `reason_codes`. `routing.rule_applied` enum constrains star-count invariant downstream.
- **1.2**: Confirm `jsonschema` Python lib in dependency manifest. If absent, add with version pin. Smoke test loads schema, validates a known-valid sample.
- **1.3**: Author 4 fixture files: 1 valid sample per `routing.rule_applied` value (`dominance_fires`, `filter_passes`, `tie_break`, `manual_override`) + 1 invalid (missing required field).

### W2 — Skill refactor

- **2.1**: `emit_packet.py` reads schema at startup; validates output before emit. Contract: any schema-violating packet raises `AuthorGatePacketError` (caught by skill harness, surfaced to Cursor Agent as recovery hint).
- **2.2**: `tools/author_gate/render_template.py` generates `packet_template.md` from schema (field names + types + constraints). CI gate `check_packet_template_generated.py` recomputes hash; fails if hand-edited.

### W3 — Audit hook refactor

- **3.1**: Replace bespoke regex in `post_cascade_author_gate_schema_audit.py` with `jsonschema.validate(packet, schema)`. JSONL output shape unchanged.
- **3.2**: `post_cascade_author_gate_ui_audit.py` reads schema for `routing.rule_applied` enum; validates `[confidence=0.NN]` prefix and ⭐ count via the existing render_card.py contract.
- **3.3**: `post_cascade_author_gate_miss_detector.py`: change `ask_user_question` from unconditional anti-signal to **conditional** anti-signal (suppresses miss flag ONLY when paired with valid packet in same response). Closes the prior-turn vacuum.

### W4 — New hook + vacuum closure

- **4.1**: `post_cascade_ask_user_question_packet_audit.py`. Detects `ask_user_question` calls; checks for paired `AUTHOR_GATE_PACKET:`; logs to `artifacts/windsurf/ask_user_question_packet_violations.jsonl`. Fail-open. Bypass: `ASK_PACKET_AUDIT_BYPASS=1`.
- **4.2**: Severity ladder per RCA proposal:
  - `ask_user_question` + valid packet → OK (no row).
  - `ask_user_question` + invalid packet → `severity=high`.
  - `ask_user_question` + no packet + decision-keyword density ≥ threshold → `severity=critical`.
  - `ask_user_question` + no packet + low density (e.g., "what filename?") → OK.

### W5 — Rule trim

- **5.1**: `author-gate-enforcement.md` trimmed to invariants-only: when-to-fire, score discipline (0.72 filter, 0.85+0.12 dominance), references schema for shape.
- **5.2**: `author-gate-decision-points.md` trimmed to category taxonomy + when-to-fire heuristics; references schema.
- **5.3**: `author-gate-svp-calibration.md` unchanged math; references schema for output shape only. Run `ops_scripts/ci/check_always_on_token_budget.py` to confirm budget is preserved/improved.

## Gap Register

1. **jsonschema lib version drift** — pin to specific version in manifest; CI gate flags major-version drift.
2. **Back-compat HITL_PACKET alias** — schema must accept both header markers; emit_packet emits AUTHOR_GATE_PACKET only; ingest readers accept both.
3. **packet_template.md hand-edits** — template becomes generated artifact; CI gate detects drift via hash file.
4. **Audit hook double-flagging** — when `ask_user_question` lacks packet, both miss_detector (after 3.3 fix) AND new ask_user_question_packet_audit fire. Mitigation: distinct violation codes; downstream rollup deduplicates by `cascade_id + packet_fingerprint`.
5. **Token budget regression** — rule trims target net-negative bytes; if any trim adds bytes, blocked by T7r gate.

## AG_QUEUE_SEED markers

```
AG_QUEUE_SEED: plan=author-gate-ssot-consolidation-b7c3e1 id=schema-version-policy depends_on= title=Schema versioning — semver vs dated breaking-bump
AG_QUEUE_SEED: plan=author-gate-ssot-consolidation-b7c3e1 id=template-generation-ownership depends_on=schema-version-policy title=packet_template.md generation — Cursor Agent-driven vs CI-driven regeneration
AG_QUEUE_SEED: plan=author-gate-ssot-consolidation-b7c3e1 id=miss-detector-vs-new-audit-overlap depends_on=template-generation-ownership title=Audit-hook overlap — keep both with distinct codes vs merge into one
AG_QUEUE_SEED: plan=author-gate-ssot-consolidation-b7c3e1 id=rule-trim-aggressiveness depends_on=miss-detector-vs-new-audit-overlap title=Rule trim aggressiveness — minimal-invariants vs aggressive-defer-to-schema
```

## ADG_HOTSPOT_REPORT

N/A — governance/SSOT consolidation, not code refactoring touching production agentic_core paths. All work lives in `.windsurf/schemas/`, `.windsurf/skills/author-gate-*/`, `.windsurf/scripts/post_cascade_author_gate_*.py`, `.windsurf/rules/author-gate-*.md`, and `tools/author_gate/` (new). Layer: L_TOOLS / L_OPS exclusively.

## ADG_GRAPH_LAYER_EVIDENCE

N/A — see above. No `agentic_core/` modules, no semantic edges, no production-layer hotspots involved.

## Success Criteria (whole-plan)

1. **One file** (`author_gate_packet.schema.json`) is the only authoritative shape; all 8 prior sources reference it.
2. **Zero regressions** — all current Author-Gate emissions in repo continue to validate against the new schema.
3. **Vacuum closed** — a new `ask_user_question` invocation without a valid packet logs `severity=critical` (verified via test fixture).
4. **Miss-detector bug fixed** — `ask_user_question` is conditional anti-signal (verified via test fixture matching the 2026-05-03 RCA scenario).
5. **packet_template.md is generated** — hand-edits blocked by CI gate.
6. **Always-on token budget preserved or improved** — `check_always_on_token_budget.py` green.
7. **No new always-on rules** — all behavioral guidance lives in skills (per Anthropic two-tier compliance, constitutional §33).

## AI Summary

- Target: Author-Gate output SSOT — collapse 8 sources to 1 JSON Schema file.
- Closes: 2026-05-03 RCA enforcement vacuum (`ask_user_question` without packet bypassed all 3 audit layers).
- New files: `.windsurf/schemas/author_gate_packet.schema.json`, `.windsurf/schemas/fixtures/author_gate_packet.*.json`, `tools/author_gate/render_template.py`, `.windsurf/scripts/post_cascade_ask_user_question_packet_audit.py`, `tests/unit/windsurf_scripts/test_author_gate_schema_smoke.py`.
- Refactors: `emit_packet.py`, `render_card.py`, `post_cascade_author_gate_{schema,ui,miss}_audit.py`, 3 rule files trimmed.
- Pattern source: jsonschema-as-SSOT (apps_e2e_proof_bundle.schema.json precedent), audit-hook trio (mcp_serialization, deferred_scope, plan_registration). 5 waves, ~27k tokens.
- Non-goals: trigger registry changes, runtime HITL changes, refactor-decision-memory ledger schema changes.
- Success: 1 schema file, 0 regressions, vacuum closed, miss-detector bug fixed, template generated, token budget preserved.

## References

- Constitutional §6 (Author-Gate scoring discipline)
- Constitutional §27 (Windsurf config schema purity)
- Constitutional §30 (Author-Gate capture health — `DECISION_CAPTURED:` markers)
- Constitutional §33 (two-tier compliance — always-on budget)
- 2026-05-03 RCA: `ask_user_question` enforcement vacuum (this plan parent)
- `.windsurf/rules/author-gate-enforcement.md` (current invariants)
- `.windsurf/rules/author-gate-decision-points.md` (current categories)
- `.windsurf/skills/author-gate-packet-builder/SKILL.md` (current packet builder)
- `.windsurf/skills/author-gate-ui-renderer/SKILL.md` (current UI renderer)
- `.windsurf/schemas/author_gate_triggers.yaml` (orthogonal trigger registry — out of scope)
