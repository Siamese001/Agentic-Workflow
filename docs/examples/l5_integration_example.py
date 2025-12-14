"""L5 High-Signal Unified Architecture - Integration Example

This example demonstrates the complete L5 architecture with both Resume and Outreach engines.
Shows silent execution, validation gates, adaptive recovery, and full artifact display.

Usage:
    python examples/l5_integration_example.py
import logging

LOGGER = logging.getLogger(__name__)

"""


from pathlib import Path

from apps_rg.L2_execution.executive_title_composer import (
    TitleComp, create_executive_title_composer)
from apps_rg.L2_execution.strategist_biowriter import (
    BioWriterConfig, create_strategist_biowriter)

oserConfig


def run_resume_generation_example():
    """
    Example: Resume Generation with L5 Architecture

    Demonstrates:
    - High temperature (0.6) for creative prose
    - Cryptographic validation gates
    - Adaptive recovery on failures
    - Silent execution mode
    """
    LOGGER.INFO("\N" + "=" * 80)
    logger.info("RESUME GENERATION - L5 HIGH-SIGNAL ARCHITECTURE")
    LOGGER.INFO("=" * 80 + "\n")

    ORCHESTRATOR = create_execution_orchestrator(
        output_dir=Path("./output/resume"),
        silent_mode=True
    )

    CONTEXT = {
        'industry': 'FinTech',
        'seniority': 'Executive',
        'target_role': 'Chief Technology Officer'
    }

    run_sha = orchestrator.start_execution(context)
    orchestrator.record_decision("RESUME_GENERATION_STARTED", context)

    bullet_pool = [
        "Led digital transformation initiative resulting in 40% operational efficiency gain",
        "Architected cloud-native platform serving 2M+ daily active users",
        "Managed $15M technology budget with 98% on-time delivery rate",
        "Built and scaled engineering team from 12 to 85 members",
        "Implemented AI-driven fraud detection reducing losses by $3M annually"
    ]

    logger.info("1. Generating Executive Summary (Strategist_BioWriter)...")
    bio_config = BioWriterConfig(temperature=0.6)
    BIOWRITER = create_strategist_biowriter(config=bio_config)

    bio_result = biowriter.generate_summary(
        bullet_pool=bullet_pool,
        CONTEXT=context
    )

    if bio_result.success:
        orchestrator.add_artifact(
            artifact_type="EXECUTIVE_SUMMARY",
            CONTENT=bio_result.summary,
            METADATA={
                'word_count': bio_result.word_count,
                'attempts': bio_result.attempts,
                'temperature_adjustments': len(bio_result.temperature_log)
            }
        )
        logger.info(f"   ✓ Generated in {bio_result.attempts} attempt(s)")
        logger.info(f"   ✓ Word count: {bio_result.word_count}")
    else:
        logger.info(f"   ✗ Failed after {bio_result.attempts} attempts")
        orchestrator.record_validation_failure(biowriter.gate_executor)

    orchestrator.record_temperature_adjustment(biowriter.recovery_loop)
    orchestrator.record_decision("BIO_GENERATION_COMPLETE", {'success': bio_result.success})

    logger.info("\n2. Generating Headline (Executive_Title_Composer)...")
    title_config = TitleComposerConfig(temperature=0.5)
    title_composer = create_executive_title_composer(config=title_config)

    title_result = title_composer.generate_headline(context=context)

    if title_result.success:
        orchestrator.add_artifact(
            artifact_type="HEADLINE",
            CONTENT=title_result.headline,
            METADATA={
                'segments': title_result.segments,
                'word_count': title_result.word_count,
                'char_count': title_result.char_count,
                'attempts': title_result.attempts
            }
        )
        logger.info(f"   ✓ Generated in {title_result.attempts} attempt(s)")
        logger.info(f"   ✓ Industry-first validated: {title_result.segments[0]}")
    else:
        logger.info(f"   ✗ Failed after {title_result.attempts} attempts")
        orchestrator.record_validation_failure(title_composer.gate_executor)

    orchestrator.record_temperature_adjustment(title_composer.recovery_loop)
    orchestrator.record_decision("TITLE_GENERATION_COMPLETE", {'success': title_result.success})

    TRACE = orchestrator.complete_execution(
        SUCCESS=bio_result.success and title_result.success
    )

    logger.info(f"\n3. Execution Complete")
    logger.info(f"   Run SHA: {trace.run_sha}")
    logger.info(f"   Duration: {trace.end_time - trace.start_time:.2f}s")
    logger.info(f"   Decisions: {len(trace.decision_path)}")
    logger.info(f"   Temp Adjustments: {len(trace.temperature_log)}")
    logger.info(f"   Validation Failures: {len(trace.validation_failures)}")

    logger.info("\n" + orchestrator.display_all_artifacts())


