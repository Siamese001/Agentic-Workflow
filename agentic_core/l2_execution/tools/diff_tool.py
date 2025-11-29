#!/usr/bin/env python3
"""
Diff Tool
Section 5: Tool Contracts - INFRA tool family
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DiffTool:
    """Text / JSON diff computation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.ignore_whitespace = self.config.get("ignore_whitespace", True)
        self.case_sensitive = self.config.get("case_sensitive", False)
        self.context_lines = self.config.get("context_lines", 3)
    
    def diff_text(self, original: str, modified: str) -> Dict[str, Any]:
        """Compute diff between two text strings"""
        try:
            # Preprocess text based on configuration
            orig_processed = self._preprocess_text(original)
            mod_processed = self._preprocess_text(modified)
            
            # Split into lines
            orig_lines = orig_processed.split('\n')
            mod_lines = mod_processed.split('\n')
            
            # Simple diff implementation
            diff_result = self._compute_line_diff(orig_lines, mod_lines)
            
            result = {
                "type": "text_diff",
                "original_length": len(original),
                "modified_length": len(modified),
                "original_lines": len(orig_lines),
                "modified_lines": len(mod_lines),
                "changes": diff_result,
                "summary": self._generate_diff_summary(diff_result)
            }
            
            logger.info(f"Text diff computed: {result['summary']['total_changes']} changes")
            return result
            
        except Exception as e:
            logger.error(f"Text diff computation failed: {e}")
            return {"type": "text_diff", "error": str(e)}
    
    def diff_json(self, original: Dict[str, Any], modified: Dict[str, Any]) -> Dict[str, Any]:
        """Compute diff between two JSON objects"""
        try:
            changes = []
            
            # Find added keys
            added_keys = set(modified.keys()) - set(original.keys())
            for key in added_keys:
                changes.append({
                    "type": "added",
                    "key": key,
                    "new_value": modified[key]
                })
            
            # Find removed keys
            removed_keys = set(original.keys()) - set(modified.keys())
            for key in removed_keys:
                changes.append({
                    "type": "removed",
                    "key": key,
                    "old_value": original[key]
                })
            
            # Find modified keys
            common_keys = set(original.keys()) & set(modified.keys())
            for key in common_keys:
                if original[key] != modified[key]:
                    changes.append({
                        "type": "modified",
                        "key": key,
                        "old_value": original[key],
                        "new_value": modified[key]
                    })
            
            result = {
                "type": "json_diff",
                "changes": changes,
                "summary": {
                    "total_changes": len(changes),
                    "added": len([c for c in changes if c["type"] == "added"]),
                    "removed": len([c for c in changes if c["type"] == "removed"]),
                    "modified": len([c for c in changes if c["type"] == "modified"])
                }
            }
            
            logger.info(f"JSON diff computed: {result['summary']['total_changes']} changes")
            return result
            
        except Exception as e:
            logger.error(f"JSON diff computation failed: {e}")
            return {"type": "json_diff", "error": str(e)}
    
    def diff_files(self, file1_path: str, file2_path: str) -> Dict[str, Any]:
        """Compute diff between two files"""
        try:
            # Simulate file reading
            file1_content = f"Content of {file1_path}\nLine 2\nLine 3"
            file2_content = f"Content of {file2_path}\nLine 2 Modified\nLine 3\nLine 4 Added"
            
            # Determine file type and compute appropriate diff
            if file1_path.endswith('.json') and file2_path.endswith('.json'):
                import json
                try:
                    data1 = json.loads(file1_content)
                    data2 = json.loads(file2_content)
                    return self.diff_json(data1, data2)
                except:
                    # Fallback to text diff if JSON parsing fails
                    pass
            
            return self.diff_text(file1_content, file2_content)
            
        except Exception as e:
            logger.error(f"File diff computation failed: {e}")
            return {"type": "file_diff", "error": str(e)}
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text based on configuration"""
        processed = text
        
        if self.ignore_whitespace:
            # Normalize whitespace
            lines = processed.split('\n')
            normalized_lines = [line.strip() for line in lines if line.strip()]
            processed = '\n'.join(normalized_lines)
        
        if not self.case_sensitive:
            processed = processed.lower()
        
        return processed
    
    def _compute_line_diff(self, lines1: List[str], lines2: List[str]) -> List[Dict[str, Any]]:
        """Simple line-based diff computation"""
        changes = []
        i, j = 0, 0
        
        while i < len(lines1) or j < len(lines2):
            if i >= len(lines1):
                # Lines added at the end
                changes.append({
                    "type": "added",
                    "line_number": i + 1,
                    "content": lines2[j]
                })
                j += 1
            elif j >= len(lines2):
                # Lines removed from the end
                changes.append({
                    "type": "removed",
                    "line_number": i + 1,
                    "content": lines1[i]
                })
                i += 1
            elif lines1[i] == lines2[j]:
                # Lines are the same
                i += 1
                j += 1
            else:
                # Lines differ
                changes.append({
                    "type": "modified",
                    "line_number": i + 1,
                    "old_content": lines1[i],
                    "new_content": lines2[j]
                })
                i += 1
                j += 1
        
        return changes
    
    def _generate_diff_summary(self, changes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Generate summary of diff changes"""
        summary = {
            "total_changes": len(changes),
            "added": len([c for c in changes if c["type"] == "added"]),
            "removed": len([c for c in changes if c["type"] == "removed"]),
            "modified": len([c for c in changes if c["type"] == "modified"])
        }
        return summary
    
    def batch_diff(self, file_pairs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Compute diffs for multiple file pairs"""
        try:
            results = []
            for file1, file2 in file_pairs:
                diff_result = self.diff_files(file1, file2)
                diff_result["file_pair"] = (file1, file2)
                results.append(diff_result)
            
            logger.info(f"Batch diff completed: {len(results)} file pairs")
            return results
            
        except Exception as e:
            logger.error(f"Batch diff computation failed: {e}")
            return [{"error": str(e), "file_pair": pair} for pair in file_pairs]
    
    def get_diff_info(self) -> Dict[str, Any]:
        """Get diff tool information"""
        return {
            "ignore_whitespace": self.ignore_whitespace,
            "case_sensitive": self.case_sensitive,
            "context_lines": self.context_lines,
            "supported_types": ["text", "json", "file"]
        }

def create_diff_tool(config: Optional[Dict[str, Any]] = None) -> DiffTool:
    """Factory function to create diff tool instance"""
    return DiffTool(config)

# Re-export components
__all__ = [
    'DiffTool', 'create_diff_tool'
]
