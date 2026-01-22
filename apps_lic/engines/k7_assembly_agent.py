"""K.7 Assembly Agent - Final Message Assembly with Signature Immutability.

This agent assembles the final message with strict signature formatting,
header order enforcement, and final QA block ordering.
"""

import logging


logger = logging.getLogger(__name__)


@dataclass
class K7Output:
    """K.7 assembly output."""

    final_message: str
    header_block: str
    body_block: str
    signature_block: str
    total_chars: int
    qa_blocks_order: list[str]
    metadata: dict[str, Any]


# Signature immutability template (from LinkedInCanonical v2.90)
SIGNATURE_TEMPLATE = """Regards,
{first_name}

{linkedin_url}"""


class K7_AssemblyAgent(Agent):
    """K.7 specialist agent for final message assembly.

    This agent assembles the final message with:
    - Exact header order (URL, Message Type, Subject)
    - Single fenced message body
    - Signature immutability (exact 4-line block)
    - QA blocks in mandatory order
    - No hard-banned prefixes/headers
    """

    def __init__(
        self,
        config: ReasoningConfig,
        route: str,
        archetype: str,
    ):
        """Initialize K.7 assembly agent.

        Args:
            config: Reasoning configuration
            route: Message route
            archetype: Recipient archetype
        """
        super().__init__(config, k_node_id="K.7", element="Final Assembly")

        self.route = route
        self.archetype = archetype

        logger.info(f"K.7 Assembly Agent initialized: route={route}, archetype={archetype}")

    async def execute(self, context: dict[str, Any]) -> K7Output:
        """Execute K.7 final assembly.

        Args:
            context: Execution context with:
                - linkedin_url: str
                - message_type: str
                - subject: Optional[str]
                - message_body: str (from K.3)
                - cta: str (from K.5)
                - sender_first_name: str
                - sender_linkedin_url: str
                - qa_blocks: Dict[str, str]

        Returns:
            K7Output with final assembled message
        """
        logger.info("Executing K.7 final message assembly")

        # Extract context
        linkedin_url = context.get("linkedin_url", "")
        message_type = context.get("message_type", self.archetype)
        subject = context.get("subject")
        message_body = context.get("message_body", "")
        cta = context.get("cta", "")
        sender_first_name = context.get("sender_first_name", "")
        sender_linkedin_url = context.get("sender_linkedin_url", "")
        qa_blocks = context.get("qa_blocks", {})

        # Assemble header block
        header_block = self._assemble_header(linkedin_url, message_type, subject)

        # Assemble body block
        body_block = self._assemble_body(message_body, cta)

        # Assemble signature block (IMMUTABLE)
        signature_block = self._assemble_signature(sender_first_name, sender_linkedin_url)

        # Assemble QA blocks in mandatory order
        qa_blocks_ordered = self._assemble_qa_blocks(qa_blocks)

        # Assemble final message
        final_message = self._assemble_final_message(
            header_block,
            body_block,
            signature_block,
            qa_blocks_ordered,
        )

        # Calculate metrics
        total_chars = len(final_message)

        # Build output
        output = K7Output(
            final_message=final_message,
            header_block=header_block,
            body_block=body_block,
            signature_block=signature_block,
            total_chars=total_chars,
            qa_blocks_order=list(qa_blocks_ordered.keys()),
            metadata={
                "k_node_id": self.k_node_id,
                "route": self.route,
                "archetype": self.archetype,
            },
        )

        logger.info(f"K.7 assembly complete: {total_chars} total chars")

        return output

    def _assemble_header(
        self,
        linkedin_url: str,
        message_type: str,
        subject: str | None,
    ) -> str:
        """Assemble header block in exact order.

        Order (from LinkedInCanonical v2.90):
        1. LinkedIn URL (plain, unfenced)
        2. Message Type (plain)
        3. Subject (plain, no "Subject:" prefix) - only if route requires

        Args:
            linkedin_url: Recipient LinkedIn URL
            message_type: Message type
            subject: Subject line (optional)

        Returns:
            Formatted header block
        """
        header_lines = [
            linkedin_url,
            message_type,
        ]

        if subject and self.route not in ["CONNECTION_REQ", "SHORT_NEW"]:
            header_lines.append(subject)

        return "\n".join(header_lines)

    def _assemble_body(self, message_body: str, cta: str) -> str:
        """Assemble body block with CTA.

        Args:
            message_body: Message body from K.3
            cta: CTA from K.5

        Returns:
            Formatted body block
        """
        # Ensure body ends with CTA
        if not message_body.strip().endswith(cta.strip()):
            body = f"{message_body.strip()}\n\n{cta.strip()}"
        else:
            body = message_body.strip()

        return body

    def _assemble_signature(
        self,
        first_name: str,
        linkedin_url: str,
    ) -> str:
        """Assemble signature block with IMMUTABILITY enforcement.

        Signature format (EXACT 4-line block):
        Line 1: Regards,
        Line 2: {first_name}
        Line 3: (blank)
        Line 4: {linkedin_url}

        Args:
            first_name: Sender first name
            linkedin_url: Sender LinkedIn URL

        Returns:
            Formatted signature block
        """
        signature = SIGNATURE_TEMPLATE.format(
            first_name=first_name,
            linkedin_url=linkedin_url,
        )

        # Validate signature immutability
        lines = signature.split("\n")
        if len(lines) != 4:
            logger.error(f"Signature immutability violation: {len(lines)} lines (expected 4)")

        if not lines[0].strip() == "Regards,":
            logger.error(f"Signature line 1 violation: '{lines[0]}' (expected 'Regards,')")

        return signature

    def _assemble_qa_blocks(self, qa_blocks: dict[str, str]) -> dict[str, str]:
        """Assemble QA blocks in mandatory order.

        Mandatory order (from LinkedInCanonical v2.90):
        1. LinkedIn QA Grid
        2. AI Filter Canonical
        3. Message-Specific RAG QA Table
        4. Evidence Pack

        Args:
            qa_blocks: QA blocks dictionary

        Returns:
            Ordered QA blocks dictionary
        """
        mandatory_order = [
            "LinkedIn QA Grid",
            "AI Filter Canonical",
            "Message-Specific RAG QA Table",
            "Evidence Pack",
        ]

        ordered_blocks = {}
        for block_name in mandatory_order:
            if block_name in qa_blocks:
                ordered_blocks[block_name] = qa_blocks[block_name]

        return ordered_blocks

    def _assemble_final_message(
        self,
        header_block: str,
        body_block: str,
        signature_block: str,
        qa_blocks: dict[str, str],
    ) -> str:
        """Assemble final message with all components.

        Args:
            header_block: Header block
            body_block: Body block
            signature_block: Signature block
            qa_blocks: QA blocks in order

        Returns:
            Final assembled message
        """
        # Assemble message components
        message_parts = [
            header_block,
            "",  # Blank line after header
            "```",  # Fence start
            body_block,
            "",  # Blank line before signature
            signature_block,
            "```",  # Fence end
        ]

        # Add QA blocks
        for block_name, block_content in qa_blocks.items():
            message_parts.append("")
            message_parts.append(f"## {block_name}")
            message_parts.append(block_content)

        final_message = "\n".join(message_parts)

        # Validate no hard-banned prefixes
        self._validate_no_banned_content(final_message)

        return final_message

    def _validate_no_banned_content(self, message: str) -> None:
        """Validate message contains no hard-banned prefixes/headers.

        Hard-banned content:
        - Audit Metadata
        - Raw SHA256
        - Internal system headers

        Args:
            message: Final message
        """
        banned_patterns = [
            "Audit Metadata",
            "SHA256:",
            "INTERNAL:",
            "DEBUG:",
            "SYSTEM:",
        ]

        for pattern in banned_patterns:
            if pattern in message:
                logger.error(f"Hard-banned content detected: {pattern}")