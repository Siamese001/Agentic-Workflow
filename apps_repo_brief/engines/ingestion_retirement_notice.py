"""
P3.3 — IngestionEngine Retirement Notice.

apps_exec.engines.IngestionEngine performed live filesystem scans of
source directories at request time. This is a pre-C0 work violation:
the canonical spine must not perform retrieval or ingestion before C0.

RETIREMENT DECISION (W3):
- Live-scan ingestion is RETIRED from the canonical spine.
- The retrieval surface is now ``repo_brief_docs`` — a durable L4
  surface seeded by the UWG (UnifiedWriteGateway) from approved sources.
- C0 performs retrieval FROM this surface using its 7-lane retrieval plan;
  it does NOT perform live directory scans.
- No runtime code in apps_repo_brief calls this class.

UWG SEEDER PATH (future — W4/W5):
  apps_repo_brief/integrations/repo_brief_uwg_seeder.py
  → UWG.commit(surface_id="repo_brief_docs", sources=[...])

APPS_EXEC SHIM COMPATIBILITY:
  apps_exec.engines.ingestion_engine is retained until W5 shim sunset.
  No hard import of apps_exec.engines.ingestion_engine in apps_repo_brief.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.3
"""

_RETIREMENT_REASON = (
    "IngestionEngine live-scan retired in W3. "
    "Use repo_brief_docs L4 surface via C0 retrieval lanes. "
    "See apps_repo_brief/engines/ingestion_retirement_notice.py §UWG SEEDER PATH."
)


def ingestion_engine_retired() -> None:
    """Raise if called — hard guard against accidental use."""
    raise RuntimeError(
        f"[apps_repo_brief] {_RETIREMENT_REASON}"
    )
