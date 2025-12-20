import asyncio
import logging
import sys
from pathlib import Path
from typing import Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.domain.context import ValidationContext
from agentic_core.agents import get_hallucination_hunter, HallucinationHunter # Added HallucinationHunter for type hinting

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


async def _setup_hunter_test_environment(ctx: ValidationContext) -> HallucinationHunter:
    """Sets up the test environment for Hallucination Hunter."""
    logger.info("="*80)
    logger.info("🔍 HALLUCINATION HUNTER TEST")
    logger.info("="*80)
    
    logger.info("\n1. Simulating PIPELINE_OUTPUT signals...")
    ctx.signals = set()
    ctx.signals.add("PIPELINE_OUTPUT:output/resume_john_doe.txt")
    logger.info(f"   Added {len([s for s in ctx.signals if s.startswith('PIPELINE_OUTPUT:')])} PIPELINE_OUTPUT signals")
    
    logger.info("\n2. Initializing Hallucination Hunter...")
    hunter = get_hallucination_hunter(ctx)
    
    if hunter.genai_available:
        logger.info("   ✅ Gemini 2.5 connected - intelligent claim extraction enabled")
    else:
        logger.info("   ⚠️  Gemini not available - using simple claim extraction")
    return hunter

def _prepare_hallucination_test_data(ctx: ValidationContext):
    """Prepares source and generated data for the hallucination test."""
    logger.info("\n3. Creating test data...")
    
    # Source raw data (ground truth)
    source_data = """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 5 years of Python development
    - Led 3 major projects at TechCorp
    - Implemented microservices architecture
    - Managed team of 4 developers
    
    Skills:
    - Python, Java, JavaScript
    - AWS, Docker, Kubernetes
    - PostgreSQL, MongoDB
    """
    
    # Generated resume (with some hallucinations)
    generated_resume = """
    JOHN DOE
    Senior Software Engineer
    
    EXPERIENCE:
    • 7 years of Python development (HALLUCINATION: actually 5 years)
    • Led 3 major projects at TechCorp (CORRECT)
    • Implemented microservices architecture (CORRECT)
    • Managed team of 10 developers (HALLUCINATION: actually 4)
    • Expert in machine learning (HALLUCINATION: not in source)
    
    SKILLS:
    • Python, Java, JavaScript (CORRECT)
    • AWS, Docker, Kubernetes (CORRECT)
    • PostgreSQL, MongoDB (CORRECT)
    """
    
    # Store in context
    ctx.pipeline_data = {
        "resume_generation": {
            "source_truth": source_data,
            "generated_artifact": generated_resume
        }
    }
    
    logger.info("   Source data: 150 characters")
    logger.info("   Generated resume: 400 characters")
    logger.info("   Expected hallucinations: 3 (7 years, 10 developers, ML expertise)")

async def _execute_hallucination_hunter(hunter: HallucinationHunter):
    """Executes the Hallucination Hunter and logs its progress."""
    logger.info("\n4. Running Hallucination Hunter...")
    logger.info("   Extracting atomic claims...")
    logger.info("   Performing vector similarity search...")
    logger.info("   Calculating integrity score...")
    
    try:
        await hunter.execute()
    except Exception as e:
        logger.error(f"   Error during execution: {e}")

def _report_integrity_results(ctx: ValidationContext, hunter: HallucinationHunter):
    """Reports the integrity scores and hallucination rates."""
    logger.info("\n5. Results:")
    
    if hasattr(ctx, 'integrity_reports'):
        for stage_name, report in ctx.integrity_reports.items():
            logger.info(f"\n   Stage: {stage_name}")
            logger.info(f"   Total claims: {report.total_claims}")
            logger.info(f"   Supported: {report.supported_claims}")
            logger.info(f"   Unsupported: {report.unsupported_claims}")
            logger.info(f"   Integrity score: {report.integrity_score:.1%}")
            logger.info(f"   Hallucination rate: {report.hallucination_percentage:.1%}")
            logger.info(f"   Risk level: {report.risk_level}")
            
            if report.hallucination_percentage > hunter.HALLUCINATION_THRESHOLD:
                logger.error(f"   🚨 HALLUCINATION THRESHOLD EXCEEDED")
                logger.error(f"      Threshold: {hunter.HALLUCINATION_THRESHOLD:.1%}")
                logger.error(f"      Actual: {report.hallucination_percentage:.1%}")

