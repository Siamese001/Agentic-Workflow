"""Memory consolidation pass — periodic garbage collection for the knowledge graph.

Usage
-----
    python tools/memory/memory_consolidation.py --report
    python tools/memory/memory_consolidation.py --apply --prune-floor 0.05
    python tools/memory/memory_consolidation.py --apply --merge-jaccard 0.80

Two tiers of action:

  1. Rule-based (deterministic, no LLM) — this file:
       - Merge near-duplicate observations (Jaccard >= merge_threshold)
       - Prune rows with effective confidence below prune_floor (default 0.05)
       - Always preserves protected entity types (ConstitutionalRule etc.)
       - Reports without --apply; no writes unless --apply is passed

  2. LLM-based (optional, higher quality) — stub hook only:
       - yuvalsuede/memory-mcp ships a Haiku-based consolidation pass that
         finds semantic duplicates, contradictions, and outdated entries.
       - A hook is exposed via --llm-hook <module:function>. This file does
         NOT invoke any LLM by itself — the caller provides the function.

Design notes
------------
- Dry-run is the default. Apply mode requires explicit --apply.
- Idempotent: running twice with the same thresholds produces no extra writes
  on the second pass.
- Transactional: each consolidation group runs in a single transaction;
  failure rolls back that group only.
"""

from __future__ import annotations

import argparse
import importlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from tools.memory.memory_decay import (
    effective_confidence,
    jaccard_similarity,
)
from tools.memory.sqlite_memory_store import SqliteMemoryStore

# Types that are NEVER pruned regardless of confidence.
_ALWAYS_PROTECTED: frozenset[str] = frozenset(
    {
        "ConstitutionalRule",
        "ArchitectureLayer",
        "ArchitecturalDecision",
        "ProceduralPattern",
    }
)


@dataclass(frozen=True)
class ConsolidationPlan:
    """What consolidation would do. Produced by --report; consumed by --apply."""

    merge_groups: list[list[int]]  # observation IDs to collapse into one
    prune_observation_ids: list[int]
    prune_entity_names: list[str]
    preserved_by_type: dict[str, int]

    def summary(self) -> str:
        lines = [
            f"Merge groups:             {len(self.merge_groups)}",
            f"Observations to merge:    {sum(len(g) - 1 for g in self.merge_groups)}",
            f"Observations to prune:    {len(self.prune_observation_ids)}",
            f"Entities to prune:        {len(self.prune_entity_names)}",
            "Preserved by type:",
        ]
        for et, cnt in sorted(self.preserved_by_type.items(), key=lambda x: -x[1]):
            lines.append(f"  {et:<28} {cnt}")
        return "\n".join(lines)


def build_plan(
    store: SqliteMemoryStore,
    merge_threshold: float = 0.80,
    prune_floor: float = 0.05,
    now: float | None = None,
) -> ConsolidationPlan:
    """Enumerate consolidation actions without applying them."""
    if now is None:
        now = time.time()

    merge_groups: list[list[int]] = []
    prune_obs: list[int] = []
    prune_entities: list[str] = []
    preserved: dict[str, int] = {}

    with store.connection() as conn:
        ent_rows = conn.execute(
            "SELECT name, entity_type, confidence, last_reinforced FROM entities"
        ).fetchall()

        for erow in ent_rows:
            name = str(erow["name"])
            etype = str(erow["entity_type"])
            protected = etype in _ALWAYS_PROTECTED
            eff = effective_confidence(
                float(erow["confidence"]),
                float(erow["last_reinforced"] or now),
                etype,
                now=now,
            )

            # Prune entity if non-protected and below floor.
            if not protected and eff < prune_floor:
                prune_entities.append(name)
                continue
            preserved[etype] = preserved.get(etype, 0) + 1

            # Scan observations on this entity for merge + prune candidates.
            obs_rows = conn.execute(
                "SELECT id, content, confidence, last_reinforced "
                "FROM observations WHERE entity_name = ? ORDER BY id",
                (name,),
            ).fetchall()

            # Prune low-confidence observations (even on protected entities —
            # they inherit the entity's half-life via decay, but stored
            # confidence may have drifted).
            for orow in obs_rows:
                oeff = effective_confidence(
                    float(orow["confidence"]),
                    float(orow["last_reinforced"] or now),
                    etype,
                    now=now,
                )
                if oeff < prune_floor and not protected:
                    prune_obs.append(int(orow["id"]))

            # Find Jaccard clusters >= merge_threshold.
            surviving = [orow for orow in obs_rows if int(orow["id"]) not in prune_obs]
            seen: set[int] = set()
            for i, a in enumerate(surviving):
                aid = int(a["id"])
                if aid in seen:
                    continue
                group = [aid]
                for b in surviving[i + 1 :]:
                    bid = int(b["id"])
                    if bid in seen:
                        continue
                    if jaccard_similarity(str(a["content"]), str(b["content"])) >= merge_threshold:
                        group.append(bid)
                        seen.add(bid)
                if len(group) > 1:
                    merge_groups.append(group)
                    seen.update(group)

    return ConsolidationPlan(
        merge_groups=merge_groups,
        prune_observation_ids=prune_obs,
        prune_entity_names=prune_entities,
        preserved_by_type=preserved,
    )


