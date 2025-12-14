import os
import json
import logging
import time
import concurrent.futures
from typing import Dict, Any, Optional

from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LLMClient")

class LLMClient:
    """
    Universal Intelligence Engine (Dec 2025 Architecture).
    Enforces Tiered Thinking:
      - HIGH TIER (Consensus): Claude 4.5 + GPT-5.1 + Gemini 3 Pro
      - LOW TIER (Mini): GPT-5 Mini / Haiku 4.5 / Gemini 2.5 Flash
    """
    
    def __init__(self):
        # Initialize Providers
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # --- MODEL REGISTRY (DEC 2025) ---
        self.models = {
            "high": {
                "anthropic": "claude-sonnet-4-5-20250929",
                "openai":    "gpt-5.1",
                "google":    "gemini-3-pro"
            },
            "mini": {
                "anthropic": "claude-haiku-4-5",
                "openai":    "gpt-5-mini", 
                "google":    "gemini-2.5-flash"
            }
        }

    def generate_plan(self, system_context: str, user_goal: str, complexity: str = "high") -> Dict[str, Any]:
        """
        Main Entry Point. Routes based on complexity.
        """
        if complexity == "high":
            return self._execute_consensus_flow(system_context, user_goal)
        else:
            return self._execute_mini_flow(system_context, user_goal)

    def _execute_consensus_flow(self, system: str, user: str) -> Dict[str, Any]:
        """HIGH TIER: Parallel Execution + Synthesis."""
        logger.info("⚖️  STARTING CONSENSUS PROTOCOL (Claude + GPT + Gemini)")
        start_time = time.time()
        
        models = self.models["high"]
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Parallel calls to the Big Three
            f_claude = executor.submit(self._call_anthropic, system, user, models["anthropic"])
            f_gpt    = executor.submit(self._call_openai,    system, user, models["openai"])
            f_gemini = executor.submit(self._call_google,    system, user, models["google"])
            
            results = [f_claude.result(), f_gpt.result(), f_gemini.result()]

        # The Judge (Claude 4.5) synthesizes the Master Plan
        logger.info("👨‍⚖️  The JUDGE (Claude 4.5) is synthesizing the Master Plan...")
        
        judge_prompt = f"""
ACT AS THE CHIEF ARCHITECT. 
Review these three proposals from your sub-agents.
Synthesize a single MASTER PLAN that combines their strengths and eliminates hallucinations.
Return ONLY valid JSON.

PROPOSAL A (Claude): {json.dumps(results[0])}
PROPOSAL B (GPT): {json.dumps(results[1])}
PROPOSAL C (Gemini): {json.dumps(results[2])}
"""
        final_plan = self._call_anthropic(system, judge_prompt, models["anthropic"])
        final_plan['consensus_metadata'] = {
            "models_used": list(models.values()),
            "latency": f"{time.time() - start_time:.2f}s",
            "mode": "CONSENSUS_HIGH_TIER"
        }
        
        logger.info(f"✅ Consensus Reached in {time.time() - start_time:.2f}s")
        return final_plan

    def _execute_mini_flow(self, system: str, user: str) -> Dict[str, Any]:
        """LOW TIER: Fast Execution via Mini Model."""
        # Default to GPT-5 Mini for balance
        model_id = self.models["mini"]["openai"]
        logger.info(f"⚡ MINI MODE: Routing to {model_id}...")
        
        start_time = time.time()
        result = self._call_openai(system, user, model_id)
        result['consensus_metadata'] = {
            "models_used": [model_id],
            "latency": f"{time.time() - start_time:.2f}s",
            "mode": "MINI_LOW_TIER"
        }
        return result

    # --- WRAPPERS ---
    
    def _call_anthropic(self, system, user, model_id):
        try:
            resp = self.anthropic.messages.create(
                model=model_id, max_tokens=4096, system=system,
                messages=[{"role": "user", "content": user}], temperature=0.2
            )
            return self._clean_json(resp.content[0].text)
        except Exception as e:
            logger.error(f"Anthropic Error: {e}")
            return {"error": str(e)}

    def _call_openai(self, system, user, model_id):
        try:
            resp = self.openai.chat.completions.create(
                model=model_id, 
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")
            return {"error": str(e)}

    def _call_google(self, system, user, model_id):
        try:
            model = genai.GenerativeModel(model_id)
            resp = model.generate_content(
                f"SYSTEM: {system}\nUSER: {user}",
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(resp.text)
        except Exception as e:
            logger.error(f"Google Error: {e}")
            return {"error": str(e)}

    def _clean_json(self, text):
        text = text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.endswith("```"): text = text[:-3]
        return json.loads(text)
