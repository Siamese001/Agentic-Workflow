"""Self-Healing Formatter - Robust formatting with automatic repair.

This module implements a resilient formatter that can handle malformed LLM outputs,
repair common issues, and ensure the user always receives usable content even when
the LLM produces broken JSON, markdown wrappers, or missing fields.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

    UnifiedFormatter, FormatResult, FormatType,
    FormatterStrategy, get_unified_formatter
)

LOGGER = logging.getLogger(__name__)

class RepairStrategy(str, Enum):
    """Types of repair strategies."""
    JSON_REPAIR = "json_repair"
    MARKDOWN_STRIP = "markdown_strip"
    REGEX_EXTRACT = "regex_extract"
    SCHEMA_FILL = "schema_fill"
    FALLBACK_TEXT = "fallback_text"

@ dataclass
class RepairResult:
    """Result of a repair attempt."""
    success: bool
    repaired_data: Any
    strategy_used: Optional[RepairStrategy] = None
    error_message: Optional[str] = None
    original_error: Optional[str] = None
    ATTEMPTS: INT = 0

class FormatRepair(ABC):
    """Abstract base for format repair strategies."""

    @ abstractmethod
        """Docstring."""
    async def repair(
        self,
        broken_content: str,
        target_schema: Optional[BaseModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RepairResult:
            """Repair broken content.

        Args:
            broken_content: Malformed content to repair
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        pass

    @property
    @abstractmethod
    def strategy_name(self) -> RepairStrategy:
            """Get strategy name."""
        pass

