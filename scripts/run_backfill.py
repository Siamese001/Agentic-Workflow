#!/usr/bin/env python3
"""
CLI Script for L5 Meta-Learning Backfill Pipeline

Usage:
    python scripts/run_backfill.py --config config/backfill.yaml
    python scripts/run_backfill.py --git-repo /path/to/repo --local-path /path/to/code
"""

import argparse
import asyncio
import json
import logging
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.etl_pipeline import BackfillPipeline, ContinuousIngester
from core.semantic_gatekeeper import get_gatekeeper
from core.qdrant_cache import QdrantCache


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('backfill.log')
        ]
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file."""
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, 'r') as f:
        if path.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif path.suffix.lower() == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")


def create_sources_from_args(args) -> Dict[str, Any]:
    """Create sources configuration from CLI arguments."""
    sources = {}
    
    if args.git_repo:
        sources["git_repos"] = [{
            "path": args.git_repo,
            "branch": args.git_branch or "main"
        }]
    
    if args.local_path:
        sources["local_paths"] = [{
            "path": args.local_path
        }]
    
    if args.s3_bucket:
        sources["s3_buckets"] = [{
            "bucket": args.s3_bucket,
            "prefix": args.s3_prefix or ""
        }]
    
    return sources


async def run_backfill(sources: Dict[str, Any], config: Dict[str, Any]):
    """Run the backfill pipeline."""
    logger = logging.getLogger(__name__)
    
    # Initialize components
    logger.info("Initializing components...")
    gatekeeper = get_gatekeeper()
    qdrant_cache = QdrantCache(
        host=config.get("qdrant_host", "localhost"),
        port=config.get("qdrant_port", 6333),
        index_name=config.get("qdrant_index", "canon-l2")
    )
    
    # Create and run pipeline
    pipeline = BackfillPipeline(gatekeeper, qdrant_cache, sources)
    
    logger.info("Starting backfill pipeline...")
    stats = await pipeline.run()
    
    # Print results
    print("\n" + "="*50)
    print("BACKFILL COMPLETE")
    print("="*50)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Chunks created: {stats['chunks_created']}")
    print(f"Vectors loaded: {stats['vectors_loaded']}")
    print(f"Errors: {stats['errors']}")
    print(f"Duration: {stats['duration_seconds']:.2f} seconds")
    print(f"Throughput: {stats['chunks_per_second']:.2f} chunks/second")
    print("="*50)
    
    return stats


async def run_continuous_ingestion(config: Dict[str, Any]):
    """Run the continuous ingestion service."""
    logger = logging.getLogger(__name__)
    
    # Initialize components
    gatekeeper = get_gatekeeper()
    qdrant_cache = QdrantCache(
        host=config.get("qdrant_host", "localhost"),
        port=config.get("qdrant_port", 6333),
        index_name=config.get("qdrant_index", "canon-l2")
    )
    
    # Create ingester
    ingester = ContinuousIngester(
        gatekeeper,
        qdrant_cache,
        failure_retention_days=config.get("failure_retention_days", 90)
    )
    
    logger.info("Starting continuous ingestion service...")
    
    # Run cleanup periodically
    while True:
        try:
            await asyncio.sleep(86400)  # Daily cleanup
            await ingester.cleanup_expired_failures()
            stats = ingester.get_stats()
            logger.info(f"Ingestion stats: {stats}")
        except KeyboardInterrupt:
            logger.info("Stopping continuous ingestion...")
            break
        except Exception as e:
            logger.error(f"Error in continuous ingestion: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="L5 Meta-Learning ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with config file
  python scripts/run_backfill.py --config config/backfill.yaml
  
  # Run backfill from Git repo
  python scripts/run_backfill.py --git-repo /path/to/repo --mode backfill
  
  # Run continuous ingestion
  python scripts/run_backfill.py --mode continuous
        """
    )
    
    # Mode
    parser.add_argument(
        "--mode",
        choices=["backfill", "continuous"],
        required=True,
        help="Pipeline mode to run"
    )
    
    # Config
    parser.add_argument(
        "--config",
        type=str,
        help="Configuration file path (YAML or JSON)"
    )
    
    # Backfill sources
    parser.add_argument(
        "--git-repo",
        type=str,
        help="Git repository path to backfill"
    )
    parser.add_argument(
        "--git-branch",
        type=str,
        help="Git branch to use (default: main)"
    )
    parser.add_argument(
        "--local-path",
        type=str,
        help="Local path to backfill"
    )
    parser.add_argument(
        "--s3-bucket",
        type=str,
        help="S3 bucket to backfill"
    )
    parser.add_argument(
        "--s3-prefix",
        type=str,
        help="S3 prefix to filter objects"
    )
    
    # Options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually running"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    if args.config:
        config = load_config(args.config)
    else:
        config = {}
    
    # Override config with CLI args
    if "qdrant" not in config:
        config["qdrant"] = {}
    config["qdrant"]["host"] = config.get("qdrant_host", "localhost")
    config["qdrant"]["port"] = config.get("qdrant_port", 6333)
    config["qdrant"]["index_name"] = config.get("qdrant_index", "canon-l2")
    
    # Run pipeline
    try:
        if args.mode == "backfill":
            # Get sources
            if args.config and "sources" in config:
                sources = config["sources"]
            else:
                sources = create_sources_from_args(args)
            
            if not sources:
                logger.error("No sources specified. Use --config or source arguments.")
                sys.exit(1)
            
            if args.dry_run:
                logger.info(f"DRY RUN: Would process sources: {sources}")
            else:
                stats = asyncio.run(run_backfill(sources, config))
                
                # Save stats
                stats_file = Path("backfill_stats.json")
                with open(stats_file, 'w') as f:
                    json.dump(stats, f, indent=2)
                logger.info(f"Stats saved to {stats_file}")
        
        elif args.mode == "continuous":
            if args.dry_run:
                logger.info("DRY RUN: Would start continuous ingestion service")
            else:
                asyncio.run(run_continuous_ingestion(config))
    
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
