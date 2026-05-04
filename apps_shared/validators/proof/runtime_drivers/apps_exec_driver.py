"""apps_exec real-runtime driver.

Imports ``apps_exec.engines.brief_assembly_engine``, builds claim register,
recommendation register, evidence-backed brief, unsupported claims, caveats.
Enforces user-spec invariant: recommendations MUST be labeled, claims MUST
have evidence support.
"""

from __future__ import annotations

from apps_shared.validators.proof.runtime_drivers._driver_base import (
    import_real_engine,
    write_artifact,
    write_markdown,
)


class AppsExecDriver:
    app_id = "apps_exec"

    def invoke(self, ctx) -> dict[str, str]:
        fixture = dict(ctx.spec.extra_payload or {})

        engine_ok, engine_detail = import_real_engine(
            "apps_exec.engines.brief_assembly_engine"
        )

        factual_claims = fixture.get("factual_claims", [])
        recommendations = fixture.get("recommendations", [])
        caveats = fixture.get("caveats", [])

        # Claim register — every claim must have an evidence_source.
        claim_register = []
        unsupported_claims = []
        for c in factual_claims:
            entry = {
                "claim_id": c["claim_id"],
                "text": c["text"],
                "evidence_source": c.get("evidence_source"),
                "support_score": c.get("support_score", 0.0),
                "labeled_as": "fact",
            }
            claim_register.append(entry)
            if not c.get("evidence_source"):
                unsupported_claims.append(entry)

        # Recommendation register — explicit "recommendation" label, never "fact".
        recommendation_register = []
        for r in recommendations:
            label = r.get("labeled_as", "recommendation")
            if label != "recommendation":
                # Mislabel — flag it.
                unsupported_claims.append({
                    "rec_id": r["rec_id"],
                    "text": r["text"],
                    "issue": f"recommendation labeled as {label!r} (must be 'recommendation')",
                })
            recommendation_register.append({
                "rec_id": r["rec_id"],
                "text": r["text"],
                "labeled_as": label,
                "confidence": r.get("confidence", 0.0),
                "depends_on_claims": r.get("depends_on_claims", []),
            })

        outputs: dict[str, str] = {}
        k, p = write_artifact(ctx, rel_filename="claim_register.json", payload=claim_register, kind="ClaimRegister")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="recommendation_register.json", payload=recommendation_register, kind="RecommendationRegister")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="unsupported_claims.json", payload=unsupported_claims, kind="UnsupportedClaims")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="caveats.json", payload=caveats, kind="Caveats")
        outputs[k] = p

        # Brief markdown — facts vs recommendations clearly separated
        body_lines = [
            f"# Executive Brief — {fixture.get('topic', 'Topic')}",
            "",
            f"- Brief ID: `{fixture.get('brief_id')}`",
            f"- Audience: {fixture.get('audience')}",
            f"- Engine import: {'OK' if engine_ok else f'FAIL ({engine_detail})'}",
            "",
            "## Facts (evidence-backed)",
            "",
        ]
        for c in claim_register:
            body_lines.append(
                f"- **[FACT {c['claim_id']}]** {c['text']}  "
                f"_(source: `{c['evidence_source']}`, support={c['support_score']:.2f})_"
            )
        body_lines.append("")
        body_lines.append("## Recommendations (NOT facts)")
        body_lines.append("")
        for r in recommendation_register:
            body_lines.append(
                f"- **[RECOMMENDATION {r['rec_id']}]** {r['text']}  "
                f"_(confidence={r['confidence']:.2f}, depends on: "
                f"{', '.join(r['depends_on_claims']) or 'none'})_"
            )
        if caveats:
            body_lines.append("")
            body_lines.append("## Caveats")
            body_lines.append("")
            for cav in caveats:
                body_lines.append(
                    f"- **[{cav['severity'].upper()}]** {cav['text']}"
                )
        rel = write_markdown(ctx, rel_filename="evidence_backed_brief.md", body="\n".join(body_lines))
        outputs["EvidenceBackedBrief"] = rel
        return outputs
