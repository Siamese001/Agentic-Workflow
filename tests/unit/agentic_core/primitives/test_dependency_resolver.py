"""Tests for DynamicLoader."""

from agentic_core.utils.dependency_resolver import DynamicLoader


class TestDynamicLoader:
    """Tests for DynamicLoader class."""

    def setup_method(self):
        """Clear cache before each test."""
        DynamicLoader.clear_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        DynamicLoader.clear_cache()

    def test_load_class_success(self):
        """Test loading a class that exists."""
        # Load a class from the standard library
        cls = DynamicLoader.load_class("dataclasses", "dataclass")
        assert cls is not None

    def test_load_class_module_not_found(self):
        """Test loading from non-existent module."""
        cls = DynamicLoader.load_class("non_existent_module", "SomeClass")
        assert cls is None

    def test_load_class_class_not_found(self):
        """Test loading non-existent class from valid module."""
        cls = DynamicLoader.load_class("dataclasses", "NonExistentClass")
        assert cls is None

    def test_load_class_caching(self):
        """Test that loaded classes are cached."""
        # First load
        cls1 = DynamicLoader.load_class("dataclasses", "dataclass")
        # Second load should return cached
        cls2 = DynamicLoader.load_class("dataclasses", "dataclass")
        assert cls1 is cls2

    def test_load_implementation_unknown_protocol(self):
        """Test loading unknown protocol returns None."""
        impl = DynamicLoader.load_implementation("unknown_protocol")
        assert impl is None

    def test_load_implementation_registered_protocol(self):
        """Test loading registered protocol."""
        # Register a test implementation
        DynamicLoader.register_implementation(
            protocol_name="test_protocol",
            module_path="dataclasses",
            class_name="dataclass",
        )

        impl = DynamicLoader.load_implementation("test_protocol")
        assert impl is not None

    def test_create_instance_unknown_protocol(self):
        """Test creating instance for unknown protocol returns None."""
        instance = DynamicLoader.create_instance("unknown_protocol")
        assert instance is None

    def test_create_instance_singleton(self):
        """Test singleton behavior for instances."""
        # Register a simple class that can be instantiated
        DynamicLoader.register_implementation(
            protocol_name="test_singleton",
            module_path="collections",
            class_name="OrderedDict",
        )

        instance1 = DynamicLoader.create_instance("test_singleton", singleton=True)
        instance2 = DynamicLoader.create_instance("test_singleton", singleton=True)
        assert instance1 is instance2

    def test_create_instance_non_singleton(self):
        """Test non-singleton creates new instances."""
        DynamicLoader.register_implementation(
            protocol_name="test_non_singleton",
            module_path="collections",
            class_name="OrderedDict",
        )

        instance1 = DynamicLoader.create_instance("test_non_singleton", singleton=False)
        instance2 = DynamicLoader.create_instance("test_non_singleton", singleton=False)
        assert instance1 is not instance2

    def test_clear_cache(self):
        """Test clearing all caches."""
        # Load something to populate cache
        DynamicLoader.load_class("dataclasses", "dataclass")
        DynamicLoader.register_implementation(
            protocol_name="test_clear",
            module_path="collections",
            class_name="OrderedDict",
        )
        DynamicLoader.create_instance("test_clear", singleton=True)

        # Verify caches are populated
        assert len(DynamicLoader._cache) > 0 or len(DynamicLoader._instance_cache) > 0

        # Clear and verify
        DynamicLoader.clear_cache()
        assert len(DynamicLoader._cache) == 0
        assert len(DynamicLoader._instance_cache) == 0

    def test_clear_instance_cache_specific(self):
        """Test clearing specific instance from cache."""
        DynamicLoader.register_implementation(
            protocol_name="test_clear_1",
            module_path="collections",
            class_name="OrderedDict",
        )
        DynamicLoader.register_implementation(
            protocol_name="test_clear_2",
            module_path="collections",
            class_name="OrderedDict",
        )

        DynamicLoader.create_instance("test_clear_1", singleton=True)
        DynamicLoader.create_instance("test_clear_2", singleton=True)

        assert "test_clear_1" in DynamicLoader._instance_cache
        assert "test_clear_2" in DynamicLoader._instance_cache

        DynamicLoader.clear_instance_cache("test_clear_1")

        assert "test_clear_1" not in DynamicLoader._instance_cache
        assert "test_clear_2" in DynamicLoader._instance_cache

    def test_clear_instance_cache_all(self):
        """Test clearing all instances from cache."""
        DynamicLoader.register_implementation(
            protocol_name="test_clear_all_1",
            module_path="collections",
            class_name="OrderedDict",
        )
        DynamicLoader.register_implementation(
            protocol_name="test_clear_all_2",
            module_path="collections",
            class_name="OrderedDict",
        )

        DynamicLoader.create_instance("test_clear_all_1", singleton=True)
        DynamicLoader.create_instance("test_clear_all_2", singleton=True)

        DynamicLoader.clear_instance_cache()

        assert len(DynamicLoader._instance_cache) == 0

    def test_register_implementation(self):
        """Test registering a custom implementation."""
        DynamicLoader.register_implementation(
            protocol_name="custom_protocol",
            module_path="collections",
            class_name="Counter",
        )

        assert "custom_protocol" in DynamicLoader.IMPLEMENTATION_REGISTRY
        assert DynamicLoader.IMPLEMENTATION_REGISTRY["custom_protocol"]["module"] == "collections"
        assert DynamicLoader.IMPLEMENTATION_REGISTRY["custom_protocol"]["class"] == "Counter"

    def test_register_implementation_clears_cache(self):
        """Test that registering clears related cache entries."""
        # First register and create instance
        DynamicLoader.register_implementation(
            protocol_name="test_reregister",
            module_path="collections",
            class_name="OrderedDict",
        )
        DynamicLoader.create_instance("test_reregister", singleton=True)

        # Re-register with different class
        DynamicLoader.register_implementation(
            protocol_name="test_reregister",
            module_path="collections",
            class_name="Counter",
        )

        # Instance cache should be cleared
        assert "test_reregister" not in DynamicLoader._instance_cache

    def test_is_available(self):
        """Test checking if implementation is available."""
        # Register valid implementation
        DynamicLoader.register_implementation(
            protocol_name="test_available",
            module_path="collections",
            class_name="OrderedDict",
        )
        assert DynamicLoader.is_available("test_available") is True

        # Check non-existent
        assert DynamicLoader.is_available("non_existent") is False

    def test_get_registered_protocols(self):
        """Test getting list of registered protocols."""
        protocols = DynamicLoader.get_registered_protocols()
        assert isinstance(protocols, list)
        # Should have the default protocols
        assert "verification" in protocols
        assert "detection" in protocols
        assert "review" in protocols
        assert "meta_learning" in protocols


