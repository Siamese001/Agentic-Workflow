# L0 Routing Calibration Harness (W0)

Plan: `.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md`

Threshold-sweep harness for the five L0 routing paths:

| Path | Signal | Default semantics |
|---|---|---|
| `R1A` | `freshness_ratio` | HIGH score = reuse |
| `R1B` | `cosine_similarity` | HIGH score = reuse |
| `R3`  | `grounding_need_prediction` | HIGH score = ground |
| `R5`  | `aggregate_confidence` | LOW score = abstain (`invert_score=true`) |
| `C0`  | `evidence_coverage` | HIGH score = proceed to Prompt Assembly |

## Usage

```bash
# Sweep one fixture
python -m tools.calibration --fixture tests/calibration/fixtures/r1b_semantic_cache.json

# Sweep every fixture and write JSON reports
python -m tools.calibration --all

# Restrict to one namespace (R1B / R3 fixtures carry namespaces)
python -m tools.calibration --fixture tests/calibration/fixtures/r1b_semantic_cache.json --namespace rg
```

Reports go to `docs/reports/calibration/<fixture-stem>_sweep.json` by default.

## What the harness emits

For each fixture + namespace, `SweepReport` carries:

- Full PR curve (`points[]`): precision, recall, F1, confusion counts per threshold.
- Four optimal thresholds under different objectives:
  - `optimal_max_f1` — highest F1 across the sweep.
  - `optimal_precision_first` — highest recall subject to `precision >= 0.90`.
  - `optimal_recall_first` — highest precision subject to `recall >= 0.80`.
  - `vertex_default` — first threshold at or above Vertex's 0.7 default.

## Wave dependencies

- **W0.P1** (DONE): fixtures under `tests/calibration/fixtures/`.
- **W0.P2** (DONE): this harness.
- **W1.P2** (DEFERRED): grounding-need classifier; output drives R3 fixture.
- **W2.P1** (DEFERRED): thresholds emitted by this harness → `config/routing_thresholds.yaml`.
- **W3** (DEFERRED): wire calibrated thresholds into `route_gates.check_d2_semantic_cache`
  and `plan_abstain`.

## Vendor references

- **Vertex AI** dynamic retrieval — default threshold **0.7**, tune on representative set.
- **OpenAI Prompt Caching 201** — `cached_tokens` hit-ratio target **>= 40%**.
- **Industry consensus** (VentureBeat / arXiv 2411.05276 / TrueFoundry / Azure APIM):
  precision-critical threshold **0.94–0.98**, recall-optimized **0.85–0.90**.
- **Anthropic** *Building Effective Agents* — routing requires accurate classification;
  heuristic or LLM classifier both acceptable.

See plan §Part 1 for full citations.
