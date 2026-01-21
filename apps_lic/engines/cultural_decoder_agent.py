"""Cultural Decoder Agent - Company Culture Alignment.

This agent analyzes company values and subtly rewrites candidate narratives
to align with the target company's specific cultural DNA and dialect.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pydantic import BaseModel, Field, validator

from .models import LLMResponse


logger = logging.getLogger(__name__)


class WritingStyle(str, Enum):
    """Company writing styles."""
    NARRATIVE = "Narrative"
    BULLET_HEAVY = "Bullet-heavy"
    ACADEMIC = "Academic"
    TECHNICAL = "Technical"
    STORYTELLING = "Storytelling"


class CompanyDNA(BaseModel):
    """DNA profile of a company's culture."""
    
    company_name: str = Field(..., description="Company identifier")
    core_values: List[str] = Field(default_factory=list, description="Core company values")
    writing_style: WritingStyle = Field(default=WritingStyle.NARRATIVE, description="Preferred writing style")
    buzzwords: List[str] = Field(default_factory=list, description="Company-specific terminology")
    value_phrases: Dict[str, str] = Field(default_factory=dict, description="Value to phrase mapping")
    forbidden_words: List[str] = Field(default_factory=list, description="Words to avoid")
    
    @validator('core_values')
    def validate_values(cls, v):
        """Ensure values are properly formatted."""
        return [val.strip().title() for val in v if val.strip()]


class CulturallyAlignedContent(BaseModel):
    """Content aligned with company culture."""
    
    original_text: str = Field(..., description="Original content")
    aligned_text: str = Field(..., description="Culturally aligned content")
    alignment_rationale: str = Field(..., description="Explanation of changes")
    alignment_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Cultural alignment score")
    key_changes: List[str] = Field(default_factory=list, description="Key changes made")


class SimpleAgentBase:
    """Simple base class for standalone agents."""
    
    def __init__(self, name: str, model_name: str = "gpt-4"):
        """Initialize the agent.
        
        Args:
            name: Agent name for logging
            model_name: LLM model to use
        """
        self.name = name
        self.model_name = model_name
        logger.info(f"Initialized {self.__class__.__name__}: model={model_name}")


