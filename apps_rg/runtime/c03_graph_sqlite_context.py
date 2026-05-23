"""C0.3 context assembly from SQLite-backed augmented skills graph.

Lane-local retrieval for section graph binding — not canonical spine C0.3 traverse.
Graph context is routing support only; claim proof remains fact/SRFS-bound.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    default_graph_sqlite_path,
    load_graph_metadata_row,
    materialize_augmented_skills_graph_sqlite,
    open_graph_sqlite,
)

PROOF_CLASSIFICATION = "graph_context_routing_support_not_claim_proof"

BRIDGE_EDGE_TYPES = frozenset(
    {"pillar_phase_bridge", "pillar_section_eligibility", "career_track_contains_pillar"}
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_sqlite(repo_root: Path, db_path: Path | None) -> Path:
    path = db_path or default_graph_sqlite_path(repo_root)
    if not path.is_file():
        materialize_augmented_skills_graph_sqlite(repo_root=repo_root, db_path=path)
    return path


def assemble_c03_graph_sqlite_context(
    *,
    role_family_key: str,
    section_id: str,
    selected_fact_ids: list[str] | None = None,
    repo_root: Path | None = None,
    db_path: Path | None = None,
    max_skills: int = 40,
    max_pillars: int = 20,
    pillar_hint_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Query SQLite graph for C0.3-style context bundle + inline receipt fields."""
    root = repo_root or _repo_root()
    path = _ensure_sqlite(root, db_path)
    facts_in = sorted({str(x).strip() for x in (selected_fact_ids or []) if str(x).strip()})
    sec = str(section_id or "").strip() or "executive_summary"
    rf = str(role_family_key or "").strip() or "SVP_ENGINEERING_AI_PLATFORM"

    conn = open_graph_sqlite(repo_root=root, db_path=path)
    try:
        meta = load_graph_metadata_row(conn)
        prof = conn.execute(
            """
            SELECT role_family_id, projection_role_family_key, track_weight_profile,
                   taxonomy_source, targeting_keywords, proof_policy_note
            FROM role_family_projection
            WHERE role_family_id = ? OR projection_role_family_key = ?
            LIMIT 1
            """,
            (rf, rf),
        ).fetchone()

        pillar_ids: list[str] = []
        fallback_pillar_bridge_used = False
        if prof:
            try:
                targeting = json.loads(prof[4] or "[]")
                for item in targeting:
                    if isinstance(item, dict) and item.get("pillar_id"):
                        pillar_ids.append(str(item["pillar_id"]))
                    elif isinstance(item, str):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                        pillar_ids.append(item)
            except json.JSONDecodeError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                pass

        if not pillar_ids and pillar_hint_ids:
            pillar_ids = [str(p).strip() for p in pillar_hint_ids if str(p).strip()][:max_pillars]
        if not pillar_ids:
            from apps_rg.runtime.c0.c03_role_family import resolve_c0_pillar_hints

            pillar_ids = list(resolve_c0_pillar_hints(rf, repo_root=root))[:max_pillars]
        if not pillar_ids:
            rows = conn.execute(
                """
                SELECT DISTINCT e.target_node_id
                FROM graph_edges e
                WHERE e.edge_type = 'career_track_contains_pillar'
                ORDER BY e.target_node_id
                LIMIT ?
                """,
                (max_pillars,),
            ).fetchall()
            pillar_ids = [r[0] for r in rows]
            fallback_pillar_bridge_used = True
        else:
            fallback_pillar_bridge_used = False

        pillar_args: tuple[Any, ...] = tuple(pillar_ids)
        if pillar_ids:
            placeholders = ",".join("?" * len(pillar_ids))
            selected_pillars = conn.execute(
                f"""
                SELECT node_id, label, support_level, activation_status, confidence, external_eligible
                FROM graph_nodes
                WHERE node_type = 'pillar' AND node_id IN ({placeholders})
                ORDER BY node_id
                LIMIT ?
                """,
                (*pillar_args, max_pillars),
            ).fetchall()
        else:
            selected_pillars = []

        skill_rows = conn.execute(
            """
            SELECT n.node_id, n.label, n.support_level, n.activation_status, n.confidence, n.external_eligible
            FROM graph_nodes n
            WHERE n.node_type = 'skill'
              AND (
                n.activation_status NOT IN ('DRAFT','INTERNAL_ONLY','DO_NOT_PROMOTE','BLOCKED')
                OR n.external_eligible = 1
              )
            ORDER BY n.external_eligible DESC, n.node_id
            LIMIT ?
            """,
            (max_skills,),
        ).fetchall()

        bridge_edges = conn.execute(
            f"""
            SELECT edge_id, source_node_id, target_node_id, edge_family, edge_type, weight, section_fit
            FROM graph_edges
            WHERE edge_type IN ({",".join("?" * len(BRIDGE_EDGE_TYPES))})
              AND (
                source_node_id IN ({",".join("?" * len(pillar_ids))})
                OR target_node_id LIKE 'section_%'
              )
            ORDER BY edge_type, edge_id
            LIMIT 120
            """,
            (
                *BRIDGE_EDGE_TYPES,
                *pillar_args,
            ),
        ).fetchall() if pillar_ids else conn.execute(
            f"""
            SELECT edge_id, source_node_id, target_node_id, edge_family, edge_type, weight, section_fit
            FROM graph_edges
            WHERE edge_type IN ({",".join("?" * len(BRIDGE_EDGE_TYPES))})
            ORDER BY edge_type, edge_id
            LIMIT 120
            """,
            tuple(BRIDGE_EDGE_TYPES),
        ).fetchall()

        section_elig = conn.execute(
            """
            SELECT node_id, section_id, allowed, claim_policy, reason, blocked_reason
            FROM section_eligibility
            WHERE section_id = ? OR section_id = '*'
            ORDER BY allowed DESC, node_id
            LIMIT 200
            """,
            (sec,),
        ).fetchall()

        if facts_in:
            ph = ",".join("?" * len(facts_in))
            fact_links = conn.execute(
                f"""
                SELECT skill_id, fact_id, support_level, claim_eligibility, external_eligible
                FROM skill_fact_links
                WHERE fact_id IN ({ph})
                ORDER BY claim_eligibility DESC, skill_id
                """,
                tuple(facts_in),
            ).fetchall()
        else:
            fact_links = conn.execute(
                """
                SELECT skill_id, fact_id, support_level, claim_eligibility, external_eligible
                FROM skill_fact_links
                WHERE claim_eligibility = 1
                ORDER BY skill_id
                LIMIT 80
                """
            ).fetchall()

        excluded_nodes = conn.execute(
            """
            SELECT node_id, node_type, activation_status, support_level, label
            FROM graph_nodes
            WHERE activation_status IN ('DRAFT','INTERNAL_ONLY','DO_NOT_PROMOTE','BLOCKED')
               OR (node_type = 'skill' AND external_eligible = 0 AND support_level IN (
                   'INTERNAL_ONLY','REPO_EVIDENCE_PORTFOLIO','TARGETING_ONLY','STYLE_ONLY','BLOCKED'))
            ORDER BY node_id
            LIMIT 60
            """
        ).fetchall()
    finally:
        conn.close()

    selected_nodes = [
        {
            "node_id": r[0],
            "node_type": "pillar",
            "label": r[1],
            "support_level": r[2],
            "activation_status": r[3],
            "confidence": r[4],
            "external_eligible": bool(r[5]),
        }
        for r in selected_pillars
    ] + [
        {
            "node_id": r[0],
            "node_type": "skill",
            "label": r[1],
            "support_level": r[2],
            "activation_status": r[3],
            "confidence": r[4],
            "external_eligible": bool(r[5]),
        }
        for r in skill_rows
    ]

    receipt = {
        "schema_version": "c03_graph_sqlite_context_receipt_v1",
        "generated_at_utc": _utc_now(),
        "sqlite_db_path": str(path),
        "graph_version": meta["graph_version"],
        "graph_hash": meta["ledger_hash"],
        "query_inputs": {
            "role_family_key": rf,
            "section_id": sec,
            "selected_fact_ids": facts_in,
            "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "sqlite_projection_row_found": prof is not None,
            "fallback_pillar_bridge_used": fallback_pillar_bridge_used,
        },
        "selected_nodes": selected_nodes,
        "selected_edges": [
            {
                "edge_id": r[0],
                "source_node_id": r[1],
                "target_node_id": r[2],
                "edge_family": r[3],
                "edge_type": r[4],
                "weight": r[5],
                "section_fit": r[6],
            }
            for r in bridge_edges
        ],
        "selected_fact_links": [
            {
                "skill_id": r[0],
                "fact_id": r[1],
                "support_level": r[2],
                "claim_eligibility": bool(r[3]),
                "external_eligible": bool(r[4]),
            }
            for r in fact_links
        ],
        "excluded_nodes": [
            {
                "node_id": r[0],
                "node_type": r[1],
                "activation_status": r[2],
                "support_level": r[3],
                "label": r[4],
            }
            for r in excluded_nodes
        ],
        "section_eligibility": [
            {
                "node_id": r[0],
                "section_id": r[1],
                "allowed": bool(r[2]),
                "claim_policy": r[3],
                "reason": r[4],
                "blocked_reason": r[5],
            }
            for r in section_elig
        ],
        "proof_classification": PROOF_CLASSIFICATION,
        "explicit_non_claims": [
            "sqlite_graph_rows_are_not_claim_proof",
            "jd_briefing_not_proof",
            "skills_not_proof_without_active_fact_binding",
            "broad_skills_ledger_non_authority",
        ],
        "broad_skills_ledger_status": "non_authority",
        "c03_integration_status": "SQLITE_CONTEXT_AVAILABLE",
    }
    return {
        "context": {
            "role_family_key": rf,
            "section_id": sec,
            "pillars": [n for n in selected_nodes if n["node_type"] == "pillar"],
            "skills": [n for n in selected_nodes if n["node_type"] == "skill"],
            "bridge_edges": receipt["selected_edges"],
            "fact_links": receipt["selected_fact_links"],
            "section_eligibility": receipt["section_eligibility"],
            "excluded_nodes": receipt["excluded_nodes"],
        },
        "receipt": receipt,
        "sqlite_db_path": str(path),
    }


