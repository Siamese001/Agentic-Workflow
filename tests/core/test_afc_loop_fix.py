"""
Test that AFC loop is fixed - model should NOT call tools.
This script verifies that configuring a Gemini chat session with `tools=[]`
successfully prevents the model from attempting to call any tools,
even when prompted with a task that might otherwise trigger tool use.
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ Error: 'google-genai' library not installed.")
    print('Please install it using: pip install google-generativeai')
    exit(1)
import pytest
from typing import Any

@pytest.mark.asyncio
async def test_no_tool_calling() -> bool:
    """
    Tests that configuring a chat session with `tools=[]` successfully
    prevents the model from calling tools.

    Returns:
        bool: True if the test passes (no tool calls detected, text response received),
              False otherwise.
    """
    api_key: Any = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print('❌ FAILED: GOOGLE_API_KEY environment variable not set.')
        return False
    client: Any = genai.Client(api_key=api_key)
    print('✅ Gemini client initialized.')
    config: Any = types.GenerateContentConfig(temperature=1.0, thinking_config=types.ThinkingConfig(thinking_budget=8000), tools=[])
    chat: Any = client.chats.create(model='gemini-2.5-flash', config=config)
    print('✅ Chat session created with `tools=[]` configuration.')
    prompt: Any = 'Fix this Python code:\ndef add(a b):\n    return a + b\n\nReturn ONLY the corrected code.'
    print('\n📤 Sending prompt to the model...')
    response: Any = await asyncio.to_thread(chat.send_message, prompt)
    if response.candidates and response.candidates[0].content.parts:
        first_part: Any = response.candidates[0].content.parts[0]
        if hasattr(first_part, 'function_call') and first_part.function_call:
            print(f"❌ FAILED: Model unexpectedly called tool '{first_part.function_call.name}'.")
            print('   This indicates that the `tools=[]` configuration is not working as expected.')
            return False
    if response.text:
        print('✅ SUCCESS: Model returned text (no tool calls detected).')
        print(f'\n📥 Response (first 200 chars):\n{response.text[:200]}...')
        return True
    else:
        print('❌ FAILED: No text response received from the model, and no tool call was detected either.')
        return False
if __name__ == '__main__':
    print('🧪 Testing AFC Loop Fix (ensuring `tools=[]` disables tool calling)\n')
    test_passed: Any = asyncio.run(test_no_tool_calling())
    if test_passed:
        print('\n✅ AFC loop fix verified: Tools were successfully disabled as per `tools=[]` configuration.')
    else:
        print('\n❌ AFC loop fix failed: Tools might still be called, or an unexpected error occurred during the test.')
