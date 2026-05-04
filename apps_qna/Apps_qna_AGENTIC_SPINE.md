# apps_qna Agentic Spine

> Build-time compiler spine for interview Q&A card-pack generation.
> This is a **deterministic template-render flow** — no runtime LLM calls, no C0 retrieval.
> The spine produces sealed card packs that are pasted into ChatGPT (external runtime).

```
USER (CLI: python -m apps_qna --interview <slug> ...)
 |
 v
U0 -> L1 (Interview Ingest + Route Selection) -> L0 (ValidatedRequest Envelope)
                                                  |
                                                  +-- R1A Exact Cache?
                                                  |    (same Interview hash)
                                                  |      |
                                                  |      hit ─► [RET] -> Exit (idempotent)
                                                  |
                                                  +-- R1B Semantic Cache?
                                                  |    (similar interview params)
                                                  |      |
                                                  |      hit ─► [RET] -> Exit (warn: stale)
                                                  |
                                                  +-- R5 Pre-route Fallback?
                                                  |    (emergency bypass)
                                                  |      |
                                                  |      yes ─► [RET] -> Exit (degraded)
                                                  |
                                                  v
                                         R3_BUILD_TIME_COMPILE
                                         (build_time_compiler route)
                                                  |
                                                  v
                                         Hop 1 Intake + Schema Validate
                                         • Interview YAML parse
                                         • RouteRegistry load
                                         • Jinja2 env init (StrictUndefined)
                                                  |
                                                  +-- SCHEMA_INVALID / MISSING_FIELD
                                                  |       |
                                                  |       v
                                                  |   sealed BuilderError packet
                                                  |       |
                                                  |       v
                                                  |   Exit -> X3 SAFE_ABSTAIN (fix inputs)
                                                  |
                                                  v
                                         Hop 2 Template Render (deterministic)
                                         • _render_all() 18 cards
                                         • Panel-mode expansion (03A, 03B...)
                                         • StrictUndefined catch
                                                  |
                                                  +-- TEMPLATE_ERROR / UNDEFINED_VAR
                                                  |       |
                                                  |       v
                                                  |   sealed BuilderError packet
                                                  |       |
                                                  |       v
                                                  |   Exit -> X3 SAFE_ABSTAIN (fix templates)
                                                  |
                                                  v
                                         Hop 3 Pack Assembly + UWG Write
                                         • ensure_pack_dir() [UWG-routed]
                                         • write_card_text() per card
                                         • Paste optimization (always_on > primary > specialist)
                                                  |
                                                  +-- UWG_REJECT / DISK_FULL / PERMISSION_DENIED
                                                  |       |
                                                  |       v
                                                  |   sealed UWGFailure packet
                                                  |       |
                                                  |       v
                                                  |   Exit -> X3 REROUTE (retry) / ESCALATE_HITL
                                                  |
                                                  v
                                         Hop 4 Manifest + FEC Seal
                                         • _build_manifest() → CardPackManifest
                                         • write_pack_manifest_json() [UWG-routed]
                                         • emit_pack_lifecycle_event() [ledger]
                                         • resolve_fec() → final_evidence_contract
                                                  |
                                                  v
                                         Exit -> X3 ALLOW_FINISH
                                         (pack sealed at reports/qna/<slug>/)
```

## Spine Characteristics

| Property | Value |
|----------|-------|
| **Route Type** | `build_time_compiler` (see `spine_manifest.yaml`) |
| **Execution Form** | `SINGLE_STEP` (deterministic, no async/resume) |
| **L3 DAG Path** | `BYPASSED` (no orchestration graph) |
| **C0 Grounding** | `False` (templates are static, not RAG-backed) |
| **Prompt Assembly** | `True` (deterministic Jinja2 template render) |
| **Runtime Authority** | `none` (downstream_authority=none; ChatGPT is runtime) |

## Cache Strategy (R1A/R1B)

| Cache Type | Key | Hit Behavior |
|------------|-----|--------------|
| **R1A Exact** | SHA256(Interview JSON) | Return cached pack path; idempotent rebuild skip |
| **R1B Semantic** | (company, role, interviewers[0].name) | Return with staleness warning; user decides |
| **R5 Fallback** | `emergency_bypass` flag | Skip to degraded single-card pack |

## Exit Disposition Mapping

| Failure Mode | Hop | X3 Disposition | User Action |
|--------------|-----|----------------|-------------|
| YAML parse fail | Hop 1 | `SAFE_ABSTAIN` | Fix Interview YAML |
| Missing required field | Hop 1 | `SAFE_ABSTAIN` | Populate Interview field |
| Template UndefinedError | Hop 2 | `SAFE_ABSTAIN` | Add var to extra_context |
| UWG write rejection | Hop 3 | `REROUTE` | Retry (--force if exists) |
| Disk full / IO error | Hop 3 | `ESCALATE_HITL` | Check disk space |
| Template not found | Hop 2 | `SAFE_FALLBACK` | Check template_dir |

## Ledger Emissions

| Event Kind | Emitter | Payload |
|------------|---------|---------|
| `validated_request_emit` | `spine_handoff.py` | request_id, interview_slug, schema_verdict |
| `pack_build` | `card_pack_builder.py` | cards_rendered, routes_covered, paste_exceeds_limit |
| `pack_lint` | `router/pack_loader.py` | lint violations, route_manifest compliance |

## FEC (Final Evidence Contract)

```yaml
# Produced by apps_qna/cert/fec_producer.py → resolve_fec()
producer: apps_qna
grounded: false                    # No C0 retrieval in this app
retrieval_sources: []              # Template-driven, not RAG
route_id: apps_qna.pack_build_single_step_v1
template_ids:
  - intake
  - validate_routes
  - assemble_prompt
  - render_cards
  - seal
evidence_sufficiency: template    # Deterministic template render
schema_version: "1.0"
```

## File Outputs (Sealed Artifacts)

```
reports/qna/<interview-slug>/
├── 00_RUNTIME_ROOT.md
├── 01_ROUTING_MANIFEST.md
├── ... (18 cards total)
├── 22_LEARNINGS.md
└── pack_manifest.json            # UWG-sealed manifest
```

## Cross-App Integration Points

| Source App | Artifact Consumed | Cards Populated |
|------------|-------------------|-----------------|
| `apps_research` | Research brief + Source register | CompanyBackground, IndustryTrends, Glossary |
| `apps_rg` | Resume + STAR proofs | ExperiencePoint[], StoryBank (card 14) |
| `apps_exec` | Executive brief | ExecutiveFit framing (card 13) |

## Non-Goals (This Spine Does NOT)

- ❌ Invoke LLM at build time (templates only)
- ❌ Runtime answer generation (ChatGPT does this)
- ❌ C0 retrieval / RAG (static templates)
- ❌ Multi-step async execution (single-step deterministic)
- ❌ L3 orchestration DAG (bypassed — no graph)
- ❌ UWG commit authorization (pack writes are pre-authorized local FS)

## See Also

- `spine_manifest.yaml` — Canonical route-type declaration
- `integrations/spine_handoff.py` — ValidatedRequest wrapper
- `builder/card_pack_builder.py` — Hop 2-4 implementation
- `cert/fec_producer.py` — FEC contract producer
- `__main__.py` — Entrypoint (product mode + live cert mode)
