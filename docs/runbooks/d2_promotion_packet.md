# D2 Semantic Cache — Promotion Packet
# Prompt 18 output
# Next rollout band: single non-production worker → full non-production fleet

> This packet is operator-ready once soak gate (PG-18) and anomaly gate (PG-18 per note)
> are both PASS. No code changes are required for widening. Promotion is env-flag only.

---

## 1. Evidence bundle — collect before promoting

Operators must gather all of the following before executing the promote command.

| # | Evidence item | How to collect | Required state |
|---|--------------|----------------|----------------|
| E-1 | PG-17 canary smoke test (ST-1 through ST-5) | Run §3 of main runbook | All 5 PASS |
| E-2 | 24 h soak: worker ran continuously | Process log timestamps | T=0 to T+24h uptime confirmed |
| E-3 | PG-18 anomaly gate: alert not firing at T+180 min+ | Prometheus alert state | `SemanticCacheMissRateAnomaly` = inactive |
| E-4 | Hit rate ≥ 40 % at T+24h | PromQL Panel 1 | `100 * rate(hit[5m]) / rate(total[5m])` ≥ 40 |
| E-5 | Zero ERROR lines in semantic_cache path | Worker log grep | `grep ERROR <log> \| grep semantic_cache` → no lines |
| E-6 | PG-19 rollback drill evidence present | `docs/runbooks/d2_rollback_drill_evidence.md` | File exists, status PASS |
| E-7 | Store not empty | `SELECT COUNT(*) FROM l2_cache` | > 0 rows |
| E-8 | All 19 PG gates in main runbook | Visual review | All PASS or marked Manual PASS |

Collect these into a promotion approval comment/ticket before executing the promote command.

---

## 2. Exact promote command (next band)

"Next band" = all remaining non-production workers. Do not use this for production.

```bash
# For each additional non-production worker, set in its environment manifest:
SEMANTIC_CACHE_D2_ENABLED=1
HIVE_MIND_STRICT_MODE=false
EMBEDDING_MODEL_ID=bge-m3-v1

# Then restart the workers in a rolling fashion (one at a time):
# Restart worker N → verify Gate A log → wait 5 min → restart worker N+1
```

If workers are managed by a process manager (systemd, supervisor, etc.):

```bash
# Example for systemd — update the environment file and reload:
echo "SEMANTIC_CACHE_D2_ENABLED=1" >> /etc/agentic_worker.env
echo "HIVE_MIND_STRICT_MODE=false" >> /etc/agentic_worker.env
echo "EMBEDDING_MODEL_ID=bge-m3-v1" >> /etc/agentic_worker.env
systemctl restart agentic-worker@*
```

**Do not set `SEMANTIC_CACHE_D2_ENABLED=1` in production** until all 19 PG gates are PASS
and an explicit production promotion decision is made.

---

## 3. First-15-minute watchlist (after each worker restart)

| Time | Check | Command | Pass condition |
|------|-------|---------|----------------|
| T=0 | Gate A log | `grep "Native L2 cache" <log>` | `Connected to Long-Term Memory` |
| T=1 | Metrics sidecar alive | `curl -s http://localhost:8000/metrics | grep semantic_cache_events` | Lines returned |
| T=2 | No immediate ERROR | `grep ERROR <log> | grep semantic_cache` | No lines |
| T=5 | Traffic visible | `60 * sum(rate(agentic_workflow_l4_semantic_cache_events_total[5m]))` | > 0 events/min |
| T=5 | `SemanticCacheNoTraffic` not firing | Prometheus | Alert inactive |
| T=10 | Miss rate reasonable | PromQL miss rate | < 100% (at least some queries re-using cache) |
| T=15 | No `SemanticCacheEvictionSpike` | Prometheus | Alert inactive |
| T=15 | Worker process healthy | `ps aux | grep apps_*` or healthcheck | Process running |

If any check fails within 15 min: execute rollback for that worker immediately (§4a of main runbook).
Do not proceed to the next worker until the current one passes all 15-min checks.

---

## 4. Rollback triggers (post-promotion)

Trigger immediate rollback (`§4a` of `d2_semantic_cache_production_rollout.md`) on ANY of:

| Trigger | Signal | Urgency |
|---------|--------|---------|
| `SemanticCacheMissRateAnomaly` firing at T+180 min+ | Prometheus alert | < 5 min |
| Any `ERROR semantic_cache_manager` log line | Worker log | Immediate |
| `SemanticCacheEvictionSpike` at > 50/min | Prometheus alert | < 5 min |
| Tenant isolation breach (AT-2 failure) | Canary smoke test | Immediate + store wipe |
| Worker OOM or repeated crash with D2 in traceback | Process monitor | < 5 min |
| Hit rate drops to < 5% and stays there for > 30 min after T+240 min | PromQL Panel 1 | Investigate then rollback if no fix |

**Rollback time target: < 5 minutes from trigger to fail-closed state.**
See `docs/runbooks/d2_rollback_drill_evidence.md` for the verified procedure.

---

## 5. Production promotion (future — not yet authorized)

Once all non-production workers are running cleanly for ≥ 48 h, the production band requires:

```bash
# In production environment manifest ONLY — not in code:
SEMANTIC_CACHE_D2_ENABLED=1

# Recommended: 1 production worker (canary) → 24 h soak → full rollout
# Monitor SemanticCacheMissRateAnomaly for 24 h before widening to all workers
```

**This step requires a separate promotion decision.** Do not execute until production
readiness review is complete and the evidence bundle above is re-collected for production.
