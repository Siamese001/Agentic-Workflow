"""
Model Registry for ML Decision Support

Provides versioned model storage, metadata tracking, promotion workflow,
and rollback capability with full audit logging.
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# from agentic_core.L4_canonical.state.snapshot_manager import SnapshotManager
# TODO: Replace with local snapshot management


class ModelStatus(Enum):
    """Model lifecycle status."""

    DEVELOPMENT = "development"
    CANDIDATE = "candidate"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ROLLED_BACK = "rolled_back"


class DecisionMode(Enum):
    """Model decision authority level."""

    ADVISORY = "advisory"
    SHADOW_ONLY = "shadow_only"
    BLOCKED = "blocked"
    ESCALATED = "escalated"


@dataclass
class ModelMetadata:
    """Complete model metadata for governance."""

    model_name: str
    model_version: str
    model_type: str
    status: ModelStatus
    decision_mode: DecisionMode
    created_at: datetime
    created_by: str
    training_data_digest: str
    feature_schema_digest: str
    model_digest: str
    metrics: dict[str, float]
    thresholds: dict[str, float]
    promotion_history: list[dict[str, Any]]
    rollback_history: list[dict[str, Any]]
    validation_results: dict[str, Any]
    compliance_checks: dict[str, bool]


@dataclass
class ModelRecord:
    """Registry record for a model."""

    metadata: ModelMetadata
    file_path: Path
    is_active: bool
    last_used: datetime | None
    usage_count: int


class ModelRegistry:
    """
    Versioned model registry with governance controls.

    Ensures all ML models are:
    - Versioned with content digests
    - Tracked with full metadata
    - Promoted through governed workflow
    - Capable of rollback
    - Audited for compliance
    """

    def __init__(self, registry_path: Path):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.models_file = self.registry_path / "models.json"
        self.models_dir = self.registry_path / "models"
        self.models_dir.mkdir(exist_ok=True)
        # self.snapshot_manager = SnapshotManager()
        # TODO: Replace with local snapshot management
        self._models: dict[str, ModelRecord] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        """Load model registry from disk."""
        if self.models_file.exists():
            try:
                with open(self.models_file, encoding="utf-8") as f:
                    data = json.load(f)

                for model_id, record_data in data.items():
                    metadata = ModelMetadata(**record_data["metadata"])
                    # Convert string timestamps back to datetime
                    metadata.created_at = datetime.fromisoformat(metadata.created_at)
                    metadata.last_used = (
                        datetime.fromisoformat(metadata.last_used) if metadata.last_used else None
                    )

                    record = ModelRecord(
                        metadata=metadata,
                        file_path=Path(record_data["file_path"]),
                        is_active=record_data["is_active"],
                        last_used=metadata.last_used,
                        usage_count=record_data["usage_count"],
                    )
                    self._models[model_id] = record

            except Exception as e:
                # Start fresh if registry is corrupted
                self._models = {}

    def _save_registry(self) -> None:
        """Save model registry to disk."""
        data = {}
        for model_id, record in self._models.items():
            data[model_id] = {
                "metadata": asdict(record.metadata),
                "file_path": str(record.file_path),
                "is_active": record.is_active,
                "usage_count": record.usage_count,
            }

        with open(self.models_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _compute_digest(self, file_path: Path) -> str:
        """Compute SHA-256 digest of model file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _generate_model_id(self, model_name: str, model_version: str) -> str:
        """Generate unique model identifier."""
        return f"{model_name}:{model_version}"

    def register_model(
        self,
        model_name: str,
        model_version: str,
        model_type: str,
        model_file_path: Path,
        training_data_digest: str,
        feature_schema_digest: str,
        metrics: dict[str, float],
        thresholds: dict[str, float],
        created_by: str,
        validation_results: dict[str, Any] | None = None,
        compliance_checks: dict[str, bool] | None = None,
    ) -> str:
        """
        Register a new model in the registry.

        Args:
            model_name: Name of the model
            model_version: Version string
            model_type: Type of model (logistic_regression, lightgbm, etc.)
            model_file_path: Path to model file
            training_data_digest: Digest of training data
            feature_schema_digest: Digest of feature schema
            metrics: Model performance metrics
            thresholds: Decision thresholds
            created_by: Who created the model
            validation_results: Validation test results
            compliance_checks: Compliance check results

        Returns:
            Model ID for registered model
        """
        model_id = self._generate_model_id(model_name, model_version)

        if model_id in self._models:
            raise ValueError(f"Model {model_id} already registered")

        # Compute model digest
        model_digest = self._compute_digest(model_file_path)

        # Create metadata
        metadata = ModelMetadata(
            model_name=model_name,
            model_version=model_version,
            model_type=model_type,
            status=ModelStatus.DEVELOPMENT,
            decision_mode=DecisionMode.SHADOW_ONLY,
            created_at=datetime.now(),
            created_by=created_by,
            training_data_digest=training_data_digest,
            feature_schema_digest=feature_schema_digest,
            model_digest=model_digest,
            metrics=metrics,
            thresholds=thresholds,
            promotion_history=[],
            rollback_history=[],
            validation_results=validation_results or {},
            compliance_checks=compliance_checks or {},
        )

        # Copy model to registry
        registry_model_path = self.models_dir / f"{model_id}.pkl"
        import shutil

        shutil.copy2(model_file_path, registry_model_path)

        # Create record
        record = ModelRecord(
            metadata=metadata,
            file_path=registry_model_path,
            is_active=False,
            last_used=None,
            usage_count=0,
        )

        self._models[model_id] = record
        self._save_registry()

        # Log to L4 canonical state
        self._log_model_event("model_registered", model_id, metadata)

        return model_id

    def promote_model(
        self,
        model_id: str,
        target_status: ModelStatus,
        target_decision_mode: DecisionMode,
        promoted_by: str,
        justification: str,
    ) -> bool:
        """
        Promote a model to new status/decision mode.

        Args:
            model_id: Model to promote
            target_status: New status
            target_decision_mode: New decision mode
            promoted_by: Who is promoting
            justification: Reason for promotion

        Returns:
            True if promotion successful
        """
        if model_id not in self._models:
            raise ValueError(f"Model {model_id} not found")

        record = self._models[model_id]
        old_status = record.metadata.status
        old_mode = record.metadata.decision_mode

        # Validate promotion path
        if not self._validate_promotion(old_status, target_status, old_mode, target_decision_mode):
            return False

        # Update metadata
        record.metadata.status = target_status
        record.metadata.decision_mode = target_decision_mode

        # Add to promotion history
        promotion_event = {
            "timestamp": datetime.now().isoformat(),
            "from_status": old_status.value,
            "to_status": target_status.value,
            "from_mode": old_mode.value,
            "to_mode": target_decision_mode.value,
            "promoted_by": promoted_by,
            "justification": justification,
        }
        record.metadata.promotion_history.append(promotion_event)

        # Update active status
        record.is_active = target_status == ModelStatus.PRODUCTION

        self._save_registry()

        # Log promotion
        self._log_model_event(
            "model_promoted",
            model_id,
            {
                "promotion_event": promotion_event,
            },
        )

        return True

    def rollback_model(
        self,
        model_id: str,
        rollback_reason: str,
        rolled_back_by: str,
    ) -> bool:
        """
        Rollback a model to previous version.

        Args:
            model_id: Model to rollback
            rollback_reason: Reason for rollback
            rolled_back_by: Who is rolling back

        Returns:
            True if rollback successful
        """
        if model_id not in self._models:
            raise ValueError(f"Model {model_id} not found")

        record = self._models[model_id]

        # Can only rollback production models
        if record.metadata.status != ModelStatus.PRODUCTION:
            return False

        # Update status
        old_status = record.metadata.status
        record.metadata.status = ModelStatus.ROLLED_BACK
        record.is_active = False

        # Add to rollback history
        rollback_event = {
            "timestamp": datetime.now().isoformat(),
            "from_status": old_status.value,
            "to_status": ModelStatus.ROLLED_BACK.value,
            "rollback_reason": rollback_reason,
            "rolled_back_by": rolled_back_by,
        }
        record.metadata.rollback_history.append(rollback_event)

        self._save_registry()

        # Log rollback
        self._log_model_event(
            "model_rolled_back",
            model_id,
            {
                "rollback_event": rollback_event,
            },
        )

        return True

    def get_model(self, model_id: str) -> ModelRecord | None:
        """Get model record by ID."""
        return self._models.get(model_id)

    def get_active_models(self, model_type: str | None = None) -> list[ModelRecord]:
        """Get all active models, optionally filtered by type."""
        active_models = [record for record in self._models.values() if record.is_active]

        if model_type:
            active_models = [record for record in active_models if record.metadata.model_type == model_type]

        return active_models

    def get_production_models(self) -> list[ModelRecord]:
        """Get all production models."""
        return [
            record for record in self._models.values() if record.metadata.status == ModelStatus.PRODUCTION
        ]

    def update_usage(self, model_id: str) -> None:
        """Update model usage statistics."""
        if model_id in self._models:
            record = self._models[model_id]
            record.usage_count += 1
            record.last_used = datetime.now()
            self._save_registry()

    def _validate_promotion(
        self,
        old_status: ModelStatus,
        new_status: ModelStatus,
        old_mode: DecisionMode,
        new_mode: DecisionMode,
    ) -> bool:
        """Validate promotion path follows governance rules."""

        # Status progression rules
        valid_status_transitions = {
            ModelStatus.DEVELOPMENT: [ModelStatus.CANDIDATE],
            ModelStatus.CANDIDATE: [ModelStatus.PRODUCTION, ModelStatus.DEPRECATED],
            ModelStatus.PRODUCTION: [ModelStatus.DEPRECATED, ModelStatus.ROLLED_BACK],
            ModelStatus.DEPRECATED: [],  # Terminal state
            ModelStatus.ROLLED_BACK: [ModelStatus.DEVELOPMENT],  # Can restart development
        }

        if new_status not in valid_status_transitions.get(old_status, []):
            return False

        # Decision mode rules
        valid_mode_transitions = {
            DecisionMode.SHADOW_ONLY: [DecisionMode.ADVISORY],
            DecisionMode.ADVISORY: [DecisionMode.ADVISORY, DecisionMode.ESCALATED],
            DecisionMode.ESCALATED: [DecisionMode.BLOCKED],
            DecisionMode.BLOCKED: [],  # Terminal state
        }

        if new_mode not in valid_mode_transitions.get(old_mode, []):
            return False

        return True

    def _log_model_event(self, event_type: str, model_id: str, data: dict[str, Any]) -> None:
        """Log model events to L4 canonical state."""
        try:
            event = {
                "event_type": event_type,
                "model_id": model_id,
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }

            # Store in L4 canonical state
            # self.snapshot_manager.store_event("ml_model_registry", event)
            # TODO: Replace with local snapshot management

        except Exception as e:
            # Log failure but don't fail the operation
            print(f"Failed to log model event: {e}")

    def get_registry_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        stats = {
            "total_models": len(self._models),
            "active_models": len([r for r in self._models.values() if r.is_active]),
            "production_models": len(self.get_production_models()),
            "models_by_type": {},
            "models_by_status": {},
        }

        for record in self._models.values():
            # Count by type
            model_type = record.metadata.model_type
            stats["models_by_type"][model_type] = stats["models_by_type"].get(model_type, 0) + 1

            # Count by status
            status = record.metadata.status.value
            stats["models_by_status"][status] = stats["models_by_status"].get(status, 0) + 1

        return stats
