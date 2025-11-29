#!/usr/bin/env python3
"""
File Wrappers
Section 5: Tool Contracts - Wrapper classes for file system integrations
"""

from typing import Dict, Any, Optional, List, Union
import logging
import os
import json

logger = logging.getLogger(__name__)

class FileWrapper:
    """Base wrapper class for file system operations"""
    
    def __init__(self, base_path: str, config: Optional[Dict[str, Any]] = None):
        self.base_path = base_path
        self.config = config or {}
        self.allowed_extensions = self.config.get("allowed_extensions", [])
        self.max_file_size = self.config.get("max_file_size", 10 * 1024 * 1024)  # 10MB
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file contents"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            
            if not os.path.exists(full_path):
                return {"status": "error", "error": "File not found"}
            
            if not self._is_allowed_file(full_path):
                return {"status": "error", "error": "File type not allowed"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "status": "success",
                "content": content,
                "size": len(content),
                "path": full_path
            }
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            
            if not self._is_allowed_file(full_path):
                return {"status": "error", "error": "File type not allowed"}
            
            if len(content.encode('utf-8')) > self.max_file_size:
                return {"status": "error", "error": "File size exceeds limit"}
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "status": "success",
                "size": len(content),
                "path": full_path
            }
        except Exception as e:
            logger.error(f"File write failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def list_files(self, directory: str = "") -> Dict[str, Any]:
        """List files in directory"""
        try:
            full_path = os.path.join(self.base_path, directory)
            
            if not os.path.exists(full_path):
                return {"status": "error", "error": "Directory not found"}
            
            files = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if os.path.isfile(item_path) and self._is_allowed_file(item_path):
                    files.append({
                        "name": item,
                        "size": os.path.getsize(item_path),
                        "path": item_path
                    })
            
            return {
                "status": "success",
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            logger.error(f"File listing failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _is_allowed_file(self, file_path: str) -> bool:
        """Check if file is allowed based on extension"""
        if not self.allowed_extensions:
            return True
        
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.allowed_extensions

class JSONFileWrapper(FileWrapper):
    """Wrapper for JSON file operations"""
    
    def __init__(self, base_path: str, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        config["allowed_extensions"] = [".json"]
        super().__init__(base_path, config)
    
    def read_json(self, file_path: str) -> Dict[str, Any]:
        """Read JSON file"""
        result = self.read_file(file_path)
        if result["status"] == "success":
            try:
                data = json.loads(result["content"])
                result["data"] = data
                del result["content"]  # Remove raw content, keep parsed data
            except json.JSONDecodeError as e:
                result["status"] = "error"
                result["error"] = f"Invalid JSON: {e}"
        return result
    
    def write_json(self, file_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Write data to JSON file"""
        try:
            content = json.dumps(data, indent=2)
            return self.write_file(file_path, content)
        except Exception as e:
            logger.error(f"JSON write failed: {e}")
            return {"status": "error", "error": str(e)}

class TextFileWrapper(FileWrapper):
    """Wrapper for text file operations"""
    
    def __init__(self, base_path: str, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        config["allowed_extensions"] = [".txt", ".md", ".csv", ".log"]
        super().__init__(base_path, config)
    
    def read_lines(self, file_path: str, max_lines: int = 1000) -> Dict[str, Any]:
        """Read file as lines"""
        result = self.read_file(file_path)
        if result["status"] == "success":
            lines = result["content"].split('\n')
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                result["truncated"] = True
            result["lines"] = lines
            del result["content"]
        return result
    
    def append_to_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Append content to file"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            
            if not self._is_allowed_file(full_path):
                return {"status": "error", "error": "File type not allowed"}
            
            with open(full_path, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
            
            return {
                "status": "success",
                "appended": len(content),
                "path": full_path
            }
        except Exception as e:
            logger.error(f"File append failed: {e}")
            return {"status": "error", "error": str(e)}

def create_file_wrapper(file_type: str, base_path: str, config: Optional[Dict[str, Any]] = None) -> FileWrapper:
    """Factory function to create appropriate file wrapper"""
    if file_type == "json":
        return JSONFileWrapper(base_path, config)
    elif file_type == "text":
        return TextFileWrapper(base_path, config)
    else:
        return FileWrapper(base_path, config)

# Re-export components
__all__ = [
    'FileWrapper', 'JSONFileWrapper', 'TextFileWrapper', 'create_file_wrapper'
]
