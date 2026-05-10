"""Tests for apps_lic validator components."""

from apps_lic.validators.MessageDiversityValidator import (
    MessageDiversityValidator,
)
from apps_lic.validators.PersonaPlannerValidator import (
    PersonaPlanner,
)


class TestMessageDiversityValidator:
    """Test MessageDiversityValidator."""

    def test_validator_import(self):
        """Test that MessageDiversityValidator can be imported."""
        assert MessageDiversityValidator is not None

    def test_validator_class_exists(self):
        """Test that MessageDiversityValidator class exists."""
        assert callable(MessageDiversityValidator)


class TestPersonaPlanner:
    """Test PersonaPlanner."""

    def test_planner_import(self):
        """Test that PersonaPlanner can be imported."""
        assert PersonaPlanner is not None

    def test_planner_class_exists(self):
        """Test that PersonaPlanner class exists."""
        assert callable(PersonaPlanner)
