"""Drafting guild stack with specialist agents."""

import json

    EvidenceBriefAssemblerTool,
    EvidenceClarificationTool,
)
    BaseAgent,
    StrategyPlan,
    track_metrics,
)

    CritiqueFindingRecord,
    CritiquePanelPacket,
    EvidenceBriefRecord,
    EvidenceClarificationRecord,
    EvidenceLiaisonPacket,
    SpecialistDraftPacket,
)


class StructureLeadAgent(BaseAgent):
    """Produces the structural outline for the draft."""

    @track_metrics("run_structure_lead")
    async def run_async(
        self,
        bullets: list[dict[str, Any]],
        strategy: StrategyPlan,
        workflow_id: str,
    ) -> SpecialistDraftPacket:
        self.log_info("Drafting Guild >> Structure Lead assembling sections...")

        summary_pivots = (
            strategy.key_achievements_to_highlight[:3]
            if strategy.key_achievements_to_highlight
            else []
        )
        bullet_texts = [b.get("text", "") for b in bullets]

        summary_content = (
            "; ".join(summary_pivots) if summary_pivots else " ".join(bullet_texts[:2])
        ).strip()

        experience_entries: list[dict[str, Any]] = []
        for bullet in bullets:
            experience = bullet.get("experience", {}) or {}
            entry: dict[str, Any] = {
                "company": experience.get("company", ""),
                "title": experience.get("title", ""),
                "bullet": bullet.get("text", ""),
                "metrics_present": any(ch.isdigit() for ch in bullet.get("text", "")),
            }
            if experience.get("years"):
                entry["tenure"] = experience.get("years")
            experience_entries.append(entry)

        sections = {
            "summary": {
                "draft": summary_content,
                "focus_areas": strategy.focus_areas,
                "tone": strategy.tone,
                "evidence_points": summary_pivots,
                "open_questions": [],
            },
            "experience": {
                "entries": experience_entries,
                "open_questions": [],
            },
        }

        notes = [
            (
                "Summary seeded from strategy achievements."
                if summary_pivots
                else "Summary derived from top-scoring bullets."
            ),
            f"Experience entries organized ({len(experience_entries)} bullets).",
        ]

        return SpecialistDraftPacket(
            specialist="Structure Lead",
            focus_area=strategy.strategy_name,
            sections=sections,
            notes=notes,
            dependencies=[],
        )


class NarrativeStylistAgent(BaseAgent):
    """Harmonizes voice and narrative flow across sections."""

    @track_metrics("run_narrative_stylist")
    async def run_async(
        self,
        structured_sections: dict[str, Any],
        strategy: StrategyPlan,
        workflow_id: str,
    ) -> SpecialistDraftPacket:
        self.log_info("Drafting Guild >> Narrative Stylist polishing tone...")

        styled_sections: dict[str, Any] = {}
        for section_name, section_payload in structured_sections.items():
            payload_copy = json.loads(json.dumps(section_payload))
            if section_name == "summary":
                base_text = payload_copy.get("draft", "")
                payload_copy["draft"] = self._apply_tone(base_text, strategy.tone)
                style_notes = payload_copy.setdefault("style_notes", [])
                style_notes.append(f"Tone harmonized to '{strategy.tone}'.")
            elif section_name == "experience":
                entries = payload_copy.get("entries", [])
                for entry in entries:
                    entry["bullet"] = self._tighten_language(entry.get("bullet", ""))
                payload_copy["entries"] = entries
            styled_sections[section_name] = payload_copy

        notes = [
            "Tone calibrated across summary and experience.",
            f"Maintained narrative focus on {', '.join(strategy.focus_areas)}.",
        ]

        return SpecialistDraftPacket(
            specialist="Narrative Stylist",
            focus_area=strategy.tone,
            sections=styled_sections,
            notes=notes,
            dependencies=[],
        )

    def _apply_tone(self, text: str, tone: str) -> str:
        if not text:
            return ""
        prefix = tone.capitalize() if tone else "Professional"
        if not text.lower().startswith(prefix.lower()):
            return f"{prefix} focus: {text}".strip()
        return text

    def _tighten_language(self, bullet: str) -> str:
        bullet = bullet.strip()
        if not bullet:
            return bullet
        bullet = bullet.replace("Responsible for", "Led")
        bullet = bullet.replace("Worked on", "Delivered")
        return bullet


