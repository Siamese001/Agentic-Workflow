#!/usr/bin/env python3
"""
Comprehensive Repository Analysis for Persistent Memory Opportunities
Identifies files and data that should be stored in persistent memory to unlock system learning
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

print("=" * 100)
print("AGENTIC REPOSITORY - PERSISTENT MEMORY OPPORTUNITIES ANALYSIS")
print("=" * 100)
print(f"Repository: {ROOT}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

class PersistentMemoryAnalyzer:
    """Analyzes repository for persistent memory opportunities."""

    def __init__(self, root_path: Path):
        self.root = root_path
        self.analysis = {
            "learning_artifacts": {},
            "state_data": {},
            "configuration_data": {},
            "performance_data": {},
            "knowledge_graphs": {},
            "training_data": {},
            "user_interactions": {},
            "system_logs": {},
            "recommendations": []
        }

    def scan_repository(self) -> dict:
        """Scan entire repository for persistent memory opportunities."""
        print("\n" + "=" * 80)
        print("SCANNING REPOSITORY FOR PERSISTENT MEMORY OPPORTUNITIES")
        print("=" * 80)

        # 1. Learning artifacts
        self._scan_learning_artifacts()

        # 2. State and configuration data
        self._scan_state_data()

        # 3. Performance and metrics data
        self._scan_performance_data()

        # 4. Knowledge graphs and embeddings
        self._scan_knowledge_graphs()

        # 5. Training and model data
        self._scan_training_data()

        # 6. User interaction data
        self._scan_user_interactions()

        # 7. System logs and telemetry
        self._scan_system_logs()

        # 8. Generate recommendations
        self._generate_recommendations()

        return self.analysis

    def _scan_learning_artifacts(self):
        """Scan for learning artifacts that should be persisted."""
        print("\n🧠 SCANNING LEARNING ARTIFACTS...")

        learning_patterns = [
            r"learning_.*\.py",
            r".*_learning\.py",
            r"meta_learning.*",
            r"reinforcement.*",
            r"ml_model.*",
            r"neural.*",
            r"embedding.*",
            r"vector.*",
            r"training.*",
            r"inference.*"
        ]

        learning_dirs = [
            "system_learning",
            "models",
            "embeddings",
            "training",
            "inference",
            "ml",
            "ai"
        ]

        learning_files = []

        # Scan for learning-related files
        for pattern in learning_patterns:
            for file_path in self.root.rglob(pattern):
                if file_path.is_file() and not self._is_ignored(file_path):
                    learning_files.append(file_path)

        # Scan learning directories
        for dir_name in learning_dirs:
            dir_path = self.root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file() and not self._is_ignored(file_path):
                        learning_files.append(file_path)

        # Analyze learning files
        for file_path in learning_files[:20]:  # Limit to first 20 for analysis
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                # Look for learning-related patterns
                learning_indicators = {
                    "has_model_save": "save" in content and ("model" in content or "checkpoint" in content),
                    "has_training_loop": "train" in content or "fit" in content or "epoch" in content,
                    "has_embeddings": "embedding" in content or "vector" in content,
                    "has_weights": "weight" in content or "parameter" in content,
                    "has_metrics": "metric" in content or "accuracy" in content or "loss" in content,
                    "file_size_kb": file_path.stat().st_size / 1024
                }

                self.analysis["learning_artifacts"][str(file_path.relative_to(self.root))] = learning_indicators
            except (ValueError, TypeError, RuntimeError):
                continue

        print(f"  Found {len(learning_files)} learning-related files")
        print(f"  Analyzed {min(20, len(learning_files))} files for patterns")

    def _scan_state_data(self):
        """Scan for state and configuration data."""
        print("\n💾 SCANNING STATE & CONFIGURATION DATA...")

        state_patterns = [
            "state*.json",
            "config*.json",
            "settings*.json",
            "*.state",
            "*.config",
            "*.yaml",
            "*.yml",
            "*.toml"
        ]

        state_files = []
        for pattern in state_patterns:
            for file_path in self.root.rglob(pattern):
                if file_path.is_file() and not self._is_ignored(file_path):
                    state_files.append(file_path)

        # Look for stateful Python files
        stateful_patterns = [
            "cache",
            "session",
            "memory",
            "storage",
            "persist",
            "checkpoint"
        ]

        python_files = list(self.root.rglob("*.py"))
        for file_path in python_files[:50]:  # Limit analysis
            if self._is_ignored(file_path):
                continue

            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                # Check for stateful patterns
                stateful_score = 0
                for pattern in stateful_patterns:
                    if pattern in content.lower():
                        stateful_score += 1

                if stateful_score > 0:
                    self.analysis["state_data"][str(file_path.relative_to(self.root))] = {
                        "stateful_score": stateful_score,
                        "file_size_kb": file_path.stat().st_size / 1024,
                        "patterns_found": [p for p in stateful_patterns if p in content.lower()]
                    }

            except (ValueError, TypeError, RuntimeError):
                continue

        print(f"  Found {len(state_files)} state/configuration files")
        print(f"  Found {len(self.analysis['state_data'])} stateful Python files")

    def _scan_performance_data(self):
        """Scan for performance and metrics data."""
        print("\n📊 SCANNING PERFORMANCE & METRICS DATA...")

        performance_patterns = [
            "metrics*.json",
            "performance*.json",
            "benchmark*.json",
            "stats*.json",
            "telemetry*.json",
            "profiling*.json",
            "*.metrics",
            "*.stats",
            "*.benchmark"
        ]

        perf_files = []
        for pattern in performance_patterns:
            for file_path in self.root.rglob(pattern):
                if file_path.is_file() and not self._is_ignored(file_path):
                    perf_files.append(file_path)

        # Analyze performance files
        for file_path in perf_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                # Try to parse as JSON to analyze structure
                try:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        keys = list(data.keys())[:10]  # First 10 keys
                        self.analysis["performance_data"][str(file_path.relative_to(self.root))] = {
                            "file_size_kb": file_path.stat().st_size / 1024,
                            "data_type": type(data).__name__,
                            "sample_keys": keys,
                            "is_json": True
                        }
                    else:
                        self.analysis["performance_data"][str(file_path.relative_to(self.root))] = {
                            "file_size_kb": file_path.stat().st_size / 1024,
                            "data_type": type(data).__name__,
                            "is_json": True
                        }
                except (ValueError, TypeError, RuntimeError):
                    self.analysis["performance_data"][str(file_path.relative_to(self.root))] = {
                        "file_size_kb": file_path.stat().st_size / 1024,
                        "is_json": False
                    }

                except (ValueError, TypeError, RuntimeError):
                    continue

            except (ValueError, TypeError, RuntimeError):
                continue
        print(f"  Found {len(perf_files)} performance-related files")

    def _scan_knowledge_graphs(self):
        """Scan for knowledge graphs and embeddings."""
        print("\n🕸️ SCANNING KNOWLEDGE GRAPHS & EMBEDDINGS...")

        # Already have ADG graphs - look for others
        kg_patterns = [
            "graph*.json",
            "knowledge*.json",
            "embedding*.json",
            "vector*.json",
            "network*.json",
            "ontology*.json",
            "taxonomy*.json"
        ]

        kg_files = []
        for pattern in kg_patterns:
            for file_path in self.root.rglob(pattern):
                if file_path.is_file() and not self._is_ignored(file_path):
                    kg_files.append(file_path)

        # Exclude ADG files we already know about
        kg_files = [f for f in kg_files if "adg" not in str(f).lower()]

        for file_path in kg_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                # Analyze structure
                try:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        node_count = len(data.get("nodes", [])) if "nodes" in data else 0
                        edge_count = len(data.get("edges", [])) if "edges" in data else 0

                        self.analysis["knowledge_graphs"][str(file_path.relative_to(self.root))] = {
                            "file_size_kb": file_path.stat().st_size / 1024,
                            "has_nodes": "nodes" in data,
                            "has_edges": "edges" in data,
                            "node_count": node_count,
                            "edge_count": edge_count,
                            "is_graph": node_count > 0 or edge_count > 0
                        }
                    else:
                        self.analysis["knowledge_graphs"][str(file_path.relative_to(self.root))] = {
                            "file_size_kb": file_path.stat().st_size / 1024,
                            "is_graph": False
                        }
                except (ValueError, TypeError, RuntimeError):
                    self.analysis["knowledge_graphs"][str(file_path.relative_to(self.root))] = {
                        "file_size_kb": file_path.stat().st_size / 1024,
                        "is_graph": False,
                        "parse_error": True
                    }

                except (ValueError, TypeError, RuntimeError):
                    continue

            except (ValueError, TypeError, RuntimeError):
                continue
        print(f"  Found {len(kg_files)} knowledge graph files")

    def _scan_training_data(self):
        """Scan for training data and models."""
        print("\n🎓 SCANNING TRAINING DATA & MODELS...")

        training_patterns = [
            "train*.json",
            "model*.json",
            "dataset*.json",
            "weights*.json",
            "checkpoint*.json",
            "*.pkl",
            "*.model",
            "*.ckpt",
            "*.pth"
        ]

        training_files = []
        for pattern in training_patterns:
            for file_path in self.root.rglob(pattern):
                if file_path.is_file() and not self._is_ignored(file_path):
                    training_files.append(file_path)

        for file_path in training_files:
            try:
                if file_path.suffix == '.json':
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    try:
                        data = json.loads(content)
                        self.analysis["training_data"][str(file_path.relative_to(self.root))] = {
                            "file_size_kb": file_path.stat().st_size / 1024,
                            "data_type": "json",
                            "keys": list(data.keys())[:5] if isinstance(data, dict) else None
                        }
                    except (ValueError, TypeError, RuntimeError):
                        continue
                        self.analysis["training_data"][str(file_path.relative_to(self.root))] = {
                            "file_size_kb": file_path.stat().st_size / 1024,
                            "data_type": "json",
                            "parse_error": True
                        }
                else:
                    # Binary files
                    self.analysis["training_data"][str(file_path.relative_to(self.root))] = {
                        "file_size_kb": file_path.stat().st_size / 1024,
                        "data_type": "binary",
                        "extension": file_path.suffix
                    }


            except (ValueError, TypeError, RuntimeError):
                continue
        print(f"  Found {len(training_files)} training data files")

    def _scan_user_interactions(self):
        """Scan for user interaction data."""
        print("\n👤 SCANNING USER INTERACTION DATA...")

        interaction_patterns = [
            "user*.json",
            "chat*.json",
            "conversation*.json",
            "feedback*.json",
            "preference*.json",
            "history*.json",
            "session*.json"
        ]

        interaction_files = []
        for pattern in interaction_patterns:
            for file_path in self.root.rglob(pattern):
                if file_path.is_file() and not self._is_ignored(file_path):
                    interaction_files.append(file_path)

        for file_path in interaction_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                try:
                    data = json.loads(content)
                    self.analysis["user_interactions"][str(file_path.relative_to(self.root))] = {
                        "file_size_kb": file_path.stat().st_size / 1024,
                        "record_count": len(data) if isinstance(data, list) else 1,
                        "keys": list(data.keys())[:5] if isinstance(data, dict) else None
                    }
                except (ValueError, TypeError, RuntimeError):
                    self.analysis["user_interactions"][str(file_path.relative_to(self.root))] = {
                        "file_size_kb": file_path.stat().st_size / 1024,
                        "parse_error": True
                    }

                except (ValueError, TypeError, RuntimeError):
                    continue

            except (ValueError, TypeError, RuntimeError):
                continue
        print(f"  Found {len(interaction_files)} user interaction files")

    def _scan_system_logs(self):
        """Scan for system logs and telemetry."""
        print("\n📝 SCANNING SYSTEM LOGS & TELEMETRY...")

        log_patterns = [
            "*.log",
            "log*.json",
            "telemetry*.json",
            "trace*.json",
            "audit*.json",
            "event*.json"
        ]

        log_files = []
        for pattern in log_patterns:
            for file_path in self.root.rglob(pattern):
                if file_path.is_file() and not self._is_ignored(file_path):
                    log_files.append(file_path)

        for file_path in log_files:
            try:
                if file_path.suffix == '.json':
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    try:
                        data = json.loads(content)
                        entry_count = len(data) if isinstance(data, list) else 1
                        self.analysis["system_logs"][str(file_path.relative_to(self.root))] = {
                            "file_size_kb": file_path.stat().st_size / 1024,
                            "entry_count": entry_count,
                            "is_structured": True
                        }
                    except (ValueError, TypeError, RuntimeError):
                        self.analysis["system_logs"][str(file_path.relative_to(self.root))] = {
                            "file_size_kb": file_path.stat().st_size / 1024,
                            "is_structured": False
                        }
                else:
                    # Text logs
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    line_count = len(content.split('\n'))
                    self.analysis["system_logs"][str(file_path.relative_to(self.root))] = {
                        "file_size_kb": file_path.stat().st_size / 1024,
                        "line_count": line_count,
                        "is_structured": False
                    }


            except (ValueError, TypeError, RuntimeError):
                continue
        print(f"  Found {len(log_files)} log files")

    def _generate_recommendations(self):
        """Generate recommendations for persistent memory implementation."""
        print("\n💡 GENERATING RECOMMENDATIONS...")

        recommendations = []

        # Learning artifacts recommendations
        if self.analysis["learning_artifacts"]:
            recommendations.append({
                "category": "Learning Artifacts",
                "priority": "HIGH",
                "description": "Implement persistent storage for model checkpoints, embeddings, and training progress",
                "files_count": len(self.analysis["learning_artifacts"]),
                "implementation": "SQLite tables: models, embeddings, training_sessions, checkpoints",
                "benefits": "Resume training, model versioning, incremental learning"
            })

        # State data recommendations
        if self.analysis["state_data"]:
            recommendations.append({
                "category": "State Management",
                "priority": "HIGH",
                "description": "Centralize application state in persistent storage",
                "files_count": len(self.analysis["state_data"]),
                "implementation": "SQLite tables: application_state, user_sessions, cache_entries",
                "benefits": "State recovery, session management, cache persistence"
            })

        # Performance data recommendations
        if self.analysis["performance_data"]:
            recommendations.append({
                "category": "Performance Analytics",
                "priority": "MEDIUM",
                "description": "Store performance metrics and benchmarks for trend analysis",
                "files_count": len(self.analysis["performance_data"]),
                "implementation": "SQLite tables: metrics, benchmarks, performance_trends",
                "benefits": "Performance tracking, regression detection, optimization insights"
            })

        # Knowledge graphs recommendations
        if self.analysis["knowledge_graphs"]:
            recommendations.append({
                "category": "Knowledge Management",
                "priority": "HIGH",
                "description": "Persist knowledge graphs and embeddings for semantic search",
                "files_count": len(self.analysis["knowledge_graphs"]),
                "implementation": "SQLite tables: knowledge_graphs, embeddings, semantic_index",
                "benefits": "Knowledge retention, semantic search, relationship mining"
            })

        # Training data recommendations
        if self.analysis["training_data"]:
            recommendations.append({
                "category": "Training Data Management",
                "priority": "MEDIUM",
                "description": "Organize and persist training datasets and model versions",
                "files_count": len(self.analysis["training_data"]),
                "implementation": "SQLite tables: datasets, model_versions, training_runs",
                "benefits": "Data lineage, model versioning, experiment tracking"
            })

        # User interaction recommendations
        if self.analysis["user_interactions"]:
            recommendations.append({
                "category": "User Analytics",
                "priority": "MEDIUM",
                "description": "Store user interactions for personalization and analytics",
                "files_count": len(self.analysis["user_interactions"]),
                "implementation": "SQLite tables: user_interactions, preferences, feedback",
                "benefits": "Personalization, user insights, interaction patterns"
            })

        # System logs recommendations
        if self.analysis["system_logs"]:
            recommendations.append({
                "category": "System Observability",
                "priority": "MEDIUM",
                "description": "Consolidate logs and telemetry in structured storage",
                "files_count": len(self.analysis["system_logs"]),
                "implementation": "SQLite tables: system_logs, events, telemetry",
                "benefits": "Centralized logging, queryable logs, system insights"
            })

        # Cross-cutting recommendations
        recommendations.extend([
            {
                "category": "Unified Memory Architecture",
                "priority": "CRITICAL",
                "description": "Implement a unified persistent memory system across all components",
                "implementation": "Central SQLite database with schema for all data types",
                "benefits": "Unified access, data relationships, system-wide learning"
            },
            {
                "category": "Memory-First Architecture",
                "priority": "HIGH",
                "description": "Design system with persistent memory as primary storage",
                "implementation": "Memory-centric design patterns with SQLite as backbone",
                "benefits": "Data persistence, system resilience, learning continuity"
            },
            {
                "category": "Learning Loop Integration",
                "priority": "HIGH",
                "description": "Integrate persistent memory into continuous learning loops",
                "implementation": "Feedback systems with SQLite-stored learning data",
                "benefits": "Continuous improvement, adaptive behavior, knowledge accumulation"
            }
        ])

        self.analysis["recommendations"] = recommendations

    def _is_ignored(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            ".venv",
            "venv"
        ]

        return any(pattern in str(file_path) for pattern in ignore_patterns)

    def generate_schema_design(self) -> str:
        """Generate a comprehensive SQLite schema design."""
        schema = """
