"""
Outreach Engine Setup CLI
LEVEL 5 - Setup and configuration utility for the Outreach Engine
"""

import argparse
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

class OutreachEngineSetup:
    """Setup utility for the Outreach Engine"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.outreach_engine_root = self.project_root / "apps" / "outreach_engine"

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def setup_environment(self, config_file: Optional[str] = None):
        """Setup the outreach engine environment"""
        try:
            self.logger.info("Setting up Outreach Engine environment")

            # Load configuration
            config = self._load_config(config_file) if config_file else self._get_default_config()

            # Create necessary directories
            self._create_directories(config)

            # Create configuration files
            self._create_config_files(config)

            # Setup database connections
            self._setup_database(config)

            # Initialize logging
            self._setup_logging_config(config)

            # Create startup scripts
            self._create_startup_scripts(config)

            print("✅ Outreach Engine environment setup completed!")
            print(f"📁 Installation directory: {self.outreach_engine_root}")
            print(f"⚙️  Configuration loaded from: {config_file or 'default'}")

        except Exception as e:
            self.logger.error(f"Environment setup failed: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)

    def validate_setup(self):
        """Validate the outreach engine setup"""
        try:
            self.logger.info("Validating Outreach Engine setup")

            validation_results = {
                "directories": self._validate_directories(),
                "config_files": self._validate_config_files(),
                "dependencies": self._validate_dependencies(),
                "database": self._validate_database(),
                "permissions": self._validate_permissions()
            }

            # Calculate overall status
            all_valid = all(result["valid"] for result in validation_results.values())

            # Display results
            print("\n🔍 Outreach Engine Setup Validation")
            print(f"{'='*50}")

            for component, result in validation_results.items():
                status = "✅" if result["valid"] else "❌"
                print(f"{status} {component.replace('_', ' ').title()}: {result['message']}")

                if not result["valid"] and result.get("details"):
                    for detail in result["details"]:
                        print(f"    • {detail}")

            overall_status = "✅ VALID" if all_valid else "❌ INVALID"
            print(f"\n📊 Overall Status: {overall_status}")

            if not all_valid:
                print("\n💡 Please fix the issues above before using the Outreach Engine")
                sys.exit(1)
            else:
                print("\n🎉 Setup validation passed! Outreach Engine is ready to use.")

        except Exception as e:
            self.logger.error(f"Setup validation failed: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)

    def create_config_template(self, output_file: str):
        """Create a configuration template file"""
        try:
            template = self._get_config_template()

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            print(f"✅ Configuration template created: {output_file}")
            print("📝 Edit this file and use it with 'setup --config <file>'")

        except Exception as e:
            self.logger.error(f"Failed to create config template: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)

    def install_dependencies(self):
        """Install required dependencies"""
        try:
            self.logger.info("Installing Outreach Engine dependencies")

            # Create requirements file
            requirements_content = self._get_requirements_content()
            requirements_file = self.outreach_engine_root / "requirements.txt"

            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write(requirements_content)

            print(f"📦 Requirements file created: {requirements_file}")
            print("💡 Install dependencies with: pip install -r requirements.txt")
            print("🔧 Or use: pip install -e . (for development mode)")

        except Exception as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "database": {
                "type": "sqlite",
                "path": "outreach_engine.db",
                "backup_enabled": True,
                "backup_interval": 3600
            },
            "logging": {
                "level": "INFO",
                "file": "outreach_engine.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "workers": {
                "outreach_worker": {
                    "max_concurrent_tasks": 5,
                    "task_timeout": 300,
                    "enabled": True
                },
                "enrichment_worker": {
                    "max_concurrent_tasks": 3,
                    "task_timeout": 180,
                    "enabled": True
                },
                "delivery_worker": {
                    "max_concurrent_tasks": 5,
                    "task_timeout": 120,
                    "enabled": True
                }
            },
            "api": {
                "host": "localhost",
                "port": 8000,
                "debug": False,
                "cors_enabled": True
            },
            "security": {
                "jwt_secret_key": "your-secret-key-here",
                "api_rate_limit": 100,
                "session_timeout": 3600
            }
        }

    def _create_directories(self, config: Dict[str, Any]):
        """Create necessary directories"""
        directories = [
            self.outreach_engine_root / "logs",
            self.outreach_engine_root / "data",
            self.outreach_engine_root / "cache",
            self.outreach_engine_root / "temp",
            self.outreach_engine_root / "backups",
            self.outreach_engine_root / "config"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")

    def _create_config_files(self, config: Dict[str, Any]):
        """Create configuration files"""
        # Save main configuration
        config_file = self.outreach_engine_root / "config" / "outreach_engine.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # Create environment file
        env_file = self.outreach_engine_root / ".env"
        env_content = self._get_env_content(config)
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)

        self.logger.info("Configuration files created")

    def _setup_database(self, config: Dict[str, Any]):
        """Setup database connections"""
        db_config = config.get("database", {})
        db_type = db_config.get("type", "sqlite")

        if db_type == "sqlite":
            db_path = self.outreach_engine_root / "data" / db_config.get("path", "outreach_engine.db")
            # Create database file (empty)
            db_path.touch()
            self.logger.info(f"SQLite database created: {db_path}")

        # Create database schema placeholder
        schema_file = self.outreach_engine_root / "config" / "schema.sql"
        schema_content = self._get_database_schema(db_type)
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(schema_content)

    def _setup_logging_config(self, config: Dict[str, Any]):
        """Setup logging configuration"""
        log_config = config.get("logging", {})
        log_file = self.outreach_engine_root / "logs" / log_config.get("file", "outreach_engine.log")

        # Create log file
        log_file.touch()
        self.logger.info(f"Logging setup completed: {log_file}")

    def _create_startup_scripts(self, config: Dict[str, Any]):
        """Create startup scripts"""
        # Create startup shell script
        startup_script = self.outreach_engine_root / "start_outreach_engine.sh"
        startup_content = self._get_startup_script_content(config)
        with open(startup_script, 'w', encoding='utf-8') as f:
            f.write(startup_content)

        # Make script executable
        os.chmod(startup_script, 0o755)

        # Create Windows batch file
        batch_script = self.outreach_engine_root / "start_outreach_engine.bat"
        batch_content = self._get_batch_script_content(config)
        with open(batch_script, 'w', encoding='utf-8') as f:
            f.write(batch_content)

        self.logger.info("Startup scripts created")

    def _validate_directories(self) -> Dict[str, Any]:
        """Validate required directories"""
        required_dirs = [
            "api/v1/endpoints",
            "api/v1/schemas",
            "api/v1/middleware",
            "services/builders",
            "services/enrichers",
            "services/generators",
            "services/pipelines",
            "services/utils",
            "workers",
            "cli",
            "tests"
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.outreach_engine_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)

        return {
            "valid": len(missing_dirs) == 0,
            "message": f"Found {len(required_dirs) - len(missing_dirs)}/{len(required_dirs)} directories",
            "details": missing_dirs if missing_dirs else None
        }

    def _validate_config_files(self) -> Dict[str, Any]:
        """Validate configuration files"""
        config_files = [
            "config/outreach_engine.json",
            ".env"
        ]

        missing_files = []
        for file_path in config_files:
            full_path = self.outreach_engine_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        return {
            "valid": len(missing_files) == 0,
            "message": f"Found {len(config_files) - len(missing_files)}/{len(config_files)} config files",
            "details": missing_files if missing_files else None
        }

    def _validate_dependencies(self) -> Dict[str, Any]:
        """Validate Python dependencies"""
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "sqlalchemy",
            "asyncio",
            "aiofiles",
            "python-multipart"
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        return {
            "valid": len(missing_packages) == 0,
            "message": f"Found {len(required_packages) - len(missing_packages)}/{len(required_packages)} packages",
            "details": missing_packages if missing_packages else None
        }

    def _validate_database(self) -> Dict[str, Any]:
        """Validate database setup"""
        db_path = self.outreach_engine_root / "data" / "outreach_engine.db"

        if not db_path.exists():
            return {
                "valid": False,
                "message": "Database file not found",
                "details": ["Create database file using setup command"]
            }

        return {
            "valid": True,
            "message": "Database file exists",
            "details": None
        }

    def _validate_permissions(self) -> Dict[str, Any]:
        """Validate file permissions"""
        issues = []

        # Check write permissions in key directories
        test_dirs = ["logs", "data", "temp"]
        for dir_name in test_dirs:
            dir_path = self.outreach_engine_root / dir_name
            if dir_path.exists():
                test_file = dir_path / "permission_test.tmp"
                try:
                    test_file.touch()
                    test_file.unlink()
                except PermissionError:
                    issues.append(f"No write permission in {dir_name}")

        return {
            "valid": len(issues) == 0,
            "message": "Permissions OK" if len(issues) == 0 else f"Permission issues found: {len(issues)}",
            "details": issues if issues else None
        }

    def _get_config_template(self) -> Dict[str, Any]:
        """Get configuration template"""
        return {
            "database": {
                "type": "sqlite",
                "path": "outreach_engine.db",
                "backup_enabled": True,
                "backup_interval": 3600,
                "_comment": "Database configuration - supports sqlite, postgresql, mysql"
            },
            "logging": {
                "level": "INFO",
                "file": "outreach_engine.log",
                "max_size": "10MB",
                "backup_count": 5,
                "_comment": "Logging configuration - levels: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            },
            "workers": {
                "outreach_worker": {
                    "max_concurrent_tasks": 5,
                    "task_timeout": 300,
                    "enabled": True,
                    "_comment": "Outreach generation worker settings"
                },
                "enrichment_worker": {
                    "max_concurrent_tasks": 3,
                    "task_timeout": 180,
                    "enabled": True,
                    "_comment": "Contact enrichment worker settings"
                },
                "delivery_worker": {
                    "max_concurrent_tasks": 5,
                    "task_timeout": 120,
                    "enabled": True,
                    "_comment": "Message delivery worker settings"
                }
            },
            "api": {
                "host": "localhost",
                "port": 8000,
                "debug": False,
                "cors_enabled": True,
                "_comment": "API server configuration"
            },
            "security": {
                "jwt_secret_key": "CHANGE-THIS-TO-SECURE-KEY",
                "api_rate_limit": 100,
                "session_timeout": 3600,
                "_comment": "Security configuration - change secret key in production"
            }
        }

    def _get_env_content(self, config: Dict[str, Any]) -> str:
        """Get environment file content"""
        return f"""# Outreach Engine Environment Configuration
