"""Bullet generation and review stack."""

import asyncio
import json
import re

    BaseAgent,
    BulletList,
    CritiqueResult,
    StrategyPlan,
    _format_prompt_with_defaults,
    track_metrics,
)


class BulletEntityExtractionAgent(BaseAgent):
    """Extracts key entities from bullet text."""

    class Output(BaseModel):
        bullet_id: str
        entities: list[dict[str, Any]] = Field(default_factory=list)
        raw_text: str
        experience_id: str | None = None

    ENTITY_PATTERN = re.compile(r"\b([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+){0,3})\b")
    ORGANIZATION_HINTS = {"inc", "corp", "llc", "ltd", "company", "technologies"}
    TECHNOLOGY_HINTS = {
        "aws",
        "gcp",
        "azure",
        "python",
        "sql",
        "spark",
        "docker",
        "kubernetes",
        "hadoop",
        "tensorflow",
        "pytorch",
        "salesforce",
    }

    @track_metrics("run_bullet_entity_extraction")
    async def run_async(
        self,
        bullet_id: str,
        bullet_text: str,
        experience: dict[str, Any],
        workflow_id: str,
    ) -> dict[str, Any]:
        text = bullet_text or ""
        entities: list[dict[str, Any]] = []
        seen = set()

        for match in self.ENTITY_PATTERN.finditer(text):
            candidate = match.group(1).strip()
            if not candidate or candidate.lower() in seen:
                continue
            seen.add(candidate.lower())
            lower_candidate = candidate.lower()
            ent_type = "proper_noun"
            if any(hint in lower_candidate for hint in self.ORGANIZATION_HINTS):
                ent_type = "organization"
            elif any(
                lower_candidate.endswith(hint) or hint in lower_candidate
                for hint in self.ORGANIZATION_HINTS
            ):
                ent_type = "organization"
            elif any(
                lower_candidate == hint or hint in lower_candidate.split()
                for hint in self.TECHNOLOGY_HINTS
            ):
                ent_type = "technology"
            entities.append(
                {
                    "name": candidate,
                    "type": ent_type,
                    "span": [match.start(), match.end()],
                }
            )

        output = self.Output(
            bullet_id=bullet_id,
            entities=entities,
            raw_text=text,
            experience_id=experience.get("id") if isinstance(experience, dict) else None,
        )
        return output.model_dump()


class BulletMetricsEnrichmentAgent(BaseAgent):
    """Annotates bullets with derived metrics metadata."""

    class Output(BaseModel):
        bullet_id: str
        has_metric: bool
        metrics: dict[str, list[str]] = Field(default_factory=dict)
        raw_numbers: list[str] = Field(default_factory=list)
        raw_text: str

    METRIC_PATTERN = re.compile(r"(?P<number>-?\d+(?:[\.,]\d+)?)(?P<suffix>%|x|X|\b)")
    CURRENCY_PATTERN = re.compile(r"\$[\d,]+(?:\.\d+)?")

    @track_metrics("run_bullet_metrics_enrichment")
    async def run_async(self, bullet_id: str, bullet_text: str, workflow_id: str) -> dict[str, Any]:
        text = bullet_text or ""
        metrics: dict[str, list[str]] = defaultdict(list)
        raw_numbers: list[str] = []

        for match in self.METRIC_PATTERN.finditer(text):
            number = match.group("number")
            suffix = match.group("suffix")
            raw = f"{number}{suffix.strip()}".strip()
            raw_numbers.append(raw)
            if suffix.strip() == "%":
                metrics["percentage"].append(raw)
            elif suffix.strip().lower() == "x":
                metrics["multipliers"].append(raw)
            else:
                metrics["absolute"].append(raw)

        for money in self.CURRENCY_PATTERN.findall(text):
            metrics["currency"].append(money)
            raw_numbers.append(money)

        output = self.Output(
            bullet_id=bullet_id,
            has_metric=bool(raw_numbers),
            metrics={k: sorted(set(v)) for k, v in metrics.items()},
            raw_numbers=sorted(set(raw_numbers)),
            raw_text=text,
        )
        return output.model_dump()