-- ============================================================================
-- UNIFIED PERSISTENT MEMORY SCHEMA FOR AGENTIC SYSTEM
-- ============================================================================

-- Learning and Model Management
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    model_type TEXT NOT NULL,
    file_path TEXT,
    parameters BLOB,  -- Serialized model parameters
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performance_metrics JSON,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS training_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER REFERENCES models(id),
    session_name TEXT NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT CHECK (status IN ('running', 'completed', 'failed', 'paused')),
    hyperparameters JSON,
    training_metrics JSON,
    final_loss REAL,
    best_checkpoint_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    embedding_vector BLOB,  -- Serialized vector
    embedding_model TEXT,
    dimension INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    UNIQUE(entity_id, entity_type, embedding_model)
);

-- Knowledge and Graph Management
CREATE TABLE IF NOT EXISTS knowledge_graphs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    graph_name TEXT NOT NULL,
    graph_type TEXT NOT NULL,
    nodes BLOB,  -- Serialized nodes
    edges BLOB,  -- Serialized edges
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS semantic_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL,
    embedding_id INTEGER REFERENCES embeddings(id),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application State Management
CREATE TABLE IF NOT EXISTS application_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_key TEXT NOT NULL UNIQUE,
    state_value BLOB,  -- Serialized state
    state_type TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    user_id TEXT,
    session_data BLOB,  -- Serialized session data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cache_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT NOT NULL UNIQUE,
    cache_value BLOB,  -- Serialized cached data
    cache_type TEXT,
    hits INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    size_bytes INTEGER
);

