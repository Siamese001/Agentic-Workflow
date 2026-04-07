"""Visual Content Detector.

Detects visual content types and routes to specialized processors.
Implements modality detection for tables, charts, diagrams, and scanned pages.
"""

import hashlib
import logging
import re
from datetime import datetime
from pathlib import Path

from .modality_types import ContentMetadata, ContentType, DocumentModality

log = logging.getLogger(__name__)


class VisualDetector:
    """Detects visual content and determines processing routes."""

    def __init__(self):
        self.visual_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.tiff', '.webp',
        }
        self.table_indicators = [
            r'\|.*\|',  # Markdown tables
            r'<table',  # HTML tables
            r'\t+',     # Tab-separated
            r',{3,}',   # CSV-like
        ]
        self.code_indicators = [
            r'```',     # Code blocks
            r'    ',    # Indented code
            r'```[\w\+\-]*\n',  # Language-specific code blocks
        ]
        self.heading_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headings
            r'^(.+)\n[=-]+$',     # Underlined headings
            r'^\d+\.\s+(.+)$',     # Numbered sections
            r'^[A-Z][A-Z\s]*$',   # ALL CAPS headings (allow empty)
        ]

    def detect_modality(self, file_path: Path, content: str | None = None) -> DocumentModality:
        """Detect document modality based on file and content analysis.

        Args:
            file_path: Path to the document
            content: Optional pre-loaded content

        Returns:
            DocumentModality classification
        """
        if content is None and file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8', errors='replace')
            except Exception as e:
                log.warning(f"Failed to read file for modality detection: {e}")
                return DocumentModality.UNKNOWN

        if not content:
            return DocumentModality.UNKNOWN

        # Check for visual content indicators
        visual_score = self._calculate_visual_score(content)
        table_score = self._calculate_table_score(content)
        code_score = self._calculate_code_score(content)
        structure_score = self._calculate_structure_score(content)

        # Determine modality based on scores
        if visual_score > 0.05:  # Lowered threshold
            return DocumentModality.VISUAL_HEAVY
        elif table_score > 0.1:  # Lowered threshold
            return DocumentModality.TABULAR_DATA
        elif code_score > 0.05:  # Lowered threshold
            return DocumentModality.CODE_BASE
        elif structure_score > 0.05:  # Lowered threshold
            return DocumentModality.STRUCTURED_TEXT
        elif visual_score > 0.02:  # Lowered threshold for mixed
            return DocumentModality.MIXED_MODAL
        else:
            return DocumentModality.TEXT_ONLY

    def extract_metadata(self, file_path: Path, content: str | None = None) -> ContentMetadata:
        """Extract comprehensive metadata from document.

        Args:
            file_path: Path to the document
            content: Optional pre-loaded content

        Returns:
            ContentMetadata with extracted information
        """
        if content is None and file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8', errors='replace')
            except Exception as e:
                log.warning(f"Failed to read file for metadata extraction: {e}")
                content = ""

        # Basic file information
        file_size = file_path.stat().st_size if file_path.exists() else 0
        content_type = self._detect_content_type(file_path)
        modality = self.detect_modality(file_path, content)

        # Calculate checksum
        checksum = self._calculate_checksum(content) if content else None

        # Content analysis
        has_tables = self._has_tables(content) if content else False
        has_images = self._has_images(content) if content else False
        has_code_blocks = self._has_code_blocks(content) if content else False
        has_headings = self._has_headings(content) if content else False

        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(content) // 4 if content else 0

        # Detect language (simple heuristic)
        language = self._detect_language(content) if content else None

        return ContentMetadata(
            file_path=str(file_path),
            content_type=content_type,
            modality=modality,
            file_size_bytes=file_size,
            estimated_tokens=estimated_tokens,
            has_tables=has_tables,
            has_images=has_images,
            has_code_blocks=has_code_blocks,
            has_headings=has_headings,
            language=language,
            checksum=checksum,
            extracted_at=datetime.utcnow().isoformat(),
        )

    def _detect_content_type(self, file_path: Path) -> ContentType:
        """Detect content type from file extension."""
        suffix = file_path.suffix.lower()

        content_type_map = {
            '.txt': ContentType.TEXT,
            '.md': ContentType.MARKDOWN,
            '.markdown': ContentType.MARKDOWN,
            '.pdf': ContentType.PDF,
            '.html': ContentType.HTML,
            '.htm': ContentType.HTML,
            '.csv': ContentType.CSV,
            '.json': ContentType.JSON,
            '.xml': ContentType.XML,
            '.py': ContentType.CODE,
            '.js': ContentType.CODE,
            '.ts': ContentType.CODE,
            '.java': ContentType.CODE,
            '.cpp': ContentType.CODE,
            '.c': ContentType.CODE,
            '.h': ContentType.CODE,
            '.css': ContentType.CODE,
            '.scss': ContentType.CODE,
            '.less': ContentType.CODE,
            '.sql': ContentType.CODE,
            '.sh': ContentType.CODE,
            '.bat': ContentType.CODE,
            '.ps1': ContentType.CODE,
        }

        # Check for visual content
        if suffix in self.visual_extensions:
            return ContentType.IMAGE

        return content_type_map.get(suffix, ContentType.UNKNOWN)

    def _calculate_visual_score(self, content: str) -> float:
        """Calculate visual content score (0-1)."""
        if not content:
            return 0.0

        score = 0.0
        content_lower = content.lower()

        # Image references
        image_patterns = [
            r'!\[.*\]\([^)]+\)',  # Markdown images
            r'<img[^>]+>',       # HTML images
            r'image\s*[:=]',     # Key-value image references
        ]

        for pattern in image_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            score += len(matches) * 0.3  # Increased weight

        # Chart/diagram indicators
        chart_keywords = ['chart', 'graph', 'diagram', 'figure', 'plot', 'visualization']
        for keyword in chart_keywords:
            score += content_lower.count(keyword) * 0.1

        # Table indicators (visual weight)
        table_matches = 0
        for pattern in self.table_indicators:
            table_matches += len(re.findall(pattern, content, re.MULTILINE))
        score += table_matches * 0.2  # Increased weight

        # Normalize based on content length
        content_length = len(content.split())
        if content_length > 0:
            score = score / content_length
        else:
            score = 0.0

        return min(score, 1.0)

    def _calculate_table_score(self, content: str) -> float:
        """Calculate table content score (0-1)."""
        if not content:
            return 0.0

        score = 0.0
        lines = content.split('\n')

        # Count table-like lines
        table_lines = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for table patterns
            for pattern in self.table_indicators:
                if re.search(pattern, line):
                    table_lines += 1
                    break

        if len(lines) > 0:
            score = table_lines / len(lines)

        return min(score, 1.0)

    def _calculate_code_score(self, content: str) -> float:
        """Calculate code content score (0-1)."""
        if not content:
            return 0.0

        score = 0.0

        # Code block patterns
        for pattern in self.code_indicators:
            matches = re.findall(pattern, content, re.MULTILINE)
            score += len(matches) * 0.4  # Increased weight

        # Language keywords
        code_keywords = [
            'def ', 'class ', 'import ', 'from ', 'function ', 'var ', 'let ', 'const ',
            'if ', 'else ', 'for ', 'while ', 'switch ', 'case ', 'try ', 'catch ',
        ]

        content_lower = content.lower()
        for keyword in code_keywords:
            score += content_lower.count(keyword) * 0.05  # Increased weight

        # Normalize based on content length
        content_length = len(content.split())
        if content_length > 0:
            score = score / content_length
        else:
            score = 0.0

        return min(score, 1.0)

    def _calculate_structure_score(self, content: str) -> float:
        """Calculate structured text score (0-1)."""
        if not content:
            return 0.0

        score = 0.0
        lines = content.split('\n')

        # Heading detection
        heading_lines = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in self.heading_patterns:
                if re.match(pattern, line, re.MULTILINE):
                    heading_lines += 1
                    break

        if len(lines) > 0:
            score = heading_lines / len(lines)

        return min(score, 1.0)

    def _has_tables(self, content: str) -> bool:
        """Check if content contains tables."""
        if not content:
            return False

        for pattern in self.table_indicators:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False

    def _has_images(self, content: str) -> bool:
        """Check if content contains image references."""
        if not content:
            return False

        image_patterns = [
            r'!\[.*\]\([^)]+\)',  # Markdown images
            r'<img[^>]+>',       # HTML images
        ]

        for pattern in image_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _has_code_blocks(self, content: str) -> bool:
        """Check if content contains code blocks."""
        if not content:
            return False

        for pattern in self.code_indicators:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False

    def _has_headings(self, content: str) -> bool:
        """Check if content contains headings."""
        if not content:
            return False

        for pattern in self.heading_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _detect_language(self, content: str) -> str | None:
        """Simple language detection based on character patterns."""
        if not content:
            return None

        # Simple heuristic for common languages
        if re.search(r'[\u4e00-\u9fff]', content):  # Chinese characters
            return 'zh'
        elif re.search(r'[\u0400-\u04ff]', content):  # Cyrillic
            return 'ru'
        elif re.search(r'[\u0590-\u05ff]', content):  # Hebrew
            return 'he'
        elif re.search(r'[\u0600-\u06ff]', content):  # Arabic
            return 'ar'
        else:
            return 'en'  # Default to English
