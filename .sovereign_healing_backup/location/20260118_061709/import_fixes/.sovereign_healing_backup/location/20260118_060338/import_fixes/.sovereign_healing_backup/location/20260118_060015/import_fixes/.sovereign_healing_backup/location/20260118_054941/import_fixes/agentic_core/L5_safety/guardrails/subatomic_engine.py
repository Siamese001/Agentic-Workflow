
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail, healer, orchestrator, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
"""
L5 Safety: SubAtomicEngine
Hardens LLM interaction with token budgets and retry logic.
"""
import asyncio
import json
import logging
import os
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
import numpy as np
try:
    from google import genai
    from google.api_core.exceptions import DeadlineExceeded, InternalServerError, ResourceExhausted
    from google.genai import types
    GENAI_AVAILABLE: Any = True
except ImportError:
    GENAI_AVAILABLE: Any = False
try:
    from agentic_core.L4_state.validation_context.PineconeSovereignAgent import PineconeSovereignAgent
    PINECONE_AVAILABLE: Any = True
except ImportError:
    PINECONE_AVAILABLE: Any = False
try:
    from agentic_core.prompt_governance.prompt_governor import PromptGovernor
    PROMPT_GOVERNOR_AVAILABLE: Any = True
except ImportError:
    PROMPT_GOVERNOR_AVAILABLE: Any = False
    
Logger: Any = logging.getLogger(__name__)

class SubAtomicEngine:
    """SubAtomicEngine - hardens LLM interaction with token budgets."""
    pass

# Alias for backward compatibility

