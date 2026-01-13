#!/usr/bin/env python3
"""
Example usage of SecretsManagementMixin in agent implementations
"""

import os
import asyncio
from agentic_core.utils.core_extensions.secrets_management_mixin import SecretsManagementMixin, SecretAccessError

class MockBaseAgent:
    """Mock base agent to avoid circular imports"""
    def __init__(self):
        self.name = "MockAgent"

class OpenAIAgent(SecretsManagementMixin, MockBaseAgent):
    """
    Example OpenAI API client with secrets management
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = None
    
    async def initialize(self):
        """Initialize API key securely"""
        try:
            self.api_key = await self.get_secret("OPENAI_API_KEY")
            print(f"✅ OpenAI API key retrieved (env: {self._env_context})")
            return True
        except SecretAccessError as e:
            print(f"❌ Failed to retrieve OpenAI API key: {e}")
            return False
    
    async def chat_completion(self, prompt):
        """Make API call with managed secret"""
        if not self.api_key:
            raise SecretAccessError("API key not initialized")
        
        # Simulate API call
        print(f"🤖 Making OpenAI API call with key ending in ...{self.api_key[-4:]}")
        await asyncio.sleep(0.01)
        return f"Response to: {prompt}"

class DatabaseAgent(SecretsManagementMixin, MockBaseAgent):
    """
    Example database agent with multiple secrets
    """
    
    def __init__(self):
        super().__init__()
        self.db_url = None
        self.db_user = None
        self.db_password = None
    
    async def connect(self):
        """Connect to database with managed secrets"""
        try:
            self.db_url = await self.get_secret("DATABASE_URL")
            self.db_user = await self.get_secret("DATABASE_USER")
            self.db_password = await self.get_secret("DATABASE_PASSWORD")
            
            print(f"✅ Database credentials retrieved (env: {self._env_context})")
            print(f"   URL: {self.db_url}")
            print(f"   User: {self.db_user}")
            print(f"   Password: {'*' * len(self.db_password)}")
            
            return True
        except SecretAccessError as e:
            print(f"❌ Failed to retrieve database credentials: {e}")
            return False
    
    async def query(self, sql):
        """Execute database query"""
        if not all([self.db_url, self.db_user, self.db_password]):
            raise SecretAccessError("Database not connected")
        
        print(f"🗄️  Executing query: {sql}")
        await asyncio.sleep(0.01)
        return [{"id": 1, "name": "test"}]

class ExternalServiceAgent(SecretsManagementMixin, MockBaseAgent):
    """
    Example external service agent with fallback values
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = None
        self.webhook_url = None
    
    async def initialize(self):
        """Initialize with fallback values"""
        # Required secret - will fail if missing
        try:
            self.api_key = await self.get_secret("EXTERNAL_API_KEY")
            print(f"✅ External API key retrieved")
        except SecretAccessError as e:
            print(f"❌ Required external API key missing: {e}")
            return False
        
        # Optional secret with fallback
        self.webhook_url = await self.get_secret(
            "WEBHOOK_URL", 
            default="https://default.webhook.example.com"
        )
        print(f"✅ Webhook URL: {self.webhook_url}")
        
        return True
    
    async def call_service(self, data):
        """Call external service"""
        print(f"🌐 Calling external service with key ending in ...{self.api_key[-4:]}")
        print(f"   Webhook: {self.webhook_url}")
        await asyncio.sleep(0.01)
        return {"status": "success", "processed": len(data)}

class MultiEnvironmentAgent(SecretsManagementMixin, MockBaseAgent):
    """
    Example agent demonstrating environment isolation
    """
    
    async def demonstrate_environment_isolation(self):
        """Show how environment context affects secret access"""
        print(f"📍 Current environment: {self._env_context}")
        
        # Try to get environment-specific secrets
        dev_secret = await self.get_secret("DEV_SECRET", default="dev_default")
        prod_secret = await self.get_secret("PROD_SECRET", default="prod_default")
        
        print(f"   DEV_SECRET: {dev_secret}")
        print(f"   PROD_SECRET: {prod_secret}")
        
        # Show audit logging
        print("📋 Audit logs will show environment context for each access")