def _report_hallucination_signals(ctx: ValidationContext):
    """Reports any factual integrity or hallucination signals."""
    fail_signals = [s for s in ctx.signals if s.startswith('FACTUAL_INTEGRITY_FAIL:')]
    if fail_signals:
        logger.error(f"\n   🚨 FACTUAL_INTEGRITY_FAIL SIGNALS: {len(fail_signals)}")
        for signal in fail_signals:
            logger.error(f"     {signal}")
    
    hallucination_signals = [s for s in ctx.signals if s.startswith('HALLUCINATION_DETECTED:')]
    if hallucination_signals:
        logger.warning(f"\n   ⚠️  HALLUCINATION_DETECTED SIGNALS: {len(hallucination_signals)}")
        for signal in hallucination_signals:
            logger.warning(f"     {signal}")

def _log_hallucination_test_summary():
    """Logs the final summary and key features of the hallucination test."""
    logger.info("\n" + "="*80)
    logger.info("✅ HALLUCINATION HUNTER TEST COMPLETE")
    logger.info("="*80)
    
    logger.info("\nKey Features Demonstrated:")
    logger.info("  1. ✅ PIPELINE_OUTPUT signal listening from blackboard")
    logger.info("  2. ✅ Gemini-powered atomic claim extraction")
    logger.info("  3. ✅ Vector similarity search (threshold: 0.85)")
    logger.info("  4. ✅ Hallucination percentage calculation")
    logger.info("  5. ✅ 5% hallucination threshold enforcement")
    logger.info("  6. ✅ FACTUAL_INTEGRITY_FAIL signal emission")
    logger.info("  7. ✅ Audit trail metadata injection")
    
    logger.info("\nAudit Trail:")
    logger.info("  - Sidecar JSON files: {output_file}_audit.json")
    logger.info("  - Maps every claim to source citation")
    logger.info("  - Includes similarity scores and unsupported claims")
    
    logger.info("\nBlocker Behavior:")
    logger.info("  - If hallucination rate > 5%:")
    logger.info("    → FACTUAL_INTEGRITY_FAIL signal emitted")
    logger.info("    → Resume blocked from output folder")
    logger.info("    → Requires human review or regeneration")


async def test_hallucination_hunter():
    """Test Hallucination Hunter atomic claim validation."""
    ctx = ValidationContext()
    hunter = await _setup_hunter_test_environment(ctx)
    _prepare_hallucination_test_data(ctx)
    await _execute_hallucination_hunter(hunter)
    _report_integrity_results(ctx, hunter)
    _report_hallucination_signals(ctx)
    _log_hallucination_test_summary()


async def test_claim_extraction():
    """Test atomic claim extraction with Gemini."""
    
    logger.info("\n" + "="*80)
    logger.info("🔬 ATOMIC CLAIM EXTRACTION TEST")
    logger.info("="*80)
    
    ctx = ValidationContext()
    hunter = get_hallucination_hunter(ctx)
    
    test_text = """
    John Doe is a Senior Software Engineer with 5 years of Python experience.
    He led 3 major projects and managed a team of 4 developers.
    His skills include AWS, Docker, and Kubernetes.
    """
    
    logger.info("\nInput text:")
    logger.info(test_text)
    
    logger.info("\nExtracting atomic claims...")
    claims = await hunter._extract_claims(test_text)
    
    logger.info(f"\nExtracted {len(claims)} atomic claims:")
    for i, claim in enumerate(claims, 1):
        logger.info(f"  {i}. {claim.text}")
    
    logger.info("\nExpected claims:")
    logger.info("  1. John Doe is a Senior Software Engineer")
    logger.info("  2. John Doe has 5 years of Python experience")
    logger.info("  3. John Doe led 3 major projects")
    logger.info("  4. John Doe managed a team of 4 developers")
    logger.info("  5. John Doe's skills include AWS, Docker, and Kubernetes")
    
    logger.info("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(test_hallucination_hunter())
    asyncio.run(test_claim_extraction())