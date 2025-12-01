"""
L5 Agentic Core - L2 Execution Layer - Browser Scrape Tool
Implements L2 Pure Execution Layer for web scraping operations
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import urllib.parse
import requests
from bs4 import BeautifulSoup
import re

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapeStatus(Enum):
    """L5 Scrape status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"

class ContentType(Enum):
    """L5 Content type enumeration"""
    TEXT = "text"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"

@dataclass
class ScrapeConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_content_size: int = 1000000  # 1MB
    timeout_seconds: int = 30
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    allowed_content_types: List[ContentType] = field(default_factory=lambda: [ContentType.TEXT, ContentType.HTML])
    require_https: bool = True
    respect_robots_txt: bool = True
    safety_level: str = "strict"

@dataclass
class ScrapeResult:
    """L5 Scrape result structure with full type safety"""
    url: str
    title: str = ""
    content: str = ""
    content_type: ContentType = ContentType.TEXT
    metadata: Dict[str, Any] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class ScrapeResponse:
    """L5 Scrape response structure"""
    scrape_id: str
    url: str
    status: ScrapeStatus
    result: Optional[ScrapeResult] = None
    error_message: str = ""
    scrape_time: float = 0.0
    safety_validated: bool = False
    timestamp: str = ""

class BrowserScrapeTool(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def scrape(self, url: str, constraints: ScrapeConstraints) -> ScrapeResponse:
        """Scrape web content with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, url: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class BrowserScrapeImpl(BrowserScrapeTool):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure web scraping execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[ScrapeConstraints] = None):
        self.constraints = constraints or ScrapeConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape(self, url: str, constraints: Optional[ScrapeConstraints] = None) -> ScrapeResponse:
        """Scrape web content following L5 architecture principles"""
        scrape_constraints = constraints or self.constraints
        self.logger.info(f"Scraping URL: {url}")
        
        # L5 Input validation
        self._validate_input(url)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(url):
            raise SecurityError("URL failed L5 safety validation")
        
        # Execute scrape
        try:
            result = self._execute_scrape(url, scrape_constraints)
            
            # Create scrape response
            response = ScrapeResponse(
                scrape_id=self._generate_scrape_id(),
                url=url,
                status=ScrapeStatus.SUCCESS,
                result=result,
                scrape_time=0.0,  # Would be populated with actual timing
                safety_validated=result.safety_validated,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Scrape completed: {len(result.content)} characters")
            return response
            
        except requests.exceptions.Timeout:
            self.logger.error("Scrape request timed out")
            return ScrapeResponse(
                scrape_id=self._generate_scrape_id(),
                url=url,
                status=ScrapeStatus.TIMEOUT,
                error_message="Request timed out",
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                status = ScrapeStatus.FORBIDDEN
                error = "Access forbidden"
            elif e.response.status_code == 404:
                status = ScrapeStatus.NOT_FOUND
                error = "Page not found"
            else:
                status = ScrapeStatus.FAILED
                error = f"HTTP error: {e.response.status_code}"
            
            self.logger.error(f"HTTP error: {error}")
            return ScrapeResponse(
                scrape_id=self._generate_scrape_id(),
                url=url,
                status=status,
                error_message=error,
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Scrape request failed: {e}")
            return ScrapeResponse(
                scrape_id=self._generate_scrape_id(),
                url=url,
                status=ScrapeStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except Exception as e:
            self.logger.error(f"Scrape execution error: {e}")
            return ScrapeResponse(
                scrape_id=self._generate_scrape_id(),
                url=url,
                status=ScrapeStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _execute_scrape(self, url: str, constraints: ScrapeConstraints) -> ScrapeResult:
        """Execute the actual scraping"""
        response = self.session.get(url, timeout=constraints.timeout_seconds)
        response.raise_for_status()
        
        # Check content length
        content_length = len(response.content)
        if content_length > constraints.max_content_size:
            raise ValueError(f"Content too large: {content_length} > {constraints.max_content_size}")
        
        # Parse content type
        content_type = self._parse_content_type(response.headers.get('content-type', ''))
        if content_type not in constraints.allowed_content_types:
            raise ValueError(f"Content type not allowed: {content_type}")
        
        # Parse HTML content
        if content_type == ContentType.HTML:
            return self._parse_html(response.text, url, constraints)
        elif content_type == ContentType.TEXT:
            return self._parse_text(response.text, url, constraints)
        elif content_type == ContentType.JSON:
            return self._parse_json(response.text, url, constraints)
        else:
            return self._parse_generic(response.text, url, content_type, constraints)
    
    def _parse_html(self, html_content: str, url: str, constraints: ScrapeConstraints) -> ScrapeResult:
        """Parse HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('title')
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # Extract main content (remove script/style elements)
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urllib.parse.urljoin(url, href)
            if self._is_safe_url(absolute_url, constraints):
                links.append(absolute_url)
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urllib.parse.urljoin(url, src)
            if self._is_safe_url(absolute_url, constraints):
                images.append(absolute_url)
        
        # Extract metadata
        metadata = {
            'word_count': len(text_content.split()),
            'char_count': len(text_content),
            'link_count': len(links),
            'image_count': len(images)
        }
        
        return ScrapeResult(
            url=url,
            title=title,
            content=text_content,
            content_type=ContentType.HTML,
            metadata=metadata,
            links=links,
            images=images,
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _parse_text(self, text_content: str, url: str, constraints: ScrapeConstraints) -> ScrapeResult:
        """Parse plain text content"""
        metadata = {
            'word_count': len(text_content.split()),
            'char_count': len(text_content)
        }
        
        return ScrapeResult(
            url=url,
            content=text_content,
            content_type=ContentType.TEXT,
            metadata=metadata,
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _parse_json(self, json_content: str, url: str, constraints: ScrapeConstraints) -> ScrapeResult:
        """Parse JSON content"""
        try:
            import json
            data = json.loads(json_content)
            metadata = {
                'json_keys': len(data) if isinstance(data, dict) else 0,
                'json_type': type(data).__name__
            }
            
            return ScrapeResult(
                url=url,
                content=json_content,
                content_type=ContentType.JSON,
                metadata=metadata,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON content: {e}")
    
    def _parse_generic(self, content: str, url: str, content_type: ContentType, constraints: ScrapeConstraints) -> ScrapeResult:
        """Parse generic content"""
        metadata = {
            'char_count': len(content)
        }
        
        return ScrapeResult(
            url=url,
            content=content,
            content_type=content_type,
            metadata=metadata,
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def validate_safety(self, url: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            
            # Check URL scheme
            if parsed_url.scheme not in ['http', 'https']:
                self.logger.error(f"Unsafe URL scheme: {parsed_url.scheme}")
                return False
            
            # Require HTTPS if specified
            if self.constraints.require_https and parsed_url.scheme != 'https':
                self.logger.error("HTTPS required but not provided")
                return False
            
            # Check for blocked domains
            if self.constraints.blocked_domains and parsed_url.netloc in self.constraints.blocked_domains:
                self.logger.error(f"Blocked domain: {parsed_url.netloc}")
                return False
            
            # Filter by allowed domains if specified
            if self.constraints.allowed_domains and parsed_url.netloc not in self.constraints.allowed_domains:
                self.logger.error(f"Domain not in allowed list: {parsed_url.netloc}")
                return False
            
            # Check for suspicious URL patterns
            suspicious_patterns = ["javascript:", "data:", "ftp:", "file:", "mailto:"]
            for pattern in suspicious_patterns:
                if url.lower().startswith(pattern):
                    self.logger.error(f"Suspicious URL pattern: {pattern}")
                    return False
            
            # Check for potential XSS in URL
            xss_patterns = ["<script", "<img", "<iframe", "javascript:", "onload=", "onerror="]
            url_lower = url.lower()
            for pattern in xss_patterns:
                if pattern in url_lower:
                    self.logger.error(f"Potential XSS in URL: {pattern}")
                    return False
            
            # Check for URL encoding abuse
            if url.count('%') > 10:  # Too much URL encoding
                self.logger.error("Suspicious URL encoding detected")
                return False
            
            self.logger.info("URL passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"URL safety validation error: {e}")
            return False  # Fail-closed
    
    def _is_safe_url(self, url: str, constraints: ScrapeConstraints) -> bool:
        """Check if a URL is safe for extraction"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            
            # Only allow HTTP/HTTPS
            if parsed_url.scheme not in ['http', 'https']:
                return False
            
            # Check blocked domains
            if constraints.blocked_domains and parsed_url.netloc in constraints.blocked_domains:
                return False
            
            # Filter by allowed domains if specified
            if constraints.allowed_domains and parsed_url.netloc not in constraints.allowed_domains:
                return False
            
            # Skip common non-content URLs
            skip_patterns = ['#', 'javascript:', 'mailto:', 'tel:']
            for pattern in skip_patterns:
                if url.lower().startswith(pattern):
                    return False
            
            return True
        except Exception:
            return False
    
    def _parse_content_type(self, content_type_header: str) -> ContentType:
        """Parse content type header"""
        content_type_lower = content_type_header.lower()
        
        if 'html' in content_type_lower:
            return ContentType.HTML
        elif 'json' in content_type_lower:
            return ContentType.JSON
        elif 'xml' in content_type_lower:
            return ContentType.XML
        elif 'text' in content_type_lower:
            return ContentType.TEXT
        else:
            return ContentType.BINARY
    
    def _validate_input(self, url: str) -> None:
        """L5 Input validation"""
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
        
        if not url.strip():
            raise ValueError("URL cannot be empty")
        
        # Basic URL format validation
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
    
    def _generate_scrape_id(self) -> str:
        """Generate unique scrape ID"""
        import uuid
        return f"scrape_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class BrowserScrapeInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, tool: BrowserScrapeTool):
        self._tool = tool
    
    def scrape_url(self, url: str, max_size: int = 1000000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            constraints = ScrapeConstraints(max_content_size=max_size)
            response = self._tool.scrape(url, constraints)
            
            if response.result:
                return {
                    "success": response.status == ScrapeStatus.SUCCESS,
                    "scrape_id": response.scrape_id,
                    "url": response.result.url,
                    "title": response.result.title,
                    "content": response.result.content[:5000],  # Limit content size for response
                    "content_type": response.result.content_type.value,
                    "metadata": response.result.metadata,
                    "link_count": len(response.result.links),
                    "image_count": len(response.result.images),
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
            self.logger.error(f"Scrape execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class BrowserScrapeFactory:
    """L5 Factory for creating browser scrape instances"""
    
    @staticmethod
    def create_tool(constraints: Optional[ScrapeConstraints] = None) -> BrowserScrapeTool:
        return BrowserScrapeImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[ScrapeConstraints] = None) -> BrowserScrapeInterface:
        tool = BrowserScrapeFactory.create_tool(constraints)
        return BrowserScrapeInterface(tool)

# L5 Export for module usage
__all__ = [
    "ScrapeStatus",
    "ContentType",
    "ScrapeConstraints",
    "ScrapeResult",
    "ScrapeResponse",
    "BrowserScrapeTool",
    "BrowserScrapeImpl",
    "BrowserScrapeInterface",
    "BrowserScrapeFactory",
    "SecurityError"
]
