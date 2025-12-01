"""
L5 Agentic Core - L2 Execution Layer - File Find Tool
Implements L2 Pure Execution Layer for safe file search operations
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import os
import re
import pathlib

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchMode(Enum):
    """L5 Search mode enumeration"""
    TEXT = "text"
    REGEX = "regex"
    EXACT = "exact"
    CASE_SENSITIVE = "case_sensitive"
    CASE_INSENSITIVE = "case_insensitive"

class SearchStatus(Enum):
    """L5 Search status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    ACCESS_DENIED = "access_denied"
    PATTERN_ERROR = "pattern_error"

@dataclass
class SearchConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_results: int = 100
    max_file_size: int = 10000000  # 10MB
    max_line_length: int = 10000
    allowed_extensions: List[str] = field(default_factory=lambda: ['.txt', '.py', '.json', '.yaml', '.yml', '.md', '.html', '.htm'])
    blocked_extensions: List[str] = field(default_factory=lambda: ['.exe', '.bat', '.cmd', '.scr', '.dll', '.so'])
    require_safe_path: bool = True
    safety_level: str = "strict"

@dataclass
class SearchResult:
    """L5 Search result structure with full type safety"""
    file_path: str
    line_number: int
    line_content: str
    match_start: int = 0
    match_end: int = 0
    context_before: List[str] = field(default_factory=list)
    context_after: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class SearchResponse:
    """L5 Search response structure"""
    search_id: str
    pattern: str
    search_path: str
    status: SearchStatus
    results: List[SearchResult] = field(default_factory=list)
    total_matches: int = 0
    files_searched: int = 0
    error_message: str = ""
    safety_validated: bool = False
    timestamp: str = ""

