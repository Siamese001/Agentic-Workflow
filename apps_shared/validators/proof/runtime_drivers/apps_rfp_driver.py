"""apps_rfp real-runtime driver.

Imports ``apps_rfp.engines.proposal_assembly_engine`` (lifecycle-trace
``_emit_*`` calls fire at module load), then builds the user-spec
artifacts (requirement_map, capability_evidence_map, response_sections,
unsupported_claims, submission_risk_packet) from the fixture.
"""

from __future__ import annotations

from apps_shared.validators.proof.runtime_drivers._driver_base import (
    import_real_engine,
    write_artifact,
    write_markdown,
)


class AppsRfpDriver:
    app_id = "apps_rfp"

    def invoke(self, ctx) -> dict[str, str]:
        fixture = dict(ctx.spec.extra_payload or {})

        engine_ok, engine_detail = import_real_engine(
            "apps_rfp.engines.proposal_assembly_engine"
        )

        requirements = fixture.get("requirements", [])
        evidence = fixture.get("capability_evidence", [])

        # requirement_map: every requirement mapped to evidence support
        evidence_by_req: dict[str, list] = {}
        for ev in evidence:
            evidence_by_req.setdefault(ev.get("supports_req", ""), []).append(ev)
        requirement_map = []
        for req in requirements:
            matched = evidence_by_req.get(req["id"], [])
            requirement_map.append({
                "requirement_id": req["id"],
                "category": req.get("category", "unknown"),
                "text": req["text"],
                "evidence_count": len(matched),
                "evidence_ids": [e["evidence_id"] for e in matched],
                "max_support_score": max(
                    (e.get("support_score", 0.0) for e in matched), default=0.0
                ),
            })

        # capability_evidence_map: inverse view
        capability_map = {}
        for ev in evidence:
            capability_map[ev["capability"]] = {
                "evidence_id": ev["evidence_id"],
                "evidence_type": ev.get("evidence_type"),
                "supports_req": ev.get("supports_req"),
                "support_score": ev.get("support_score"),
            }

        # unsupported_claims: requirements with no evidence
        unsupported = [
            {"requirement_id": r["requirement_id"], "text": r["text"]}
            for r in requirement_map
            if r["evidence_count"] == 0
        ]

        # submission_risk_packet
        risk_packet = {
            "rfp_id": fixture.get("rfp_id"),
            "client_name": fixture.get("client_name"),
            "industry": fixture.get("industry"),
            "total_requirements": len(requirements),
            "supported_requirements": sum(1 for r in requirement_map if r["evidence_count"] > 0),
            "unsupported_requirements": len(unsupported),
            "coverage_pct": (
                (len(requirements) - len(unsupported)) / len(requirements)
                if requirements else 0.0
            ),
            "engine_import_ok": engine_ok,
            "engine_detail": engine_detail,
        }

        # response_sections.md — deterministic skeleton
        section_lines = [
            "# RFP Response — " + str(fixture.get("client_name", "Client")),
            "",
            f"- RFP ID: `{fixture.get('rfp_id')}`",
            f"- Industry: {fixture.get('industry')}",
            f"- Coverage: {risk_packet['supported_requirements']}/{risk_packet['total_requirements']} requirements",
            "",
            "## Requirements & evidence",
            "",
        ]
        for r in requirement_map:
            section_lines.append(
                f"- **{r['requirement_id']}** ({r['category']}): {r['text']} → "
                f"{r['evidence_count']} evidence item(s) "
                f"(max support {r['max_support_score']:.2f})"
            )
        if unsupported:
            section_lines.append("")
            section_lines.append("## Unsupported claims (auto-flagged)")
            for u in unsupported:
                section_lines.append(f"- **{u['requirement_id']}**: {u['text']}")

        outputs: dict[str, str] = {}
        k, p = write_artifact(ctx, rel_filename="requirement_map.json", payload=requirement_map, kind="RequirementMap")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="capability_evidence_map.json", payload=capability_map, kind="CapabilityEvidenceMap")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="unsupported_claims.json", payload=unsupported, kind="UnsupportedClaims")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="submission_risk_packet.json", payload=risk_packet, kind="SubmissionRiskPacket")
        outputs[k] = p
        rel = write_markdown(ctx, rel_filename="response_sections.md", body="\n".join(section_lines))
        outputs["ResponseSections"] = rel
        return outputs