class TestDynamicLoaderDefaultRegistry:
    """Tests for default implementation registry."""

    def test_default_protocols_registered(self):
        """Test that default protocols are registered."""
        expected_protocols = ["verification", "detection", "review", "meta_learning"]
        for protocol in expected_protocols:
            assert protocol in DynamicLoader.IMPLEMENTATION_REGISTRY

    def test_verification_registry_entry(self):
        """Test verification protocol registry entry."""
        entry = DynamicLoader.IMPLEMENTATION_REGISTRY.get("verification")
        assert entry is not None
        assert "module" in entry
        assert "class" in entry
        assert "verification_gate" in entry["module"]
        assert entry["class"] == "VerificationGate"

    def test_detection_registry_entry(self):
        """Test detection protocol registry entry."""
        entry = DynamicLoader.IMPLEMENTATION_REGISTRY.get("detection")
        assert entry is not None
        assert "detection_signal" in entry["module"]

    def test_review_registry_entry(self):
        """Test review protocol registry entry."""
        entry = DynamicLoader.IMPLEMENTATION_REGISTRY.get("review")
        assert entry is not None
        assert "review_queue" in entry["module"]

    def test_meta_learning_registry_entry(self):
        """Test meta_learning protocol registry entry."""
        entry = DynamicLoader.IMPLEMENTATION_REGISTRY.get("meta_learning")
        assert entry is not None
        assert "meta_learning" in entry["module"]
