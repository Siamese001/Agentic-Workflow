"""
Shared Text Processing Utilities
LEVEL 5 - Common text processing functions shared across resume and outreach engines
"""

import re
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import unicodedata

class TextProcessor:
    """Shared text processing utilities for both engines"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Common patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.url_pattern = re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?')
        self.skill_pattern = re.compile(r'\b(?:Python|Java|JavaScript|React|Node\.js|SQL|AWS|Docker|Kubernetes|Git|Agile|Scrum|DevOps|CI/CD|Machine Learning|AI|Data Science|Analytics|Cloud|Microservices|REST API|GraphQL|MongoDB|PostgreSQL|MySQL|Redis|Elasticsearch|Kafka|RabbitMQ|Terraform|Ansible|Jenkins|GitHub|GitLab|Bitbucket)\b', re.IGNORECASE)
    
    async def clean_text(self, text: str, remove_extra_whitespace: bool = True, 
                         normalize_unicode: bool = True, remove_special_chars: bool = False) -> str:
        """Clean and normalize text content"""
        try:
            if not text:
                return ""
            
            cleaned = text.strip()
            
            # Normalize Unicode
            if normalize_unicode:
                cleaned = unicodedata.normalize('NFKC', cleaned)
            
            # Remove extra whitespace
            if remove_extra_whitespace:
                cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # Remove special characters (keep basic punctuation)
            if remove_special_chars:
                cleaned = re.sub(r'[^\w\s.,!?;:()-]', '', cleaned)
            
            self.logger.debug(f"Text cleaned: {len(text)} -> {len(cleaned)} characters")
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Error cleaning text: {e}")
            return text
    
    async def extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        """Extract contact information from text"""
        try:
            contacts = {
                "emails": [],
                "phone_numbers": [],
                "urls": [],
                "social_links": []
            }
            
            # Extract emails
            emails = self.email_pattern.findall(text)
            contacts["emails"] = list(set(emails))  # Remove duplicates
            
            # Extract phone numbers
            phones = self.phone_pattern.findall(text)
            contacts["phone_numbers"] = [f"{phone[0]}({phone[1]}) {phone[2]}-{phone[3]}" for phone in phones]
            
            # Extract URLs
            urls = self.url_pattern.findall(text)
            contacts["urls"] = list(set(urls))
            
            # Extract social media links
            social_patterns = [
                r'https?://(?:www\.)?linkedin\.com/[\w/-]+',
                r'https?://(?:www\.)?github\.com/[\w-]+',
                r'https?://(?:www\.)?twitter\.com/[\w-]+',
                r'https?://(?:www\.)?facebook\.com/[\w-]+'
            ]
            
            for pattern in social_patterns:
                social_links = re.findall(pattern, text, re.IGNORECASE)
                contacts["social_links"].extend(social_links)
            
            contacts["social_links"] = list(set(contacts["social_links"]))
            
            self.logger.debug(f"Extracted contacts: {sum(len(v) for v in contacts.values())} items")
            return contacts
            
        except Exception as e:
            self.logger.error(f"Error extracting contact info: {e}")
            return {"emails": [], "phone_numbers": [], "urls": [], "social_links": []}
    
    async def extract_skills(self, text: str, custom_skills: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract skills from text with categorization"""
        try:
            # Default skill categories
            skill_categories = {
                "programming_languages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin"],
                "frameworks": ["React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring", "Express.js", "FastAPI", "Next.js", "Nuxt.js"],
                "databases": ["SQL", "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch", "Cassandra", "DynamoDB", "Neo4j"],
                "cloud_platforms": ["AWS", "Azure", "Google Cloud", "GCP", "Heroku", "DigitalOcean", "Vercel", "Netlify"],
                "devops_tools": ["Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI"],
                "methodologies": ["Agile", "Scrum", "Kanban", "DevOps", "CI/CD", "TDD", "BDD", "Microservices"],
                "data_science": ["Machine Learning", "AI", "Data Science", "Analytics", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy"],
                "other": ["Git", "Linux", "REST API", "GraphQL", "OAuth", "JWT", "SAML", "WebSocket", "gRPC"]
            }
            
            # Add custom skills if provided
            if custom_skills:
                skill_categories["custom"] = custom_skills
            
            found_skills = {category: [] for category in skill_categories}
            
            # Extract skills using patterns
            text_upper = text.upper()
            
            for category, skills in skill_categories.items():
                for skill in skills:
                    # Check for exact word boundaries
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        found_skills[category].append(skill)
            
            # Calculate skill statistics
            total_skills = sum(len(skills) for skills in found_skills.values())
            skill_density = total_skills / len(text.split()) if text.split() else 0
            
            result = {
                "skills_by_category": found_skills,
                "total_skills": total_skills,
                "skill_density": round(skill_density, 3),
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.debug(f"Extracted {total_skills} skills across {len(skill_categories)} categories")
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}")
            return {"skills_by_category": {}, "total_skills": 0, "skill_density": 0}
    
    async def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity metrics"""
        try:
            if not text:
                return {"error": "Empty text provided"}
            
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Basic metrics
            word_count = len(words)
            sentence_count = len(sentences)
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Vocabulary complexity
            unique_words = set(word.lower().strip('.,!?;:()[]{}"\'') for word in words)
            vocabulary_size = len(unique_words)
            lexical_diversity = vocabulary_size / word_count if word_count > 0 else 0
            
            # Readability approximation (simplified Flesch-Kincaid)
            avg_syllables = sum(self._count_syllables(word) for word in words) / word_count if word_count > 0 else 0
            readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
            
            # Technical complexity indicators
            technical_terms = len(self.skill_pattern.findall(text))
            jargon_ratio = technical_terms / word_count if word_count > 0 else 0
            
            result = {
                "basic_metrics": {
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "avg_sentence_length": round(avg_sentence_length, 2)
                },
                "vocabulary_metrics": {
                    "vocabulary_size": vocabulary_size,
                    "lexical_diversity": round(lexical_diversity, 3),
                    "unique_words_ratio": round(lexical_diversity, 3)
                },
                "readability_metrics": {
                    "readability_score": round(readability_score, 2),
                    "complexity_level": self._get_complexity_level(readability_score),
                    "avg_syllables_per_word": round(avg_syllables, 2)
                },
                "technical_metrics": {
                    "technical_terms_count": technical_terms,
                    "jargon_ratio": round(jargon_ratio, 3),
                    "technical_density": "high" if jargon_ratio > 0.1 else "medium" if jargon_ratio > 0.05 else "low"
                },
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.debug(f"Text complexity analysis completed: {word_count} words analyzed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing text complexity: {e}")
            return {"error": str(e)}
    
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text (simplified version)"""
        try:
            entities = {
                "organizations": [],
                "locations": [],
                "dates": [],
                "numbers": [],
                "certifications": [],
                "education": []
            }
            
            # Extract organizations (capitalized words that look like company names)
            org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|LLC|Ltd|Co|Company|Technologies|Systems|Solutions))?\b'
            potential_orgs = re.findall(org_pattern, text)
            entities["organizations"] = list(set(potential_orgs))
            
            # Extract locations (cities, states, countries)
            location_keywords = ["New York", "San Francisco", "Los Angeles", "Chicago", "Boston", "Seattle", "Austin", 
                                "California", "Texas", "New York", "Florida", "Washington", "Colorado", "Oregon",
                                "United States", "USA", "Canada", "UK", "London", "Paris", "Berlin", "Tokyo"]
            
            for location in location_keywords:
                if location.lower() in text.lower():
                    entities["locations"].append(location)
            
            # Extract dates
            date_patterns = [
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
                r'\b\d{4}-\d{2}-\d{2}\b',      # YYYY-MM-DD
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'  # Month DD, YYYY
            ]
            
            for pattern in date_patterns:
                dates = re.findall(pattern, text, re.IGNORECASE)
                entities["dates"].extend(dates)
            
            entities["dates"] = list(set(entities["dates"]))
            
            # Extract numbers and measurements
            number_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:years?|months?|weeks?|days?|%|percent|USD|dollars?|$|K|M|B|T))?\b'
            entities["numbers"] = re.findall(number_pattern, text)
            
            # Extract certifications
            cert_keywords = ["AWS", "Azure", "Google Cloud", "PMP", "Scrum Master", "Certified", "Professional", 
                            "Associate", "Solutions Architect", "Developer", "Engineer"]
            
            for cert in cert_keywords:
                if cert.lower() in text.lower():
                    entities["certifications"].append(cert)
            
            # Extract education indicators
            education_keywords = ["Bachelor", "Master", "PhD", "Doctorate", "MBA", "BS", "BA", "MS", "MA", 
                                 "University", "College", "Institute", "School", "Degree", "Diploma"]
            
            for edu in education_keywords:
                if edu.lower() in text.lower():
                    entities["education"].append(edu)
            
            # Remove duplicates and filter
            for key in entities:
                entities[key] = list(set(entities[key]))
                entities[key] = [item for item in entities[key] if len(item.strip()) > 0]
            
            self.logger.debug(f"Extracted entities: {sum(len(v) for v in entities.values())} total")
            return entities
            
        except Exception as e:
            self.logger.error(f"Error extracting entities: {e}")
            return {"organizations": [], "locations": [], "dates": [], "numbers": [], "certifications": [], "education": []}
    
    async def normalize_text_for_comparison(self, text: str) -> str:
        """Normalize text for comparison purposes"""
        try:
            if not text:
                return ""
            
            # Convert to lowercase
            normalized = text.lower()
            
            # Remove punctuation
            normalized = re.sub(r'[^\w\s]', '', normalized)
            
            # Normalize whitespace
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizing text: {e}")
            return text.lower()
    
    async def calculate_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """Calculate similarity between two texts"""
        try:
            norm1 = await self.normalize_text_for_comparison(text1)
            norm2 = await self.normalize_text_for_comparison(text2)
            
            words1 = set(norm1.split())
            words2 = set(norm2.split())
            
            # Jaccard similarity
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            jaccard_similarity = len(intersection) / len(union) if union else 0
            
            # Word overlap ratio
            overlap_ratio = len(intersection) / min(len(words1), len(words2)) if words1 and words2 else 0
            
            # Length similarity
            len_similarity = 1 - abs(len(text1) - len(text2)) / max(len(text1), len(text2))
            
            result = {
                "jaccard_similarity": round(jaccard_similarity, 3),
                "word_overlap_ratio": round(overlap_ratio, 3),
                "length_similarity": round(len_similarity, 3),
                "overall_similarity": round((jaccard_similarity + overlap_ratio + len_similarity) / 3, 3)
            }
            
            self.logger.debug(f"Similarity calculated: {result['overall_similarity']:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return {"jaccard_similarity": 0, "word_overlap_ratio": 0, "length_similarity": 0, "overall_similarity": 0}
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (approximation)"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _get_complexity_level(self, readability_score: float) -> str:
        """Get complexity level based on readability score"""
        if readability_score >= 90:
            return "very_easy"
        elif readability_score >= 80:
            return "easy"
        elif readability_score >= 70:
            return "fairly_easy"
        elif readability_score >= 60:
            return "standard"
        elif readability_score >= 50:
            return "fairly_difficult"
        elif readability_score >= 30:
            return "difficult"
        else:
            return "very_difficult"

@dataclass
class TextProcessingResult:
    """Result of text processing operations"""
    original_text: str
    processed_text: str
    contact_info: Dict[str, List[str]]
    skills: Dict[str, Any]
    entities: Dict[str, List[str]]
    complexity: Dict[str, Any]
    processing_timestamp: str
    processing_time_ms: float
