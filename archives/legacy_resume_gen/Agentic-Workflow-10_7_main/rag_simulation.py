"""RAG simulation models."""

from typing import List

from pydantic import BaseModel

from .simulation_base import SimulationInput, SimulationResult


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
