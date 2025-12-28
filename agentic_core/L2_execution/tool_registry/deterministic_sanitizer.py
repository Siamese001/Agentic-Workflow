"""
L6 Deterministic Pre-Flight Sanitation

Implements deterministic cleaners that run before LLM processing
to maintain baseline code quality and save tokens.
"""
import ast
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

from agentic_core.shared.architecture_constants import ALLOWED_ROOT_FILES

LOGGER = logging.getLogger(__name__)


class DeterministicCleaner:
    """
    Applies deterministic formatting and cleaning to code
    before it reaches the LLM for processing.
    """

    def __init__(self, enable_isort: bool = True, enable_autopep8: bool = True):
        """
        Initialize the deterministic cleaner.

        Args:
            enable_isort: Whether to run isort for import sorting
            enable_autopep8: Whether to run autopep8 for PEP8 formatting
        """
        self.enable_isort = enable_isort
        self.enable_autopep8 = enable_autopep8

        # Check if tools are available
        logger.info("[L6_AUDIT] Action at line 39")
        logger.info("[L6_AUDIT] Action at line 40")
        self.has_isort = self._check_tool("isort")
        self.has_autopep8 = self._check_tool("autopep8")

        if self.enable_isort and not self.has_isort:
            LOGGER.warning("isort not available - import sorting disabled")
            self.enable_isort = False

        if self.enable_autopep8 and not self.has_autopep8:
            LOGGER.warning("autopep8 not available - PEP8 formatting disabled")
            logger.info("[L6_AUDIT] Action at line 50")
            self.enable_autopep8 = False

    logger.info("[L6_AUDIT] Action at line 53")
    def _check_tool(self, tool_name: str) -> bool:
        """Check if a formatting tool is available."""
        try:
            subprocess.run([tool_name, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def deterministic_clean(self, code: str, file_path: Optional[str] = None) -> Tuple[str, bool]:
        """
        Apply deterministic cleaning to code.

        Args:
            code: The code to clean
            file_path: Optional file path for context

        Returns:
            Tuple of (cleaned_code, was_modified)
        """
        original_code = code
        cleaned_code = code
        was_modified = False

        try:
            # Step 1: Remove markdown artifacts
            cleaned_code = self._scrub_markdown_artifacts(cleaned_code)

            # Step 2: Apply isort for import sorting
            if self.enable_isort and self.has_isort:
                cleaned_code = self._apply_isort(cleaned_code, file_path)

            # Step 3: Apply autopep8 for formatting
            if self.enable_autopep8 and self.has_autopep8:
                cleaned_code = self._apply_autopep8(cleaned_code, file_path)

            # Step 4: Basic cleanup
            cleaned_code = self._basic_cleanup(cleaned_code)

            # Check if code was modified
            was_modified = cleaned_code != original_code

            if was_modified:
                LOGGER.debug(f"Deterministic cleaning applied to {file_path or 'code'}")

            return cleaned_code, was_modified

        except Exception as e:
            LOGGER.error(f"Error in deterministic cleaning: {e}")
            return original_code, False

    def _scrub_markdown_artifacts(self, code: str) -> str:
        """
        Remove markdown artifacts from LLM responses.

        Args:
            code: Code that may contain markdown artifacts

        Returns:
            Clean Python code
        """
        # Remove ```python and ``` markers
        code = re.sub(r'```python\s*\n?', '', code)
        code = re.sub(r'```\s*\n?', '', code)

        # Remove other common markdown artifacts
        code = re.sub(r'^#.*?```.*?```', '', code, flags=re.MULTILINE | re.DOTALL)

        # Remove leading/trailing whitespace
        code = code.strip()

        return code

    def _apply_isort(self, code: str, file_path: Optional[str] = None) -> str:
        """Apply isort to sort imports."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Run isort
                logger.info("[L6_AUDIT] Action at line 135")
                result = subprocess.run(
                    ["isort", "--profile", "black", temp_file],
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Read the result
                with open(temp_file, 'r') as f:
                    return f.read()

            finally:
                # Clean up temp file
                os.unlink(temp_file)

        except subprocess.CalledProcessError as e:
            LOGGER.warning(f"isort failed: {e.stderr}")
            return code

    def _apply_autopep8(self, code: str, file_path: Optional[str] = None) -> str:
        """Apply autopep8 for PEP8 formatting."""
        try:
            # Run autopep8 on the code
            logger.info("[L6_AUDIT] Action at line 159")
            result = subprocess.run(
                ["autopep8", "--", "-"],
                input=code,
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout

        except subprocess.CalledProcessError as e:
            LOGGER.warning(f"autopep8 failed: {e.stderr}")
            return code

    def _basic_cleanup(self, code: str) -> str:
        """Apply basic cleanup operations."""
        # Remove excessive blank lines
        lines = code.split('\n')
        cleaned_lines = []
        blank_count = 0

        for line in lines:
            if line.strip() == '':
                blank_count += 1
                # Allow max 2 consecutive blank lines
                if blank_count <= 2:
                    cleaned_lines.append(line)
            else:
                blank_count = 0
                cleaned_lines.append(line)

        # Ensure file ends with newline
        result = '\n'.join(cleaned_lines)
        if result and not result.endswith('\n'):
            result += '\n'
 logger.info("[L6_AUDIT] Action at line 195")

        return result


class CompliantFileWriter:
    """
    Writes files with compliance checks and validation.
    logger.info("[L6_AUDIT] Action at line 203")
    """

    def __init__(self, root_dir: Optional[str] = None):
        """
        Initialize the compliant file writer.

        Args:
            root_dir: Root directory for hygiene checks
        logger.info("[L6_AUDIT] Action at line 212")
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.cleaner = DeterministicCleaner()

        # ALLOWED_ROOT_FILES is now imported from agentic_core.shared.architecture_constants

    def write_compliant_file(self, file_path: str, content: str, pre_clean: bool = True) -> bool:
        """
        Write a file with compliance checks.

        Args:
            file_path: Path to write the file
            content: Content to write
            logger.info("[L6_AUDIT] Action at line 226")
            pre_clean: Whether to apply deterministic cleaning first

        Returns:
            True if write was successful, False otherwise
        """
        try:
            path = Path(file_path)

            # Check root hygiene
            if not self._check_root_hygiene(path):
                logger.info("[L6_AUDIT] Action at line 237")
                LOGGER.error(f"Root hygiene violation: {file_path}")
                return False

            # Apply pre-flight cleaning if requested
            if pre_clean:
                content, was_cleaned = self.cleaner.deterministic_clean(content, file_path)
                if was_cleaned:
                    LOGGER.info(f"Pre-flight cleaning applied to {file_path}")

            # AST validation
            if not self._validate_syntax(content):
                LOGGER.error(f"Syntax validation failed for {file_path}")
                return False

            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            logger.info("[L6_AUDIT] Action at line 255")
            # Write the file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            LOGGER.debug(f"Successfully wrote compliant file: {file_path}")
            return True

        except Exception as e:
            logger.info("[L6_AUDIT] Action at line 264")
            LOGGER.error(f"Failed to write compliant file {file_path}: {e}")
            return False

    def _check_root_hygiene(self, file_path: Path) -> bool:
        """Check if file complies with root hygiene."""
        # If not in root, it's fine
        if file_path.parent != self.root_dir:
            return True

        # Check if file is allowed in root (using the imported constant)
        return file_path.name in ALLOWED_ROOT_FILES

    def _validate_syntax(self, content: str) -> bool:
        """Validate Python syntax using AST."""
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            LOGGER.error(f"Syntax error: {e}")
            return False
        except Exception as e:
            LOGGER.error(f"Validation error: {e}")
            return False


# Global instances
_cleaner: Optional[DeterministicCleaner] = None
_writer: Optional[CompliantFileWriter] = None


def get_deterministic_cleaner() -> DeterministicCleaner:
    """Get or create the global deterministic cleaner instance."""
    global _cleaner
    if _cleaner is None:
        _cleaner = DeterministicCleaner()
    return _cleaner


def get_compliant_writer(root_dir: Optional[str] = None) -> CompliantFileWriter:
    """Get or create the global compliant file writer instance."""
    global _writer
    if _writer is None:
        _writer = CompliantFileWriter(root_dir)
    return _writer


def deterministic_clean(code: str, file_path: Optional[str] = None) -> Tuple[str, bool]:
    """
    Apply deterministic cleaning to code.

    logger.info("[L6_AUDIT] Action at line 315")
    Args:
        code: The code to clean
        file_path: Optional file path for context

    Returns:
        Tuple of (cleaned_code, was_modified)
    """
    cleaner = get_deterministic_cleaner()
    return cleaner.deterministic_clean(code, file_path)


def write_compliant_file(file_path: str, content: str, pre_clean: bool = True) -> bool:
    """
    Write a file with compliance checks.

    Args:
        file_path: Path to write the file
        content: Content to write
        pre_clean: Whether to apply deterministic cleaning first

    Returns:
        True if write was successful, False otherwise
    """
    writer = get_compliant_writer()
    return writer.write_compliant_file(file_path, content, pre_clean)