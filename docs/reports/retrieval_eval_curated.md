# Retrieval Quality Benchmark — curated_agent_docs vs arch_docs vs ext_knowledge

**Queries**: 40 · **K**: 5 · **Elapsed**: 16.0s

## 1. Collection-Level Metrics (mean over all 40 queries)

| Metric                |          arch_docs |      ext_knowledge |   curated_agent_docs |
|-----------------------|--------------------|--------------------|----------------------|
| P@K (dist<0.5)        |            0.985 ✓ |              0.485 |                0.640 |
| MRR (dist<0.35)       |              0.175 |              0.100 |              0.250 ✓ |
| Mean dist@1           |            0.395 ✓ |              0.467 |                0.421 |
| Mean dist@K           |            0.421 ✓ |              0.483 |                0.461 |
| Canonical hit rate    |              0.045 |              0.000 |              1.000 ✓ |
| Mean authority        |              0.682 |              0.471 |              0.867 ✓ |
| Arch depth            |            0.995 ✓ |              0.000 |                0.495 |
| BP relevance          |              0.000 |              0.000 |              1.000 ✓ |
| Answer support        |            0.645 ✓ |              0.440 |                0.545 |
| Redundancy rate       |            0.090 ✓ |              0.150 |                0.345 |
| Source diversity      |              1.400 |              1.000 |              2.425 ✓ |
| Tooling contam.       |            0.000 ✓ |              0.035 |                0.000 |

## 2. Per-Category Win Rate

| Category     | arch_docs wins | ext_knowledge wins | curated_agent_docs wins |
|--------------|---------------|-------------------|-----------------------|
| architecture |           2/5 |               0/5 |                     3/5 |
| history      |           0/5 |               0/5 |                     5/5 |
| layer        |           0/5 |               0/5 |                     5/5 |
| multiagent   |           0/5 |               0/5 |                     5/5 |
| policy       |           2/5 |               0/5 |                     3/5 |
| retrieval    |           0/5 |               0/5 |                     5/5 |
| standards    |           0/5 |               0/5 |                     5/5 |
| tooling      |           1/5 |               0/5 |                     4/5 |

## 3. Query-by-Query Win/Loss Summary

| QID       | Category     | Winner               | arch dist@1 | ext dist@1 | curated dist@1 | Notes |
|-----------|--------------|----------------------|-------------|------------|----------------|-------|
| ARCH-01   | architecture | curated_agent_docs   |       0.370 |      0.428 |          0.353 |  |
| ARCH-02   | architecture | arch_docs            |       0.324 |      0.526 |          0.502 |  |
| ARCH-03   | architecture | curated_agent_docs   |       0.451 |      0.501 |          0.497 |  |
| ARCH-04   | architecture | arch_docs            |       0.406 |      0.482 |          0.458 |  |
| ARCH-05   | architecture | curated_agent_docs   |       0.365 |      0.505 |          0.326 | high redundancy |
| HIST-01   | history      | curated_agent_docs   |       0.338 |      0.604 |          0.344 | high redundancy |
| HIST-02   | history      | curated_agent_docs   |       0.327 |      0.494 |          0.277 | high redundancy |
| HIST-03   | history      | curated_agent_docs   |       0.426 |      0.551 |          0.449 | high redundancy |
| HIST-04   | history      | curated_agent_docs   |       0.392 |      0.487 |          0.438 |  |
| HIST-05   | history      | curated_agent_docs   |       0.449 |      0.527 |          0.406 |  |
| LAYER-01  | layer        | curated_agent_docs   |       0.352 |      0.471 |          0.434 |  |
| LAYER-02  | layer        | curated_agent_docs   |       0.366 |      0.527 |          0.436 |  |
| LAYER-03  | layer        | curated_agent_docs   |       0.404 |      0.569 |          0.545 |  |
| LAYER-04  | layer        | curated_agent_docs   |       0.424 |      0.515 |          0.422 |  |
| LAYER-05  | layer        | curated_agent_docs   |       0.354 |      0.531 |          0.457 |  |
| MA-01     | multiagent   | curated_agent_docs   |       0.411 |      0.335 |          0.311 | high redundancy |
| MA-02     | multiagent   | curated_agent_docs   |       0.459 |      0.321 |          0.334 | high redundancy |
| MA-03     | multiagent   | curated_agent_docs   |       0.431 |      0.384 |          0.342 |  |
| MA-04     | multiagent   | curated_agent_docs   |       0.437 |      0.286 |          0.275 | high redundancy |
| MA-05     | multiagent   | curated_agent_docs   |       0.414 |      0.354 |          0.337 | high redundancy |
| POLICY-01 | policy       | arch_docs            |       0.360 |      0.574 |          0.511 |  |
| POLICY-02 | policy       | curated_agent_docs   |       0.329 |      0.436 |          0.454 |  |
| POLICY-03 | policy       | curated_agent_docs   |       0.456 |      0.537 |          0.505 |  |
| POLICY-04 | policy       | arch_docs            |       0.396 |      0.518 |          0.488 |  |
| POLICY-05 | policy       | curated_agent_docs   |       0.452 |      0.585 |          0.490 |  |
| RETR-01   | retrieval    | curated_agent_docs   |       0.372 |      0.306 |          0.459 | high redundancy |
| RETR-02   | retrieval    | curated_agent_docs   |       0.385 |      0.358 |          0.363 | high redundancy |
| RETR-03   | retrieval    | curated_agent_docs   |       0.439 |      0.441 |          0.493 |  |
| RETR-04   | retrieval    | curated_agent_docs   |       0.384 |      0.419 |          0.477 |  |
| RETR-05   | retrieval    | curated_agent_docs   |       0.454 |      0.523 |          0.492 |  |
| STD-01    | standards    | curated_agent_docs   |       0.451 |      0.463 |          0.488 |  |
| STD-02    | standards    | curated_agent_docs   |       0.415 |      0.466 |          0.463 |  |
| STD-03    | standards    | curated_agent_docs   |       0.460 |      0.556 |          0.382 | high redundancy |
| STD-04    | standards    | curated_agent_docs   |       0.378 |      0.357 |          0.322 | high redundancy |
| STD-05    | standards    | curated_agent_docs   |       0.451 |      0.404 |          0.367 |  |
| TOOL-01   | tooling      | arch_docs            |       0.308 |      0.517 |          0.501 | high redundancy |
| TOOL-02   | tooling      | curated_agent_docs   |       0.332 |      0.487 |          0.382 | high redundancy |
| TOOL-03   | tooling      | curated_agent_docs   |       0.289 |      0.504 |          0.344 |  |
| TOOL-04   | tooling      | curated_agent_docs   |       0.376 |      0.397 |          0.467 |  |
| TOOL-05   | tooling      | curated_agent_docs   |       0.420 |      0.418 |          0.465 |  |

