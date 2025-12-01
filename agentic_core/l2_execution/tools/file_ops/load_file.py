"""
L5 Agentic Core - L2 Execution Layer - File Load Tool
Implements L2 Pure Execution Layer for safe file loading operations
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import os
import pathlib
import mimetypes

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileStatus(Enum):
    """L5 File status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    ACCESS_DENIED = "access_denied"
    TOO_LARGE = "too_large"
    UNSAFE_TYPE = "unsafe_type"

class FileType(Enum):
    """L5 File type enumeration"""
    TEXT = "text"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    BINARY = "binary"
    UNKNOWN = "unknown"

@dataclass
class FileConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_file_size: int = 10000000  # 10MB
    allowed_extensions: List[str] = field(default_factory=lambda: ['.txt', '.json', '.yaml', '.yml', '.xml', '.csv', '.py', '.md'])
    blocked_extensions: List[str] = field(default_factory=lambda: ['.exe', '.bat', '.cmd', '.scr', '.dll', '.so'])
    allowed_mime_types: List[str] = field(default_factory=lambda: ['text/', 'application/json', 'application/xml', 'text/yaml'])
    require_safe_path: bool = True
    safety_level: str = "strict"

@dataclass
class FileResult:
    """L5 File result structure with full type safety"""
    file_path: str
    file_type: FileType
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class FileResponse:
    """L5 File response structure"""
    operation_id: str
    file_path: str
    status: FileStatus
    result: Optional[FileResult] = None
    error_message: str = ""
    safety_validated: bool = False
    timestamp: str = ""

