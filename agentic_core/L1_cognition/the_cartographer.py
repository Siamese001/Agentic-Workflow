"""
TheCartographer - L6 Semantic Mapping & Multi-Repository Awareness

Maps entire codebase (including additional repo roots) into semantic context.
Generates one-sentence summaries for every file using Gemini LLM.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


class TheCartographer:
    """
    Maps codebases into semantic context for architectural queries.
    
    Scans:
    - Primary repository root
    - ADDITIONAL_REPO_ROOTS from environment variables
    - Generates file summaries using Gemini
    - Excludes patterns: .git, __pycache__, node_modules, etc.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize TheCartographer.
        
        Args:
            llm_client: LLM client for generating summaries
        """
        self.llm_client = llm_client
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        # Repository roots
        self.primary_root = Path.cwd()
        self.additional_roots = self._get_additional_roots()
        
        # File summaries cache
        self.file_summaries = {}
        
        # Exclusion patterns
        self.exclude_patterns = {
            ".git", "__pycache__", ".pytest_cache", ".tox", "venv", ".venv",
            "node_modules", ".idea", ".vscode", "dist", "build", "coverage",
            ".mypy_cache", ".coverage", "*.egg-info", ".DS_Store"
        }
        
    def _get_additional_roots(self) -> List[Path]:
        """
        Get additional repository roots from environment variables.
        
        Returns:
            List of additional repository root paths
        """
        roots = []
        
        # Check ADDITIONAL_REPO_ROOTS (comma-separated)
        env_roots = os.getenv("ADDITIONAL_REPO_ROOTS", "")
        if env_roots:
            for root_path in env_roots.split(","):
                root_path = root_path.strip()
                if root_path and Path(root_path).exists():
                    roots.append(Path(root_path).resolve())
                    LOGGER.info(f"📍 Scanning additional root: {root_path}")
        
        return roots
    
    async def map_all_repositories(self) -> Dict[str, Any]:
        """
        Map all repositories (primary + additional).
        
        Returns:
            Dictionary with mapping results
        """
        LOGGER.info("🗺️  TheCartographer: Beginning semantic mapping")
        
        results = {
            "primary_root": str(self.primary_root),
            "additional_roots": [str(r) for r in self.additional_roots],
            "files_mapped": 0,
            "summaries_generated": 0,
            "repositories": {}
        }
        
        # Map primary repository
        primary_result = await self._map_repository(self.primary_root, "primary")
        results["repositories"]["primary"] = primary_result
        results["files_mapped"] += primary_result["files_mapped"]
        results["summaries_generated"] += primary_result["summaries_generated"]
        
        # Map additional repositories
        for i, root in enumerate(self.additional_roots):
            repo_name = f"additional_{i+1}"
            repo_result = await self._map_repository(root, repo_name)
            results["repositories"][repo_name] = repo_result
            results["files_mapped"] += repo_result["files_mapped"]
            results["summaries_generated"] += repo_result["summaries_generated"]
        
        LOGGER.info(f"✅ TheCartographer: Mapped {results['files_mapped']} files")
        
        return results
    
    async def _map_repository(self, root_path: Path, repo_name: str) -> Dict[str, Any]:
        """
        Map a single repository.
        
        Args:
            root_path: Root directory of the repository
            repo_name: Name identifier for the repository
            
        Returns:
            Mapping result for this repository
        """
        result = {
            "root": str(root_path),
            "files_mapped": 0,
            "summaries_generated": 0,
            "files": {}
        }
        
        # Find all Python files
        python_files = list(root_path.rglob("*.py"))
        
        # Filter out excluded patterns
        filtered_files = []
        for file_path in python_files:
            if not self._should_exclude(file_path):
                filtered_files.append(file_path)
        
        LOGGER.info(f"  📁 {repo_name}: Found {len(filtered_files)} Python files")
        
        # Process each file
        for file_path in filtered_files:
            relative_path = file_path.relative_to(root_path)
            file_key = f"{repo_name}/{relative_path}"
            
            # Generate summary
            summary = await self._generate_file_summary(file_path)
            
            # Store summary
            self.file_summaries[file_key] = {
                "path": str(relative_path),
                "absolute_path": str(file_path),
                "repository": repo_name,
                "summary": summary,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            }
            
            result["files"][str(relative_path)] = summary
            result["files_mapped"] += 1
            
            if summary:
                result["summaries_generated"] += 1
        
        return result
    
    def _should_exclude(self, file_path: Path) -> bool:
        """
        Check if file should be excluded from mapping.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if should exclude
        """
        # Check any part of the path against exclude patterns
        for part in file_path.parts:
            if part in self.exclude_patterns:
                return True
        
        # Check file patterns
        for pattern in self.exclude_patterns:
            if "*" in pattern:
                # Simple glob matching
                if file_path.name.endswith(pattern.replace("*", "")):
                    return True
        
        return False
    
    async def _generate_file_summary(self, file_path: Path) -> Optional[str]:
        """
        Generate a one-sentence summary of a file using Gemini.
        
        Args:
            file_path: Path to the file
            
        Returns:
            One-sentence summary or None
        """
        if not self.api_key:
            return None
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Truncate if too large
            if len(content) > 2000:
                content = content[:2000] + "..."
            
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
Generate a one-sentence summary of this Python file's purpose:

File: {file_path.name}
Path: {file_path}

Content:
```python
{content}
```

Respond with only one sentence describing what this file does.
"""
            
            response = model.generate_content(prompt)
            summary = response.text.strip()
            
            # Ensure it's a single sentence
            if summary and not summary.endswith('.'):
                summary += '.'
            
            return summary
        
        except Exception as e:
            LOGGER.error(f"Failed to generate summary for {file_path}: {e}")
            return None
    
    def get_file_summary(self, file_path: str, repository: str = "primary") -> Optional[str]:
        """
        Get summary for a specific file.
        
        Args:
            file_path: Relative path to the file
            repository: Repository name
            
        Returns:
            File summary or None
        """
        key = f"{repository}/{file_path}"
        return self.file_summaries.get(key, {}).get("summary")
    
    def search_summaries(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search file summaries by keyword.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching files with summaries
        """
        query_lower = query.lower()
        matches = []
        
        for file_key, data in self.file_summaries.items():
            # Check path and summary
            if (query_lower in data["path"].lower() or 
                (data["summary"] and query_lower in data["summary"].lower())):
                matches.append(data)
                
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_repository_overview(self, repo_name: str = None) -> Dict[str, Any]:
        """
        Get overview of a repository or all repositories.
        
        Args:
            repo_name: Specific repository or None for all
            
        Returns:
            Repository overview
        """
        if repo_name:
            files = {k: v for k, v in self.file_summaries.items() 
                    if v["repository"] == repo_name}
        else:
            files = self.file_summaries
        
        # Calculate statistics
        total_files = len(files)
        total_size = sum(f["size"] for f in files.values())
        files_with_summaries = sum(1 for f in files.values() if f["summary"])
        
        # Group by directory
        directories = {}
        for file_data in files.values():
            dir_path = str(Path(file_data["path"]).parent)
            if dir_path not in directories:
                directories[dir_path] = {"count": 0, "size": 0}
            directories[dir_path]["count"] += 1
            directories[dir_path]["size"] += file_data["size"]
        
        return {
            "repository": repo_name or "all",
            "total_files": total_files,
            "total_size": total_size,
            "files_with_summaries": files_with_summaries,
            "coverage_percent": (files_with_summaries / total_files * 100) if total_files > 0 else 0,
            "directories": directories
        }


# Global instance
_the_cartographer: Optional[TheCartographer] = None


def get_cartographer() -> TheCartographer:
    """Get or create the global TheCartographer instance."""
    global _the_cartographer
    if _the_cartographer is None:
        _the_cartographer = TheCartographer()
    return _the_cartographer


async def initialize_cartographer(llm_client=None):
    """
    Initialize TheCartographer and map all repositories.
    
    Args:
        llm_client: LLM client instance
    """
    global _the_cartographer
    _the_cartographer = TheCartographer(llm_client)
    
    # Map all repositories
    await _the_cartographer.map_all_repositories()
    
    LOGGER.info("TheCartographer initialized and repositories mapped")


# Convenience functions
async def map_repositories() -> Dict[str, Any]:
    """Map all repositories."""
    cartographer = get_cartographer()
    return await cartographer.map_all_repositories()


def search_files(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search file summaries."""
    cartographer = get_cartographer()
    return cartographer.search_summaries(query, limit)