class ComplianceEditorAgent(BaseAgent):
    """Ensures stylistic and policy compliance for the guild."""

    @track_metrics("run_compliance_editor")
    async def run_async(
        self,
        narrative_sections: dict[str, Any],
        workflow_id: str,
    ) -> SpecialistDraftPacket:
        self.log_info("Drafting Guild >> Compliance Editor auditing sections...")

        compliant_sections = json.loads(json.dumps(narrative_sections))
        notes: list[str] = []
        dependencies: list[str] = []

        summary = compliant_sections.get("summary", {})
        summary_text = summary.get("draft", "")
        if summary_text and len(summary_text.split()) < 40:
            summary.setdefault("open_questions", []).append(
                "Expand summary to ~40 words for recruiter context."
            )
        compliant_sections["summary"] = summary

        experience = compliant_sections.get("experience", {})
        entries = experience.get("entries", [])
        for entry in entries:
            bullet_text = entry.get("bullet", "")
            if bullet_text and not bullet_text.startswith("•"):
                entry["bullet"] = f"• {bullet_text}"
            if entry.get("metrics_present") is False:
                dependencies.append(
                    f"Add measurable outcomes for {entry.get('company', 'experience')}"
                )
        experience["entries"] = entries
        compliant_sections["experience"] = experience

        if dependencies:
            notes.append("Metrics enrichment required for some experience entries.")

        return SpecialistDraftPacket(
            specialist="Compliance Editor",
            focus_area="Policy & Style",
            sections=compliant_sections,
            notes=notes or ["No stylistic adjustments required."],
            dependencies=dependencies,
        )


class EvidenceLiaisonAgent(BaseAgent):
    """Coordinates clarification loops and evidence briefs."""

    def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.clarification_tool = EvidenceClarificationTool(context, debug_mode)
        self.brief_tool = EvidenceBriefAssemblerTool(context, debug_mode)

    @track_metrics("run_evidence_liaison")
    async def run_async(
        self,
        sections: dict[str, Any],
        resume: dict[str, Any],
        workflow_id: str,
    ) -> EvidenceLiaisonPacket:
        self.log_info("Drafting Guild >> Evidence Liaison orchestrating clarifications...")

        clarifications: list[EvidenceClarificationRecord] = []
        briefs: list[EvidenceBriefRecord] = []

        for section_name, payload in sections.items():
            payload_dict = payload if isinstance(payload, dict) else {"draft": payload}
            open_questions = payload_dict.get("open_questions", [])
            evidence_points = payload_dict.get("evidence_points") or self._harvest_resume_evidence(
                section_name, resume
            )

            if open_questions:
                clar_payload = {
                    "recipient": "bullet_team" if section_name == "experience" else "rag_team",
                    "questions": open_questions,
                    "context_summary": payload_dict.get("draft", "")[:200],
                }
                clar_dict = await self.clarification_tool.run_async(clar_payload, workflow_id)
                record = EvidenceClarificationTool.ClarificationRequestOutput.model_validate(
                    clar_dict
                )
                clarifications.append(EvidenceClarificationRecord(**record.model_dump()))

            brief_payload = {
                "section": section_name,
                "draft_content": payload_dict.get("draft", payload_dict),
                "evidence_points": evidence_points,
                "open_questions": open_questions,
            }
            brief_dict = await self.brief_tool.run_async(brief_payload, workflow_id)
            brief_record = EvidenceBriefAssemblerTool.EvidenceBriefOutput.model_validate(brief_dict)
            briefs.append(EvidenceBriefRecord(**brief_record.model_dump()))

        return EvidenceLiaisonPacket(clarifications=clarifications, briefs=briefs)

    def _harvest_resume_evidence(self, section_name: str, resume: dict[str, Any]) -> list[str]:
        evidence: list[str] = []
        if section_name == "experience":
            for experience in resume.get("professional_experience", []):
                company = experience.get("company", "")
                for bullet in experience.get("bullet_pool", [])[:3]:
                    evidence.append(f"{company}: {bullet}")
        else:
            summary_points = resume.get("summary", []) or resume.get("highlights", [])
            if isinstance(summary_points, list):
                evidence.extend(summary_points[:3])
        return evidence


