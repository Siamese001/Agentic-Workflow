"""
Enhancements Integration Layer for 10_12
Unified facade for all 10_12 enhancement capabilities.

This module provides a clean interface to access all implemented
enhancements while maintaining architectural simplicity.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .enhanced_semantic_cache import EnhancedSemanticCache
from .safety_enhancements import SafetyEnhancer, PIIResult, BiasResult
from .retrieval_enhancements import RetrievalEnhancer, HyDEDocument, WeightedResult
from .content_quality_enhancements import ContentQualityEnhancer, EvidenceItem, ToneAdaptation
from .intelligence_bundles import IntelligenceBundleSystem, CompanyInsights, ProductInsights
from .hybrid_scoring import HybridScoringSystem, ScoringResult
from .meta_learning_system import MetaLearningSystem, FeedbackSignal, FeedbackType
from .constitutional_ai_system import ConstitutionalAISystem, ConstitutionalReviewResult
from .goal_alignment_engine import GoalAlignmentEngine, StrategicGoal, GoalAlignmentResult

logger = logging.getLogger(__name__)


@dataclass
class EnhancementConfig:
    """Configuration for enhancement system"""
    enable_semantic_cache: bool = True
    enable_safety_enhancements: bool = True
    enable_retrieval_enhancements: bool = True
    enable_content_quality: bool = True
    enable_intelligence_bundles: bool = True
    enable_hybrid_scoring: bool = True
    enable_meta_learning: bool = True
    enable_constitutional_ai: bool = True
    enable_goal_alignment: bool = True
    
    # Specific configuration
    semantic_threshold: float = 0.8
    auto_correct_safety: bool = False
    learning_mode: str = "active"


class EnhancementFacade:
    """
    Unified Facade for All 10_12 Enhancements
    
    Provides a simple interface to access all enhancement
    capabilities without exposing internal complexity.
    """
    
    def __init__(self, config: EnhancementConfig = None):
        self.config = config or EnhancementConfig()
        self._initialize_enhancements()
        
        logger.info("Enhancement Facade initialized with 10_12-native capabilities")
    
    def _initialize_enhancements(self) -> None:
        """Initialize all enhancement systems."""
        # Core enhancements
        if self.config.enable_semantic_cache:
            self.semantic_cache = EnhancedSemanticCache(
                similarity_threshold=self.config.semantic_threshold
            )
        
        if self.config.enable_safety_enhancements:
            self.safety_enhancer = SafetyEnhancer()
        
        if self.config.enable_retrieval_enhancements:
            self.retrieval_enhancer = RetrievalEnhancer()
        
        if self.config.enable_content_quality:
            self.content_quality_enhancer = ContentQualityEnhancer()
        
        if self.config.enable_intelligence_bundles:
            self.intelligence_system = IntelligenceBundleSystem()
        
        if self.config.enable_hybrid_scoring:
            self.hybrid_scorer = HybridScoringSystem()
        
        # Advanced capabilities
        if self.config.enable_meta_learning:
            from .meta_learning_system import LearningMode
            mode = LearningMode.ACTIVE if self.config.learning_mode == "active" else LearningMode.PASSIVE
            self.meta_learning = MetaLearningSystem(learning_mode=mode)
        
        if self.config.enable_constitutional_ai:
            self.constitutional_ai = ConstitutionalAISystem()
        
        if self.config.enable_goal_alignment:
            self.goal_alignment = GoalAlignmentEngine()
    
    def enhance_content_pipeline(
        self,
        content: str,
        context: Dict[str, Any] = None,
        goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        Apply comprehensive content enhancement pipeline.
        
        Args:
            content: Original content
            context: Context information
            goals: Strategic goals
            
        Returns:
            Enhanced content with all improvements applied
        """
        results = {
            'original_content': content,
            'enhanced_content': content,
            'improvements': [],
            'safety_results': {},
            'quality_results': {},
            'compliance_results': {}
        }
        
        enhanced_content = content
        
        # Step 1: Safety enhancements
        if self.config.enable_safety_enhancements:
            enhanced_content, pii_result, bias_result = self.safety_enhancer.enhance_content_safety(
                enhanced_content
            )
            results['enhanced_content'] = enhanced_content
            results['safety_results'] = {
                'pii_detected': len(pii_result.detected_pii),
                'bias_detected': bias_result.has_bias,
                'is_compliant': self.safety_enhancer.is_content_compliant(pii_result, bias_result)
            }
            results['improvements'].append("Applied safety enhancements")
        
        # Step 2: Content quality enhancements
        if self.config.enable_content_quality:
            persona = context.get('persona', {}) if context else {}
            evidence_list = context.get('evidence', []) if context else []
            
            if evidence_list:
                top_evidence, tone_adaptation = self.content_quality_enhancer.enhance_content_quality(
                    evidence_list, enhanced_content, context.get('query', ''), persona
                )
                enhanced_content = tone_adaptation.adapted_content
                results['enhanced_content'] = enhanced_content
                results['quality_results'] = {
                    'tone_applied': tone_adaptation.tone_profile.tone_type.value,
                    'evidence_ranked': len(top_evidence),
                    'tone_confidence': tone_adaptation.adaptation_confidence
                }
                results['improvements'].append("Applied content quality enhancements")
        
        # Step 3: Goal alignment
        if self.config.enable_goal_alignment and goals:
            strategic_goals = self.goal_alignment.create_strategic_goals(
                business_objectives=goals
            )
            alignment_result = self.goal_alignment.align_prompt_to_goals(
                enhanced_content, strategic_goals
            )
            results['enhanced_content'] = alignment_result.aligned_prompt
            results['quality_results']['goal_alignment'] = {
                'score': alignment_result.alignment_score,
                'goals_aligned': len(alignment_result.aligned_goals)
            }
            results['improvements'].append("Applied goal alignment")
        
        # Step 4: Constitutional AI review
        if self.config.enable_constitutional_ai:
            compliance_result = self.constitutional_ai.review_content(
                enhanced_content, context, self.config.auto_correct_safety
            )
            results['compliance_results'] = {
                'is_compliant': compliance_result.is_compliant,
                'violations': len(compliance_result.violations),
                'compliance_score': compliance_result.compliance_score
            }
            results['improvements'].append("Applied constitutional AI review")
        
        # Add feedback to meta-learning
        if self.config.enable_meta_learning:
            self._add_feedback_to_meta_learning(results)
        
        logger.info(f"Enhanced content with {len(results['improvements'])} improvements")
        
        return results
    
    def enhance_retrieval_pipeline(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        Apply comprehensive retrieval enhancement pipeline.
        
        Args:
            query: Search query
            documents: Documents to retrieve from
            goals: Strategic goals
            
        Returns:
            Enhanced retrieval results
        """
        results = {
            'query': query,
            'original_results': documents,
            'enhanced_results': [],
            'hyde_document': {},
            'scoring_improvements': {}
        }
        
        # Step 1: Retrieval enhancements
        if self.config.enable_retrieval_enhancements:
            base_prompt = ''  # Default empty prompt
            context_data = {'query': query}
            
            enhanced_prompt, hyde_doc, weighted_results = self.retrieval_enhancer.enhance_retrieval(
                base_prompt, goals or [], query, documents, context_data
            )
            
            results['hyde_document'] = {
                'hypothetical_doc': hyde_doc.hypothetical_doc,
                'strategy': hyde_doc.expansion_strategy,
                'confidence': hyde_doc.confidence
            }
            
            results['enhanced_results'] = [
                {
                    'content': result.content,
                    'final_score': result.final_score,
                    'metadata': result.metadata
                }
                for result in weighted_results
            ]
            
            results['scoring_improvements'] = {
                'results_weighted': len(weighted_results),
                'top_score': weighted_results[0].final_score if weighted_results else 0.0
            }
        
        # Step 2: Hybrid scoring
        if self.config.enable_hybrid_scoring:
            if not self.hybrid_scorer.is_indexed:
                self.hybrid_scorer.initialize_system(documents)
            
            hybrid_results = self.hybrid_scorer.search(query, top_k=10)
            
            if not results['enhanced_results']:
                results['enhanced_results'] = [
                    {
                        'content': result.content,
                        'final_score': result.hybrid_score,
                        'metadata': result.metadata
                    }
                    for result in hybrid_results
                ]
            
            results['scoring_improvements']['hybrid_applied'] = len(hybrid_results)
        
        logger.info(f"Enhanced retrieval for query: {len(results['enhanced_results'])} results")
        
        return results
    
    def analyze_business_intelligence(
        self,
        company_data: Dict[str, Any],
        product_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply business intelligence analysis.
        
        Args:
            company_data: Company information
            product_data: Product information
            
        Returns:
            Business intelligence insights
        """
        if not self.config.enable_intelligence_bundles:
            return {'error': 'Intelligence bundles not enabled'}
        
        company_insights, product_insights = self.intelligence_system.analyze_business_intelligence(
            company_data, product_data
        )
        
        results = {
            'company_insights': {
                'name': company_insights.company_name,
                'business_stage': company_insights.business_stage.value,
                'market_position': company_insights.market_position,
                'competitive_advantages': company_insights.competitive_advantages,
                'growth_indicators': company_insights.growth_indicators,
                'strategic_priorities': company_insights.strategic_priorities,
                'confidence': company_insights.confidence_score
            },
            'product_insights': {
                'name': product_insights.product_name,
                'category': product_insights.category.value,
                'value_proposition': product_insights.value_proposition,
                'target_market': product_insights.target_market,
                'competitive_differentiators': product_insights.competitive_differentiators,
                'market_opportunities': product_insights.market_opportunities,
                'confidence': product_insights.confidence_score
            }
        }
        
        logger.info(f"Analyzed business intelligence for {company_insights.company_name}")
        
        return results
    
    def add_feedback(
        self,
        task_id: str,
        feedback_type: str,
        score: float,
        context: Dict[str, Any] = None
    ) -> None:
        """
        Add feedback for meta-learning.
        
        Args:
            task_id: Unique task identifier
            feedback_type: Type of feedback
            score: Feedback score (0.0 to 1.0)
            context: Context information
        """
        if not self.config.enable_meta_learning:
            logger.warning("Meta-learning not enabled")
            return
        
        try:
            from .meta_learning_system import FeedbackType
            fb_type = FeedbackType(feedback_type)
            self.meta_learning.add_feedback(task_id, fb_type, score, context)
            logger.debug(f"Added feedback for task {task_id}: {score:.3f}")
        except ValueError as e:
            logger.error(f"Invalid feedback type: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            'config': {
                'enabled_capabilities': [
                    name for name, enabled in [
                        ('semantic_cache', self.config.enable_semantic_cache),
                        ('safety_enhancements', self.config.enable_safety_enhancements),
                        ('retrieval_enhancements', self.config.enable_retrieval_enhancements),
                        ('content_quality', self.config.enable_content_quality),
                        ('intelligence_bundles', self.config.enable_intelligence_bundles),
                        ('hybrid_scoring', self.config.enable_hybrid_scoring),
                        ('meta_learning', self.config.enable_meta_learning),
                        ('constitutional_ai', self.config.enable_constitutional_ai),
                        ('goal_alignment', self.config.enable_goal_alignment)
                    ] if enabled
                ]
            }
        }
        
        # Add status from individual systems
        if self.config.enable_meta_learning:
            status['meta_learning'] = self.meta_learning.get_learning_insights()
        
        if self.config.enable_constitutional_ai:
            status['constitutional_ai'] = self.constitutional_ai.get_system_status()
        
        if self.config.enable_goal_alignment:
            status['goal_alignment'] = self.goal_alignment.get_alignment_stats()
        
        return status
    
    def _add_feedback_to_meta_learning(self, results: Dict[str, Any]) -> None:
        """Add automatic feedback based on enhancement results."""
        if not self.config.enable_meta_learning:
            return
        
        # Add safety feedback
        if results.get('safety_results'):
            safety_score = 1.0
            if results['safety_results'].get('pii_detected', 0) > 0:
                safety_score -= 0.1
            if results['safety_results'].get('bias_detected', False):
                safety_score -= 0.1
            
            self.add_feedback(
                task_id="safety_enhancement",
                feedback_type="quality",
                score=max(safety_score, 0.0),
                context=results['safety_results']
            )
        
        # Add compliance feedback
        if results.get('compliance_results'):
            compliance_score = results['compliance_results'].get('compliance_score', 0.5)
            self.add_feedback(
                task_id="constitutional_review",
                feedback_type="quality",
                score=compliance_score,
                context=results['compliance_results']
            )


# Factory function for easy integration
def create_enhancement_system(config: EnhancementConfig = None) -> EnhancementFacade:
    """
    Create complete enhancement system.
    
    Args:
        config: Optional configuration
        
    Returns:
        Enhancement facade with all capabilities
    """
    return EnhancementFacade(config)


# Convenience functions for specific capabilities
def create_safety_enhancer() -> SafetyEnhancer:
    """Create safety enhancer for PII and bias detection."""
    return SafetyEnhancer()


def create_meta_learning_system(learning_mode: str = "active") -> MetaLearningSystem:
    """Create meta-learning system for continuous improvement."""
    from .meta_learning_system import LearningMode
    mode = LearningMode.ACTIVE if learning_mode == "active" else LearningMode.PASSIVE
    return MetaLearningSystem(learning_mode=mode)


def create_constitutional_ai_system() -> ConstitutionalAISystem:
    """Create constitutional AI system for content compliance."""
    return ConstitutionalAISystem()


# Export main classes
__all__ = [
    'EnhancementFacade',
    'EnhancementConfig',
    'create_enhancement_system',
    'create_safety_enhancer',
    'create_meta_learning_system',
    'create_constitutional_ai_system'
]
