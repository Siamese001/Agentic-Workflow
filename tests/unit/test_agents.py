import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from unittest.mock import AsyncMock, MagicMock
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from canon_validator_agentic import Historian, TheCartographer, ValidationContext

@pytest.fixture
def async_context() -> Any:
    """Brief description of functionality and purpose."""
    ctx: Any = ValidationContext()
    ctx.redis = AsyncMock()
    ctx.pinecone = MagicMock()
    ctx._client = MagicMock()
    ctx._client.models.embed_content = AsyncMock(return_value=MagicMock(embeddings=[MagicMock(values=[0.1, 0.2])]))
    return ctx

@pytest.fixture
def mock_context() -> Any:
    """Brief description of functionality and purpose."""
    ctx: Any = ValidationContext()
    ctx.redis = MagicMock()
    ctx.pinecone = MagicMock()
    ctx._client = MagicMock()
    ctx._client.models.embed_content = AsyncMock(return_value=MagicMock(embeddings=[MagicMock(values=[0.1, 0.2])]))
    return ctx

@pytest.mark.asyncio
async def test_historian_skips_cached_files(async_context: Any) -> Any:
    """Historian should signal SKIP if Redis hash matches."""
    agent: Any = Historian(async_context)
    file_path: Any = 'agentic_core/engine/logic.py'
    async_context.python_files = [file_path]
    current_hash: Any = 'abc123'
    async_context.file_hashes[file_path] = current_hash
    key: Any = async_context._get_file_key(file_path)
    async_context.results[key] = {'passed': True, 'details': []}
    async_context.calculate_file_hash = MagicMock(return_value=current_hash)
    await agent.execute()
    assert file_path in async_context.skip_files
    print('\n   ✅ Historian correctly skipped cached file.')

@pytest.mark.asyncio
async def test_historian_validates_changed_files(async_context: Any) -> Any:
    """Historian should NOT skip if hash differs."""
    agent: Any = Historian(async_context)
    file_path: Any = 'agentic_core/engine/logic.py'
    async_context.python_files = [file_path]
    async_context.file_hashes[file_path] = 'old_hash_123'
    async_context.calculate_file_hash = MagicMock(return_value='new_hash_456')
    await agent.execute()
    assert file_path not in async_context.skip_files
    print('\n   ✅ Historian correctly flagged changed file for review.')

@pytest.mark.asyncio
async def test_cartographer_handles_disabled_intelligence(async_context: Any) -> Any:
    """Cartographer should handle disabled intelligence gracefully."""
    agent: Any = TheCartographer(async_context)
    file_path: Any = 'apps_lic/auth/login.py'
    async_context.modified_files = {file_path}
    async_context.read_file = MagicMock(return_value='def login(): pass')
    await agent.execute()
    assert not async_context._client.models.embed_content.called
    print('\n   ✅ Cartographer handled disabled intelligence correctly.')
