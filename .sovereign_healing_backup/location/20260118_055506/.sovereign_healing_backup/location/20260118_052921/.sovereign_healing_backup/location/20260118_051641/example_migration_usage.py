#!/usr/bin/env python3
"""
Example usage of MigrationMixin in agent implementations
"""

import asyncio
import logging
from agentic_core.utils.core_extensions.migration_mixin import MigrationMixin, MigrationError

class MockBaseAgent:
    """Mock base agent to avoid circular imports"""
    def __init__(self):
        self.name = "MockAgent"

class ConfigurationAgent(MigrationMixin, MockBaseAgent):
    """
    Example configuration agent with schema evolution support
    """
    
    def __init__(self):
        super().__init__()
        self._schema_version = "3.0"
        self.config = {}
    
    async def load_config(self, config_data: dict, version: str = None):
        """Load configuration with automatic migration"""
        if version is None:
            version = config_data.get("_version", "1.0")
        
        try:
            migrated_config = await self.migrate_data(config_data, from_version=version)
            self.config = migrated_config
            self.config["_version"] = self._schema_version
            return self.config
        except MigrationError as e:
            self.logger.error(f"Configuration migration failed: {e}")
            raise
    
    async def migrate_v1_0_to_next(self, data):
        """Migrate from v1.0 to v2.0: Rename fields and add new structure"""
        # v1.0 had flat config structure
        old_config = data.copy()
        
        # Create new nested structure
        new_data = {
            "database": {
                "host": old_config.pop("db_host", "localhost"),
                "port": old_config.pop("db_port", 5432),
                "name": old_config.pop("db_name", "default")
            },
            "api": {
                "key": old_config.pop("api_key", ""),
                "timeout": old_config.pop("timeout", 30)
            },
            "features": old_config.pop("features", []),
            "_new_version_id": "2.0"
        }
        
        return new_data
    
    async def migrate_v2_0_to_next(self, data):
        """Migrate from v2.0 to v3.0: Add security and monitoring"""
        # Add security section
        data["security"] = {
            "encryption": {
                "enabled": True,
                "algorithm": "AES-256"
            },
            "authentication": {
                "method": "token",
                "token_expiry": 3600
            }
        }
        
        # Add monitoring section
        data["monitoring"] = {
            "enabled": True,
            "metrics": ["performance", "errors", "usage"],
            "alert_threshold": 0.95
        }
        
        # Update API section with new fields
        data["api"]["rate_limit"] = {
            "requests_per_minute": 100,
            "burst_size": 150
        }
        
        data["_new_version_id"] = "3.0"
        return data

class DataSchemaAgent(MigrationMixin, MockBaseAgent):
    """
    Example data processing agent with schema evolution
    """
    
    def __init__(self):
        super().__init__()
        self._schema_version = "2.1"
        self.data_schema = {}
    
    async def migrate_v1_0_to_next(self, data):
        """Migrate from v1.0 to v2.0: Restructure data schema"""
        # v1.0 had simple key-value pairs
        new_data = {
            "metadata": {
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "version": "2.0"
            },
            "content": {
                "title": data.get("title"),
                "body": data.get("content"),
                "tags": data.get("tags", [])
            },
            "settings": {
                "public": data.get("public", False),
                "featured": data.get("featured", False)
            },
            "_new_version_id": "2.0"
        }
        
        return new_data
    
    async def migrate_v2_0_to_next(self, data):
        """Migrate from v2.0 to v2.1: Add analytics and SEO"""
        # Add analytics section
        data["analytics"] = {
            "views": 0,
            "shares": 0,
            "engagement_score": 0.0
        }
        
        # Add SEO metadata
        data["seo"] = {
            "description": data["content"]["body"][:160] if data["content"]["body"] else "",
            "keywords": data["content"]["tags"],
            "canonical_url": ""
        }
        
        # Update content with new fields
        data["content"]["excerpt"] = data["content"]["body"][:200] if data["content"]["body"] else ""
        
        data["_new_version_id"] = "2.1"
        return data

