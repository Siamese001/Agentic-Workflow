"""[SSOT] Logic Node for K1 Routing.
Moved from engines/k1_routing_agent.py to comply with Blueprint Depth-2 Structure.
This is a deterministic utility, NOT an autonomous agent.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


@dataclass
class ArchetypeClassificationResult:
    """Result of archetype classification."""

    archetype: str  # C_LEVEL, EXECUTIVE, SENIOR_TA, RECRUITER
    confidence: float
    matched_tokens: list[str]
    cxo_precedence_triggered: bool
    manual_override_required: bool


@dataclass
class RouteSelectionResult:
    """Result of route selection."""

    route: str  # INMAIL, CONNECTION_REQ, SHORT_NEW, FOLLOW_UP
    premium_available: bool
    premium_routing_mismatch: bool
    blocking_reason: str | None = None


@dataclass
class K1Output:
    """K.1 routing node output."""

    archetype: ArchetypeClassificationResult
    route: RouteSelectionResult
    entrance_gates_passed: list[str]
    metadata: dict[str, Any]


class K1Router:
    """
    Handles state transitions and routing logic for the Profile Analysis workflow.

    This is a deterministic logic node that implements the 7 Prompt Shell Entrance Gates,
    archetype classification with CXO precedence, and route selection with premium
    routing validation. It is NOT an autonomous agent.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}

        # Default configuration
        self.archetype_tokens: dict[str, list[str]] = self.config.get(
            "archetype_tokens",
            {
                "C_LEVEL": ["CEO", "CTO", "CFO", "CIO", "COO", "PRESIDENT", "DIRECTOR"],
                "EXECUTIVE": ["VP", "VICE PRESIDENT", "SENIOR", "LEAD", "HEAD", "MANAGER"],
                "SENIOR_TA": ["SENIOR", "PRINCIPAL", "STAFF", "ENGINEER", "DEVELOPER"],
                "RECRUITER": ["RECRUITER", "TALENT", "HR", "SOURCING"],
            },
        )
        self.cxo_precedence_tokens: list[str] = self.config.get(
            "cxo_precedence_tokens",
            ["CEO", "CTO", "CFO", "CIO", "COO", "PRESIDENT", "FOUNDER", "CHIEF"],
        )
        self.route_configs: dict[str, Any] = self.config.get("route_configs", {})

    def __call__(self, state: dict[str, Any]) -> K1Output:
        """
        Executes routing logic using functor pattern for graph compatibility.

        Args:
            state (dict): The current workflow state containing:
                - linkedin_url: str
                - contact_name: str
                - contact_title: str
                - contact_about: Optional[str]
                - lifecycle: str (NEW or EXISTING)
                - premium_available: bool
                - route_override: Optional[str]

        Returns:
            K1Output: Complete routing output with archetype and route

        Raises:
            ValueError: If routing state is empty or validation fails
        """
        if not state:
            raise ValueError("Routing state cannot be empty")

        return self.execute_routing(state)

    def determine_next_hop(self, state: dict[str, Any]) -> str:
        """
        Determines the next hop identifier for workflow routing.

        Args:
            state: Current workflow state

        Returns:
            str: Next hop identifier
        """
        if not state:
            raise ValueError("Routing state cannot be empty")

        # Basic routing logic - can be extended based on state
        result = self.execute_routing(state)
        return f"route_{result.route.lower()}"

    def execute_routing(self, context: dict[str, Any]) -> K1Output:
        """Execute K.1 routing and classification.

        Args:
            context: Execution context with routing parameters

        Returns:
            K1Output with archetype and route
        """
        logger.info("Executing K.1 routing and classification")

        entrance_gates_passed = []

        # Gate 1: Lifecycle determination
        lifecycle = context.get("lifecycle", "NEW")
        entrance_gates_passed.append("GATE_1_LIFECYCLE_DETERMINED")
        logger.info(f"Gate 1: Lifecycle = {lifecycle}")

        # Gate 2: Contact block validation
        contact_name = context.get("contact_name")
        contact_title = context.get("contact_title")
        contact_about = context.get("contact_about", "")

        if not contact_name or not contact_title:
            raise ValueError("GATE_2_FAILED: Contact name and title are required")

        entrance_gates_passed.append("GATE_2_CONTACT_BLOCK_VALIDATED")
        logger.info(f"Gate 2: Contact validated - {contact_name}, {contact_title}")

        # Gate 3A: Premium InMail availability check
        premium_available = context.get("premium_available", False)
        entrance_gates_passed.append("GATE_3A_PREMIUM_AVAILABILITY_CHECKED")
        logger.info(f"Gate 3A: Premium InMail = {premium_available}")

        # Gate 3B: Route override check
        route_override = context.get("route_override")
        if route_override:
            entrance_gates_passed.append("GATE_3B_ROUTE_OVERRIDE_DETECTED")
            logger.info(f"Gate 3B: Route override = {route_override}")

        # Gate 4: Archetype classification with CXO precedence
        archetype_result = self._classify_archetype(contact_title, contact_about)
        entrance_gates_passed.append("GATE_4_ARCHETYPE_CLASSIFIED")
        logger.info(
            f"Gate 4: Archetype = {archetype_result.archetype} "
            f"(confidence={archetype_result.confidence:.2f}, "
            f"CXO_precedence={archetype_result.cxo_precedence_triggered})",
        )

        # Gate 5: Route selection
        route_result = self._select_route(
            lifecycle=lifecycle,
            premium_available=premium_available,
            route_override=route_override,
            archetype=archetype_result.archetype,
        )
        entrance_gates_passed.append("GATE_5_ROUTE_SELECTED")
        logger.info(f"Gate 5: Route = {route_result.route}")

        # Gate 6: Premium routing mismatch detection (CRITICAL)
        if route_result.premium_routing_mismatch:
            entrance_gates_passed.append("GATE_6_PREMIUM_MISMATCH_DETECTED")
            logger.critical(f"Gate 6: PREMIUM ROUTING MISMATCH BLOCKER - {route_result.blocking_reason}")
            raise ValueError(f"GATE_6_BLOCKED: {route_result.blocking_reason}")

        entrance_gates_passed.append("GATE_6_PREMIUM_ROUTING_VALIDATED")
        logger.info("Gate 6: Premium routing validated")

        # Gate 7: Final gate approval
        entrance_gates_passed.append("GATE_7_FINAL_APPROVAL")
        logger.info("Gate 7: All entrance gates passed")

        # Build output
        output = K1Output(
            archetype=archetype_result,
            route=route_result,
            entrance_gates_passed=entrance_gates_passed,
            metadata={
                "router_id": "K1Router",
                "lifecycle": lifecycle,
                "contact_name": contact_name,
                "contact_title": contact_title,
            },
        )

        logger.info(f"K.1 routing complete: {archetype_result.archetype} → {route_result.route}")

        return output

    def _classify_archetype(
        self,
        title: str,
        about: str = "",
    ) -> ArchetypeClassificationResult:
        """Classify recipient archetype with CXO precedence rule.

        Classification order (from LinkedInCanonical v2.90):
        1. Check for CXO-level tokens FIRST (immediate C_LEVEL assignment)
        2. Else check Executive tokens
        3. Else check TA tokens
        4. Else default to EXECUTIVE

        Args:
            title: Recipient job title
            about: Recipient about section

        Returns:
            ArchetypeClassificationResult
        """
        combined_text = f"{title} {about}".upper()
        matched_tokens = []

        # Step 1: CXO Precedence Rule (CRITICAL)
        for token in self.cxo_precedence_tokens:
            if token.upper() in combined_text:
                matched_tokens.append(token)
                logger.info(f"CXO precedence triggered: {token}")
                return ArchetypeClassificationResult(
                    archetype="C_LEVEL",
                    confidence=1.0,  # CXO precedence = 100% confidence
                    matched_tokens=matched_tokens,
                    cxo_precedence_triggered=True,
                    manual_override_required=False,
                )

        # Step 2: C_LEVEL tokens (non-CXO)
        for token in self.archetype_tokens.get("C_LEVEL", []):
            if token.upper() in combined_text:
                matched_tokens.append(token)

        if matched_tokens:
            return ArchetypeClassificationResult(
                archetype="C_LEVEL",
                confidence=0.95,
                matched_tokens=matched_tokens,
                cxo_precedence_triggered=False,
                manual_override_required=False,
            )

        # Step 3: EXECUTIVE tokens
        matched_tokens = []
        for token in self.archetype_tokens.get("EXECUTIVE", []):
            if token.upper() in combined_text:
                matched_tokens.append(token)

        if matched_tokens:
            return ArchetypeClassificationResult(
                archetype="EXECUTIVE",
                confidence=0.90,
                matched_tokens=matched_tokens,
                cxo_precedence_triggered=False,
                manual_override_required=False,
            )

        # Step 4: SENIOR_TA tokens
        matched_tokens = []
        for token in self.archetype_tokens.get("SENIOR_TA", []):
            if token.upper() in combined_text:
                matched_tokens.append(token)

        if matched_tokens:
            return ArchetypeClassificationResult(
                archetype="SENIOR_TA",
                confidence=0.90,
                matched_tokens=matched_tokens,
                cxo_precedence_triggered=False,
                manual_override_required=False,
            )

        # Step 5: RECRUITER tokens
        matched_tokens = []
        for token in self.archetype_tokens.get("RECRUITER", []):
            if token.upper() in combined_text:
                matched_tokens.append(token)

        if matched_tokens:
            return ArchetypeClassificationResult(
                archetype="RECRUITER",
                confidence=0.85,
                matched_tokens=matched_tokens,
                cxo_precedence_triggered=False,
                manual_override_required=False,
            )

        # Default: EXECUTIVE with low confidence (manual override required)
        logger.warning("No archetype tokens matched - defaulting to EXECUTIVE")
        return ArchetypeClassificationResult(
            archetype="EXECUTIVE",
            confidence=0.50,
            matched_tokens=[],
            cxo_precedence_triggered=False,
            manual_override_required=True,  # Confidence < 0.85
        )

    def _select_route(
        self,
        lifecycle: str,
        premium_available: bool,
        route_override: str | None,
        archetype: str,
    ) -> RouteSelectionResult:
        """Select message route with premium routing validation.

        Args:
            lifecycle: NEW or EXISTING
            premium_available: Premium InMail availability
            route_override: Manual route override
            archetype: Classified archetype

        Returns:
            RouteSelectionResult with mismatch detection
        """
        # Check for route override
        if route_override:
            selected_route = route_override

            # CRITICAL: Premium routing mismatch detection
            if selected_route == "INMAIL" and not premium_available:
                return RouteSelectionResult(
                    route=selected_route,
                    premium_available=premium_available,
                    premium_routing_mismatch=True,
                    blocking_reason=(
                        "INMAIL route selected but Premium InMail not available. "
                        "Operator response to Gate 3A conflicts with route selection."
                    ),
                )

            return RouteSelectionResult(
                route=selected_route,
                premium_available=premium_available,
                premium_routing_mismatch=False,
            )

        # Default routing logic
        if lifecycle == "EXISTING":
            selected_route = "FOLLOW_UP"
        elif premium_available:
            selected_route = "INMAIL"
        else:
            selected_route = "CONNECTION_REQ"

        return RouteSelectionResult(
            route=selected_route,
            premium_available=premium_available,
            premium_routing_mismatch=False,
        )
