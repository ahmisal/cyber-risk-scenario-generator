"""Pytest tests for agent orchestration."""

import pytest
import os
from app.agents.orchestrator import AgentOrchestrator


@pytest.fixture
def sample_document():
    """Sample IT environment document for testing."""
    return """
    IT Environment Overview:
    
    Infrastructure:
    - Web servers running Apache 2.4.41 on Ubuntu 20.04
    - Database: PostgreSQL 12.5
    - Load balancer: Nginx 1.18
    - Cloud provider: AWS
    
    Applications:
    - Customer portal (React frontend)
    - Payment processing API (Python Flask)
    - Admin dashboard (Django)
    
    Security:
    - SSL/TLS certificates
    - Firewall rules configured
    - Regular backups
    """


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
def test_orchestrator_initialization():
    """Test that orchestrator can be initialized."""
    orchestrator = AgentOrchestrator()
    assert orchestrator is not None
    assert orchestrator.llm is not None


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
def test_agent_orchestration_returns_output(sample_document):
    """Test that agent orchestration returns a report."""
    orchestrator = AgentOrchestrator()
    report = orchestrator.analyze_risk(
        asset_name="Test Web Server",
        document_text=sample_document
    )
    
    assert report is not None
    assert isinstance(report, str)
    assert len(report) > 0