class CulturalDecoderAgent(SimpleAgentBase):
    """Agent that adapts content to match company culture."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the Cultural Decoder Agent.
        
        Args:
            model_name: LLM model to use for cultural adaptation
        """
        super().__init__(name="Cultural Decoder", model_name=model_name)
        
        # Pre-loaded DNA profiles for major tech companies
        self.dna_profiles = {
            "Amazon": CompanyDNA(
                company_name="Amazon",
                core_values=["Customer Obsession", "Ownership", "Invent and Simplify", 
                           "Are Right, A Lot", "Learn and Be Curious", "Hire and Develop the Best",
                           "Insist on the Highest Standards", "Think Big", "Bias for Action",
                           "Frugality", "Earn Trust", "Deliver Results"],
                writing_style=WritingStyle.NARRATIVE,
                buzzwords=["Bar Raiser", "6-Pager", "Two-Pizza Team", "Single Threaded Owner", "Disagree and Commit"],
                value_phrases={
                    "Customer Obsession": ["customer-obsessed", "working backwards from the customer"],
                    "Ownership": ["took ownership", "end-to-end ownership", "driver"],
                    "Deliver Results": ["delivered results", "measured impact", "metrics-driven"],
                    "Bias for Action": ["bias for action", "calculated risks", "moved quickly"]
                },
                forbidden_words=["synergy", "paradigm", "leverage", "optimize"]
            ),
            
            "Google": CompanyDNA(
                company_name="Google",
                core_values=["Focus on the user", "Technical excellence", "Scale", "Innovation", 
                           "Collaboration", "10x thinking"],
                writing_style=WritingStyle.TECHNICAL,
                buzzwords=["20% Time", "TGIF", "OKR", "Design Doc", "Launch", "Scale", "Moonshot"],
                value_phrases={
                    "Focus on the user": ["user-centric", "user-focused", "user experience first"],
                    "Technical excellence": ["technically rigorous", "elegant solutions", "robust architecture"],
                    "Scale": ["at scale", "global scale", "billions of users"],
                    "Innovation": ["breakthrough", "novel approach", "cutting-edge"]
                },
                forbidden_words=["quick win", "low-hanging fruit", "synergy"]
            ),
            
            "Meta": CompanyDNA(
                company_name="Meta",
                core_values=["Move Fast", "Build Awesome Things", "Focus on Impact", "Be Open", 
                           "Social Value", "Bold Action"],
                writing_style=WritingStyle.BULLET_HEAVY,
                buzzwords=["Move Fast", "Hackathon", "Zuck", "Meta", "Horizon", "Quest"],
                value_phrases={
                    "Move Fast": ["moved fast", "rapid iteration", "ship early"],
                    "Build Awesome Things": ["built impactful products", "game-changing", "revolutionary"],
                    "Focus on Impact": ["measurable impact", "billion-user impact", "moved the needle"],
                    "Bold Action": ["bold bets", "audacious goals", "challenged the status quo"]
                },
                forbidden_words=["enterprise", "corporate", "bureaucracy"]
            ),
            
            "Netflix": CompanyDNA(
                company_name="Netflix",
                core_values=["Judgment", "Communication", "Curiosity", "Courage", "Passion", 
                           "Selflessness", "Innovation", "Inclusion", "Integrity", "Impact"],
                writing_style=WritingStyle.STORYTELLING,
                buzzwords=["Context not Control", "High Performance", "No Rules Rules", "Keeper Test", 
                          "Radical Candor", "Freedom and Responsibility"],
                value_phrases={
                    "Context not Control": ["provided context", "empowered teams", "delegated effectively"],
                    "High Performance": ["high-performing team", "stunning colleagues", "top talent"],
                    "Freedom and Responsibility": ["took ownership", "acted with freedom", "responsible freedom"],
                    "Judgment": ["sound judgment", "good instincts", "wise decisions"]
                },
                forbidden_words=["process", "procedure", "protocol", "approval chain"]
            ),
            
            "Stripe": CompanyDNA(
                company_name="Stripe",
                core_values=["Users First", "Rigorous Thinking", "Optimism", "Trust", "Macro-optimism",
                           "Micro-pessimism", "Move with Urgency"],
                writing_style=WritingStyle.TECHNICAL,
                buzzwords=["API", "Infrastructure", "Payments", "Developers", "Elegance", "Simplicity"],
                value_phrases={
                    "Users First": ["developer-first", "user-obsessed", "solved real user problems"],
                    "Rigorous Thinking": ["thoughtful approach", "deep analysis", "first principles"],
                    "Elegance": ["elegant solution", "beautiful API", "thoughtful design"],
                    "Move with Urgency": ["moved with urgency", "rapid execution", "focused delivery"]
                },
                forbidden_words=["enterprise software", "B2B", "sales-driven"]
            )
        }
        
        # Default profile for unknown companies
        self.default_dna = CompanyDNA(
            company_name="Modern Agile",
            core_values=["Collaboration", "Innovation", "Excellence", "Agility", "Customer Focus"],
            writing_style=WritingStyle.NARRATIVE,
            buzzwords=["Agile", "Scrum", "Sprint", "MVP", "Iterate", "Pivot"],
            value_phrases={
                "Collaboration": ["cross-functional", "team player", "collaborative approach"],
                "Innovation": ["innovative solutions", "creative problem-solving", "breakthrough thinking"],
                "Excellence": ["high-quality", "best practices", "continuous improvement"],
                "Agility": ["agile mindset", "quick adaptation", "flexible approach"]
            },
            forbidden_words=[]
        )
    
    def _load_dna(self, company_name: str, about_text: Optional[str] = None) -> CompanyDNA:
        """Load company DNA, either from pre-loaded profiles or by inference.
        
        Args:
            company_name: Name of the target company
            about_text: Optional About page text for dynamic inference
            
        Returns:
            CompanyDNA profile
        """
        # Check pre-loaded profiles first
        for name, dna in self.dna_profiles.items():
            if company_name.lower() in name.lower() or name.lower() in company_name.lower():
                logger.info(f"Using pre-loaded DNA profile for {name}")
                return dna
        
        # If no pre-loaded profile and no about text, return default
        if not about_text:
            logger.warning(f"No DNA profile for {company_name}, using default")
            return self.default_dna
        
        # Dynamic inference from About text
        logger.info(f"Inferring DNA for {company_name} from About text")
        return self._infer_dna_from_text(company_name, about_text)
    
    async def _infer_dna_from_text(self, company_name: str, about_text: str) -> CompanyDNA:
        """Infer company DNA from About page text.
        
        Args:
            company_name: Name of the company
            about_text: About page text
            
        Returns:
            Inferred CompanyDNA
        """
        prompt = f"""
        Analyze this company's About page and extract their cultural DNA:
        
        Company: {company_name}
        
        About: {about_text[:2000]}
        
        Return JSON with:
        {{
            "core_values": ["value1", "value2", ...],
            "writing_style": "Narrative|Bullet-heavy|Technical|Academic|Storytelling",
            "buzzwords": ["term1", "term2", ...],
            "key_themes": ["theme1", "theme2", ...]
        }}
        """
        
        try:
            response = await self._call_llm(prompt, temperature=0.1)
            import json
            extracted = json.loads(response.content.strip())
            
            return CompanyDNA(
                company_name=company_name,
                core_values=extracted.get("core_values", []),
                writing_style=WritingStyle(extracted.get("writing_style", "Narrative")),
                buzzwords=extracted.get("buzzwords", []),
                value_phrases={}
            )
        except Exception as e:
            logger.error(f"Failed to infer DNA: {e}")
            return self.default_dna
    
    async def rewrite_for_culture(
        self, 
        original_text: str, 
        company_dna: CompanyDNA,
        text_type: str = "resume"
    ) -> CulturallyAlignedContent:
        """Rewrite text to align with company culture.
        
        Args:
            original_text: Original text to rewrite
            company_dna: Target company DNA
            text_type: Type of text (resume, cover_letter, etc.)
            
        Returns:
            Culturally aligned content
        """
        # Build the adaptation prompt
        values_str = ", ".join(company_dna.core_values[:5])  # Limit to top 5
        buzzwords_str = ", ".join(company_dna.buzzwords[:5])
        
        prompt = f"""
        You are an expert career coach helping a candidate align their narrative with {company_dna.company_name}'s culture.
        
        REWRITE RULES:
        1. Be SUBTLE and AUTHENTIC - do not caricature or stuff keywords unnaturally
        2. Weave in these values naturally: {values_str}
        3. Use this writing style: {company_dna.writing_style.value}
        4. If appropriate, subtly include these terms: {buzzwords_str}
        5. Avoid these words: {", ".join(company_dna.forbidden_words)}
        
        Original {text_type}:
        "{original_text}"
        
        Provide:
        1. Rewritten text that sounds like it belongs to a high-performing leader at {company_dna.company_name}
        2. Brief rationale for key changes
        
        Format as JSON:
        {{
            "rewritten_text": "...",
            "rationale": "...",
            "key_changes": ["change1", "change2", ...]
        }}
        """
        
        try:
            response = await self._call_llm(prompt, temperature=0.3)
            import json
            result = json.loads(response.content.strip())
            
            # Calculate alignment score
            alignment_score = self._calculate_alignment_score(
                result["rewritten_text"], 
                company_dna
            )
            
            return CulturallyAlignedContent(
                original_text=original_text,
                aligned_text=result["rewritten_text"],
                alignment_rationale=result["rationale"],
                alignment_score=alignment_score,
                key_changes=result.get("key_changes", [])
            )
            
        except Exception as e:
            logger.error(f"Failed to rewrite for culture: {e}")
            return CulturallyAlignedContent(
                original_text=original_text,
                aligned_text=original_text,
                alignment_rationale="Failed to adapt - using original",
                alignment_score=0.0,
                key_changes=[]
            )
    
    def audit_fit(self, text: str, company_name: str) -> Dict[str, Any]:
        """Audit text for cultural alignment with target company.
        
        Args:
            text: Text to audit
            company_name: Target company name
            
        Returns:
            Audit results with score and suggestions
        """
        dna = self._load_dna(company_name)
        
        # Check for alignment indicators
        alignment_indicators = []
        misalignment_indicators = []
        
        # Check buzzword usage
        buzzword_matches = [bw for bw in dna.buzzwords if bw.lower() in text.lower()]
        if buzzword_matches:
            alignment_indicators.append(f"Uses company terminology: {', '.join(buzzword_matches)}")
        
        # Check forbidden words
        forbidden_matches = [fw for fw in dna.forbidden_words if fw.lower() in text.lower()]
        if forbidden_matches:
            misalignment_indicators.append(f"Uses discouraged words: {', '.join(forbidden_matches)}")
        
        # Check value alignment
        value_mentions = []
        for value, phrases in dna.value_phrases.items():
            for phrase in phrases:
                if phrase in text.lower():
                    value_mentions.append(value)
                    break
        
        if value_mentions:
            alignment_indicators.append(f"Reflects company values: {', '.join(value_mentions)}")
        
        # Calculate score
        base_score = 0.5
        for indicator in alignment_indicators:
            base_score += 0.15
        for indicator in misalignment_indicators:
            base_score -= 0.2
        
        score = max(0.0, min(1.0, base_score))
        
        # Generate suggestions
        suggestions = []
        if score < 0.7:
            suggestions.append(f"Incorporate language that reflects {company_name}'s core values")
            if not buzzword_matches and dna.buzzwords:
                suggestions.append(f"Consider using relevant terminology like '{dna.buzzwords[0]}'")
            if forbidden_matches:
                suggestions.append(f"Replace '{forbidden_matches[0]}' with more aligned language")
        
        return {
            "company": company_name,
            "alignment_score": score,
            "alignment_indicators": alignment_indicators,
            "misalignment_indicators": misalignment_indicators,
            "suggestions": suggestions,
            "grade": self._get_grade(score)
        }
    
    def _calculate_alignment_score(self, text: str, dna: CompanyDNA) -> float:
        """Calculate how well text aligns with company DNA.
        
        Args:
            text: Text to evaluate
            dna: Company DNA to compare against
            
        Returns:
            Alignment score (0-1)
        """
        score = 0.5  # Base score
        
        text_lower = text.lower()
        
        # Check buzzword alignment
        buzzword_count = sum(1 for bw in dna.buzzwords if bw.lower() in text_lower)
        score += min(0.2, buzzword_count * 0.05)
        
        # Check value phrase alignment
        value_phrase_count = sum(
            1 for phrases in dna.value_phrases.values()
            for phrase in phrases
            if phrase in text_lower
        )
        score += min(0.2, value_phrase_count * 0.05)
        
        # Check forbidden words
        forbidden_count = sum(1 for fw in dna.forbidden_words if fw.lower() in text_lower)
        score -= min(0.3, forbidden_count * 0.1)
        
        return max(0.0, min(1.0, score))
    
    def _get_grade(self, score: float) -> str:
        """Convert alignment score to grade.
        
        Args:
            score: Alignment score (0-1)
            
        Returns:
            Grade letter
        """
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    async def _call_llm(self, prompt: str, temperature: float = 0.3) -> LLMResponse:
        """Call the LLM with the given prompt.
        
        Args:
            prompt: Prompt to send to LLM
            temperature: Sampling temperature
            
        Returns:
            LLM response
        """
        try:
            # Import here to avoid circular imports
            from .multi_provider_clients import get_client, Provider
            
            # Get Anthropic client
            client = get_client(Provider.ANTHROPIC)
            
            # Call LLM
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content
            
            return LLMResponseImpl(response.content[0].text)
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            # Return fallback response
            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content
            
            return LLMResponseImpl('{"rewritten_text": "sample", "rationale": "sample", "key_changes": []}')
