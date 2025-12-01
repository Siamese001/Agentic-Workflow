"""
L5 Agentic Core - L2 Execution Layer - Browser Extraction Utils
Implements L2 Pure Execution Layer for web content extraction utilities
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import re
from bs4 import BeautifulSoup, Tag
import urllib.parse

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtractionType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    TEXT = "text"
    LINKS = "links"
    IMAGES = "images"
    METADATA = "metadata"
    TABLES = "tables"
    LISTS = "lists"
    HEADINGS = "headings"
    FORMS = "forms"

class ExtractionStatus(Enum):
    """L5 Extraction status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    EMPTY = "empty"
    BLOCKED = "blocked"

@dataclass
class ExtractionConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_items: int = 100
    max_text_length: int = 50000
    allowed_tags: List[str] = field(default_factory=lambda: ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    blocked_attributes: List[str] = field(default_factory=lambda: ['onclick', 'onload', 'onerror'])
    sanitize_content: bool = True
    safety_level: str = "strict"

@dataclass
class ExtractionResult:
    """L5 Extraction result structure with full type safety"""
    extraction_type: ExtractionType
    items: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    safety_validated: bool = False
    timestamp: str = ""

class BrowserExtractionUtils(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def extract_content(self, html: str, extraction_type: ExtractionType, constraints: ExtractionConstraints) -> ExtractionResult:
        """Extract content with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, content: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class BrowserExtractionUtilsImpl(BrowserExtractionUtils):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure content extraction execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[ExtractionConstraints] = None):
        self.constraints = constraints or ExtractionConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_content(self, html: str, extraction_type: ExtractionType, constraints: Optional[ExtractionConstraints] = None) -> ExtractionResult:
        """Extract content following L5 architecture principles"""
        extraction_constraints = constraints or self.constraints
        self.logger.info(f"Extracting {extraction_type.value} from HTML content")
        
        # L5 Input validation
        self._validate_input(html)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(html):
            raise SecurityError("HTML content failed L5 safety validation")
        
        try:
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract based on type
            if extraction_type == ExtractionType.TEXT:
                items = self._extract_text(soup, extraction_constraints)
            elif extraction_type == ExtractionType.LINKS:
                items = self._extract_links(soup, extraction_constraints)
            elif extraction_type == ExtractionType.IMAGES:
                items = self._extract_images(soup, extraction_constraints)
            elif extraction_type == ExtractionType.METADATA:
                items = self._extract_metadata(soup, extraction_constraints)
            elif extraction_type == ExtractionType.TABLES:
                items = self._extract_tables(soup, extraction_constraints)
            elif extraction_type == ExtractionType.LISTS:
                items = self._extract_lists(soup, extraction_constraints)
            elif extraction_type == ExtractionType.HEADINGS:
                items = self._extract_headings(soup, extraction_constraints)
            elif extraction_type == ExtractionType.FORMS:
                items = self._extract_forms(soup, extraction_constraints)
            else:
                raise ValueError(f"Unsupported extraction type: {extraction_type}")
            
            # Create extraction result
            result = ExtractionResult(
                extraction_type=extraction_type,
                items=items[:extraction_constraints.max_items],
                metadata={
                    'item_count': len(items),
                    'total_found': len(items),
                    'extraction_type': extraction_type.value
                },
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Extraction completed: {len(result.items)} items extracted")
            return result
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return ExtractionResult(
                extraction_type=extraction_type,
                metadata={'error': str(e)},
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _extract_text(self, soup: BeautifulSoup, constraints: ExtractionConstraints) -> List[Dict[str, Any]]:
        """Extract text content"""
        items = []
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text from allowed tags
        for tag_name in constraints.allowed_tags:
            elements = soup.find_all(tag_name)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) <= constraints.max_text_length:
                    # Sanitize content if required
                    if constraints.sanitize_content:
                        text = self._sanitize_text(text)
                    
                    items.append({
                        'tag': tag_name,
                        'text': text,
                        'length': len(text),
                        'word_count': len(text.split())
                    })
        
        return items
    
    def _extract_links(self, soup: BeautifulSoup, constraints: ExtractionConstraints) -> List[Dict[str, Any]]:
        """Extract links"""
        items = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Validate link safety
            if self._is_safe_link(href):
                items.append({
                    'url': href,
                    'text': text,
                    'title': link.get('title', ''),
                    'target': link.get('target', ''),
                    'is_external': href.startswith('http')
                })
        
        return items
    
    def _extract_images(self, soup: BeautifulSoup, constraints: ExtractionConstraints) -> List[Dict[str, Any]]:
        """Extract images"""
        items = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            # Validate image safety
            if self._is_safe_image(src):
                items.append({
                    'src': src,
                    'alt': alt,
                    'title': title,
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        
        return items
    
    def _extract_metadata(self, soup: BeautifulSoup, constraints: ExtractionConstraints) -> List[Dict[str, Any]]:
        """Extract metadata"""
        items = []
        
        # Extract title
        title_elem = soup.find('title')
        if title_elem:
            items.append({
                'type': 'title',
                'content': title_elem.get_text(strip=True)
            })
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                items.append({
                    'type': 'meta',
                    'name': name,
                    'content': content
                })
        
        return items
    
    def _extract_tables(self, soup: BeautifulSoup, constraints: ExtractionConstraints) -> List[Dict[str, Any]]:
        """Extract tables"""
        items = []
        
        for table in soup.find_all('table'):
            rows = []
            
            # Extract header
            header = table.find('tr')
            if header:
                header_cells = [th.get_text(strip=True) for th in header.find_all(['th', 'td'])]
                rows.append(header_cells)
            
            # Extract data rows
            for row in table.find_all('tr')[1:]:  # Skip header
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            
            if rows:
                items.append({
                    'type': 'table',
                    'rows': rows,
                    'row_count': len(rows),
                    'column_count': len(rows[0]) if rows else 0
                })
        
        return items
    
    def _extract_lists(self, soup: BeautifulSoup, constraints: ExtractionConstraints) -> List[Dict[str, Any]]:
        """Extract lists"""
        items = []
        
        for list_elem in soup.find_all(['ul', 'ol']):
            list_items = []
            
            for li in list_elem.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                if text:
                    list_items.append(text)
            
            if list_items:
                items.append({
                    'type': list_elem.name,
                    'items': list_items,
                    'item_count': len(list_items)
                })
        
        return items
    
    def _extract_headings(self, soup: BeautifulSoup, constraints: ExtractionConstraints) -> List[Dict[str, Any]]:
        """Extract headings"""
        items = []
        
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                if text:
                    items.append({
                        'level': level,
                        'text': text,
                        'id': heading.get('id', ''),
                        'word_count': len(text.split())
                    })
        
        return items
    
    def _extract_forms(self, soup: BeautifulSoup, constraints: ExtractionConstraints) -> List[Dict[str, Any]]:
        """Extract forms"""
        items = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'fields': []
            }
            
            # Extract form fields
            for field in form.find_all(['input', 'select', 'textarea']):
                field_data = {
                    'type': field.get('type', field.name),
                    'name': field.get('name', ''),
                    'id': field.get('id', ''),
                    'required': field.get('required', False)
                }
                
                if field.name == 'select':
                    options = [option.get_text(strip=True) for option in field.find_all('option')]
                    field_data['options'] = options
                
                form_data['fields'].append(field_data)
            
            items.append(form_data)
        
        return items
    
    def validate_safety(self, content: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script", "javascript:", "eval(", "exec(", "__import__"]
            content_lower = content.lower()
            for pattern in dangerous_patterns:
                if pattern in content_lower:
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check content size
            if len(content) > 1000000:  # 1MB limit
                self.logger.error("Content exceeds size limit")
                return False
            
            # Check for suspicious attributes
            dangerous_attrs = ["onclick", "onload", "onerror", "onmouseover"]
            for attr in dangerous_attrs:
                if f"{attr}=" in content_lower:
                    self.logger.error(f"Dangerous attribute detected: {attr}")
                    return False
            
            self.logger.info("Content passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text content"""
        # Remove potentially dangerous characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Limit repeated characters
        text = re.sub(r'(.)\1{10,}', r'\1\1\1', text)
        
        return text.strip()
    
    def _is_safe_link(self, href: str) -> bool:
        """Check if a link is safe"""
        # Skip javascript and data URLs
        unsafe_schemes = ['javascript:', 'data:', 'ftp:', 'file:']
        for scheme in unsafe_schemes:
            if href.lower().startswith(scheme):
                return False
        
        # Check for XSS patterns
        xss_patterns = ['<script', '<img', '<iframe', 'onload=', 'onerror=']
        href_lower = href.lower()
        for pattern in xss_patterns:
            if pattern in href_lower:
                return False
        
        return True
    
    def _is_safe_image(self, src: str) -> bool:
        """Check if an image source is safe"""
        # Skip data URLs that might contain malicious content
        if src.lower().startswith('data:'):
            return False
        
        # Check for XSS patterns
        xss_patterns = ['<script', '<img', '<iframe', 'onload=', 'onerror=']
        src_lower = src.lower()
        for pattern in xss_patterns:
            if pattern in src_lower:
                return False
        
        return True
    
    def _validate_input(self, content: str) -> None:
        """L5 Input validation"""
        if not isinstance(content, str):
            raise ValueError("Content must be a string")
        
        if not content.strip():
            raise ValueError("Content cannot be empty")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class BrowserExtractionUtilsInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, utils: BrowserExtractionUtils):
        self._utils = utils
    
    def extract_from_html(self, html: str, extraction_type: str, max_items: int = 100) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            extract_type = ExtractionType(extraction_type)
            constraints = ExtractionConstraints(max_items=max_items)
            
            result = self._utils.extract_content(html, extract_type, constraints)
            
            return {
                "success": True,
                "extraction_type": result.extraction_type.value,
                "item_count": len(result.items),
                "items": result.items,
                "metadata": result.metadata,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class BrowserExtractionUtilsFactory:
    """L5 Factory for creating browser extraction utils instances"""
    
    @staticmethod
    def create_utils(constraints: Optional[ExtractionConstraints] = None) -> BrowserExtractionUtils:
        return BrowserExtractionUtilsImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[ExtractionConstraints] = None) -> BrowserExtractionUtilsInterface:
        utils = BrowserExtractionUtilsFactory.create_utils(constraints)
        return BrowserExtractionUtilsInterface(utils)

# L5 Export for module usage
__all__ = [
    "ExtractionType",
    "ExtractionStatus",
    "ExtractionConstraints",
    "ExtractionResult",
    "BrowserExtractionUtils",
    "BrowserExtractionUtilsImpl",
    "BrowserExtractionUtilsInterface",
    "BrowserExtractionUtilsFactory",
    "SecurityError"
]
