# Apps_* Eval Harness — Residual Deferred Scope

**Slug:** `apps-eval-harness-residual-a2d9c7`
**Created:** 2026-05-03
**Status:** Completed
**Last Updated:** 2026-05-03
**Completion Note:** All 6 waves executed in one session. 312 tests pass in `tests/_apps_contract/` (+57 net). `check_app_domain_harness_parity` gate: ERROR=0, WARN=0 across all 8 apps.
**Parent plans:**
- `.windsurf/plans/apps-eval-harness-parity-f8d4a2.md` (Completed)
- `.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md` (Completed)

**Owner:** Cascade

## 1. Problem Statement

Parent plan + first continuation closed 9 of 10 audit BLOCKERs, leaving **three residual axes** that were explicitly deferred to separate plans:

1. **BLOCKER #4** — C0 FEC producer binding for 5 grounded apps (`apps_qna`, `apps_research`, `apps_rfp`, `apps_exec`, `apps_underwriting_ai`). Schema wired; producers missing.
2. **Real LLM-judge scoring** — 4 judges currently stubbed with `IS_STUB=True` sentinels. No Spearman ≥ 0.80 calibration infrastructure.
3. **Production observability / SSOT** — Holdout-vs-dev fixture separation, production-log mining, legacy YAML deprecation audit.

This plan picks up the residual work as **minimum-viable producer/registry skeletons + deprecation audit**. Real LLM scoring against human-labeled holdouts remains deferred (no holdout corpus yet) and is gated by W2.P1 of this plan.

## 2. Goals

- Land an **FEC producer registry** (`apps_shared/cert/fec_producer.py`) so each grounded app can register a producer when its retrieval path is ready. No-op default keeps current fail-open behavior.
- Create `apps_eval/fixtures/{dev,holdout}/` directory structure with a release-gate-only README contract protecting `holdout/`.
- Skeleton `ops_scripts/calibration/production_log_miner.py` with PII-redaction hook.
- Skeleton `ops_scripts/maintenance/legacy_yaml_audit.py` enumerating `*_policies.yaml` / `*_thresholds.yaml` migration candidates.
- Judge promotion registry (`apps_shared/judge_registry.py`) tracking stub → real transition state so CI can alarm when a judge flips.
- All new modules shape-tested; parity CI gate remains green.

## 3. Non-Goals

- Per-app retrieval refactor to actually route through C0 (multi-session; owns its own plan per grounded app).
- Real LLM judge scoring logic (needs holdout corpus from W2 + budget for model calls).
- Fixture corpus authoring (operators supply real human-labeled fixtures later).
- Legacy YAML actual deletion (audit surfaces candidates; deletion owns its own Author-Gate).

## 4. Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1–W1.P2 | FEC producer registry + no-op default | ~5k | `ExitReviewPacket.final_evidence_contract` field already exists | ✅ Done | Registry module + 9 tests green |
| W2 | W2.P1–W2.P2 | `apps_eval/fixtures/{dev,holdout}/` scaffold + release-gate contract | ~3k | No existing fixtures to migrate | ✅ Done | Directories + README + package markers; 6 tests green |
| W3 | W3.P1 | Production-log mining skeleton | ~4k | PII redaction stub acceptable | ✅ Done | CLI + PII-redactor gate; 5 tests green |
| W4 | W4.P1 | Legacy YAML deprecation audit | ~3k | Read-only audit; no deletion | ✅ Done | Scanner + JSON report; 4 tests green |
| W5 | W5.P1 | Judge promotion registry | ~3k | Tracks stub vs real state | ✅ Done | Registry module + 4 tests green |
| W6 | W6.P1 | Verification — full suite + parity gate | ~2k | All prior waves green | ✅ Done | 312 tests pass; gate ERROR=0 WARN=0 |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | FEC producer registry skeleton | `apps_shared/cert/fec_producer.py` (new) | Must be importable + thread-safe | 3k | ✅ Done |
| W1.P2 | Tests for FEC producer registry | `tests/_apps_contract/test_w1_fec_producer_registry.py` (new) | Cover register/resolve/noop paths | 2k | ✅ Done |
| W2.P1 | `apps_eval/fixtures/{dev,holdout}/` scaffold | New dirs + README + `__init__.py` | Holdout isolation contract text | 2k | ✅ Done |
| W2.P2 | Test — fixture structure present | `tests/_apps_contract/test_w2_fixtures_scaffold.py` (new) | Asserts dirs + README exist | 1k | ✅ Done |
| W3.P1 | Production-log miner skeleton | `ops_scripts/calibration/production_log_miner.py` (new) | PII hook; JSONL writer | 4k | ✅ Done |
| W4.P1 | Legacy YAML audit | `ops_scripts/maintenance/legacy_yaml_audit.py` (new) | Pattern-match `*_policies.yaml`/`*_thresholds.yaml` | 3k | ✅ Done |
| W5.P1 | Judge promotion registry | `apps_shared/judge_registry.py` (new) + test | Stub vs real sentinel detection | 3k | ✅ Done |
| W6.P1 | Full-suite verification | Run pytest + parity gate | Zero regressions | 2k | ✅ Done |

## 6. Governance & Cross-References

- Constitutional §22 (ADG graph-layer primary)
- Constitutional §24 (deferred-scope capture — this plan IS the pickup)
- Constitutional §25 (MCP serialization — Notion writes deferred to plan-end)
- Constitutional §31 (SSOT folder routing — all new scripts in canonical folders)
- Constitutional §32 (Fort Knox certification discipline — W6 fence unchanged)

## 7. Author-Gate Decision Points

None anticipated — all pre-decided by parent plans' AG packets. Residual work is mechanical scaffolding.

## 8. Risks

| Risk | Mitigation |
|---|---|
| FEC producer registry misused to widen app authority | Registry is READ-ONLY; no write path; only ExitReviewPacket.final_evidence_contract consumers read it |
| Production-log miner leaks PII | Skeleton ships with PII-redaction HOOK; operator wires real redactor before CI promotion |
| Legacy YAML audit deletes config | Read-only; emits migration-candidate JSON, never deletes |
| Judge promotion registry confused with real impls | IS_STUB sentinel preserved; registry explicitly distinguishes stub/real |

## 9. Metadata

- Plan file path: `.windsurf/plans/apps-eval-harness-residual-a2d9c7.md`
- Notion Plans row: create on W6 completion with Status=Completed
- Template: `.windsurf/templates/execution-plan-template.md`

## AG_QUEUE_SEED

None — mechanical work; no Author-Gate class decisions anticipated.
