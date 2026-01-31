"""
HuggingFace Spaces Entry Point
Combines backend and frontend for unified deployment.
"""

import os
import sys
import io
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable analytics and telemetry
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import gradio as gr
from PyPDF2 import PdfReader
from docx import Document

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.orchestrator import AgentOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global orchestrator (lazy loaded)
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        logger.info("Initializing AgentOrchestrator...")
        _orchestrator = AgentOrchestrator()
    return _orchestrator


def extract_text(file_content: bytes, filename: str) -> str:
    """Extract text from uploaded file."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.pdf':
        reader = PdfReader(io.BytesIO(file_content))
        return "\n".join([p.extract_text() or "" for p in reader.pages])
    elif ext == '.docx':
        doc = Document(io.BytesIO(file_content))
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    elif ext == '.txt':
        return file_content.decode('utf-8')
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def analyze_risk(asset_name: str, file):
    """Main analysis function for Gradio interface."""
    if not asset_name or not asset_name.strip():
        return "❌ Error: Asset name is required"
    
    if file is None:
        return "❌ Error: Please upload a document"
    
    try:
        # Read and extract text
        with open(file.name, 'rb') as f:
            content = f.read()
        
        document_text = extract_text(content, file.name)
        
        if not document_text.strip():
            return "❌ Error: Could not extract text from document"
        
        # Run analysis
        orch = get_orchestrator()
        report = orch.analyze_risk(asset_name=asset_name, document_text=document_text)
        
        return report
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


# Build Gradio Interface
with gr.Blocks(title="Cyber Risk Scenario Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🛡️ Cyber Risk Scenario Generator
    
    Upload a document describing your IT environment and get a comprehensive cyber risk analysis report.
    
    **How it works:**
    1. Enter an Asset Name (e.g., "Production Web Server")
    2. Upload a document (TXT, DOCX, or PDF) describing your IT environment
    3. Click "Analyze Risk" to generate the report
    4. Review the prioritized cyber risk scenarios
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            asset_input = gr.Textbox(
                label="Asset Name",
                placeholder="e.g., Production Web Server, Corporate Network"
            )
            file_input = gr.File(
                label="IT Environment Document",
                file_types=[".txt", ".docx", ".pdf"]
            )
            analyze_btn = gr.Button("🔍 Analyze Risk", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            output = gr.Markdown(
                label="Cyber Risk Report",
                value="## Report will appear here\n\nUpload a document and click 'Analyze Risk' to begin."
            )
    
    analyze_btn.click(
        fn=analyze_risk,
        inputs=[asset_input, file_input],
        outputs=[output],
        show_progress=True
    )
    
    gr.Markdown("""
    ---
    **Note:** Analysis takes 2-5 minutes. The system uses 5 AI agents to analyze threats and vulnerabilities.
    """)

if __name__ == "__main__":
    demo.launch()
