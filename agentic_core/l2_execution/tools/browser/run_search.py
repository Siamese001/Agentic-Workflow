"""
L5 Agentic Core - L2 Execution Layer - Browser Search Tool
Implements L2 Pure Execution Layer for web search operations
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngine(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    CUSTOM = "custom"

class SearchStatus(Enum):
    """L5 Search status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"

@dataclass
class SearchConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_results: int = 10
    max_query_length: int = 1000
    timeout_seconds: int = 30
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    require_safe_search: bool = True
    safety_level: str = "strict"

@dataclass
class SearchResult:
    """L5 Search result structure with full type safety"""
    url: str
    title: str
    description: str
    domain: str
    relevance_score: float = 0.0
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class SearchResponse:
    """L5 Search response structure"""
    search_id: str
    query: str
    engine: SearchEngine
    status: SearchStatus
    results: List[SearchResult] = field(default_factory=list)
    total_results: int = 0
    search_time: float = 0.0
    safety_validated: bool = False
    timestamp: str = ""

class BrowserSearchTool(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def search(self, query: str, engine: SearchEngine, constraints: SearchConstraints) -> SearchResponse:
        """Execute web search with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, query: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class BrowserSearchImpl(BrowserSearchTool):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure web search execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[SearchConstraints] = None):
        self.constraints = constraints or SearchConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search(self, query: str, engine: SearchEngine, constraints: Optional[SearchConstraints] = None) -> SearchResponse:
        """Execute web search following L5 architecture principles"""
        search_constraints = constraints or self.constraints
        self.logger.info(f"Executing search: '{query}' using {engine.value}")
        
        # L5 Input validation
        self._validate_input(query)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(query):
            raise SecurityError("Search query failed L5 safety validation")
        
        # Execute search
        try:
            results = self._execute_search(query, engine, search_constraints)
            
            # Validate results
            validated_results = []
            for result in results:
                if self._validate_result_safety(result, search_constraints):
                    result.safety_validated = True
                    validated_results.append(result)
            
            # Create search response
            response = SearchResponse(
                search_id=self._generate_search_id(),
                query=query,
                engine=engine,
                status=SearchStatus.SUCCESS,
                results=validated_results,
                total_results=len(validated_results),
                search_time=0.0,  # Would be populated with actual timing
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Search completed: {len(validated_results)} results")
            return response
            
        except requests.exceptions.Timeout:
            self.logger.error("Search request timed out")
            return SearchResponse(
                search_id=self._generate_search_id(),
                query=query,
                engine=engine,
                status=SearchStatus.TIMEOUT,
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Search request failed: {e}")
            return SearchResponse(
                search_id=self._generate_search_id(),
                query=query,
                engine=engine,
                status=SearchStatus.FAILED,
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except Exception as e:
            self.logger.error(f"Search execution error: {e}")
            return SearchResponse(
                search_id=self._generate_search_id(),
                query=query,
                engine=engine,
                status=SearchStatus.FAILED,
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _execute_search(self, query: str, engine: SearchEngine, constraints: SearchConstraints) -> List[SearchResult]:
        """Execute the actual search request"""
        if engine == SearchEngine.DUCKDUCKGO:
            return self._search_duckduckgo(query, constraints)
        elif engine == SearchEngine.GOOGLE:
            return self._search_google(query, constraints)
        elif engine == SearchEngine.BING:
            return self._search_bing(query, constraints)
        else:
            raise ValueError(f"Unsupported search engine: {engine}")
    
    def _search_duckduckgo(self, query: str, constraints: SearchConstraints) -> List[SearchResult]:
        """Search using DuckDuckGo"""
        url = "https://duckduckgo.com/html/"
        params = {
            'q': query,
            'kl': 'us-en',
            'safe_search': constraints.require_safe_search
        }
        
        response = self.session.get(url, params=params, timeout=constraints.timeout_seconds)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Parse DuckDuckGo results
        for result_element in soup.find_all('div', class_='result')[:constraints.max_results]:
            title_elem = result_element.find('a', class_='result__a')
            snippet_elem = result_element.find('a', class_='result__snippet')
            
            if title_elem and snippet_elem:
                url = title_elem.get('href', '')
                title = title_elem.get_text(strip=True)
                description = snippet_elem.get_text(strip=True)
                domain = urllib.parse.urlparse(url).netloc
                
                # Skip blocked domains
                if constraints.blocked_domains and domain in constraints.blocked_domains:
                    continue
                
                # Filter by allowed domains if specified
                if constraints.allowed_domains and domain not in constraints.allowed_domains:
                    continue
                
                result = SearchResult(
                    url=url,
                    title=title,
                    description=description,
                    domain=domain,
                    relevance_score=0.8,  # Would be calculated based on actual ranking
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
                results.append(result)
        
        return results
    
    def _search_google(self, query: str, constraints: SearchConstraints) -> List[SearchResult]:
        """Search using Google (placeholder implementation)"""
        # Note: Google search requires API keys for production use
        # This is a simplified implementation for demonstration
        self.logger.warning("Google search requires API key - using placeholder implementation")
        return []
    
    def _search_bing(self, query: str, constraints: SearchConstraints) -> List[SearchResult]:
        """Search using Bing (placeholder implementation)"""
        # Note: Bing search requires API keys for production use
        # This is a simplified implementation for demonstration
        self.logger.warning("Bing search requires API key - using placeholder implementation")
        return []
    
    def validate_safety(self, query: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            query_lower = query.lower()
            for pattern in dangerous_patterns:
                if pattern in query_lower:
                    self.logger.error(f"Dangerous pattern detected in query: {pattern}")
                    return False
            
            # Check query length
            if len(query) > self.constraints.max_query_length:
                self.logger.error("Query exceeds maximum length")
                return False
            
            # Check for potential SQL injection
            sql_patterns = ["drop table", "delete from", "insert into", "update set", "union select"]
            for pattern in sql_patterns:
                if pattern in query_lower:
                    self.logger.error(f"Potential SQL injection detected: {pattern}")
                    return False
            
            # Check for XSS patterns
            xss_patterns = ["<img", "<iframe", "<object", "<embed", "onload=", "onerror="]
            for pattern in xss_patterns:
                if pattern in query_lower:
                    self.logger.error(f"Potential XSS pattern detected: {pattern}")
                    return False
            
            self.logger.info("Query passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_result_safety(self, result: SearchResult, constraints: SearchConstraints) -> bool:
        """Validate individual search result safety"""
        try:
            # Check URL safety
            parsed_url = urllib.parse.urlparse(result.url)
            
            # Only allow HTTP/HTTPS
            if parsed_url.scheme not in ['http', 'https']:
                self.logger.warning(f"Unsafe URL scheme: {parsed_url.scheme}")
                return False
            
            # Check for blocked domains
            if constraints.blocked_domains and result.domain in constraints.blocked_domains:
                self.logger.warning(f"Blocked domain: {result.domain}")
                return False
            
            # Filter by allowed domains if specified
            if constraints.allowed_domains and result.domain not in constraints.allowed_domains:
                self.logger.warning(f"Domain not in allowed list: {result.domain}")
                return False
            
            # Check for suspicious URLs
            suspicious_patterns = ["javascript:", "data:", "ftp:", "file:"]
            for pattern in suspicious_patterns:
                if result.url.lower().startswith(pattern):
                    self.logger.warning(f"Suspicious URL pattern: {pattern}")
                    return False
            
            # Check title and description for dangerous content
            content = f"{result.title} {result.description}".lower()
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            for pattern in dangerous_patterns:
                if pattern in content:
                    self.logger.warning(f"Dangerous pattern in result content: {pattern}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Result safety validation error: {e}")
            return False
    
    def _validate_input(self, query: str) -> None:
        """L5 Input validation"""
        if not isinstance(query, str):
            raise ValueError("Query must be a string")
        
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        if len(query.strip()) < 2:
            raise ValueError("Query too short")
    
    def _generate_search_id(self) -> str:
        """Generate unique search ID"""
        import uuid
        return f"search_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class BrowserSearchInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, tool: BrowserSearchTool):
        self._tool = tool
    
    def execute_search(self, query: str, engine: str = "duckduckgo", max_results: int = 10) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            search_engine = SearchEngine(engine)
            constraints = SearchConstraints(max_results=max_results)
            
            response = self._tool.search(query, search_engine, constraints)
            
            return {
                "success": response.status == SearchStatus.SUCCESS,
                "search_id": response.search_id,
                "query": response.query,
                "engine": response.engine.value,
                "result_count": len(response.results),
                "results": [
                    {
                        "url": result.url,
                        "title": result.title,
                        "description": result.description,
                        "domain": result.domain,
                        "relevance_score": result.relevance_score,
                        "safety_validated": result.safety_validated
                    }
                    for result in response.results
                ],
                "safety_validated": response.safety_validated,
                "timestamp": response.timestamp
            }
        except Exception as e:
            self.logger.error(f"Search execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class BrowserSearchFactory:
    """L5 Factory for creating browser search instances"""
    
    @staticmethod
    def create_tool(constraints: Optional[SearchConstraints] = None) -> BrowserSearchTool:
        return BrowserSearchImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[SearchConstraints] = None) -> BrowserSearchInterface:
        tool = BrowserSearchFactory.create_tool(constraints)
        return BrowserSearchInterface(tool)

# L5 Export for module usage
__all__ = [
    "SearchEngine",
    "SearchStatus",
    "SearchConstraints",
    "SearchResult",
    "SearchResponse",
    "BrowserSearchTool",
    "BrowserSearchImpl",
    "BrowserSearchInterface",
    "BrowserSearchFactory",
    "SecurityError"
]
