"""apps_research real-runtime driver.

Imports ``apps_research.engines.research_assembly_engine``, builds
source manifest, credibility scores, citation support map,
contradiction register, and research report from the fixture.
"""

from __future__ import annotations

from apps_shared.proof.runtime_drivers._driver_base import (
    import_real_engine,
    write_artifact,
    write_markdown,
)


class AppsResearchDriver:
    app_id = "apps_research"

    def invoke(self, ctx) -> dict[str, str]:
        fixture = dict(ctx.spec.extra_payload or {})

        engine_ok, engine_detail = import_real_engine(
            "apps_research.engines.research_assembly_engine"
        )

        sources = fixture.get("approved_sources", [])
        claims = fixture.get("claims", [])
        contradictions = fixture.get("potential_contradictions", [])

        source_manifest = {
            "research_id": fixture.get("research_id"),
            "topic": fixture.get("topic"),
            "approved_count": len(sources),
            "sources": sources,
        }
        credibility_scores = {
            s["source_id"]: {
                "credibility_score": s.get("credibility_score", 0.0),
                "publisher": s.get("publisher"),
                "year": s.get("year"),
            }
            for s in sources
        }

        # Citation support map: claim -> resolves to which sources
        citation_support_map = []
        for claim in claims:
            supporting = claim.get("supporting_source_ids", [])
            citation_support_map.append({
                "claim_id": claim["claim_id"],
                "claim_text": claim["text"],
                "supporting_source_ids": supporting,
                "support_score": claim.get("support_score", 0.0),
                "anchored": all(
                    sid in credibility_scores for sid in supporting
                ) and bool(supporting),
            })

        # Contradiction register
        contradiction_register = {
            "total": len(contradictions),
            "entries": contradictions,
        }

        outputs: dict[str, str] = {}
        k, p = write_artifact(ctx, rel_filename="source_manifest.json", payload=source_manifest, kind="SourceManifest")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="source_credibility_scores.json", payload=credibility_scores, kind="SourceCredibilityScores")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="citation_support_map.json", payload=citation_support_map, kind="CitationSupportMap")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="contradiction_register.json", payload=contradiction_register, kind="ContradictionRegister")
        outputs[k] = p

        # Research report markdown
        body_lines = [
            "# Research Report — " + str(fixture.get("topic", "Topic")),
            "",
            f"- Research ID: `{fixture.get('research_id')}`",
            f"- Sources: {len(sources)} approved",
            f"- Engine import: {'OK' if engine_ok else f'FAIL ({engine_detail})'}",
            "",
            "## Approved sources",
            "",
        ]
        for s in sources:
            body_lines.append(
                f"- **{s['source_id']}** — {s.get('title', 'Untitled')} "
                f"({s.get('publisher')}, {s.get('year')}) "
                f"credibility={s.get('credibility_score', 0.0):.2f}"
            )
        body_lines.append("")
        body_lines.append("## Claims with citations")
        body_lines.append("")
        for c in citation_support_map:
            anchor = "anchored" if c["anchored"] else "UNANCHORED"
            body_lines.append(
                f"- **{c['claim_id']}** [{anchor}]: {c['claim_text']} → "
                f"sources={c['supporting_source_ids']} "
                f"support={c['support_score']:.2f}"
            )
        if contradictions:
            body_lines.append("")
            body_lines.append("## Surfaced contradictions")
            for con in contradictions:
                body_lines.append(
                    f"- **{con['contradiction_id']}** ({con['topic']}): "
                    f"{con['left_source_id']} says \"{con['left_position']}\" vs "
                    f"{con['right_source_id']} says \"{con['right_position']}\""
                )
        rel = write_markdown(ctx, rel_filename="research_report.md", body="\n".join(body_lines))
        outputs["ResearchReport"] = rel

        # Engine ok report
        k, p = write_artifact(
            ctx,
            rel_filename="research_engine_invocation.json",
            payload={"engine_ok": engine_ok, "engine_detail": engine_detail},
            kind="ResearchEngineInvocation",
        )
        outputs[k] = p
        return outputs
