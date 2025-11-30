# Message Generation Executor - L2 Execution Layer
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class GenerationContext:
    """Enhanced generation context with comprehensive parameters"""
    prompt: str = ""
    task_type: str = "general"  # summary, bullet, skills, optimization
    target_role: str = ""
    experience_level: str = "mid"
    target_company: Optional[str] = None
    optimization_focus: List[str] = None
    tone: str = "professional"
    length_constraint: Optional[str] = None  # short, medium, long
    keyword_requirements: List[str] = None
    compliance_rules: Dict[str, Any] = None
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.optimization_focus is None:
            self.optimization_focus = ["impact", "readability"]
        if self.keyword_requirements is None:
            self.keyword_requirements = []
        if self.compliance_rules is None:
            self.compliance_rules = {}
        if self.parameters is None:
            self.parameters = {}

@dataclass
class MessageResult:
    """Enhanced message generation result with comprehensive metadata"""
    content: str = ""
    confidence_score: float = 0.0
    token_usage: int = 0
    generation_time_ms: int = 0
    metadata: Dict[str, Any] = None
    quality_metrics: Dict[str, float] = None
    compliance_check: Dict[str, bool] = None
    enhancement_applied: List[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.quality_metrics is None:
            self.quality_metrics = {}
        if self.compliance_check is None:
            self.compliance_check = {}
        if self.enhancement_applied is None:
            self.enhancement_applied = []

@dataclass
class MessageSection:
    """Enhanced message section with detailed metadata"""
    section_type: str = ""
    content: str = ""
    priority: int = 0
    word_count: int = 0
    keyword_density: float = 0.0
    readability_score: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class MessageGenerationExecutor:
    """Comprehensive message generation execution engine with real business logic"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.generation_templates = self._load_generation_templates()
        self.compliance_rules = self._load_compliance_rules()
        self.quality_thresholds = self._load_quality_thresholds()
        self.generation_history = []

    def _load_generation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive generation templates"""
        return {
            "professional_summary": {
                "entry_level": (
                    "Eager to contribute technical skills and fresh perspectives to "
                    "drive innovation and team success."
                ),
                "mid_level": (
                    "Proven track record of {key_achievements} and expertise in {technical_skills}."
                ),
                "senior_level": (
                    "Seasoned leader with demonstrated success in {key_achievements} and "
                    "deep expertise in {technical_skills}."
                ),
                "executive": (
                    "Strategic driver of {key_achievements} with proven ability to transform "
                    "organizations and deliver exceptional business results."
                )
            },
            "bullet_enhancement": {
                "action_verbs": [
                    "developed", "implemented", "architected", "led", "optimized", 
                    "transformed", "launched", "scaled"
                ],
                "impact_patterns": [
                    "resulting in {metric} improvement", "driving {metric} growth", 
                    "achieving {metric} efficiency", "delivering {metric} value"
                ],
                "technical_keywords": [
                    "machine learning", "cloud architecture", "data analytics", 
                    "microservices", "devops", "automation"
                ]
            },
            "skills_optimization": {
                "technical_priority": [
                    "Python", "Machine Learning", "Cloud Computing", "DevOps", "Data Engineering"
                ],
                "leadership_priority": [
                    "Team Leadership", "Project Management", "Strategic Planning", 
                    "Stakeholder Management"
                ],
                "tools_priority": [
                    "AWS", "Azure", "Docker", "Kubernetes", "Git", "Jenkins"
                ]
            }
        }

    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load platform compliance rules"""
        return {
            "linkedin": {
                "max_summary_chars": 2000,
                "max_bullet_chars": 600,
                "max_bullets_per_experience": 5,
                "required_sections": ["experience", "education"],
                "keyword_density_min": 0.02,
                "keyword_density_max": 0.06
            },
            "ats_friendly": {
                "standard_section_names": True,
                "avoid_special_characters": True,
                "readability_score_min": 60,
                "bullet_format": "action_verb + impact + metric"
            },
            "general": {
                "min_word_count_summary": 50,
                "max_word_count_summary": 150,
                "min_word_count_bullet": 15,
                "max_word_count_bullet": 25
            }
        }

    def _load_quality_thresholds(self) -> Dict[str, float]:
        """Load quality assessment thresholds"""
        return {
            "confidence_threshold": 0.7,
            "readability_threshold": 65.0,
            "keyword_density_min": 0.02,
            "keyword_density_max": 0.06,
            "impact_score_threshold": 0.6,
            "completeness_threshold": 0.8
        }

    def execute(self, context: GenerationContext) -> MessageResult:
        """Execute comprehensive message generation"""
        start_time = datetime.now()

        # Route to appropriate generation method
        if context.task_type == "professional_summary":
            result = self._generate_professional_summary(context)
        elif context.task_type == "bullet_enhancement":
            result = self._enhance_bullet(context)
        elif context.task_type == "skills_optimization":
            result = self._optimize_skills(context)
        elif context.task_type == "section_generation":
            result = self._generate_section(context)
        else:
            result = self._generate_general_content(context)

        # Calculate generation time
        generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
        result.generation_time_ms = generation_time

        # Apply compliance checks
        result.compliance_check = self._check_compliance(result.content, context)

        # Calculate quality metrics
        result.quality_metrics = self._calculate_quality_metrics(result.content, context)

        # Store generation history
        self.generation_history.append({
            "timestamp": datetime.now().isoformat(),
            "task_type": context.task_type,
            "context_summary": self._create_context_summary(context),
            "result_summary": {
                "word_count": len(result.content.split()),
                "confidence": result.confidence_score,
                "compliance_passed": all(result.compliance_check.values())
            }
        })

        return result

    def _generate_professional_summary(self, context: GenerationContext) -> MessageResult:
        """Generate professional summary with role-specific logic"""
        templates = self.generation_templates["professional_summary"]
        template = templates.get(context.experience_level, templates["mid"])

        # Extract key information
        key_areas = self._extract_key_areas(context.prompt, context.target_role)
        key_achievements = self._extract_key_achievements(context.prompt)
        technical_skills = self._extract_technical_skills(context.prompt)
        years_experience = self._estimate_experience_from_prompt(context.prompt)

        # Generate summary
        summary = template.format(
            target_role=context.target_role,
            years=years_experience,
            key_areas=", ".join(key_areas),
            key_achievements=", ".join(key_achievements),
            technical_skills=", ".join(technical_skills)
        )

        # Apply optimizations
        if "keywords" in context.optimization_focus:
            summary = self._optimize_keywords(summary, context.keyword_requirements)

        if "impact" in context.optimization_focus:
            summary = self._enhance_impact_language(summary)

        # Apply length constraints
        if context.length_constraint:
            summary = self._apply_length_constraint(summary, context.length_constraint)

        return MessageResult(
            content=summary,
            confidence_score=0.85,
            token_usage=len(summary.split()),
            metadata={
                "template_used": context.experience_level,
                "key_areas": key_areas,
                "achievements_highlighted": len(key_achievements)
            },
            enhancement_applied=["template_generation", "keyword_optimization", "impact_enhancement"]
        )

    def _enhance_bullet(self, context: GenerationContext) -> MessageResult:
        """Enhance resume bullet with comprehensive business logic"""
        original_bullet = context.prompt.strip()

        if not original_bullet:
            return MessageResult(
                content="",
                confidence_score=0.0,
                metadata={"error": "Empty bullet provided"}
            )

        enhanced_bullet = original_bullet
        enhancements_applied = []

        # Apply action verb enhancement
        if not self._has_action_verb(enhanced_bullet):
            enhanced_bullet = self._add_action_verb(enhanced_bullet, context.target_role)
            enhancements_applied.append("action_verb")

        # Apply quantification
        if not self._has_quantification(enhanced_bullet):
            enhanced_bullet = self._add_quantification(enhanced_bullet, context.target_role)
            enhancements_applied.append("quantification")

        # Apply role-specific keywords
        enhanced_bullet = self._add_role_keywords(enhanced_bullet, context.target_role, context.keyword_requirements)
        enhancements_applied.append("role_keywords")

        # Apply impact language
        if "impact" in context.optimization_focus:
            enhanced_bullet = self._enhance_impact_language(enhanced_bullet)
            enhancements_applied.append("impact_enhancement")

        # Check compliance
        if len(enhanced_bullet) > self.compliance_rules["linkedin"]["max_bullet_chars"]:
            enhanced_bullet = self._truncate_bullet(enhanced_bullet)
            enhancements_applied.append("compliance_truncation")

        confidence = self._calculate_bullet_confidence(original_bullet, enhanced_bullet, context)

        return MessageResult(
            content=enhanced_bullet,
            confidence_score=confidence,
            token_usage=len(enhanced_bullet.split()),
            metadata={
                "original_length": len(original_bullet),
                "enhanced_length": len(enhanced_bullet),
                "enhancement_count": len(enhancements_applied)
            },
            enhancement_applied=enhancements_applied
        )

    def _optimize_skills(self, context: GenerationContext) -> MessageResult:
        """Optimize skills section with strategic prioritization"""
        skills_templates = self.generation_templates["skills_optimization"]

        # Parse skills from context
        technical_skills = context.parameters.get("technical_skills", [])
        leadership_skills = context.parameters.get("leadership_skills", [])
        tools = context.parameters.get("tools", [])

        # Prioritize based on target role
        prioritized_tech = self._prioritize_skills(technical_skills, skills_templates["technical_priority"], context.target_role)
        prioritized_leadership = self._prioritize_skills(leadership_skills, skills_templates["leadership_priority"], context.target_role)
        prioritized_tools = self._prioritize_skills(tools, skills_templates["tools_priority"], context.target_role)

        # Generate optimized skills content
        skills_content = self._format_skills_section(
            prioritized_tech, prioritized_leadership, prioritized_tools, context
        )

        return MessageResult(
            content=skills_content,
            confidence_score=0.8,
            token_usage=len(skills_content.split()),
            metadata={
                "technical_skills_count": len(prioritized_tech),
                "leadership_skills_count": len(prioritized_leadership),
                "tools_count": len(prioritized_tools)
            },
            enhancement_applied=["skill_prioritization", "role_alignment", "formatting"]
        )

    def _generate_section(self, context: GenerationContext) -> MessageResult:
        """Generate specific resume section"""
        section_type = context.parameters.get("section_type", "general")

        if section_type == "experience":
            return self._generate_experience_section(context)
        elif section_type == "education":
            return self._generate_education_section(context)
        elif section_type == "projects":
            return self._generate_projects_section(context)
        else:
            return self._generate_general_content(context)

    def _generate_general_content(self, context: GenerationContext) -> MessageResult:
        """Generate general content with basic logic"""
        content = f"Generated content for {context.task_type} related to {context.target_role}"

        if context.target_company:
            content += f" tailored for {context.target_company}"

        return MessageResult(
            content=content,
            confidence_score=0.6,
            token_usage=len(content.split()),
            metadata={"generation_type": "general"}
        )

    def _extract_key_areas(self, prompt: str, target_role: str) -> List[str]:
        """Extract key areas of expertise from prompt"""
        common_areas = {
            "ai_engineer": ["Machine Learning", "AI Systems", "Data Engineering"],
            "technical_lead": ["System Architecture", "Team Leadership", "Technical Strategy"],
            "data_scientist": ["Data Analytics", "Statistical Modeling", "Business Intelligence"],
            "executive": ["Strategic Planning", "Business Development", "Organizational Leadership"]
        }

        # Extract from prompt first
        prompt_areas = self._extract_keywords_from_text(prompt, limit=5)

        # Add role-specific areas
        role_areas = common_areas.get(target_role.lower().replace(" ", "_"), ["Technology", "Innovation"])

        return list(set(prompt_areas + role_areas))[:5]

    def _extract_key_achievements(self, prompt: str) -> List[str]:
        """Extract key achievements from prompt"""
        achievement_patterns = [
            r"(improved|increased|reduced|optimized|achieved|delivered|launched|scaled)\s+[^.]*",
            r"(led|managed|directed|oversaw)\s+[^.]*",
            r"(developed|built|created|implemented|architected)\s+[^.]*"
        ]

        achievements = []
        for pattern in achievement_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            achievements.extend(matches[:2])  # Take max 2 per pattern

        return achievements[:5]

    def _extract_technical_skills(self, prompt: str) -> List[str]:
        """Extract technical skills from prompt"""
        technical_keywords = [
            "python", "java", "javascript", "aws", "azure", "docker", "kubernetes",
            "machine learning", "ai", "deep learning", "data science", "analytics",
            "react", "node.js", "tensorflow", "pytorch", "sql", "nosql"
        ]

        found_skills = []
        prompt_lower = prompt.lower()
        for skill in technical_keywords:
            if skill in prompt_lower:
                found_skills.append(skill)

        return found_skills[:8]

    def _estimate_experience_from_prompt(self, prompt: str) -> str:
        """Estimate years of experience from prompt"""
        experience_patterns = [
            r"(\d+)\+?\s*years?",
            r"(\d+)\s*-\s*(\d+)\s*years?"
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1)

        # Default based on role seniority indicators
        if any(word in prompt.lower() for word in ["senior", "lead", "principal"]):
            return "8+"
        elif any(word in prompt.lower() for word in ["junior", "entry", "associate"]):
            return "2-3"
        else:
            return "5"

    def _optimize_keywords(self, content: str, keyword_requirements: List[str]) -> str:
        """Optimize content for keyword density"""
        if not keyword_requirements:
            return content

        # Simple keyword optimization - in production would use more sophisticated NLP
        optimized_content = content
        for keyword in keyword_requirements[:3]:  # Limit to avoid over-optimization
            if keyword.lower() not in optimized_content.lower():
                # Add keyword in natural way
                optimized_content += f" with expertise in {keyword}"

        return optimized_content

    def _enhance_impact_language(self, content: str) -> str:
        """Enhance content with impact-focused language"""
        impact_replacements = {
            "responsible for": "drove",
            "worked on": "delivered",
            "helped with": "enabled",
            "participated in": "contributed to",
            "involved in": "spearheaded"
        }

        enhanced_content = content
        for old_phrase, new_phrase in impact_replacements.items():
            enhanced_content = enhanced_content.replace(old_phrase, new_phrase)

        return enhanced_content

    def _apply_length_constraint(self, content: str, constraint: str) -> str:
        """Apply length constraints to content"""
        words = content.split()

        if constraint == "short":
            return " ".join(words[:30])
        elif constraint == "medium":
            return " ".join(words[:60])
        elif constraint == "long":
            return " ".join(words[:100])

        return content

    def _has_action_verb(self, bullet: str) -> bool:
        """Check if bullet starts with action verb"""
        action_verbs = ["led", "developed", "implemented", "architected", "managed", "optimized",
                       "built", "created", "improved", "reduced", "increased", "launched", "scaled"]

        first_word = bullet.lower().split()[0] if bullet.split() else ""
        return first_word in action_verbs

    def _add_action_verb(self, bullet: str, target_role: str) -> str:
        """Add appropriate action verb to bullet"""
        role_verbs = {
            "ai_engineer": "Developed",
            "technical_lead": "Led",
            "data_scientist": "Analyzed",
            "executive": "Directed"
        }

        verb = role_verbs.get(target_role.lower().replace(" ", "_"), "Developed")
        return f"{verb} {bullet[0].lower() + bullet[1:] if bullet else ''}"

    def _has_quantification(self, bullet: str) -> bool:
        """Check if bullet has quantifiable metrics"""
        quantifiable_patterns = [r"\d+%", r"\$\d+", r"\d+x", r"by \d+", r"\d+fold"]
        return any(re.search(pattern, bullet) for pattern in quantifiable_patterns)

    def _add_quantification(self, bullet: str, target_role: str) -> str:
        """Add quantification to bullet"""
        if "improved" in bullet.lower():
            return f"{bullet}, resulting in 25% improvement in efficiency"
        elif "reduced" in bullet.lower():
            return f"{bullet}, cutting costs by 30%"
        elif "increased" in bullet.lower():
            return f"{bullet}, driving 40% growth in key metrics"
        else:
            return f"{bullet}, delivering measurable business impact"

    def _add_role_keywords(self, bullet: str, target_role: str, keyword_requirements: List[str]) -> str:
        """Add role-specific keywords to bullet"""
        role_keywords = {
            "ai_engineer": ["machine learning", "AI", "algorithms", "models"],
            "technical_lead": ["architecture", "scalability", "leadership", "team"],
            "data_scientist": ["analytics", "insights", "data", "statistical"],
            "executive": ["strategic", "business", "revenue", "transformation"]
        }

        keywords = role_keywords.get(target_role.lower().replace(" ", "_"), [])
        all_keywords = keywords + keyword_requirements

        # Add up to 2 keywords naturally
        added_count = 0
        for keyword in all_keywords:
            if keyword.lower() not in bullet.lower() and added_count < 2:
                bullet += f" using advanced {keyword}"
                added_count += 1

        return bullet

    def _truncate_bullet(self, bullet: str) -> str:
        """Truncate bullet to comply with character limits"""
        max_chars = self.compliance_rules["linkedin"]["max_bullet_chars"]
        if len(bullet) <= max_chars:
            return bullet

        # Truncate at word boundary
        truncated = bullet[:max_chars-3]
        last_space = truncated.rfind(" ")
        if last_space > max_chars - 20:
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."

    def _calculate_bullet_confidence(self, original: str, enhanced: str, context: GenerationContext) -> float:
        """Calculate confidence score for bullet enhancement"""
        base_confidence = 0.7

        # Increase confidence based on enhancements applied
        if self._has_action_verb(enhanced):
            base_confidence += 0.1

        if self._has_quantification(enhanced):
            base_confidence += 0.1

        # Check keyword inclusion
        if context.keyword_requirements:
            keyword_matches = sum(1 for kw in context.keyword_requirements
                                if kw.lower() in enhanced.lower())
            base_confidence += (keyword_matches / len(context.keyword_requirements)) * 0.1

        return min(base_confidence, 0.95)

    def _prioritize_skills(self, skills: List[str], priority_list: List[str], target_role: str) -> List[str]:
        """Prioritize skills based on role requirements"""
        if not skills:
            return []

        # Create priority mapping
        priority_dict = {skill.lower(): idx for idx, skill in enumerate(priority_list)}

        # Sort skills by priority
        prioritized = sorted(skills, key=lambda x: priority_dict.get(x.lower(), 999))

        return prioritized[:10]  # Return top 10

    def _format_skills_section(self, technical: List[str], leadership: List[str],
                              tools: List[str], context: GenerationContext) -> str:
        """Format skills section professionally"""
        sections = []

        if technical:
            sections.append(f"Technical Skills: {', '.join(technical)}")

        if leadership:
            sections.append(f"Leadership Skills: {', '.join(leadership)}")

        if tools:
            sections.append(f"Tools & Technologies: {', '.join(tools)}")

        return "\n\n".join(sections)

    def _generate_experience_section(self, context: GenerationContext) -> MessageResult:
        """Generate experience section"""
        return MessageResult(
            content="Professional experience section with role-specific achievements and quantified impacts.",
            confidence_score=0.7,
            metadata={"section_type": "experience"}
        )

    def _generate_education_section(self, context: GenerationContext) -> MessageResult:
        """Generate education section"""
        return MessageResult(
            content="Education section highlighting relevant degrees, certifications, and academic achievements.",
            confidence_score=0.7,
            metadata={"section_type": "education"}
        )

    def _generate_projects_section(self, context: GenerationContext) -> MessageResult:
        """Generate projects section"""
        return MessageResult(
            content="Projects section showcasing key technical projects, innovations, and practical applications.",
            confidence_score=0.7,
            metadata={"section_type": "projects"}
        )

    def _check_compliance(self, content: str, context: GenerationContext) -> Dict[str, bool]:
        """Check content compliance with platform rules"""
        compliance = {}

        # LinkedIn compliance
        if context.compliance_rules.get("linkedin", True):
            compliance["linkedin_length"] = len(content) <= self.compliance_rules["linkedin"]["max_summary_chars"]
            compliance["linkedin_keyword_density"] = self._check_keyword_density(content)

        # ATS compliance
        if context.compliance_rules.get("ats_friendly", True):
            compliance["ats_readable"] = self._check_readability(content)
            compliance["ats_format"] = not self._has_special_characters(content)

        return compliance

    def _calculate_quality_metrics(self, content: str, context: GenerationContext) -> Dict[str, float]:
        """Calculate comprehensive quality metrics"""
        return {
            "readability_score": self._calculate_readability(content),
            "keyword_density": self._calculate_keyword_density(content),
            "impact_score": self._calculate_impact_score(content),
            "completeness_score": self._calculate_completeness(content, context)
        }

    def _extract_keywords_from_text(self, text: str, limit: int = 10) -> List[str]:
        """Extract keywords from text using heuristics"""
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:limit]]

    def _check_keyword_density(self, content: str) -> bool:
        """Check if keyword density is within acceptable range"""
        density = self._calculate_keyword_density(content)
        return self.quality_thresholds["keyword_density_min"] <= density <= self.quality_thresholds["keyword_density_max"]

    def _check_readability(self, content: str) -> bool:
        """Check readability score"""
        readability = self._calculate_readability(content)
        return readability >= self.quality_thresholds["readability_threshold"]

    def _has_special_characters(self, content: str) -> bool:
        """Check for ATS-unfriendly special characters"""
        special_chars = [
            "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "=", "{", "}", 
            "[", "]", "|", "\\", ":", ";", '"', "'", "<", ">", ",", ".", "?", "/"
        ]
        return any(char in content for char in special_chars if not content.strip().endswith(char))

    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (simplified Flesch-Kincaid)"""
        words = content.split()
        sentences = content.split(".")

        if not words or not sentences:
            return 0.0

        avg_words_per_sentence = len(words) / len(sentences)
        avg_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words)

        # Simplified readability score
        readability = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        return max(0, min(100, readability))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_char_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                syllable_count += 1
            prev_char_was_vowel = is_vowel

        if word.endswith("e"):
            syllable_count -= 1

        return max(1, syllable_count)

    def _calculate_keyword_density(self, content: str) -> float:
        """Calculate keyword density"""
        if not content:
            return 0.0

        words = content.split()
        if not words:
            return 0.0

        # Simple keyword identification
        keywords = self._extract_keywords_from_text(content, limit=20)
        keyword_count = sum(1 for word in words if word.lower() in [kw.lower() for kw in keywords])

        return keyword_count / len(words)

    def _calculate_impact_score(self, content: str) -> float:
        """Calculate impact score based on action verbs and quantification"""
        impact_indicators = ["increased", "decreased", "improved", "reduced", "achieved", "delivered", "generated", "saved"]
        quantification_patterns = [r"\d+%", r"\$\d+", r"\d+x", r"by \d+"]

        content_lower = content.lower()
        impact_count = sum(1 for indicator in impact_indicators if indicator in content_lower)
        quantification_count = sum(1 for pattern in quantification_patterns if re.search(pattern, content))

        total_words = len(content.split())
        if total_words == 0:
            return 0.0

        impact_score = (impact_count + quantification_count * 2) / total_words * 100
        return min(1.0, impact_score)

    def _calculate_completeness(self, content: str, context: GenerationContext) -> float:
        """Calculate completeness score based on context requirements"""
        score = 0.5  # Base score

        # Check for required elements
        if context.keyword_requirements:
            keyword_matches = sum(1 for kw in context.keyword_requirements if kw.lower() in content.lower())
            score += (keyword_matches / len(context.keyword_requirements)) * 0.3

        # Check length appropriateness
        word_count = len(content.split())
        if 50 <= word_count <= 150:  # Good length range
            score += 0.2

        return min(1.0, score)

    def _create_context_summary(self, context: GenerationContext) -> Dict[str, Any]:
        """Create summary of generation context for history tracking"""
        return {
            "task_type": context.task_type,
            "target_role": context.target_role,
            "experience_level": context.experience_level,
            "optimization_focus": context.optimization_focus,
            "has_target_company": context.target_company is not None
        }

    def run(self, input_data: Dict[str, Any]) -> MessageResult:
        """Run message generation from dictionary input"""
        context = GenerationContext(
            prompt=input_data.get("prompt", ""),
            task_type=input_data.get("task_type", "general"),
            target_role=input_data.get("target_role", ""),
            experience_level=input_data.get("experience_level", "mid"),
            target_company=input_data.get("target_company"),
            optimization_focus=input_data.get("optimization_focus", ["impact"]),
            parameters=input_data.get("parameters", {})
        )

        return self.execute(context)

    def get_generation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get generation history"""
        return self.generation_history[-limit:]

    def analyze_generation_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in generation history"""
        if not self.generation_history:
            return {"message": "No generation history available"}

        task_types = {}
        confidence_scores = []
        compliance_rates = []

        for entry in self.generation_history:
            task_type = entry["context_summary"]["task_type"]
            task_types[task_type] = task_types.get(task_type, 0) + 1
            confidence_scores.append(entry["result_summary"]["confidence"])
            compliance_rates.append(1 if entry["result_summary"]["compliance_passed"] else 0)

        return {
            "total_generations": len(self.generation_history),
            "task_type_distribution": task_types,
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "compliance_rate": sum(compliance_rates) / len(compliance_rates),
            "most_common_task": max(task_types.items(), key=lambda x: x[1])[0] if task_types else None
        }
