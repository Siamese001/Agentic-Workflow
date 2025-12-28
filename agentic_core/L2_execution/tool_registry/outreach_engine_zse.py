#!/usr/bin/env python3
"""
Outreach Engine (E3) - Zero-Side Effect (ZSE) Execution
Implements outreach with P6 vetting and P10 Shadow Mode
"""
import logging
import os
import time
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

from agentic_core.utils.P1_core.core_utilities import log_action, register_process
from agentic_core.utils.P1_core.networking import (
    get_networking_utility,
    send_email,
    strict_egress_filter,
)
from agentic_core.utils.P1_core.pitch_generator import PitchGenerator
from agentic_core.utils.P1_core.shadow_mode import ShadowModeEngine

logger = logging.getLogger(__name__)


class ExitReason(Enum):
    """Exit reasons for Outreach Engine."""
    ZSE_SUCCESS = "ZSE_SUCCESS"
    P8_EGRESS_BLOCK = "P8_EGRESS_BLOCK"
    ZSE_MAX_REFINEMENTS = "ZSE_MAX_REFINEMENTS"
    CRITICAL_ERROR = "CRITICAL_ERROR"


class OutreachEngineZSE:
    """
    Outreach Engine with Zero-Side Effect (ZSE) policy.

    Features:
    - P8 Egress Filter for all network traffic
    - P6 Consensus for brand compliance
    - P10 Shadow Mode for pitch refinement
    - MAX_PITCH_REFINEMENTS=2 hard limit
    - Mock email sending by default (dry_run=True)
    """

    MAX_PITCH_REFINEMENTS = 2

    def __init__(self, output_dir: str = "output", dry_run: bool = True):
        """
        Initialize Outreach Engine.

        Args:
            output_dir: Output directory for logs
            dry_run: If True, uses mock email sending
        """
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.refinement_count = 0

        # Initialize components
        self.networking = get_networking_utility()
        self.knowledge = get_consolidated_knowledge()
        self.pitch_generator = PitchGenerator()
        self.shadow_mode = ShadowModeEngine(self.pitch_generator)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Register with P5
        register_process("OutreachEngine", os.getpid())
        logger.info("============================================================")
        logger.info("ZSE ENGINE START: Outreach Engine (E3)")
        logger.info("============================================================")

    def execute_outreach(self, company_url: str, contact_email: str) -> tuple:
        """
        Execute full outreach sequence with ZSE policy.

        Args:
            company_url: URL to fetch company context
            contact_email: Target contact email

        Returns:
            Tuple of (exit_reason, result_data)
        """
        try:
            # ----------------------------------------------------------------
            # Action 1: Fetch Company Context with P8 Filter
            # ----------------------------------------------------------------
            log_action("L1_FETCH_START", {"company_url": company_url})

            # Check egress filter first
            egress_result = strict_egress_filter(company_url)
            if egress_result.status == "FAIL":
                logger.error(f"P8_BLOCK: {egress_result.reason}")
                log_action("P8_EGRESS_BLOCK", {"host": egress_result.host})
                return (ExitReason.P8_EGRESS_BLOCK, None)

            # Fetch company context
            context = self._fetch_company_context(company_url)

            # ----------------------------------------------------------------
            # Action 2: L5 Knowledge Retrieval and L4 Time
            # ----------------------------------------------------------------
            log_action("L5_L4_START")

            # Get contact relationships
            contact_context = self.knowledge.search_knowledge(
                query=f"Contact for {company_url}",
                types=["profile"]
            )

            # Convert time (L4 utility)
            optimal_send_time = self._calculate_optimal_time(contact_context)

            # ----------------------------------------------------------------
            # Action 3: Initial Pitch Generation
            # ----------------------------------------------------------------
            log_action("PITCH_START")

            pitch_draft = self.pitch_generator.generate_pitch(
                context=context,
                relationships=contact_context.user_profile or {}
            )

            # ----------------------------------------------------------------
            # ZSE LOOP: VET, SHADOW MODE, AND SELF-CORRECT
            # ----------------------------------------------------------------
            while True:
                # Check refinement limit
                if self.refinement_count >= self.MAX_PITCH_REFINEMENTS:
                    logger.error("ZSE_FAIL: Max refinement attempts reached")
                    log_action("ZSE_FAIL_MAX_REFINEMENTS", {"count": self.refinement_count})
                    self.knowledge.add_observations({
                        "event": "ZSE_FAIL_MAX_REFINEMENTS",
                        "count": self.refinement_count
                    })
                    return (ExitReason.ZSE_MAX_REFINEMENTS, None)

                # ----------------------------------------------------------------
                # Action 4: P6 Consensus Vetting
                # ----------------------------------------------------------------
                log_action("P6_START", {"attempt": self.refinement_count})

                p6_result = self.knowledge.query_consensus(
                    pitch=pitch_draft.content,
                    guidelines=self._get_brand_guidelines()
                )

                # ----------------------------------------------------------------
                # Action 5: ZSE Vetting Gate
                # ----------------------------------------------------------------
                if p6_result["status"] == "FAIL":
                    logger.warning(f"VET_FAIL: P6 Compliance Failure - {p6_result['reason']}")
                    log_action("P6_COMPLIANCE_FAIL", {"reason": p6_result["reason"]})

                    # Trigger P10 Shadow Mode
                    self.refinement_count += 1
                    log_action("P10_START", {"attempt": self.refinement_count})

                    shadow_result = self.shadow_mode.refine_pitch(
                        pitch_draft,
                        p6_result["reason"]
                    )

                    # Apply refinement
                    pitch_draft = self.shadow_mode.apply_refinement(
                        pitch_draft,
                        shadow_result
                    )

                    # Log and restart loop
                    log_action("P10_SHADOW_REFINEMENT", {
                        "attempt": self.refinement_count,
                        "improvements": shadow_result.improvements
                    })

                    self.knowledge.add_observations({
                        "event": "P10_SHADOW_REFINEMENT",
                        "attempt": self.refinement_count
                    })

                    continue  # Restart ZSE loop

                # ----------------------------------------------------------------
                # Action 6: Finalization (ZSE Success Path)
                # ----------------------------------------------------------------
                log_action("ZSE_SUCCESS")

                # Execute side effect (send email)
                send_result = send_email(
                    to=contact_email,
                    subject=pitch_draft.subject,
                    body=pitch_draft.content,
                    send_time=optimal_send_time,
                    dry_run=self.dry_run
                )

                # ----------------------------------------------------------------
                # Action 7: Final P5 and L5 Logging
                # ----------------------------------------------------------------
                log_action("SEND_EMAIL_SUCCESS", {
                    "to": contact_email,
                    "subject": pitch_draft.subject,
                    "dry_run": self.dry_run
                })

                self.knowledge.add_observations({
                    "event": "OUTREACH_COMPLETE",
                    "status": "SENT" if not self.dry_run else "DRY_RUN",
                    "refinement_count": self.refinement_count
                })

                return (ExitReason.ZSE_SUCCESS, {
                    "email_result": send_result,
                    "pitch": pitch_draft,
                    "refinements": self.refinement_count
                })

        except Exception as e:
            logger.error(f"CRITICAL_ERROR: {e}")
            log_action("CRITICAL_ERROR", {"error": str(e)})
            return (ExitReason.CRITICAL_ERROR, None)

    def _fetch_company_context(self, company_url: str) -> Dict[str, Any]:
        """Fetch company context with P8 enforcement."""
        # Use networking utility with built-in P8 filter
        result = self.networking.fetch_url(company_url)

        if result["status"] == "blocked":
            raise Exception(f"P8 Block: {result['reason']}")

        # Parse mock content
        return {
            "company_url": company_url,
            "company_name": "TechCorp",  # Extract from real content
            "recent_news": "launched new AI platform",
            "company_focus": "artificial intelligence",
            "my_name": "John Doe",
            "my_title": "AI Engineer",
            "my_field": "machine learning",
            "my_contact": "john.doe@email.com"
        }

    def _calculate_optimal_time(self, contact_context) -> str:
        """Calculate optimal send time (L4 utility)."""
        # Mock implementation - would use real timezone conversion
        timezone = contact_context.user_profile.get("timezone", "UTC") if contact_context.user_profile else "UTC"
        optimal_time = datetime.now().strftime("%Y-%m-%d %H:00")
        logger.info(f"L4_TIME: Optimal send time calculated for {timezone}: {optimal_time}")
        log_action("L4_TIME", {"timezone": timezone, "send_time": optimal_time})
        return optimal_time

    def _get_brand_guidelines(self) -> Dict[str, Any]:
        """Get brand style guidelines for P6 consensus."""
        return {
            "tone": "professional",
            "prohibited_words": ["amazing", "incredible", "revolutionary", "guarantee"],
            "max_exclamation": 1,
            "min_length": 100,
            "max_length": 200
        }


# Main execution for testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/outreach_engine_zse.log"),
            logging.StreamHandler()
        ]
    )

    # Test execution
    engine = OutreachEngineZSE(output_dir="output", dry_run=True)
    exit_reason, result = engine.execute_outreach(
        company_url="https://linkedin.com/company/techcorp",
        contact_email="hiring@techcorp.com"
    )

    print(f"\nExecution complete: {exit_reason.value}")
    if result:
        print(f"Refinements: {result.get('refinements', 0)}")
        print(f"Email status: {result['email_result']['status']}")