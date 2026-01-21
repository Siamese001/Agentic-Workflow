"""
ETL Pipeline for L5 Meta-Learning System

Implements Extract, Transform, Load processes for:
1. Initial Backfill - Historical data loading into Qdrant
2. Continuous Ingestion - Real-time updates from Redis to Qdrant
"""

import ast
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
import git
from botocore.exceptions import ClientError
from core.qdrant_cache import QdrantCache
from core.semantic_gatekeeper import SemanticGatekeeper

from schemas.canon_models import CanonEntry

logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """A chunk of code with its context and metadata."""
    content: str
    start_line: int
    end_line: int
    node_type: str  # function, class, module, etc.
    name: str
    file_path: str
    ast_json: Dict[str, Any]
    metadata: Dict[str, Any]


class ASTAwareChunker:
    """
    Splits Python code into semantically meaningful chunks
    using AST analysis to preserve integrity.
    """

    def __init__(self, max_chunk_size: int = 2000):
        """Initialize the chunker."""
        self.max_chunk_size = max_chunk_size
        self.logger = logging.getLogger(f"{__name__}.ASTAwareChunker")

    def chunk_file(self, file_path: Path) -> List[CodeChunk]:
        """
        Chunk a Python file into AST-aware segments.

        Args:
            file_path: Path to the Python file

        Returns:
            List of CodeChunk objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Extract chunks
            chunks = []

            # Module-level docstring and imports
            module_chunk = self._extract_module_chunk(tree, content, file_path)
            if module_chunk:
                chunks.append(module_chunk)

            # Functions and classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunk = self._extract_function_chunk(
                        node, content, file_path)
                    if chunk:
                        chunks.append(chunk)
                elif isinstance(node, ast.ClassDef):
                    chunk = self._extract_class_chunk(node, content, file_path)
                    if chunk:
                        chunks.append(chunk)

            self.logger.info(f"Chunked {file_path} into {len(chunks)} chunks")
            return chunks

        except Exception as e:
self.logger.error(f"Failed to chunk {file_path}: {e}")
            return []

    def _extract_module_chunk(self, tree: ast.AST, content: str, file_path: Path) -> Optional[CodeChunk]:
        """Extract module-level code (imports, docstring)."""
        lines = content.split('\n')
        module_lines = []

        # Module docstring
        if (tree.body and isinstance(tree.body[0], ast.Expr) and
                isinstance(tree.body[0].value, ast.Constant)):
            module_lines.extend(lines[:tree.body[0].end_lineno])
            start_idx = tree.body[0].end_lineno
        else:
            start_idx = 0

        # Imports
        for node in tree.body[start_idx:]:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_lines.extend(lines[node.lineno - 1:node.end_lineno])
            else:
                break

        if not module_lines:
            return None

        chunk_content = '\n'.join(module_lines)
        ast_json = ast.dump(ast.parse(chunk_content), include_attributes=True)

        return CodeChunk(
            content=chunk_content,
            start_line=1,
            end_line=len(module_lines),
            node_type="module",
            name=file_path.stem,
            file_path=str(file_path),
            ast_json=ast_json,
            metadata={
                "chunk_type": "module",
                "imports": self._extract_imports(chunk_content)
            }
        )

    def _extract_function_chunk(self, node: ast.FunctionDef, content: str, file_path: Path) -> Optional[CodeChunk]:
        """Extract a function or method as a chunk."""
        lines = content.split('\n')
        chunk_lines = lines[node.lineno - 1:node.end_lineno]
        chunk_content = '\n'.join(chunk_lines)

        # Check size
        if len(chunk_content) > self.max_chunk_size:
            self.logger.warning(f"Function {node.name} exceeds max chunk size")
            return None

        try:
            ast_json = ast.dump(ast.parse(chunk_content),
                                include_attributes=True)
        except SyntaxError:
# Might be a method with incomplete syntax
            return None

        return CodeChunk(
            content=chunk_content,
            start_line=node.lineno,
            end_line=node.end_lineno,
            node_type="function",
            name=node.name,
            file_path=str(file_path),
            ast_json=ast_json,
            metadata={
                "chunk_type": "function",
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "args": [arg.arg for arg in node.args.args],
                "decorators": [ast.dump(d) for d in node.decorator_list]
            }
        )

    def _extract_class_chunk(self, node: ast.ClassDef, content: str, file_path: Path) -> Optional[CodeChunk]:
        """Extract a class as a chunk."""
        lines = content.split('\n')
        chunk_lines = lines[node.lineno - 1:node.end_lineno]
        chunk_content = '\n'.join(chunk_lines)

        # Check size
        if len(chunk_content) > self.max_chunk_size:
            self.logger.warning(f"Class {node.name} exceeds max chunk size")
            return None

        try:
            ast_json = ast.dump(ast.parse(chunk_content),
                                include_attributes=True)
        except SyntaxError:
return None

        # Extract methods and properties
        methods = []
        properties = []
        bases = []

        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(ast.dump(base))

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        properties.append(target.id)

        return CodeChunk(
            content=chunk_content,
            start_line=node.lineno,
            end_line=node.end_lineno,
            node_type="class",
            name=node.name,
            file_path=str(file_path),
            ast_json=ast_json,
            metadata={
                "chunk_type": "class",
                "bases": bases,
                "methods": methods,
                "properties": properties,
                "decorators": [ast.dump(d) for d in node.decorator_list]
            }
        )

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from content."""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
        except Exception:
pass
        return imports


class BackfillPipeline:
    """
    One-time batch process to load historical data into Qdrant.

    Extracts from Git repos, S3, and wikis, transforms with
    chunking and embedding, then loads to Qdrant.
    """

    def __init__(
        self,
        gatekeeper: SemanticGatekeeper,
        qdrant_cache: QdrantCache,
        sources: Dict[str, Any]
    ):
        """
        Initialize the backfill pipeline.

        Args:
            gatekeeper: SemanticGatekeeper for embeddings
            qdrant_cache: Qdrant cache for loading
            sources: Configuration for data sources
        """
        self.gatekeeper = gatekeeper
        self.qdrant_cache = qdrant_cache
        self.sources = sources
        self.chunker = ASTAwareChunker()
        self.logger = logging.getLogger(f"{__name__}.BackfillPipeline")

        # Statistics
        self.stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "vectors_loaded": 0,
            "errors": 0
        }

    async def run(self) -> Dict[str, Any]:
        """
        Execute the backfill pipeline.

        Returns:
            Statistics about the backfill process
        """
        self.logger.info("Starting backfill pipeline...")
        start_time = datetime.utcnow()

        # Extract from all sources
        all_chunks = []

        # Git repositories
        if "git_repos" in self.sources:
            git_chunks = await self._extract_from_git()
            all_chunks.extend(git_chunks)

        # S3 storage
        if "s3_buckets" in self.sources:
            s3_chunks = await self._extract_from_s3()
            all_chunks.extend(s3_chunks)

        # Local files
        if "local_paths" in self.sources:
            local_chunks = await self._extract_from_local()
            all_chunks.extend(local_chunks)

        # Transform chunks to vectors
        entries = await self._transform_chunks(all_chunks)

        # Load to Qdrant
        await self._load_to_qdrant(entries)

        # Calculate statistics
        duration = (datetime.utcnow() - start_time).total_seconds()
        self.stats["duration_seconds"] = duration
        self.stats["chunks_per_second"] = self.stats["chunks_created"] / \
            duration if duration > 0 else 0

        self.logger.info(f"Backfill completed: {self.stats}")
        return self.stats

    async def _extract_from_git(self) -> List[CodeChunk]:
        """Extract code from Git repositories."""
        chunks = []

        for repo_config in self.sources["git_repos"]:
            repo_path = repo_config["path"]
            branch = repo_config.get("branch", "main")

            try:
                repo = git.Repo(repo_path)
                repo.git.checkout(branch)

                # Find all Python files
                for py_file in Path(repo_path).rglob("*.py"):
                    if "__pycache__" in str(py_file):
                        continue

                    file_chunks = self.chunker.chunk_file(py_file)
                    for chunk in file_chunks:
                        # Add Git metadata
                        chunk.metadata.update({
                            "source": "git",
                            "repo": repo_path,
                            "branch": branch,
                            "commit": repo.head.commit.hexsha,
                            "commit_date": datetime.fromtimestamp(repo.head.commit.committed_date).isoformat()
                        })

                    chunks.extend(file_chunks)
                    self.stats["files_processed"] += 1

            except Exception as e:
