"""
Enhancement System Demo for 10_12
Demonstrates integration of all enhancement capabilities
with the existing outreach orchestrator.

This demo shows how to use the EnhancementFacade to add
advanced capabilities while maintaining architectural simplicity.
"""

import logging
from typing import Dict, List, object

from . import EnhancementFacade, EnhancementConfig, create_enhancement_system
from ..orchestrator import OutreachOrchestrator

logger = logging.getLogger(__name__)


def demo_basic_enhancement_pipeline():
    """Demonstrate basic content enhancement pipeline."""
    print("🚀 DEMO: Basic Content Enhancement Pipeline")
    print("=" * 50)
    
    # Create enhancement system with default configuration
    config = EnhancementConfig(
        enable_safety_enhancements=True,
        enable_content_quality=True,
        enable_goal_alignment=True,
        enable_constitutional_ai=True
    )
    
    facade = create_enhancement_system(config)
    
    # Sample content to enhance
    sample_content = """
    We are excited to announce our new product launch! 
    Contact john.doe@company.com for more information.
    This will definitely change the market forever.
    """
    
    # Sample context and goals
    context = {
        'persona': {
            'tone': 'professional'
        },
        'domain': 'business_communication'
    }
    
    goals = [
        "Maintain professional communication",
        "Ensure compliance with privacy regulations",
        "Deliver clear and concise messaging"
    ]
    
    # Apply enhancement pipeline
    results = facade.enhance_content_pipeline(
        content=sample_content,
        context=context,
        goals=goals
    )
    
    # Display results
    print(f"Original Content: {sample_content.strip()}")
    print(f"Enhanced Content: {results['enhanced_content'].strip()}")
    print(f"Improvements Applied: {', '.join(results['improvements'])}")
    print(f"Safety Results: {results['safety_results']}")
    print(f"Quality Results: {results['quality_results']}")
    print(f"Compliance Results: {results['compliance_results']}")
    print()


def demo_retrieval_enhancement_pipeline():
    """Demonstrate retrieval enhancement pipeline."""
    print("🔍 DEMO: Retrieval Enhancement Pipeline")
    print("=" * 50)
    
    facade = create_enhancement_system()
    
    # Sample query and documents
    query = "AI startup funding opportunities"
    documents = [
        {
            'content': 'Recent AI startup raised $10M in Series A funding for machine learning platform',
            'source': 'tech_news',
            'date': '2024-01-15'
        },
        {
            'content': 'Venture capital firms investing in artificial intelligence companies',
            'source': 'investment_report',
            'date': '2024-01-10'
        },
        {
            'content': 'Machine learning startup secures seed funding for enterprise solutions',
            'source': 'press_release',
            'date': '2024-01-20'
        }
    ]
    
    goals = ['Find recent funding information', 'Identify investment trends']
    
    # Apply retrieval enhancement
    results = facade.enhance_retrieval_pipeline(
        query=query,
        documents=documents,
        goals=goals
    )
    
    # Display results
    print(f"Query: {query}")
    print(f"Original Documents: {len(documents)}")
    print(f"HyDE Strategy: {results['hyde_document']['strategy']}")
    print(f"HyDE Confidence: {results['hyde_document']['confidence']:.2f}")
    print(f"Enhanced Results: {len(results['enhanced_results'])}")
    
    for i, result in enumerate(results['enhanced_results'][:3]):
        print(f"  Result {i+1}: Score {result['final_score']:.3f} - {result['content'][:80]}...")
    
    print(f"Scoring Improvements: {results['scoring_improvements']}")
    print()


def demo_business_intelligence():
    """Demonstrate business intelligence analysis."""
    print("📊 DEMO: Business Intelligence Analysis")
    print("=" * 50)
    
    facade = create_enhancement_system()
    
    # Sample company and product data
    company_data = {
        'name': 'TechCorp AI',
        'description': 'Leading AI startup focused on enterprise machine learning solutions',
        'funding': {
            'stage': 'Series A',
            'amount': '$15M'
        },
        'market': {
            'competition_level': 'high',
            'growing_market': True
        }
    }
    
    product_data = {
        'name': 'ML Platform Pro',
        'description': 'Scalable machine learning platform for enterprise customers',
        'features': [
            'Automated model training',
            'Real-time predictions',
            'Enterprise security',
            'Scalable infrastructure'
        ],
        'market': {
            'underserved': False,
            'new_technology': True
        }
    }
    
    # Apply business intelligence analysis
    results = facade.analyze_business_intelligence(
        company_data=company_data,
        product_data=product_data
    )
    
    # Display results
    print(f"Company: {results['company_insights']['name']}")
    print(f"Business Stage: {results['company_insights']['business_stage']}")
    print(f"Market Position: {results['company_insights']['market_position']}")
    print(f"Strategic Priorities: {', '.join(results['company_insights']['strategic_priorities'])}")
    print(f"Confidence: {results['company_insights']['confidence']:.2f}")
    
    print(f"\nProduct: {results['product_insights']['name']}")
    print(f"Category: {results['product_insights']['category']}")
    print(f"Value Proposition: {results['product_insights']['value_proposition']}")
    print(f"Target Market: {results['product_insights']['target_market']}")
    print(f"Confidence: {results['product_insights']['confidence']:.2f}")
    print()


