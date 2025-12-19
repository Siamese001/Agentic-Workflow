import json
import logging
import os
import time
from typing import Any, Dict

import google.generativeai as genai

# 1. LOAD ENVIRONMENT VARIABLES
from dotenv import load_dotenv

load_dotenv()  # This reads .env from the root


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LLMClient")


class LLMClient:
    """
    Single-Model Intelligence Engine.
    Powered by Gemini 1.5 Flash (Verified Model ID).
    """

    def __init__(self):
        # 2. FETCH KEY SECURELY
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("❌ GOOGLE_API_KEY not found in .env!")
            raise ValueError(
                "Missing GOOGLE_API_KEY. Please check your .env file.")

        genai.configure(api_key=api_key)

        # 3. VERIFIED MODEL NAME
        self.model_id = "models/gemini-2.5-flash"

    def generate_plan(self, system_context: str, user_goal: str, complexity: str = "mini") -> Dict[str, Any]:
        """
        Executes a reasoning step using Gemini 1.5 Flash.
        """
        logger.info(f"⚡ Sending request to {self.model_id}...")
        start_time = time.time()

        try:
            # Gemini SDK allows separating System Instruction from User Prompt
            model = genai.GenerativeModel(
                model_name=self.model_id,
                system_instruction=system_context
            )

            # Force JSON response
            response = model.generate_content(
                user_goal,
                generation_config={"response_mime_type": "application/json"}
            )

            # Parse result
            result = json.loads(response.text)

            # Add observability metrics
            result["metrics"] = {
                "latency": f"{time.time() - start_time:.4f}s",
                "model": self.model_id,
                "cost_tier": "mini"
            }
            return result

        except Exception as e:
logger.error(f"Gemini Call Failed: {e}")
            return {
                "status": "error",
                "reasoning": f"API Error: {str(e)}",
                "plan": {}
            }

