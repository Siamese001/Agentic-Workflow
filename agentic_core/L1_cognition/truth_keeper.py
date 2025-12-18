"""
TruthKeeper - Semantic Consistency & Docstring Alignment Agent

Ensures that function docstrings accurately match their implementation logic.
Uses Gemini LLM to analyze docstring-code consistency and auto-fix mismatches.
"""

import ast
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


class TruthKeeper:
    """
    Agent that ensures semantic consistency between docstrings and code.
    
    Analyzes functions to verify their docstrings accurately describe:
    - Parameters and their types
    - Return values and types
    - Function behavior and side effects
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize the TruthKeeper agent.
        
        Args:
            llm_client: LLM client for consistency checking
        """
        self.llm_client = llm_client
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
    async def check_file_consistency(self, file_path: str) -> Dict[str, Any]:
        """
        Check docstring consistency for all public functions in a file.
        
        Args:
            file_path: Path to the Python file to check
            
        Returns:
            Dictionary with consistency violations and fixes
        """
        violations = []
        fixes = []
        
        # Skip test files
        if "test" in file_path.lower() or file_path.endswith("_test.py"):
            return {"violations": [], "fixes": [], "skipped": True}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check each function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    result = await self._check_function_consistency(file_path, node, content)
                    
                    if result["violation"]:
                        violations.append(result["violation"])
                    
                    if result["fixed_docstring"]:
                        fixes.append({
                            "function": node.name,
                            "line": node.lineno,
                            "old_docstring": result.get("old_docstring"),
                            "new_docstring": result["fixed_docstring"]
                        })
        
        except SyntaxError as e:
            violations.append({
                "type": "syntax",
                "file": file_path,
                "message": f"Syntax error: {e}"
            })
        except Exception as e:
            LOGGER.error(f"Error checking {file_path}: {e}")
        
        return {
            "violations": violations,
            "fixes": fixes,
            "file": file_path
        }
    
    async def _check_function_consistency(self, file_path: str, node: ast.FunctionDef, content: str) -> Dict[str, Any]:
        """
        Check consistency for a single function.
        
        Args:
            file_path: Path to the file
            node: AST function node
            content: Full file content
            
        Returns:
            Dictionary with violation info and potential fix
        """
        # Extract function signature
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        returns = ast.get_docstring(node) is not None
        docstring = ast.get_docstring(node) or ""
        
        # Get function source
        func_lines = content.split('\n')[node.lineno-1:node.end_lineno]
        func_code = '\n'.join(func_lines)
        
        # Check if docstring exists
        if not docstring:
            return {
                "violation": {
                    "type": "missing_docstring",
                    "function": node.name,
                    "line": node.lineno,
                    "message": f"Function '{node.name}' missing docstring"
                },
                "fixed_docstring": await self._generate_docstring(node.name, args, func_code)
            }
        
        # Check consistency with LLM
        if self.api_key:
            consistency = await self._check_docstring_with_llm(node.name, args, docstring, func_code)
            
            if not consistency["matches"]:
                return {
                    "violation": {
                        "type": "inconsistent_docstring",
                        "function": node.name,
                        "line": node.lineno,
                        "message": f"Docstring doesn't match implementation: {consistency['reason']}"
                    },
                    "old_docstring": docstring,
                    "fixed_docstring": consistency["suggested_docstring"]
                }
        
        return {"violation": None, "fixed_docstring": None}
    
    async def _check_docstring_with_llm(self, func_name: str, args: List[str], 
                                      docstring: str, func_code: str) -> Dict[str, Any]:
        """
        Use Gemini to check if docstring matches implementation.
        
        Args:
            func_name: Name of the function
            args: List of argument names
            docstring: Current docstring
            func_code: Function implementation
            
        Returns:
            Dictionary with consistency check result
        """
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
You are a code documentation expert. Analyze if this docstring accurately describes the function.

Function: {func_name}
Arguments: {args}
Current Docstring:
\"\"\"
{docstring}
\"\"\"

Implementation:
```python
{func_code}
```

Questions:
1. Does the docstring correctly describe all parameters?
2. Does it correctly describe the return value?
3. Does it accurately describe what the function does?
4. Are there any side effects or exceptions not mentioned?

