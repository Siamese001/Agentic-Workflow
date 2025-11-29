"""
Content Enhancer - Subatomic Agent with Full v5 Instructional Framework

A specialized subatomic agent for enhancing content quality, clarity, and impact
while preserving original meaning. Uses complete 30-point instructional injection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

from agentic_core.shared.prompts.prompt_composer import (
    PromptComposer, 
    AgentProfile,
    create_content_enhancer_profile
)

logger = logging.getLogger(__name__)


@dataclass
class ContentEnhancement:
    """Individual content enhancement operation."""
    enhancement_id: str
    enhancement_type: str  # "clarity", "tone", "impact", "readability"
    original_text: str
    enhanced_text: str
    confidence_score: float
    improvement_rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentEnhancerOutput:
    """Structured output from content enhancer subatomic agent."""
    enhanced_content: str
    enhancements_applied: List[ContentEnhancement]
    overall_confidence: float
    processing_metadata: Dict[str, Any] = field(default_factory=dict)


class ContentEnhancerAgent:
    """Subatomic agent for content enhancement with full v5 instructional framework."""
    
    def __init__(self, model_client=None):
        self.model_client = model_client
        self.prompt_composer = PromptComposer()
        self.profile = create_content_enhancer_profile()
        self.prompt_composer.register_profile(self.profile)
        
        # Agent-specific configuration
        self.agent_id = "content_enhancer_v1"
        self.version = "1.0.0"
        self.capabilities = [
            "text_clarity_enhancement",
            "tone_optimization", 
            "impact_improvement",
            "readability_optimization"
        ]
    
    def enhance_content(self, 
                       content: str,
                       context: Optional[Dict[str, Any]] = None,
                       enhancement_targets: Optional[List[str]] = None,
                       parent_prompt: Optional[str] = None) -> ContentEnhancerOutput:
        """
        Enhance content quality using full v5 instructional framework.
        
        Args:
            content: Original content to enhance
            context: Additional context for enhancement (audience, purpose, etc.)
            enhancement_targets: Specific areas to focus on
            parent_prompt: Inherited prompt from parent K-node
            
        Returns:
            ContentEnhancerOutput with enhanced content and metadata
        """
        
        # Generate complete prompt using v5 framework
        complete_prompt = self._generate_enhancement_prompt(
            content, context, enhancement_targets, parent_prompt
        )
        
        # Execute enhancement with model
        enhancement_result = self._execute_enhancement(complete_prompt, content)
        
        # Process and structure output
        structured_output = self._process_enhancement_result(enhancement_result, content)
        
        return structured_output
    
    def _generate_enhancement_prompt(self,
                                   content: str,
                                   context: Optional[Dict[str, Any]],
                                   enhancement_targets: Optional[List[str]],
                                   parent_prompt: Optional[str]) -> str:
        """Generate complete prompt using v5 framework layers."""
        
        # Customize profile with specific parameters
        custom_profile = AgentProfile(
            agent_name=f"{self.profile.agent_name}_session",
            agent_type=self.profile.agent_type,
            enable_framing=True,
            enable_context=True,
            enable_reasoning=True,
            enable_tooling=True,
            enable_safety=True,
            enable_output=True,
            inherit_from_parent=parent_prompt is not None,
            
            # Framing layer customization
            framing_params={
                'goal': self.profile.framing_params['goal'],
                'success_criteria': self.profile.framing_params['success_criteria'],
                'task_mode': 'synthesis',
                'scope': f"Content enhancement focusing on: {', '.join(enhancement_targets or ['general quality'])}",
                'constraints': [
                    "Preserve original meaning and factual accuracy",
                    "Maintain professional tone appropriate for context",
                    "Enhance without excessive wordiness",
                    "Respect character limits and formatting requirements"
                ],
                'max_tokens': 2000,
                'efficiency_mode': 'balanced'
            },
            
            # Context layer customization
            context_params={
                'user_input': content,
                'source': 'content_enhancement_request',
                'canonicalization': True,
                'pruning': True,
                'relevance_threshold': 0.8,
                'token_budget': 1500,
                'consistency_fields': {
                    'content': 'Original text content',
                    'context': 'Provided enhancement context',
                    'targets': 'Specified enhancement areas'
                },
                'ordering': ['content', 'context', 'enhancement_targets', 'constraints']
            },
            
            # Reasoning layer customization
            reasoning_params={
                'failure_modes': [
                    "Over-enhancement that changes meaning",
                    "Inconsistent tone throughout content",
                    "Introduction of factual errors",
                    "Excessive verbosity or wordiness",
                    "Loss of original intent"
                ],
                'multi_branch': True,
                'branches': 3
            },
            
            # Tooling layer customization
            tooling_params={
                'tools': {
                    'content_analyzer': 'Analyze text structure and readability',
                    'tone_detector': 'Assess current tone and style',
                    'clarity_scorer': 'Measure text clarity and comprehension'
                }
            },
            
            # Output layer customization
            output_params={
                'schema': {
                    'type': 'object',
                    'properties': {
                        'enhanced_content': {'type': 'string'},
                        'enhancements': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'type': {'type': 'string'},
                                    'original': {'type': 'string'},
                                    'enhanced': {'type': 'string'},
                                    'rationale': {'type': 'string'},
                                    'confidence': {'type': 'number'}
                                }
                            }
                        },
                        'overall_confidence': {'type': 'number'},
                        'processing_notes': {'type': 'string'}
                    },
                    'required': ['enhanced_content', 'enhancements', 'overall_confidence']
                },
                'field_order': ['enhanced_content', 'enhancements', 'overall_confidence', 'processing_notes'],
                'minimality': True,
                'max_fields': 4
            }
        )
        
        return self.prompt_composer.compose_prompt(custom_profile, parent_prompt)
    
    def _execute_enhancement(self, prompt: str, original_content: str) -> Dict[str, Any]:
        """Execute content enhancement using model client."""
        
        if self.model_client:
            # Use actual model client
            response = self.model_client.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3,
                response_format={'type': 'json_object'}
            )
            return response
        else:
            # Mock implementation for testing
            return self._mock_enhancement_execution(original_content)
    
    def _mock_enhancement_execution(self, content: str) -> Dict[str, Any]:
        """Mock enhancement execution for testing without model client."""
        
        # Simple mock enhancement logic
        enhanced_content = content.replace("  ", " ").replace("   ", " ")
        
        mock_enhancements = [
            {
                'type': 'readability',
                'original': content[:100] + "..." if len(content) > 100 else content,
                'enhanced': enhanced_content[:100] + "..." if len(enhanced_content) > 100 else enhanced_content,
                'rationale': 'Improved spacing and formatting for better readability',
                'confidence': 0.85
            }
        ]
        
        return {
            'enhanced_content': enhanced_content,
            'enhancements': mock_enhancements,
            'overall_confidence': 0.85,
            'processing_notes': 'Mock enhancement executed successfully'
        }
    
    def _process_enhancement_result(self, 
                                   result: Dict[str, Any], 
                                   original_content: str) -> ContentEnhancerOutput:
        """Process model output into structured result."""
        
        try:
            # Extract enhancements
            enhancements = []
            for enhancement_data in result.get('enhancements', []):
                enhancement = ContentEnhancement(
                    enhancement_id=f"enh_{len(enhancements)}",
                    enhancement_type=enhancement_data.get('type', 'general'),
                    original_text=enhancement_data.get('original', ''),
                    enhanced_text=enhancement_data.get('enhanced', ''),
                    confidence_score=enhancement_data.get('confidence', 0.5),
                    improvement_rationale=enhancement_data.get('rationale', ''),
                    metadata={
                        'timestamp': datetime.now().isoformat(),
                        'agent_id': self.agent_id
                    }
                )
                enhancements.append(enhancement)
            
            # Create structured output
            output = ContentEnhancerOutput(
                enhanced_content=result.get('enhanced_content', original_content),
                enhancements_applied=enhancements,
                overall_confidence=result.get('overall_confidence', 0.5),
                processing_metadata={
                    'agent_id': self.agent_id,
                    'version': self.version,
                    'processing_time': 'mock_timing',
                    'enhancement_count': len(enhancements),
                    'original_length': len(original_content),
                    'enhanced_length': len(result.get('enhanced_content', original_content)),
                    'processing_notes': result.get('processing_notes', ''),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return output
            
        except Exception as e:
            logger.error(f"Error processing enhancement result: {e}")
            
            # Fallback output
            return ContentEnhancerOutput(
                enhanced_content=original_content,
                enhancements_applied=[],
                overall_confidence=0.0,
                processing_metadata={
                    'error': str(e),
                    'agent_id': self.agent_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and configuration."""
        return {
            'agent_id': self.agent_id,
            'agent_type': 'subatomic_content_enhancer',
            'version': self.version,
            'capabilities': self.capabilities,
            'framework_version': 'v5',
            'layers_enabled': [
                'framing', 'context', 'reasoning', 
                'tooling', 'safety', 'output'
            ],
            'supports_inheritance': True,
            'max_input_length': 10000,
            'max_output_length': 2000
        }


