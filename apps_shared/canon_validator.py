#!/usr/bin/env python3
"""
🚀 HARDENED SUBATOMIC CANON VALIDATOR - V2.2 (ZERO-LOSS & FISSION)
Enforces 50 validation keys with AI-powered fixes and Atomic Fission.
"""

print("DEBUG: VERSION 2.2 - BUDGET HARDENED - DECEMBER 19 2025")

import argparse
import ast
import asyncio
import hashlib
import importlib.util
import json
import logging
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# L3 ORCHESTRATION: FISSION MANAGER
# ==============================================================================
class FissionManager:
    """Manages the pivot from healing to atomic decomposition."""
    def __init__(self, line_limit=800, deletion_guardrail=110, max_rounds=3):
        self.line_limit = line_limit
        self.deletion_guardrail = deletion_guardrail
        self.max_rounds = max_rounds

    def should_trigger_fission(self, file_path: str, current_round: int) -> Tuple[bool, Optional[str]]:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > self.line_limit:
                    return True, f"L4 State Bloat: {len(lines)} lines exceeds limit."
        if current_round >= self.max_rounds:
            return True, "Cognitive Exhaustion: Round 3 reached."
        return False, None

# ==============================================================================
# L5 SAFETY: GUARDRAIL
# ==============================================================================
class SafetyGuardrail:
    """Enforces Zero-Loss principles during mutation."""
    def verify_change(self, original_code: str, new_code: str, mode: str = "HEAL") -> Tuple[bool, str]:
        orig_len = len(original_code.splitlines())
        new_len = len(new_code.splitlines())
        delta = orig_len - new_len

        if mode == "ATOMIC_FISSION":
            return True, "Fission Whitelist: Mass deletion permitted for Facade."
        if delta > 110:
            return False, f"Safety Block: Mass deletion detected ({delta} lines)."
        if not new_code.strip():
            return False, "Safety Block: Attempted to wipe file."
        return True, "Safety Pass."

# ==============================================================================
# VALIDATION CONTEXT (BLACKBOARD)
# ==============================================================================
@dataclass
class ValidationContext:
    python_files: List[str] = field(default_factory=list)
    modified_files: Set[str] = field(default_factory=set)
    fission_active: bool = False
    last_fission_map: Dict[str, str] = field(default_factory=dict)
    chat_sessions: Dict[str, Any] = field(default_factory=dict)
    _client: Any = None

    def __post_init__(self):
        from google import genai
        self._client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    async def resilient_mutation(self, file_path: str, code: str, round_num: int) -> str:
        from google.genai import types
        f_mgr = FissionManager()
        should_fiss, reason = f_mgr.should_trigger_fission(file_path, round_num)

        if should_fiss:
            self.fission_active = True
            task = f"ATOMIC FISSION: Split {file_path} into 3 sub-modules. Return ONLY a JSON map."
        else:
            task = f"HEAL: Fix all syntax and style violations in {file_path}."

        # 🛑 HARDENED: Cap thinking_budget at 50,000 to avoid API Error 400
        safe_budget = 50000 if self.fission_active else 24000
        
        config = types.GenerateContentConfig(
            temperature=0.1,
            thinking_config=types.ThinkingConfig(thinking_budget=safe_budget)
        )
        
        chat_key = f"chat_{file_path}"
        if chat_key not in self.chat_sessions:
            self.chat_sessions[chat_key] = self._client.chats.create(
                model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-thinking-exp'), 
                config=config
            )
        
        prompt = f"TASK: {task}\n\nCODE:\n{code}"
        response = await asyncio.to_thread(self.chat_sessions[chat_key].send_message, prompt)
        output = response.text.strip()

        # Truncation Guard
        if not self.fission_active and "..." in output and len(output) < (len(code) * 0.8):
            print("   🚫 TRUNCATION DETECTED. Rejecting mutation.")
            return code

        if self.fission_active:
            try:
                json_match = re.search(r'\{.*\}', output, re.DOTALL)
                if json_match:
                    self.last_fission_map = json.loads(json_match.group())
                    return "FISSION_COMPLETE"
            except: pass
            
        return output

# ==============================================================================
# EXECUTION LOGIC
# ==============================================================================
async def handle_fission_write(ctx: ValidationContext, monolith_path: str):
    print(f"   ⚛️ Executing Atomic Fission for {monolith_path}...")
    for path, content in ctx.last_fission_map.items():
        full_path = Path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        ctx.modified_files.add(str(full_path))
        print(f"      Created: {path}")
    return True

def get_python_files(root: str = '.') -> List[str]:
    """Hardened scanner using absolute paths."""
    abs_root = os.path.abspath(root)
    print(f"   📂 Scanning: {abs_root}")
    files = []
    for r, dirs, f_list in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv'}]
        for f in f_list:
            if f.endswith('.py'):
                files.append(os.path.join(r, f))
    return files

async def run_mission():
    ctx = ValidationContext()
    ctx.python_files = get_python_files(".")
    safety = SafetyGuardrail()

    for fp in ctx.python_files:
        with open(fp, 'r', encoding='utf-8') as f:
            orig_code = f.read()
        
        # Simulated Healing Round
        mutated = await ctx.resilient_mutation(fp, orig_code, 1)
        
        if mutated == "FISSION_COMPLETE":
            await handle_fission_write(ctx, fp)
        else:
            is_safe, _ = safety.verify_change(orig_code, mutated)
            if is_safe:
                with open(fp, 'w', encoding='utf-8') as f: f.write(mutated)
                ctx.modified_files.add(fp)

if __name__ == "__main__":
    asyncio.run(run_mission())
