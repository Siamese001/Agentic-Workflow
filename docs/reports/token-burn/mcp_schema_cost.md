# MCP Schema Cost Audit

**Generated:** 2026-05-02T22:03:13.796324+00:00
**Servers measured:** 10 of 10
**Total schema bytes (measured):** 74,963
**Approx total schema tokens:** 18,740 (bytes/4)
**Total tools registered:** 111

> Every always-on session pays this token cost regardless of use.
> Retirement candidates: high-cost low-frequency MCPs.

## Ranked by Schema Bytes

| Rank | Server | Tools | Schema Bytes | Approx Tokens |
|-----:|--------|------:|-------------:|--------------:|
| 1 | `io.windsurf/mcp-playwright` | 23 | 17,002 | 4,250 |
| 2 | `filesystem` | 14 | 12,227 | 3,056 |
| 3 | `task_manager` | 4 | 10,099 | 2,524 |
| 4 | `memory` | 15 | 8,589 | 2,147 |
| 5 | `adg_sqlite` | 18 | 8,419 | 2,104 |
| 6 | `context7` | 2 | 5,093 | 1,273 |
| 7 | `vector_db` | 10 | 4,365 | 1,091 |
| 8 | `redis` | 10 | 3,757 | 939 |
| 9 | `pytest_mcp` | 6 | 2,810 | 702 |
| 10 | `otel_mcp` | 9 | 2,602 | 650 |

## Notes

- Source: `tools/diagnostics/mcp_schema_cost.py`
- Machine-readable: `artifacts/windsurf/mcp_schema_cost.json`
- Plan reference: `.windsurf/plans/windsurf-token-burn-augmentation-b7a3f1.md` W2/P6
- Approximation: tokens = bytes/4 (Claude tokenizer ratio 3-5x)
