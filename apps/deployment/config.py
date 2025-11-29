"""
Deployment Configuration - Environment Separation

Section 18: Deployment Layer - Environment configuration
and separation for development, staging, and production.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "agentic_db"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class RedisConfig:
    """Redis configuration for session management."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    max_connections: int = 100


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = "dev-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    require_email_verification: bool = False


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class DeploymentConfig:
    """
    Main deployment configuration with environment separation.
    
    Provides configuration management for different deployment
    environments with appropriate security and isolation.
    """
    environment: Environment = Environment.DEVELOPMENT
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Feature flags
    enable_auth: bool = True
    enable_session_management: bool = True
    enable_rate_limiting: bool = True
    enable_cors: bool = True
    enable_https: bool = False
    
    # Environment-specific settings
    debug_mode: bool = False
    mock_external_services: bool = True
    
    @classmethod
    def from_environment(cls) -> DeploymentConfig:
        """
        Load configuration from environment variables.
        
        Returns:
            DeploymentConfig loaded from environment
        """
        env_str = os.getenv("DEPLOYMENT_ENV", "development").lower()
        try:
            environment = Environment(env_str)
        except ValueError:
            logger.warning(f"Invalid environment '{env_str}', using development")
            environment = Environment.DEVELOPMENT
        
        # Build configuration based on environment
        config = cls(environment=environment)
        
        # Override with environment variables
        config.api.host = os.getenv("API_HOST", config.api.host)
        config.api.port = int(os.getenv("API_PORT", str(config.api.port)))
        config.api.debug = os.getenv("API_DEBUG", "false").lower() == "true"
        
        config.database.host = os.getenv("DB_HOST", config.database.host)
        config.database.port = int(os.getenv("DB_PORT", str(config.database.port)))
        config.database.name = os.getenv("DB_NAME", config.database.name)
        config.database.username = os.getenv("DB_USERNAME", config.database.username)
        config.database.password = os.getenv("DB_PASSWORD", config.database.password)
        
        config.redis.host = os.getenv("REDIS_HOST", config.redis.host)
        config.redis.port = int(os.getenv("REDIS_PORT", str(config.redis.port)))
        config.redis.password = os.getenv("REDIS_PASSWORD", config.redis.password)
        
        config.security.secret_key = os.getenv("SECRET_KEY", config.security.secret_key)
        
        config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
        config.logging.file_path = os.getenv("LOG_FILE_PATH", config.logging.file_path)
        
        # Apply environment-specific settings
        config._apply_environment_defaults()
        
        return config
    
    def _apply_environment_defaults(self) -> None:
        """Apply environment-specific default settings."""
        if self.environment == Environment.DEVELOPMENT:
            self.debug_mode = True
            self.api.debug = True
            self.mock_external_services = True
            self.enable_https = False
            self.security.secret_key = "dev-secret-key"
            self.api.cors_origins = ["*"]
            
        elif self.environment == Environment.TESTING:
            self.debug_mode = True
            self.mock_external_services = True
            self.enable_https = False
            self.security.secret_key = "test-secret-key"
            self.enable_rate_limiting = False
            self.database.name = "agentic_test_db"
            
        elif self.environment == Environment.STAGING:
            self.debug_mode = False
            self.mock_external_services = False
            self.enable_https = True
            self.enable_auth = True
            self.enable_session_management = True
            self.api.cors_origins = [
                "https://staging.example.com",
                "https://admin-staging.example.com"
            ]
            
        elif self.environment == Environment.PRODUCTION:
            self.debug_mode = False
            self.mock_external_services = False
            self.enable_https = True
            self.enable_auth = True
            self.enable_session_management = True
            self.enable_rate_limiting = True
            self.security.secret_key = os.getenv("SECRET_KEY", "")
            self.api.cors_origins = [
                "https://app.example.com",
                "https://admin.example.com"
            ]
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required security settings for production
        if self.environment == Environment.PRODUCTION:
            if not self.security.secret_key or self.security.secret_key in ["dev-secret-key", "test-secret-key"]:
                errors.append("Production environment requires a strong secret key")
            
            if not self.enable_https:
                errors.append("Production environment requires HTTPS")
            
            if not self.enable_auth:
                errors.append("Production environment requires authentication")
        
        # Check database configuration
        if not self.database.host:
            errors.append("Database host is required")
        
        if not self.database.name:
            errors.append("Database name is required")
        
        # Check API configuration
        if self.api.port < 1 or self.api.port > 65535:
            errors.append("API port must be between 1 and 65535")
        
        # Check Redis configuration for session management
        if self.enable_session_management and not self.redis.host:
            errors.append("Redis host is required when session management is enabled")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "environment": self.environment.value,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "name": self.database.name,
                "username": self.database.username,
                "ssl_mode": self.database.ssl_mode,
                "pool_size": self.database.pool_size,
            },
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "db": self.redis.db,
                "ssl": self.redis.ssl,
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "debug": self.api.debug,
                "cors_origins": self.api.cors_origins,
            },
            "security": {
                "algorithm": self.security.algorithm,
                "access_token_expire_minutes": self.security.access_token_expire_minutes,
                "password_min_length": self.security.password_min_length,
            },
            "features": {
                "enable_auth": self.enable_auth,
                "enable_session_management": self.enable_session_management,
                "enable_rate_limiting": self.enable_rate_limiting,
                "enable_cors": self.enable_cors,
                "enable_https": self.enable_https,
            },
            "debug_mode": self.debug_mode,
            "mock_external_services": self.mock_external_services,
        }


def load_config(config_path: Optional[str] = None) -> DeploymentConfig:
    """
    Load deployment configuration.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Loaded deployment configuration
    """
    if config_path and Path(config_path).exists():
        # TODO: Implement file-based config loading
        logger.info(f"Loading config from file: {config_path}")
    
    # Load from environment variables
    config = DeploymentConfig.from_environment()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        error_msg = "Configuration validation failed: " + "; ".join(errors)
        if config.environment == Environment.PRODUCTION:
            raise ValueError(error_msg)
        else:
            logger.warning(error_msg)
    
    logger.info(f"Loaded deployment config for environment: {config.environment.value}")
    return config


__all__ = [
    "Environment",
    "DeploymentConfig", 
    "DatabaseConfig",
    "RedisConfig",
    "SecurityConfig",
    "APIConfig",
    "LoggingConfig",
    "load_config"
]





