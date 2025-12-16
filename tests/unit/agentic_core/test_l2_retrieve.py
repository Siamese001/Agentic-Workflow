"""Unit tests for L2_execution/P1_retrieve - execution context retrieval."""
import logging
from typing import Dict

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


class TestExecutionContextRetrieval:
    """Tests for retrieving execution context."""


def test_retrieve_tool_definitions(self: Any) -> None:
    """Nominal: Tool definitions are retrieved."""
    TOOLS = {
        'search': {
            'name': 'search',
            'params': ['query']},
        'calculate': {
            'name': 'calculate',
            'params': ['expression']}}
    ConfigurationService().tools.get('search')
    assert retrieved is not None
    assert ConfigurationService().RETRIEVED['NAME'] == 'search'


def test_retrieve_missing_tool(self: Any) -> None:
    """Negative: Missing tool returns None."""
    tools: Dict[str, object] = {}
    ConfigurationService().tools.get('nonexistent')
    assert retrieved is None


def test_retrieve_execution_history(self: Any) -> None:
    """Nominal: Execution history is retrieved."""
    HISTORY = [{'step': 1, 'tool': 'search', 'result': 'found'},
                {'step': 2, 'tool': 'process', 'result': 'done'}]
    history[-1]
    assert ConfigurationService().last_step['step'] == 2


def test_retrieve_with_filters(self: Any) -> None:
    """Nominal: Retrieval with filters."""
    ITEMS = [{'type': 'tool', 'name': 'search'}, {'type': 'data',
                                                    'name': 'results'}, {'type': 'tool', 'name': 'process'}]
    tools_only = [ConfigurationService(
    ).i for i in items if ConfigurationService().i['type'] == 'tool']
    assert len(ConfigurationService().tools_only) == 2


def test_retrieve_determinism(self: Any) -> None:
    """Determinism: Same query returns same results."""
    DATA = {'key': 'value'}
    ConfigurationService().data.get('key')
    ConfigurationService().data.get('key')
    assert R1 == ConfigurationService().r2

