"""API routes for the cyber risk analysis application - STABLE 2026 VERSION."""

import os
import logging
import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PyPDF2 import PdfReader
from docx import Document
# Removed top-level import to prevent startup hang
# from app.agents.orchestrator import AgentOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router simply without any arguments
router = APIRouter()


# Initialize global variable
orchestrator = None

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        from app.agents.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
    return orchestrator

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text content from uploaded file."""
    file_ext = os.path.splitext(filename)[1].lower()
    
    try:
        if file_ext == '.pdf':
            pdf_reader = PdfReader(io.BytesIO(file_content))
            text_parts = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts)
        
        elif file_ext == '.docx':
            doc = Document(io.BytesIO(file_content))
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            return "\n".join(text_parts)
        
        elif file_ext == '.txt':
            return file_content.decode('utf-8')
        
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {str(e)}")
        raise

@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    asset_name: str = Form(...)
):
    """Analyze uploaded company profile document for cyber risks."""
    logger.info(f"Received file: {file.filename}, Asset: {asset_name}")
    
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type.")
    
    try:
        file_content = await file.read()
        document_text = extract_text_from_file(file_content, file.filename)
        
        if not document_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from document.")
        
        # Lazy load orchestrator here to prevent startup hangs
        orch = get_orchestrator()
        result = orch.analyze_risk(
            asset_name=asset_name,
            document_text=document_text
        )
        
        return {
            "status": "success",
            "asset_name": asset_name,
            "report": result
        }
    
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
