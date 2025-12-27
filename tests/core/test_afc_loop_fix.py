#!/usr/bin/env python3
"""
Test that AFC loop is fixed - model should NOT call tools.
This script verifies that configuring a Gemini chat session with `tools=[]`
successfully prevents the model from attempting to call any tools,
even when prompted with a task that might otherwise trigger tool use.
"""
import asyncio
import os

from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

try:
    # Attempt to import Google GenAI library components
    from google import genai
    from google.genai import types
except ImportError:
    # If the library is not installed, print an error and exit
    print("❌ Error: 'google-genai' library not installed.")
    print("Please install it using: pip install google-generativeai")
    exit(1)


async def test_no_tool_calling() -> bool:
    """
    Tests that configuring a chat session with `tools=[]` successfully
    prevents the model from calling tools.

    Returns:
        bool: True if the test passes (no tool calls detected, text response received),
              False otherwise.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ FAILED: GOOGLE_API_KEY environment variable not set.")
        return False

    # Initialize the Gemini client
    # NOTE: The use of `genai.Client` and `client.chats.create` with `config`
    # is not standard for the public `google-generativeai` library.
    # Typically, you'd use `genai.configure(api_key=api_key)`
    # and then `model = genai.GenerativeModel('gemini-2.5-flash', tools=[])`
    # followed by `chat = model.start_chat()`.
    # Assuming this custom client/API pattern is intentional for this project.
    client = genai.Client(api_key=api_key)
    print("✅ Gemini client initialized.")

    # Configure the chat session to explicitly disable tool calling
    # The `tools=[]` parameter is critical for this test.
    config = types.GenerateContentConfig(
        temperature=1.0,
        thinking_config=types.ThinkingConfig(thinking_budget=8000),
        tools=[]  # CRITICAL: Disable all tools for this session
    )

    # Create a chat session with the specified model and configuration
    chat = client.chats.create(model='gemini-2.5-flash', config=config)
    print("✅ Chat session created with `tools=[]` configuration.")

    # Define a prompt that might otherwise trigger tool use (e.g., code fixing)
    prompt = """Fix this Python code:
def add(a b):
    return a + b

Return ONLY the corrected code."""

    print("\n📤 Sending prompt to the model...")

    # Send the message to the chat session.
    # asyncio.to_thread is used defensively in case chat.send_message performs
    # blocking I/O. If chat.send_message is truly asynchronous,
    # `await chat.send_message(prompt)` would suffice.
    response = await asyncio.to_thread(chat.send_message, prompt)

    # Check the response for any signs of tool calling
    if response.candidates and response.candidates[0].content.parts:
        first_part = response.candidates[0].content.parts[0]
        # Check if the first part of the content is a function call
        if hasattr(first_part, 'function_call') and first_part.function_call:
            print(
                f"❌ FAILED: Model unexpectedly called tool "
                f"'{first_part.function_call.name}'."
            )
            print(
                "   This indicates that the `tools=[]` configuration "
                "is not working as expected."
            )
            return False  # Explicitly return False on failure

    # If no tool call was detected, check if the model returned a text response
    if response.text:
        print("✅ SUCCESS: Model returned text (no tool calls detected).")
        # Truncate the response for cleaner output in the console
        print(f"\n📥 Response (first 200 chars):\n{response.text[:200]}...")
        return True  # Explicitly return True on success
    else:
        print(
            "❌ FAILED: No text response received from the model, "
            "and no tool call was detected either."
        )
        return False  # Explicitly return False if neither text nor tool call


if __name__ == "__main__":
    print("🧪 Testing AFC Loop Fix (ensuring `tools=[]` disables tool calling)\n")

    # Run the asynchronous test function
    test_passed = asyncio.run(test_no_tool_calling())

    if test_passed:
        print(
            "\n✅ AFC loop fix verified: Tools were successfully disabled "
            "as per `tools=[]` configuration."
        )
    else:
        print(
            "\n❌ AFC loop fix failed: Tools might still be called, "
            "or an unexpected error occurred during the test."
        )
