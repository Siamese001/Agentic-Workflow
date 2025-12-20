"""
Fission Manager - L3 Orchestration Layer

Manages the transition from code healing to atomic fission (decomposition)
when L1 Cognition limits are reached.

Strategy:
- L1 Cognition: Detects reasoning exhaustion (3+ failed rounds)
- L4 State: Identifies monolithic files (>800 lines)
- L5 Safety: Prevents destructive deletions (>110 lines)
- L3 Orchestration: Triggers atomic fission to partition monoliths
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Any, Tuple

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class FissionResult:
    """Result of atomic fission decomposition."""
    triggered: bool
    reason: str
    new_files: Dict[str, str]  # Map of file paths to content
    original_file: str
    success: bool
    error_message: Optional[str] = None


class FissionManager:
    """
    L3 Orchestration Layer: Manages transition from healing to atomic fission.
    
    Triggers when:
    1. L4 State: File exceeds line limit (Key 42 violation)
    2. L5 Safety: Destructive mass deletion detected (>110 lines)
    3. L1 Cognition: Reasoning exhausted after 3+ rounds
    
    Strategy:
    - Partition monoliths into 3 sub-modules
    - Preserve function signatures (backward compatibility)
    - Create facade pattern for existing imports
    - Distribute complexity across smaller files
    """
    
    def __init__(self, gemini_client: Optional[Any] = None, 
                 line_limit: int = 800, 
                 deletion_guardrail: int = 110, 
                 max_rounds: int = 3):
        """
        Initialize Fission Manager.
        
        Args:
            gemini_client: Optional Gemini client (creates new if None)
            line_limit: L4 State line limit (Key 42)
            deletion_guardrail: L5 Safety deletion limit
            max_rounds: L1 Cognition max rounds before exhaustion
        """
        self.line_limit = line_limit
        self.deletion_guardrail = deletion_guardrail
        self.max_rounds = max_rounds
        
        self.genai_available = GENAI_AVAILABLE
        
        if gemini_client:
            self._client = gemini_client
        elif GENAI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                self._client = genai.Client(api_key=api_key)
                logger.info("✅ Fission Manager connected to Gemini 2.5")
            else:
                self._client = None
                logger.warning("⚠️  Fission Manager: No Gemini API key found")
        else:
            self._client = None
            logger.warning("⚠️  Fission Manager: Gemini not available")
    
    def should_trigger_fission(self, file_path: str, current_round: int, 
                               last_error: Optional[str] = None, 
                               lines_deleted: int = 0) -> Tuple[bool, Optional[str]]:
        """
        Determines if L4 State requires partitioning based on L1/L5 signals.
        
        Args:
            file_path: Path to file being healed
            current_round: Current healing round
            last_error: Last error message
            lines_deleted: Number of lines that would be deleted
            
        Returns:
            Tuple of (should_trigger, reason)
        """
        # 1. Check if the file is a known monolith (Static Key 42 check)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = len(f.readlines())
                    if line_count > self.line_limit:
                        return True, f"Static Metric: File exceeds L4 line limit (Key 42): {line_count} > {self.line_limit}"
            except Exception as e:
                logger.warning(f"Could not read file for fission check: {e}")
        
        # 2. Check if L5 Safety is blocking progress
        if lines_deleted > self.deletion_guardrail:
            return True, f"L5 Safety: Detected destructive mass deletion ({lines_deleted}L > {self.deletion_guardrail}L)"
        
        # 3. Check if L1 Cognition is stuck in a loop
        if current_round >= self.max_rounds and last_error and "SyntaxError" in str(last_error):
            return True, f"L1 Cognition: Reasoning exhausted after {current_round} rounds (SyntaxError loop)"
        
        return False, None
    
    def get_fission_prompt(self, file_name: str, content: str) -> str:
        """
        Generates the Atomic Fission prompt for SystemArchitect.
        
        Args:
            file_name: Name of file to decompose
            content: File content
            
        Returns:
            Fission prompt for Gemini
        """
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        parent_dir = os.path.dirname(file_name) or "."
        
        return f"""### MISSION: ATOMIC FISSION (Monolith Decomposition)
