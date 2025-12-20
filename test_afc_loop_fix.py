#!/usr/bin/env python3
"""
Test that AFC loop is fixed - model should NOT call tools.
"""
import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ google-genai not installed")
    exit(1)

async def test_no_tool_calling():
    """Test that tools=[] prevents tool calling."""
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set")
        return
    
    client = genai.Client(api_key=api_key)
    print("✅ Gemini client initialized")
    
    # Config with tools=[] to disable tool calling
    config = types.GenerateContentConfig(
        temperature=1.0,
        thinking_config=types.ThinkingConfig(thinking_budget=8000),
        tools=[]  # CRITICAL: Disable all tools
    )
    
    chat = client.chats.create(model='gemini-2.5-flash', config=config)
    print("✅ Chat session created with tools=[]")
    
    # Ask a question that might trigger tool use
    prompt = """Fix this Python code:
def add(a b):
    return a + b

Return ONLY the corrected code."""
    
    print(f"\n📤 Sending prompt...")
    response = await asyncio.to_thread(chat.send_message, prompt)
    
    # Check if model tried to call tools
    if response.candidates and response.candidates[0].content.parts:
        first_part = response.candidates[0].content.parts[0]
        if hasattr(first_part, 'function_call') and first_part.function_call:
            print(f"❌ FAILED: Model called tool '{first_part.function_call.name}'")
            print(f"   This means tools=[] is not working!")
            return False
    
    # Model should return text
    if response.text:
        print(f"✅ SUCCESS: Model returned text (no tool calls)")
        print(f"\n📥 Response:\n{response.text[:200]}...")
        return True
    else:
        print(f"❌ FAILED: No text response")
        return False

if __name__ == "__main__":
    print("🧪 Testing AFC Loop Fix (tools=[] disables tool calling)\n")
    result = asyncio.run(test_no_tool_calling())
    
    if result:
        print("\n✅ AFC loop fix verified - tools are disabled")
    else:
        print("\n❌ AFC loop fix failed - tools still being called")