class FileFindTool(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def find_in_file(self, file_path: str, pattern: str, mode: SearchMode, constraints: SearchConstraints) -> SearchResponse:
        """Search in file with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, file_path: str, pattern: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class FileFindImpl(FileFindTool):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure file search execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[SearchConstraints] = None):
        self.constraints = constraints or SearchConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def find_in_file(self, file_path: str, pattern: str, mode: SearchMode, constraints: Optional[SearchConstraints] = None) -> SearchResponse:
        """Search in file following L5 architecture principles"""
        search_constraints = constraints or self.constraints
        self.logger.info(f"Searching in file: {file_path} for pattern: {pattern}")
        
        # L5 Input validation
        self._validate_input(file_path, pattern)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(file_path, pattern):
            raise SecurityError("File search parameters failed L5 safety validation")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return SearchResponse(
                    search_id=self._generate_search_id(),
                    pattern=pattern,
                    search_path=file_path,
                    status=SearchStatus.NOT_FOUND,
                    error_message="File not found",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > search_constraints.max_file_size:
                return SearchResponse(
                    search_id=self._generate_search_id(),
                    pattern=pattern,
                    search_path=file_path,
                    status=SearchStatus.FAILED,
                    error_message=f"File too large: {file_size} > {search_constraints.max_file_size}",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Validate file extension
            if not self._validate_file_extension(file_path, search_constraints):
                return SearchResponse(
                    search_id=self._generate_search_id(),
                    pattern=pattern,
                    search_path=file_path,
                    status=SearchStatus.FAILED,
                    error_message="File type not allowed",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Perform search
            results = self._search_file(file_path, pattern, mode, search_constraints)
            
            # Create search response
            response = SearchResponse(
                search_id=self._generate_search_id(),
                pattern=pattern,
                search_path=file_path,
                status=SearchStatus.SUCCESS,
                results=results[:search_constraints.max_results],
                total_matches=len(results),
                files_searched=1,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Search completed: {len(response.results)} matches found")
            return response
            
        except PermissionError:
            self.logger.error("Access denied to file")
            return SearchResponse(
                search_id=self._generate_search_id(),
                pattern=pattern,
                search_path=file_path,
                status=SearchStatus.ACCESS_DENIED,
                error_message="Access denied",
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except re.error as e:
            self.logger.error(f"Regex pattern error: {e}")
            return SearchResponse(
                search_id=self._generate_search_id(),
                pattern=pattern,
                search_path=file_path,
                status=SearchStatus.PATTERN_ERROR,
                error_message=f"Invalid regex pattern: {str(e)}",
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except Exception as e:
            self.logger.error(f"File search error: {e}")
            return SearchResponse(
                search_id=self._generate_search_id(),
                pattern=pattern,
                search_path=file_path,
                status=SearchStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _search_file(self, file_path: str, pattern: str, mode: SearchMode, constraints: SearchConstraints) -> List[SearchResult]:
        """Perform the actual file search"""
        results = []
        
        try:
            # Read file with safe encoding
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                lines = file.readlines()
            
            # Prepare search pattern
            search_pattern = self._prepare_pattern(pattern, mode)
            
            # Search through lines
            for line_num, line in enumerate(lines, 1):
                # Skip extremely long lines
                if len(line) > constraints.max_line_length:
                    continue
                
                line_stripped = line.rstrip('\n\r')
                
                # Search for pattern
                matches = self._search_line(line_stripped, search_pattern, mode)
                
                for match in matches:
                    # Validate match safety
                    if not self._validate_match_safety(line_stripped, match):
                        continue
                    
                    # Get context lines
                    context_before = []
                    context_after = []
                    
                    # Get context before (up to 2 lines)
                    for i in range(max(0, line_num - 3), line_num - 1):
                        if i < len(lines):
                            context_before.append(lines[i].rstrip('\n\r'))
                    
                    # Get context after (up to 2 lines)
                    for i in range(line_num, min(len(lines), line_num + 3)):
                        context_after.append(lines[i].rstrip('\n\r'))
                    
                    result = SearchResult(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line_stripped,
                        match_start=match.start(),
                        match_end=match.end(),
                        context_before=context_before,
                        context_after=context_after,
                        safety_validated=True,
                        timestamp=self._get_timestamp()
                    )
                    results.append(result)
            
            return results
            
        except UnicodeDecodeError:
            # Try alternative encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                        lines = file.readlines()
                    
                    # Retry search with alternative encoding
                    return self._search_with_lines(file_path, lines, pattern, mode, constraints)
                except Exception:
                    continue
            
            raise ValueError("Unable to decode file with safe encoding")
    
    def _search_with_lines(self, file_path: str, lines: List[str], pattern: str, mode: SearchMode, constraints: SearchConstraints) -> List[SearchResult]:
        """Search with pre-read lines"""
        results = []
        search_pattern = self._prepare_pattern(pattern, mode)
        
        for line_num, line in enumerate(lines, 1):
            if len(line) > constraints.max_line_length:
                continue
            
            line_stripped = line.rstrip('\n\r')
            matches = self._search_line(line_stripped, search_pattern, mode)
            
            for match in matches:
                if self._validate_match_safety(line_stripped, match):
                    result = SearchResult(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line_stripped,
                        match_start=match.start(),
                        match_end=match.end(),
                        safety_validated=True,
                        timestamp=self._get_timestamp()
                    )
                    results.append(result)
        
        return results
    
    def _prepare_pattern(self, pattern: str, mode: SearchMode) -> str:
        """Prepare search pattern based on mode"""
        if mode == SearchMode.CASE_INSENSITIVE:
            return pattern.lower()
        elif mode == SearchMode.CASE_SENSITIVE:
            return pattern
        else:
            return pattern
    
    def _search_line(self, line: str, pattern: str, mode: SearchMode) -> List[re.Match]:
        """Search for pattern in a line"""
        try:
            if mode == SearchMode.TEXT:
                # Simple text search
                if mode == SearchMode.CASE_INSENSITIVE:
                    search_line = line.lower()
                    pattern_lower = pattern.lower()
                    start = search_line.find(pattern_lower)
                    if start != -1:
                        # Create a mock match object
                        class MockMatch:
                            def __init__(self, start, end):
                                self._start = start
                                self._end = end
                            def start(self): return self._start
                            def end(self): return self._end
                        return [MockMatch(start, start + len(pattern))]
                else:
                    start = line.find(pattern)
                    if start != -1:
                        class MockMatch:
                            def __init__(self, start, end):
                                self._start = start
                                self._end = end
                            def start(self): return self._start
                            def end(self): return self._end
                        return [MockMatch(start, start + len(pattern))]
                
                return []
            
            elif mode == SearchMode.REGEX:
                # Regex search
                flags = re.IGNORECASE if mode == SearchMode.CASE_INSENSITIVE else 0
                return list(re.finditer(pattern, line, flags))
            
            elif mode == SearchMode.EXACT:
                # Exact match
                if mode == SearchMode.CASE_INSENSITIVE:
                    if line.strip().lower() == pattern.lower():
                        class MockMatch:
                            def __init__(self, line):
                                self._line = line
                            def start(self): return 0
                            def end(self): return len(self._line)
                        return [MockMatch(line)]
                else:
                    if line.strip() == pattern:
                        class MockMatch:
                            def __init__(self, line):
                                self._line = line
                            def start(self): return 0
                            def end(self): return len(self._line)
                        return [MockMatch(line)]
                
                return []
            
            return []
            
        except Exception as e:
            self.logger.error(f"Line search error: {e}")
            return []
    
    def _validate_match_safety(self, line: str, match: re.Match) -> bool:
        """Validate match for safety"""
        try:
            # Extract matched content
            matched_content = line[match.start():match.end()]
            
            # Check for dangerous patterns in match
            dangerous_patterns = ["<script", "javascript:", "eval(", "exec(", "__import__"]
            match_lower = matched_content.lower()
            
            for pattern in dangerous_patterns:
                if pattern in match_lower:
                    self.logger.warning(f"Dangerous pattern in match: {pattern}")
                    return False  # Skip this match
            
            return True
            
        except Exception as e:
            self.logger.error(f"Match safety validation error: {e}")
            return False
    
    def _validate_file_extension(self, file_path: str, constraints: SearchConstraints) -> bool:
        """Validate file extension"""
        _, ext = os.path.splitext(file_path.lower())
        
        # Check blocked extensions
        if ext in constraints.blocked_extensions:
            return False
        
        # Check allowed extensions
        if constraints.allowed_extensions and ext not in constraints.allowed_extensions:
            return False
        
        return True
    
    def validate_safety(self, file_path: str, pattern: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Validate file path safety
            normalized_path = os.path.normpath(file_path)
            
            # Check for path traversal
            if '..' in normalized_path:
                self.logger.error("Path traversal attempt detected")
                return False
            
            # Check absolute path requirements
            if self.constraints.require_safe_path and not os.path.isabs(normalized_path):
                self.logger.error("Absolute path required")
                return False
            
            # Validate pattern safety
            if not self._validate_pattern_safety(pattern):
                self.logger.error("Pattern failed safety validation")
                return False
            
            self.logger.info("File search parameters passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_pattern_safety(self, pattern: str) -> bool:
        """Validate search pattern for safety"""
        try:
            # Check for dangerous regex patterns
            dangerous_patterns = [
                r'\\x[0-9a-fA-F]{2}',  # Hex escape sequences
                r'\\[0-7]{3}',        # Octal escape sequences
                r'\\p\{',             # Unicode property (can be complex)
                r'\(\?\(',            # Recursive patterns
                r'\(\?\>',            # Atomic groups (can cause DoS)
                r'\*\+',              # Possessive quantifiers
                r'\?\+',              # Possessive quantifiers
            ]
            
            for dangerous_pattern in dangerous_patterns:
                if re.search(dangerous_pattern, pattern):
                    self.logger.warning(f"Potentially dangerous regex pattern: {dangerous_pattern}")
                    # Allow but log warning
            
            # Check pattern length
            if len(pattern) > 1000:
                self.logger.error("Pattern too long")
                return False
            
            # Check for nested quantifiers (can cause exponential backtracking)
            if re.search(r'\*.*\*|\+.*\+|\{.*\}.*\{', pattern):
                self.logger.warning("Nested quantifiers detected")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pattern safety validation error: {e}")
            return False
    
    def _validate_input(self, file_path: str, pattern: str) -> None:
        """L5 Input validation"""
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string")
        
        if not isinstance(pattern, str):
            raise ValueError("Pattern must be a string")
        
        if not file_path.strip():
            raise ValueError("File path cannot be empty")
        
        if not pattern.strip():
            raise ValueError("Pattern cannot be empty")
    
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
class FileFindInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, tool: FileFindTool):
        self._tool = tool
    
    def find_in_file(self, file_path: str, pattern: str, mode: str = "text", max_results: int = 100) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            search_mode = SearchMode(mode)
            constraints = SearchConstraints(max_results=max_results)
            
            response = self._tool.find_in_file(file_path, pattern, search_mode, constraints)
            
            return {
                "success": response.status == SearchStatus.SUCCESS,
                "search_id": response.search_id,
                "pattern": response.pattern,
                "file_path": response.search_path,
                "match_count": len(response.results),
                "total_matches": response.total_matches,
                "results": [
                    {
                        "line_number": result.line_number,
                        "line_content": result.line_content,
                        "match_start": result.match_start,
                        "match_end": result.match_end,
                        "context_before": result.context_before,
                        "context_after": result.context_after,
                        "safety_validated": result.safety_validated
                    }
                    for result in response.results
                ],
                "safety_validated": response.safety_validated,
                "timestamp": response.timestamp
            }
        except Exception as e:
            self.logger.error(f"File search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class FileFindFactory:
    """L5 Factory for creating file find instances"""
    
    @staticmethod
    def create_tool(constraints: Optional[SearchConstraints] = None) -> FileFindTool:
        return FileFindImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[SearchConstraints] = None) -> FileFindInterface:
        tool = FileFindFactory.create_tool(constraints)
        return FileFindInterface(tool)

# L5 Export for module usage
__all__ = [
    "SearchMode",
    "SearchStatus",
    "SearchConstraints",
    "SearchResult",
    "SearchResponse",
    "FileFindTool",
    "FileFindImpl",
    "FileFindInterface",
    "FileFindFactory",
    "SecurityError"
]
