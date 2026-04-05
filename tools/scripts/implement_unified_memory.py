#!/usr/bin/env python3
"""
Unified Memory Implementation for Agentic System
Phase 1: Critical Learning Components Persistence
"""

import json
import logging
import pickle
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MEMORY_DB_PATH = ROOT / "artifacts" / "memory" / "unified_memory.db"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelCheckpoint:
    """Model checkpoint data structure."""
    model_name: str
    version: str
    model_type: str
    weights: dict[str, Any]
    metadata: dict[str, Any]
    performance_metrics: dict[str, float]
    created_at: datetime

@dataclass
class EmbeddingVector:
    """Embedding vector data structure."""
    entity_id: str
    entity_type: str
    vector: list[float]
    model_version: str
    dimension: int
    created_at: datetime

@dataclass
class TrainingSession:
    """Training session data structure."""
    session_id: str
    model_id: int
    status: str
    current_epoch: int
    loss_history: list[float]
    hyperparameters: dict[str, Any]
    start_time: datetime
    end_time: datetime | None
    created_at: datetime

@dataclass
class LearningExperience:
    """Learning experience data structure."""
    experience_type: str
    input_context: dict[str, Any]
    outcome_result: dict[str, Any]
    lesson_learned: str
    confidence_score: float
    created_at: datetime
    metadata: dict[str, Any]

