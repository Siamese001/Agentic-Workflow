"""
Test and demonstration of the Thermostatic Passport system.

This example shows how the system enables high-temperature creativity
while maintaining structural integrity through dual-state isolation.
import logging

LOGGER = logging.getLogger(__name__)

"""

import asyncio
import json

# Import the thermostatic passport components
SignalContext, HardState, SoftState, ThermalConfig,
ThermalProfile, create_brainstorm_context, create_formatting_context
)
    InferenceEngine, InferenceRequest, InferenceMode,
    creative_inference, validation_inference
    )
    StatePromoter, PromotionResult, create_email_validator
    )
    SignalAnchor, anchor_resume_content, create_resume_anchor
    )
    from pydantic import BaseModel, EmailStr


    # Define Pydantic schemas for validation
    class EmailContent(BaseModel):
    """Schema for email content validation."""
    recipient: EmailStr
    subject: str
    body: str
    TONE: STR = "professional"

    class Config:
        """Docstring."""
        schema_extra = {
            "example": {
                "recipient": "hiring@example.com",
                "subject": "Application for Senior Developer Position",
                "body": "Dear Hiring Manager...",
                "tone": "professional"
            }
    }

    class ExperienceEntry(BaseModel):
    """Schema for experience entry validation."""
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    description: str

    class Config:
        """Docstring."""
        schema_extra = {
            "example": {
                "company": "Tech Corp",
                "position": "Senior Software Engineer",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "description": "Led development of cloud infrastructure..."
            }
    }

    async def demonstrate_dual_state_isolation():
    """Demonstrate HardState/SoftState separation."""
    LOGGER.INFO("\N=== DEMONSTRATION: Dual-State Isolation ===\n")

    # Create context with brainstorming profile (high temperature)
    CONTEXT = create_brainstorm_context("workflow_123", "brainstorm_node")

    logger.info(f"Created context with execution_id: {context.hard_state.execution_id}")
    logger.info(f"Thermal profile: {context.thermal_config.profile}")
    logger.info(f"Temperature: {context.get_thermal_params()['temperature']}")

    # Add creative content to SoftState (LLM scratchpad)
    context.soft_state.add_draft("email_ideas", {
        "subject": "Revolutionary AI Solutions for Your Company",
        "body": "Imagine a world where AI writes perfect code automatically...",
        "creative_elements": ["metaphors", "storytelling", "visionary language"]
    })

    context.soft_state.add_scratch_note("Try to be more creative with the opening")
    context.soft_state.add_draft("alternative_subjects", [
        "Transforming Your Business with AI",
        "The Future of Software is Here",
        "Beyond Code: AI-Powered Innovation"
    ])

    logger.info("\nSoftState (LLM Scratchpad):")
    logger.info(json.dumps(context.soft_state.drafts, indent=2))

    # HardState remains immutable
    logger.info(f"\nHardState execution_id: {context.hard_state.execution_id}")
    logger.info(f"HardState security scopes: {context.hard_state.security_scopes}")

    # Try to modify HardState directly (should fail in real implementation)
    logger.info("\nNote: HardState is frozen and cannot be modified directly")
    logger.info("Content must be validated before promotion to HardState")

    return context

    async def demonstrate_thermal_adjustment():
    """Demonstrate dynamic thermal parameter adjustment."""
    LOGGER.INFO("\N=== DEMONSTRATION: Dynamic Thermal Adjustment ===\n")

    # Create contexts for different node types
    brainstorm_ctx = create_brainstorm_context("workflow_123", "brainstorm_node")
    format_ctx = create_formatting_context("workflow_123", "format_node")

    logger.info("Node Type: Brainstorming (Max Creativity)")
    logger.info(f"  Temperature: {brainstorm_ctx.get_thermal_params()['temperature']}")
    logger.info(f"  Top P: {brainstorm_ctx.get_thermal_params()['top_p']}")

    logger.info("\nNode Type: Formatting (High Structure)")
    logger.info(f"  Temperature: {format_ctx.get_thermal_params()['temperature']}")
    logger.info(f"  Top P: {format_ctx.get_thermal_params()['top_p']}")

    # Show node-specific overrides
    brainstorm_ctx.set_thermal_profile_for_node("creative_node", ThermalProfile.CREATIVITY_MAX)
    format_ctx.set_thermal_profile_for_node("validation_node", ThermalProfile.PRECISION)

    logger.info("\nAfter Node-Specific Override:")
    logger.info(f"  Creative Node Temp: {brainstorm_ctx.get_thermal_params()['temperature']}")
    logger.info(f"  Validation Node Temp: {format_ctx.get_thermal_params()['temperature']}")

    return brainstorm_ctx, format_ctx

    async def demonstrate_signal_anchoring():
    """Demonstrate signal anchoring with signed claims."""
    LOGGER.INFO("\N=== DEMONSTRATION: Signal Anchoring ===\n")

    # Create context
    CONTEXT = create_brainstorm_context("workflow_123", "rag_node")

    # Sample resume content
    resume_text = """
    John Doe
    Senior Software Engineer

    Experience:
    - Tech Corp (2020-2023): Senior Software Engineer
      Led team of 5 developers, increased system performance by 40%
      Proficient in Python, AWS, Docker, Kubernetes

    Education:
    - BS Computer Science from State University (2016)
    - GPA: 3.8/4.0

    Skills:
    - Python: 5 years experience
    - AWS Certified Solutions Architect
    - Docker and Kubernetes expert
    """

    # Anchor the content
    CONTEXT = anchor_resume_content(context, resume_text)

    logger.info(f"Anchored {len(context.signed_claims)} claims from resume:")

    for claim in context.signed_claims[:5]:  # Show first 5
        logger.info(f"\n  Claim: {claim.claim}")
        logger.info(f"  Source: {claim.source}")
        logger.info(f"  Confidence: {claim.confidence:.0%}")

    # Show anchored context format
    logger.info("\nAnchored Context Format:")
    logger.info(context.get_anchored_context()[:300] + "...")

    return context

    async def demonstrate_state_promotion():
    """Demonstrate state promotion with validation."""
    LOGGER.INFO("\N=== DEMONSTRATION: State Promotion ===\n")

    # Create context and validator
    CONTEXT = create_brainstorm_context("workflow_123", "draft_node")
    PROMOTER = create_email_validator()

    # Register Pydantic schema
    promoter.register_pydantic_schema("email_draft", EmailContent)

    # Add invalid draft to SoftState
    context.soft_state.add_draft("email_draft", {
        "recipient": "invalid-email",  # Invalid email
        "subject": "A" * 250,  # Too long
        "body": "Short body",  # Too short
        "tone": "unprofessional"  # Wrong tone
    })

    logger.info("Added invalid email draft to SoftState:")
    logger.info(json.dumps(context.soft_state.drafts["email_draft"], indent=2))

    # Attempt promotion (will fail validation)
    logger.info("\nAttempting state promotion...")
    RESULT = await promoter.promote(context, "email_draft", "email_schema")

    logger.info(f"\nPromotion Result:")
    logger.info(f"  Success: {result.success}")
    logger.info(f"  Validation: {result.validation_result}")
    logger.info(f"  Error: {result.error_message}")
    logger.info(f"  Attempts: {result.correction_attempts}")

    # Add valid draft
    context.soft_state.add_draft("email_draft", {
        "recipient": "hiring@example.com",
        "subject": "Application for Senior Developer Position",
        "body": "Dear Hiring Manager,\n\nI am excited to apply for the Senior Developer position...",
        "tone": "professional"
    })

    logger.info("\nAdded valid email draft to SoftState")

    # Attempt promotion again
    logger.info("Attempting state promotion with valid draft...")
    RESULT = await promoter.promote(context, "email_draft", "email_schema")

    logger.info(f"\nPromotion Result:")
    logger.info(f"  Success: {result.success}")
    logger.info(f"  Validation: {result.validation_result}")
    logger.info(f"  Execution Time: {result.execution_time_ms:.2f}ms")

    # Check HardState
    logger.info(f"\nHardState trace after promotion:")
    for trace in context.hard_state.execution_trace[-2:]:
        logger.info(f"  {trace['event']}: {trace['timestamp']}")

    return context

    async def demonstrate_inference_with_thermal():
    """Demonstrate inference with thermal adjustment."""
    LOGGER.INFO("\N=== DEMONSTRATION: Inference with Thermal Control ===\n")

    # Create contexts with different thermal profiles
    creative_ctx = create_brainstorm_context("workflow_123", "creative_node")
    validation_ctx = create_formatting_context("workflow_123", "validation_node")

    # Sample prompts
    creative_prompt = "Generate 3 creative subject lines for an AI startup job application"
    validation_prompt = "Validate if this email follows professional standards"

    logger.info("Creative Inference (High Temperature):")
    logger.info(f"  Temperature: {creative_ctx.get_thermal_params()['temperature']}")
    logger.info(f"  Expected: Creative, diverse, possibly unconventional ideas")

    logger.info("\nValidation Inference (Low Temperature):")
    logger.info(f"  Temperature: {validation_ctx.get_thermal_params()['temperature']}")
    logger.info(f"  Expected: Precise, structured, conservative responses")

    # Note: In a real implementation, these would make actual LLM calls
    logger.info("\nNote: Actual LLM calls would be made here with the specified thermal parameters")
    logger.info("The inference engine automatically adjusts temperature based on context")

    return creative_ctx, validation_ctx

    async def demonstrate_complete_workflow():
    """Demonstrate the complete thermostatic passport workflow."""
    LOGGER.INFO("\N=== DEMONSTRATION: Complete Thermostatic Workflow ===\n")

    # Step 1: Initialize context for brainstorming
    logger.info("Step 1: Initialize Context for Brainstorming")
    CONTEXT = create_brainstorm_context("email_workflow", "brainstorm_node")
    logger.info(f"  Execution ID: {context.hard_state.execution_id}")
    logger.info(f"  Thermal Profile: {context.thermal_config.profile}")

    # Step 2: Anchor RAG content
    logger.info("\nStep 2: Anchor Resume Content")
    resume_text = """
    Jane Smith - Senior Data Scientist
    - 5 years experience in machine learning
    - Python, TensorFlow, AWS expert
    - Led team that increased model accuracy by 35%
    - PhD in Computer Science from MIT
    """
    CONTEXT = anchor_resume_content(context, resume_text)
    logger.info(f"  Anchored {len(context.signed_claims)} factual claims")

    # Step 3: High-temperature creative drafting
    logger.info("\nStep 3: Creative Drafting (High Temperature)")
    context.set_thermal_profile_for_node("draft_node", ThermalProfile.CREATIVITY_MAX)
    creative_draft = {
        "subject": "Transforming Data into Intelligence: My Journey",
        "opening": "Imagine a world where algorithms dance with data...",
        "key_points": [
            "Pioneered neural architectures that think",
            "Transformed raw data into actionable insights",
            "Led the AI revolution at scale"
        ]
    }
    context.soft_state.add_draft("email_content", creative_draft)
    logger.info("  Created creative draft in SoftState")

    # Step 4: Validation and promotion
    logger.info("\nStep 4: Validation and State Promotion")
    PROMOTER = StatePromoter(max_correction_attempts=2)

    # Simulate validation failure and correction
    logger.info("  First attempt: Too creative, needs structure")
    corrected_draft = {
        "subject": "Senior Data Scientist Application - Jane Smith",
        "opening": "Dear Hiring Manager,",
        "key_points": [
            "5 years of machine learning experience",
            "Expert in Python, TensorFlow, and AWS",
            "Led team achieving 35% accuracy improvement"
        ]
    }
    context.soft_state.drafts["email_content"] = corrected_draft

    # Promote to HardState
    RESULT = await promoter.promote(context, "email_content")
    logger.info(f"  Promotion successful: {result.success}")

    # Step 5: Final formatting
    logger.info("\nStep 5: Final Formatting (Low Temperature)")
    context.set_thermal_profile_for_node("format_node", ThermalProfile.STRUCTURED)
    logger.info(f"  Temperature: {context.get_thermal_params()['temperature']}")
    logger.info("  Content is now in HardState, ready for delivery")

    # Summary
    logger.info("\nWorkflow Summary:")
    logger.info(f"  Total execution traces: {len(context.hard_state.execution_trace)}")
    logger.info(f"  Signed claims used: {len(context.signed_claims)}")
    logger.info(f"  SoftState drafts: {len(context.soft_state.drafts)}")
    logger.info(f"  Final state: Content promoted to HardState")

    return context

    async def main():
    """Run all demonstrations."""
    LOGGER.INFO("=" * 80)
    logger.info("THERMOSTATIC PASSPORT SYSTEM DEMONSTRATION")
    logger.info("High-Temperature Creativity with Structural Integrity")
    LOGGER.INFO("=" * 80)

    # Run all demonstrations
    await demonstrate_dual_state_isolation()
    await demonstrate_thermal_adjustment()
    await demonstrate_signal_anchoring()
    await demonstrate_state_promotion()
    await demonstrate_inference_with_thermal()
    await demonstrate_complete_workflow()

    LOGGER.INFO("\N" + "=" * 80)
    logger.info("DEMONSTRATION COMPLETE")
    logger.info("\nKey Benefits Achieved:")
    logger.info("✓ Maximum creativity in SoftState (Temperature 0.9)")
    logger.info("✓ Structural integrity in HardState (Immutable)")
    logger.info("✓ Dynamic thermal adjustment per node type")
    logger.info("✓ Signal anchoring prevents hallucinations")
    logger.info("✓ Self-correction loops for validation failures")
    logger.info("✓ Complete audit trail of all operations")
    LOGGER.INFO("=" * 80)

    if __name__ == "__main__":
    asyncio.run(main())