def write_c03_graph_sqlite_context_receipt(
    bundle: dict[str, Any],
    *,
    repo_root: Path | None = None,
    run_id: str | None = None,
) -> Path:
    """Persist C0.3 SQLite context receipt under artifacts/apps_rg/runtime_proofs/."""
    root = repo_root or _repo_root()
    rid = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = root / "artifacts/apps_rg/runtime_proofs/c03_graph_sqlite_context"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"c03_graph_sqlite_context_{rid}.json"
    out_path.write_text(
        json.dumps(bundle.get("receipt") or bundle, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def enrich_c03_bound_with_sqlite_context(
    c03_doc: dict[str, Any],
    *,
    role_family_key: str = "SVP_ENGINEERING_AI_PLATFORM",
    section_id: str | None = None,
    selected_fact_ids: list[str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Attach SQLite context receipt to an existing section graph binding shim document."""
    sec = section_id or str(c03_doc.get("section_id") or "executive_summary")
    try:
        bundle = assemble_c03_graph_sqlite_context(
            role_family_key=role_family_key,
            section_id=sec,
            selected_fact_ids=list(selected_fact_ids or []),
            repo_root=repo_root,
        )
        receipt_path = write_c03_graph_sqlite_context_receipt(bundle, repo_root=repo_root)
        out = dict(c03_doc)
        out["c03_sqlite_attach_status"] = "ATTACHED"
        out["c03_sqlite_context_status"] = "ATTACHED"
        out["c03_sqlite_attach_reason"] = "sqlite_context_bound"
        out["c03_sqlite_db_path"] = bundle["sqlite_db_path"]
        out["c03_sqlite_graph_version"] = bundle["receipt"]["graph_version"]
        out["c03_sqlite_graph_hash"] = bundle["receipt"]["graph_hash"]
        out["c03_sqlite_context_receipt_path"] = str(
            receipt_path.relative_to(repo_root or _repo_root())
            if receipt_path.is_relative_to(repo_root or _repo_root())
            else receipt_path
        )
        out["c03_sqlite_proof_classification"] = PROOF_CLASSIFICATION
        out["c03_sqlite_context_summary"] = {
            "pillar_count": len(bundle["context"]["pillars"]),
            "skill_count": len(bundle["context"]["skills"]),
            "bridge_edge_count": len(bundle["context"]["bridge_edges"]),
            "fact_link_count": len(bundle["context"]["fact_links"]),
            "excluded_node_count": len(bundle["context"]["excluded_nodes"]),
        }
        return out
    except (OSError, ValueError, FileNotFoundError) as exc:
        out = dict(c03_doc)
        out["c03_sqlite_attach_status"] = "DEGRADED"
        out["c03_sqlite_context_status"] = "UNAVAILABLE"
        out["c03_sqlite_attach_reason"] = f"{type(exc).__name__}:{exc}"
        out["c03_sqlite_context_error"] = f"{type(exc).__name__}:{exc}"
        out["c03_sqlite_proof_classification"] = PROOF_CLASSIFICATION
        return out


__all__ = [
    "PROOF_CLASSIFICATION",
    "assemble_c03_graph_sqlite_context",
    "enrich_c03_bound_with_sqlite_context",
    "write_c03_graph_sqlite_context_receipt",
]
