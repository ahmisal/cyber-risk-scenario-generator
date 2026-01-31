"""Pydantic schemas for request/response models."""

from pydantic import BaseModel
from typing import Optional


class RiskAnalysisRequest(BaseModel):
    """Request model for risk analysis."""
    asset_name: str
    document_text: str


class RiskAnalysisResponse(BaseModel):
    """Response model for risk analysis."""
    report: str
    status: str = "success"
    error: Optional[str] = None
