#!/usr/bin/env python3
"""
File Tool
Section 5: Tool Contracts - INFRA tool family
"""

from typing import Dict, Any, List, Optional
import logging
import json
import os

logger = logging.getLogger(__name__)

class FileTool:
    """File IO abstraction"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_file_size = self.config.get("max_file_size", "10MB")
        self.allowed_extensions = self.config.get("allowed_extensions", [".json", ".txt", ".md", ".csv"])
        self.base_path = self.config.get("base_path", "/tmp")
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file content"""
        try:
            # Validate file path
            full_path = os.path.join(self.base_path, file_path)
            
            # Simulate file reading
            if file_path.endswith(".json"):
                mock_content = {
                    "name": "John Doe",
                    "role": "Software Engineer",
                    "skills": ["Python", "AWS", "Docker"],
                    "experience": "5 years"
                }
            elif file_path.endswith(".txt") or file_path.endswith(".md"):
                mock_content = "John Doe - Software Engineer\n\nSkills: Python, AWS, Docker\nExperience: 5 years"
            elif file_path.endswith(".csv"):
                mock_content = "name,role,skills\nJohn Doe,Software Engineer,Python,AWS,Docker"
            else:
                mock_content = "Generic file content"
            
            result = {
                "status": "success",
                "content": mock_content,
                "file_path": full_path,
                "size": len(str(mock_content)),
                "encoding": encoding,
                "extension": os.path.splitext(file_path)[1]
            }
            
            logger.info(f"File read successfully: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return {"status": "error", "error": str(e), "file_path": file_path}
    
    def write_file(self, file_path: str, content: Any, encoding: str = "utf-8") -> Dict[str, Any]:
        """Write content to file"""
        try:
            # Validate file path and extension
            full_path = os.path.join(self.base_path, file_path)
            extension = os.path.splitext(file_path)[1]
            
            if extension not in self.allowed_extensions:
                return {"status": "error", "error": f"File extension {extension} not allowed", "file_path": file_path}
            
            # Format content based on file type
            if extension == ".json" and isinstance(content, (dict, list)):
                formatted_content = json.dumps(content, indent=2)
            else:
                formatted_content = str(content)
            
            # Simulate file writing
            bytes_written = len(formatted_content.encode(encoding))
            
            result = {
                "status": "success",
                "file_path": full_path,
                "bytes_written": bytes_written,
                "encoding": encoding,
                "extension": extension
            }
            
            logger.info(f"File written successfully: {file_path} ({bytes_written} bytes)")
            return result
            
        except Exception as e:
            logger.error(f"File write failed: {e}")
            return {"status": "error", "error": str(e), "file_path": file_path}
    
    def append_file(self, file_path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Append content to file"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            
            # Simulate file append
            bytes_appended = len(content.encode(encoding))
            
            result = {
                "status": "success",
                "file_path": full_path,
                "bytes_appended": bytes_appended,
                "encoding": encoding
            }
            
            logger.info(f"Content appended to file: {file_path} ({bytes_appended} bytes)")
            return result
            
        except Exception as e:
            logger.error(f"File append failed: {e}")
            return {"status": "error", "error": str(e), "file_path": file_path}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete file"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            
            # Simulate file deletion
            result = {
                "status": "success",
                "file_path": full_path,
                "deleted": True
            }
            
            logger.info(f"File deleted successfully: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return {"status": "error", "error": str(e), "file_path": file_path}
    
    def list_files(self, directory: str = "", pattern: str = "*") -> List[Dict[str, Any]]:
        """List files in directory"""
        try:
            full_dir = os.path.join(self.base_path, directory)
            
            # Simulate directory listing
            mock_files = [
                {"name": "resume.json", "path": os.path.join(full_dir, "resume.json"), "size": 1024, "type": "file"},
                {"name": "cover_letter.txt", "path": os.path.join(full_dir, "cover_letter.txt"), "size": 512, "type": "file"},
                {"name": "skills.md", "path": os.path.join(full_dir, "skills.md"), "size": 256, "type": "file"},
                {"name": "documents", "path": os.path.join(full_dir, "documents"), "size": 0, "type": "directory"}
            ]
            
            # Filter by pattern if specified
            if pattern != "*":
                mock_files = [f for f in mock_files if pattern in f["name"]]
            
            logger.info(f"Listed {len(mock_files)} files in directory: {directory}")
            return mock_files
            
        except Exception as e:
            logger.error(f"File listing failed: {e}")
            return []
    
    def copy_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """Copy file from source to destination"""
        try:
            full_source = os.path.join(self.base_path, source_path)
            full_destination = os.path.join(self.base_path, destination_path)
            
            # Simulate file copy
            result = {
                "status": "success",
                "source_path": full_source,
                "destination_path": full_destination,
                "bytes_copied": 1024  # Mock size
            }
            
            logger.info(f"File copied: {source_path} -> {destination_path}")
            return result
            
        except Exception as e:
            logger.error(f"File copy failed: {e}")
            return {"status": "error", "error": str(e), "source_path": source_path, "destination_path": destination_path}
    
    def move_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """Move file from source to destination"""
        try:
            full_source = os.path.join(self.base_path, source_path)
            full_destination = os.path.join(self.base_path, destination_path)
            
            # Simulate file move
            result = {
                "status": "success",
                "source_path": full_source,
                "destination_path": full_destination,
                "moved": True
            }
            
            logger.info(f"File moved: {source_path} -> {destination_path}")
            return result
            
        except Exception as e:
            logger.error(f"File move failed: {e}")
            return {"status": "error", "error": str(e), "source_path": source_path, "destination_path": destination_path}
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            
            # Simulate file info
            mock_info = {
                "name": os.path.basename(file_path),
                "path": full_path,
                "size": 1024,
                "extension": os.path.splitext(file_path)[1],
                "created_at": "2023-01-01T00:00:00Z",
                "modified_at": "2023-12-01T00:00:00Z",
                "is_file": True,
                "is_directory": False
            }
            
            logger.info(f"Retrieved file info: {file_path}")
            return mock_info
            
        except Exception as e:
            logger.error(f"File info retrieval failed: {e}")
            return {"error": str(e), "file_path": file_path}

def create_file_tool(config: Optional[Dict[str, Any]] = None) -> FileTool:
    """Factory function to create file tool instance"""
    return FileTool(config)

# Re-export components
__all__ = [
    'FileTool', 'create_file_tool'
]
