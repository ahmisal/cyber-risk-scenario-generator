"""Orchestrator for managing the multi-agent workflow - OPTIMIZED VERSION."""

import os
import logging
from dotenv import load_dotenv
from crewai import Crew, Process
from langsmith import traceable
from app.agents.crew_agents import CyberRiskAgents

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LangSmith Observability - Auto-enabled when LANGCHAIN_API_KEY is set
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    logger.info(f"LangSmith tracing ENABLED for project: {os.getenv('LANGCHAIN_PROJECT', 'default')}")
else:
    logger.info("LangSmith tracing disabled (no LANGCHAIN_API_KEY found)")



class AgentOrchestrator:
    """Orchestrates the multi-agent cyber risk analysis workflow."""
    
    def __init__(self):
        """Initialize the orchestrator with agents."""
        logger.info("Initializing AgentOrchestrator")
        self.agents = CyberRiskAgents()
        logger.info("AgentOrchestrator initialized successfully")
    
    @traceable(name="Cyber Risk Analysis Run")
    def analyze_risk(self, asset_name: str, document_text: str) -> str:
        """
        Execute the complete risk analysis workflow.
        
        OPTIMIZED: Reduced iterations, controlled tool usage, concise outputs.
        Expected runtime: 3-5 minutes
        """
        logger.info(f"Starting risk analysis for asset: {asset_name}")
        logger.info(f"Document text length: {len(document_text)} characters")
        
        try:
            # ==================== CREATE 5 AGENTS ====================
            logger.info("Creating agents...")
            context_analyst = self.agents.create_context_analyst()
            threat_specialist = self.agents.create_threat_specialist()
            vuln_researcher = self.agents.create_vuln_researcher()
            risk_architect = self.agents.create_risk_architect()
            ciso = self.agents.create_ciso()
            logger.info("All 5 agents created")
            
            # ==================== CREATE 5 TASKS ====================
            logger.info("Creating tasks...")
            
            context_task = self.agents.create_context_task(
                agent=context_analyst,
                asset_name=asset_name,
                document_text=document_text
            )
            
            threat_task = self.agents.create_threat_task(
                agent=threat_specialist,
                asset_name=asset_name,
                context_task=context_task
            )
            
            vuln_task = self.agents.create_vuln_task(
                agent=vuln_researcher,
                asset_name=asset_name,
                context_task=context_task
            )
            
            scenario_task = self.agents.create_scenario_task(
                agent=risk_architect,
                context_task=context_task,
                threat_task=threat_task,
                vuln_task=vuln_task
            )
            
            review_task = self.agents.create_review_task(
                agent=ciso,
                scenario_task=scenario_task
            )
            
            logger.info("All 5 tasks created")
            
            # ==================== EXECUTE CREW ====================
            logger.info("Creating and executing crew...")
            crew = Crew(
                agents=[context_analyst, threat_specialist, vuln_researcher, risk_architect, ciso],
                tasks=[context_task, threat_task, vuln_task, scenario_task, review_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            logger.info("Crew workflow completed")
            
            # Extract final report
            if hasattr(result, 'raw'):
                final_report = result.raw
            elif isinstance(result, str):
                final_report = result
            else:
                final_report = str(result)
            
            logger.info(f"Final report: {len(final_report)} characters")
            return final_report
        
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            raise Exception(f"Risk analysis failed: {str(e)}")