self.logger.error(
                    f"Failed to extract from Git repo {repo_path}: {e}")
                self.stats["errors"] += 1

        return chunks

    async def _extract_from_s3(self) -> List[CodeChunk]:
        """Extract code from S3 buckets."""
        chunks = []

        for bucket_config in self.sources["s3_buckets"]:
            bucket_name = bucket_config["bucket"]
            prefix = bucket_config.get("prefix", "")

            try:
                s3 = boto3.client('s3')
                paginator = s3.get_paginator('list_objects_v2')

                for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                    for obj in page.get('Contents', []):
                        key = obj['Key']

                        if not key.endswith('.py'):
                            continue

                        # Download file
                        response = s3.get_object(Bucket=bucket_name, Key=key)
                        content = response['Body'].read().decode('utf-8')

                        # Create temporary file for chunking
                        temp_file = Path(f"/tmp/{key.replace('/', '_')}")
                        temp_file.parent.mkdir(parents=True, exist_ok=True)
                        temp_file.write_text(content)

                        file_chunks = self.chunker.chunk_file(temp_file)
                        for chunk in file_chunks:
                            chunk.metadata.update({
                                "source": "s3",
                                "bucket": bucket_name,
                                "key": key,
                                "last_modified": obj['LastModified'].isoformat()
                            })

                        chunks.extend(file_chunks)
                        self.stats["files_processed"] += 1

                        # Clean up
                        temp_file.unlink()

            except ClientError as e:
self.logger.error(
                    f"Failed to extract from S3 bucket {bucket_name}: {e}")
                self.stats["errors"] += 1

        return chunks

    async def _extract_from_local(self) -> List[CodeChunk]:
        """Extract code from local paths."""
        chunks = []

        for path_config in self.sources["local_paths"]:
            base_path = Path(path_config["path"])

            for py_file in base_path.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue

                file_chunks = self.chunker.chunk_file(py_file)
                for chunk in file_chunks:
                    chunk.metadata.update({
                        "source": "local",
                        "base_path": str(base_path),
                        "relative_path": str(py_file.relative_to(base_path))
                    })

                chunks.extend(file_chunks)
                self.stats["files_processed"] += 1

        return chunks

    async def _transform_chunks(self, chunks: List[CodeChunk]) -> List[CanonEntry]:
        """Transform chunks into CanonEntry objects with embeddings."""
        entries = []
        batch_size = 100

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            for chunk in batch:
                try:
                    # Create embedding
                    description = f"{chunk.node_type} {chunk.name} in {chunk.file_path}"
                    vector = self.gatekeeper.embed_action(description)

                    # Create AST hash
                    ast_hash = hashlib.sha256(
                        json.dumps(chunk.ast_json, sort_keys=True).encode()
                    ).hexdigest()

                    # Create CanonEntry
                    entry = CanonEntry(
                        vector=vector,
                        ast_json=chunk.ast_json,
                        ast_hash=ast_hash,
                        policy_key=f"historical:{chunk.node_type}",
                        failure_count=0,
                        success_count=1,  # Historical code assumed validated
                        latency_ms=0,
                        project_tag=chunk.metadata.get("repo", "historical"),
                        metadata={
                            **chunk.metadata,
                            "risk_score": 0,
                            "max_files_touched": 0,
                            "pattern_type": "historical",
                            "agent_name": "BackfillPipeline",
                            "validation_status": "validated",
                            "is_canon_key": False,
                            "created_at": datetime.utcnow().isoformat(),
                            "last_seen": datetime.utcnow().isoformat(),
                            "promoted_to_l2": "true"
                        }
                    )

                    entries.append(entry)
                    self.stats["chunks_created"] += 1

                except Exception as e:
self.logger.error(
                        f"Failed to transform chunk {chunk.name}: {e}")
                    self.stats["errors"] += 1

            # Progress logging
            if i % (batch_size * 10) == 0:
                self.logger.info(
                    f"Transformed {i + len(batch)}/{len(chunks)} chunks")

        return entries

    async def _load_to_qdrant(self, entries: List[CanonEntry]):
        """Load entries to Qdrant in batches."""
        batch_size = 500

        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]

            try:
                # Upsert batch to Qdrant
                for entry in batch:
                    self.qdrant_cache.upsert(entry)

                self.stats["vectors_loaded"] += len(batch)

                # Progress logging
                if i % (batch_size * 2) == 0:
                    self.logger.info(
                        f"Loaded {i + len(batch)}/{len(entries)} vectors to Qdrant")

            except Exception as e:
self.logger.error(f"Failed to load batch to Qdrant: {e}")
                self.stats["errors"] += 1


class ContinuousIngester:
    """
    Continuous real-time ingestion from Redis to Qdrant.

    Extends the existing promotion worker to handle both
    successes and failures with proper metadata.
    """

    def __init__(
        self,
        gatekeeper: SemanticGatekeeper,
        qdrant_cache: QdrantCache,
        failure_retention_days: int = 90
    ):
        """
        Initialize the continuous ingester.

        Args:
            gatekeeper: SemanticGatekeeper instance
            qdrant_cache: Qdrant cache for L2 storage
            failure_retention_days: Days to retain failure patterns
        """
        self.gatekeeper = gatekeeper
        self.qdrant_cache = qdrant_cache
        self.failure_retention_days = failure_retention_days
        self.logger = logging.getLogger(f"{__name__}.ContinuousIngester")

        # Statistics
        self.stats = {
            "successes_ingested": 0,
            "failures_ingested": 0,
            "errors": 0,
            "last_ingestion": None
        }

    async def ingest_success(self, entry: CanonEntry):
        """
        Ingest a successful pattern to L2.

        Args:
            entry: The successful CanonEntry
        """
        try:
            # Enrich metadata for L2
            entry.metadata["ingestion_type"] = "success"
            entry.metadata["ingestion_timestamp"] = datetime.utcnow(
            ).isoformat()
            entry.metadata["promoted_to_l2"] = "true"

            # Upsert to Qdrant
            self.qdrant_cache.upsert(entry)

            self.stats["successes_ingested"] += 1
            self.stats["last_ingestion"] = datetime.utcnow().isoformat()

            self.logger.info(f"Ingested success pattern: {entry.id}")

        except Exception as e:
self.logger.error(
                f"Failed to ingest success pattern {entry.id}: {e}")
            self.stats["errors"] += 1

    async def ingest_failure(self, entry: CanonEntry, error_trace: str):
        """
        Ingest a failure pattern with error trace.

        Args:
            entry: The failed CanonEntry
            error_trace: Full error trace for analysis
        """
        try:
            # Create failure-specific entry
            failure_entry = CanonEntry(
                vector=entry.vector,
                ast_json=entry.ast_json,
                ast_hash=entry.ast_hash,
                policy_key=entry.policy_key,
                failure_count=entry.failure_count,
                success_count=0,
                latency_ms=entry.latency_ms,
                project_tag=entry.project_tag,
                metadata={
                    **entry.metadata,
                    "ingestion_type": "failure",
                    "ingestion_timestamp": datetime.utcnow().isoformat(),
                    "error_trace": error_trace,
                    "failure_date": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + timedelta(days=self.failure_retention_days)).isoformat()
                }
            )

            # Upsert to Qdrant
            self.qdrant_cache.upsert(failure_entry)

            self.stats["failures_ingested"] += 1
            self.stats["last_ingestion"] = datetime.utcnow().isoformat()

            self.logger.info(f"Ingested failure pattern: {entry.id}")

        except Exception as e:
self.logger.error(
                f"Failed to ingest failure pattern {entry.id}: {e}")
            self.stats["errors"] += 1

    async def cleanup_expired_failures(self):
        """Remove expired failure patterns from L2."""
        try:
            # Find expired failures
            cutoff = datetime.utcnow().isoformat()
            expired = self.qdrant_cache.search(
                query_vector=[0.0] * 768,  # Dummy vector
                filters={
                    "ingestion_type": "failure",
                    "expires_at": {"lte": cutoff}
                },
                limit=1000
            )

            # Delete expired entries
            for item in expired:
                self.qdrant_cache.client.delete(
                    collection_name=self.qdrant_cache.index_name,
                    points_selector={"ids": [item["id"]]}
                )

            self.logger.info(
                f"Cleaned up {len(expired)} expired failure patterns")

        except Exception as e:
self.logger.error(f"Failed to cleanup expired failures: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return self.stats.copy()