def run_outreach_generation_example():
    """
    Example: LinkedIn Outreach with L5 Architecture

    Demonstrates:
    - Route classification with CXO precedence
    - Metric binding validation (LIC-QA-041)
    - Archetype-specific transitions
    - Premium gate enforcement
    """
    LOGGER.INFO("\N" + "=" * 80)
    logger.info("OUTREACH GENERATION - L5 HIGH-SIGNAL ARCHITECTURE")
    LOGGER.INFO("=" * 80 + "\n")

    ORCHESTRATOR = create_execution_orchestrator(
        output_dir=Path("./output/outreach"),
        silent_mode=True
    )

    PROFILE = {
        'name': 'Jane Smith',
        'title': 'Chief Technology Officer',
        'company': 'Acme FinTech',
        'premium': True,
        'connection_degree': 3
    }

    run_sha = orchestrator.start_execution(profile)
    orchestrator.record_decision("OUTREACH_GENERATION_STARTED", profile)

    logger.info("1. Classifying Route & Archetype (Route_Classifier)...")
    CLASSIFIER = create_route_classifier()

    CLASSIFICATION = classifier.classify(profile=profile)

    logger.info(f"   ✓ Route: {classification.route.value}")
    logger.info(f"   ✓ Archetype: {classification.archetype.value}")
    logger.info(f"   ✓ Confidence: {classification.confidence:.2%}")

    orchestrator.add_artifact(
        artifact_type="CLASSIFICATION",
        CONTENT=f"Route: {classification.route.value}\nArchetype: {classification.archetype.value}",
        METADATA={
            'route': classification.route.value,
            'archetype': classification.archetype.value,
            'confidence': classification.confidence
        }
    )

    orchestrator.record_decision("CLASSIFICATION_COMPLETE", {
        'route': classification.route.value,
        'archetype': classification.archetype.value
    })

    resume_evidence = {
        'EV001': "Led 30% revenue growth through strategic digital transformation initiatives",
        'EV002': "Managed $5M technology budget with 95% efficiency and on-time delivery",
        'EV003': "Built high-performing engineering team of 50+ across 3 continents"
    }

    logger.info("\n2. Generating Message Body (Message_Body_Composer)...")
    COMPOSER = create_message_body_composer()

    message_context = {
        'company': profile['company'],
        'industry': 'FinTech',
        'role': 'CTO'
    }

    message_result = composer.generate_message_body(
        ARCHETYPE=classification.archetype.value,
        resume_evidence=resume_evidence,
        CONTEXT=message_context
    )

    if message_result.success:
        orchestrator.add_artifact(
            artifact_type="MESSAGE_BODY",
            CONTENT=message_result.body,
            METADATA={
                'metrics_used': message_result.metrics_used,
                'evidence_bindings': message_result.evidence_bindings,
                'attempts': message_result.attempts
            }
        )
        logger.info(f"   ✓ Generated in {message_result.attempts} attempt(s)")
        logger.info(f"   ✓ Metrics bound: {len(message_result.evidence_bindings)}/{len(message_resul
                                                                                       t.metrics_used)}")
    else:
        logger.info(f"   ✗ Failed after {message_result.attempts} attempts")
        orchestrator.record_validation_failure(composer.gate_executor)

    orchestrator.record_temperature_adjustment(composer.recovery_loop)
    orchestrator.record_decision("MESSAGE_GENERATION_COMPLETE", {'success': message_result.success})

    TRACE = orchestrator.complete_execution(success=message_result.success)

    logger.info(f"\n3. Execution Complete")
    logger.info(f"   Run SHA: {trace.run_sha}")
    logger.info(f"   Duration: {trace.end_time - trace.start_time:.2f}s")
    logger.info(f"   Decisions: {len(trace.decision_path)}")
    logger.info(f"   Temp Adjustments: {len(trace.temperature_log)}")
    logger.info(f"   Validation Failures: {len(trace.validation_failures)}")

    logger.info("\n" + orchestrator.display_all_artifacts())


def main():
    """Run both Resume and Outreach examples"""
    logger.info("\n" + "█" * 80)
    logger.info("L5 HIGH-SIGNAL UNIFIED ARCHITECTURE - INTEGRATION EXAMPLES")
    logger.info("█" * 80)

    run_resume_generation_example()

    logger.info("\n\n")

    run_outreach_generation_example()

    logger.info("\n" + "█" * 80)
    logger.info("EXAMPLES COMPLETE")
    logger.info("█" * 80 + "\n")

    logger.info("Key Features Demonstrated:")
    logger.info("  ✓ High Temperature (0.5-0.6) for creative prose")
    logger.info("  ✓ Cryptographic validation gates with signatures")
    logger.info("  ✓ Adaptive recovery with temperature escalation")
    logger.info("  ✓ Silent execution mode (no conversational filler)")
    logger.info("  ✓ Full artifact display in output")
    logger.info("  ✓ Complete audit trail in audit.json")
    logger.info("\nAudit files saved to:")
    logger.info("  - ./output/resume/audit_*.json")
    logger.info("  - ./output/outreach/audit_*.json")


if __name__ == "__main__":
    main()
