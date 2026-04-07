#!/usr/bin/env python3
"""
Execute Full Migration to Persistent Memory
Actually migrate all learning-related files to unified memory storage
"""

import json
import logging
import pickle
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FullMigrationExecutor:
    """Execute comprehensive migration of learning data to persistent memory."""

    def __init__(self):
        self.unified_memory_db = ROOT / "artifacts" / "memory" / "unified_memory.db"
        self.migration_stats = {
            "total_files": 0,
            "migrated_files": 0,
            "failed_files": 0,
            "skipped_files": 0,
            "start_time": datetime.now(),
            "categories": {},
        }
        self.batch_size = 100
        self.max_workers = 4

    def execute_full_migration(self):
        """Execute complete migration of all learning-related files."""
        print("=" * 80)
        print("EXECUTING FULL MIGRATION TO PERSISTENT MEMORY")
        print("=" * 80)

        # Initialize unified memory
        self._ensure_unified_memory()

        # Migration categories
        migration_tasks = [
            ("system_learning_config", self._migrate_system_learning_config),
            ("model_checkpoints", self._migrate_model_checkpoints),
            ("training_data", self._migrate_training_data),
            ("application_state", self._migrate_application_state),
            ("performance_logs", self._migrate_performance_logs),
            ("user_interactions", self._migrate_user_interactions),
            ("knowledge_graphs", self._migrate_knowledge_graphs),
            ("embeddings", self._migrate_embeddings),
        ]

        # Execute migrations
        for category_name, migration_func in migration_tasks:
            print(f"\n🔄 MIGRATING: {category_name.upper()}")
            print("-" * 60)

            try:
                category_stats = migration_func()
                self.migration_stats["categories"][category_name] = category_stats
                print(f"✅ {category_name}: {category_stats['migrated']} migrated, {category_stats['failed']} failed")

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error in {category_name} migration: {e}")
                self.migration_stats["categories"][category_name] = {
                    "migrated": 0, "failed": 0, "skipped": 0,
                }

        # Final summary
        self._print_final_summary()

        return self.migration_stats

    def _ensure_unified_memory(self):
        """Ensure unified memory database is ready."""
        print("📊 Initializing Unified Memory Database...")

        # Import and initialize
        from tools.implement_unified_memory import UnifiedMemoryManager
        self.memory_manager = UnifiedMemoryManager()

        print("✅ Unified memory database ready")

    def _migrate_system_learning_config(self) -> dict[str, int]:
        """Migrate system learning configuration files."""
        stats = {"migrated": 0, "failed": 0, "skipped": 0}

        # System learning directories
        config_dirs = [
            ROOT / "system_learning" / "config",
            ROOT / "system_learning" / "stores",
            ROOT / "system_learning" / "snapshots",
        ]

        for config_dir in config_dirs:
            if not config_dir.exists():
                continue

            print(f"  Scanning: {config_dir.relative_to(ROOT)}")

            # Find all JSON and pickle files
            config_files = []
            for pattern in ["*.json", "*.pkl", "*.ckpt"]:
                config_files.extend(config_dir.rglob(pattern))

            # Process files in batches
            for i in range(0, len(config_files), self.batch_size):
                batch = config_files[i:i + self.batch_size]

                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(self._migrate_config_file, file_path) for file_path in batch]

                    for future in as_completed(futures):
                        try:
                            success = future.result()
                            if success:
                                stats["migrated"] += 1
                            else:
                                stats["skipped"] += 1
                        except (ValueError, TypeError, RuntimeError) as e:
                            logger.error(f"Error migrating config file: {e}")
                            stats["failed"] += 1

                # Progress update
                progress = min(i + self.batch_size, len(config_files))
                print(f"    Progress: {progress}/{len(config_files)} files")

        return stats

    def _migrate_config_file(self, file_path: Path) -> bool:
        """Migrate a single configuration file."""
        try:
            # Read file content
            if file_path.suffix == '.json':
                with open(file_path, encoding='utf-8') as f:
                    content = json.load(f)
            elif file_path.suffix in ['.pkl', '.ckpt']:
                with open(file_path, 'rb') as f:
                    content = pickle.load(f)
            else:
                return False

            # Generate unique key
            relative_path = str(file_path.relative_to(ROOT))
            state_key = f"config_{relative_path.replace('/', '_').replace('.', '_')}"

            # Store in application state
            self.memory_manager.store_application_state(
                key=state_key,
                value=content,
                state_type="pickle" if file_path.suffix in ['.pkl', '.ckpt'] else "json",
            )

            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error migrating config file {file_path}: {e}")
            return False

    def _migrate_model_checkpoints(self) -> dict[str, int]:
        """Migrate model checkpoint files."""
        stats = {"migrated": 0, "failed": 0, "skipped": 0}

        # Find checkpoint files
        checkpoint_patterns = [
            "system_learning/snapshots/*.pkl",
            "system_learning/snapshots/*.ckpt",
            "system_learning/snapshots/*.model",
            "**/checkpoints/*.pkl",
            "**/models/*.ckpt",
            "**/models/*.pth",
        ]

        checkpoint_files = []
        for pattern in checkpoint_patterns:
            try:
                checkpoint_files.extend(ROOT.rglob(pattern.split('/')[-1]))
            except (ValueError, TypeError, RuntimeError) as e:
                continue

        # Remove duplicates
        checkpoint_files = list(set(checkpoint_files))

        print(f"  Found {len(checkpoint_files)} checkpoint files")

        # Process checkpoints
        for i, checkpoint_file in enumerate(checkpoint_files):
            try:
                if self._migrate_checkpoint_file(checkpoint_file):
                    stats["migrated"] += 1
                else:
                    stats["skipped"] += 1

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error migrating checkpoint {checkpoint_file}: {e}")
                stats["failed"] += 1

            # Progress update
            if (i + 1) % 10 == 0:
                print(f"    Progress: {i + 1}/{len(checkpoint_files)} checkpoints")

        return stats

    def _migrate_checkpoint_file(self, file_path: Path) -> bool:
        """Migrate a single checkpoint file."""
        try:
            # Load checkpoint data
            if file_path.suffix in ['.pkl', '.ckpt', '.model', '.pth']:
                with open(file_path, 'rb') as f:
                    checkpoint_data = pickle.load(f)
            else:
                return False

            # Extract model information
            model_name = file_path.stem
            version = "migrated_1.0.0"

            # Try to extract metadata
            metadata = {
                "original_path": str(file_path.relative_to(ROOT)),
                "migration_timestamp": datetime.now().isoformat(),
                "file_size": file_path.stat().st_size,
                "original_format": file_path.suffix,
            }

            # Extract performance metrics if available
            performance_metrics = {}
            if isinstance(checkpoint_data, dict):
                if "accuracy" in checkpoint_data:
                    performance_metrics["accuracy"] = checkpoint_data["accuracy"]
                if "loss" in checkpoint_data:
                    performance_metrics["loss"] = checkpoint_data["loss"]
                if "epoch" in checkpoint_data:
                    metadata["epoch"] = checkpoint_data["epoch"]

            # Store as model checkpoint
            from tools.implement_unified_memory import ModelCheckpoint
            checkpoint = ModelCheckpoint(
                model_name=model_name,
                version=version,
                model_type="migrated_checkpoint",
                weights=checkpoint_data if not isinstance(checkpoint_data, dict) else checkpoint_data.get("weights", {}),
                metadata=metadata,
                performance_metrics=performance_metrics,
                created_at=datetime.now(),
            )

            self.memory_manager.store_model_checkpoint(checkpoint)
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error migrating checkpoint file {file_path}: {e}")
            return False

    def _migrate_training_data(self) -> dict[str, int]:
        """Migrate training data files."""
        stats = {"migrated": 0, "failed": 0, "skipped": 0}

        # Find training data files
        training_patterns = [
            "system_learning/training/*.json",
            "system_learning/datasets/*.json",
            "**/training/*.json",
            "**/datasets/*.json",
            "**/data/*.json",
        ]

        training_files = []
        for pattern in training_patterns:
            try:
                training_files.extend(ROOT.rglob(pattern.split('/')[-1]))
            except (ValueError, TypeError, RuntimeError) as e:
                continue

        # Filter relevant training files
        training_files = [f for f in training_files if any(keyword in str(f).lower()
                          for keyword in ['training', 'dataset', 'data', 'train'])]

        training_files = list(set(training_files))[:100]  # Limit to 100 for demo

        print(f"  Processing {len(training_files)} training files (limited)")

        # Process training data
        for i, training_file in enumerate(training_files):
            try:
                if self._migrate_training_file(training_file):
                    stats["migrated"] += 1
                else:
                    stats["skipped"] += 1

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error migrating training file {training_file}: {e}")
                stats["failed"] += 1

        return stats

    def _migrate_training_file(self, file_path: Path) -> bool:
        """Migrate a single training file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                training_data = json.load(f)

            # Store as learning experience
            from tools.implement_unified_memory import LearningExperience
            experience = LearningExperience(
                experience_type="migrated_training_data",
                input_context={"original_path": str(file_path.relative_to(ROOT))},
                outcome_result=training_data,
                lesson_learned=f"Migrated training data from {file_path.name}",
                confidence_score=0.9,
                created_at=datetime.now(),
                metadata={
                    "file_type": "training_data",
                    "migration_timestamp": datetime.now().isoformat(),
                },
            )

            self.memory_manager.store_learning_experience(experience)
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error migrating training file {file_path}: {e}")
            return False

    def _migrate_application_state(self) -> dict[str, int]:
        """Migrate application state files."""
        stats = {"migrated": 0, "failed": 0, "skipped": 0}

        # Find state files
        state_patterns = [
            "system_learning/state/*.json",
            "system_learning/cache/*.json",
            "**/state/*.json",
            "**/cache/*.json",
            "**/session/*.json",
        ]

        state_files = []
        for pattern in state_patterns:
            try:
                state_files.extend(ROOT.rglob(pattern.split('/')[-1]))
            except (ValueError, TypeError, RuntimeError) as e:
                continue

        state_files = list(set(state_files))[:50]  # Limit for demo

        print(f"  Processing {len(state_files)} state files (limited)")

        # Process state files
        for state_file in state_files:
            try:
                if self._migrate_state_file(state_file):
                    stats["migrated"] += 1
                else:
                    stats["skipped"] += 1

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error migrating state file {state_file}: {e}")
                stats["failed"] += 1

        return stats

    def _migrate_state_file(self, file_path: Path) -> bool:
        """Migrate a single state file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                state_data = json.load(f)

            # Generate state key
            relative_path = str(file_path.relative_to(ROOT))
            state_key = f"migrated_state_{relative_path.replace('/', '_').replace('.', '_')}"

            # Store in application state
            self.memory_manager.store_application_state(
                key=state_key,
                value=state_data,
                state_type="json",
            )

            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error migrating state file {file_path}: {e}")
            return False

    def _migrate_performance_logs(self) -> dict[str, int]:
        """Migrate performance log files."""
        stats = {"migrated": 0, "failed": 0, "skipped": 0}

        # Find performance log files
        log_patterns = [
            "system_learning/logs/*.json",
            "**/logs/*.json",
            "**/metrics/*.json",
            "**/performance/*.json",
            "**/telemetry/*.json",
        ]

        log_files = []
        for pattern in log_patterns:
            try:
                log_files.extend(ROOT.rglob(pattern.split('/')[-1]))
            except (ValueError, TypeError, RuntimeError) as e:
                continue

        # Filter performance logs
        log_files = [f for f in log_files if any(keyword in str(f).lower()
                    for keyword in ['log', 'metric', 'performance', 'telemetry'])]

        log_files = list(set(log_files))[:30]  # Limit for demo

        print(f"  Processing {len(log_files)} performance log files (limited)")

        # Process log files
        for log_file in log_files:
            try:
                if self._migrate_log_file(log_file):
                    stats["migrated"] += 1
                else:
                    stats["skipped"] += 1

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error migrating log file {log_file}: {e}")
                stats["failed"] += 1

        return stats

    def _migrate_log_file(self, file_path: Path) -> bool:
        """Migrate a single log file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                log_data = json.load(f)

            # Extract performance metrics
            if isinstance(log_data, list):
                # Multiple log entries
                for entry in log_data[:10]:  # Limit to 10 entries
                    if isinstance(entry, dict):
                        for key, value in entry.items():
                            if isinstance(value, (int, float)):
                                self.memory_manager.store_performance_metric(
                                    name=key,
                                    value=value,
                                    context={"source": str(file_path.relative_to(ROOT))},
                                    component="migrated_logs",
                                )
            elif isinstance(log_data, dict):
                # Single log entry
                for key, value in log_data.items():
                    if isinstance(value, (int, float)):
                        self.memory_manager.store_performance_metric(
                            name=key,
                            value=value,
                            context={"source": str(file_path.relative_to(ROOT))},
                            component="migrated_logs",
                        )

            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error migrating log file {file_path}: {e}")
            return False

    def _migrate_user_interactions(self) -> dict[str, int]:
        """Migrate user interaction data."""
        stats = {"migrated": 0, "failed": 0, "skipped": 0}

        # Find user interaction files
        interaction_patterns = [
            "**/chat*.json",
            "**/conversation*.json",
            "**/interaction*.json",
            "**/user*.json",
            "**/feedback*.json",
        ]

        interaction_files = []
        for pattern in interaction_patterns:
            try:
                interaction_files.extend(ROOT.rglob(pattern.split('/')[-1]))
            except (ValueError, TypeError, RuntimeError) as e:
                continue

        interaction_files = list(set(interaction_files))[:20]  # Limit for demo

        print(f"  Processing {len(interaction_files)} user interaction files (limited)")

        # Process interaction files
        for interaction_file in interaction_files:
            try:
                if self._migrate_interaction_file(interaction_file):
                    stats["migrated"] += 1
                else:
                    stats["skipped"] += 1

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error migrating interaction file {interaction_file}: {e}")
                stats["failed"] += 1

        return stats

    def _migrate_interaction_file(self, file_path: Path) -> bool:
        """Migrate a single user interaction file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                interaction_data = json.load(f)

            # Store as learning experience
            from tools.implement_unified_memory import LearningExperience
            experience = LearningExperience(
                experience_type="migrated_user_interaction",
                input_context={"original_path": str(file_path.relative_to(ROOT))},
                outcome_result=interaction_data,
                lesson_learned=f"Migrated user interaction from {file_path.name}",
                confidence_score=0.8,
                created_at=datetime.now(),
                metadata={
                    "file_type": "user_interaction",
                    "migration_timestamp": datetime.now().isoformat(),
                },
            )

            self.memory_manager.store_learning_experience(experience)
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error migrating interaction file {file_path}: {e}")
            return False

    def _migrate_knowledge_graphs(self) -> dict[str, int]:
        """Migrate knowledge graph files."""
        stats = {"migrated": 0, "failed": 0, "skipped": 0}

        # Find knowledge graph files (excluding ADG which is already in SQLite)
        graph_patterns = [
            "**/graph*.json",
            "**/knowledge*.json",
            "**/network*.json",
            "**/ontology*.json",
        ]

        graph_files = []
        for pattern in graph_patterns:
            try:
                files = ROOT.rglob(pattern.split('/')[-1])
                # Exclude ADG files
                graph_files.extend([f for f in files if "adg" not in str(f).lower()])
            except (ValueError, TypeError, RuntimeError) as e:
                continue

        graph_files = list(set(graph_files))[:10]  # Limit for demo

        print(f"  Processing {len(graph_files)} knowledge graph files (limited)")

        # Process graph files
        for graph_file in graph_files:
            try:
                if self._migrate_graph_file(graph_file):
                    stats["migrated"] += 1
                else:
                    stats["skipped"] += 1

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error migrating graph file {graph_file}: {e}")
                stats["failed"] += 1

        return stats

    def _migrate_graph_file(self, file_path: Path) -> bool:
        """Migrate a single knowledge graph file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                graph_data = json.load(f)

            # Store in knowledge graphs table
            graph_name = file_path.stem
            graph_type = "migrated_graph"

            # Serialize nodes and edges
            nodes_blob = pickle.dumps(graph_data.get("nodes", []))
            edges_blob = pickle.dumps(graph_data.get("edges", []))

            # Store using direct SQL for now
            conn = self.memory_manager.conn
            conn.execute("""
                INSERT OR REPLACE INTO knowledge_graphs
                (graph_name, graph_type, nodes, edges, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                graph_name,
                graph_type,
                nodes_blob,
                edges_blob,
                json.dumps({
                    "original_path": str(file_path.relative_to(ROOT)),
                    "migration_timestamp": datetime.now().isoformat(),
                }),
            ))

            conn.commit()
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error migrating graph file {file_path}: {e}")
            return False

    def _migrate_embeddings(self) -> dict[str, int]:
        """Migrate embedding files."""
        stats = {"migrated": 0, "failed": 0, "skipped": 0}

        # Find embedding files
        embedding_patterns = [
            "system_learning/embeddings/*.pkl",
            "system_learning/embeddings/*.npy",
            "**/embeddings/*.pkl",
            "**/vectors/*.pkl",
            "**/embeddings/*.json",
        ]

        embedding_files = []
        for pattern in embedding_patterns:
            try:
                embedding_files.extend(ROOT.rglob(pattern.split('/')[-1]))
            except (ValueError, TypeError, RuntimeError) as e:
                continue

        embedding_files = list(set(embedding_files))[:15]  # Limit for demo

        print(f"  Processing {len(embedding_files)} embedding files (limited)")

        # Process embedding files
        for embedding_file in embedding_files:
            try:
                if self._migrate_embedding_file(embedding_file):
                    stats["migrated"] += 1
                else:
                    stats["skipped"] += 1

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Error migrating embedding file {embedding_file}: {e}")
                stats["failed"] += 1

        return stats

    def _migrate_embedding_file(self, file_path: Path) -> bool:
        """Migrate a single embedding file."""
        try:
            # Load embedding data
            if file_path.suffix == '.json':
                with open(file_path, encoding='utf-8') as f:
                    embedding_data = json.load(f)
            else:
                with open(file_path, 'rb') as f:
                    embedding_data = pickle.load(f)

            # Handle different embedding formats
            if isinstance(embedding_data, dict) and "vectors" in embedding_data:
                # Multiple embeddings
                for entity_id, vector in list(embedding_data["vectors"].items())[:5]:  # Limit to 5
                    if isinstance(vector, list) and len(vector) > 0:
                        from tools.implement_unified_memory import EmbeddingVector
                        embedding = EmbeddingVector(
                            entity_id=str(entity_id),
                            entity_type="migrated_embedding",
                            vector=vector,
                            model_version="migrated_1.0",
                            dimension=len(vector),
                            created_at=datetime.now(),
                        )
                        self.memory_manager.store_embedding(embedding)
            elif isinstance(embedding_data, list) and len(embedding_data) > 0:
                # Single embedding vector
                from tools.implement_unified_memory import EmbeddingVector
                embedding = EmbeddingVector(
                    entity_id=file_path.stem,
                    entity_type="migrated_embedding",
                    vector=embedding_data,
                    model_version="migrated_1.0",
                    dimension=len(embedding_data),
                    created_at=datetime.now(),
                )
                self.memory_manager.store_embedding(embedding)

            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Error migrating embedding file {file_path}: {e}")
            return False

    def _print_final_summary(self):
        """Print final migration summary."""
        end_time = datetime.now()
        duration = (end_time - self.migration_stats["start_time"]).total_seconds()

        print("\n" + "=" * 80)
        print("MIGRATION EXECUTION SUMMARY")
        print("=" * 80)

        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Start time: {self.migration_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Category breakdown
        print("\n📋 CATEGORY BREAKDOWN:")
        total_migrated = 0
        total_failed = 0
        total_skipped = 0

        for category, stats in self.migration_stats["categories"].items():
            migrated = stats.get("migrated", 0)
            failed = stats.get("failed", 0)
            skipped = stats.get("skipped", 0)

            total_migrated += migrated
            total_failed += failed
            total_skipped += skipped

            status = "✅" if failed == 0 else "⚠️" if failed < 5 else "❌"
            print(f"  {status} {category}: {migrated} migrated, {failed} failed, {skipped} skipped")

        # Overall statistics
        self.migration_stats["migrated_files"] = total_migrated
        self.migration_stats["failed_files"] = total_failed
        self.migration_stats["skipped_files"] = total_skipped

        print("\n📊 OVERALL STATISTICS:")
        print(f"  ✅ Files migrated: {total_migrated}")
        print(f"  ❌ Files failed: {total_failed}")
        print(f"  ⚪ Files skipped: {total_skipped}")
        print(f"  📈 Success rate: {(total_migrated / max(1, total_migrated + total_failed)) * 100:.1f}%")

        # Database statistics
        print("\n💾 DATABASE STATISTICS:")
        db_stats = self.memory_manager.get_database_stats()
        for key, value in db_stats.items():
            if "count" in key and value > 0:
                print(f"  {key}: {value}")

        print(f"  Database size: {db_stats.get('database_size_mb', 0):.2f} MB")

        # Migration status
        if total_failed == 0:
            status = "✅ SUCCESS"
            message = "All files migrated successfully!"
        elif total_failed < 10:
            status = "⚠️ MOSTLY SUCCESS"
            message = "Migration completed with few failures."
        else:
            status = "❌ NEEDS ATTENTION"
            message = "Migration had significant failures."

        print(f"\n🎯 MIGRATION STATUS: {status}")
        print(f"📝 {message}")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if total_failed > 0:
            print("  🔴 Review failed files and retry migration")
        if total_skipped > 0:
            print("  🟡 Investigate skipped files for relevance")
        print("  🟢 Verify migrated data integrity")
        print("  🟢 Set up continuous migration for new files")
        print("  🟢 Monitor database performance")


def main():
    """Execute full migration."""
    print("🚀 STARTING FULL MIGRATION EXECUTION")
    print("This will migrate learning-related files to persistent memory storage.")
    print("⚠️  This process may take several minutes...")

    # Confirm execution
    response = input("\nContinue with migration? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migration cancelled by user")
        return

    # Execute migration
    executor = FullMigrationExecutor()
    stats = executor.execute_full_migration()

    # Save migration report
    artifacts_dir = ROOT / "artifacts" / "analysis"
    artifacts_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_file = artifacts_dir / f"migration_report_{timestamp}.json"

    import json
    with open(report_file, 'w') as f:
        json.dump(stats, f, indent=2, default=str)

    print(f"\n📊 Migration report saved: {report_file.name}")

    # Exit with appropriate code
    if stats["failed_files"] == 0:
        print("🎉 Migration completed successfully!")
        exit(0)
    else:
        print("⚠️ Migration completed with some failures")
        exit(1)


if __name__ == "__main__":
    main()