class BulletNarrativeSynthesisAgent(BaseAgent):
    """Produces narrative scaffolding for each bullet."""

    class Output(BaseModel):
        bullet_id: str
        storyline: str
        highlights: list[str] = Field(default_factory=list)
        tone: str

    @track_metrics("run_bullet_narrative_synthesis")
    async def run_async(
        self,
        bullet_id: str,
        bullet_text: str,
        metrics_payload: dict[str, Any],
        workflow_id: str,
    ) -> dict[str, Any]:
        text = bullet_text or ""
        fragments = [frag.strip() for frag in re.split(r"[.;]", text) if frag.strip()]
        tone = "impact" if metrics_payload.get("has_metric") else "descriptive"
        if not fragments:
            fragments = [text.strip()] if text else []

        output = self.Output(
            bullet_id=bullet_id,
            storyline="; ".join(fragments[:2]),
            highlights=fragments[:3],
            tone=tone,
        )
        return output.model_dump()


class BulletEvidenceLinkerAgent(BaseAgent):
    """Links bullets back to resume evidence."""

    class Output(BaseModel):
        bullet_id: str
        evidence: list[str] = Field(default_factory=list)
        confidence: float

    @track_metrics("run_bullet_evidence_linker")
    async def run_async(
        self,
        bullet_id: str,
        bullet_text: str,
        resume_section: dict[str, Any],
        workflow_id: str,
    ) -> dict[str, Any]:
        evidence: list[str] = []
        section_bullets = resume_section.get("bullet_pool", [])
        for existing in section_bullets[:5]:
            if bullet_text and existing.lower() in bullet_text.lower():
                evidence.append(existing)
        if not evidence and section_bullets:
            evidence.append(section_bullets[0])

        output = self.Output(
            bullet_id=bullet_id,
            evidence=evidence,
            confidence=0.7 if evidence else 0.3,
        )
        return output.model_dump()


class BulletConfidenceScoringAgent(BaseAgent):
    """Scores bullet readiness for publication."""

    class Output(BaseModel):
        bullet_id: str
        score: float
        rationale: str

    @track_metrics("run_bullet_confidence_scoring")
    async def run_async(
        self,
        bullet_id: str,
        bullet_payload: dict[str, Any],
        workflow_id: str,
    ) -> dict[str, Any]:
        score = 0.5
        rationale: list[str] = []
        if bullet_payload.get("metrics", {}).get("has_metric"):
            score += 0.2
            rationale.append("Contains quantifiable metric.")
        if bullet_payload.get("entities", {}).get("entities"):
            score += 0.1
            rationale.append("References specific entities.")
        if bullet_payload.get("storyline", {}).get("storyline"):
            score += 0.1
            rationale.append("Narrative structure present.")
        score = min(score, 1.0)

        output = self.Output(
            bullet_id=bullet_id,
            score=round(score, 2),
            rationale=" ".join(rationale) or "Baseline confidence.",
        )
        return output.model_dump()


