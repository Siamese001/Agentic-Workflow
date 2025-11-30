"""
resume_app/workflows – app_resume_research_workflow.py

Apps layer workflow for resume research and job analysis.
Performs job description analysis, keyword extraction, and thematic analysis
to provide enriched context for resume generation with LIC compliance.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging
import re

# Import apps layer components
from apps.resume_app.adapters.app_resume_engine_adapter import (
    ResumeEngineAdapter, LLMRequest
)
from apps.resume_app.adapters.app_resume_memory_adapter import (
    ResumeMemoryAdapter, MemoryQueryRequest
)
from apps.resume_app.validators.app_resume_input_validator import (
    ResumeInputValidator, ValidationResult
)


@dataclass
class JobAnalysisResult:
    """Result of job description analysis"""
    target_role: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    experience_level: str = ""
    key_responsibilities: List[str] = field(default_factory=list)
    company_context: str = ""
    industry_keywords: List[str] = field(default_factory=list)


@dataclass
class ThematicAnalysisResult:
    """Result of thematic analysis"""
    primary_themes: List[str] = field(default_factory=list)
    secondary_themes: List[str] = field(default_factory=list)
    skill_clusters: List[str] = field(default_factory=list)
    achievement_indicators: List[str] = field(default_factory=list)
    culture_fit_keywords: List[str] = field(default_factory=list)


@dataclass
class ResearchResult:
    """Complete research workflow result"""
    success: bool = False
    job_analysis: Optional[JobAnalysisResult] = None
    thematic_analysis: Optional[ThematicAnalysisResult] = None
    keyword_rankings: Dict[str, float] = field(default_factory=dict)
    competitive_insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    total_time_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResumeResearchWorkflow:
    """Apps layer workflow for resume research and job analysis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.engine_adapter = ResumeEngineAdapter(self.config)
        self.memory_adapter = ResumeMemoryAdapter(self.config)
        self.input_validator = ResumeInputValidator(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Research-specific configuration
        self.enable_memory_storage = self.config.get("enable_memory_storage", True)
        self.max_keywords_extracted = self.config.get("max_keywords_extracted", 50)
        self.enable_thematic_analysis = self.config.get("enable_thematic_analysis", True)
    
    def execute_job_research(self, job_description: str, target_role: str, 
                           company_info: Optional[str] = None) -> ResearchResult:
        """Execute complete job research workflow"""
        start_time = datetime.now()
        result = ResearchResult()
        
        try:
            self.logger.info(f"Starting job research for {target_role}")
            
            # Step 1: Job description analysis
            job_analysis = self._analyze_job_description(job_description, target_role, company_info)
            result.job_analysis = job_analysis
            
            # Step 2: Thematic analysis
            if self.enable_thematic_analysis:
                thematic_analysis = self._perform_thematic_analysis(job_description, job_analysis)
                result.thematic_analysis = thematic_analysis
            
            # Step 3: Keyword extraction and ranking
            keyword_rankings = self._extract_and_rank_keywords(job_description, job_analysis)
            result.keyword_rankings = keyword_rankings
            
            # Step 4: Competitive insights
            competitive_insights = self._generate_competitive_insights(job_analysis, keyword_rankings)
            result.competitive_insights = competitive_insights
            
            # Step 5: Generate recommendations
            recommendations = self._generate_resume_recommendations(job_analysis, result.thematic_analysis)
            result.recommendations = recommendations
            
            # Step 6: Store research results in memory if enabled
            if self.enable_memory_storage:
                self._store_research_results(result, target_role)
            
            result.success = True
            self.logger.info(f"Job research completed successfully for {target_role}")
            
        except Exception as e:
            self.logger.error(f"Job research failed: {str(e)}")
            result.metadata["error"] = str(e)
        
        # Calculate total time
        end_time = datetime.now()
        result.total_time_seconds = (end_time - start_time).total_seconds()
        result.metadata["executed_at"] = end_time.isoformat()
        
        return result
    
    def _analyze_job_description(self, job_description: str, target_role: str, 
                                company_info: Optional[str] = None) -> JobAnalysisResult:
        """Analyze job description to extract key information"""
        analysis = JobAnalysisResult(target_role=target_role)
        
        # Extract required skills
        analysis.required_skills = self._extract_skills(job_description, required=True)
        
        # Extract preferred skills
        analysis.preferred_skills = self._extract_skills(job_description, required=False)
        
        # Determine experience level
        analysis.experience_level = self._extract_experience_level(job_description)
        
        # Extract key responsibilities
        analysis.key_responsibilities = self._extract_responsibilities(job_description)
        
        # Set company context
        analysis.company_context = company_info or ""
        
        # Extract industry keywords
        analysis.industry_keywords = self._extract_industry_keywords(job_description)
        
        return analysis
    
    def _perform_thematic_analysis(self, job_description: str, 
                                  job_analysis: JobAnalysisResult) -> ThematicAnalysisResult:
        """Perform thematic analysis on job description"""
        themes = ThematicAnalysisResult()
        
        # Use L2 adapter for thematic analysis
        llm_request = LLMRequest(
            prompt=f"Analyze themes in this job description: {job_description}",
            context={
                "target_role": job_analysis.target_role,
                "required_skills": job_analysis.required_skills,
                "experience_level": job_analysis.experience_level,
                "task_type": "thematic_analysis"
            },
            task_type="thematic_analysis"
        )
        
        try:
            # Simulate thematic analysis (template-based)
            themes.primary_themes = self._extract_primary_themes(job_description)
            themes.secondary_themes = self._extract_secondary_themes(job_description)
            themes.skill_clusters = self._group_skills_into_clusters(job_analysis.required_skills)
            themes.achievement_indicators = self._extract_achievement_indicators(job_description)
            themes.culture_fit_keywords = self._extract_culture_keywords(job_description)
            
        except Exception as e:
            self.logger.warning(f"Thematic analysis failed: {str(e)}")
            # Provide fallback basic themes
            themes.primary_themes = ["technical excellence", "collaboration", "innovation"]
            themes.secondary_themes = ["problem solving", "communication"]
        
        return themes
    
    def _extract_and_rank_keywords(self, job_description: str, 
                                 job_analysis: JobAnalysisResult) -> Dict[str, float]:
        """Extract and rank keywords by importance"""
        keywords = {}
        
        # Combine all text sources
        all_text = f"{job_description} {' '.join(job_analysis.required_skills)} {' '.join(job_analysis.key_responsibilities)}"
        
        # Extract technical keywords
        technical_keywords = self._extract_technical_keywords(all_text)
        for keyword in technical_keywords:
            keywords[keyword] = keywords.get(keyword, 0) + 1.0
        
        # Extract action verbs
        action_verbs = self._extract_action_verbs(all_text)
        for verb in action_verbs:
            keywords[verb] = keywords.get(verb, 0) + 0.8
        
        # Extract industry-specific terms
        industry_terms = self._extract_industry_keywords(all_text)
        for term in industry_terms:
            keywords[term] = keywords.get(term, 0) + 0.6
        
        # Sort by importance and limit results
        sorted_keywords = dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True))
        return dict(list(sorted_keywords.items())[:self.max_keywords_extracted])
    
    def _generate_competitive_insights(self, job_analysis: JobAnalysisResult, 
                                     keyword_rankings: Dict[str, float]) -> List[str]:
        """Generate competitive insights for the job market"""
        insights = []
        
        # Analyze skill demand
        high_demand_skills = [skill for skill, score in keyword_rankings.items() if score > 1.0][:5]
        if high_demand_skills:
            insights.append(f"High-demand skills: {', '.join(high_demand_skills)}")
        
        # Experience level insights
        if job_analysis.experience_level:
            insights.append(f"Target experience level: {job_analysis.experience_level}")
        
        # Industry trends
        if job_analysis.industry_keywords:
            insights.append(f"Industry focus: {', '.join(job_analysis.industry_keywords[:3])}")
        
        # Responsibility complexity
        if len(job_analysis.key_responsibilities) > 5:
            insights.append("Role involves diverse responsibilities - emphasize adaptability")
        
        return insights
    
    def _generate_resume_recommendations(self, job_analysis: JobAnalysisResult, 
                                       thematic_analysis: Optional[ThematicAnalysisResult]) -> List[str]:
        """Generate specific resume recommendations"""
        recommendations = []
        
        # Skill-based recommendations
        if job_analysis.required_skills:
            recommendations.append(f"Emphasize these key skills: {', '.join(job_analysis.required_skills[:5])}")
        
        # Experience recommendations
        if job_analysis.experience_level in ["senior", "lead", "principal"]:
            recommendations.append("Highlight leadership and mentoring experience")
        elif job_analysis.experience_level in ["junior", "entry"]:
            recommendations.append("Focus on learning ability and growth potential")
        
        # Thematic recommendations
        if thematic_analysis:
            if "technical excellence" in thematic_analysis.primary_themes:
                recommendations.append("Include measurable technical achievements")
            if "collaboration" in thematic_analysis.primary_themes:
                recommendations.append("Showcase teamwork and cross-functional projects")
        
        # LinkedIn compliance reminder
        recommendations.append("Ensure bullet points are under 600 characters and max 5 per experience")
        
        return recommendations
    
    def _store_research_results(self, result: ResearchResult, target_role: str):
        """Store research results in memory adapter"""
        try:
            memory_request = MemoryQueryRequest(
                query_type="store_research",
                target_role=target_role,
                filters={
                    "research_data": {
                        "required_skills": result.job_analysis.required_skills if result.job_analysis else [],
                        "keyword_rankings": result.keyword_rankings,
                        "recommendations": result.recommendations,
                        "researched_at": datetime.now().isoformat()
                    }
                }
            )
            self.memory_adapter.store_research_data(memory_request)
        except Exception as e:
            self.logger.warning(f"Failed to store research results: {str(e)}")
    
    # Helper methods for extraction
    def _extract_skills(self, text: str, required: bool = True) -> List[str]:
        """Extract skills from job description"""
        # Common skill patterns
        skill_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|React|Angular|Vue|Node\.js|Django|Flask|Spring|\.NET|SQL|NoSQL|MongoDB|PostgreSQL|MySQL|AWS|Azure|GCP|Docker|Kubernetes|Git|CI/CD|Agile|Scrum|REST|GraphQL|Microservices|Machine Learning|AI|Data Science|Analytics|DevOps|Security|Testing|Unit Testing|Integration Testing)\b',
            r'\b(\w+ development|\w+ programming|\w+ engineering|\w+ design|\w+ architecture)\b'
        ]
        
        skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend(matches)
        
        # Filter and deduplicate
        unique_skills = list(set([skill.strip() for skill in skills if len(skill.strip()) > 2]))
        return unique_skills[:10]  # Limit to top 10 skills
    
    def _extract_experience_level(self, text: str) -> str:
        """Extract experience level from job description"""
        level_patterns = {
            'entry': r'\b(entry level|junior|associate|0-1|1-2)\b',
            'mid': r'\b(mid level|intermediate|2-5|3-5)\b',
            'senior': r'\b(senior|lead|5-10|6-8)\b',
            'principal': r'\b(principal|staff|8-10|10\+)\b',
            'executive': r'\b(director|vp|vice president|c-level|cto|cio)\b'
        }
        
        for level, pattern in level_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return level
        
        return "mid"  # Default assumption
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities from job description"""
        # Look for bullet points or numbered lists
        responsibility_patterns = [
            r'•\s*(.*?)(?=•|$|\n)',
            r'\*\s*(.*?)(?=\*|$|\n)',
            r'\d+\.\s*(.*?)(?=\d+\.|$|\n)'
        ]
        
        responsibilities = []
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            responsibilities.extend([resp.strip() for resp in matches if len(resp.strip()) > 10])
        
        return responsibilities[:8]  # Limit to top 8 responsibilities
    
    def _extract_industry_keywords(self, text: str) -> List[str]:
        """Extract industry-specific keywords"""
        industry_terms = [
            'fintech', 'healthcare', 'e-commerce', 'saas', 'enterprise', 'startup',
            'consulting', 'banking', 'insurance', 'retail', 'manufacturing',
            'telecommunications', 'media', 'gaming', 'education', 'government'
        ]
        
        found_terms = []
        for term in industry_terms:
            if term.lower() in text.lower():
                found_terms.append(term)
        
        return found_terms[:5]
    
    def _extract_primary_themes(self, text: str) -> List[str]:
        """Extract primary themes from job description"""
        theme_keywords = {
            'technical excellence': ['technical', 'engineering', 'development', 'programming'],
            'leadership': ['lead', 'manage', 'team', 'mentor', 'guide'],
            'innovation': ['innovate', 'create', 'design', 'build', 'develop'],
            'collaboration': ['collaborate', 'teamwork', 'partner', 'cross-functional'],
            'business impact': ['business', 'revenue', 'growth', 'impact', 'results']
        }
        
        found_themes = []
        for theme, keywords in theme_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                found_themes.append(theme)
        
        return found_themes[:3]
    
    def _extract_secondary_themes(self, text: str) -> List[str]:
        """Extract secondary themes from job description"""
        secondary_keywords = {
            'problem solving': ['solve', 'problem', 'challenge', 'solution'],
            'communication': ['communicate', 'present', 'document', 'write'],
            'analytical thinking': ['analyze', 'data', 'metrics', 'insights'],
            'adaptability': ['adapt', 'flexible', 'agile', 'pivot'],
            'quality focus': ['quality', 'testing', 'review', 'standards']
        }
        
        found_themes = []
        for theme, keywords in secondary_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                found_themes.append(theme)
        
        return found_themes[:3]
    
    def _group_skills_into_clusters(self, skills: List[str]) -> List[str]:
        """Group skills into logical clusters"""
        clusters = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#'],
            'web': ['react', 'angular', 'vue', 'html', 'css', 'node.js'],
            'database': ['sql', 'nosql', 'mongodb', 'postgresql', 'mysql'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'devops': ['ci/cd', 'git', 'jenkins', 'terraform', 'ansible']
        }
        
        found_clusters = []
        for cluster_name, cluster_skills in clusters.items():
            if any(skill.lower() in [s.lower() for s in skills] for skill in cluster_skills):
                found_clusters.append(cluster_name)
        
        return found_clusters
    
    def _extract_achievement_indicators(self, text: str) -> List[str]:
        """Extract achievement indicators from job description"""
        achievement_patterns = [
            r'\b(\d+%|\d+ percent|\d+x|\d+ times)\b',
            r'\b(increased|decreased|improved|reduced|optimized|accelerated)\b',
            r'\b(millions|billions|thousands|hundreds)\b',
            r'\b(award|recognition|certification|patent)\b'
        ]
        
        indicators = []
        for pattern in achievement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            indicators.extend(matches)
        
        return list(set(indicators))[:5]
    
    def _extract_culture_keywords(self, text: str) -> List[str]:
        """Extract culture fit keywords"""
        culture_terms = [
            'fast-paced', 'innovative', 'collaborative', 'entrepreneurial',
            'team-oriented', 'customer-focused', 'data-driven', 'agile',
            'flexible', 'inclusive', 'diverse', 'sustainable'
        ]
        
        found_terms = []
        for term in culture_terms:
            if term.lower() in text.lower():
                found_terms.append(term)
        
        return found_terms[:5]
    
    def _extract_technical_keywords(self, text: str) -> List[str]:
        """Extract technical keywords"""
        # This is a simplified version - in production would use NLP
        technical_words = re.findall(r'\b[A-Za-z]+\b', text)
        # Filter for likely technical terms (length > 3 and contains certain patterns)
        technical_keywords = []
        for word in technical_words:
            if (len(word) > 3 and 
                (any(char in word for char in 'xyz') or 
                 word.endswith('ion') or 
                 word.endswith('ment') or
                 word.endswith('ness') or
                 word.endswith('ity') or
                 word[0].isupper())):
                technical_keywords.append(word.lower())
        
        return list(set(technical_keywords))[:20]
    
    def _extract_action_verbs(self, text: str) -> List[str]:
        """Extract action verbs from text"""
        action_verbs = [
            'develop', 'design', 'implement', 'create', 'build', 'lead',
            'manage', 'optimize', 'improve', 'analyze', 'coordinate',
            'collaborate', 'drive', 'support', 'maintain', 'enhance'
        ]
        
        found_verbs = []
        for verb in action_verbs:
            if verb in text.lower():
                found_verbs.append(verb)
        
        return found_verbs[:10]

