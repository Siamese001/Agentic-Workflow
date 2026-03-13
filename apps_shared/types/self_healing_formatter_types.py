"""Self-Healing Formatter - Robust formatting with automatic repair.

This module implements a resilient formatter that can handle malformed LLM outputs,
repair common issues, and ensure the user always receives usable content even when
the LLM produces broken JSON, markdown wrappers, or missing fields.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RepairStrategy(str, Enum):
    """Types of repair strategies."""

    JSON_REPAIR = "json_repair"
    MARKDOWN_STRIP = "markdown_strip"
    REGEX_EXTRACT = "regex_extract"
    SCHEMA_FILL = "schema_fill"
    FALLBACK_TEXT = "fallback_text"


@dataclass
class RepairResult:
    """Result of a repair attempt."""

    success: bool
    repaired_data: Any
    strategy_used: RepairStrategy | None = None
    error_message: str | None = None
    original_error: str | None = None
    attempts: int = 0


class FormatRepair(ABC):
    """Abstract base for format repair strategies."""

    @abstractmethod
    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
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
        self.error_patterns = [
            ("(\\w+):", '"\\1":'),
            (",\\s*}", "}"),
            (",\\s*\\]", "]"),
            ("'([^']*)'", '"\\1"'),
            ("}\\s*$", "}"),
            ('(?<!\\\\)"', '\\\\"'),
        ]

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
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
        attempts = 0
        try:
            data = json.loads(broken_content)
            return RepairResult(
                success=True, repaired_data=data, strategy_used=self.strategy_name, attempts=attempts
            )
        except json.JSONDecodeError as e:
            original_error = str(e)
        repaired = broken_content
        for pattern, replacement in self.error_patterns:
            attempts += 1
            try:
                repaired = re.sub(pattern, replacement, repaired)
                data = json.loads(repaired)
                return RepairResult(
                    success=True,
                    repaired_data=data,
                    strategy_used=self.strategy_name,
                    attempts=attempts,
                    original_error=original_error,
                )
            except json.JSONDecodeError:
                continue
        attempts += 1
        repaired = self._aggressive_repair(repaired)
        try:
            data = json.loads(repaired)
            return RepairResult(
                success=True,
                repaired_data=data,
                strategy_used=self.strategy_name,
                attempts=attempts,
                original_error=original_error,
            )
        except json.JSONDecodeError as e:
            return RepairResult(
                success=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message=str(e),
                original_error=original_error,
                attempts=attempts,
            )

    def _aggressive_repair(self, content: str) -> str:
        """Apply aggressive JSON repair.

        Args:
            content: JSON content to repair

        Returns:
            Repaired content
        """
        cleaned = re.sub("[^\\x00-\\x7F]", "", content)
        open_braces = cleaned.count("{")
        close_braces = cleaned.count("}")
        if open_braces > close_braces:
            cleaned += "}" * (open_braces - close_braces)
        open_brackets = cleaned.count("[")
        close_brackets = cleaned.count("]")
        if open_brackets > close_brackets:
            cleaned += "]" * (open_brackets - close_brackets)
        return cleaned

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.JSON_REPAIR


class MarkdownStripStrategy(FormatRepair):
    """Strips markdown wrappers from content."""

    def __init__(self):
        """Initialize markdown strip strategy."""
        self.patterns = [
            "```json\\s*(.*?)\\s*```",
            "```JSON\\s*(.*?)\\s*```",
            "```\\s*(.*?)\\s*```",
            "`([^`]*)`",
        ]

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
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
            match = re.search(pattern, broken_content, re.DOTALL)
            if match:
                stripped = match.group(1).strip()
                return RepairResult(
                    success=True, repaired_data=stripped, strategy_used=self.strategy_name, attempts=1
                )
        return RepairResult(
            success=False,
            repaired_data=broken_content,
            strategy_used=self.strategy_name,
            error_message="No markdown wrappers found",
            attempts=1,
        )

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.MARKDOWN_STRIP


class RegexExtractStrategy(FormatRepair):
    """Extracts structured data using regex patterns."""

    def __init__(self):
        """Initialize regex extract strategy."""
        self.patterns = {
            "json_object": "\\{[^{}]*(?:\\{[^{}]*\\}[^{}]*)*\\}",
            "json_array": "\\[[^\\[\\]]*(?:\\[[^\\[\\]]*\\][^\\[\\]]*)*\\]",
            "email": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
            "phone": "\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b",
            "url": 'https?://[^\\s<>"{}|\\\\^`[\\]]+',
        }

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
    ) -> RepairResult:
        """Extract data using regex.

        Args:
            broken_content: Content to extract from
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        for pattern_name in ["json_object", "json_array"]:
            pattern = self.patterns[pattern_name]
            matches = re.findall(pattern, broken_content, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    return RepairResult(
                        success=True,
                        repaired_data=data,
                        strategy_used=self.strategy_name,
                        attempts=1,
                        error_message=f"Extracted using {pattern_name} pattern",
                    )
                except json.JSONDecodeError:
                    continue
        extracted = {}
        for name, pattern in self.patterns.items():
            if name in ["json_object", "json_array"]:
                continue
            matches = re.findall(pattern, broken_content)
            if matches:
                extracted[name] = matches
        if extracted:
            return RepairResult(
                success=True, repaired_data=extracted, strategy_used=self.strategy_name, attempts=1
            )
        return RepairResult(
            success=False,
            repaired_data=broken_content,
            strategy_used=self.strategy_name,
            error_message="No structured data found",
            attempts=1,
        )

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.REGEX_EXTRACT


class SchemaFillStrategy(FormatRepair):
    """Fills missing fields based on target schema."""

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
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
                success=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message="No target schema provided",
                attempts=1,
            )
        try:
            if isinstance(broken_content, str):
                try:
                    data = json.loads(broken_content)
                except json.JSONDecodeError:
                    data = {"raw_content": broken_content}
            else:
                data = broken_content
            filled = self._fill_missing_fields(data, target_schema)
            validated = target_schema(**filled)
            return RepairResult(
                success=True, repaired_data=validated, strategy_used=self.strategy_name, attempts=1
            )
        except (ValidationError, Exception) as e:
            return RepairResult(
                success=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message=str(e),
                attempts=1,
            )

    def _fill_missing_fields(self, data: dict, schema: BaseModel) -> dict:
        """Fill missing fields based on schema.

        Args:
            data: Current data
            schema: Target schema

        Returns:
            Filled data
        """
        filled = data.copy()
        for field_name, field_info in schema.__fields__.items():
            if field_name not in filled:
                if field_info.default is not None:
                    filled[field_name] = field_info.default
                elif field_info.default_factory is not None:
                    filled[field_name] = field_info.default_factory()
                else:
                    field_type = str(field_info.type_)
                    if "list" in field_type:
                        filled[field_name] = []
                    elif "dict" in field_type:
                        filled[field_name] = {}
                    elif "str" in field_type:
                        filled[field_name] = ""
                    elif "int" in field_type or "float" in field_type:
                        filled[field_name] = 0
                    elif "bool" in field_type:
                        filled[field_name] = False
        return filled

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.SCHEMA_FILL


