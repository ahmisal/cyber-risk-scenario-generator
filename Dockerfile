FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY ui/ ./ui/

# Expose ports
# 8000 for FastAPI, 7860 for Gradio
EXPOSE 8000 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV API_URL=http://localhost:8000/api/v1

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