class CritiqueRoutingPanel(BaseAgent):
    """Routes specialist critiques (style, fact, policy)."""

    @track_metrics("run_critique_routing_panel")
    async def run_async(
        self,
        sections: dict[str, Any],
        liaison_packet: EvidenceLiaisonPacket,
        workflow_id: str,
    ) -> CritiquePanelPacket:
        self.log_info("Drafting Guild >> Critique panel aggregating findings...")

        findings = [
            self._style_critic(sections),
            self._fact_critic(liaison_packet),
            self._policy_critic(sections),
        ]

        severity_rank = {"approved": 0, "info": 1, "revise": 2, "block": 3}
        overall_status = "approved"
        for finding in findings:
            level = finding.severity
            if severity_rank.get(level, 0) > severity_rank.get(overall_status, 0):
                overall_status = level

        return CritiquePanelPacket(findings=findings, overall_status=overall_status)

    def _style_critic(self, sections: dict[str, Any]) -> CritiqueFindingRecord:
        summary = sections.get("summary", {})
        text = ""
        if isinstance(summary, dict):
            text = summary.get("draft", "")
        issues: list[str] = []
        recommendations: list[str] = []
        severity = "approved"

        if text and len(text.split()) < 35:
            severity = "info"
            issues.append("Summary is shorter than the recommended range.")
            recommendations.append("Add more context or achievements to the summary.")

        return CritiqueFindingRecord(
            critic="Style Critic",
            severity=severity,
            issues=issues,
            recommendations=recommendations,
            blockers=[],
        )

    def _fact_critic(self, liaison_packet: EvidenceLiaisonPacket) -> CritiqueFindingRecord:
        outstanding = [brief for brief in liaison_packet.briefs if brief.outstanding_questions]
        clarifications_pending = [clar for clar in liaison_packet.clarifications if clar.questions]

        severity = "approved"
        issues: list[str] = []
        recommendations: list[str] = []

        if outstanding:
            severity = "revise"
            issues.append("Outstanding questions remain in evidence briefs.")
            recommendations.append("Resolve open questions before final synthesis.")
        elif clarifications_pending:
            severity = "info"
            issues.append("Clarification requests have been queued.")
            recommendations.append("Monitor responses from bullet/RAG agents.")

        return CritiqueFindingRecord(
            critic="Fact Critic",
            severity=severity,
            issues=issues,
            recommendations=recommendations,
            blockers=[],
        )

    def _policy_critic(self, sections: dict[str, Any]) -> CritiqueFindingRecord:
        banned_terms = {"confidential", "classified", "secret"}
        text_blob = json.dumps(sections).lower()
        offenders = [term for term in banned_terms if term in text_blob]

        severity = "approved"
        issues: list[str] = []
        blockers: list[str] = []
        recommendations: list[str] = []

        if offenders:
            severity = "block"
            issues.append(f"Policy-sensitive terms detected: {', '.join(offenders)}")
            blockers = offenders
            recommendations.append("Remove or sanitize policy-sensitive language.")

        return CritiqueFindingRecord(
            critic="Policy Critic",
            severity=severity,
            issues=issues,
            recommendations=recommendations,
            blockers=blockers,
        )


class DraftingGuildCoordinator(BaseAgent):
    """Coordinates drafting specialists and synthesizes outputs."""

    def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.structure_lead = StructureLeadAgent(context, debug_mode)
        self.narrative_stylist = NarrativeStylistAgent(context, debug_mode)
        self.compliance_editor = ComplianceEditorAgent(context, debug_mode)
        self.evidence_liaison = EvidenceLiaisonAgent(context, debug_mode)
        self.critique_panel = CritiqueRoutingPanel(context, debug_mode)

    @track_metrics("run_drafting_guild_coordinator")
    async def run_async(
        self,
        task_context: dict[str, Any],
        workflow_id: str,
    ) -> dict[str, Any]:
        self.log_info("Drafting Guild Coordinator orchestrating specialists...")

        strategy = task_context.get("strategy")
        if isinstance(strategy, dict):
            strategy = StrategyPlan.model_validate(strategy)

        bullets = task_context.get("bullets", [])
        resume = task_context.get("resume", {})

        structure_packet = await self.structure_lead.run_async(bullets, strategy, workflow_id)
        narrative_packet = await self.narrative_stylist.run_async(
            structure_packet.sections, strategy, workflow_id
        )
        compliance_packet = await self.compliance_editor.run_async(
            narrative_packet.sections, workflow_id
        )
        liaison_packet = await self.evidence_liaison.run_async(
            compliance_packet.sections, resume, workflow_id
        )
        critique_packet = await self.critique_panel.run_async(
            compliance_packet.sections, liaison_packet, workflow_id
        )

        final_sections = self._merge_sections(
            structure_packet.sections,
            narrative_packet.sections,
            compliance_packet.sections,
        )

        for brief in liaison_packet.briefs:
            section_payload = final_sections.setdefault(brief.section, {})
            if isinstance(section_payload, dict):
                section_payload.setdefault("evidence_brief", brief.brief)
                if brief.key_points:
                    section_payload.setdefault("evidence_points", brief.key_points)
                if brief.outstanding_questions:
                    section_payload.setdefault("open_questions", []).extend(
                        brief.outstanding_questions
                    )
            final_sections[brief.section] = section_payload

        guild_metadata = {
            "structure": structure_packet.model_dump(),
            "narrative": narrative_packet.model_dump(),
            "compliance": compliance_packet.model_dump(),
            "evidence": liaison_packet.model_dump(),
            "critique": critique_packet.model_dump(),
        }

        return {
            "final_output": final_sections,
            "guild_metadata": guild_metadata,
            "overall_status": critique_packet.overall_status,
            "phases_executed": 5,
        }

    def _merge_sections(self, *layers: dict[str, Any]) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for layer in layers:
            for key, value in layer.items():
                merged[key] = json.loads(json.dumps(value))
        return merged
