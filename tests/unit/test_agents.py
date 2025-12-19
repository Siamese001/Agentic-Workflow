import os
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add the scripts directory to the path to import canon_validator_agentic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from canon_validator_agentic import Historian, TheCartographer, ValidationContext


@pytest.fixture
def async_context():
    ctx = ValidationContext()
    ctx.redis = AsyncMock() # Mock Async Redis
    ctx.pinecone = MagicMock()
    ctx._client = MagicMock() # Gemini - set private attribute
    # Mock Gemini embedding response
    ctx._client.models.embed_content = AsyncMock(return_value=MagicMock(embeddings=[MagicMock(values=[0.1, 0.2])]))
    return ctx

@pytest.fixture
def mock_context():
    ctx = ValidationContext()
    # Mock the Tri-Brain clients to avoid connection errors
    ctx.redis = MagicMock()
    ctx.pinecone = MagicMock()
    ctx._client = MagicMock() # Gemini - set private attribute
    # Mock Gemini embedding response
    ctx._client.models.embed_content = AsyncMock(return_value=MagicMock(embeddings=[MagicMock(values=[0.1, 0.2])]))
    return ctx

@pytest.mark.asyncio
async def test_historian_skips_cached_files(async_context):
    """Historian should signal SKIP if Redis hash matches."""
    agent = Historian(async_context)

    # Setup a file in the context
    file_path = "agentic_core/engine/logic.py"
    async_context.python_files = [file_path]

    # Mock file hash and saved hash to be the same
    current_hash = "abc123"
    async_context.file_hashes[file_path] = current_hash

    # Mock results to show file previously passed
    key = async_context._get_file_key(file_path)
    async_context.results[key] = {"passed": True, "details": []}

    # Mock calculate_file_hash to return the same hash
    async_context.calculate_file_hash = MagicMock(return_value=current_hash)

    await agent.execute()

    # Verification
    assert file_path in async_context.skip_files
    print("\n   ✅ Historian correctly skipped cached file.")

@pytest.mark.asyncio
async def test_historian_validates_changed_files(async_context):
    """Historian should NOT skip if hash differs."""
    agent = Historian(async_context)

    # Setup a file in the context
    file_path = "agentic_core/engine/logic.py"
    async_context.python_files = [file_path]

    # Mock saved hash to be different
    async_context.file_hashes[file_path] = "old_hash_123"

    # Mock calculate_file_hash to return a new hash
    async_context.calculate_file_hash = MagicMock(return_value="new_hash_456")

    await agent.execute()

    # Verification
    assert file_path not in async_context.skip_files
    print("\n   ✅ Historian correctly flagged changed file for review.")

@pytest.mark.asyncio
async def test_cartographer_handles_disabled_intelligence(async_context):
    """Cartographer should handle disabled intelligence gracefully."""
    agent = TheCartographer(async_context)

    # Setup a modified file
    file_path = "apps_lic/auth/login.py"
    async_context.modified_files = {file_path}

    # Mock file reading
    async_context.read_file = MagicMock(return_value="def login(): pass")

    await agent.execute()

    # Verify that when intelligence is disabled, the agent skips embedding generation
    # The output shows "🧊 Deep Brain unavailable - skipping mapping"
    assert not async_context._client.models.embed_content.called
    print("\n   ✅ Cartographer handled disabled intelligence correctly.")
