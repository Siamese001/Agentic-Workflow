"""Unit Tests for Dependency Injection System

Tests DI container functionality and proper service injection
across all layers to maintain L1-L5 atomicity.
"""

import pytest
from unittest.mock import Mock, patch

from core.di_container import (
    SimpleDIContainer,
    get_container,
    register_service,
    get_service,
    initialize_default_services,
    inject_dependencies
)
from l4.pinecone_adapter import PineconeAdapter, PineconeConfig
from l5.policy import SafetyEngine


class TestSimpleDIContainer:
    """Test cases for dependency injection container."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.container = SimpleDIContainer()
    
    def test_register_and_get_service(self):
        """Test registering and retrieving services."""
        # Register a mock service
        mock_service = Mock()
        self.container.register(Mock, mock_service)
        
        # Retrieve the service
        retrieved = self.container.get(Mock)
        
        assert retrieved is mock_service
    
    def test_get_nonexistent_service(self):
        """Test getting a service that doesn't exist."""
        result = self.container.get(Mock)
        assert result is None
    
    def test_clear_services(self):
        """Test clearing all services."""
        # Register services
        self.container.register(Mock, Mock())
        self.container.register(str, "test")
        
        # Clear services
        self.container.clear()
        
        # Should be empty
        assert self.container.get(Mock) is None
        assert self.container.get(str) is None
    
    def test_duplicate_registration_raises_error(self):
        """Test that registering the same service type twice raises error."""
        self.container.register(Mock, Mock())
        
        with pytest.raises(Exception):  # Should raise some error
            self.container.register(Mock, Mock())


class TestGlobalDIContainer:
    """Test cases for global DI container functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Clear global container before each test
        container = get_container()
        container.clear()
    
    def test_global_register_and_get(self):
        """Test global register and get functions."""
        mock_service = Mock()
        
        # Register globally
        register_service(Mock, mock_service)
        
        # Get globally
        retrieved = get_service(Mock)
        
        assert retrieved is mock_service
    
    def test_initialize_default_services(self):
        """Test initialization of default services."""
        initialize_default_services()
        
        container = get_container()
        
        # Should have PineconeAdapter and SafetyEngine
        assert container.get(PineconeAdapter) is not None
        assert container.get(SafetyEngine) is not None


class TestDependencyInjection:
    """Test cases for dependency injection in execution contexts."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Initialize default services
        initialize_default_services()
        
        # Create clean mock context
        self.ctx = Mock()
        self.ctx.user_id = "test_user"
        self.ctx.session_id = "test_session"
        # Remove any existing attributes that might interfere
        for attr in ['pinecone_adapter', 'safety_engine', 'state_manager']:
            if hasattr(self.ctx, attr):
                delattr(self.ctx, attr)
    
    def test_inject_dependencies_adds_services(self):
        """Test that inject_dependencies adds services to context."""
        # Ensure context doesn't have services
        assert not hasattr(self.ctx, 'pinecone_adapter')
        assert not hasattr(self.ctx, 'safety_engine')
        
        # Inject dependencies
        updated_ctx = inject_dependencies(self.ctx)
        
        # Should have services added
        assert hasattr(updated_ctx, 'pinecone_adapter')
        assert hasattr(updated_ctx, 'safety_engine')
        assert isinstance(updated_ctx.pinecone_adapter, PineconeAdapter)
        assert isinstance(updated_ctx.safety_engine, SafetyEngine)
    
    def test_inject_dependencies_preserves_existing(self):
        """Test that inject_dependencies preserves existing services."""
        # Add existing service
        existing_adapter = Mock(spec=PineconeAdapter)
        self.ctx.pinecone_adapter = existing_adapter
        
        # Inject dependencies
        updated_ctx = inject_dependencies(self.ctx)
        
        # Should preserve existing service
        assert updated_ctx.pinecone_adapter is existing_adapter
        assert hasattr(updated_ctx, 'safety_engine')


class TestLayerDIIntegration:
    """Test DI integration across all layers - simplified."""
    
    def setup_method(self):
        """Set up test fixtures."""
        initialize_default_services()
    
    def test_pinecone_adapter_di_interface(self):
        """Test that PineconeAdapter provides DI-compatible interface."""
        from l4.pinecone_adapter import PineconeConfig
        
        config = PineconeConfig(
            api_key="test_key",
            index_name="test_index"
        )
        adapter = PineconeAdapter(config)
        
        # Should have retrieve_evidence method for DI
        assert hasattr(adapter, 'retrieve_evidence')
        assert callable(getattr(adapter, 'retrieve_evidence'))
    
    def test_safety_engine_di_interface(self):
        """Test that SafetyEngine provides DI-compatible interface."""
        engine = SafetyEngine()
        
        # Should have evaluate method for DI
        assert hasattr(engine, 'evaluate')
        assert callable(getattr(engine, 'evaluate'))


class TestDIAtomicityCompliance:
    """Test that DI maintains L1-L5 atomicity constraints."""
    
    def test_no_direct_imports_in_l2(self):
        """Test that L2 doesn't directly import services."""
        import l2.execution
        
        # Should import from DI container, not direct services
        source_lines = []
        try:
            with open('l2/execution.py', 'r') as f:
                source_lines = f.readlines()
        except FileNotFoundError:
            # Skip if file not found in test environment
            return
        
        source = ''.join(source_lines)
        
        # Should contain DI imports
        assert 'from core.di_container import' in source
        
        # Should not contain direct Pinecone imports for business logic
        # (except for type hints)
        business_logic_imports = [
            'from pinecone import',
            'import pinecone'
        ]
        
        for imp in business_logic_imports:
            # Allow in comments or type hints only
            lines_with_imp = [line for line in source_lines if imp in line and not line.strip().startswith('#')]
            assert len(lines_with_imp) == 0, f"Found direct import: {imp}"
    
    def test_no_direct_imports_in_l3(self):
        """Test that L3 doesn't directly import services."""
        import l3
        
        # Should import from DI container
        source_lines = []
        try:
            with open('l3/__init__.py', 'r') as f:
                source_lines = f.readlines()
        except FileNotFoundError:
            return
        
        source = ''.join(source_lines)
        assert 'from core.di_container import' in source


if __name__ == "__main__":
    pytest.main([__file__])