def demo_meta_learning():
    """Demonstrate meta-learning capabilities."""
    print("🧠 DEMO: Meta-Learning System")
    print("=" * 50)
    
    config = EnhancementConfig(
        enable_meta_learning=True,
        learning_mode="active"
    )
    
    facade = create_enhancement_system(config)
    
    # Add various types of feedback
    facade.add_feedback(
        task_id="content_enhancement_001",
        feedback_type="quality",
        score=0.85,
        context={'improvements': ['safety', 'tone']}
    )
    
    facade.add_feedback(
        task_id="retrieval_enhancement_001", 
        feedback_type="relevance",
        score=0.92,
        context={'query': 'AI funding', 'results_count': 10}
    )
    
    facade.add_feedback(
        task_id="safety_check_001",
        feedback_type="user_satisfaction",
        score=0.78,
        context={'pii_detected': 2, 'bias_detected': False}
    )
    
    # Get learning insights
    system_status = facade.get_system_status()
    meta_learning = system_status.get('meta_learning', {})
    
    print("Meta-Learning Insights:")
    print(f"Learning Mode: {meta_learning.get('learning_mode', 'unknown')}")
    print(f"Total Feedback: {meta_learning.get('learning_stats', {}).get('total_feedback', 0)}")
    print(f"Patterns Detected: {meta_learning.get('learning_stats', {}).get('patterns_detected', 0)}")
    print(f"Adaptations Applied: {meta_learning.get('learning_stats', {}).get('adaptations_applied', 0)}")
    
    if 'recent_patterns' in meta_learning:
        print("Recent Patterns:")
        for pattern in meta_learning['recent_patterns'][:3]:
            print(f"  - {pattern.description}")
    
    print()


def demo_constitutional_ai():
    """Demonstrate constitutional AI capabilities."""
    print("🛡️ DEMO: Constitutional AI System")
    print("=" * 50)
    
    config = EnhancementConfig(
        enable_constitutional_ai=True,
        auto_correct_safety=True
    )
    
    facade = create_enhancement_system(config)
    
    # Sample content with potential issues
    test_content = """
    We guarantee this will absolutely change everything forever!
    Contact us at 555-123-4567 for immediate results.
    This is the best product in the universe without question.
    """
    
    # Review content with constitutional AI
    results = facade.enhance_content_pipeline(
        content=test_content,
        context={'is_personal': False}
    )
    
    # Display compliance results
    compliance = results['compliance_results']
    print(f"Content Compliant: {compliance['is_compliant']}")
    print(f"Compliance Score: {compliance['compliance_score']:.2f}")
    print(f"Violations Found: {compliance['violations']}")
    
    # Get detailed constitutional AI status
    system_status = facade.get_system_status()
    constitutional_status = system_status.get('constitutional_ai', {})
    
    print(f"\nConstitutional AI System Status:")
    print(f"Rules Loaded: {constitutional_status.get('system_stats', {}).get('rules_loaded', 0)}")
    print(f"Validations Performed: {constitutional_status.get('system_stats', {}).get('validations_performed', 0)}")
    print(f"Overall Compliance Rate: {constitutional_status.get('system_stats', {}).get('compliance_rate', 0):.2f}")
    
    print()


