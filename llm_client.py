import os
import json
import logging
import time
from typing import Dict, Any, Optional

# Import all three major providers
# pip install openai anthropic google-generativeai
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LLMClient")

class LLMClient:
    """
    Universal Interface to Frontier Intelligence (Dec 2025).
    Supports:
      - Anthropic: claude-sonnet-4-5-20250929
      - OpenAI:    gpt-5.1
      - Google:    gemini-3-pro
    """
    
    def __init__(self, provider: str = "anthropic"):
        self.provider = provider.lower()
        self.client = None
        self.model = None
        self.api_key_set = False
        
        # 1. ANTHROPIC CONFIGURATION
        if self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = Anthropic(api_key=api_key)
                self.model = "claude-sonnet-4-5-20250929"
                self.api_key_set = True
            else:
                logger.warning("⚠️ ANTHROPIC_API_KEY missing. Set it with: export ANTHROPIC_API_KEY=your_key")

        # 2. OPENAI CONFIGURATION
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-5.1"
                self.api_key_set = True
            else:
                logger.warning("⚠️ OPENAI_API_KEY missing. Set it with: export OPENAI_API_KEY=your_key")

        # 3. GOOGLE CONFIGURATION
        elif self.provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = "gemini-3-pro"
                self.api_key_set = True
            else:
                logger.warning("⚠️ GOOGLE_API_KEY missing. Set it with: export GOOGLE_API_KEY=your_key")
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def generate_plan(self, system_context: str, user_goal: str) -> Dict[str, Any]:
        """
        Generates a JSON execution plan using the selected provider.
        Falls back to mock mode if no API key is configured.
        """
        start_time = time.time()
        
        # Check if we have API keys
        if not self.api_key_set:
            logger.warning("⚠️ No API key configured. Using MOCK MODE.")
            return self._mock_response(user_goal)
        
        logger.info(f"⚡ Sending request to {self.provider.upper()} ({self.model})...")

        # JSON Schema Injection (Critical for Agentic Control)
        json_instruction = """
IMPORTANT: You must respond with raw JSON only. Do not wrap in markdown ```json blocks.
Schema:
{
    "goal": "Refined user goal",
    "reasoning": "Explanation of your plan based on the Context",
    "plan": {
        "steps": [
            { "step": 1, "action": "tool_name", "params": { "key": "value" } }
        ]
    }
}
"""
        full_system_prompt = f"{system_context}\n\n{json_instruction}"

        try:
            if self.provider == "anthropic":
                return self._call_anthropic(full_system_prompt, user_goal)
            elif self.provider == "openai":
                return self._call_openai(full_system_prompt, user_goal)
            elif self.provider == "google":
                return self._call_google(full_system_prompt, user_goal)
                
        except Exception as e:
            logger.error(f"LLM Call Failed: {e}")
            return self._error_response(str(e))
        finally:
            logger.info(f"✅ Response received in {time.time() - start_time:.2f}s")

    def _mock_response(self, user_goal: str) -> Dict[str, Any]:
        """Fallback response when no API key is configured."""
        return {
            "goal": user_goal,
            "reasoning": "MOCK MODE: No API key configured. This is a simulated response.",
            "plan": {
                "steps": [
                    {
                        "step": 1,
                        "action": "write_file",
                        "params": {
                            "filename": "mock_output.py",
                            "content": f"# Mock response for: {user_goal}\nprint('Hello from mock mode!')"
                        }
                    }
                ]
            }
        }

    # --- PROVIDER IMPLEMENTATIONS ---

    def _call_anthropic(self, system: str, user: str) -> Dict:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}],
            temperature=0.2
        )
        return self._clean_json(response.content[0].text)

    def _call_openai(self, system: str, user: str) -> Dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            response_format={"type": "json_object"}, # GPT-5.1 native JSON mode
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)

    def _call_google(self, system: str, user: str) -> Dict:
        # Gemini 3 Pro uses the 'generation_config' for JSON enforcement
        model = genai.GenerativeModel(self.model)
        chat = model.start_chat(history=[])
        
        combined_prompt = f"SYSTEM: {system}\n\nUSER: {user}"
        
        response = chat.send_message(
            combined_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)

    def _clean_json(self, text: str) -> Dict:
        """Helper to strip markdown fences if the model adds them."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text)

    def _error_response(self, msg: str) -> Dict:
        return {
            "goal": "Error",
            "reasoning": f"LLM Failure: {msg}",
            "plan": {"steps": []},
            "status": "error"
        }