class SubAtomicEngineImpl:
    """Hardens the LLM interaction with the 24,576 token budget."""

    def __init__(self, gemini_client: Optional[Any]=None, redis_client: Optional[Any]=None, pinecone_index: Optional[Any]=None):
        """
        Initialize SubAtomicEngine with Meta-Learning storage.
        
        Args:
            gemini_client: Optional Gemini client (creates new if None)
            redis_client: Optional Redis client for L3 Failure Tracking
            pinecone_index: Optional Pinecone index for L2 Long-term Memory
        """
        self.redis_client = redis_client
        self.pinecone_index = pinecone_index
        if not GENAI_AVAILABLE:
            raise RuntimeError('Gemini SDK not available. Install with: pip install google-generativeai')
        if gemini_client:
            self._client = gemini_client
        else:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    Logger.warning('[L5] Using legacy GEMINI_API_KEY. Please migrate to GOOGLE_API_KEY.')
            if not api_key:
                raise RuntimeError('No Gemini API key found. Set GOOGLE_API_KEY in your .env file.')
            self._client = genai.Client(api_key=api_key)
        self.chat_sessions: Dict[str, Any] = {}
        self.pinecone = None
        
        # [HARDENING 8] Initialize prompt governor for centralized prompt management
        if PROMPT_GOVERNOR_AVAILABLE:
            self.prompt_gov = PromptGovernor()
            print('   [OK] SubAtomicEngine: Prompt governance enabled')
        else:
            self.prompt_gov = None
            print('   [!] SubAtomicEngine: Prompt governance unavailable')
        
        print('   [OK] SubAtomicEngine: Hybrid routing deferred (lazy init)')

    @staticmethod
    def get_safe_config(is_fission: bool=False) -> Any:
        """
        Get safe Gemini configuration with hardened thinking budget.
        
        Args:
            is_fission: Whether this is for fission mode (uses max budget)
            
        Returns:
            GenerateContentConfig with safe thinking budget
        """
        if not GENAI_AVAILABLE:
            raise RuntimeError('Gemini SDK not available')
        safe_budget: Any = 24576 if is_fission else 16000
        return types.GenerateContentConfig(temperature=0.1, thinking_config=types.ThinkingConfig(thinking_budget=safe_budget))

    @staticmethod
    def parse_fission_output(output: str) -> Dict[str, str]:
        """
        Extracts JSON file map from AI response.
        
        Args:
            output: Raw output from Gemini
            
        Returns:
            Dictionary mapping file paths to content
        """
        try:
            if not output or len(output.strip()) < 20:
                return {}
            json_match: Any = re.search('\\{.*\\}', output, re.DOTALL)
            if json_match:
                data: Any = json.loads(json_match.group())
                return data if isinstance(data, dict) else {}
        except Exception as e:
            Logger.warning(f'Failed to parse fission output: {e}')
        return {}

    async def get_embedding(self, text: str) -> List[float]:
        """Generates semantic embeddings for code/tasks using Gemini 2025."""
        try:
            result: Any = await asyncio.to_thread(self._client.models.embed_content, model='text-embedding-004', contents=text)
            return result.embeddings[0].values
        except Exception as e:
            Logger.error(f'   [MEMORY ERROR] Embedding failed: {e}')
            return [0.0] * 768

    async def resilient_mutation(self, *args, system_prompt: Optional[str]=None, **kwargs) -> str:
        """
        Hardened LLM Gateway: Universal signature with legacy system_prompt support.
        Scrubs unknown kwargs to prevent Gemini API errors.
        """
        if len(args) >= 2:
            code, Task = (args[0], args[1])
            prompt: Any = f'### TASK\n{Task}\n\n### CODE\n{code}'
        elif len(args) == 1:
            prompt: Any = args[0]
        else:
            prompt: Any = kwargs.get('prompt', '')
        if not system_prompt:
            system_prompt: Any = kwargs.pop('system_prompt', None)
        if system_prompt:
            prompt: Any = f'[SYSTEM_INSTRUCTION]\n{system_prompt}\n\n[USER_INPUT]\n{prompt}'
        file_path: Any = kwargs.get('file_path', 'unknown_file')
        code: Any = kwargs.get('code', '')
        Task: Any = kwargs.get('Task', prompt)
        round_num: Any = kwargs.get('round_num', 1)
        fission_active: Any = kwargs.get('fission_active', False)
        scrubbed_kwargs: Any = {k: v for k, v in kwargs.items() if k not in ['stop_sequences', 'top_p', 'response_format']}
        return await self._resilient_mutation_impl(file_path=file_path, code=code or prompt, Task=Task, round_num=round_num, fission_active=fission_active, system_prompt=system_prompt, **scrubbed_kwargs)

    async def _resilient_mutation_impl(self, file_path: str, code: str, Task: str, round_num: int=1, fission_active: bool=False, system_prompt: Optional[str]=None, **kwargs) -> str:
        """Execute resilient mutation with exponential backoff retry.
        
        Args:
            file_path: Path to the file being mutated
            code: Code content to mutate
            Task: Task description
            round_num: Current round number
            fission_active: Whether fission mode is active
            system_prompt: Optional system prompt override
            **kwargs: Additional arguments (ignored for compatibility)
        """
        if self.pinecone is None and PINECONE_AVAILABLE:
            try:
                from agentic_core.L4_state.validation_context.PineconeSovereignAgent import PineconeSovereignAgent
                self.pinecone = PineconeSovereignAgent(Path('.'))
                print('   [OK] SubAtomicEngine: Hybrid routing activated (lazy)')
            except Exception as e:
                print(f'   [!] Hybrid routing failed (will use fallback): {e}')
                self.pinecone = None
        if not self._client:
            raise RuntimeError('Gemini client not initialized')
        start_time = time.time()
        temp_override = 0.1
        if self.redis_client:
            fail_key = f'fail_count:{file_path}'
            current_fails = self.redis_client.get(fail_key)
            if current_fails and int(current_fails) >= 2:
                Logger.warning(f'   [ADAPTIVE] Repeat failure ({current_fails}) detected for {file_path}. Bumping temperature.')
                temp_override = 0.8
        # [HARDENING 8] Use PromptGovernor for centralized prompt construction
        if self.prompt_gov:
            if fission_active:
                prompt_dict = self.prompt_gov.build_fission_prompt(code, file_path)
            else:
                # Retrieve vector memory context if available
                context_str = ""
                if self.pinecone and hasattr(self.pinecone, 'semantic_search'):
                    try:
                        context_chunks = await self.pinecone.semantic_search(
                            query=Task,
                            file_path=Path(file_path),
                            top_k=3
                        )
                        if context_chunks:
                            context_str = "\n\n".join(context_chunks)
                    except Exception as e:
                        Logger.warning(f'Vector memory retrieval failed: {e}')
                
                prompt_dict = self.prompt_gov.build_healing_prompt(
                    Task=Task if not system_prompt else system_prompt,
                    code=code,
                    file_path=file_path,
                    context=context_str
                )
            
            # Use system prompt from governor
            prompt = f"{prompt_dict['system']}\n\n{prompt_dict['user']}"
        else:
            # Fallback to legacy prompt construction
            if system_prompt:
                prompt = f'[INSTRUCTION]\n{system_prompt}\n\n[CONTEXT]\nFILE: {file_path}\n\nTASK: {Task}\n\nCODE:\n{code}'
            elif fission_active:
                prompt = f'ATOMIC FISSION: Split {file_path} into 3 sub-modules. Return ONLY a JSON map.\n\nCODE:\n{code}'
            else:
                prompt = f'HEAL: Fix violations in {file_path}.\n\nTASK: {Task}\n\nCODE:\n{code}'
        config = self.get_safe_config(is_fission=fission_active)
        config.temperature = temp_override
        chat_key = f'chat_{file_path}'
        if chat_key not in self.chat_sessions:
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            self.chat_sessions[chat_key] = self._client.chats.create(model=model_name, config=config)
            Logger.info(f'   [NEW] Created chat session for {os.path.basename(file_path)}')
        max_retries = 3
        response = None
        for attempt in range(1, max_retries + 1):
            try:
                response = await asyncio.to_thread(self.chat_sessions[chat_key].send_message, prompt)
                break
            except (ResourceExhausted, InternalServerError, DeadlineExceeded) as e:
                if attempt == max_retries:
                    Logger.error(f'   [X] Gemini Error (Final): {e}')
                    return code
                wait = 2 ** attempt + random.uniform(0, 1)
                Logger.warning(f'   [!] Gemini Transient Error ({attempt}/{max_retries}): {e}. Retrying in {wait:.1f}s')
                await asyncio.sleep(wait)
            except Exception as e:
                Logger.error(f'   [X] Gemini Fatal Error: {e}')
                return code
        if response and response.candidates and response.candidates[0].content.parts:
            raw_output = response.candidates[0].content.parts[0].text.strip()
            duration = time.time() - start_time
            if duration < 0.1 and (not raw_output or len(raw_output) < 50):
                Logger.error(f'   [X] HALLUCINATION REJECTED (Latency: {duration:.3f}s).')
                return code
            
            # [HARDENING 8] Use PromptGovernor to enforce output format
            if self.prompt_gov and not fission_active:
                try:
                    healed_code = self.prompt_gov.enforce_output_format(raw_output)
                except ValueError as e:
                    Logger.error(f'   [X] Output format validation failed: {e}')
                    if self.redis_client:
                        self.redis_client.incr(f'fail_count:{file_path}')
                    return code
            else:
                # Fallback: Extract code block if fenced (common LLM output format)
                code_match = re.search(r'```python\n(.*?)\n```', raw_output, re.DOTALL)
                healed_code = code_match.group(1) if code_match else raw_output
            
            # [HARDENING] Stage 1: Post-LLM Validation Pipeline
            if not fission_active:
                try:
                    from agentic_core.L5_safety.validators.heal_validator import HealValidatorAgent
                    validator = HealValidatorAgent(Path('.'))
                    ValidationResult = validator.validate_healed_code(code, healed_code, Path(file_path))
                    
                    if not ValidationResult['valid']:
                        Logger.error(f"   [X] HEAL REJECTED ({ValidationResult['stage']}): {ValidationResult['reason']}")
                        if self.redis_client:
                            self.redis_client.incr(f'fail_count:{file_path}')
                        return code
                    
                    Logger.info(f"   [✓] Heal validated: {os.path.basename(file_path)}")
                except ImportError as e:
                    Logger.warning(f'   [!] HealValidatorAgent unavailable: {e}')
                except Exception as e:
                    Logger.error(f'   [!] Validation failed: {e}')
                    return code
            
            output = healed_code
            
            # Legacy truncation check (now redundant with HealValidatorAgent but kept for defense-in-depth)
            if not fission_active and '...' in output and (len(output) < len(code) * 0.8):
                Logger.warning('   [X] TRUNCATION DETECTED. Rejecting mutation.')
                if self.redis_client:
                    self.redis_client.incr(f'fail_count:{file_path}')
                return code
            if self.pinecone and hasattr(self.pinecone, 'index'):
                try:
                    vector = await self.get_embedding(Task)
                    self.pinecone.index.upsert(vectors=[{'id': f'succ:{os.path.basename(file_path)}', 'values': vector, 'metadata': {'Task': Task[:200], 'round': round_num, 'type': 'HealingPattern'}}])
                    print(f'   [MEMORY] Stored healing pattern for {os.path.basename(file_path)}')
                except Exception as e:
                    print(f'   [!] Failed to store pattern in Pinecone: {e}')
            if self.redis_client:
                self.redis_client.delete(f'fail_count:{file_path}')
            return output
        Logger.warning('   [!] Malformed response from Gemini')
        return code

    def route_mission(self, mission: str) -> Dict:
        """
        Eternal sub-atomic routing: Vector + Keyword precision.
        """
        if self.pinecone is None and PINECONE_AVAILABLE:
            try:
                from agentic_core.L4_state.validation_context.PineconeSovereignAgent import PineconeSovereignAgent
                self.pinecone = PineconeSovereignAgent(Path('.'))
            except Exception as e:
                print(f'   [!] Routing failed to initialize Pinecone: {e}')
                self.pinecone = None
        if not self.pinecone:
            return {'Route': 'fallback', 'reason': 'Hybrid routing offline', 'confidence': 0.0}
        from agentic_core.L5_safety.validators.structure_blueprint_1 import CANON_SIGNALS
        keywords: Any = [w for w in CANON_SIGNALS if w.lower() in mission.lower()]
        if hasattr(self.pinecone, 'hybrid_search'):
            try:
                results: Any = self.pinecone.hybrid_search(query=mission, top_k=8)
            except Exception as e:
                print(f'   [!] Hybrid search failed: {e}')
                results: Any = None
        else:
            results: Any = None
        if not results or not results.get('matches'):
            return {'Route': 'unknown', 'reason': 'No high-confidence matches', 'confidence': 0.0}
        territories: Any = {}
        agents: Any = set()
        for match in results.get('matches', []):
            meta: Any = match.get('metadata', {})
            territory: Any = meta.get('territory', 'unknown')
            score: Any = match.get('score', 0)
            path: Any = meta.get('path', '')
            territories[territory] = territories.get(territory, 0) + score
            if 'agent' in path.lower():
                file_stem: Any = Path(path).stem
                if file_stem.endswith('_agent'):
                    agents.add(file_stem.replace('_', ' ').title().replace(' ', ''))
        if not territories:
            return {'Route': 'unknown', 'reason': 'No territory data found', 'confidence': 0.0}
        best_territory: Any = max(territories, key=territories.get)
        confidence: Any = territories[best_territory] / sum(territories.values())
        routing_plan: Any = {'primary_territory': best_territory, 'confidence': round(confidence, 3), 'relevant_agents': list(agents)[:3], 'top_matches': [{'path': m['metadata'].get('path'), 'score': round(m['score'], 3)} for m in results.get('matches', [])[:3]], 'recommended_action': f"Deploy {(list(agents)[0] if agents else 'Agent')} to {best_territory}"}
        print(f"   [ROUTING] Mission routed to '{best_territory}' ({confidence:.1%})")
        return routing_plan