# Factory function for creating content enhancer agents
def create_content_enhancer(model_client=None) -> ContentEnhancerAgent:
    """Factory function to create content enhancer subatomic agent."""
    return ContentEnhancerAgent(model_client=model_client)


# Example usage and testing
if __name__ == "__main__":
    # Create agent
    agent = create_content_enhancer()
    
    # Test content enhancement
    test_content = """
    This is a sample resume summary. I have experience in software development 
    and I worked at several companies. I am good at programming and I know 
    Python, Java, and JavaScript. I want to get a job as a senior developer.
    """
    
    context = {
        'purpose': 'resume_summary',
        'audience': 'hiring_managers',
        'target_role': 'senior_software_developer'
    }
    
    enhancement_targets = ['clarity', 'impact', 'professional_tone']
    
    # Execute enhancement
    result = agent.enhance_content(
        content=test_content,
        context=context,
        enhancement_targets=enhancement_targets
    )
    
    # Display results
    print("=== CONTENT ENHANCEMENT RESULT ===")
    print(f"Original: {test_content}")
    print(f"Enhanced: {result.enhanced_content}")
    print(f"Confidence: {result.overall_confidence}")
    print(f"Enhancements: {len(result.enhancements_applied)}")
    
    for enhancement in result.enhancements_applied:
        print(f"- {enhancement.enhancement_type}: {enhancement.improvement_rationale}")