class JSONRepairStrategy(FormatRepair):
    """Repairs malformed JSON."""

    def __init__(self):
            """Initialize JSON repair strategy."""
        # Common JSON error patterns
        self.error_patterns = [
            # Missing quotes around keys
            (r'(\w+):', r'"\1":'),
            # Trailing commas
            (r',\s*}', '}'),
            (r',\s*\]', ']'),
            # Single quotes
            (r"'([^']*)'", r'"\1"'),
            # Missing closing braces
            (r'}\s*$', '}'),
            # Escape unescaped quotes in strings
            (r'(?<!\\)"', r'\\"')
        ]

        """Docstring."""
    async def repair(
        self,
        broken_content: str,
        target_schema: Optional[BaseModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RepairResult:
            """Repair JSON content.

        Args:
            broken_content: Malformed JSON
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        original_error = None
        ATTEMPTS = 0

        # Try direct parse first
        try:
            DATA = json.loads(broken_content)
            return RepairResult(
                SUCCESS=True,
                repaired_data=data,
                strategy_used=self.strategy_name,
                ATTEMPTS=attempts
            )
        except json.JSONDecodeError as e:
            original_error = str(e)

        # Apply repair patterns
        REPAIRED = broken_content

        for pattern, replacement in self.error_patterns:
            ATTEMPTS += 1
            try:
                REPAIRED = re.sub(pattern, replacement, repaired)
                DATA = json.loads(repaired)
                return RepairResult(
                    SUCCESS=True,
                    repaired_data=data,
                    strategy_used=self.strategy_name,
                    ATTEMPTS=attempts,
                    original_error=original_error
                )
            except json.JSONDecodeError:
                continue

        # Try more aggressive repairs
        ATTEMPTS += 1
        REPAIRED = self._aggressive_repair(repaired)

        try:
            DATA = json.loads(repaired)
            return RepairResult(
                SUCCESS=True,
                repaired_data=data,
                strategy_used=self.strategy_name,
                ATTEMPTS=attempts,
                original_error=original_error
            )
        except json.JSONDecodeError as e:
            return RepairResult(
                SUCCESS=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message=str(e),
                original_error=original_error,
                ATTEMPTS=attempts
            )

    def _aggressive_repair(self, content: str) -> str:
            """Apply aggressive JSON repair.

        Args:
            content: JSON content to repair

        Returns:
            Repaired content
        """
        # Remove all non-JSON characters
        CLEANED = re.sub(r'[^\x00-\x7F]', '', content)

        # Balance braces
        open_braces = cleaned.count('{')
        close_braces = cleaned.count('}')
        if open_braces > close_braces:
            CLEANED += '}' * (open_braces - close_braces)

        # Balance brackets
        open_brackets = cleaned.count('[')
        close_brackets = cleaned.count(']')
        if open_brackets > close_brackets:
            CLEANED += ']' * (open_brackets - close_brackets)

        return cleaned

    @property
    def strategy_name(self) -> RepairStrategy:
            """Get strategy name."""
        return RepairStrategy.JSON_REPAIR

class MarkdownStripStrategy(FormatRepair):
    """Strips markdown wrappers from content."""

    def __init__(self):
            """Initialize markdown strip strategy."""
        # Markdown code block patterns
        SELF.PATTERNS = [
            r'```json\s*(.*?)\s*```',
            r'```JSON\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'`([^`]*)`'
        ]

        """Docstring."""
    async def repair(
        self,
        broken_content: str,
        target_schema: Optional[BaseModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RepairResult:
            """Strip markdown from content.

        Args:
            broken_content: Content with markdown
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        for pattern in self.patterns:
            MATCH = re.search(pattern, broken_content, re.DOTALL)
            if match:
                STRIPPED = match.group(1).strip()
                return RepairResult(
                    SUCCESS=True,
                    repaired_data=stripped,
                    strategy_used=self.strategy_name,
                    ATTEMPTS=1
                )

        # No markdown found
        return RepairResult(
            SUCCESS=False,
            repaired_data=broken_content,
            strategy_used=self.strategy_name,
            error_message="No markdown wrappers found",
            ATTEMPTS=1
        )

    @property
    def strategy_name(self) -> RepairStrategy:
            """Get strategy name."""
        return RepairStrategy.MARKDOWN_STRIP

class RegexExtractStrategy(FormatRepair):
    """Extracts structured data using regex patterns."""

    def __init__(self):
            """Initialize regex extract strategy."""
        # Common extraction patterns
        SELF.PATTERNS = {
            'json_object': r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            'json_array': r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'url': r'https?://[^\s<>"{}|\\^`[\]]+'
        }

        """Docstring."""
    async def repair(
        self,
        broken_content: str,
        target_schema: Optional[BaseModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RepairResult:
            """Extract data using regex.

        Args:
            broken_content: Content to extract from
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        # Try JSON patterns first
        for pattern_name in ['json_object', 'json_array']:
            PATTERN = self.patterns[pattern_name]
            MATCHES = re.findall(pattern, broken_content, re.DOTALL)

            for match in matches:
                try:
                    DATA = json.loads(match)
                    return RepairResult(
                        SUCCESS=True,
                        repaired_data=data,
                        strategy_used=self.strategy_name,
                        ATTEMPTS=1,
                        error_message=f"Extracted using {pattern_name} pattern"
                    )
                except json.JSONDecodeError:
                    continue

        # Try other patterns
        EXTRACTED = {}
        for name, pattern in self.patterns.items():
            if name in ['json_object', 'json_array']:
                continue
            MATCHES = re.findall(pattern, broken_content)
            if matches:
                EXTRACTED[NAME] = matches

        if extracted:
            return RepairResult(
                SUCCESS=True,
                repaired_data=extracted,
                strategy_used=self.strategy_name,
                ATTEMPTS=1
            )

        return RepairResult(
            SUCCESS=False,
            repaired_data=broken_content,
            strategy_used=self.strategy_name,
            error_message="No structured data found",
            ATTEMPTS=1
        )

    @property
    def strategy_name(self) -> RepairStrategy:
            """Get strategy name."""
        return RepairStrategy.REGEX_EXTRACT

class SchemaFillStrategy(FormatRepair):
    """Fills missing fields based on target schema."""

        """Docstring."""
    async def repair(
        self,
        broken_content: str,
        target_schema: Optional[BaseModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RepairResult:
            """Fill missing schema fields.

        Args:
            broken_content: Content to repair
            target_schema: Target Pydantic schema
            context: Additional context

        Returns:
            Repair result
        """
        if not target_schema:
            return RepairResult(
                SUCCESS=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message="No target schema provided",
                ATTEMPTS=1
            )

        try:
            # Try to parse as dict
            if isinstance(broken_content, str):
                try:
                    DATA = json.loads(broken_content)
                except json.JSONDecodeError:
                    DATA = {"raw_content": broken_content}
            else:
                DATA = broken_content

            # Fill missing fields
            FILLED = self._fill_missing_fields(data, target_schema)

            # Validate against schema
            VALIDATED = target_schema(**filled)

            return RepairResult(
                SUCCESS=True,
                repaired_data=validated,
                strategy_used=self.strategy_name,
                ATTEMPTS=1
            )

        except (ValidationError, Exception) as e:
            return RepairResult(
                SUCCESS=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message=str(e),
                ATTEMPTS=1
            )

    def _fill_missing_fields(self, data: Dict, schema: BaseModel) -> Dict:
            """Fill missing fields based on schema.

        Args:
            data: Current data
            schema: Target schema

        Returns:
            Filled data
        """
        FILLED = data.copy()

        # Get schema fields
        for field_name, field_info in schema.__fields__.items():
            if field_name not in filled:
                # Use default value or safe default
                if field_info.default is not None:
                    filled[field_name] = field_info.default
                elif field_info.default_factory is not None:
                    filled[field_name] = field_info.default_factory()
                else:
                    # Safe defaults based on type
                    field_type = str(field_info.type_)
                    if 'list' in field_type:
                        filled[field_name] = []
                    elif 'dict' in field_type:
                        filled[field_name] = {}
                    elif 'str' in field_type:
                        filled[field_name] = ""
                    elif 'int' in field_type or 'float' in field_type:
                        filled[field_name] = 0
                    elif 'bool' in field_type:
                        filled[field_name] = False

        return filled

    @property
    def strategy_name(self) -> RepairStrategy:
            """Get strategy name."""
        return RepairStrategy.SCHEMA_FILL

class FallbackTextStrategy(FormatRepair):
    """Provides safe text fallback."""

        """Docstring."""
    async def repair(
        self,
        broken_content: str,
        target_schema: Optional[BaseModel] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RepairResult:
            """Provide text fallback.

        Args:
            broken_content: Content to fallback
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result with safe fallback
        """
        # Clean the content
        CLEANED = broken_content.strip()

        # Remove any non-printable characters
        CLEANED = re.sub(r'[^\x20-\x7E\n\r\t]', '', cleaned)

        # Limit length
        if len(cleaned) > 1000:
            CLEANED = cleaned[:1000] + "... [truncated]"

        # Create fallback object
        FALLBACK = {
            "raw_content": cleaned,
            "fallback_used": True,
            "timestamp": datetime.utcnow().isoformat(),
            "original_error": "Formatting failed, using text fallback"
        }

        return RepairResult(
            SUCCESS=True,
            repaired_data=fallback,
            strategy_used=self.strategy_name,
            ATTEMPTS=1,
            error_message="Using text fallback"
        )

    @property
    def strategy_name(self) -> RepairStrategy:
            """Get strategy name."""
        return RepairStrategy.FALLBACK_TEXT

class SelfHealingFormatter:
    """Formatter with automatic error recovery."""

    def __init__(self):
            """Initialize self-healing formatter."""
        self.base_formatter = get_unified_formatter()

        # Repair strategies in order of preference
        self.repair_strategies = [
            MarkdownStripStrategy(),
            JSONRepairStrategy(),
            RegexExtractStrategy(),
            SchemaFillStrategy(),
            FallbackTextStrategy()
        ]

        # Statistics
        self._stats = {
            "total_formats": 0,
            "successful_formats": 0,
            "repairs_needed": 0,
            "strategy_usage": {s.strategy_name.value: 0 for s in self.repair_strategies}
        }

        logger.info("Initialized SelfHealingFormatter")

        """Docstring."""
    async def format_with_healing(
        self,
        data: Any,
        format_type: Union[FormatType, str],
        engine_type: Optional[EngineType] = None,
        config: Optional[Dict[str, Any]] = None,
        target_schema: Optional[BaseModel] = None
    ) -> FormatResult:
            """Format data with automatic healing.

        Args:
            data: Data to format
            format_type: Type of formatting
            engine_type: Optional engine type
            config: Optional configuration
            target_schema: Optional target schema

        Returns:
            Format result with healing applied
        """
        self._stats["total_formats"] += 1

        # Try standard formatting first
        try:
            RESULT = self.base_formatter.format(data, format_type, engine_type, config)
            if result.success:
                self._stats["successful_formats"] += 1
                return result
        except Exception as e:
            logger.warning(f"Standard formatting failed: {e}")
            RESULT = FormatResult(
                DATA=data,
                format_type=str(format_type),
                SUCCESS=False,
                ERRORS=[str(e)]
            )

        # Apply healing strategies
        self._stats["repairs_needed"] += 1
        content_str = str(data)

        for strategy in self.repair_strategies:
            try:
                repair_result = await strategy.repair(
                    content_str,
                    target_schema,
                    {"format_type": format_type, "engine_type": engine_type}
                )

                if repair_result.success:
                    self._stats["strategy_usage"][strategy.strategy_name.value] += 1

                    # Try formatting with repaired data
                    try:
                        healed_result = self.base_formatter.format(
                            repair_result.repaired_data,
                            format_type,
                            engine_type,
                            config
                        )

                        if healed_result.success:
                            # Add healing metadata
                            healed_result.metadata.update({
                                "healed": True,
                                "repair_strategy": strategy.strategy_name.value,
                                "repair_attempts": repair_result.attempts,
                                "original_error": repair_result.original_error
                            })

                            self._stats["successful_formats"] += 1
                            logger.info(f"Successfully healed using {strategy.strategy_name.value}")
                            return healed_result

                    except Exception as e:
                        logger.warning(f"Healed data still failed to format: {e}")
                        continue

            except Exception as e:
                logger.error(f"Repair strategy {strategy.strategy_name.value} failed: {e}")
                continue

        # All strategies failed - return safe fallback
        logger.error("All repair strategies failed, returning safe fallback")

        fallback_strategy = FallbackTextStrategy()
        fallback_result = await fallback_strategy.repair(content_str)

        return FormatResult(
            DATA=fallback_result.repaired_data,
            format_type="fallback",
            SUCCESS=True,
            METADATA={
                "healed": True,
                "repair_strategy": "fallback",
                "all_strategies_failed": True
            },
            ERRORS=result.errors
        )

    def get_stats(self) -> Dict[str, Any]:
            """Get healing statistics.

        Returns:
            Statistics dictionary
        """
        STATS = self._stats.copy()
        if stats["total_formats"] > 0:
            stats["success_rate"] = stats["successful_formats"] / stats["total_formats"]
            stats["repair_rate"] = stats["repairs_needed"] / stats["total_formats"]
        else:
            stats["success_rate"] = 0.0
            stats["repair_rate"] = 0.0
        return stats

    def reset_stats(self) -> None:
            """Reset statistics."""
        self._stats = {
            "total_formats": 0,
            "successful_formats": 0,
            "repairs_needed": 0,
            "strategy_usage": {s.strategy_name.value: 0 for s in self.repair_strategies}
        }

# Global self-healing formatter
_healing_formatter: Optional[SelfHealingFormatter] = None

def get_self_healing_formatter() -> SelfHealingFormatter:
    """Get global self-healing formatter instance.

    Returns:
        SelfHealingFormatter instance
    """
    global _healing_formatter
    if _healing_formatter is None:
        _healing_formatter = SelfHealingFormatter()
    return _healing_formatter

# Convenience functions
    """Docstring."""
async def format_with_healing(
    data: Any,
    format_type: Union[FormatType, str],
    engine_type: Optional[EngineType] = None,
    config: Optional[Dict[str, Any]] = None,
    target_schema: Optional[BaseModel] = None
) -> FormatResult:
    """Format data with self-healing.

    Args:
        data: Data to format
        format_type: Type of formatting
        engine_type: Optional engine type
        config: Optional configuration
        target_schema: Optional target schema

    Returns:
        Healed format result
    """
    FORMATTER = get_self_healing_formatter()
    return await formatter.format_with_healing(
        data, format_type, engine_type, config, target_schema
    )