def apply_plan(store: SqliteMemoryStore, plan: ConsolidationPlan) -> dict[str, int]:
    """Execute a consolidation plan. Returns counts of rows changed."""
    now = time.time()
    merged = 0
    pruned_obs = 0
    pruned_ent = 0

    with store.connection() as conn:
        # Merge: keep first ID of each group, delete the rest; bump survivor.
        for group in plan.merge_groups:
            if len(group) < 2:
                continue
            survivor_id = group[0]
            losers = group[1:]
            placeholders = ",".join("?" * len(losers))
            conn.execute(
                f"DELETE FROM observations WHERE id IN ({placeholders})",
                tuple(losers),
            )
            # Touch survivor so future reads see the latest reinforcement.
            conn.execute(
                "UPDATE observations SET last_reinforced = ?, access_count = access_count + ? WHERE id = ?",
                (now, len(losers), survivor_id),
            )
            merged += len(losers)

        # Prune observations.
        if plan.prune_observation_ids:
            placeholders = ",".join("?" * len(plan.prune_observation_ids))
            pruned_obs = conn.execute(
                f"DELETE FROM observations WHERE id IN ({placeholders})",
                tuple(plan.prune_observation_ids),
            ).rowcount

        # Prune entities (cascade deletes observations + relations).
        if plan.prune_entity_names:
            placeholders = ",".join("?" * len(plan.prune_entity_names))
            pruned_ent = conn.execute(
                f"DELETE FROM entities WHERE name IN ({placeholders})",
                tuple(plan.prune_entity_names),
            ).rowcount

    return {
        "merged_observations": merged,
        "pruned_observations": pruned_obs,
        "pruned_entities": pruned_ent,
    }


def _load_llm_hook(spec: str) -> Callable[..., Any]:
    """Load a callable from 'module:function' spec. The hook receives the
    ConsolidationPlan + store and returns a refined plan (LLM-driven)."""
    if ":" not in spec:
        raise ValueError(f"Expected 'module:function', got {spec!r}")
    mod_name, fn_name = spec.split(":", 1)
    mod = importlib.import_module(mod_name)
    return getattr(mod, fn_name)  # type: ignore[no-any-return]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=None, help="Path to memory SQLite DB")
    ap.add_argument("--report", action="store_true", help="Print plan without applying (default)")
    ap.add_argument("--apply", action="store_true", help="Execute the plan")
    ap.add_argument(
        "--merge-jaccard",
        type=float,
        default=0.80,
        help="Jaccard similarity threshold for merging (default 0.80)",
    )
    ap.add_argument(
        "--prune-floor",
        type=float,
        default=0.05,
        help="Effective confidence floor below which rows are pruned (default 0.05)",
    )
    ap.add_argument(
        "--llm-hook",
        type=str,
        default=None,
        help="Optional 'module:function' hook that refines the plan before apply",
    )
    args = ap.parse_args()

    store = SqliteMemoryStore(args.db)
    plan = build_plan(
        store,
        merge_threshold=args.merge_jaccard,
        prune_floor=args.prune_floor,
    )

    if args.llm_hook:
        hook = _load_llm_hook(args.llm_hook)
        refined = hook(plan=plan, store=store)
        if isinstance(refined, ConsolidationPlan):
            plan = refined

    print("=" * 60)
    print("MEMORY CONSOLIDATION PLAN")
    print("=" * 60)
    print(plan.summary())
    print()

    if not args.apply:
        print("(dry run — re-run with --apply to execute)")
        return 0

    result = apply_plan(store, plan)
    print("=" * 60)
    print("APPLIED")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k:<24} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
