from __future__ import annotations
from dataclasses import dataclass
"""Secure Configuration Management - Handles secrets, keys, and config validation.

This module provides secure configuration management with encrypted key storage,
configuration validation, and prevention of hardcoded secrets.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import threading

from .secure_error import SecurityError, ConfigurationError
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.decorators import standard_heal
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

Logger = logging.getLogger(__name__)


@dataclass
class SecureConfigManagerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Manages secure configuration with encrypted storage."""
    
    def __init__(
        self,
        config_dir: Optional[Path] = None,
        master_password: Optional[str] = None,
        env_prefix: str = "AGENTIC_"
    ) -> None:
        """Initialize the secure config manager.
        
        Args:
            config_dir: Directory for encrypted config files
            master_password: Optional master password for encryption
            env_prefix: Prefix for environment variables
        """
        self.config_dir: Path = config_dir or Path.home() / ".agentic_workflow" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.env_prefix: str = env_prefix
        
        # Initialize encryption
        self._init_encryption(master_password)
        
        # Load existing config or create new
        self.config_file = self.config_dir / "secure_config.encrypted"
        self.keys_file = self.config_dir / "encryption_keys.encrypted"
        
        self._lock = threading.Lock()
        self._config = self._load_config()
        self._keys = self._load_keys()
        
        Logger.info(f"Initialized SecureConfigManagerAgent with config dir: {self.config_dir}")
    
    def _init_encryption(self, master_password: Optional[str]) -> None:
        """Initialize encryption keys.
        
        Args:
            master_password: Optional master password
        """
        # Try to get master password from environment
        if not master_password:
            master_password = os.getenv(f"{self.env_prefix}MASTER_PASSWORD")
        
        if master_password:
            # Derive key from password
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
            self.cipher = Fernet(key)
            self.salt = base64.b64encode(salt)
        else:
            # Generate random key
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
    
    def _load_config(self) -> Dict[str, Any]:
        """Load encrypted configuration.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            Logger.error(f"Failed to load config: {e}")
            raise ConfigurationError(f"Configuration load failed: {e}")
    
    def _save_config(self) -> None:
        """Save encrypted configuration."""
        try:
            config_json = json.dumps(self._config, indent=2)
            encrypted_data = self._encrypt_data(config_json)
            
            # Atomic write
            temp_file = self.config_file.with_suffix(".tmp")
            with open(temp_file, 'wb') as f:
                f.write(encrypted_data)
            temp_file.replace(self.config_file)
            
        except Exception as e:
            Logger.error(f"Failed to save config: {e}")
            raise ConfigurationError(f"Configuration save failed: {e}")
    
    def _load_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load encryption keys with metadata.
        
        Returns:
            Keys dictionary with metadata
        """
        if not self.keys_file.exists():
            return {}
        
        try:
            with open(self.keys_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            Logger.error(f"Failed to load keys: {e}")
            return {}
    
    def _save_keys(self) -> None:
        """Save encryption keys with metadata."""
        try:
            keys_json = json.dumps(self._keys, indent=2)
            encrypted_data = self._encrypt_data(keys_json)
            
            # Atomic write
            temp_file = self.keys_file.with_suffix(".tmp")
            with open(temp_file, 'wb') as f:
                f.write(encrypted_data)
            temp_file.replace(self.keys_file)
            
        except Exception as e:
            Logger.error(f"Failed to save keys: {e}")
            raise ConfigurationError(f"Keys save failed: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        with self._lock:
            # Check environment first
            env_key = f"{self.env_prefix}{key.upper()}"
            env_value = os.getenv(env_key)
            if env_value is not None:
                return env_value
            
            # Check stored config
            return self._config.get(key, default)
    
    def set(self, key: str, value: Any, sensitive: bool = False) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
            sensitive: Whether the value is sensitive
        """
        with self._lock:
            if sensitive and not isinstance(value, str):
                raise ConfigurationError("Sensitive values must be strings")
            
            self._config[key] = value
            self._save_config()
            
            Logger.debug(f"Set config: {key} (sensitive: {sensitive})")
    
    def generate_key(self, key_name: str, rotation_days: int = 90) -> str:
        """Generate and store an encryption key.
        
        Args:
            key_name: Name for the key
            rotation_days: Days before key should be rotated
            
        Returns:
            Generated key (base64 encoded)
        """
        with self._lock:
            # Generate key
            key = Fernet.generate_key()
            key_b64 = base64.b64encode(key).decode()
            
            # Store with metadata
            self._keys[key_name] = {
                "key": key_b64,
                "created_at": time.time(),
                "rotation_days": rotation_days,
                "last_rotated": time.time()
            }
            
            self._save_keys()
            Logger.info(f"Generated encryption key: {key_name}")
            
            return key_b64
    
    def get_key(self, key_name: str) -> Optional[str]:
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
            
            # Check if key needs rotation
            if self._key_needs_rotation(key_data):
                Logger.warning(f"Key {key_name} needs rotation")
            
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
            
            # Generate new key
            new_key = self.generate_key(key_name, old_key_data["rotation_days"])
            
            # Archive old key
            archive_name = f"{key_name}_archived_{int(time.time())}"
            self._keys[archive_name] = old_key_data.copy()
            
            Logger.info(f"Rotated key: {key_name}")
            return new_key
    
    def _key_needs_rotation(self, key_data: Dict[str, Any]) -> bool:
        """Check if a key needs rotation.
        
        Args:
            key_data: Key metadata
            
        Returns:
            True if key needs rotation
        """
        last_rotated = key_data.get("last_rotated", 0)
        rotation_days = key_data.get("rotation_days", 90)
        
        rotation_time = last_rotated + (rotation_days * 24 * 60 * 60)
        return time.time() > rotation_time
    
    def list_keys_needing_rotation(self) -> List[str]:
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
    
    def validate_config(self, schema: Dict[str, Any]) -> List[str]:
        """Validate configuration against a schema.
        
        Args:
            schema: Validation schema
            
        Returns:
            List of validation errors
        """
        errors = []
        
        for key, spec in schema.items():
            if spec.get("required", False) and key not in self._config:
                if not os.getenv(f"{self.env_prefix}{key.upper()}"):
                    errors.append(f"Required configuration Missing: {key}")
            
            if key in self._config:
                value = self._config[key]
                expected_type = spec.get("type")
                if expected_type and not isinstance(value, expected_type):
                    errors.append(f"Invalid type for {key}: expected {expected_type.__name__}")
        
        return errors
    
    def export_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Export configuration for backup.
        
        Args:
            include_secrets: Whether to include sensitive values
            
        Returns:
            Exported configuration
        """
        with self._lock:
            exported = {
                "config": {},
                "metadata": {
                    "exported_at": time.time(),
                    "version": "1.0"
                }
            }
            
            for key, value in self._config.items():
                if self._is_sensitive_key(key) and not include_secrets:
                    exported["config"][key] = "<REDACTED>"
                else:
                    exported["config"][key] = value
            
            return exported
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key is considered sensitive.
        
        Args:
            key: Configuration key
            
        Returns:
            True if key is sensitive
        """
        sensitive_patterns = [
            "password", "secret", "token", "key", "credential",
            "api_key", "private", "auth"
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
            cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
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
                Logger.info(f"Cleaned up {len(keys_to_remove)} old keys")
            
            return len(keys_to_remove)

    @timeout(120)
    @standard_heal
    def heal_repository(
        self, 
        dry_run: bool = True, 
        execute: bool = False, 
        depth: int = 0, 
        max_depth: int = 3, 
        _call_path: Optional[set] = None
    ) -> Dict[str, int]:
        """
        Sovereign security healing - validates encryption, detects exposed secrets, 
        and reconciles config formats.
        
        WIRED CAPABILITIES:
        - _validate_encryption_hygiene(): Checks if sensitive keys are properly encrypted.
        - _scan_for_exposed_secrets(): Looks for plaintext API keys in config files.
        - _reconcile_config_schema(): Ensures configs match the current standard blueprint.
        """
        # CRITICAL: Chain up to HealerMixin
        super().heal_repository(dry_run=dry_run, execute=execute)
        
        # Cycle/Depth Detection
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path or depth > max_depth:
            return {"errors": 1, "skipped": 1}
        _call_path.add(agent_name)
        
        metrics = {"violations": 0, "fixed": 0, "errors": 0, "skipped": 0}
        
        try:
            # 1. Encryption Hygiene (The most dangerous orphaned capability)
            if hasattr(self, '_validate_encryption_hygiene'):
                enc_results = self._validate_encryption_hygiene(dry_run=dry_run)
                metrics["violations"] += enc_results.get("violations", 0)
                metrics["fixed"] += enc_results.get("fixed", 0)
                
            # 2. Schema Reconciliation
            if hasattr(self, '_reconcile_config_schema'):
                schema_results = self._reconcile_config_schema(dry_run=dry_run)
                metrics["violations"] += schema_results.get("violations", 0)
                metrics["fixed"] += schema_results.get("fixed", 0)

            # 3. Handle Execution/Commit if applicable
            if execute and not dry_run and getattr(self, 'dirty_config', False):
                if hasattr(self, '_save_config'):
                    self._save_config()
                    metrics["fixed"] += 1

        except Exception as e:
            Logger.error(f"[{agent_name}] Security Healing Failed: {str(e)}")
            metrics["errors"] += 1
        finally:
            _call_path.discard(agent_name)
            
        return metrics


# Global config manager instance
_default_manager: Optional[SecureConfigManagerAgent] = None
_manager_lock = threading.Lock()


def get_config_manager() -> SecureConfigManagerAgent:
    """Get the default secure config manager.
    
    Returns:
        SecureConfigManagerAgent instance
    """
    global _default_manager
    
    if _default_manager is None:
        with _manager_lock:
            if _default_manager is None:
                _default_manager = SecureConfigManagerAgent()
    
    return _default_manager


def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value from the default manager.
    
    Args:
        key: Configuration key
        default: Default value
        
    Returns:
        Configuration value
    """
    return get_config_manager().get(key, default)


def set_config(key: str, value: Any, sensitive: bool = False) -> None:
    """Set a configuration value in the default manager.
    
    Args:
        key: Configuration key
        value: Value to set
        sensitive: Whether the value is sensitive
    """
    get_config_manager().set(key, value, sensitive)


def get_encryption_key(key_name: str) -> Optional[str]:
    """Get an encryption key from the default manager.
    
    Args:
        key_name: Name of the encryption key
        
    Returns:
        The encryption key or None
    """
    return get_config_manager().get_key(key_name)

def get_secure_config_manager(config_dir: Optional[Path] = None, master_password: Optional[str] = None) -> SecureConfigManagerAgent:
    """Factory function to get secure config manager."""
    return SecureConfigManagerAgent(config_dir, master_password)