class FileLoadTool(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def load_file(self, file_path: str, constraints: FileConstraints) -> FileResponse:
        """Load file with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, file_path: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class FileLoadImpl(FileLoadTool):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure file loading execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[FileConstraints] = None):
        self.constraints = constraints or FileConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_file(self, file_path: str, constraints: Optional[FileConstraints] = None) -> FileResponse:
        """Load file following L5 architecture principles"""
        load_constraints = constraints or self.constraints
        self.logger.info(f"Loading file: {file_path}")
        
        # L5 Input validation
        self._validate_input(file_path)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(file_path):
            raise SecurityError("File path failed L5 safety validation")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return FileResponse(
                    operation_id=self._generate_operation_id(),
                    file_path=file_path,
                    status=FileStatus.NOT_FOUND,
                    error_message="File not found",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > load_constraints.max_file_size:
                return FileResponse(
                    operation_id=self._generate_operation_id(),
                    file_path=file_path,
                    status=FileStatus.TOO_LARGE,
                    error_message=f"File too large: {file_size} > {load_constraints.max_file_size}",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Determine file type
            file_type = self._determine_file_type(file_path, load_constraints)
            if file_type == FileType.UNKNOWN:
                return FileResponse(
                    operation_id=self._generate_operation_id(),
                    file_path=file_path,
                    status=FileStatus.UNSAFE_TYPE,
                    error_message="Unknown or unsafe file type",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Load file content
            content = self._load_file_content(file_path, file_type)
            
            # Create file result
            result = FileResult(
                file_path=file_path,
                file_type=file_type,
                content=content,
                metadata=self._extract_metadata(file_path, file_size, file_type),
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            # Create file response
            response = FileResponse(
                operation_id=self._generate_operation_id(),
                file_path=file_path,
                status=FileStatus.SUCCESS,
                result=result,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"File loaded successfully: {len(content)} characters")
            return response
            
        except PermissionError:
            self.logger.error("Access denied to file")
            return FileResponse(
                operation_id=self._generate_operation_id(),
                file_path=file_path,
                status=FileStatus.ACCESS_DENIED,
                error_message="Access denied",
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except Exception as e:
            self.logger.error(f"File loading error: {e}")
            return FileResponse(
                operation_id=self._generate_operation_id(),
                file_path=file_path,
                status=FileStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _determine_file_type(self, file_path: str, constraints: FileConstraints) -> FileType:
        """Determine file type with safety validation"""
        # Get file extension
        _, ext = os.path.splitext(file_path.lower())
        
        # Check blocked extensions
        if ext in constraints.blocked_extensions:
            raise SecurityError(f"Blocked file extension: {ext}")
        
        # Check allowed extensions
        if constraints.allowed_extensions and ext not in constraints.allowed_extensions:
            raise SecurityError(f"File extension not allowed: {ext}")
        
        # Determine file type based on extension
        type_map = {
            '.txt': FileType.TEXT,
            '.json': FileType.JSON,
            '.yaml': FileType.YAML,
            '.yml': FileType.YAML,
            '.xml': FileType.XML,
            '.csv': FileType.CSV,
            '.py': FileType.TEXT,
            '.md': FileType.TEXT,
            '.html': FileType.TEXT,
            '.htm': FileType.TEXT
        }
        
        return type_map.get(ext, FileType.UNKNOWN)
    
    def _load_file_content(self, file_path: str, file_type: FileType) -> str:
        """Load file content based on type"""
        try:
            if file_type == FileType.BINARY:
                # For binary files, return a hex representation or error
                raise ValueError("Binary file loading not supported for text extraction")
            
            # Load as text with encoding detection
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
            
            # Validate content safety
            if not self._validate_content_safety(content):
                raise SecurityError("File content failed safety validation")
            
            return content
            
        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                        content = file.read()
                    
                    if self._validate_content_safety(content):
                        return content
                except Exception:
                    continue
            
            raise ValueError("Unable to decode file with safe encoding")
    
    def _validate_content_safety(self, content: str) -> bool:
        """Validate file content for safety"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = ["<script", "javascript:", "eval(", "exec(", "__import__"]
            content_lower = content.lower()
            
            for pattern in dangerous_patterns:
                if pattern in content_lower:
                    self.logger.warning(f"Potentially dangerous pattern in content: {pattern}")
                    # Allow text files but log warning
            
            # Check for extremely long lines (potential buffer overflow)
            lines = content.split('\n')
            for line in lines:
                if len(line) > 10000:  # Very long line
                    self.logger.warning("Very long line detected in file")
                    break
            
            return True
        except Exception as e:
            self.logger.error(f"Content safety validation error: {e}")
            return False
    
    def _extract_metadata(self, file_path: str, file_size: int, file_type: FileType) -> Dict[str, Any]:
        """Extract file metadata"""
        try:
            stat = os.stat(file_path)
            
            metadata = {
                'file_size': file_size,
                'file_type': file_type.value,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK)
            }
            
            # Add MIME type if available
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                metadata['mime_type'] = mime_type
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata extraction error: {e}")
            return {'error': str(e)}
    
    def validate_safety(self, file_path: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Normalize path
            normalized_path = os.path.normpath(file_path)
            
            # Check for path traversal attempts
            if '..' in normalized_path:
                self.logger.error("Path traversal attempt detected")
                return False
            
            # Check absolute path requirements
            if self.constraints.require_safe_path and not os.path.isabs(normalized_path):
                self.logger.error("Absolute path required")
                return False
            
            # Check for dangerous file names
            dangerous_names = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9']
            basename = os.path.basename(normalized_path).lower()
            if basename in dangerous_names:
                self.logger.error(f"Dangerous file name: {basename}")
                return False
            
            # Check file extension
            _, ext = os.path.splitext(normalized_path.lower())
            if ext in self.constraints.blocked_extensions:
                self.logger.error(f"Blocked file extension: {ext}")
                return False
            
            if self.constraints.allowed_extensions and ext not in self.constraints.allowed_extensions:
                self.logger.error(f"File extension not allowed: {ext}")
                return False
            
            self.logger.info("File path passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"File path safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, file_path: str) -> None:
        """L5 Input validation"""
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string")
        
        if not file_path.strip():
            raise ValueError("File path cannot be empty")
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        import uuid
        return f"load_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class FileLoadInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, tool: FileLoadTool):
        self._tool = tool
    
    def load_file(self, file_path: str, max_size: int = 10000000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            constraints = FileConstraints(max_file_size=max_size)
            response = self._tool.load_file(file_path, constraints)
            
            if response.result:
                return {
                    "success": response.status == FileStatus.SUCCESS,
                    "operation_id": response.operation_id,
                    "file_path": response.result.file_path,
                    "file_type": response.result.file_type.value,
                    "content": response.result.content[:10000],  # Limit content size for response
                    "metadata": response.result.metadata,
                    "content_length": len(response.result.content),
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
            self.logger.error(f"File loading failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class FileLoadFactory:
    """L5 Factory for creating file load instances"""
    
    @staticmethod
    def create_tool(constraints: Optional[FileConstraints] = None) -> FileLoadTool:
        return FileLoadImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[FileConstraints] = None) -> FileLoadInterface:
        tool = FileLoadFactory.create_tool(constraints)
        return FileLoadInterface(tool)

# L5 Export for module usage
__all__ = [
    "FileStatus",
    "FileType",
    "FileConstraints",
    "FileResult",
    "FileResponse",
    "FileLoadTool",
    "FileLoadImpl",
    "FileLoadInterface",
    "FileLoadFactory",
    "SecurityError"
]