class UnifiedMemoryManager:
    """Centralized persistent memory manager for agentic system learning."""

    def __init__(self, db_path: Path = MEMORY_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._lock = threading.Lock()
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the unified memory database with schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")

        # Create schema
        self._create_schema()

        logger.info(f"Unified memory database initialized: {self.db_path}")

    def _create_schema(self):
        """Create database schema for learning components."""

        # Learning Models and Checkpoints
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                version TEXT NOT NULL,
                model_type TEXT NOT NULL,
                weights BLOB,
                metadata JSON,
                performance_metrics JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(model_name, version)
            )
        """)

        # Training Sessions
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                model_id INTEGER REFERENCES learning_models(id),
                status TEXT CHECK (status IN ('running', 'completed', 'failed', 'paused')),
                current_epoch INTEGER DEFAULT 0,
                loss_history JSON,
                hyperparameters JSON,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Embeddings and Vectors
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                vector BLOB,
                model_version TEXT,
                dimension INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(entity_id, entity_type, model_version)
            )
        """)

        # Knowledge Graphs
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_graphs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                graph_name TEXT NOT NULL,
                graph_type TEXT NOT NULL,
                nodes BLOB,
                edges BLOB,
                metadata JSON,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Application State
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS application_state (
                state_key TEXT PRIMARY KEY,
                state_value BLOB,
                state_type TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Learning Experiences
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experience_type TEXT NOT NULL,
                input_context BLOB,
                outcome_result BLOB,
                lesson_learned TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON
            )
        """)

        # System Learning Configuration
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_config (
                config_key TEXT PRIMARY KEY,
                config_value BLOB,
                config_type TEXT,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Performance Metrics
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                context JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                component TEXT
            )
        """)

        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_learning_models_name ON learning_models(model_name)",
            "CREATE INDEX IF NOT EXISTS idx_training_sessions_model ON training_sessions(model_id)",
            "CREATE INDEX IF NOT EXISTS idx_embeddings_entity ON embeddings(entity_id, entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_graphs_name ON knowledge_graphs(graph_name)",
            "CREATE INDEX IF NOT EXISTS idx_learning_experiences_type ON learning_experiences(experience_type)",
            "CREATE INDEX IF NOT EXISTS idx_learning_experiences_timestamp ON learning_experiences(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_application_state_expires ON application_state(expires_at)"
        ]

        for index_sql in indexes:
            self.conn.execute(index_sql)

        # Create triggers for automatic updates
        triggers = [
            # Update timestamps
            "CREATE TRIGGER IF NOT EXISTS update_learning_models_timestamp AFTER UPDATE ON learning_models BEGIN UPDATE learning_models SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END",
            "CREATE TRIGGER IF NOT EXISTS update_knowledge_graphs_timestamp AFTER UPDATE ON knowledge_graphs BEGIN UPDATE knowledge_graphs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END",
            "CREATE TRIGGER IF NOT EXISTS update_application_state_timestamp AFTER UPDATE ON application_state BEGIN UPDATE application_state SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END",
            "CREATE TRIGGER IF NOT EXISTS update_learning_config_timestamp AFTER UPDATE ON learning_config BEGIN UPDATE learning_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END"
        ]

        for trigger_sql in triggers:
            self.conn.execute(trigger_sql)

        self.conn.commit()
        logger.info("Database schema created successfully")

    def store_model_checkpoint(self, checkpoint: ModelCheckpoint) -> int:
        """Store a model checkpoint in persistent memory."""
        with self._lock:
            try:
                # Serialize weights and metadata
                weights_blob = pickle.dumps(checkpoint.weights)
                metadata_json = json.dumps(checkpoint.metadata)
                metrics_json = json.dumps(checkpoint.performance_metrics)

                cursor = self.conn.execute("""
                    INSERT OR REPLACE INTO learning_models
                    (model_name, version, model_type, weights, metadata, performance_metrics)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    checkpoint.model_name,
                    checkpoint.version,
                    checkpoint.model_type,
                    weights_blob,
                    metadata_json,
                    metrics_json
                ))

                model_id = cursor.lastrowid
                self.conn.commit()

                logger.info(f"Stored model checkpoint: {checkpoint.model_name} v{checkpoint.version}")
                return model_id

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Failed to store model checkpoint: {e}")
                raise

    def load_model_checkpoint(self, model_name: str, version: str = "latest") -> ModelCheckpoint | None:
        """Load a model checkpoint from persistent memory."""
        try:
            if version == "latest":
                cursor = self.conn.execute("""
                    SELECT * FROM learning_models
                    WHERE model_name = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (model_name,))
            else:
                cursor = self.conn.execute("""
                    SELECT * FROM learning_models
                    WHERE model_name = ? AND version = ?
                """, (model_name, version))

            row = cursor.fetchone()
            if not row:
                logger.warning(f"Model checkpoint not found: {model_name} v{version}")
                return None

            # Deserialize data
            weights = pickle.loads(row['weights'])
            metadata = json.loads(row['metadata'])
            performance_metrics = json.loads(row['performance_metrics'])

            checkpoint = ModelCheckpoint(
                model_name=row['model_name'],
                version=row['version'],
                model_type=row['model_type'],
                weights=weights,
                metadata=metadata,
                performance_metrics=performance_metrics,
                created_at=datetime.fromisoformat(row['created_at'])
            )

            logger.info(f"Loaded model checkpoint: {model_name} v{version}")
            return checkpoint

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to load model checkpoint: {e}")
            return None

    def store_embedding(self, embedding: EmbeddingVector) -> int:
        """Store an embedding vector in persistent memory."""
        try:
            # Serialize vector
            vector_blob = pickle.dumps(embedding.vector)

            cursor = self.conn.execute("""
                INSERT OR REPLACE INTO embeddings
                (entity_id, entity_type, vector, model_version, dimension)
                VALUES (?, ?, ?, ?, ?)
            """, (
                embedding.entity_id,
                embedding.entity_type,
                vector_blob,
                embedding.model_version,
                embedding.dimension
            ))

            embedding_id = cursor.lastrowid
            self.conn.commit()

            logger.info(f"Stored embedding: {embedding.entity_id} ({embedding.entity_type})")
            return embedding_id

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to store embedding: {e}")
            raise

    def load_embedding(self, entity_id: str, entity_type: str, model_version: str = "latest") -> EmbeddingVector | None:
        """Load an embedding vector from persistent memory."""
        try:
            cursor = self.conn.execute("""
                SELECT * FROM embeddings
                WHERE entity_id = ? AND entity_type = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (entity_id, entity_type))

            row = cursor.fetchone()
            if not row:
                logger.warning(f"Embedding not found: {entity_id} ({entity_type})")
                return None

            # Deserialize vector
            vector = pickle.loads(row['vector'])

            embedding = EmbeddingVector(
                entity_id=row['entity_id'],
                entity_type=row['entity_type'],
                vector=vector,
                model_version=row['model_version'],
                dimension=row['dimension'],
                created_at=datetime.fromisoformat(row['created_at'])
            )

            logger.info(f"Loaded embedding: {entity_id} ({entity_type})")
            return embedding

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to load embedding: {e}")
            return None

    def create_training_session(self, session: TrainingSession) -> int:
        """Create a new training session."""
        try:
            loss_history_json = json.dumps(session.loss_history)
            hyperparameters_json = json.dumps(session.hyperparameters)

            cursor = self.conn.execute("""
                INSERT INTO training_sessions
                (session_id, model_id, status, current_epoch, loss_history, hyperparameters, start_time, end_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.model_id,
                session.status,
                session.current_epoch,
                loss_history_json,
                hyperparameters_json,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else None
            ))

            session_id = cursor.lastrowid
            self.conn.commit()

            logger.info(f"Created training session: {session.session_id}")
            return session_id

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to create training session: {e}")
            raise

    def update_training_session(self, session_id: str, updates: dict[str, Any]) -> bool:
        """Update a training session."""
        try:
            set_clauses = []
            values = []

            for key, value in updates.items():
                if key in ['status', 'current_epoch']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                elif key == 'loss_history':
                    set_clauses.append("loss_history = ?")
                    values.append(json.dumps(value))
                elif key == 'end_time':
                    set_clauses.append("end_time = ?")
                    values.append(value.isoformat() if value else None)

            if not set_clauses:
                return False

            values.append(session_id)

            self.conn.execute(f"""
                UPDATE training_sessions
                SET {', '.join(set_clauses)}
                WHERE session_id = ?
            """, values)

            self.conn.commit()
            logger.info(f"Updated training session: {session_id}")
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to update training session: {e}")
            return False

    def store_learning_experience(self, experience: LearningExperience) -> int:
        """Store a learning experience for continuous improvement."""
        try:
            input_context_blob = pickle.dumps(experience.input_context)
            outcome_result_blob = pickle.dumps(experience.outcome_result)
            metadata_json = json.dumps(experience.metadata)

            cursor = self.conn.execute("""
                INSERT INTO learning_experiences
                (experience_type, input_context, outcome_result, lesson_learned, confidence_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                experience.experience_type,
                input_context_blob,
                outcome_result_blob,
                experience.lesson_learned,
                experience.confidence_score,
                metadata_json
            ))

            experience_id = cursor.lastrowid
            self.conn.commit()

            logger.info(f"Stored learning experience: {experience.experience_type}")
            return experience_id

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to store learning experience: {e}")
            raise

    def get_learning_experiences(self, experience_type: str = None, limit: int = 100) -> list[LearningExperience]:
        """Retrieve learning experiences for analysis."""
        try:
            if experience_type:
                cursor = self.conn.execute("""
                    SELECT * FROM learning_experiences
                    WHERE experience_type = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (experience_type, limit))
            else:
                cursor = self.conn.execute("""
                    SELECT * FROM learning_experiences
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

            experiences = []
            for row in cursor.fetchall():
                input_context = pickle.loads(row['input_context'])
                outcome_result = pickle.loads(row['outcome_result'])
                metadata = json.loads(row['metadata'])

                experience = LearningExperience(
                    experience_type=row['experience_type'],
                    input_context=input_context,
                    outcome_result=outcome_result,
                    lesson_learned=row['lesson_learned'],
                    confidence_score=row['confidence_score'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    metadata=metadata
                )
                experiences.append(experience)

            logger.info(f"Retrieved {len(experiences)} learning experiences")
            return experiences

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to get learning experiences: {e}")
            return []

    def store_application_state(self, key: str, value: Any, state_type: str = "json", expires_at: datetime = None) -> bool:
        """Store application state persistently."""
        try:
            # Serialize value
            if state_type == "json":
                state_blob = json.dumps(value).encode()
            elif state_type == "pickle":
                state_blob = pickle.dumps(value)
            else:
                state_blob = str(value).encode()

            expires_at_str = expires_at.isoformat() if expires_at else None

            self.conn.execute("""
                INSERT OR REPLACE INTO application_state
                (state_key, state_value, state_type, expires_at)
                VALUES (?, ?, ?, ?)
            """, (key, state_blob, state_type, expires_at_str))

            self.conn.commit()
            logger.info(f"Stored application state: {key}")
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to store application state: {e}")
            return False

    def load_application_state(self, key: str) -> Any | None:
        """Load application state from persistent storage."""
        try:
            cursor = self.conn.execute("""
                SELECT * FROM application_state
                WHERE state_key = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            """, (key,))

            row = cursor.fetchone()
            if not row:
                logger.warning(f"Application state not found: {key}")
                return None

            # Deserialize based on type
            state_blob = row['state_value']
            state_type = row['state_type']

            if state_type == "json":
                return json.loads(state_blob.decode())
            elif state_type == "pickle":
                return pickle.loads(state_blob)
            else:
                return state_blob.decode()

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to load application state: {e}")
            return None

    def store_performance_metric(self, name: str, value: float, unit: str = None, context: dict = None, component: str = None) -> int:
        """Store a performance metric."""
        try:
            context_json = json.dumps(context) if context else None

            cursor = self.conn.execute("""
                INSERT INTO performance_metrics
                (metric_name, metric_value, metric_unit, context, component)
                VALUES (?, ?, ?, ?, ?)
            """, (name, value, unit, context_json, component))

            metric_id = cursor.lastrowid
            self.conn.commit()

            logger.info(f"Stored performance metric: {name} = {value} {unit or ''}")
            return metric_id

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to store performance metric: {e}")
            raise

    def get_performance_metrics(self, name: str = None, component: str = None, limit: int = 1000) -> list[dict]:
        """Get performance metrics for analysis."""
        try:
            query = "SELECT * FROM performance_metrics WHERE 1=1"
            params = []

            if name:
                query += " AND metric_name = ?"
                params.append(name)

            if component:
                query += " AND component = ?"
                params.append(component)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = self.conn.execute(query, params)

            metrics = []
            for row in cursor.fetchall():
                context = json.loads(row['context']) if row['context'] else None
                metric = {
                    'id': row['id'],
                    'name': row['metric_name'],
                    'value': row['metric_value'],
                    'unit': row['metric_unit'],
                    'context': context,
                    'component': row['component'],
                    'timestamp': row['timestamp']
                }
                metrics.append(metric)

            logger.info(f"Retrieved {len(metrics)} performance metrics")
            return metrics

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return []

    def get_database_stats(self) -> dict[str, Any]:
        """Get database statistics for monitoring."""
        try:
            stats = {}

            # Table counts
            tables = ['learning_models', 'training_sessions', 'embeddings', 'knowledge_graphs',
                     'application_state', 'learning_experiences', 'learning_config', 'performance_metrics']

            for table in tables:
                cursor = self.conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()['count']

            # Database size
            stats['database_size_mb'] = self.db_path.stat().st_size / 1024 / 1024

            # Latest timestamps (skip tables that might not have created_at)
            timestamp_tables = ['learning_models', 'training_sessions', 'embeddings', 'knowledge_graphs',
                              'learning_experiences', 'learning_config', 'performance_metrics']
            for table in timestamp_tables:
                try:
                    cursor = self.conn.execute(f"SELECT MAX(created_at) as latest FROM {table}")
                    latest = cursor.fetchone()['latest']
                    stats[f"{table}_latest"] = latest
                except (ValueError, TypeError, RuntimeError) as e:
                    # Skip tables without created_at column
                    continue

            return stats

        except (ValueError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


def main():
    """Demonstrate unified memory manager usage."""
    print("=" * 80)
    print("UNIFIED MEMORY MANAGER DEMONSTRATION")
    print("=" * 80)

    # Initialize memory manager
    memory_manager = UnifiedMemoryManager()

    # Example 1: Store and load model checkpoint
    print("\n🧠 MODEL CHECKPOINT STORAGE")
    checkpoint = ModelCheckpoint(
        model_name="meta_learning_adapter",
        version="1.0.0",
        model_type="neural_network",
        weights={"layer1": [0.1, 0.2, 0.3], "layer2": [0.4, 0.5, 0.6]},
        metadata={"framework": "pytorch", "optimizer": "adam"},
        performance_metrics={"accuracy": 0.95, "loss": 0.05},
        created_at=datetime.now()
    )

    model_id = memory_manager.store_model_checkpoint(checkpoint)
    print(f"✅ Stored model checkpoint with ID: {model_id}")

    loaded_checkpoint = memory_manager.load_model_checkpoint("meta_learning_adapter")
    if loaded_checkpoint:
        print(f"✅ Loaded model: {loaded_checkpoint.model_name} v{loaded_checkpoint.version}")

    # Example 2: Store and load embedding
    print("\n🔤 EMBEDDING STORAGE")
    embedding = EmbeddingVector(
        entity_id="user_session_123",
        entity_type="session",
        vector=[0.1, 0.2, 0.3, 0.4, 0.5],
        model_version="embedding_v2",
        dimension=5,
        created_at=datetime.now()
    )

    embedding_id = memory_manager.store_embedding(embedding)
    print(f"✅ Stored embedding with ID: {embedding_id}")

    loaded_embedding = memory_manager.load_embedding("user_session_123", "session")
    if loaded_embedding:
        print(f"✅ Loaded embedding: {loaded_embedding.entity_id} (dim={loaded_embedding.dimension})")

    # Example 3: Store learning experience
    print("\n📚 LEARNING EXPERIENCE")
    experience = LearningExperience(
        experience_type="user_feedback",
        input_context={"query": "help with debugging", "user_id": "user123"},
        outcome_result={"response": "debugging assistance provided", "satisfaction": 4.5},
        lesson_learned="Users prefer step-by-step debugging guidance",
        confidence_score=0.85,
        created_at=datetime.now(),
        metadata={"session_id": "sess_123", "response_time_ms": 150}
    )

    experience_id = memory_manager.store_learning_experience(experience)
    print(f"✅ Stored learning experience with ID: {experience_id}")

    # Example 4: Application state
    print("\n💾 APPLICATION STATE")
    state_data = {
        "active_models": ["meta_learning_adapter", "confidence_engine"],
        "current_config": {"learning_rate": 0.001, "batch_size": 32},
        "user_preferences": {"theme": "dark", "verbosity": "high"}
    }

    memory_manager.store_application_state("system_config", state_data, "json")
    loaded_state = memory_manager.load_application_state("system_config")
    if loaded_state:
        print(f"✅ Loaded application state: {list(loaded_state.keys())}")

    # Example 5: Performance metrics
    print("\n📊 PERFORMANCE METRICS")
    memory_manager.store_performance_metric("training_accuracy", 0.92, "%", {"epoch": 10}, "meta_learning")
    memory_manager.store_performance_metric("response_time", 120, "ms", {"endpoint": "/chat"}, "api")

    metrics = memory_manager.get_performance_metrics()
    print(f"✅ Retrieved {len(metrics)} performance metrics")

    # Database statistics
    print("\n📈 DATABASE STATISTICS")
    stats = memory_manager.get_database_stats()
    for key, value in stats.items():
        if "count" in key:
            print(f"  {key}: {value}")

    print(f"\n💾 Database size: {stats.get('database_size_mb', 0):.2f} MB")

    # Clean up
    memory_manager.close()

    print("\n🎉 UNIFIED MEMORY MANAGER DEMONSTRATION COMPLETE")
    print("The system is now ready for persistent learning capabilities!")


if __name__ == "__main__":
    main()
