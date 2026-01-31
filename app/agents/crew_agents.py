"""CrewAI agent definitions - CAPSTONE FINAL STABLE VERSION 2026."""

import os
import requests
import time
import ssl
import urllib3
import warnings
import logging
from app.utils.ssl_patch import patch_ssl_requests

# APPLY SSL PATCH IMMEDIATELY
patch_ssl_requests()

# DISABLE CHROMA TELEMETRY (Fixes Google Drive Hang)
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_DB_IMPL"] = "duckdb+parquet"


# 1. CORE IMPORTS
from crewai import Agent, Task, LLM
from crewai.tools import tool 
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# ==================== GLOBAL CONFIGURATION ====================
logger = logging.getLogger(__name__)

# SSL/NETWORK FIXES (Critical for Windows 'Unexpected EOF' errors)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Suppress messy console warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

# ==================== CUSTOM NVD TOOL ====================

@tool("Search NVD for CVEs")
def nvd_cve_search(keyword: str) -> str:
    """Search NVD database for CVEs. Use this tool FIRST."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    api_key = os.getenv("NVD_API_KEY")
    if api_key:
        headers["apiKey"] = api_key

    try:
        url = "https://services.nvd.nist.gov"
        params = {"keywordSearch": keyword, "resultsPerPage": 3}
        # verify=False is used to bypass local SSL handshake failures
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if not data.get("vulnerabilities"):
                return f"No results for '{keyword}'. Switching to internet search."
            
            results = []
            for item in data["vulnerabilities"]:
                cve = item.get("cve", {})
                cve_id = cve.get("id", "Unknown")
                metrics = cve.get("metrics", {})
                cvss = "N/A"
                for v in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                    if metrics.get(v):
                        cvss = metrics[v][0]["cvssData"]["baseScore"]
                        break
                results.append(f"**{cve_id}** (CVSS: {cvss})")
            return "\n".join(results)
    except:
        pass
    
    return "NVD API is currently busy. Use Internet Search fallback."

# ==================== AGENT FACTORY ====================

class CyberRiskAgents:
    def __init__(self):
        print("DEBUG: CyberRiskAgents: Initializing...", flush=True)
        
        # Modern LLM setup (v1.8.0+)
        print("DEBUG: CyberRiskAgents: Setting up LLM...", flush=True)
        try:
            self.llm = LLM(
                model="gpt-4o-mini",
                temperature=0.2,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            print("DEBUG: CyberRiskAgents: LLM setup complete.", flush=True)
        except Exception as e:
            print(f"DEBUG: CyberRiskAgents: LLM setup failed: {e}", flush=True)
            raise

        # Tools
        print("DEBUG: CyberRiskAgents: Setting up NVD Tool...", flush=True)
        self.nvd_tool = nvd_cve_search
        
        print("DEBUG: CyberRiskAgents: Setting up SerperDevTool...", flush=True)
        try:
            self.search_tool = SerperDevTool()
            print("DEBUG: CyberRiskAgents: SerperDevTool setup complete.", flush=True)
        except Exception as e:
             print(f"DEBUG: CyberRiskAgents: SerperDevTool setup failed: {e}", flush=True)

        print("DEBUG: CyberRiskAgents: Setting up ScrapeWebsiteTool...", flush=True)
        try:
            self.scrape_tool = ScrapeWebsiteTool()
            print("DEBUG: CyberRiskAgents: ScrapeWebsiteTool setup complete.", flush=True)
        except Exception as e:
             print(f"DEBUG: CyberRiskAgents: ScrapeWebsiteTool setup failed: {e}", flush=True)
            
        print("DEBUG: CyberRiskAgents: Initialization Done.", flush=True)

    def create_context_analyst(self) -> Agent:
        return Agent(
            role="Operational Context Analyst",
            goal="Extract tech stack and business criticality.",
            backstory="Expert auditor. You extract facts once and move on.",
            llm=self.llm,
            max_iter=2,
            verbose=True
        )

    def create_threat_specialist(self) -> Agent:
        return Agent(
            role="Threat Intelligence Specialist",
            goal="Identify the top threat for the technology stack.",
            backstory=(
                "You are an expert. You scrape CISA.gov EXACTLY ONCE. "
                "If it works, use that. If it fails, use your internal knowledge. "
                "Do not try multiple websites."
            ),
            tools=[self.scrape_tool],
            llm=self.llm,
            max_iter=2, # Hard stop to prevent scraping loops
            verbose=True
        )

    def create_vuln_researcher(self) -> Agent:
        return Agent(
            role="Vulnerability Researcher",
            goal="Find one critical CVE (2024-2026) for the stack.",
            backstory=(
                "Vulnerability expert. 1. Try NVD once. 2. If it fails/busy, "
                "try Serper once. 3. If both fail, use your own knowledge of 2025 CVEs. "
                "Stop after two tool attempts maximum."
            ),
            tools=[self.nvd_tool, self.search_tool],
            llm=self.llm,
            max_iter=2, # Hard stop to prevent NVD/Serper loops
            verbose=True
        )

    def create_risk_architect(self) -> Agent:
        return Agent(
            role="Cyber Risk Architect",
            goal="Create 3 attack scenarios.",
            backstory="Risk expert. You synthesize previous findings.",
            llm=self.llm,
            max_iter=2,
            verbose=True
        )

    def create_ciso(self) -> Agent:
        return Agent(
            role="CISO",
            goal="Deliver an executive summary report.",
            backstory="Executive leader. No tools needed.",
            llm=self.llm,
            max_iter=2,
            verbose=True
        )

    # ==================== TASKS ====================

    def create_context_task(self, agent, asset_name, document_text):
        return Task(
            description=f"Analyze documentation for '{asset_name}':\n{document_text[:4000]}", 
            expected_output="Tech stack and criticality summary.", 
            agent=agent
        )

    def create_threat_task(self, agent, asset_name, context_task):
        return Task(
            description=(
                f"Find the top threat for '{asset_name}'.\n"
                "SCRAPE THIS SITE ONCE: https://www.cisa.gov\n"
                "If blocked, use your knowledge. Do not loop."
            ), 
            expected_output="Top threat summary.", 
            agent=agent, 
            context=[context_task]
        )

    def create_vuln_task(self, agent, asset_name, context_task):
        return Task(
            description=(
                f"Find vulnerabilities for '{asset_name}'.\n"
                "1. Search NVD for '{asset_name}' ONCE.\n"
                "2. If busy, Search Internet (Serper) for 'critical {asset_name} CVE 2025' ONCE.\n"
                "3. Stop after that."
            ),
            expected_output="One CVE ID and CVSS score.",
            agent=agent,
            context=[context_task]
        )

    def create_scenario_task(self, agent, context_task, threat_task, vuln_task):
        return Task(
            description="Create 3 scenarios based on the gathered threats and vulnerabilities.", 
            expected_output="3 scenarios.", 
            agent=agent, 
            context=[context_task, threat_task, vuln_task]
        )

    def create_review_task(self, agent, scenario_task):
        return Task(
            description="Produce the final CISO executive report.", 
            expected_output="Executive report.", 
            agent=agent, 
            context=[scenario_task]
        )