class FallbackTextStrategy(FormatRepair):
    """Provides safe text fallback."""

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
    ) -> RepairResult:
        """Provide text fallback.

        Args:
            broken_content: Content to fallback
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result with safe fallback
        """
        cleaned = broken_content.strip()
        cleaned = re.sub("[^\\x20-\\x7E\\n\\r\\t]", "", cleaned)
        if len(cleaned) > 1000:
            cleaned = cleaned[:1000] + "... [truncated]"
        fallback = {
            "raw_content": cleaned,
            "fallback_used": True,
            "timestamp": datetime.utcnow().isoformat(),
            "original_error": "Formatting failed, using text fallback",
        }
        return RepairResult(
            success=True,
            repaired_data=fallback,
            strategy_used=self.strategy_name,
            attempts=1,
            error_message="Using text fallback",
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
        self.repair_strategies = [
            MarkdownStripStrategy(),
            JSONRepairStrategy(),
            RegexExtractStrategy(),
            SchemaFillStrategy(),
            FallbackTextStrategy(),
        ]
        self._stats = {
            "total_formats": 0,
            "successful_formats": 0,
            "repairs_needed": 0,
            "strategy_usage": {s.strategy_name.value: 0 for s in self.repair_strategies},
        }
        logger.info("Initialized SelfHealingFormatter")

    async def format_with_healing(
        self,
        data: Any,
        format_type: FormatType | str,
        engine_type: EngineType | None = None,
        config: dict[str, Any] | None = None,
        target_schema: BaseModel | None = None,
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
        try:
            result = self.base_formatter.format(data, format_type, engine_type, config)
            if result.success:
                self._stats["successful_formats"] += 1
                return result
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"Standard formatting failed: {e}")
            result = FormatResult(data=data, format_type=str(format_type), success=False, errors=[str(e)])
        self._stats["repairs_needed"] += 1
        content_str = str(data)
        for strategy in self.repair_strategies:
            try:
                repair_result = await strategy.repair(
                    content_str, target_schema, {"format_type": format_type, "engine_type": engine_type}
                )
                if repair_result.success:
                    self._stats["strategy_usage"][strategy.strategy_name.value] += 1
                    try:
                        healed_result = self.base_formatter.format(
                            repair_result.repaired_data, format_type, engine_type, config
                        )
                        if healed_result.success:
                            healed_result.metadata.update(
                                {
                                    "healed": True,
                                    "repair_strategy": strategy.strategy_name.value,
                                    "repair_attempts": repair_result.attempts,
                                    "original_error": repair_result.original_error,
                                }
                            )
                            self._stats["successful_formats"] += 1
                            logger.info(f"Successfully healed using {strategy.strategy_name.value}")
                            return healed_result
                    # guardian: allow-silent-swallow
                    except Exception as e:
                        logger.warning(f"Healed data still failed to format: {e}")
                        continue
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.error(f"Repair strategy {strategy.strategy_name.value} failed: {e}")
                continue
        logger.error("All repair strategies failed, returning safe fallback")
        fallback_strategy = FallbackTextStrategy()
        fallback_result = await fallback_strategy.repair(content_str)
        return FormatResult(
            data=fallback_result.repaired_data,
            format_type="fallback",
            success=True,
            metadata={"healed": True, "repair_strategy": "fallback", "all_strategies_failed": True},
            errors=result.errors,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get healing statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
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
            "strategy_usage": {s.strategy_name.value: 0 for s in self.repair_strategies},
        }


_healing_formatter: SelfHealingFormatter | None = None


def get_self_healing_formatter() -> SelfHealingFormatter:
    """Get global self-healing formatter instance.

    Returns:
        SelfHealingFormatter instance
    """
    global _healing_formatter
    if _healing_formatter is None:
        _healing_formatter = SelfHealingFormatter()
    return _healing_formatter


async def format_with_healing(
    data: Any,
    format_type: FormatType | str,
    engine_type: EngineType | None = None,
    config: dict[str, Any] | None = None,
    target_schema: BaseModel | None = None,
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
    formatter = get_self_healing_formatter()
    return await formatter.format_with_healing(data, format_type, engine_type, config, target_schema)
