"""
Main FastAPI application for the Resume Builder Backend

This file contains:
1. FastAPI app initialization
2. CORS middleware setup
3. API route definitions
4. Main application entry point

Key endpoints implemented:
- POST /api/generate-pdf - Main endpoint for PDF generation
- POST /api/polish-content - Endpoint for AI content improvement
- GET /api/health - Health check endpoint
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import tempfile
import shutil
from pathlib import Path
from fastapi.encoders import jsonable_encoder

# Import our custom modules
from models.resume_models import ResumeData, UpdateMessage, PolishRequest
from agents.improvement_agent import improve_update
from agents.latex_agent import LaTeXAgent
from services.pdf_service import PDFService

# Initialize FastAPI app
app = FastAPI(
    title="Resume Builder API",
    description="Backend API for the Resume Builder application",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
latex_agent = LaTeXAgent()
pdf_service = PDFService()

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Resume Builder API is running",
        "version": "1.0.0"
    }

# Content improvement endpoint
@app.post("/api/polish-content")
async def polish_content(request: PolishRequest):
    try:
        update_message = {
            "section": request.section,
            "entryId": request.entryId,
            "changeType": "update",  # Assume update for polishing
            "content": request.content
        }
        print(update_message)
        
        # Get improved content
        improved_update = await improve_update(update_message)

        # Normalize to plain dict
        if isinstance(improved_update, BaseModel):
            improved_update = improved_update.model_dump()

        # Extract the content payload for frontend
        improved_content = improved_update.get("content", improved_update)

        payload = {
            "success": True,
            "improvedContent": improved_content,
            "message": "Content improved successfully"
        }

        print(payload)
        return JSONResponse(content=jsonable_encoder(payload))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error improving content: {str(e)}")

# PDF generation endpoint
@app.post("/api/generate-pdf")
async def generate_pdf(resume_data: ResumeData):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            latex_source = latex_agent.generate_latex(resume_data.model_dump())
            pdf_path = pdf_service.compile_latex_to_pdf(latex_source, str(temp_path))
            if not pdf_service.validate_pdf_output(pdf_path):
                raise HTTPException(status_code=500, detail="PDF generation failed - invalid output")
            return FileResponse(path=pdf_path, media_type="application/pdf", filename="resume.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# Batch content improvement endpoint
@app.post("/api/polish-batch")
async def polish_batch(updates: List[UpdateMessage]):
    try:
        improved_updates: List[Dict[str, Any]] = []
        for update in updates:
            improved = await improve_update(update.model_dump())
            if isinstance(improved, BaseModel):
                improved = improved.model_dump()
            improved_updates.append(improved)
        return JSONResponse(content=jsonable_encoder({
            "success": True,
            "improvedUpdates": improved_updates,
            "message": f"Improved {len(improved_updates)} content items"
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error improving batch content: {str(e)}")

# Get available templates endpoint
@app.get("/api/templates")
async def get_templates():
    try:
        templates = latex_agent.get_available_templates()
        return {"success": True, "templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

# Preview LaTeX endpoint (for debugging)
@app.post("/api/preview-latex")
async def preview_latex(resume_data: ResumeData):
    try:
        latex_source = latex_agent.generate_latex(resume_data.model_dump())
        return {"success": True, "latexSource": latex_source}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating LaTeX: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
