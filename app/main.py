"""FastAPI application entry point - STABLE 2026 VERSION."""

import os
import ssl
from app.utils.ssl_patch import patch_ssl_requests

# APPLY SSL PATCH IMMEDIATELY
patch_ssl_requests()

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.observability.logging_conf import setup_logging

# 1. SSL FIX: Must be at the very top for local environments
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

# 2. LOAD ENVIRONMENT
load_dotenv()

# 3. LOGGING SETUP
logger = setup_logging()

# 4. APP INITIALIZATION
# Initialize cleanly without passing middleware in the constructor
app = FastAPI(
    title="Cyber Risk Scenario Generator",
    description="Multi-agent AI system for generating cyber risk reports",
    version="1.0.0"
)

# 5. CORS MIDDLEWARE
# Adding this via add_middleware avoids the "too many values to unpack" error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. ROUTER INCLUSION
# Prefix is kept, but tags are removed here to avoid metadata conflicts
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Cyber Risk Scenario Generator API",
        "status": "online",
        "version": "1.0.0"
    }