class MultiStepMigrationAgent(MigrationMixin, MockBaseAgent):
    """
    Example agent demonstrating multi-step migration
    """
    
    def __init__(self):
        super().__init__()
        self._schema_version = "3.0"
    
    async def migrate_v1_0_to_next(self, data):
        """Step 1: Basic restructuring"""
        data["version"] = "2.0"
        data["structure"] = {"level": "basic"}
        data["_new_version_id"] = "2.0"
        return data
    
    async def migrate_v2_0_to_next(self, data):
        """Step 2: Add advanced features"""
        data["structure"]["level"] = "advanced"
        data["features"] = ["feature_a", "feature_b"]
        data["_new_version_id"] = "3.0"
        return data

class ErrorHandlingAgent(MigrationMixin, MockBaseAgent):
    """
    Example agent demonstrating error handling in migrations
    """
    
    def __init__(self):
        super().__init__()
        self._schema_version = "2.0"
    
    async def migrate_v1_0_to_next(self, data):
        """Migration that might fail"""
        if "invalid_data" in data:
            raise ValueError("Cannot migrate invalid data")
        
        data["validated"] = True
        data["_new_version_id"] = "2.0"
        return data

async def demonstrate_basic_migration():
    """Demonstrate basic configuration migration"""
    print("\n1. Basic Configuration Migration:")
    print("-" * 50)
    
    agent = ConfigurationAgent()
    
    # v1.0 configuration
    old_config = {
        "db_host": "localhost",
        "db_port": 5432,
        "db_name": "myapp",
        "api_key": "secret123",
        "timeout": 60,
        "features": ["auth", "logging"]
    }
    
    print(f"  📦 Original config (v1.0): {len(old_config)} fields")
    
    # Migrate to current version
    migrated_config = await agent.load_config(old_config, version="1.0")
    
    print(f"  ✅ Migrated config (v{agent._schema_version}):")
    print(f"     - Database section: {len(migrated_config['database'])} fields")
    print(f"     - API section: {len(migrated_config['api'])} fields")
    print(f"     - Security section: {len(migrated_config['security'])} fields")
    print(f"     - Monitoring section: {len(migrated_config['monitoring'])} fields")

async def demonstrate_multi_step_migration():
    """Demonstrate multi-step migration"""
    print("\n2. Multi-Step Migration:")
    print("-" * 50)
    
    agent = MultiStepMigrationAgent()
    
    # Start with v1.0 data
    data = {"initial": "data"}
    print(f"  📦 Starting with v1.0 data")
    
    # Migrate through multiple steps
    result = await agent.migrate_data(data, from_version="1.0")
    
    print(f"  ✅ Final result (v{agent._schema_version}):")
    print(f"     - Structure level: {result['structure']['level']}")
    print(f"     - Features: {result['features']}")
    print(f"     - Migration history: {len(agent._migration_history)} steps")
    
    for i, step in enumerate(agent._migration_history):
        print(f"       Step {i+1}: {step['from']} -> {step['to']}")

async def demonstrate_data_schema_migration():
    """Demonstrate data schema migration"""
    print("\n3. Data Schema Migration:")
    print("-" * 50)
    
    agent = DataSchemaAgent()
    
    # v1.0 data
    old_data = {
        "title": "My Article",
        "content": "This is the content of my article...",
        "tags": ["python", "programming"],
        "public": True,
        "created_at": "2026-01-13T10:00:00Z"
    }
    
    print(f"  📦 Original data (v1.0): {len(old_data)} fields")
    
    # Migrate to current version
    migrated_data = await agent.migrate_data(old_data, from_version="1.0")
    
    print(f"  ✅ Migrated data (v{agent._schema_version}):")
    print(f"     - Metadata section: {len(migrated_data['metadata'])} fields")
    print(f"     - Content section: {len(migrated_data['content'])} fields")
    print(f"     - Settings section: {len(migrated_data['settings'])} fields")
    print(f"     - Analytics section: {len(migrated_data['analytics'])} fields")
    print(f"     - SEO section: {len(migrated_data['seo'])} fields")