class BulletCoordinatorAgent(BaseAgent):
    """Coordinates bullet enrichment agents."""

    def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.entity_agent = BulletEntityExtractionAgent(context, debug_mode)
        self.metrics_agent = BulletMetricsEnrichmentAgent(context, debug_mode)
        self.narrative_agent = BulletNarrativeSynthesisAgent(context, debug_mode)
        self.evidence_agent = BulletEvidenceLinkerAgent(context, debug_mode)
        self.confidence_agent = BulletConfidenceScoringAgent(context, debug_mode)

    @track_metrics("run_bullet_coordinator")
    async def run_async(
        self,
        bullets: list[dict[str, Any]],
        resume: dict[str, Any],
        workflow_id: str,
    ) -> list[dict[str, Any]]:
        self.log_info("Coordinating bullet enrichment agents...")

        enriched_bullets = []
        for bullet in bullets:
            bullet_id = bullet.get("id", "unknown")
            text = bullet.get("text", "")
            experience = bullet.get("experience", {})

            entities = await self.entity_agent.run_async(bullet_id, text, experience, workflow_id)
            metrics = await self.metrics_agent.run_async(bullet_id, text, workflow_id)
            narrative = await self.narrative_agent.run_async(bullet_id, text, metrics, workflow_id)
            evidence = await self.evidence_agent.run_async(
                bullet_id,
                text,
                experience if isinstance(experience, dict) else {},
                workflow_id,
            )
            confidence = await self.confidence_agent.run_async(
                bullet_id,
                {
                    "metrics": metrics,
                    "entities": entities,
                    "storyline": narrative,
                },
                workflow_id,
            )

            enriched_bullets.append(
                {
                    "id": bullet_id,
                    "text": text,
                    "experience": experience,
                    "entities": entities,
                    "metrics": metrics,
                    "narrative": narrative,
                    "evidence": evidence,
                    "confidence": confidence,
                }
            )

        return enriched_bullets


class BulletProvenanceAuditorAgent(BaseAgent):
    """Audits bullet provenance and ensures traceability."""

    @track_metrics("run_bullet_provenance_auditor")
    async def run_async(
        self,
        bullets: list[dict[str, Any]],
        workflow_id: str,
    ) -> dict[str, Any]:
        self.log_info("Auditing bullet provenance...")
        missing_evidence = [
            bullet["id"] for bullet in bullets if not bullet.get("evidence", {}).get("evidence")
        ]
        duplicates = [
            item for item, count in Counter(b["text"] for b in bullets).items() if count > 1
        ]
        return {
            "missing_evidence": missing_evidence,
            "duplicate_text": duplicates,
        }