-- Performance and Analytics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    context JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    component TEXT
);

CREATE TABLE IF NOT EXISTS benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    benchmark_name TEXT NOT NULL,
    benchmark_type TEXT NOT NULL,
    score REAL,
    parameters JSON,
    baseline_score REAL,
    environment_info JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training Data Management
CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name TEXT NOT NULL UNIQUE,
    dataset_type TEXT NOT NULL,
    file_path TEXT,
    size_bytes INTEGER,
    sample_count INTEGER,
    feature_count INTEGER,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS training_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_name TEXT NOT NULL,
    dataset_id INTEGER REFERENCES datasets(id),
    model_id INTEGER REFERENCES models(id),
    config JSON,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT CHECK (status IN ('running', 'completed', 'failed')),
    results JSON,
    artifacts JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Interaction and Analytics
CREATE TABLE IF NOT EXISTS user_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    session_id TEXT,
    interaction_type TEXT NOT NULL,
    interaction_data BLOB,  -- Serialized interaction data
    context JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    satisfaction_score INTEGER CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value BLOB,  -- Serialized preference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

-- System Observability
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    component TEXT,
    context JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    trace_id TEXT
);

CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_data BLOB,  -- Serialized event data
    source_component TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    correlation_id TEXT,
    metadata JSON
);

