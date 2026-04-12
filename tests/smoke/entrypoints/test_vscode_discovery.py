"""VS Code Test Discovery Trigger - Simple test to force discovery"""


def test_simple_math():
    """Basic math test"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """String operation test"""
    assert "hello".upper() == "HELLO"
    assert "world".lower() == "world"


def test_list_operations():
    """List operation test"""
    items = [1, 2, 3]
    assert len(items) == 3
    assert items[0] == 1


class TestSampleClass:
    """Sample test class for VS Code discovery"""

    def test_class_method(self):
        """Test method in class"""
        assert self is not None

    def test_boolean_logic(self):
        """Boolean logic test"""
        assert True is True
        assert False is False
        assert False is not True
