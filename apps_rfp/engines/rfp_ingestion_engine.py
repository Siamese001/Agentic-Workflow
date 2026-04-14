"""
RFP Document Ingestion Engine — apps_rfp.enterprise.

Parses RFP documents from multiple formats (PDF, DOCX, TXT, MD)
and extracts structured requirements, constraints, and evaluation criteria.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from apps_rfp._compat.lifecycle_trace import (
    _emit_captures_pattern,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)
from tqdm import tqdm

_log = logging.getLogger(__name__)


class DocumentParser(Protocol):
    """Protocol for RFP document parsers."""

    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the file."""
        ...

    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse the document and return structured content."""
        ...


@dataclass(frozen=True)
class ParsedDocument:
    """Structured content extracted from an RFP document."""

    source_path: str
    file_type: str
    raw_text: str
    title: str = ""
    organization: str = ""
    submission_deadline: str = ""
    sections: dict[str, str] = field(default_factory=dict)
    requirements: list[Requirement] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    evaluation_criteria: list[EvalCriterion] = field(default_factory=list)


@dataclass(frozen=True)
class Requirement:
    """Structured requirement extracted from RFP."""

    req_id: str
    category: str  # functional, technical, security, compliance
    priority: str  # mandatory, preferred, optional
    text: str
    section_ref: str = ""  # Reference to original section


@dataclass(frozen=True)
class Constraint:
    """Constraint or limitation specified in RFP."""

    constraint_id: str
    category: str  # budget, timeline, technical, legal
    description: str


@dataclass(frozen=True)
class EvalCriterion:
    """Evaluation criterion from RFP."""

    criterion_id: str
    category: str  # technical, commercial, experience
    weight: float  # 0-100
    description: str


class PlainTextParser:
    """Parser for plain text (.txt) and markdown (.md) files."""

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".txt", ".md", ".markdown"}

    def parse(self, file_path: Path) -> ParsedDocument:
        _emit_records_execution_trace("enterprise", "PlainTextParser", "parse_start")

        raw_text = file_path.read_text(encoding="utf-8", errors="ignore")

        # Extract title from first heading or first line
        title = self._extract_title(raw_text)
        org = self._extract_organization(raw_text)
        deadline = self._extract_deadline(raw_text)

        # Parse sections
        sections = self._parse_sections(raw_text)

        # Extract requirements
        requirements = self._extract_requirements(raw_text, sections)
        constraints = self._extract_constraints(raw_text, sections)
        criteria = self._extract_eval_criteria(raw_text, sections)

        _emit_captures_pattern("enterprise", "PlainTextParser", "parse_complete")

        return ParsedDocument(
            source_path=str(file_path),
            file_type=file_path.suffix[1:],
            raw_text=raw_text,
            title=title,
            organization=org,
            submission_deadline=deadline,
            sections=sections,
            requirements=requirements,
            constraints=constraints,
            evaluation_criteria=criteria,
        )

    def _extract_title(self, text: str) -> str:
        # Try markdown heading first
        if match := re.search(r"^#\s+(.+)$", text, re.MULTILINE):
            return match.group(1).strip()
        # Fallback to first non-empty line
        for line in text.split("\n"):
            if line.strip():
                return line.strip()[:100]
        return "Untitled RFP"

    def _extract_organization(self, text: str) -> str:
        patterns = [
            r"(?:issued by|from|organization|client)[:\s]+([A-Z][A-Za-z\s&]+(?:Inc\.?|LLC|Corp\.?|Ltd\.?)?)",
            r"([A-Z][A-Za-z\s]+(?:Department|Agency|Authority))",
        ]
        for pattern in patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                return match.group(1).strip()
        return ""

    def _extract_deadline(self, text: str) -> str:
        patterns = [
            r"(?:deadline|due date|submission date)[:\s]+([A-Za-z0-9,\s/\-]+(?:202\d|202\d))",
            r"(\d{1,2}[/-]\d{1,2}[/-]202\d)",
        ]
        for pattern in patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                return match.group(1).strip()
        return ""

    def _parse_sections(self, text: str) -> dict[str, str]:
        """Parse document into sections based on headings."""
        sections: dict[str, str] = {}
        current_section = "intro"
        current_content: list[str] = []

        for line in text.split("\n"):
            # Check for markdown heading
            if match := re.match(r"^(#{1,3})\s+(.+)$", line):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = match.group(2).strip().lower().replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)

        # Save final section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _extract_requirements(self, text: str, sections: dict[str, str]) -> list[Requirement]:
        """Extract requirements from RFP text."""
        requirements: list[Requirement] = []
        req_counter = 1

        # Look in requirements section
        req_section = sections.get("requirements", sections.get("scope", text))

        # Pattern: numbered requirements, bullet points with must/shall/will
        patterns = [
            r"(?:^|\n)(?:\d+[.\)])\s+([^\n]+(?:must|shall|will|required)[^\n]*\.?)",
            r"(?:^|\n)[\-\*]\s+([^\n]+(?:must|shall|will|required)[^\n]*\.?)",
            r"(?:mandatory|required)\s*[:\-\s]*([^\n]+\.?)",
        ]

        for pattern in tqdm(patterns, desc="Processing", unit="item"):
            for match in tqdm(
                re.finditer(pattern, req_section, re.IGNORECASE), desc="Processing", unit="item"
            ):
                req_text = match.group(1).strip()
                if len(req_text) > 10:  # Filter out noise
                    requirements.append(
                        Requirement(
                            req_id=f"R{req_counter:03d}",
                            category=self._classify_requirement(req_text),
                            priority="mandatory" if "must" in req_text.lower() else "preferred",
                            text=req_text,
                        ),
                    )
                    req_counter += 1

        return requirements

    def _extract_constraints(self, text: str, sections: dict[str, str]) -> list[Constraint]:
        """Extract constraints from RFP."""
        constraints: list[Constraint] = []
        c_counter = 1

        constraint_section = sections.get("constraints", sections.get("limitations", text))

        # Budget constraints
        if match := re.search(
            r"(?:budget|cost|price)[:\s]*[$]?([\d,]+(?:K|M|B)?)", constraint_section, re.IGNORECASE
        ):
            constraints.append(
                Constraint(
                    constraint_id=f"C{c_counter:03d}",
                    category="budget",
                    description=f"Budget limit: {match.group(1)}",
                ),
            )
            c_counter += 1

        # Timeline constraints
        if match := re.search(
            r"(?:duration|timeline|period)[:\s]*(\d+\s*(?:weeks?|months?|years?))",
            constraint_section,
            re.IGNORECASE,
        ):
            constraints.append(
                Constraint(
                    constraint_id=f"C{c_counter:03d}",
                    category="timeline",
                    description=f"Timeline: {match.group(1)}",
                ),
            )
            c_counter += 1

        return constraints

    def _extract_eval_criteria(self, text: str, sections: dict[str, str]) -> list[EvalCriterion]:
        """Extract evaluation criteria."""
        criteria: list[EvalCriterion] = []
        ec_counter = 1

        eval_section = sections.get("evaluation", sections.get("criteria", text))

        # Pattern: weighted criteria
        pattern = r"([A-Za-z\s]+)\s*[:\-\s]+(\d+)%?"
        for match in tqdm(re.finditer(pattern, eval_section), desc="Processing", unit="item"):
            cat = match.group(1).strip()
            weight = float(match.group(2))
            criteria.append(
                EvalCriterion(
                    criterion_id=f"EC{ec_counter:03d}",
                    category=cat.lower(),
                    weight=weight,
                    description=f"{cat} evaluation criterion",
                ),
            )
            ec_counter += 1

        return criteria

    def _classify_requirement(self, text: str) -> str:
        """Classify requirement by category."""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["security", "compliance", "audit", "encryption"]):
            return "security"
        if any(kw in text_lower for kw in ["api", "integration", "database", "cloud", "architecture"]):
            return "technical"
        if any(kw in text_lower for kw in ["user", "interface", "ux", "accessibility"]):
            return "functional"
        return "general"


class MockPDFParser:
    """Mock PDF parser for demonstration (would use PyPDF2 or pdfplumber in production)."""

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"

    def parse(self, file_path: Path) -> ParsedDocument:
        _emit_records_execution_trace("enterprise", "MockPDFParser", "parse_start")

        # In production, use pdfplumber or PyPDF2
        # This is a mock that extracts text heuristics from filename
        _log.warning("[MockPDFParser] Using mock parser - install pdfplumber for real PDF parsing")

        # Simulate extraction
        org_name = file_path.stem.replace("_", " ").title()

        return ParsedDocument(
            source_path=str(file_path),
            file_type="pdf",
            raw_text=f"Mock PDF content for {org_name}",
            title=f"RFP from {org_name}",
            organization=org_name,
            submission_deadline="",
            sections={"mock": "Mock content"},
            requirements=[
                Requirement("R001", "technical", "mandatory", "System must be cloud-deployable"),
                Requirement("R002", "security", "mandatory", "Data must be encrypted at rest"),
            ],
        )


class RfpIngestionEngine:
    """Main engine for ingesting RFP documents."""

    def __init__(self) -> None:
        self.parsers: list[DocumentParser] = [
            PlainTextParser(),
            MockPDFParser(),
        ]

    def ingest(self, file_path: str | Path) -> ParsedDocument:
        """Ingest an RFP document and return parsed structure."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"RFP document not found: {path}")

        # Find appropriate parser
        for parser in self.parsers:
            if parser.can_parse(path):
                _emit_records_execution_trace(
                    "enterprise", "RfpIngestionEngine", f"using_{type(parser).__name__}"
                )
                return parser.parse(path)

        # Fallback to plain text
        _log.warning(f"[RfpIngestionEngine] No specific parser for {path.suffix}, using plain text")
        return PlainTextParser().parse(path)

    def ingest_batch(self, directory: str | Path) -> list[ParsedDocument]:
        """Ingest all RFP documents in a directory."""
        dir_path = Path(directory)
        results: list[ParsedDocument] = []

        for ext in ["*.txt", "*.md", "*.pdf", "*.docx"]:
            for file_path in dir_path.glob(ext):
                try:
                    doc = self.ingest(file_path)
                    results.append(doc)
                except Exception as exc:
                    _log.error(f"[RfpIngestionEngine] Failed to ingest {file_path}: {exc}")

        _emit_stores_embedding("enterprise", "RfpIngestionEngine", f"batch_ingested_{len(results)}")
        return results


def extract_rfp_summary(parsed: ParsedDocument) -> dict[str, Any]:
    """Generate a human-readable summary of parsed RFP."""
    return {
        "title": parsed.title,
        "organization": parsed.organization,
        "deadline": parsed.submission_deadline,
        "sections_found": list(parsed.sections.keys()),
        "requirements_count": len(parsed.requirements),
        "constraints_count": len(parsed.constraints),
        "evaluation_criteria_count": len(parsed.evaluation_criteria),
        "requirement_categories": list(set(r.category for r in parsed.requirements)),
        "mandatory_requirements": len([r for r in parsed.requirements if r.priority == "mandatory"]),
    }