class AsyncBulletGeneratorAgent(BaseAgent):
    """Generates and validates bullets asynchronously."""

    def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.coordinator = BulletCoordinatorAgent(context, debug_mode)

    async def _generate_customized(
        self, prompt: str, experience: dict[str, Any], client: Any
    ) -> list[str]:
        gen_prompt = f"""
        {client.goal_state}
        {client.top_failures}
        -------------------
        MODE: CREATIVE
        TASK: {prompt}\nCustomize these bullets:\n{json.dumps(experience.get("bullet_pool", []))}
        REFLECTION: Are these bullets customized to the prompt?
        Output: JSON array of 2-3 achievement bullets.
        """
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": gen_prompt}],
            temperature=self.config.model_config.bullet_generator_model.temperature,
            response_format="json_object",
        )
        content, error = self.validator.validate(response["content"], (list, dict))
        if error:
            return []
        if isinstance(content, list):
            return content
        if isinstance(content, dict) and "bullets" in content:
            return content["bullets"]
        return []

    async def _generate_synthetic(
        self, prompt: str, experience: dict[str, Any], client: Any
    ) -> list[str]:
        gen_prompt = f"""
        {client.goal_state}
        {client.top_failures}
        -------------------
        MODE: CREATIVE
        TASK: {prompt}\nExperience (no bullets):\n{json.dumps({"title": experience.get("title"), "company": experience.get("company")})}
        REFLECTION: Are these bullets new and metrics-driven?
        Output: JSON array of 2 new achievement bullets.
        """
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": gen_prompt}],
            temperature=self.config.model_config.bullet_generator_model.temperature,
            response_format="json_object",
        )
        content, error = self.validator.validate(response["content"], (list, dict))
        if error:
            return []
        if isinstance(content, list):
            return content
        if isinstance(content, dict) and "bullets" in content:
            return content["bullets"]
        return []

    @track_metrics("run_fact_check_bullets")
    async def run_fact_check(
        self,
        bullets: list[str],
        experience: dict[str, Any],
        strategy: StrategyPlan,
        client: Any,
    ) -> list[str]:
        self.log_info("Fact-checking bullets (v10.7)...")

        prompt_template = self.prompt_manager.get_template("bullet_generation_fact_check")

        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {
                "experience": json.dumps(experience),
                "bullets": json.dumps(bullets),
                "strategy": strategy.model_dump_json(),
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.bullet_fact_check_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(response["content"], BulletList)
        if error:
            self.log_warning(f"Fact-check validation failed: {error}. Returning original bullets.")
            return bullets

        return validated_output.verified_bullets

    @track_metrics("run_bullet_generator")
    async def run_async(
        self,
        task_context: dict[str, Any],
        strategy: StrategyPlan,
        workflow_id: str,
    ) -> dict[str, Any]:
        self.log_info("Generating bullets asynchronously...")

        generation_client = self.get_model_client("bullet_generator_model")
        fact_check_client = self.get_model_client("bullet_fact_check_model")

        bullet_prompts = task_context.get("prompts", [])
        resume_experience = task_context.get("experience", [])

        generation_tasks = []
        for prompt in bullet_prompts:
            for experience in resume_experience:
                if experience.get("bullet_pool"):
                    generation_tasks.append(
                        self._generate_customized(prompt, experience, generation_client)
                    )
                else:
                    generation_tasks.append(
                        self._generate_synthetic(prompt, experience, generation_client)
                    )

        generated_results = await asyncio.gather(*generation_tasks)
        flat_generated = [bullet for result in generated_results for bullet in result]

        fact_checked = await self.run_fact_check(
            flat_generated,
            resume_experience[0] if resume_experience else {},
            strategy,
            fact_check_client,
        )

        enriched_payload = await self.coordinator.run_async(
            [
                {
                    "id": f"gen_{idx}",
                    "text": bullet_text,
                    "experience": resume_experience[idx % len(resume_experience)]
                    if resume_experience
                    else {},
                }
                for idx, bullet_text in enumerate(fact_checked)
            ],
            {"master_resume": {"professional_experience": resume_experience}},
            workflow_id,
        )

        return {
            "bullets": enriched_payload,
            "raw_generated": flat_generated,
        }


class AsyncBulletCritiqueAgent(BaseAgent):
    """Critiques bullets in parallel and aggregates feedback."""

    @track_metrics("run_bullet_critique")
    async def run_async(
        self,
        bullets: list[dict[str, Any]],
        critique_prompt: str,
        workflow_id: str,
    ) -> list[dict[str, Any]]:
        self.log_info("Critiquing bullets with validation (v10.7)...")

        client = self.get_model_client("critique_model")
        bullet_texts = [b["text"] for b in bullets]
        critique_tasks = []
        for bullet in bullet_texts:
            task_prompt = f"""
            {client.goal_state}
            {client.top_failures}
            -------------------
            MODE: ANALYTICAL
            TASK: {critique_prompt}\nBullet: {bullet}
            REFLECTION: Is this critique specific?
            Output: JSON with score 0-10 and suggestions.
            """
            critique_tasks.append(
                client.chat_completion_async(
                    messages=[{"role": "user", "content": task_prompt}],
                    temperature=self.config.model_config.critique_model.temperature,
                    response_format="json_object",
                )
            )
        responses = await asyncio.gather(*critique_tasks)

        critique_results: list[CritiqueResult] = []
        for res in responses:
            validated_output, error = self.validator.validate(res["content"], CritiqueResult)
            if error:
                critique_results.append(
                    CritiqueResult(score=0.0, suggestions=["Validation failed"])
                )
            else:
                critique_results.append(validated_output)

        self.log_feedback(
            workflow_id,
            "parallel_critique",
            "success",
            {"bullets_critiqued": len(bullets)},
        )

        final_critiqued_bullets = []
        for bullet, critique in zip(bullets, critique_results, strict=False):
            final_critiqued_bullets.append(
                {
                    "text": bullet["text"],
                    "experience": bullet.get("experience"),
                    "critique": critique.model_dump(),
                }
            )

        return final_critiqued_bullets
