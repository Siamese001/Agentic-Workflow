"""RAG simulation models."""

from typing import List

from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.simulation_base import SimulationInput, SimulationResult  # INVALID: Cannot import from path with hyphens


class RAGSimRequest(SimulationInput):
    """Input payload for RAG simulation."""

    query: str
    documents: List[str]


class RAGSimMetrics(BaseModel):
    """Metrics produced by the RAG simulation."""

    recall: float
    precision: float
    redundancy: float


class RAGSimResult(SimulationResult):
    """Result model for RAG simulations."""

    pass