-- Learning and Adaptation
CREATE TABLE IF NOT EXISTS learning_experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experience_type TEXT NOT NULL,
    input_data BLOB,  -- Serialized input
    outcome_data BLOB,  -- Serialized outcome
    lesson_learned TEXT,
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

CREATE TABLE IF NOT EXISTS adaptation_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT NOT NULL,
    condition_expression TEXT,
    action_expression TEXT,
    priority INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Learning indexes
CREATE INDEX IF NOT EXISTS idx_models_name_version ON models(name, version);
CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type);
CREATE INDEX IF NOT EXISTS idx_training_sessions_model ON training_sessions(model_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_entity ON embeddings(entity_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(embedding_model);

-- Knowledge graph indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_graphs_name ON knowledge_graphs(graph_name);
CREATE INDEX IF NOT EXISTS idx_knowledge_graphs_type ON knowledge_graphs(graph_type);
CREATE INDEX IF NOT EXISTS idx_semantic_index_content ON semantic_index(content_type);

-- State management indexes
CREATE INDEX IF NOT EXISTS idx_application_state_key ON application_state(state_key);
CREATE INDEX IF NOT EXISTS idx_user_sessions_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_cache_entries_key ON cache_entries(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_entries_expires ON cache_entries(expires_at);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_benchmarks_name ON benchmarks(benchmark_name);

-- Training data indexes
CREATE INDEX IF NOT EXISTS idx_datasets_name ON datasets(dataset_name);
CREATE INDEX IF NOT EXISTS idx_training_runs_dataset ON training_runs(dataset_id);
CREATE INDEX IF NOT EXISTS idx_training_runs_model ON training_runs(model_id);

-- User interaction indexes
CREATE INDEX IF NOT EXISTS idx_user_interactions_user ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_session ON user_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions(timestamp);

-- System observability indexes
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_component ON system_logs(component);
CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type);
CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp);

-- Learning indexes
CREATE INDEX IF NOT EXISTS idx_learning_experiences_type ON learning_experiences(experience_type);
CREATE INDEX IF NOT EXISTS idx_learning_experiences_timestamp ON learning_experiences(created_at);
CREATE INDEX IF NOT EXISTS idx_adaptation_rules_active ON adaptation_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_adaptation_rules_priority ON adaptation_rules(priority DESC);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC HOUSEKEEPING
-- ============================================================================

-- Update timestamps
CREATE TRIGGER IF NOT EXISTS update_models_timestamp
    AFTER UPDATE ON models
    BEGIN
        UPDATE models SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_knowledge_graphs_timestamp
    AFTER UPDATE ON knowledge_graphs
    BEGIN
        UPDATE knowledge_graphs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_application_state_timestamp
    AFTER UPDATE ON application_state
    BEGIN
        UPDATE application_state SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Cache hit tracking
CREATE TRIGGER IF NOT EXISTS increment_cache_hits
    AFTER SELECT ON cache_entries
    BEGIN
        UPDATE cache_entries SET hits = hits + 1, last_accessed = CURRENT_TIMESTAMP WHERE cache_key = NEW.cache_key;
    END;

-- Session expiry cleanup
CREATE TRIGGER IF NOT EXISTS cleanup_expired_sessions
    AFTER INSERT ON user_sessions
    BEGIN
        DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP;
    END;
"""
        return schema

    def print_summary(self):
        """Print analysis summary."""
        print("\n" + "=" * 80)
        print("PERSISTENT MEMORY OPPORTUNITIES SUMMARY")
        print("=" * 80)

        categories = [
            ("Learning Artifacts", "learning_artifacts"),
            ("State Data", "state_data"),
            ("Performance Data", "performance_data"),
            ("Knowledge Graphs", "knowledge_graphs"),
            ("Training Data", "training_data"),
            ("User Interactions", "user_interactions"),
            ("System Logs", "system_logs")
        ]

        for category_name, category_key in categories:
            count = len(self.analysis[category_key])
            status = "🔴" if count == 0 else "🟡" if count < 5 else "🟢"
            print(f"{status} {category_name}: {count} files")

        print(f"\n📋 RECOMMENDATIONS: {len(self.analysis['recommendations'])}")

        high_priority = [r for r in self.analysis["recommendations"] if r["priority"] in ["CRITICAL", "HIGH"]]
        print(f"🚨 HIGH PRIORITY: {len(high_priority)}")

        print("\n" + "=" * 80)
        print("TOP RECOMMENDATIONS")
        print("=" * 80)

        for i, rec in enumerate(high_priority[:5], 1):
            print(f"{i}. {rec['category']} ({rec['priority']})")
            print(f"   {rec['description']}")
            print(f"   Files: {rec.get('files_count', 'N/A')}")
            print(f"   Benefits: {rec['benefits']}")
            print()


def main():
    """Run the persistent memory analysis."""
    analyzer = PersistentMemoryAnalyzer(ROOT)
    analysis = analyzer.scan_repository()
    analyzer.print_summary()

    # Save analysis results
    results_dir = ROOT / "artifacts" / "analysis"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # Save analysis
    analysis_file = results_dir / f"persistent_memory_analysis_{timestamp}.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)

    print(f"📊 Analysis saved: {analysis_file.name}")

    # Save schema design
    schema_file = results_dir / f"unified_memory_schema_{timestamp}.sql"
    with open(schema_file, 'w') as f:
        f.write(analyzer.generate_schema_design())

    print(f"🗄️ Schema design saved: {schema_file.name}")

    print("\n🎯 NEXT STEPS:")
    print(f"1. Review the analysis results in {analysis_file.name}")
    print(f"2. Implement the unified schema from {schema_file.name}")
    print("3. Prioritize HIGH and CRITICAL recommendations")
    print("4. Design migration strategy for existing data")
    print("5. Implement incremental rollout with fallback")


if __name__ == "__main__":
    main()
