"""
Document Package Types - Domain contracts for document references.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class DocumentRef(BaseModel):
    """Reference to a document with metadata."""

    doc_id: str = Field(..., description="Unique document ID")
    doc_type: str = Field(..., description="Document type")
    source_uri: str = Field(..., description="Document location/URI")
    hash: str = Field(..., description="Content hash for integrity")
    extracted_text_available: bool = Field(False, description="Whether text extraction completed")
    parsed_structured_fields: Dict[str, Any] = Field(default_factory=dict, description="Extracted fields")
    document_flags: List[str] = Field(default_factory=list, description="Document quality flags")


class DocumentPackage(BaseModel):
    """
    Complete document package for underwriting.
    """

    financial_statements: List[DocumentRef] = Field(default_factory=list)
    tax_returns: List[DocumentRef] = Field(default_factory=list)
    bank_statements: List[DocumentRef] = Field(default_factory=list)
    ar_aging: List[DocumentRef] = Field(default_factory=list)
    ap_aging: List[DocumentRef] = Field(default_factory=list)
    debt_schedule: List[DocumentRef] = Field(default_factory=list)
    entity_docs: List[DocumentRef] = Field(default_factory=list)
    insurance_certificates: List[DocumentRef] = Field(default_factory=list)
    appraisals: List[DocumentRef] = Field(default_factory=list)
    management_comments: List[DocumentRef] = Field(default_factory=list)

    @property
    def total_doc_count(self) -> int:
        """Total number of documents in package."""
        return (
            len(self.financial_statements)
            + len(self.tax_returns)
            + len(self.bank_statements)
            + len(self.ar_aging)
            + len(self.ap_aging)
            + len(self.debt_schedule)
            + len(self.entity_docs)
            + len(self.insurance_certificates)
            + len(self.appraisals)
            + len(self.management_comments)
        )

    @property
    def doc_types_present(self) -> List[str]:
        """List of document types present in package."""
        types_present = []
        if self.financial_statements:
            types_present.append("financial_statements")
        if self.tax_returns:
            types_present.append("tax_returns")
        if self.bank_statements:
            types_present.append("bank_statements")
        if self.ar_aging:
            types_present.append("ar_aging")
        if self.ap_aging:
            types_present.append("ap_aging")
        if self.debt_schedule:
            types_present.append("debt_schedule")
        if self.entity_docs:
            types_present.append("entity_docs")
        if self.insurance_certificates:
            types_present.append("insurance_certificates")
        if self.appraisals:
            types_present.append("appraisals")
        if self.management_comments:
            types_present.append("management_comments")
        return types_present

    class Config:
        json_schema_extra = {
            "example": {
                "financial_statements": [
                    {
                        "doc_id": "DOC-001",
                        "doc_type": "financial_statement",
                        "source_uri": "s3://docs/acme/fs_2023.pdf",
                        "hash": "abc123",
                        "extracted_text_available": True,
                        "parsed_structured_fields": {},
                        "document_flags": [],
                    },
                ],
            },
        }