async def demonstrate_basic_usage():
    """Demonstrate basic secrets management"""
    print("\n1. Basic OpenAI Agent Example:")
    print("-" * 40)
    
    # Set up test environment
    os.environ["OPENAI_API_KEY"] = "sk-test1234567890abcdef"
    
    agent = OpenAIAgent()
    
    # Initialize with secret
    success = await agent.initialize()
    if success:
        # Make API call
        response = await agent.chat_completion("Hello, world!")
        print(f"   Response: {response}")
    
    # Clean up
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

async def demonstrate_database_secrets():
    """Demonstrate database credential management"""
    print("\n2. Database Agent Example:")
    print("-" * 40)
    
    # Set up test environment
    os.environ.update({
        "DATABASE_URL": "postgresql://localhost:5432/testdb",
        "DATABASE_USER": "testuser",
        "DATABASE_PASSWORD": "secretpassword123"
    })
    
    agent = DatabaseAgent()
    
    # Connect with secrets
    success = await agent.connect()
    if success:
        # Execute query
        results = await agent.query("SELECT * FROM users LIMIT 1")
        print(f"   Query results: {results}")
    
    # Clean up
    for key in ["DATABASE_URL", "DATABASE_USER", "DATABASE_PASSWORD"]:
        if key in os.environ:
            del os.environ[key]

async def demonstrate_fallback_values():
    """Demonstrate fallback value handling"""
    print("\n3. External Service Agent with Fallbacks:")
    print("-" * 40)
    
    # Set up test environment (only required secret)
    os.environ["EXTERNAL_API_KEY"] = "ext-key-1234567890"
    
    agent = ExternalServiceAgent()
    
    # Initialize (will use fallback for webhook)
    success = await agent.initialize()
    if success:
        # Call service
        result = await agent.call_service({"data": "test"})
        print(f"   Service result: {result}")
    
    # Clean up
    if "EXTERNAL_API_KEY" in os.environ:
        del os.environ["EXTERNAL_API_KEY"]

async def demonstrate_environment_isolation():
    """Demonstrate environment isolation"""
    print("\n4. Environment Isolation Example:")
    print("-" * 40)
    
    # Test with DEV environment
    os.environ["SOVEREIGN_ENV"] = "DEV"
    os.environ.update({
        "DEV_SECRET": "dev_secret_value",
        "PROD_SECRET": "prod_secret_value"
    })
    
    agent = MultiEnvironmentAgent()
    await agent.demonstrate_environment_isolation()
    
    # Test with PROD environment
    os.environ["SOVEREIGN_ENV"] = "PROD"
    prod_agent = MultiEnvironmentAgent()
    await prod_agent.demonstrate_environment_isolation()
    
    # Clean up
    for key in ["SOVEREIGN_ENV", "DEV_SECRET", "PROD_SECRET"]:
        if key in os.environ:
            del os.environ[key]

async def demonstrate_error_handling():
    """Demonstrate error handling for missing secrets"""
    print("\n5. Error Handling Example:")
    print("-" * 40)
    
    agent = OpenAIAgent()
    
    # Try to initialize without setting environment variable
    success = await agent.initialize()
    if not success:
        print("   ✅ Correctly handled missing secret")
    
    # Try with default value
    default_value = await agent.get_secret("MISSING_KEY", default="default_value")
    print(f"   ✅ Default value: {default_value}")

async def main():
    """Run all demonstrations"""
    print("=" * 60)
    print("SECRETS MANAGEMENT MIXIN USAGE DEMONSTRATIONS")
    print("=" * 60)
    
    await demonstrate_basic_usage()
    await demonstrate_database_secrets()
    await demonstrate_fallback_values()
    await demonstrate_environment_isolation()
    await demonstrate_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ ALL DEMONSTRATIONS COMPLETE")
    print("=" * 60)
    
    print("\nKey Features Demonstrated:")
    print("• Secure secret retrieval from environment variables")
    print("• Access auditing with environment context")
    print("• Fallback value handling for optional secrets")
    print("• Environment isolation (DEV/PROD/STAGING)")
    print("• Error handling for missing secrets")
    print("• Centralized secrets management")

if __name__ == "__main__":
    asyncio.run(main())
