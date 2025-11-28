import subprocess
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.mock
def test_no_todo_or_mock_comments():
    result = subprocess.run(["grep", "-R", "TODO", "agentic_workflow/"], capture_output=True, text=True)
    assert "TODO" not in result.stdout


@pytest.mark.mock
def test_no_identity_function_returns():
    result = subprocess.run(["grep", "-R", "return input", "agentic_workflow/"], capture_output=True, text=True)
    assert "return input" not in result.stdout


@pytest.mark.asyncio
async def test_mock_llm_client_triggers_idempotency(mock_workflow_context, mock_llm_client):
    cached_response = {"content": "cached", "usage": {}}
    mock_workflow_context.cache_manager.get_llm_cache = AsyncMock(return_value=cached_response)

    with patch.object(mock_llm_client, "_run_idempotency_check", new_callable=AsyncMock) as run_check:
        await mock_llm_client.chat_completion_async(
            messages=[{"role": "user", "content": "hello"}],
            temperature=0.2,
        )

    run_check.assert_called_once()
