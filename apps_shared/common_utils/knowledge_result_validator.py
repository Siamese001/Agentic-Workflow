"""
L5 Consolidated Knowledge Retrieval for Resume Engine
Consolidates L3 (Pinecone) and L5 (MEMemory) into unified knowledge access

This module provides unified access to:
- User profiles from MEMemory
- Cover letter templates from Pinecone/L3
- Consolidated search across both knowledge bases
"""

import logging

Logger: Any = logging.getLogger(__name__)


@dataclass
class KnowledgeResult:
    """Result from knowledge retrieval."""

    user_profile: dict[str, Any] | None
    template: dict[str, Any] | None
    metadata: dict[str, Any]


class L5ConsolidatedKnowledge:
    """Consolidated knowledge access layer."""

    def __init__(self, memory_client=None, pinecone_client=None):
        """
        Initialize consolidated knowledge layer.

        Args:
            memory_client: MEMemory client for user profiles
            pinecone_client: Pinecone client for templates
        """
        self.memory_client = memory_client
        self.pinecone_client = pinecone_client
        self._fallback_profiles = self._load_fallback_profiles()
        self._fallback_templates = self._load_fallback_templates()

    def _load_fallback_profiles(self) -> dict[str, Any]:
        """Load fallback user profiles if MEMemory unavailable."""
        return {
            "default": {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "experience": "5 years",
                "skills": ["Python", "JavaScript", "React", "Docker"],
                "education": "B.S. Computer Science",
                "achievements": [
                    "Led team of 5 developers",
                    "Reduced deployment time by 50%",
                    "Implemented CI/CD pipeline",
                ],
                "contact": {
                    "email": "john.doe@email.com",
                    "phone": "(555) 123-4567",
                    "linkedin": "linkedin.com/in/johndoe",
                },
            },
        }

    def _load_fallback_templates(self) -> dict[str, Any]:
        """Load fallback templates if Pinecone unavailable."""
        return {
            "professional": {
                "name": "Professional Cover Letter",
                "structure": {
                    "header": "{name}\n{contact}\n{date}",
                    "greeting": "Dear {hiring_manager},",
                    "introduction": "I am writing to express my interest in the {position} position at {company}.",
                    "body": [
                        "With {experience} of experience in {field}, I have developed strong skills in {skills}.",
                        "At my previous role at {previous_company}, I {achievement}.",
                        "I am particularly drawn to {company} because of {company_value}.",
                    ],
                    "closing": "I look forward to discussing how my skills can benefit your team.",
                    "signature": "Sincerely,\n{name}",
                },
                "tone": "formal",
                "length": "medium",
            },
            "modern": {
                "name": "Modern Cover Letter",
                "structure": {
                    "header": "{name} | {title} | {contact}",
                    "greeting": "Hello {hiring_manager},",
                    "introduction": "Excited about the {position} opportunity at {company}!",
                    "body": [
                        "My {experience} in {field} has prepared me to tackle {challenge}.",
                        "Key achievements: {achievements}",
                        "Why I'm excited: {company_culture}",
                    ],
                    "closing": "Let's connect and discuss how I can contribute!",
                    "signature": "Best regards,\n{name}",
                },
                "tone": "casual",
                "length": "short",
            },
        }

    def search_knowledge(self, query: str, types: list[str] = None) -> KnowledgeResult:
        """
        Search consolidated knowledge base.

        Args:
            query: Search query
            types: Types to search ["profile", "template"]

        Returns:
            KnowledgeResult with retrieved data
        """
        if types is None:
            types: Any = ["profile", "template"]
        result: Any = KnowledgeResult(
            user_profile=None, template=None, metadata={"query": query, "types": types},
        )
        if "profile" in types:
            result.user_profile = self._get_user_profile(query)
            result.metadata["profile_source"] = self._get_profile_source()
        if "template" in types:
            result.template = self._get_template(query)
            result.metadata["template_source"] = self._get_template_source()
        return result

    def _get_user_profile(self, query: str) -> dict[str, Any] | None:
        """Get user profile from MEMemory or fallback."""
        if self.memory_client:
            try:
                profile = self.memory_client.get_profile(query)
                if profile:
                    Logger.info("Retrieved profile from MEMemory")
                    return profile
            except Exception as e:
                Logger.warning(f"Failed to retrieve from MEMemory: {e}")
        Logger.info("Using fallback user profile")
        return self._fallback_profiles.get("default")

    def _get_template(self, query: str) -> dict[str, Any] | None:
        """Get template from Pinecone or fallback."""
        if self.pinecone_client:
            try:
                templates = self.pinecone_client.query(
                    vector=self._embed_query(query), top_k=1, include_metadata=True,
                )
                if templates:
                    Logger.info("Retrieved template from Pinecone")
                    return templates[0].metadata
            except Exception as e:
                Logger.warning(f"Failed to retrieve from Pinecone: {e}")
        template_type = "professional" if "professional" in query.lower() else "modern"
        Logger.info(f"Using fallback template: {template_type}")
        return self._fallback_templates.get(template_type)

    def _embed_query(self, query: str) -> list[float]:
        """Create embedding for query (placeholder)."""
        return [0.1] * 384

    def _get_profile_source(self) -> str:
        """Get source of profile retrieval."""
        return "memory" if self.memory_client else "fallback"

    def _get_template_source(self) -> str:
        """Get source of template retrieval."""
        return "pinecone" if self.pinecone_client else "fallback"

    def save_profile(self, profile: dict[str, Any]) -> bool:
        """
        Save user profile to MEMemory.

        Args:
            profile: User profile to save

        Returns:
            True if successful
        """
        if self.memory_client:
            try:
                self.memory_client.save_profile(profile)
                Logger.info("Profile saved to MEMemory")
                return True
            except Exception as e:
                Logger.error(f"Failed to save profile: {e}")
                return False
        self._fallback_profiles["default"] = profile
        Logger.info("Profile saved to fallback storage")
        return True

    def add_template(self, template: dict[str, Any]) -> bool:
        """
        Add template to Pinecone.

        Args:
            template: Template to add

        Returns:
            True if successful
        """
        if self.pinecone_client:
            try:
                embedding: Any = self._embed_query(template.get("name", ""))
                self.pinecone_client.upsert(
                    vectors=[
                        {
                            "id": template.get("id", "custom"),
                            "values": embedding,
                            "metadata": template,
                        },
                    ],
                )
                Logger.info("Template added to Pinecone")
                return True
            except Exception as e:
                Logger.error(f"Failed to add template: {e}")
                return False
        template_name: Any = template.get("name", "custom").lower()
        self._fallback_templates[template_name] = template
        Logger.info("Template added to fallback storage")
        return True

    def query_consensus(self, pitch: str, guidelines: dict) -> dict:
        """
        Query multiple models for consensus on pitch compliance.

        Args:
            pitch: Pitch content to evaluate
            guidelines: Brand style guidelines to check against

        Returns:
            Consensus result with status and reasoning
        """
        Logger.info("P6_CONSENSUS_START: Evaluating pitch compliance")
        evaluations: Any = []
        brand_score: Any = self._check_brand_compliance(pitch, guidelines)
        evaluations.append(
            {
                "model": "brand_checker",
                "status": "PASS" if brand_score >= 0.7 else "FAIL",
                "score": brand_score,
                "reason": "Brand tone and style analysis",
            },
        )
        spam_score: Any = self._check_spam_indicators(pitch)
        evaluations.append(
            {
                "model": "spam_detector",
                "status": "PASS" if spam_score <= 0.3 else "FAIL",
                "score": spam_score,
                "reason": "Spam and promotional content analysis",
            },
        )
        professionalism_score: Any = self._check_professionalism(pitch)
        evaluations.append(
            {
                "model": "professionalism_checker",
                "status": "PASS" if professionalism_score >= 0.6 else "FAIL",
                "score": professionalism_score,
                "reason": "Professional tone and language analysis",
            },
        )
        pass_count: Any = sum(1 for e in evaluations if e["status"] == "PASS")
        total_count: Any = len(evaluations)
        consensus_status: Any = "PASS" if pass_count == total_count else "FAIL"
        failure_reasons: Any = [e["reason"] for e in evaluations if e["status"] == "FAIL"]
        result: Any = {
            "status": consensus_status,
            "evaluations": evaluations,
            "consensus_score": pass_count / total_count,
            "reason": "; ".join(failure_reasons) if failure_reasons else "All checks passed",
        }
        Logger.info(
            f"P6_CONSENSUS_COMPLETE: Status={consensus_status}, Score={result['consensus_score']}",
        )
        return result

    def _check_brand_compliance(self, pitch: str, guidelines: dict) -> float:
        """Check pitch against brand guidelines."""
        score = 0.8
        prohibited = guidelines.get("prohibited_words", [])
        for word in prohibited:
            if word.lower() in pitch.lower():
                score -= 0.2
        required_tone = guidelines.get("tone", "professional")
        if required_tone == "professional":
            if any(word in pitch.lower() for word in ["amazing", "incredible", "revolutionary"]):
                score -= 0.1
        return max(0, min(1, score))

    def _check_spam_indicators(self, pitch: str) -> float:
        """Check for spam indicators (lower is better)."""
        spam_score = 0.0
        spam_triggers = ["!!", "FREE", "ACT NOW", "LIMITED TIME", "GUARANTEE"]
        for trigger in spam_triggers:
            if trigger in pitch.upper():
                spam_score += 0.2
        words = pitch.split()
        caps_ratio = sum(1 for w in words if w.isupper()) / len(words)
        if caps_ratio > 0.1:
            spam_score += 0.2
        return min(1, spam_score)

    def _check_professionalism(self, pitch: str) -> float:
        """Check professionalism of the pitch."""
        score = 0.7
        if pitch.strip().startswith(("Dear", "Hello", "Hi")):
            score += 0.1
        if any(closing in pitch for closing in ["Best regards", "Sincerely", "Regards"]):
            score += 0.1
        word_count = len(pitch.split())
        if 100 <= word_count <= 200:
            score += 0.1
        return min(1, score)

    def add_observations(self, data: dict) -> bool:
        """Add observations to knowledge graph."""
        try:
            if self.memory_client:
                self.memory_client.add_observations(data)
            return True
        except Exception as e:
            Logger.error(f"Failed to add observations: {e}")
            return False


_consolidated_knowledge = None


def get_consolidated_knowledge(
    memory_client: Any = None, pinecone_client: Any = None,
) -> L5ConsolidatedKnowledge:
    """Get singleton instance of consolidated knowledge."""
    global _consolidated_knowledge
    if _consolidated_knowledge is None:
        _consolidated_knowledge = L5ConsolidatedKnowledge(memory_client, pinecone_client)
    return _consolidated_knowledge


def search_profile_and_template(query: str) -> KnowledgeResult:
    """Convenience function to search for profile and template."""
    return get_consolidated_knowledge().search_knowledge(query)
