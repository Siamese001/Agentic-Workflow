"""
Threshold Configuration for ML Decision Support

Manages versioned threshold configurations with A/B testing support,
gradual rollout control, and automated rollback triggers.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# from agentic_core.L4_canonical.state.snapshot_manager import SnapshotManager
# TODO: Replace with local snapshot management


class ThresholdType(Enum):
    """Types of thresholds."""
    CONFIDENCE = "confidence"
    PROBABILITY = "probability"
    SCORE = "score"
    RATE = "rate"
    COUNT = "count"
    PERCENTILE = "percentile"


class RollbackTrigger(Enum):
    """Automatic rollback trigger types."""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ERROR_RATE_SPIKE = "error_rate_spike"
    DRIFT_DETECTED = "drift_detected"
    FEATURE_AVAILABILITY_LOW = "feature_availability_low"
    CALIBRATION_LOSS = "calibration_loss"
    MANUAL_REQUEST = "manual_request"


@dataclass
class ThresholdDefinition:
    """Definition for a single threshold."""
    name: str
    threshold_type: ThresholdType
    description: str
    current_value: float
    min_value: float | None = None
    max_value: float | None = None
    rollout_percentage: float = 0.0  # 0-100% of traffic using this threshold
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    version: str = "1.0"
    validation_rules: dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackCondition:
    """Condition for automatic rollback."""
    trigger_type: RollbackTrigger
    threshold_value: float
    comparison_operator: str  # ">", "<", ">=", "<=", "=="
    grace_period_minutes: int = 5  # Wait period before triggering
    is_active: bool = True


@dataclass
class ThresholdConfig:
    """Complete threshold configuration for a model."""
    model_name: str
    model_version: str
    config_version: str
    description: str
    thresholds: list[ThresholdDefinition]
    rollback_conditions: list[RollbackCondition]
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    config_digest: str = ""

    def __post_init__(self):
        """Compute config digest after creation."""
        self.config_digest = self._compute_digest()

    def _compute_digest(self) -> str:
        """Compute SHA-256 digest of config."""
        config_dict = {
            'model_name': self.model_name,
            'model_version': self.model_version,
            'config_version': self.config_version,
            'thresholds': [
                {
                    'name': t.name,
                    'type': t.threshold_type.value,
                    'current_value': t.current_value,
                    'min_value': t.min_value,
                    'max_value': t.max_value,
                    'rollout_percentage': t.rollout_percentage,
                    'is_active': t.is_active,
                    'version': t.version,
                }
                for t in self.thresholds
            ],
            'rollback_conditions': [
                {
                    'trigger_type': rc.trigger_type.value,
                    'threshold_value': rc.threshold_value,
                    'comparison_operator': rc.comparison_operator,
                    'grace_period_minutes': rc.grace_period_minutes,
                    'is_active': rc.is_active,
                }
                for rc in self.rollback_conditions
            ],
        }

        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    def get_threshold(self, name: str) -> ThresholdDefinition | None:
        """Get threshold by name."""
        for threshold in self.thresholds:
            if threshold.name == name:
                return threshold
        return None

    def update_threshold(
        self,
        name: str,
        new_value: float,
        rollout_percentage: float | None = None,
    ) -> bool:
        """Update threshold value and rollout."""
        threshold = self.get_threshold(name)
        if not threshold:
            return False

        # Validate new value
        if threshold.min_value is not None and new_value < threshold.min_value:
            return False
        if threshold.max_value is not None and new_value > threshold.max_value:
            return False

        threshold.current_value = new_value
        if rollout_percentage is not None:
            threshold.rollout_percentage = max(0.0, min(100.0, rollout_percentage))

        # Recompute digest
        self.config_digest = self._compute_digest()

        return True

    def should_use_threshold(self, request_id: str) -> bool:
        """Determine if request should use new threshold based on rollout."""
        # Simple hash-based rollout for consistency
        import hashlib
        hash_value = int(hashlib.md5(request_id.encode()).hexdigest(), 16)
        rollout_threshold = int(self.get_active_rollout_percentage() * 100)

        return hash_value % 100 < rollout_threshold

    def get_active_rollout_percentage(self) -> float:
        """Get maximum rollout percentage among active thresholds."""
        active_rollouts = [
            t.rollout_percentage for t in self.thresholds
            if t.is_active
        ]
        return max(active_rollouts) if active_rollouts else 0.0


class ThresholdConfig:
    """
    Manages threshold configurations with versioning and A/B testing.

    Provides:
    - Versioned threshold storage
    - Gradual rollout control
    - Automated rollback triggers
    - Performance monitoring integration
    """

    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.configs_file = self.config_path / "threshold_configs.json"
        # self.snapshot_manager = SnapshotManager()
        # TODO: Replace with local snapshot management
        self._configs: dict[str, ThresholdConfig] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load threshold configurations from disk."""
        if self.configs_file.exists():
            try:
                with open(self.configs_file, encoding='utf-8') as f:
                    data = json.load(f)

                for config_key, config_data in data.items():
                    # Reconstruct thresholds
                    thresholds = []
                    for t_data in config_data['thresholds']:
                        threshold = ThresholdDefinition(
                            name=t_data['name'],
                            threshold_type=ThresholdType(t_data['type']),
                            description=t_data['description'],
                            current_value=t_data['current_value'],
                            min_value=t_data.get('min_value'),
                            max_value=t_data.get('max_value'),
                            rollout_percentage=t_data.get('rollout_percentage', 0.0),
                            is_active=t_data.get('is_active', False),
                            created_at=datetime.fromisoformat(t_data['created_at']),
                            created_by=t_data.get('created_by', ''),
                            version=t_data.get('version', '1.0'),
                        )
                        thresholds.append(threshold)

                    # Reconstruct rollback conditions
                    rollback_conditions = []
                    for rc_data in config_data.get('rollback_conditions', []):
                        condition = RollbackCondition(
                            trigger_type=RollbackTrigger(rc_data['trigger_type']),
                            threshold_value=rc_data['threshold_value'],
                            comparison_operator=rc_data['comparison_operator'],
                            grace_period_minutes=rc_data.get('grace_period_minutes', 5),
                            is_active=rc_data.get('is_active', True),
                        )
                        rollback_conditions.append(condition)

                    # Reconstruct config
                    config = ThresholdConfig(
                        model_name=config_data['model_name'],
                        model_version=config_data['model_version'],
                        config_version=config_data['config_version'],
                        description=config_data['description'],
                        thresholds=thresholds,
                        rollback_conditions=rollback_conditions,
                        created_at=datetime.fromisoformat(config_data['created_at']),
                        created_by=config_data.get('created_by', ''),
                    )

                    self._configs[config_key] = config

            except Exception as e:
                # Start fresh if config is corrupted
                self._configs = {}

    def _save_configs(self) -> None:
        """Save threshold configurations to disk."""
        data = {}
        for config_key, config in self._configs.items():
            data[config_key] = {
                'model_name': config.model_name,
                'model_version': config.model_version,
                'config_version': config.config_version,
                'description': config.description,
                'thresholds': [
                    {
                        'name': t.name,
                        'type': t.threshold_type.value,
                        'description': t.description,
                        'current_value': t.current_value,
                        'min_value': t.min_value,
                        'max_value': t.max_value,
                        'rollout_percentage': t.rollout_percentage,
                        'is_active': t.is_active,
                        'created_at': t.created_at.isoformat(),
                        'created_by': t.created_by,
                        'version': t.version,
                        'validation_rules': t.validation_rules,
                    }
                    for t in config.thresholds
                ],
                'rollback_conditions': [
                    {
                        'trigger_type': rc.trigger_type.value,
                        'threshold_value': rc.threshold_value,
                        'comparison_operator': rc.comparison_operator,
                        'grace_period_minutes': rc.grace_period_minutes,
                        'is_active': rc.is_active,
                    }
                    for rc in config.rollback_conditions
                ],
                'created_at': config.created_at.isoformat(),
                'created_by': config.created_by,
                'config_digest': config.config_digest,
            }

        with open(self.configs_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _generate_config_key(self, model_name: str, model_version: str, config_version: str) -> str:
        """Generate unique config key."""
        return f"{model_name}:{model_version}:{config_version}"

    def create_config(
        self,
        model_name: str,
        model_version: str,
        description: str,
        thresholds: list[ThresholdDefinition],
        rollback_conditions: list[RollbackCondition] | None = None,
        created_by: str = "",
    ) -> str:
        """
        Create a new threshold configuration.

        Args:
            model_name: Name of the model
            model_version: Version of the model
            description: Configuration description
            thresholds: List of threshold definitions
            rollback_conditions: List of rollback conditions
            created_by: Who created the config

        Returns:
            Configuration key
        """
        config_version = "1.0"
        config_key = self._generate_config_key(model_name, model_version, config_version)

        # Check if config already exists
        if config_key in self._configs:
            # Increment version
            existing_configs = [
                key for key in self._configs.keys()
                if key.startswith(f"{model_name}:{model_version}:")
            ]
            config_version = str(len(existing_configs) + 1)
            config_key = self._generate_config_key(model_name, model_version, config_version)

        config = ThresholdConfig(
            model_name=model_name,
            model_version=model_version,
            config_version=config_version,
            description=description,
            thresholds=thresholds,
            rollback_conditions=rollback_conditions or [],
            created_by=created_by,
        )

        self._configs[config_key] = config
        self._save_configs()

        # Log to L4 canonical state
        self._log_threshold_event("threshold_config_created", config_key, {
            'model_name': model_name,
            'model_version': model_version,
            'config_version': config_version,
            'threshold_count': len(thresholds),
        })

        return config_key

    def get_config(
        self,
        model_name: str,
        model_version: str,
        config_version: str = "latest",
    ) -> ThresholdConfig | None:
        """Get threshold configuration."""
        if config_version == "latest":
            # Find latest version
            matching_configs = [
                (key, config) for key, config in self._configs.items()
                if config.model_name == model_name and config.model_version == model_version
            ]

            if not matching_configs:
                return None

            # Return config with highest version
            latest_config = max(matching_configs, key=lambda x: int(x[1].config_version))
            return latest_config[1]
        else:
            config_key = self._generate_config_key(model_name, model_version, config_version)
            return self._configs.get(config_key)

    def update_threshold_rollout(
        self,
        model_name: str,
        model_version: str,
        threshold_name: str,
        rollout_percentage: float,
        updated_by: str = "",
    ) -> bool:
        """Update threshold rollout percentage."""
        config = self.get_config(model_name, model_version)
        if not config:
            return False

        success = config.update_threshold(threshold_name, None, rollout_percentage)
        if success:
            self._save_configs()

            # Log rollout update
            self._log_threshold_event("threshold_rollout_updated",
                f"{model_name}:{model_version}", {
                    'threshold_name': threshold_name,
                    'rollout_percentage': rollout_percentage,
                    'updated_by': updated_by,
                })

        return success

    def check_rollback_conditions(
        self,
        model_name: str,
        model_version: str,
        metrics: dict[str, float],
    ) -> list[RollbackTrigger]:
        """
        Check if any rollback conditions are triggered.

        Args:
            model_name: Name of the model
            model_version: Version of the model
            metrics: Current performance metrics

        Returns:
            List of triggered rollback conditions
        """
        config = self.get_config(model_name, model_version)
        if not config:
            return []

        triggered_triggers = []

        for condition in config.rollback_conditions:
            if not condition.is_active:
                continue

            # Get metric value
            metric_value = metrics.get(condition.trigger_type.value)
            if metric_value is None:
                continue

            # Check condition
            triggered = self._evaluate_condition(
                metric_value,
                condition.threshold_value,
                condition.comparison_operator,
            )

            if triggered:
                triggered_triggers.append(condition.trigger_type)

        return triggered_triggers

    def _evaluate_condition(
        self,
        actual_value: float,
        threshold_value: float,
        operator: str,
    ) -> bool:
        """Evaluate rollback condition."""
        if operator == ">":
            return actual_value > threshold_value
        elif operator == "<":
            return actual_value < threshold_value
        elif operator == ">=":
            return actual_value >= threshold_value
        elif operator == "<=":
            return actual_value <= threshold_value
        elif operator == "==":
            return actual_value == threshold_value
        else:
            return False

    def _log_threshold_event(self, event_type: str, config_key: str, data: dict[str, Any]) -> None:
        """Log threshold events to L4 canonical state."""
        try:
            event = {
                'event_type': event_type,
                'config_key': config_key,
                'timestamp': datetime.now().isoformat(),
                'data': data,
            }

            # Store in L4 canonical state
            # self.snapshot_manager.store_event("ml_threshold_config", event)
            # TODO: Replace with local snapshot management

        except Exception as e:
            # Log failure but don't fail the operation
            print(f"Failed to log threshold event: {e}")

    def get_default_thresholds(self, model_type: str) -> list[ThresholdDefinition]:
        """Get default thresholds for a model type."""
        defaults = {
            "logistic_regression": [
                ThresholdDefinition(
                    name="confidence_threshold",
                    threshold_type=ThresholdType.CONFIDENCE,
                    description="Minimum confidence for prediction",
                    current_value=0.7,
                    min_value=0.0,
                    max_value=1.0,
                ),
                ThresholdDefinition(
                    name="escalation_threshold",
                    threshold_type=ThresholdType.PROBABILITY,
                    description="Probability threshold for escalation",
                    current_value=0.9,
                    min_value=0.0,
                    max_value=1.0,
                ),
            ],
            "lightgbm": [
                ThresholdDefinition(
                    name="score_threshold",
                    threshold_type=ThresholdType.SCORE,
                    description="Minimum score for positive prediction",
                    current_value=0.5,
                    min_value=0.0,
                    max_value=1.0,
                ),
            ],
            "isolation_forest": [
                ThresholdDefinition(
                    name="anomaly_score_threshold",
                    threshold_type=ThresholdType.SCORE,
                    description="Threshold for anomaly detection",
                    current_value=0.1,
                    min_value=0.0,
                    max_value=1.0,
                ),
            ],
        }

        return defaults.get(model_type, [])
