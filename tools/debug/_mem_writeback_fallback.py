"""One-shot memory writeback via direct SQLite (fallback for dead Memory MCP).

Plan `-d5e8b3` §Q5. Writes the `ProceduralPattern:EvalSpineShadowWiring`
entity + observations directly to `artifacts/memory/knowledge_graph.sqlite`
using the same shape the Memory MCP would persist.

Idempotent: re-runs overwrite nothing; duplicate observations are skipped.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

DB = pathlib.Path("artifacts/memory/knowledge_graph.sqlite")


def main() -> int:
    if not DB.exists():
        print(f"[mem-writeback] SQLite not found: {DB}", file=sys.stderr)
        return 2
    print(f"[mem-writeback] db={DB} size={DB.stat().st_size}")

    con = sqlite3.connect(str(DB))
    try:
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("[mem-writeback] tables:", tables)

        # Probe for the memory MCP schema shape.
        if "entities" not in tables:
            print(
                "[mem-writeback] 'entities' table missing; aborting fallback",
                file=sys.stderr,
            )
            return 3

        ent_cols = [r[1] for r in con.execute("PRAGMA table_info(entities)").fetchall()]
        obs_cols = (
            [r[1] for r in con.execute("PRAGMA table_info(observations)").fetchall()]
            if "observations" in tables
            else []
        )
        print("[mem-writeback] entity cols:", ent_cols)
        print("[mem-writeback] observation cols:", obs_cols)

        name = "ProceduralPattern:EvalSpineShadowWiring"
        etype = "ProceduralPattern"
        now = datetime.now(timezone.utc).isoformat()

        observations = [
            (
                "Observer-first wiring pattern for high-risk runtime integrations. "
                "Established 2026-04-23 via plan exit-eval-spine-shadow-wiring-a9c124 "
                "and Author-Gate (confidence 0.86, principle=observer-first-enforcer-later)."
            ),
            (
                "Technique: gate behavior change behind env var (EVAL_SPINE_SHADOW=1 for "
                "observer, EVAL_SPINE_ENFORCE=1 for upgrade-only enforcement). Hook at the "
                "seam where mature code returns a typed result (ExitControlGate.evaluate_sealed). "
                "Append call after return value is built; swallow every exception the observer "
                "can raise; never mutate return."
            ),
            (
                "Active enforcement pattern (plan -d5e8b3 §Q4): use upgrade-only semantics "
                "where eval_spine can make disposition stricter but never looser. "
                "Rank: ESCALATE(3) > DENY(2) > ALLOW/COMMIT(0). policy_halt forces ESCALATE."
            ),
            (
                "Judge backend plugin pattern (plan -d5e8b3 §Q3): DimScorer callable "
                "type alias serves as JudgeBackend. NullBackend returns Unknown; "
                "AnthropicBackend stub is env-gated and raises NotImplementedError when "
                "ANTHROPIC_API_KEY is set to prevent silent fake scoring."
            ),
            (
                "Guardian exemption justification pattern: shadow observers and enforcement "
                "bridges legitimately need broad exception catches because a live-path "
                "integration must never fail due to observer/bridge bugs. Mark with "
                "'guardian: allow-broad-shadow' or 'allow-broad-enforce' + specific reason."
            ),
            (
                "Writeback receipts (2026-04-23): Plans row=34c27693-f55c-81d7-9752-cbf01b5cffc2; "
                "ADR-036=34c27693-f55c-815a-8c03-f4acbeb88b23; "
                "ADR-039=34c27693-f55c-8187-8286-e8b8343d29db; "
                "ADR-042=34c27693-f55c-81df-8c9c-e7d6ff181417."
            ),
            (
                "Name collision pattern: when adding a new ADR number (038), first "
                "grep existing ADR-*.md files to avoid collisions. Repo has both "
                "ADR-038-budget-envelope.md and ADR-038-eval-trial-isolation.md; the "
                "exit-eval-spine work uses the budget-envelope file."
            ),
        ]

        # Resolve primary-key column name for entities.
        pk_col = "name" if "name" in ent_cols else ent_cols[0]

        # Upsert entity with full schema (snake_case, NOT NULL timestamps).
        con.execute(
            "INSERT OR IGNORE INTO entities "
            "(name, entity_type, created_at, updated_at, confidence, "
            "last_reinforced, access_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, etype, now, now, 1.0, now, 0),
        )

        # Insert observations — dedupe by content.
        if "observations" in tables and obs_cols:
            entity_ref_col = None
            for candidate in ("entityName", "entity_name", "entity"):
                if candidate in obs_cols:
                    entity_ref_col = candidate
                    break
            content_col = "content" if "content" in obs_cols else "observation"
            if entity_ref_col is None:
                print(
                    "[mem-writeback] observation entity-ref column unknown; cols=" + str(obs_cols),
                    file=sys.stderr,
                )
            else:
                existing = {
                    r[0]
                    for r in con.execute(
                        f"SELECT {content_col} FROM observations WHERE {entity_ref_col} = ?",
                        (name,),
                    ).fetchall()
                }
                new_count = 0
                for obs in observations:
                    if obs in existing:
                        continue
                    con.execute(
                        "INSERT INTO observations "
                        "(entity_name, content, created_at, confidence, "
                        "last_reinforced, access_count) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (name, obs, now, 1.0, now, 0),
                    )
                    new_count += 1
                print(f"[mem-writeback] wrote {new_count} new observations (existing={len(existing)})")
        con.commit()
        print(f"[mem-writeback] OK at {now}")
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
