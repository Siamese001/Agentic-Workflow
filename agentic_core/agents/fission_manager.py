"""
Fission Manager - Atomic Decomposition for Monolithic Files

When healing fails or would cause excessive deletions, the Fission Manager
decomposes large files into functionally cohesive sub-modules.

Strategy:
- Trigger on >110 line deletions (L5 Guardrail)
- Trigger on 3+ failed healing rounds (Cognitive Loop Stall)
- Use Gemini to intelligently decompose into sub-modules
- Maintain functional cohesion and import relationships
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Any

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
    Manages atomic fission decomposition of monolithic files.
    
    Triggers when:
    1. Healing would delete >110 lines (L5 Guardrail)
    2. 3+ healing rounds fail (Cognitive Loop Stall)
    
    Strategy:
    - Decompose into functionally cohesive sub-modules
    - Preserve import relationships
    - Maintain code functionality
    """
    
    def __init__(self, gemini_client: Optional[Any] = None):
        """
        Initialize Fission Manager.
        
        Args:
            gemini_client: Optional Gemini client (creates new if None)
        """
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
    
    def check_criteria(self, deleted_lines: int, round_count: int, success: bool) -> tuple[bool, str]:
        """
        Detects if a file needs Fission instead of Healing.
        
        Args:
            deleted_lines: Number of lines that would be deleted
            round_count: Current healing round number
            success: Whether healing succeeded
            
        Returns:
            Tuple of (should_trigger, reason)
        """
        # L5 Guardrail: Excessive deletions
        if deleted_lines > 110:
            return True, f"L5_GUARDRAIL_TRIGGERED: {deleted_lines} lines would be deleted (max 110)"
        
        # Cognitive Loop Stall: Multiple failed rounds
        if round_count >= 3 and not success:
            return True, f"COGNITIVE_LOOP_STALL: {round_count} rounds failed"
        
        return False, ""
    
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
            prompt = self._get_fission_prompt(file_path, content)
            
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
    
    def _get_fission_prompt(self, file_path: str, content: str) -> str:
        """
        Generates the mission instructions for decomposing the monolith.
        
        Args:
            file_path: Path to file being decomposed
            content: File content
            
        Returns:
            Fission prompt for Gemini
        """
        base_name = Path(file_path).stem
        parent_dir = Path(file_path).parent
        
        return f"""### MISSION: ATOMIC FISSION

The file `{file_path}` is too large for structural healing.
Decompose this monolith into functionally cohesive sub-modules.

ORIGINAL FILE CONTENT:
```python
{content}
```

DECOMPOSITION REQUIREMENTS:
1. Split into 3-5 functionally cohesive modules
2. Preserve all functionality - zero data loss
3. Maintain proper import relationships
4. Follow naming convention: {base_name}_<purpose>.py
5. Create a main module that imports and coordinates sub-modules

SUGGESTED DECOMPOSITION:
- {base_name}_core.py: Core classes and base functionality
- {base_name}_signals.py: Signal handling and event logic
- {base_name}_registry.py: Registry and lookup functionality
- {base_name}_utils.py: Utility functions
- {base_name}.py: Main coordination module (imports others)

OUTPUT FORMAT:
Return ONLY a valid JSON object mapping file paths to their content:
```json
{{
    "{parent_dir}/{base_name}_core.py": "# Core functionality\\n\\nclass CoreClass:\\n    pass",
    "{parent_dir}/{base_name}_signals.py": "# Signal handling\\n\\ndef handle_signal():\\n    pass",
    "{parent_dir}/{base_name}_registry.py": "# Registry\\n\\nclass Registry:\\n    pass",
    "{parent_dir}/{base_name}.py": "# Main coordination\\n\\nfrom .{base_name}_core import CoreClass\\nfrom .{base_name}_signals import handle_signal"
}}
```

CRITICAL:
- Return ONLY the JSON object, no markdown code blocks
- Ensure all imports are correct
- Preserve all original functionality
- Use relative imports where appropriate
"""
    
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
    
    def write_decomposed_files(self, result: FissionResult) -> bool:
        """
        Write decomposed files to disk and archive original.
        
        Args:
            result: FissionResult with new files
            
        Returns:
            True if successful, False otherwise
        """
        if not result.success or not result.new_files:
            return False
        
        try:
            # Archive original file
            original_path = Path(result.original_file)
            archive_path = original_path.with_suffix('.py.fission_archive')
            
            logger.info(f"   📦 Archiving original: {archive_path}")
            original_path.rename(archive_path)
            
            # Write new files
            for file_path, content in result.new_files.items():
                new_path = Path(file_path)
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"   ✅ Created: {file_path}")
            
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