The target file `{file_name}` has exceeded L1 Cognition limits and is structurally unstable.

ORIGINAL FILE CONTENT:
{content}
```

### OBJECTIVE:
Partition `{file_name}` into three sub-modules to clear Key 42 violations.

### REQUIRED STRUCTURE:
1. `{file_name}` (Main Facade/Imports - preserves the original interface)
2. `{parent_dir}/{base_name}_core.py` (Primary state management and core logic)
3. `{parent_dir}/{base_name}_signals.py` (L1-L5 communication and helper methods)

### CONSTRAINTS:
- SIGNATURE PARITY: Do NOT delete or change existing function signatures
- LINE LIMIT: Each new file MUST be under 350 lines
- LOGIC PRESERVATION: Total line count across new files must match original (+/- 5%)
- FACADE PATTERN: Original file becomes import facade for backward compatibility
- ZERO DATA LOSS: All functionality must be preserved

### OUTPUT FORMAT:
Return ONLY a valid JSON object mapping file paths to their content:
```json
{{
    "{file_name}": "# Facade pattern\\nfrom .{base_name}_core import *\\nfrom .{base_name}_signals import *",
    "{parent_dir}/{base_name}_core.py": "# Core logic\\n\\nclass CoreClass:\\n    pass",
    "{parent_dir}/{base_name}_signals.py": "# Signal handling\\n\\ndef handle_signal():\\n    pass"
}}
```

CRITICAL:
- Return ONLY the JSON object, no markdown code blocks
- Ensure facade maintains all original exports
- Preserve all imports and dependencies
- Each file must be syntactically valid Python
"""
    
    async def execute_fission(self, file_path: str, content: str, reason: str) -> FissionResult:
        """
        Execute atomic fission decomposition.
        
        Args:
            file_path: Path to monolithic file
            content: File content
            reason: Reason for fission trigger
            
        Returns:
            FissionResult with decomposed files
        """
        if not self._client:
            return FissionResult(
                triggered=True,
                reason=reason,
                new_files={},
                original_file=file_path,
                success=False,
                error_message="Gemini client not available"
            )
        
        logger.info(f"🔬 ATOMIC FISSION TRIGGERED: {file_path}")
        logger.info(f"   Reason: {reason}")
        
        try:
            # Generate fission prompt
            prompt = self.get_fission_prompt(file_path, content)
            
            # Call Gemini for decomposition
            config = types.GenerateContentConfig(
                temperature=0.2,
                thinking_config=types.ThinkingConfig(
                    thinking_budget=50000
                ),
                tools=[]
            )
            
            response = self._client.models.generate_content(
                model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
                contents=prompt,
                config=config
            )
            
            # Parse response
            new_files = self._parse_fission_response(response, file_path)
            
            if new_files:
                logger.info(f"   ✅ Decomposed into {len(new_files)} sub-modules")
                for new_file in new_files.keys():
                    logger.info(f"      → {new_file}")
                
                return FissionResult(
                    triggered=True,
                    reason=reason,
                    new_files=new_files,
                    original_file=file_path,
                    success=True
                )
            else:
                return FissionResult(
                    triggered=True,
                    reason=reason,
                    new_files={},
                    original_file=file_path,
                    success=False,
                    error_message="Failed to parse decomposition response"
                )
        
        except Exception as e:
            logger.error(f"   ❌ Fission failed: {e}")
            return FissionResult(
                triggered=True,
                reason=reason,
                new_files={},
                original_file=file_path,
                success=False,
                error_message=str(e)
            )
    
    def _parse_fission_response(self, response: Any, original_file: str) -> Dict[str, str]:
        """
        Parse Gemini response to extract decomposed files.
        
        Args:
            response: Gemini API response
            original_file: Original file path
            
        Returns:
            Dictionary mapping file paths to content
        """
        if not (response.candidates and response.candidates[0].content.parts):
            logger.warning("Malformed response from Gemini")
            return {}
        
        text = response.candidates[0].content.parts[0].text.strip()
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            new_files = json.loads(text)
            
            # Validate structure
            if not isinstance(new_files, dict):
                logger.warning("Response is not a dictionary")
                return {}
            
            # Validate all values are strings
            for key, value in new_files.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    logger.warning(f"Invalid file mapping: {key} -> {type(value)}")
                    return {}
            
            return new_files
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {text[:500]}")
            return {}
    
    def handle_architect_output(self, output_text: str, mission_type: str, 
                                current_target: Optional[str] = None) -> bool:
        """
        L3 Orchestrator: Decides how to write L1 Cognition results to L4 State.
        
        Args:
            output_text: Output from SystemArchitect
            mission_type: "ATOMIC_FISSION" or "HEALING"
            current_target: Current file being processed
            
        Returns:
            True if successful, False otherwise
        """
        if mission_type == "ATOMIC_FISSION":
            try:
                # Parse the JSON map of new files
                fission_map = json.loads(output_text)
                
                for file_path, content in fission_map.items():
                    # Ensure parent directory exists
                    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    line_count = len(content.splitlines())
                    logger.info(f"  [Fission] Created: {file_path} ({line_count} lines)")
                
                logger.info(f"  ✅ Fission complete: {len(fission_map)} files created")
                return True
            
            except json.JSONDecodeError as e:
                logger.error(f"  [Error] L1 failed to return valid JSON for Fission: {e}")
                return False
            except Exception as e:
                logger.error(f"  [Error] Failed to write fission files: {e}")
                return False
        else:
            # Standard Single-File Heal Logic
            if current_target:
                try:
                    with open(current_target, 'w', encoding='utf-8') as f:
                        f.write(output_text)
                    logger.info(f"  [Healing] Updated: {current_target}")
                    return True
                except Exception as e:
                    logger.error(f"  [Error] Failed to write healed file: {e}")
                    return False
            else:
                logger.error("  [Error] No target file specified for healing")
                return False
    
    def write_decomposed_files(self, result: FissionResult) -> bool:
        """
        Write decomposed files to disk.
        
        Args:
            result: FissionResult with new files
            
        Returns:
            True if successful, False otherwise
        """
        if not result.success or not result.new_files:
            return False
        
        try:
            for file_path, content in result.new_files.items():
                new_path = Path(file_path)
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                line_count = len(content.splitlines())
                logger.info(f"   ✅ Created: {file_path} ({line_count} lines)")
            
            logger.info(f"   🎯 Fission complete: {len(result.new_files)} files created")
            return True
        
        except Exception as e:
            logger.error(f"   ❌ Failed to write decomposed files: {e}")
            return False


def get_fission_manager(gemini_client: Optional[Any] = None) -> FissionManager:
    """
    Factory function to create FissionManager instance.
    
    Args:
        gemini_client: Optional Gemini client
        
    Returns:
        FissionManager instance
    """
    return FissionManager(gemini_client=gemini_client)


# Integration Example for orchestrator_main.py:
"""
from agentic_core.infra.fission_manager import FissionManager
from agentic_core.infra.tui_dashboard import AgenticTUI

# Initialize managers
fission_manager = FissionManager()
tui = AgenticTUI()

# Inside healing loop:
trigger, reason = fission_manager.should_trigger_fission(
    file_path=target_file,
    current_round=round_count,
    last_error=error_msg,
    lines_deleted=deleted_lines
)

if trigger:
    # Update TUI to show fission mode
    tui.update_state(
        file=target_file,
        key="FISSION",
        round_num=round_count,
        tokens=token_count,
        log_msg=f"🚨 {reason}"
    )
    
    # Execute fission
    with open(target_file, 'r') as f:
        content = f.read()
    
    result = await fission_manager.execute_fission(
        file_path=target_file,
        content=content,
        reason=reason
    )
    
    if result.success:
        # Write decomposed files
        fission_manager.write_decomposed_files(result)
        
        # Update TUI
        tui.update_state(
            file=target_file,
            key="Key 42",
            round_num=round_count,
            tokens=token_count,
            log_msg=f"✅ Key 42 Resolved: Complexity distributed"
        )
"""
