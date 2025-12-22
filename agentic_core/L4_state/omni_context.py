"""
TheOmniContext - L6 Semantic Context Buffer

Concatenates all source code from mapped repositories into a single context buffer
for complex architectural queries and RAG-based agent retrieval.
"""

import logging
from typing import Any, Dict, Optional

LOGGER = logging.getLogger(__name__)


class TheOmniContext:
    """
    Manages the omniscient context buffer for architectural queries.

    Provides:
    - Concatenated source code from all repositories
    - Indexed access to file contents
    - Pinecone integration for RAG
    - Query capabilities across entire codebase
    """

    def __init__(self, pinecone_client=None):
        """
        Initialize TheOmniContext.

        Args:
            pinecone_client: Pinecone client for RAG storage
        """
        self.pinecone_client = pinecone_client
        self.index_name = "omni-context"

        # Context buffer
        self.context_buffer = ""
        self.file_index = {}  # Maps file paths to buffer positions

        # File contents cache
        self.file_contents = {}

        # Exclusion patterns for content
        self.content_exclude_patterns = {
            ".min.js", ".map", ".lock", "__pycache__", ".pyc",
            "test_", "_test.py", "conftest.py"
        }

    async def build_context(self, file_summaries: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the omniscient context buffer from file summaries.

        Args:
            file_summaries: File summaries from TheCartographer

        Returns:
            Build result with statistics
        """
        LOGGER.info("🌐 TheOmniContext: Building context buffer")

        # Clear existing buffer
        self.context_buffer = ""
        self.file_index = {}
        self.file_contents = {}

        # Statistics
        stats = {
            "files_processed": 0,
            "total_characters": 0,
            "repositories": set(),
            "skipped": 0
        }

        # Process each file
        buffer_parts = []
        current_position = 0

        for file_key, data in file_summaries.items():
            file_path = data["absolute_path"]
            relative_path = data["path"]
            repository = data["repository"]

            # Check if should exclude
            if self._should_exclude_content(relative_path):
                stats["skipped"] += 1
                continue

            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Limit content size
                if len(content) > 5000:
                    content = content[:5000] + "\n...[truncated]..."

                # Create file header
                header = f"\n{'='*60}\n"
                header += f"FILE: {repository}/{relative_path}\n"
                header += f"SUMMARY: {data['summary'] or 'No summary'}\n"
                header += f"{'='*60}\n\n"

                # Add to buffer
                start_pos = current_position
                buffer_parts.append(header)
                buffer_parts.append(content)
                buffer_parts.append("\n\n")

                current_position += len(header) + len(content) + 4

                # Index file
                self.file_index[file_key] = {
                    "start": start_pos,
                    "end": current_position - 1,
                    "repository": repository,
                    "path": relative_path,
                    "summary": data["summary"]
                }

                # Cache content
                self.file_contents[file_key] = content

                # Update stats
                stats["files_processed"] += 1
                stats["total_characters"] += len(content)
                stats["repositories"].add(repository)

            except Exception as e:
                LOGGER.error(f"Failed to read {file_path}: {e}")
                stats["skipped"] += 1

        # Build final buffer
        self.context_buffer = "".join(buffer_parts)
        stats["repositories"] = list(stats["repositories"])
        stats["buffer_size"] = len(self.context_buffer)

        LOGGER.info(f"✅ TheOmniContext: Built buffer with {stats['files_processed']} files")

        return stats

    def _should_exclude_content(self, file_path: str) -> bool:
        """
        Check if file content should be excluded from buffer.

        Args:
            file_path: Relative file path

        Returns:
            True if should exclude
        """
        # Check patterns
        for pattern in self.content_exclude_patterns:
            if pattern in file_path:
                return True

        # Skip very large binary files
        if any(file_path.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.zip']):
            return True

        return False

    def query_context(self, query: str, context_window: int = 10000) -> Dict[str, Any]:
        """
        Query the omniscient context buffer.

        Args:
            query: Search query
            context_window: Maximum characters to return

        Returns:
            Query results with relevant context
        """
        if not self.context_buffer:
            return {"error": "Context buffer not built"}

        # Simple text search (could be enhanced with semantic search)
        query_lower = query.lower()
        matches = []

        # Search in file index first
        for file_key, index_data in self.file_index.items():
            # Check file path and summary
            if (query_lower in index_data["path"].lower() or
                (index_data["summary"] and query_lower in index_data["summary"].lower())):

                # Extract content
                content = self.get_file_content(file_key)
                if content:
                    matches.append({
                        "file": file_key,
                        "repository": index_data["repository"],
                        "path": index_data["path"],
                        "summary": index_data["summary"],
                        "content": content[:1000] + "..." if len(content) > 1000 else content
                    })

        # Also search in full buffer if needed
        if len(matches) < 5:
            buffer_lower = self.context_buffer.lower()
            if query_lower in buffer_lower:
                # Find all occurrences
                start = 0
                while True:
                    pos = buffer_lower.find(query_lower, start)
                    if pos == -1:
                        break

                    # Find which file this position belongs to
                    for file_key, index_data in self.file_index.items():
                        if index_data["start"] <= pos <= index_data["end"]:
                            # Extract context around match
                            context_start = max(0, pos - 500)
                            context_end = min(len(self.context_buffer), pos + 500)
                            context = self.context_buffer[context_start:context_end]

                            if not any(m["file"] == file_key for m in matches):
                                matches.append({
                                    "file": file_key,
                                    "repository": index_data["repository"],
                                    "path": index_data["path"],
                                    "summary": index_data["summary"],
                                    "content": context
                                })
                            break

                    start = pos + 1

        # Limit results
        if len(matches) > 10:
            matches = matches[:10]

        return {
            "query": query,
            "matches_found": len(matches),
            "results": matches
        }

    def get_file_content(self, file_key: str) -> Optional[str]:
        """
        Get content for a specific file.

        Args:
            file_key: File key (repository/path)

        Returns:
            File content or None
        """
        return self.file_contents.get(file_key)

    def get_context_window(self, file_key: str, window_size: int = 2000) -> Optional[str]:
        """
        Get a context window around a file.

        Args:
            file_key: File key
            window_size: Size of context window

        Returns:
            Context window or None
        """
        if file_key not in self.file_index:
            return None

        index = self.file_index[file_key]
        start = max(0, index["start"] - window_size // 2)
        end = min(len(self.context_buffer), index["end"] + window_size // 2)

        return self.context_buffer[start:end]

    async def sync_to_pinecone(self, file_summaries: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync file summaries to Pinecone for RAG retrieval.

        Args:
            file_summaries: File summaries from TheCartographer

        Returns:
            Sync results
        """
        if not self.pinecone_client:
            LOGGER.warning("Pinecone client not available - skipping sync")
            return {"synced": 0, "error": "Pinecone not available"}

        try:
            # Initialize index if needed
            from L1_cognition.reflection_agent import ReflectionAgent

            reflection = ReflectionAgent(pinecone_client=self.pinecone_client)

            # Upsert each file summary as a trace
            synced = 0
            for file_key, data in file_summaries.items():
                # Create trace-like structure
                trace = {
                    "task": f"Index file: {data['path']}",
                    "code_before": self.get_file_content(file_key) or "",
                    "context": {
                        "file": data["path"],
                        "repository": data["repository"],
                        "summary": data["summary"]
                    },
                    "signals": ["INDEXED"]
                }

                # Use reflection agent to internalize
                analysis = await reflection._analyze_success_pattern(trace)
                success = await reflection._internalize_trace(trace, analysis)

                if success:
                    synced += 1

            LOGGER.info(f"📚 TheOmniContext: Synced {synced} files to Pinecone")

            return {
                "synced": synced,
                "total": len(file_summaries),
                "index": self.index_name
            }

        except Exception as e:
            LOGGER.error(f"Failed to sync to Pinecone: {e}")
            return {"synced": 0, "error": str(e)}

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the context buffer.

        Returns:
            Statistics dictionary
        """
        if not self.context_buffer:
            return {"built": False}

        # Calculate repository distribution
        repo_counts = {}
        for index_data in self.file_index.values():
            repo = index_data["repository"]
            repo_counts[repo] = repo_counts.get(repo, 0) + 1

        return {
            "built": True,
            "total_files": len(self.file_index),
            "buffer_size": len(self.context_buffer),
            "repositories": repo_counts,
            "average_file_size": len(self.context_buffer) // len(self.file_index) if self.file_index else 0
        }


# Global instance
_the_omni_context: Optional[TheOmniContext] = None


def get_omni_context() -> TheOmniContext:
    """Get or create the global TheOmniContext instance."""
    global _the_omni_context
    if _the_omni_context is None:
        _the_omni_context = TheOmniContext()
    return _the_omni_context


async def initialize_omni_context(pinecone_client=None, file_summaries: Dict[str, Any] = None):
    """
    Initialize TheOmniContext and build buffer.

    Args:
        pinecone_client: Pinecone client for RAG
        file_summaries: File summaries from TheCartographer
    """
    global _the_omni_context
    _the_omni_context = TheOmniContext(pinecone_client)

    if file_summaries:
        await _the_omni_context.build_context(file_summaries)
        LOGGER.info("TheOmniContext initialized with file summaries")
    else:
        LOGGER.info("TheOmniContext initialized (no summaries provided)")


# Convenience functions
async def query_omni_context(query: str) -> Dict[str, Any]:
    """Query the omniscient context."""
    omni = get_omni_context()
    return omni.query_context(query)
