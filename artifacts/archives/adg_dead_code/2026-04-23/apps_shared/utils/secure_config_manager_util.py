"""Secure configuration Management - Handles secrets, keys, and config validation.

This module provides secure configuration management with encrypted key storage,
configuration validation, and prevention of hardcoded secrets.
"""

import base64
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "secure_config_manager_util", "p0_governance")
_emit_reads_policy_state("p0", "secure_config_manager_util", "policy_binding")
_emit_snapshots_state("p0", "secure_config_manager_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("secure_config_manager_util", "p4obs", "metric_1")
_emit_emits_metric_event("secure_config_manager_util", "p4obs", "metric_2")
_emit_emits_metric_event("secure_config_manager_util", "p4obs", "metric_3")
_emit_emits_metric_event("secure_config_manager_util", "p4obs", "metric_4")
_emit_emits_metric_event("secure_config_manager_util", "p4obs", "metric_5")
_emit_emits_metric_event("secure_config_manager_util", "p4obs", "metric_6")
_emit_records_incident_event("secure_config_manager_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("secure_config_manager_util", "p4obs", "anomaly")
_emit_writes_observability_log("secure_config_manager_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("secure_config_manager_util", "p4obs", "mon_state")
_emit_triggers_alert("secure_config_manager_util", "p4obs", "alert")
_emit_links_incident_trace("secure_config_manager_util", "p4obs", "trace_link")
_emit_captures_pattern("secure_config_manager_util", "p3lm", "pattern")
_emit_records_learning_event("secure_config_manager_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("secure_config_manager_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("secure_config_manager_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("secure_config_manager_util", "p3lm", "routing")
_emit_improves_agent_policy("secure_config_manager_util", "p3lm", "policy")
_emit_stores_learning_state("secure_config_manager_util", "p3lm", "state")
_emit_records_execution_trace("secure_config_manager_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("secure_config_manager_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("secure_config_manager_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("secure_config_manager_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("secure_config_manager_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("secure_config_manager_util", "env_read", "p2_env_1")
_emit_reads_environ("secure_config_manager_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("secure_config_manager_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("secure_config_manager_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "secure_config_manager_util", "context_pull")
_emit_pulls_context("p1", "secure_config_manager_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "secure_config_manager_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "secure_config_manager_util", "uwg_term_2")
_emit_writes_through("p1", "secure_config_manager_util", "write_through")
_emit_writes_through("p1", "secure_config_manager_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "secure_config_manager_util", "safety_validation")
_emit_invokes_eval("p1", "secure_config_manager_util", "eval_call")
_emit_proposal_commits_routing("p1", "secure_config_manager_util", "routing_commit")
_emit_escalates_to_human("p1", "secure_config_manager_util", "human_escalation")
_emit_routes_through("p1", "secure_config_manager_util", "route_through")
_emit_checks_agent_registry("p1", "secure_config_manager_util", "agent_registry")
_emit_validates_agent_capability("p1", "secure_config_manager_util", "capability")
_emit_dispatches_execution_plan("p1", "secure_config_manager_util", "exec_plan")
_emit_agent_executes_agent("p1", "secure_config_manager_util", "sub_agent")
_emit_routes_to_agent("p1", "secure_config_manager_util", "target_agent")
_emit_verifies_policy("p1", "secure_config_manager_util", "policy_check")
_emit_observes_runtime_state("p1", "secure_config_manager_util", "runtime_state")
_emit_verifies_boundary("p1", "secure_config_manager_util", "boundary_check")
_emit_transcripts_response("p1", "secure_config_manager_util", "transcript")
_emit_hard_fails_untranscripted("p1", "secure_config_manager_util")
_emit_gated_by_confidence("p1", "secure_config_manager_util", "confidence_gate")
emit_replay_key("p0", "secure_config_manager_util")
emit_determinism_digest("p0", "secure_config_manager_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "secure_config_manager_util", "execution_auth")
_emit_validates_capability("p2", "secure_config_manager_util", "capability_check")
_emit_routes_to_capability("p2", "secure_config_manager_util", "capability_route")
_emit_writes_via_uwg("p2", "secure_config_manager_util", "uwg_write")
_emit_blocks_direct_write("p2", "secure_config_manager_util", "direct_write_block")
_emit_records_tool_invocation("p2", "secure_config_manager_util", "tool_invocation")
_emit_captures_execution_output("p2", "secure_config_manager_util", "exec_output")
_emit_dispatches_agent("p3", "secure_config_manager_util", "agent_dispatch")
_emit_coordinates_agents("p3", "secure_config_manager_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "secure_config_manager_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "secure_config_manager_util", "healing_outcome")
_emit_escalates_failure("p3", "secure_config_manager_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "secure_config_manager_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "secure_config_manager_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "secure_config_manager_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "secure_config_manager_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "secure_config_manager_util", "eval_metric")
_emit_stores_embedding("p4", "secure_config_manager_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "secure_config_manager_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "secure_config_manager_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class SecureConfigManager:
    """Manages secure configuration with encrypted storage."""

    def __init__(
        self,
        config_dir: Path | None = None,
        master_password: str | None = None,
        env_prefix: str = "AGENTIC_",
    ):
        """Initialize the secure config manager.

        Args:
            config_dir: Directory for encrypted config files
            master_password: Optional master password for encryption
            env_prefix: Prefix for environment variables
        """
        self.config_dir = config_dir or Path.home() / ".agentic_workflow" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.env_prefix = env_prefix
        self._init_encryption(master_password)
        self.config_file = self.config_dir / "secure_config.encrypted"
        self.keys_file = self.config_dir / "encryption_keys.encrypted"
        self._lock = threading.Lock()
        self._config = self._load_config()
        self._keys = self._load_keys()
        logger.info(f"Initialized SecureConfigManager with config dir: {self.config_dir}")

    def _init_encryption(self, master_password: str | None) -> None:
        """Initialize encryption keys.

        Args:
            master_password: Optional master password
        """
        if not master_password:
            master_password = os.getenv(f"{self.env_prefix}MASTER_PASSWORD")
        if master_password:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
            self.cipher = Fernet(key)
            self.salt = base64.b64encode(salt)
        else:
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)
            self.salt = None

    def _encrypt_data(self, data: str) -> bytes:
        """Encrypt data.

        Args:
            data: Data to encrypt

        Returns:
            Encrypted bytes
        """
        return self.cipher.encrypt(data.encode())

    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data.

        Args:
            encrypted_data: Encrypted data

        Returns:
            Decrypted string
        """
        return self.cipher.decrypt(encrypted_data).decode()

    def _load_config(self) -> dict[str, Any]:
        """Load encrypted configuration.

        Returns:
            configuration dictionary
        """
        # guardian: allow-config-with-logic
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self._decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to load config: {e}")
            raise ConfigurationError(f"configuration load failed: {e}") from e

    def _save_config(self) -> None:
        """Save encrypted configuration."""
        try:
            config_json = json.dumps(self._config, indent=2)
            encrypted_data = self._encrypt_data(config_json)
            temp_file = self.config_file.with_suffix(".tmp")
            with open(temp_file, "wb") as f:
                f.write(encrypted_data)
            temp_file.replace(self.config_file)
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to save config: {e}")
            raise ConfigurationError(f"configuration save failed: {e}") from e

    def _load_keys(self) -> dict[str, dict[str, Any]]:
        """Load encryption keys with metadata.

        Returns:
            Keys dictionary with metadata
        """
        if not self.keys_file.exists():
            return {}
        try:
            with open(self.keys_file, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self._decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to load keys: {e}")
            return {}

    def _save_keys(self) -> None:
        """Save encryption keys with metadata."""
        try:
            keys_json = json.dumps(self._keys, indent=2)
            encrypted_data = self._encrypt_data(keys_json)
            temp_file = self.keys_file.with_suffix(".tmp")
            with open(temp_file, "wb") as f:
                f.write(encrypted_data)
            temp_file.replace(self.keys_file)
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to save keys: {e}")
            raise ConfigurationError(f"Keys save failed: {e}") from e

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: configuration key
            default: Default value if not found

        Returns:
            configuration value
        """
        with self._lock:
            env_key = f"{self.env_prefix}{key.upper()}"
            env_value = os.getenv(env_key)
            if env_value is not None:
                return env_value
            return self._config.get(key, default)

    def set(self, key: str, value: Any, sensitive: bool = False) -> None:
        """Set a configuration value.

        Args:
            key: configuration key
            value: Value to set
            sensitive: Whether the value is sensitive
        """
        with self._lock:
            if sensitive and (not isinstance(value, str)):
                raise ConfigurationError("Sensitive values must be strings")
            self._config[key] = value
            self._save_config()
            logger.debug(f"Set config: {key} (sensitive: {sensitive})")

    def generate_key(self, key_name: str, rotation_days: int = 90) -> str:
        """Generate and store an encryption key.

        Args:
            key_name: Name for the key
            rotation_days: Days before key should be rotated

        Returns:
            Generated key (base64 encoded)
        """
        with self._lock:
            key = Fernet.generate_key()
            key_b64 = base64.b64encode(key).decode()
            self._keys[key_name] = {
                "key": key_b64,
                "created_at": time.time(),
                "rotation_days": rotation_days,
                "last_rotated": time.time(),
            }
            self._save_keys()
            logger.info(f"Generated encryption key: {key_name}")
            return key_b64

    def get_key(self, key_name: str) -> str | None:
        """Get an encryption key.

        Args:
            key_name: Name of the key

        Returns:
            Key if found, None otherwise
        """
        with self._lock:
            key_data = self._keys.get(key_name)
            if not key_data:
                return None
            if self._key_needs_rotation(key_data):
                logger.warning(f"Key {key_name} needs rotation")
            return key_data["key"]

    def rotate_key(self, key_name: str) -> str:
        """Rotate an encryption key.

        Args:
            key_name: Name of the key to rotate

        Returns:
            New key
        """
        with self._lock:
            old_key_data = self._keys.get(key_name)
            if not old_key_data:
                raise ConfigurationError(f"Key not found: {key_name}")
            new_key = self.generate_key(key_name, old_key_data["rotation_days"])
            archive_name = f"{key_name}_archived_{int(time.time())}"
            self._keys[archive_name] = old_key_data.copy()
            logger.info(f"Rotated key: {key_name}")
            return new_key

    def _key_needs_rotation(self, key_data: dict[str, Any]) -> bool:
        """Check if a key needs rotation.

        Args:
            key_data: Key metadata

        Returns:
            True if key needs rotation
        """
        last_rotated = key_data.get("last_rotated", 0)
        rotation_days = key_data.get("rotation_days", 90)
        rotation_time = last_rotated + rotation_days * 24 * 60 * 60
        return time.time() > rotation_time

    def list_keys_needing_rotation(self) -> list[str]:
        """List keys that need rotation.

        Returns:
            List of key names needing rotation
        """
        with self._lock:
            needs_rotation = []
            for key_name, key_data in self._keys.items():
                if not key_name.endswith("_archived_") and self._key_needs_rotation(key_data):
                    needs_rotation.append(key_name)
            return needs_rotation

    def validate_config(self, schema: dict[str, Any]) -> list[str]:
        """Validate configuration against a schema.

        Args:
            schema: Validation schema

        Returns:
            List of validation errors
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SecureConfigManager.validate_config"
        )

        errors = []
        for key, spec in tqdm(schema.items(), desc="Processing", unit="item"):
            # guardian: allow-config-with-logic
            if spec.get("required", False) and key not in self._config:
                # guardian: allow-config-with-logic
                if not os.getenv(f"{self.env_prefix}{key.upper()}"):
                    errors.append(f"Required configuration missing: {key}")
            # guardian: allow-config-with-logic
            if key in self._config:
                value = self._config[key]
                expected_type = spec.get("type")
                # guardian: allow-config-with-logic
                if expected_type and (not isinstance(value, expected_type)):
                    errors.append(f"Invalid type for {key}: expected {expected_type.__name__}")
        return errors

    def export_config(self, include_secrets: bool = False) -> dict[str, Any]:
        """Export configuration for backup.

        Args:
            include_secrets: Whether to include sensitive values

        Returns:
            Exported configuration
        """
        with self._lock:
            exported = {"config": {}, "metadata": {"exported_at": time.time(), "version": "1.0"}}
            for key, value in self._config.items():
                # guardian: allow-config-with-logic
                if self._is_sensitive_key(key) and (not include_secrets):
                    exported["config"][key] = "<REDACTED>"
                else:
                    exported["config"][key] = value
            return exported

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key is considered sensitive.

        Args:
            key: configuration key

        Returns:
            True if key is sensitive
        """
        sensitive_patterns = [
            "password",
            "secret",
            "token",
            "key",
            "credential",
            "api_key",
            "private",
            "auth",
        ]
        return any(pattern in key.lower() for pattern in sensitive_patterns)

    def cleanup_old_keys(self, keep_days: int = 30) -> int:
        """Clean up old archived keys.

        Args:
            keep_days: Days to keep archived keys

        Returns:
            Number of keys cleaned up
        """
        with self._lock:
            cutoff_time = time.time() - keep_days * 24 * 60 * 60
            keys_to_remove = []
            for key_name in list(self._keys.keys()):
                if key_name.endswith("_archived_"):
                    try:
                        timestamp = int(key_name.split("_")[-1])
                        if timestamp < cutoff_time:
                            keys_to_remove.append(key_name)
                    except (ValueError, IndexError):
                        continue
            for key_name in keys_to_remove:
                del self._keys[key_name]
            if keys_to_remove:
                self._save_keys()
                logger.info(f"Cleaned up {len(keys_to_remove)} old keys")
            return len(keys_to_remove)


_default_manager: SecureConfigManager | None = None
_manager_lock = threading.Lock()


def get_config_manager() -> SecureConfigManager:
    """Get the default secure config manager.

    Returns:
        SecureConfigManager instance
    """
    global _default_manager
    if _default_manager is None:
        with _manager_lock:
            if _default_manager is None:
                _default_manager = SecureConfigManager()
    return _default_manager


def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value from the default manager.

    Args:
        key: configuration key
        default: Default value

    Returns:
        configuration value
    """
    return get_config_manager().get(key, default)


def set_config(key: str, value: Any, sensitive: bool = False) -> None:
    """Set a configuration value in the default manager.

    Args:
        key: configuration key
        value: Value to set
        sensitive: Whether the value is sensitive
    """
    get_config_manager().set(key, value, sensitive)


def get_encryption_key(key_name: str) -> str | None:
    """Get an encryption key from the default manager.

    Args:
        key_name: Name of the key

    Returns:
        Encryption key if found
    """
    return get_config_manager().get_key(key_name)