async def demonstrate_error_handling():
    """Demonstrate migration error handling"""
    print("\n4. Migration Error Handling:")
    print("-" * 50)
    
    agent = ErrorHandlingAgent()
    
    # Valid data - should succeed
    try:
        valid_data = {"valid": "data"}
        result = await agent.migrate_data(valid_data, from_version="1.0")
        print(f"  ✅ Valid data migrated successfully")
        print(f"     - Validated: {result['validated']}")
    except MigrationError as e:
        print(f"  ❌ Unexpected error: {e}")
    
    # Invalid data - should fail
    try:
        invalid_data = {"invalid_data": "true"}
        result = await agent.migrate_data(invalid_data, from_version="1.0")
        print(f"  ❌ Should have failed but didn't")
    except MigrationError as e:
        print(f"  ✅ Invalid data correctly rejected: {e}")

async def demonstrate_version_compatibility():
    """Demonstrate version compatibility checking"""
    print("\n5. Version Compatibility:")
    print("-" * 50)
    
    agent = ConfigurationAgent()
    
    # Same version - no migration needed
    current_version_data = {"_version": "3.0", "test": "data"}
    result = await agent.migrate_data(current_version_data, from_version="3.0")
    print(f"  ✅ Same version (3.0 -> 3.0): No migration needed")
    
    # Different version - migration needed
    old_version_data = {"_version": "1.0", "db_host": "localhost"}
    result = await agent.migrate_data(old_version_data, from_version="1.0")
    print(f"  ✅ Different version (1.0 -> 3.0): Migration performed")
    
    # Check migration history
    print(f"  📊 Migration history: {len(agent._migration_history)} steps")
    for step in agent._migration_history:
        print(f"     {step['from']} -> {step['to']} at {step['timestamp']}")

async def demonstrate_backward_compatibility():
    """Demonstrate backward compatibility warnings"""
    print("\n6. Backward Compatibility:")
    print("-" * 50)
    
    agent = ConfigurationAgent()
    
    # Load very old configuration
    very_old_config = {
        "db_host": "old-server",
        "api_key": "old-key",
        "_version": "1.0"
    }
    
    try:
        result = await agent.load_config(very_old_config, version="1.0")
        print(f"  ✅ Successfully migrated from v1.0 to v{agent._schema_version}")
        print(f"  📋 Migration path: v1.0 -> v2.0 -> v3.0")
        
        # Show what changed
        print(f"  🔄 Changes made:")
        print(f"     - Database: Flat -> Nested structure")
        print(f"     - API: Simple -> With rate limiting")
        print(f"     - Security: Added encryption settings")
        print(f"     - Monitoring: Added metrics and alerts")
        
    except MigrationError as e:
        print(f"  ❌ Migration failed: {e}")

async def main():
    """Run all demonstrations"""
    print("=" * 60)
    print("MIGRATION MIXIN USAGE DEMONSTRATIONS")
    print("=" * 60)
    
    await demonstrate_basic_migration()
    await demonstrate_multi_step_migration()
    await demonstrate_data_schema_migration()
    await demonstrate_error_handling()
    await demonstrate_version_compatibility()
    await demonstrate_backward_compatibility()
    
    print("\n" + "=" * 60)
    print("✅ ALL DEMONSTRATIONS COMPLETE")
    print("=" * 60)
    
    print("\nKey Features Demonstrated:")
    print("• Automatic schema version detection")
    print("• Step-by-step migration execution")
    print("• Multi-version migration support")
    print("• Error handling and validation")
    print("• Migration history tracking")
    print("• Backward compatibility support")
    print("• Configuration and data schema evolution")

if __name__ == "__main__":
    asyncio.run(main())
