"""
L5 Agentic Core - L2 Execution Layer - Summarization Utils
Implements L2 Pure Execution Layer for text summarization utilities
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import re
import math
from collections import Counter

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummaryType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    EXTRACTIVE = "extractive"
    ABSTRACTIVE = "abstractive"
    KEY_SENTENCES = "key_sentences"
    KEYWORDS = "keywords"
    BULLETS = "bullets"

class SummaryStatus(Enum):
    """L5 Summary status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    EMPTY_INPUT = "empty_input"

@dataclass
class SummaryConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_input_length: int = 100000  # 100KB
    max_summary_length: int = 1000
    min_summary_length: int = 50
    max_sentences: int = 10
    require_safety: bool = True
    safety_level: str = "strict"

@dataclass
class SummaryResult:
    """L5 Summary result structure with full type safety"""
    summary_type: SummaryType
    summary_text: str = ""
    original_length: int = 0
    summary_length: int = 0
    compression_ratio: float = 0.0
    key_points: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class SummaryResponse:
    """L5 Summary response structure"""
    summary_id: str
    status: SummaryStatus
    result: Optional[SummaryResult] = None
    error_message: str = ""
    safety_validated: bool = False
    timestamp: str = ""

class SummarizationUtils(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def summarize(self, text: str, summary_type: SummaryType, constraints: SummaryConstraints) -> SummaryResponse:
        """Summarize text with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, text: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class SummarizationUtilsImpl(SummarizationUtils):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure text summarization execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[SummaryConstraints] = None):
        self.constraints = constraints or SummaryConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def summarize(self, text: str, summary_type: SummaryType, constraints: Optional[SummaryConstraints] = None) -> SummaryResponse:
        """Summarize text following L5 architecture principles"""
        summary_constraints = constraints or self.constraints
        self.logger.info(f"Summarizing text using {summary_type.value} method")
        
        # L5 Input validation
        self._validate_input(text)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(text):
            raise SecurityError("Text failed L5 safety validation")
        
        try:
            # Check text length constraints
            if len(text) > summary_constraints.max_input_length:
                return SummaryResponse(
                    summary_id=self._generate_summary_id(),
                    status=SummaryStatus.TOO_LONG,
                    error_message=f"Text too long: {len(text)} > {summary_constraints.max_input_length}",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            if len(text.strip()) < 10:
                return SummaryResponse(
                    summary_id=self._generate_summary_id(),
                    status=SummaryStatus.TOO_SHORT,
                    error_message="Text too short to summarize",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Perform summarization based on type
            if summary_type == SummaryType.EXTRACTIVE:
                summary_result = self._extractive_summary(text, summary_constraints)
            elif summary_type == SummaryType.KEY_SENTENCES:
                summary_result = self._key_sentences_summary(text, summary_constraints)
            elif summary_type == SummaryType.KEYWORDS:
                summary_result = self._keywords_summary(text, summary_constraints)
            elif summary_type == SummaryType.BULLETS:
                summary_result = self._bullets_summary(text, summary_constraints)
            else:
                summary_result = self._extractive_summary(text, summary_constraints)  # Default
            
            # Validate summary result
            if len(summary_result.summary_text) < summary_constraints.min_summary_length:
                return SummaryResponse(
                    summary_id=self._generate_summary_id(),
                    status=SummaryStatus.TOO_SHORT,
                    error_message="Generated summary too short",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Create summary response
            response = SummaryResponse(
                summary_id=self._generate_summary_id(),
                status=SummaryStatus.SUCCESS,
                result=summary_result,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Summarization completed: {summary_result.summary_length} characters")
            return response
            
        except Exception as e:
            self.logger.error(f"Summarization error: {e}")
            return SummaryResponse(
                summary_id=self._generate_summary_id(),
                status=SummaryStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _extractive_summary(self, text: str, constraints: SummaryConstraints) -> SummaryResult:
        """Generate extractive summary by selecting important sentences"""
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return SummaryResult(
                summary_type=SummaryType.EXTRACTIVE,
                original_length=len(text),
                summary_length=0,
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        
        # Score sentences based on various factors
        sentence_scores = self._score_sentences(sentences)
        
        # Select top sentences
        num_sentences = min(len(sentences), constraints.max_sentences)
        top_sentences = sorted(
            zip(sentences, sentence_scores, range(len(sentences))),
            key=lambda x: x[1],
            reverse=True
        )[:num_sentences]
        
        # Sort by original order
        top_sentences.sort(key=lambda x: x[2])
        
        # Combine sentences
        summary_text = ' '.join([s[0] for s in top_sentences])
        
        # Extract key points
        key_points = [s[0] for s in top_sentences[:3]]  # Top 3 as key points
        
        # Calculate compression ratio
        compression_ratio = len(summary_text) / len(text) if len(text) > 0 else 0
        
        return SummaryResult(
            summary_type=SummaryType.EXTRACTIVE,
            summary_text=summary_text,
            original_length=len(text),
            summary_length=len(summary_text),
            compression_ratio=compression_ratio,
            key_points=key_points,
            metadata={
                'sentence_count': len(sentences),
                'selected_sentences': num_sentences,
                'method': 'extractive'
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _key_sentences_summary(self, text: str, constraints: SummaryConstraints) -> SummaryResult:
        """Generate summary of key sentences"""
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return SummaryResult(
                summary_type=SummaryType.KEY_SENTENCES,
                original_length=len(text),
                summary_length=0,
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        
        # Score sentences using TF-IDF-like approach
        sentence_scores = self._score_sentences_tfidf(sentences)
        
        # Select top sentences
        num_sentences = min(len(sentences), constraints.max_sentences)
        top_indices = sorted(
            range(len(sentence_scores)),
            key=lambda i: sentence_scores[i],
            reverse=True
        )[:num_sentences]
        
        # Sort by original order
        top_indices.sort()
        
        # Create summary
        summary_sentences = [sentences[i] for i in top_indices]
        summary_text = ' '.join(summary_sentences)
        
        # Key points are the selected sentences
        key_points = summary_sentences
        
        return SummaryResult(
            summary_type=SummaryType.KEY_SENTENCES,
            summary_text=summary_text,
            original_length=len(text),
            summary_length=len(summary_text),
            compression_ratio=len(summary_text) / len(text) if len(text) > 0 else 0,
            key_points=key_points,
            metadata={
                'method': 'key_sentences',
                'selected_count': len(summary_sentences)
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _keywords_summary(self, text: str, constraints: SummaryConstraints) -> SummaryResult:
        """Extract keywords from text"""
        # Clean and tokenize text
        words = self._extract_words(text)
        
        # Calculate word frequencies
        word_freq = Counter(words)
        
        # Filter out common words and get top keywords
        stop_words = self._get_stop_words()
        filtered_words = {word: freq for word, freq in word_freq.items() 
                         if word not in stop_words and len(word) > 2}
        
        # Get top keywords
        top_keywords = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Create summary text from keywords
        summary_text = ', '.join([word for word, freq in top_keywords])
        
        # Key points are the keywords with their frequencies
        key_points = [f"{word} ({freq})" for word, freq in top_keywords[:10]]
        
        return SummaryResult(
            summary_type=SummaryType.KEYWORDS,
            summary_text=summary_text,
            original_length=len(text),
            summary_length=len(summary_text),
            compression_ratio=len(summary_text) / len(text) if len(text) > 0 else 0,
            key_points=key_points,
            metadata={
                'method': 'keywords',
                'total_words': len(words),
                'unique_keywords': len(top_keywords)
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _bullets_summary(self, text: str, constraints: SummaryConstraints) -> SummaryResult:
        """Generate bullet point summary"""
        # First get extractive summary
        extractive_result = self._extractive_summary(text, constraints)
        
        # Convert to bullet points
        sentences = self._split_into_sentences(extractive_result.summary_text)
        bullet_points = []
        
        for sentence in sentences:
            # Clean and format as bullet point
            cleaned_sentence = sentence.strip()
            if cleaned_sentence:
                bullet_points.append(f"• {cleaned_sentence}")
        
        summary_text = '\n'.join(bullet_points)
        
        return SummaryResult(
            summary_type=SummaryType.BULLETS,
            summary_text=summary_text,
            original_length=len(text),
            summary_length=len(summary_text),
            compression_ratio=len(summary_text) / len(text) if len(text) > 0 else 0,
            key_points=extractive_result.key_points,
            metadata={
                'method': 'bullets',
                'bullet_count': len(bullet_points)
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - can be enhanced with NLP libraries
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_endings.split(text.strip())
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            cleaned = sentence.strip()
            if cleaned and len(cleaned) > 10:  # Filter very short fragments
                cleaned_sentences.append(cleaned)
        
        return cleaned_sentences
    
    def _score_sentences(self, sentences: List[str]) -> List[float]:
        """Score sentences based on position, length, and keywords"""
        scores = []
        
        # Calculate word frequencies across all sentences
        all_words = []
        for sentence in sentences:
            all_words.extend(self._extract_words(sentence))
        word_freq = Counter(all_words)
        
        for i, sentence in enumerate(sentences):
            score = 0.0
            
            # Position score (earlier sentences get higher scores)
            position_score = 1.0 - (i / len(sentences))
            score += position_score * 0.3
            
            # Length score (prefer medium-length sentences)
            length = len(sentence.split())
            if 10 <= length <= 25:
                length_score = 1.0
            elif 5 <= length <= 35:
                length_score = 0.8
            else:
                length_score = 0.5
            score += length_score * 0.2
            
            # Keyword score (based on word frequency)
            words = self._extract_words(sentence)
            if words:
                word_scores = [word_freq.get(word, 0) for word in words]
                keyword_score = sum(word_scores) / len(words)
                score += min(keyword_score / 10, 1.0) * 0.5
            
            scores.append(score)
        
        return scores
    
    def _score_sentences_tfidf(self, sentences: List[str]) -> List[float]:
        """Score sentences using TF-IDF-like approach"""
        # Calculate term frequencies
        all_words = []
        for sentence in sentences:
            all_words.extend(self._extract_words(sentence))
        term_freq = Counter(all_words)
        
        # Calculate document frequency for each word
        doc_freq = {}
        for word in set(all_words):
            doc_freq[word] = sum(1 for sentence in sentences if word in self._extract_words(sentence))
        
        scores = []
        for sentence in sentences:
            words = self._extract_words(sentence)
            if not words:
                scores.append(0.0)
                continue
            
            # Calculate TF-IDF score
            tfidf_score = 0.0
            for word in words:
                tf = term_freq.get(word, 0) / len(all_words)
                idf = math.log(len(sentences) / doc_freq.get(word, 1))
                tfidf_score += tf * idf
            
            scores.append(tfidf_score)
        
        return scores
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return words
    
    def _get_stop_words(self) -> set:
        """Get common stop words"""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'along', 'following',
            'across', 'behind', 'beyond', 'plus', 'except', 'but', 'yet', 'nor', 'not',
            'no', 'never', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can',
            'will', 'just', 'should', 'now', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'having', 'may', 'might',
            'must', 'shall', 'could', 'would', 'should', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when',
            'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very'
        }
    
    def validate_safety(self, text: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            text_lower = text.lower()
            for pattern in dangerous_patterns:
                if pattern in text_lower:
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check text length
            if len(text) > self.constraints.max_input_length:
                self.logger.error("Text exceeds maximum length")
                return False
            
            # Check for suspicious content
            if text.count('\0') > 0:  # Null bytes
                self.logger.error("Null bytes detected in text")
                return False
            
            # Check for extremely long words (potential buffer overflow)
            words = text.split()
            for word in words:
                if len(word) > 1000:
                    self.logger.error("Extremely long word detected")
                    return False
            
            self.logger.info("Text passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, text: str) -> None:
        """L5 Input validation"""
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
    
    def _generate_summary_id(self) -> str:
        """Generate unique summary ID"""
        import uuid
        return f"summary_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class SummarizationUtilsInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, utils: SummarizationUtils):
        self._utils = utils
    
    def summarize_text(self, text: str, summary_type: str = "extractive", max_sentences: int = 10) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            sum_type = SummaryType(summary_type)
            constraints = SummaryConstraints(max_sentences=max_sentences)
            
            response = self._utils.summarize(text, sum_type, constraints)
            
            if response.result:
                return {
                    "success": response.status == SummaryStatus.SUCCESS,
                    "summary_id": response.summary_id,
                    "summary_type": response.result.summary_type.value,
                    "summary": response.result.summary_text,
                    "original_length": response.result.original_length,
                    "summary_length": response.result.summary_length,
                    "compression_ratio": response.result.compression_ratio,
                    "key_points": response.result.key_points,
                    "metadata": response.result.metadata,
                    "safety_validated": response.result.safety_validated,
                    "timestamp": response.result.timestamp
                }
            else:
                return {
                    "success": False,
                    "error": response.error_message,
                    "status": response.status.value,
                    "safety_validated": response.safety_validated
                }
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class SummarizationUtilsFactory:
    """L5 Factory for creating summarization utils instances"""
    
    @staticmethod
    def create_utils(constraints: Optional[SummaryConstraints] = None) -> SummarizationUtils:
        return SummarizationUtilsImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[SummaryConstraints] = None) -> SummarizationUtilsInterface:
        utils = SummarizationUtilsFactory.create_utils(constraints)
        return SummarizationUtilsInterface(utils)

# L5 Export for module usage
__all__ = [
    "SummaryType",
    "SummaryStatus",
    "SummaryConstraints",
    "SummaryResult",
    "SummaryResponse",
    "SummarizationUtils",
    "SummarizationUtilsImpl",
    "SummarizationUtilsInterface",
    "SummarizationUtilsFactory",
    "SecurityError"
]
