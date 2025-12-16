"""
ETL Pipeline Module - Canon Validator System

Facade module that wraps the existing ETL implementation
to match the master prompt specifications.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from sentence_transformers import SentenceTransformer

from db_manager import HybridDatabaseManager
from schemas import CanonEntry, UnifiedSemanticElement, generate_ast_structure

logger = logging.getLogger(__name__)

# Initialize embedding model
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')


def generate_entry(code_str: str, metadata: Optional[Dict[str, Any]] = None) -> CanonEntry:
    """
    Generate a CanonEntry from code string.

    This function:
    1. Parses code_str to generate Python AST
    2. Generates Embedding using sentence-transformers
    3. Returns a CanonEntry with all components

    Args:
        code_str: Python code string to process
        metadata: Optional metadata to include

    Returns:
        CanonEntry with embedding, AST, and metadata
    """
    # Generate AST structure
    ast_structure = generate_ast_structure(code_str)

    # Generate embedding from code description
    description = f"Python code with AST: {ast_structure[:100]}..."
    embedding = EMBEDDING_MODEL.encode(description).tolist()

    # Prepare metadata
    if metadata is None:
        metadata = {}

    metadata.update({
        "created_at": datetime.utcnow().isoformat(),
        "code_length": len(code_str),
        "ast_valid": "error" not in ast_structure
    })

    # Create UnifiedSemanticElement
    entry = UnifiedSemanticElement(
        code_snippet=code_str,
        ast_structure=ast_structure,
        embedding=embedding,
        metadata=metadata
    )

    logger.debug(f"Generated CanonEntry: {entry.id}")
    return entry


def backfill_qdrant(
    source_dir: str = "./data/code_samples",
    file_pattern: str = "*.py",
    db_manager: Optional[HybridDatabaseManager] = None
) -> int:
    """
    Backfill Qdrant with historical code data.

    Reads code files, converts to CanonEntry, pushes to Qdrant.

    Args:
        source_dir: Directory containing code files
        file_pattern: Pattern to match files
        db_manager: Database manager instance

    Returns:
        Number of entries processed
    """
    if db_manager is None:
        db_manager = HybridDatabaseManager()

    source_path = Path(source_dir)
    if not source_path.exists():
        source_path.mkdir(parents=True, exist_ok=True)
        logger.warning(f"Created source directory: {source_dir}")

    # Find all Python files
    code_files = list(source_path.glob(file_pattern))
    if not code_files:
        logger.warning(
            f"No files found matching {file_pattern} in {source_dir}")
        return 0

    logger.info(f"Found {len(code_files)} files to backfill")

    entries = []
    for file_path in code_files:
        try:
            # Read code
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Generate entry
            metadata = {
                "source_file": str(file_path),
                "file_size": len(code),
                "project_context": "historical",
                "canon_rule_id": "backfill"
            }

            entry = generate_entry(code, metadata)
            entries.append(entry)

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

    # Upsert to Qdrant in batches
    if entries:
        success = db_manager.qdrant.upsert(entries)
        if success:
            logger.info(f"Backfilled {len(entries)} entries to Qdrant")
        else:
            logger.error("Failed to backfill entries to Qdrant")

    return len(entries)


def hydrate_redis(
    db_manager: Optional[HybridDatabaseManager] = None,
    success_threshold: int = 10,
    max_patterns: int = 50
) -> int:
    """
    Hydrate Redis with top golden patterns from Qdrant.

    Queries Qdrant for successful patterns and loads them into Redis
    to prime the L1 cache.

    Args:
        db_manager: Database manager instance
        success_threshold: Minimum success count for golden patterns
        max_patterns: Maximum number of patterns to load

    Returns:
        Number of patterns loaded into Redis
    """
    if db_manager is None:
        db_manager = HybridDatabaseManager()

    logger.info(
        f"Fetching top {max_patterns} golden patterns (success > {success_threshold})")

    # Get trending patterns from Qdrant
    trending = db_manager.qdrant.get_trending_patterns(
        days=365,  # Last year
        min_success_count=success_threshold,
        project_tag=None
    )

    # Limit to max_patterns
    golden_patterns = trending[:max_patterns]

    # Load into Redis
    loaded_count = 0
    for entry in golden_patterns:
        try:
            # Mark as golden pattern
            entry.metadata["is_golden_pattern"] = True
            entry.metadata["loaded_into_redis"] = datetime.utcnow().isoformat()

            # Store in Redis
            db_manager.redis.store_entry(entry)
            loaded_count += 1

        except Exception as e:
            logger.error(f"Failed to load pattern {entry.id} into Redis: {e}")

    logger.info(f"Hydrated Redis with {loaded_count} golden patterns")
    return loaded_count


def create_sample_data(output_dir: str = "./data/code_samples") -> int:
    """
    Create sample code files for testing.

    Args:
        output_dir: Directory to create sample files

    Returns:
        Number of files created
    """
    samples = {
        "good_function.py": '''
def calculate_factorial(n):
    """Calculate factorial of a number."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1)
''',
        "good_class.py": '''
class DataProcessor:
    """Process data with validation."""

    def __init__(self, data):
        self.data = data
        self.processed = False

    def process(self):
        """Process the data."""
        if not self.data:
            raise ValueError("No data to process")
        self.processed = True
        return self.data
''',
        "error_pattern.py": '''
def broken_function():
    # This will cause an error
    return undefined_variable
''',
        "async_function.py": '''
import asyncio

async def fetch_data(url):
    """Fetch data from URL asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
'''
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for filename, content in samples.items():
        file_path = output_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())

    logger.info(f"Created {len(samples)} sample files in {output_dir}")
    return len(samples)


def run_etl_pipeline(
    source_dir: str = "./data/code_samples",
    create_samples: bool = True,
    backfill: bool = True,
    hydrate: bool = True
) -> Dict[str, int]:
    """
    Run the complete ETL pipeline.

    Args:
        source_dir: Source directory for code files
        create_samples: Whether to create sample data
        backfill: Whether to backfill Qdrant
        hydrate: Whether to hydrate Redis

    Returns:
        Dictionary with operation counts
    """
    results = {
        "samples_created": 0,
        "entries_backfilled": 0,
        "patterns_hydrated": 0
    }

    # Initialize database manager
    db_manager = HybridDatabaseManager()

    # Create sample data
    if create_samples:
        results["samples_created"] = create_sample_data(source_dir)

    # Backfill Qdrant
    if backfill:
        results["entries_backfilled"] = backfill_qdrant(
            source_dir, db_manager=db_manager)

    # Hydrate Redis
    if hydrate:
        results["patterns_hydrated"] = hydrate_redis(db_manager)

    logger.info(f"ETL Pipeline complete: {results}")
    return results


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run pipeline
    run_etl_pipeline()

