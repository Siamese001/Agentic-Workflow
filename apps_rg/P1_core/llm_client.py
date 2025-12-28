from typing import Any, Optional, Protocol, Dict, List

import json
import logging
import os
import time
from typing import Any, Dict

import google.generativeai as genai

# Load environment variables
from dotenv import load_dotenv
from agentic_core.config.P1_core.sovereign_config import config

load_dotenv()


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LLMClient")


class LLMClient:
    """
    Single-Model Intelligence Engine.
    Powered EXCLUSIVELY by Gemini 1.5 Flash.
    """

    def __init__(self):
        # 1. Fetch Key from sovereign config
        api_key = os.getenv("GOOGLE_API_KEY")  # Keep for backward compatibility
        if not api_key:
            logger.error("❌ GOOGLE_API_KEY not found in .env!")
            raise ValueError("Missing GOOGLE_API_KEY")

        genai.configure(api_key=api_key)

        # 2. Get model from environment or use standard Flash
        self.model_id = os.getenv("LLM_MODEL", "gemini-2.5-flash-preview-09-2025")  # Keep for backward compatibility

    def generate_plan(self, system_context: str, user_goal: str, complexity: str = "mini") -> Dict[str, Any]:
        """
        Executes a reasoning step using Gemini 1.5 Flash.
        """
        logger.info(f"⚡ Sending request to {self.model_id}...")
        start_time = time.time()

        try:
            # Initialize Model
            model = genai.GenerativeModel(
                model_name=self.model_id,
                system_instruction=system_context
            )

            # Generate (Force JSON)
            response = model.generate_content(
                user_goal,
                generation_config={"response_mime_type": "application/json"}
            )

            # Parse Response
            logger.debug(f"Raw LLM response: {response.text}")
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError as je:
                # Fallback if model returns text wrapped in markdown
                try:
                    text = response.text.replace(
                        "```json", "").replace("```", "")
                    logger.debug(f"Cleaned response for JSON parsing: {text}")
                    result = json.loads(text)
                except json.JSONDecodeError:
                    # Return structured error for JSON parsing failures
                    logger.error(f"JSON parsing failed: {str(je)}")
                    logger.error(f"Full raw response: {response.text}")
                    return {
                        "status": "error",
                        "reasoning": f"LLM response parse error: {str(je)}",
                        # First 500 chars for debugging
                        "raw_response": response.text[:500]
                    }

            result["metrics"] = {
                "latency": f"{time.time() - start_time:.4f}s",
                "model": self.model_id
            }
            return result

        except Exception as e:
            logger.error(f"Gemini Call Failed: {e}")
            return {
                "status": "error",
                "reasoning": f"LLM call failed: {str(e)}",
                "raw_response": ""
            }

