"""K.1 Routing Agent - Archetype Classification and Route Selection.

This agent implements the mandatory 7 Prompt Shell Entrance Gates, classifies
the recipient archetype using CXO precedence rules, and selects the correct
route (INMAIL vs CONNECTION_REQ) with premium routing validation.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from runtime.shared.agent_base import Agent, ReasoningConfig


logger = logging.getLogger(__name__)


@dataclass
class ArchetypeClassificationResult:
    """Result of archetype classification."""
    archetype: str  # C_LEVEL, EXECUTIVE, SENIOR_TA, RECRUITER
    confidence: float
    matched_tokens: List[str]
    cxo_precedence_triggered: bool
    manual_override_required: bool


@dataclass
class RouteSelectionResult:
    """Result of route selection."""
    route: str  # INMAIL, CONNECTION_REQ, SHORT_NEW, FOLLOW_UP
    premium_available: bool
    premium_routing_mismatch: bool
    blocking_reason: Optional[str] = None


@dataclass
class K1Output:
    """K.1 routing agent output."""
    archetype: ArchetypeClassificationResult
    route: RouteSelectionResult
    entrance_gates_passed: List[str]
    metadata: Dict[str, Any]


class K1_RoutingAgent(Agent):
    """K.1 specialist agent for routing and archetype classification.

    This agent executes the mandatory 7 Prompt Shell Entrance Gates:
    1. Lifecycle determination (NEW vs EXISTING)
    2. Contact block validation (Name, Title, About)
    3A. Premium InMail availability check
    3B. Route override check
    4. Archetype classification with CXO precedence
    5. Route selection validation
    6. Premium routing mismatch detection
    7. Final gate approval
    """

    def __init__(
        self,
        config: ReasoningConfig,
        archetype_tokens: Dict[str, List[str]],
        cxo_precedence_tokens: List[str],
        route_configs: Dict[str, Any],
    ):
        """Initialize K.1 routing agent.

        Args:
            config: Reasoning configuration
            archetype_tokens: Token lists for each archetype
            cxo_precedence_tokens: CXO-level tokens for precedence rule
            route_configs: Route configuration objects
        """
        super().__init__(config, k_node_id="K.1", element="Routing & Classification")

        self.archetype_tokens = archetype_tokens
        self.cxo_precedence_tokens = cxo_precedence_tokens
        self.route_configs = route_configs

        logger.info("K.1 Routing Agent initialized with CXO precedence rule")

    async def execute(self, context: Dict[str, Any]) -> K1Output:
        """Execute K.1 routing and classification.

        Args:
            context: Execution context with:
                - linkedin_url: str
                - contact_name: str
                - contact_title: str
                - contact_about: Optional[str]
                - lifecycle: str (NEW or EXISTING)
                - premium_available: bool
                - route_override: Optional[str]

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
            f"CXO_precedence={archetype_result.cxo_precedence_triggered})"
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
            logger.critical(
                f"Gate 6: PREMIUM ROUTING MISMATCH BLOCKER - {route_result.blocking_reason}"
            )
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
                "k_node_id": self.k_node_id,
                "lifecycle": lifecycle,
                "contact_name": contact_name,
                "contact_title": contact_title,
            },
        )

        logger.info(
            f"K.1 routing complete: {archetype_result.archetype} → {route_result.route}"
        )

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
        route_override: Optional[str],
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
