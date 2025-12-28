#!/usr/bin/env python3
"""
Resume Engine (E2) - Zero-Loss Generation (ZLG) Implementation
L5 Sub-Atomic Agentic System for Hyper-Personalized Document Generation

Phases:
- P3: Prompt Firewall (Input Security)
- P4: Fact Checker (Truth Anchor Validation)
- P5: Process Registration and Logging
- P10: Shadow Mode (Self-Correction)
- ZLG Loop: Draft, Vet, and Self-Correct (MAX_REWRITE_ATTEMPTS=3)
"""
# Standard library imports
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

from agentic_core.L2_execution.knowledge.knowledge_utilities import (
    KnowledgeResult,
    get_consolidated_knowledge,
)
from agentic_core.L2_execution.security.security_utilities import (
    SecurityStatus,
    get_fact_checker,
    get_prompt_firewall,
)
from agentic_core.utils.core_extensions.core_utilities import (
    DraftGenerator,
    FileManager,
    SemanticScorer,
    log_action,
    register_process,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/resume_engine_zlg.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EngineStatus(Enum):
    """Status codes for engine operations."""
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    IN_PROGRESS = "IN_PROGRESS"
    SHADOW_MODE = "SHADOW_MODE"


class ExitReason(Enum):
    """Exit reasons for ZLG termination."""
    P3_INJECTION_BLOCK = "P3_INJECTION_BLOCK"
    ZLG_MAX_ATTEMPTS = "ZLG_MAX_ATTEMPTS"
    ZLG_SUCCESS = "ZLG_SUCCESS"
    CRITICAL_ERROR = "CRITICAL_ERROR"


@dataclass
class JobDescription:
    """Job description data."""
    url: str
    content: str
    company: Optional[str] = None
    position: Optional[str] = None


@dataclass
class DraftResult:
    """Result from draft generation."""
    content: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RewriteResult:
    """Result from shadow mode rewrite."""
    content: str
    improvements: List[str]
    confidence: float


class ShadowModeEngine:
    """P10: Shadow Mode for self-correction simulation."""

    def __init__(self, llm_client=None):
        """
        Initialize Shadow Mode engine.

        Args:
            llm_client: LLM client for rewrite generation
        """
        self.llm_client = llm_client

    def rewrite_draft(self, draft: str, error_reason: str) -> RewriteResult:
        """
        Rewrite draft in shadow mode to test improvements.

        Args:
            draft: Original draft content
            error_reason: Reason for rewrite

        Returns:
            RewriteResult with improved draft
        """
        logger.info(f"P10_SHADOW_START: Rewriting due to: {error_reason}")

        if self.llm_client:
            return self._rewrite_with_llm(draft, error_reason)
        else:
            return self._rewrite_with_rules(draft, error_reason)

    def _rewrite_with_llm(self, draft: str, error_reason: str) -> RewriteResult:
        """Rewrite using LLM."""
        try:
            prompt = f"""
Improve this cover letter draft to address: {error_reason}

ORIGINAL DRAFT:
{draft}

Requirements:
- Fix the identified issues
- Maintain professional tone
- Keep it concise and impactful
- Ensure all claims are verifiable

IMPROVED DRAFT:
"""
            response = self.llm_client.generate(prompt)

            return RewriteResult(
                content=response.text,
                improvements=["Fixed " + error_reason],
                confidence=0.8
            )
        except Exception as e:
            logger.error(f"P10_LLM_FAILED: {e}")
            return self._rewrite_with_rules(draft, error_reason)

    def _rewrite_with_rules(self, draft: str, error_reason: str) -> RewriteResult:
        """Rewrite using rule-based approach."""
        improvements = []
        improved_draft = draft

        # Fix skill exaggerations
        if "skill" in error_reason.lower():
            improved_draft = self._fix_skill_claims(improved_draft)
            improvements.append("Verified all skill claims")

        # Fix quality issues
        if "quality" in error_reason.lower() or "score" in error_reason.lower():
            improved_draft = self._improve_quality(improved_draft)
            improvements.append("Improved readability and structure")

        # Fix professionalism
        if "professional" in error_reason.lower():
            improved_draft = self._enhance_professionalism(improved_draft)
            improvements.append("Enhanced professional tone")

        return RewriteResult(
            content=improved_draft,
            improvements=improvements,
            confidence=0.6
        )

    def _fix_skill_claims(self, draft: str) -> str:
        """Fix exaggerated skill claims."""
        # Replace superlatives with more modest claims
        replacements = {
            "expert in": "experienced in",
            "master of": "proficient in",
            "world-class": "skilled",
            "best": "skilled",
            "perfect": "strong"
        }

        improved = draft
        for old, new in replacements.items():
            improved = improved.replace(old, new)

        return improved

    def _improve_quality(self, draft: str) -> str:
        """Improve draft quality."""
        # Add paragraph breaks if missing
        if "\n\n" not in draft:
            sentences = draft.split(". ")
            improved = ".\n\n".join(sentences)
        else:
            improved = draft

        # Ensure proper closing
        if not any(closing in improved for closing in ["Sincerely", "Best regards", "Regards"]):
            improved += "\n\nSincerely,\n[Your Name]"

        return improved

    def _enhance_professionalism(self, draft: str) -> str:
        """Enhance professional tone."""
        # Remove casual language
        casual_replacements = {
            "I'm": "I am",
            "I've": "I have",
            "I'd": "I would",
            "really": "highly",
            "awesome": "excellent",
            "cool": "innovative",
            "guys": "team",
            "stuff": "elements"
        }

        improved = draft
        for old, new in casual_replacements.items():
            improved = improved.replace(old, new)

        return improved


class ResumeEngineZLG:
    """
    Zero-Loss Generation Resume Engine.

    Implements ZLG policy with P3/P4 security checks,
    P10 shadow mode self-correction, and MAX_REWRITE_ATTEMPTS=3.
    """

    MAX_REWRITE_ATTEMPTS = 3
    MIN_ACCEPTABLE_SCORE = 0.5

    def __init__(self, output_dir: str = "output"):
        """
        Initialize Resume Engine.

        Args:
            output_dir: Directory for generated documents
        """
        self.output_dir = output_dir
        self.agent_pid = os.getpid()
        self.rewrite_count = 0
        self.last_score = 0.0

        # Initialize components
        self.prompt_firewall = get_prompt_firewall()
        self.fact_checker = get_fact_checker()
        self.knowledge = get_consolidated_knowledge()
        self.draft_generator = DraftGenerator()
        self.semantic_scorer = SemanticScorer()
        self.shadow_engine = ShadowModeEngine()

        # P5: Register process
        register_process("ResumeEngine", self.agent_pid)

        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def generate_cover_letter(self, job_url: str, user_id: str = "default") -> Tuple[ExitReason, Optional[str]]:
        """
        Generate cover letter with ZLG policy.

        Args:
            job_url: URL of job posting
            user_id: User identifier for profile

        Returns:
            Tuple of (exit_reason, output_path)
        """
        logger.info("="*60)
        logger.info("ZLG ENGINE START: Resume Engine (E2)")
        logger.info("="*60)

        try:
            # ----------------------------------------------------------------
            # Action 1: Fetch Job Description
            # ----------------------------------------------------------------
            log_action("L1_FETCH_START", {"job_url": job_url})
            job_desc = self._fetch_job_description(job_url)

            if not job_desc.content:
                logger.error("Failed to fetch job description")
                return (ExitReason.CRITICAL_ERROR, None)

            # ----------------------------------------------------------------
            # Action 2: P3 Prompt Firewall Scan
            # ----------------------------------------------------------------
            log_action("P3_START")
            p3_result = self.prompt_firewall.scan_input(job_desc.content)

            if p3_result.status == SecurityStatus.FAIL:
                logger.error("P3_FAIL: Injection detected")
                log_action("P3_INJECTION_BLOCK")
                return (ExitReason.P3_INJECTION_BLOCK, None)

            # ----------------------------------------------------------------
            # Action 3: L5 Consolidated Knowledge Retrieval
            # ----------------------------------------------------------------
            log_action("L5_START")
            knowledge = self.knowledge.search_knowledge(
                query=f"{user_id} cover letter template",
                types=["profile", "template"]
            )

            if not knowledge.user_profile or not knowledge.template:
                logger.error("Failed to retrieve knowledge")
                return (ExitReason.CRITICAL_ERROR, None)

            # ----------------------------------------------------------------
            # ZLG LOOP: Draft, Vet, and Self-Correct
            # ----------------------------------------------------------------
            while True:
                # Check rewrite limit
                if self.rewrite_count >= self.MAX_REWRITE_ATTEMPTS:
                    logger.error("ZLG_FAIL: Max rewrite attempts reached")
                    log_action("ZLG_FAIL_MAX_ATTEMPTS", {"score": self.last_score})
                    return (ExitReason.ZLG_MAX_ATTEMPTS, None)

                # ----------------------------------------------------------------
                # Action 4: Draft Generation
                # ----------------------------------------------------------------
                log_action("DRAFT_START", {
                    "attempt": self.rewrite_count,
                    "max_attempts": self.MAX_REWRITE_ATTEMPTS
                })

                draft_result = self.draft_generator.generate_draft_llm(
                    profile=knowledge.user_profile,
                    job_desc=job_desc.content,
                    template=knowledge.template
                )

                # ----------------------------------------------------------------
                # Action 5: P4 Truth Anchor Validation
                # ----------------------------------------------------------------
                log_action("P4_START")
                p4_result = self.fact_checker.validate_skills(draft_result.content)

                # ----------------------------------------------------------------
                # Action 6: Semantic Scoring
                # ----------------------------------------------------------------
                log_action("SCORE_START")
                score_result = self.semantic_scorer.semantic_score_draft(draft_result.content)
                self.last_score = score_result["quality"]

                # ----------------------------------------------------------------
                # ZLG VETTING GATE: P4 & QUALITY CHECK
                # ----------------------------------------------------------------
                if (p4_result.status == SecurityStatus.PASS and
                    score_result["quality"] >= self.MIN_ACCEPTABLE_SCORE):
                    # Success path
                    logger.info("ZLG_SUCCESS: Draft passed all checks")
                    return self._finalize_output(draft_result, knowledge, score_result)

                # Failure path - trigger P10 Shadow Mode
                logger.warning(f"VET_FAIL: P4={p4_result.status.value}, Score={self.last_score}")
                self.rewrite_count += 1

                # ----------------------------------------------------------------
                # Action 7: P10 Shadow Mode Self-Correction
                # ----------------------------------------------------------------
                log_action("P10_START", {"attempt": self.rewrite_count})

                error_reason = ""
                if p4_result.status == SecurityStatus.FAIL:
                    error_reason += f"P4: {p4_result.reason}; "
                if score_result["quality"] < self.MIN_ACCEPTABLE_SCORE:
                    error_reason += f"Quality: {score_result['reason']}"

                rewrite_result = self.shadow_engine.rewrite_draft(
                    draft_result.content,
                    error_reason
                )

                # Apply shadow mode rewrite
                draft_result.content = rewrite_result.content
                log_action("P10_SHADOW_REWRITE", {
                    "attempt": self.rewrite_count,
                    "improvements": rewrite_result.improvements
                })

                # Continue loop for re-validation
                continue

        except Exception as e:
            logger.error(f"Critical error: {e}")
            return (ExitReason.CRITICAL_ERROR, None)

    def _fetch_job_description(self, url: str) -> JobDescription:
        """Fetch job description from URL."""
        # In real implementation, use web scraper
        # For now, return mock data
        return JobDescription(
            url=url,
            content="""We are seeking a Senior Software Engineer to join our growing team.
            The ideal candidate will have experience with Python, JavaScript, and React.
            You will be responsible for developing and maintaining web applications,
            working with a team of developers, and ensuring high-quality code delivery."""
        )

    def _finalize_output(self, draft_result: DraftResult,
                        knowledge: KnowledgeResult,
                        score_result: Dict[str, Any]) -> Tuple[ExitReason, str]:
        """Finalize and save successful draft."""
        # Generate output filename
        timestamp = knowledge.user_profile.get("name", "cover_letter").replace(" ", "_")
        filename = f"{timestamp}_cover_letter.txt"
        output_path = os.path.join(self.output_dir, filename)

        # Write file
        if FileManager.write_file(output_path, draft_result.content):
            logger.info(f"ZLG_FINAL_SUCCESS: Cover letter saved to {output_path}")

            # Log to L5 (placeholder)
            log_action("ZLG_FINAL_SUCCESS", {
                "output_file": output_path,
                "score": self.last_score,
                "grade": score_result["grade"]
            })

            return (ExitReason.ZLG_SUCCESS, output_path)
        else:
            logger.error("Failed to write output file")
            return (ExitReason.CRITICAL_ERROR, None)


def main():
    """Main entry point for Resume Engine."""
    # Example usage
    engine = ResumeEngineZLG()

    # Test generation
    exit_reason, output_path = engine.generate_cover_letter(
        job_url="https://example.com/job/123",
        user_id="default"
    )

    print(f"\n{'='*60}")
    print(f"Resume Engine Exit: {exit_reason.value}")
    if output_path:
        print(f"Output: {output_path}")
    print(f"{'='*60}")

    return 0 if exit_reason == ExitReason.ZLG_SUCCESS else 1


if __name__ == "__main__":
    sys.exit(main())