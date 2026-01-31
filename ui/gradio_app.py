"""Gradio frontend for cyber risk analysis."""

import os
import sys

# Critical: Print immediately to verify python execution
print("DEBUG: Script started... Please wait.", flush=True)

import sys
# Add project root to path so we can import app.utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Critical: Disable Gradio Analytics BEFORE import to prevent startup hang
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

# Critical: Move Matplotlib cache to temp to avoid Google Drive file locking
import tempfile
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib_cache")

# Apply SSL Patch to frontend as well so it doesn't fail connecting to backend
try:
    from app.utils.ssl_patch import patch_ssl_requests
    print("DEBUG: Applying SSL patch to frontend...", flush=True)
    patch_ssl_requests()
except ImportError:
    print("DEBUG: Could not import SSL patch, continuing without it.", flush=True)

import requests
print("DEBUG: Importing gradio (this may take 20-30 seconds on Google Drive)...", flush=True)
import gradio as gr
print("DEBUG: Imported gradio successfully.", flush=True)
from typing import Tuple, Optional

print("DEBUG: Starting Gradio App...", flush=True)

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
print(f"DEBUG: Using API URL: {API_URL}", flush=True)


def analyze_cyber_risk(asset_name: str, file) -> Tuple[str, Optional[str]]:
    """
    Submit risk analysis request to backend API.
    
    Args:
        asset_name: Name of the asset
        file: Uploaded file object
    
    Returns:
        Tuple of (report_markdown, error_message)
    """
    if not asset_name or not asset_name.strip():
        return "", "Asset name is required"
    
    if file is None:
        return "", "Please upload a document"
    
    try:
        # Prepare file for upload
        with open(file.name, 'rb') as f:
            files = {'file': (os.path.basename(file.name), f, 'application/octet-stream')}
            data = {'asset_name': asset_name}
            
            # Make API request
            response = requests.post(
                f"{API_URL}/analyze",
                files=files,
                data=data,
                timeout=3000  # 5 minute timeout for agent execution
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return result.get("report", ""), None
            else:
                error = result.get("error", "Unknown error occurred")
                return "", f"Error: {error}"
        else:
            error_msg = response.json().get("detail", "Unknown error occurred")
            return "", f"API Error ({response.status_code}): {error_msg}"
    
    except requests.exceptions.Timeout:
        return "", "Request timed out. The analysis may take several minutes. Please try again."
    except requests.exceptions.ConnectionError:
        return "", f"Could not connect to backend API at {API_URL}. Make sure the FastAPI server is running."
    except Exception as e:
        return "", f"Error: {str(e)}"


def create_interface():
    """Create and launch the Gradio interface."""
    
    with gr.Blocks(title="Cyber Risk Scenario Generator", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🛡️ Cyber Risk Scenario Generator
            
            Upload a document describing your IT environment and get a comprehensive cyber risk analysis report.
            
            **How it works:**
            1. Enter an Asset Name
            2. Upload a document (TXT, DOCX, or PDF) describing your IT environment
            3. Click "Analyze Risk" to generate the report
            4. Review the prioritized cyber risk scenarios and recommendations
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                asset_input = gr.Textbox(
                    label="Asset Name",
                    placeholder="e.g., Production Web Server, Corporate Network, etc."
                )
                
                file_input = gr.File(
                    label="IT Environment Document (TXT, DOCX, or PDF)",
                    file_types=[".txt", ".docx", ".pdf"]
                )
                
                analyze_btn = gr.Button("Analyze Risk", variant="primary", size="lg")
            
            with gr.Column(scale=2):
                output = gr.Markdown(
                    label="Cyber Risk Report",
                    value="## Report will appear here after analysis\n\nUpload a document and click 'Analyze Risk' to begin."
                )
                
                error_output = gr.Textbox(
                    label="Status",
                    visible=False,
                    interactive=False
                )
        
        # Event handlers
        analyze_btn.click(
            fn=analyze_cyber_risk,
            inputs=[asset_input, file_input],
            outputs=[output, error_output],
            show_progress=True
        ).then(
            fn=lambda error: gr.update(visible=error is not None, value=error if error else ""),
            inputs=[error_output],
            outputs=[error_output]
        )
        
        gr.Markdown(
            """
            ---
            **Note:** Analysis may take 2-5 minutes depending on document complexity. 
            The system uses multiple AI agents to analyze your environment, research threats, 
            and generate comprehensive risk scenarios.
            """
        )
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