## 4. Worst 10 Queries for curated_agent_docs (RCA)

| Rank | QID       | Category     | win_score | dist@1 | P@K   | Canonical | Auth  | RCA |
|------|-----------|--------------|-----------|--------|-------|-----------|-------|-----|
|    1 | TOOL-01   | tooling      |     0.583 |  0.501 | 0.000 |     1.000 | 0.720 | high duplicate rate — insufficient diversity |
|    2 | ARCH-04   | architecture |     0.602 |  0.458 | 0.200 |     1.000 | 0.870 | text matches but lacks query-specific content |
|    3 | RETR-03   | retrieval    |     0.629 |  0.493 | 0.200 |     1.000 | 0.820 | text matches but lacks query-specific content |
|    4 | ARCH-02   | architecture |     0.640 |  0.502 | 0.000 |     1.000 | 0.900 | text matches but lacks query-specific content |
|    5 | LAYER-03  | layer        |     0.640 |  0.545 | 0.000 |     1.000 | 0.880 | text matches but lacks query-specific content |
|    6 | POLICY-04 | policy       |     0.640 |  0.488 | 0.200 |     1.000 | 0.890 | text matches but lacks query-specific content |
|    7 | ARCH-03   | architecture |     0.651 |  0.497 | 0.200 |     1.000 | 0.840 | competitive — marginal loss |
|    8 | TOOL-04   | tooling      |     0.669 |  0.467 | 0.200 |     1.000 | 0.860 | text matches but lacks query-specific content |
|    9 | TOOL-05   | tooling      |     0.670 |  0.465 | 0.400 |     1.000 | 0.800 | competitive — marginal loss |
|   10 | LAYER-05  | layer        |     0.681 |  0.457 | 0.600 |     1.000 | 0.800 | text matches but lacks query-specific content |

## 5. Win Rate Summary by Query Group

| Group                  | arch_docs | ext_knowledge | curated_agent_docs |
|------------------------|-----------|---------------|--------------------|
| Architecture/Policy/History | 4/20 (20%) |     0/20 (0%) |        16/20 (80%) |
| Best-practice/Standards/MA | 0/15 (0%) |     0/15 (0%) |       15/15 (100%) |
| Tooling/MCP queries    | 1/5 (20%) |      0/5 (0%) |          4/5 (80%) |
| All queries            | 5/40 (12%) |     0/40 (0%) |        35/40 (87%) |
