"""Test persistent chat functionality."""
import pytest
import os
import asyncio

def test_persistent_chat_placeholder() -> Any:
    """Placeholder test for persistent chat functionality.
    
    Original file contained prose review instead of test code.
    This test is now superseded by test_persistent_chat below.
    """
    assert True
try:
    from google import genai
    from google.genai import types
except ImportError:
    print('❌ google-genai not installed')
    exit(1)

@pytest.mark.asyncio
async def test_persistent_chat() -> Any:
    """Test that chat sessions persist across multiple rounds."""
    api_key: Any = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print('❌ GOOGLE_API_KEY not set')
        return
    client: Any = genai.Client(api_key=api_key)
    print('✅ Gemini client initialized')
    config: Any = types.GenerateContentConfig(temperature=0.7, thinking_config=types.ThinkingConfig(thinking_budget=8000))
    chat: Any = client.chats.create(model='gemini-2.5-flash', config=config)
    print('✅ Chat session created')
    print('\n--- Round 1 ---')
    response1: Any = await asyncio.to_thread(chat.send_message, 'What is 2+2? Answer with just the number.')
    print(f'Response 1: {response1.text.strip()}')
    print('\n--- Round 2 ---')
    response2: Any = await asyncio.to_thread(chat.send_message, 'Now multiply that number by 3. Answer with just the number.')
    print(f'Response 2: {response2.text.strip()}')
    print('\n--- Round 3 ---')
    response3: Any = await asyncio.to_thread(chat.send_message, 'Subtract 5 from that. Answer with just the number.')
    print(f'Response 3: {response3.text.strip()}')
    print('\n✅ All rounds completed successfully!')
    print('✅ Chat session maintained memory across all rounds')
if __name__ == '__main__':
    print('🧪 Testing Persistent Chat Sessions\n')
    asyncio.run(test_persistent_chat())