def demo_integration_with_orchestrator():
    """Demonstrate integration with existing OutreachOrchestrator."""
    print("🔗 DEMO: Integration with Outreach Orchestrator")
    print("=" * 50)
    
    # Create the original orchestrator
    orchestrator = OutreachOrchestrator()
    
    # Create enhancement system
    facade = create_enhancement_system()
    
    # Sample context for orchestrator
    sample_context = {
        'sender_profile': {
            'name': 'John Doe',
            'company': 'TechCorp',
            'role': 'CEO'
        },
        'recipient_context': {
            'name': 'Jane Smith',
            'company': 'Investment Partners',
            'role': 'Partner'
        },
        'research_data': {
            'recent_funding': True,
            'market_trends': 'AI growth',
            'competitive_landscape': 'Crowded'
        }
    }
    
    print("1. Traditional Orchestrator Flow:")
    print("   - Planning → Research → Insights → Message Generation")
    print("   - Linear execution with basic capabilities")
    
    print("\n2. Enhanced Orchestrator Flow:")
    print("   - Planning + Goal Alignment")
    print("   - Research + Retrieval Enhancements + Hybrid Scoring")
    print("   - Insights + Business Intelligence Analysis")
    print("   - Message Generation + Content Quality + Safety + Constitutional AI")
    
    print("\n3. Integration Points:")
    print("   - Use facade.enhance_content_pipeline() for message generation")
    print("   - Use facade.enhance_retrieval_pipeline() for research phase")
    print("   - Use facade.analyze_business_intelligence() for insights")
    print("   - Use facade.add_feedback() for continuous improvement")
    
    # Demonstrate enhanced message generation
    base_message = "Dear Jane, I hope this email finds you well. We're excited about our recent progress."
    
    enhanced_results = facade.enhance_content_pipeline(
        content=base_message,
        context=sample_context,
        goals=['Professional communication', 'Investment interest', 'Clear value proposition']
    )
    
    print(f"\n4. Enhanced Message Example:")
    print(f"   Original: {base_message}")
    print(f"   Enhanced: {enhanced_results['enhanced_content']}")
    print(f"   Improvements: {', '.join(enhanced_results['improvements'])}")
    
    print()


def demo_system_configuration():
    """Demonstrate different system configurations."""
    print("⚙️ DEMO: System Configuration Options")
    print("=" * 50)
    
    # Minimal configuration (safety only)
    minimal_config = EnhancementConfig(
        enable_safety_enhancements=True,
        enable_constitutional_ai=True
    )
    
    # Performance-focused configuration
    performance_config = EnhancementConfig(
        enable_semantic_cache=True,
        enable_retrieval_enhancements=True,
        enable_hybrid_scoring=True,
        enable_content_quality=True
    )
    
    # Full-featured configuration
    full_config = EnhancementConfig(
        enable_semantic_cache=True,
        enable_safety_enhancements=True,
        enable_retrieval_enhancements=True,
        enable_content_quality=True,
        enable_intelligence_bundles=True,
        enable_hybrid_scoring=True,
        enable_meta_learning=True,
        enable_constitutional_ai=True,
        enable_goal_alignment=True
    )
    
    configs = [
        ("Minimal (Safety Only)", minimal_config),
        ("Performance-Focused", performance_config),
        ("Full-Featured", full_config)
    ]
    
    for name, config in configs:
        facade = create_enhancement_system(config)
        status = facade.get_system_status()
        enabled_capabilities = status['config']['enabled_capabilities']
        
        print(f"\n{name}:")
        print(f"   Enabled Capabilities: {len(enabled_capabilities)}")
        print(f"   Features: {', '.join(enabled_capabilities[:3])}{'...' if len(enabled_capabilities) > 3 else ''}")
    
    print()


def run_complete_demo():
    """Run complete demonstration of all enhancement capabilities."""
    print("🎯 COMPLETE 10_12 ENHANCEMENT SYSTEM DEMO")
    print("=" * 60)
    print("This demo showcases all implemented enhancement capabilities")
    print("and their integration with the existing 10_12 architecture.")
    print()
    
    try:
        # Run individual demos
        demo_basic_enhancement_pipeline()
        demo_retrieval_enhancement_pipeline()
        demo_business_intelligence()
        demo_meta_learning()
        demo_constitutional_ai()
        demo_integration_with_orchestrator()
        demo_system_configuration()
        
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nKey Takeaways:")
        print("• All enhancement capabilities are fully functional")
        print("• Integration maintains 10_12's architectural simplicity")
        print("• Configurable system allows selective capability enablement")
        print("• Meta-learning provides continuous improvement")
        print("• Constitutional AI ensures content compliance")
        print("• Unified facade pattern provides clean integration")
        
    except Exception as e:
        print(f"❌ Demo Error: {e}")
        logger.error(f"Demo failed: {e}", exc_info=True)


if __name__ == "__main__":
    # Configure logging for demo
    logging.basicConfig(level=logging.INFO)
    
    # Run the complete demo
    run_complete_demo()