# Generated on: {datetime.utcnow().isoformat()}

# Database Configuration
DATABASE_TYPE={config.get('database', {}).get('type', 'sqlite')}
DATABASE_PATH={config.get('database', {}).get('path', 'outreach_engine.db')}

# API Configuration
API_HOST={config.get('api', {}).get('host', 'localhost')}
API_PORT={config.get('api', {}).get('port', 8000)}
API_DEBUG={config.get('api', {}).get('debug', False)}

# Security
JWT_SECRET_KEY={config.get('security', {}).get('jwt_secret_key', 'your-secret-key-here')}
API_RATE_LIMIT={config.get('security', {}).get('api_rate_limit', 100)}

# Logging
LOG_LEVEL={config.get('logging', {}).get('level', 'INFO')}
LOG_FILE={config.get('logging', {}).get('file', 'outreach_engine.log')}

# Worker Configuration
OUTREACH_WORKER_ENABLED={config.get('workers', {}).get('outreach_worker', {}).get('enabled', True)}
ENRICHMENT_WORKER_ENABLED={config.get('workers', {}).get('enrichment_worker', {}).get('enabled', True)}
DELIVERY_WORKER_ENABLED={config.get('workers', {}).get('delivery_worker', {}).get('enabled', True)}
"""

    def _get_database_schema(self, db_type: str) -> str:
        """Get database schema"""
        return f"""-- Outreach Engine Database Schema