Respond with:
MATCHES: YES/NO
REASON: [Brief explanation]
CORRECTED_DOCSTRING:
[If NO, provide a corrected Google-style docstring. If YES, leave empty.]
"""
            
            response = model.generate_content(prompt)
            text = response.text
            
            # Parse response
            result = {"matches": False, "reason": "", "suggested_docstring": ""}
            
            for line in text.split('\n'):
                if line.startswith("MATCHES:"):
                    result["matches"] = "YES" in line.upper()
                elif line.startswith("REASON:"):
                    result["reason"] = line.replace("REASON:", "").strip()
                elif line.startswith("CORRECTED_DOCSTRING:"):
                    # Collect the rest as the docstring
                    idx = text.index(line)
                    docstring_text = text[idx + len("CORRECTED_DOCSTRING:"):].strip()
                    if docstring_text and docstring_text != "empty":
                        result["suggested_docstring"] = docstring_text
            
            return result
            
        except ImportError:
            LOGGER.warning("google.generativeai not installed - skipping LLM check")
            return {"matches": True, "reason": "LLM not available", "suggested_docstring": ""}
        except Exception as e:
            LOGGER.error(f"LLM check failed: {e}")
            return {"matches": True, "reason": "Error occurred", "suggested_docstring": ""}
    
    async def _generate_docstring(self, func_name: str, args: List[str], func_code: str) -> str:
        """
        Generate a docstring for a function using LLM.
        
        Args:
            func_name: Name of the function
            args: List of argument names
            func_code: Function implementation
            
        Returns:
            Generated Google-style docstring
        """
        if not self.api_key:
            # Return basic template
            args_str = ", ".join(args)
            return f"""\"\"\"{func_name}.

Args:
    {args_str}: Description of parameter.

Returns:
    Description of return value.
\"\"\""""
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
Generate a Google-style docstring for this function:

Function: {func_name}
Arguments: {args}

Implementation:
```python
{func_code}
```

Provide only the docstring, wrapped in triple quotes, following Google style:
- Brief description
- Args section with parameter descriptions
- Returns section if applicable
- Raises section if applicable
"""
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            LOGGER.error(f"Failed to generate docstring: {e}")
            # Return basic template
            args_str = "\n    ".join([f"{arg}: Description of parameter." for arg in args])
            return f'''"""{func_name}.

Args:
    {args_str}

Returns:
    Description of return value.
"""'''
    
    async def fix_file_docstrings(self, file_path: str, apply_fixes: bool = False) -> Dict[str, Any]:
        """
        Fix docstring issues in a file.
        
        Args:
            file_path: Path to the file
            apply_fixes: Whether to actually apply the fixes
            
        Returns:
            Dictionary with fix results
        """
        result = await self.check_file_consistency(file_path)
        
        if not result["fixes"]:
            return {"fixed": 0, "applied": False, "fixes": []}
        
        if apply_fixes:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply fixes
            lines = content.split('\n')
            
            for fix in result["fixes"]:
                func_name = fix["function"]
                line_num = fix["line"]
                new_docstring = fix["new_docstring"]
                
                # Find the function in the AST
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == func_name:
                        # Replace docstring
                        if ast.get_docstring(node):
                            # Find docstring start/end
                            start_line = node.lineno
                            if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                                docstring_node = node.body[0]
                                end_line = docstring_node.end_lineno
                                
                                # Replace lines
                                new_lines = new_docstring.split('\n')
                                lines[start_line-1:end_line] = new_lines
                                break
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            return {"fixed": len(result["fixes"]), "applied": True, "fixes": result["fixes"]}
        
        return {"fixed": len(result["fixes"]), "applied": False, "fixes": result["fixes"]}


# Global instance
_truth_keeper: Optional[TruthKeeper] = None


def get_truth_keeper() -> TruthKeeper:
    """Get or create the global TruthKeeper instance."""
    global _truth_keeper
    if _truth_keeper is None:
        _truth_keeper = TruthKeeper()
    return _truth_keeper


async def initialize_truth_keeper(llm_client=None):
    """
    Initialize the TruthKeeper system.
    
    Args:
        llm_client: LLM client instance
    """
    global _truth_keeper
    _truth_keeper = TruthKeeper(llm_client)
    LOGGER.info("TruthKeeper initialized")


# Convenience functions
async def check_docstring_consistency(file_path: str) -> Dict[str, Any]:
    """
    Check docstring consistency for a file.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        Consistency check results
    """
    keeper = get_truth_keeper()
    return await keeper.check_file_consistency(file_path)


async def fix_docstrings(file_path: str, apply: bool = False) -> Dict[str, Any]:
    """
    Fix docstring issues in a file.
    
    Args:
        file_path: Path to the file
        apply: Whether to apply the fixes
        
    Returns:
        Fix results
    """
    keeper = get_truth_keeper()
    return await keeper.fix_file_docstrings(file_path, apply_fixes=apply)