-- Database Type: {db_type}
-- Generated on: {datetime.utcnow().isoformat()}

-- Outreach tasks table
CREATE TABLE IF NOT EXISTS outreach_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    recipient_data TEXT,
    sender_data TEXT,
    outreach_content TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contact enrichment table
CREATE TABLE IF NOT EXISTS contact_enrichments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id VARCHAR(255) UNIQUE NOT NULL,
    original_data TEXT,
    enriched_data TEXT,
    enrichment_sources TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Delivery tracking table
CREATE TABLE IF NOT EXISTS delivery_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id VARCHAR(255) UNIQUE NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    delivery_channel VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    delivery_data TEXT,
    error_message TEXT,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metadata TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

    def _get_startup_script_content(self, config: Dict[str, Any]) -> str:
        """Get startup script content"""
        return f"""#!/bin/bash
# Outreach Engine Startup Script
# Generated on: {datetime.utcnow().isoformat()}

echo "🚀 Starting Outreach Engine..."

# Set environment variables
export PYTHONPATH="{self.project_root}"
cd "{self.outreach_engine_root}"

# Start API server
echo "📡 Starting API server on {config.get('api', {}).get('host', 'localhost')}:{config.get('api', {}).get('port', 8000)}..."
python -m uvicorn api.main:app --host {config.get('api', {}).get('host', 'localhost')} --port {config.get('api', {}).get('port', 8000)} {'--reload' if config.get('api', {}).get('debug', False) else ''}

echo "✅ Outreach Engine started successfully!"
"""

    def _get_batch_script_content(self, config: Dict[str, Any]) -> str:
        """Get Windows batch script content"""
        return f"""@echo off
REM Outreach Engine Startup Script for Windows
REM Generated on: {datetime.utcnow().isoformat()}

echo 🚀 Starting Outreach Engine...

REM Set environment variables
set PYTHONPATH={self.project_root}
cd /d "{self.outreach_engine_root}"

REM Start API server
echo 📡 Starting API server on {config.get('api', {}).get('host', 'localhost')}:{config.get('api', {}).get('port', 8000)}...
python -m uvicorn api.main:app --host {config.get('api', {}).get('host', 'localhost')} --port {config.get('api', {}).get('port', 8000)} {'--reload' if config.get('api', {}).get('debug', False) else ''}

echo ✅ Outreach Engine started successfully!
pause
"""

    def _get_requirements_content(self) -> str:
        """Get requirements.txt content"""
        return """# Outreach Engine Dependencies
# Core Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0

# Database
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# Async Support
asyncio>=3.4.3
aiofiles>=23.2.0

# HTTP Client
httpx>=0.25.0
requests>=2.31.0

# Email Support
aiosmtplib>=3.0.0
email-validator>=2.1.0

# Data Processing
pandas>=2.1.0
numpy>=1.24.0

# Authentication & Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# Monitoring & Logging
structlog>=23.2.0
prometheus-client>=0.19.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# Development
black>=23.11.0
ruff>=0.1.0
mypy>=1.7.0

# Utilities
python-dotenv>=1.0.0
click>=8.1.0
rich>=13.7.0
"""

def main():
    """Main setup CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Outreach Engine Setup Utility"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup Outreach Engine environment')
    setup_parser.add_argument('--config', help='Configuration file path')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate Outreach Engine setup')

    # Config template command
    config_parser = subparsers.add_parser('config-template', help='Create configuration template')
    config_parser.add_argument('--output', required=True, help='Output file path')

    # Dependencies command
    deps_parser = subparsers.add_parser('install-deps', help='Install dependencies')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Create setup instance
    setup = OutreachEngineSetup()

    # Execute command
    if args.command == 'setup':
        setup.setup_environment(args.config)
    elif args.command == 'validate':
        setup.validate_setup()
    elif args.command == 'config-template':
        setup.create_config_template(args.output)
    elif args.command == 'install-deps':
        setup.install_dependencies()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
