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
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import tempfile
import shutil
from pathlib import Path
from fastapi.encoders import jsonable_encoder
import subprocess
from pathlib import Path
import asyncio

# Import our custom modules
from models.resume_models import ResumeData, UpdateMessage, PolishRequest
from agents.improvement_agent import improve_update
from agents.latex_agent import generate_latex
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
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
"""
FastAPI routes for LaTeX generation and PDF compilation
"""

@app.post("/api/generate-latex")
async def generate_latex_endpoint(request: dict):
    """
    Generate LaTeX code (full or incremental)
    
    request_data: Dictionary with format:
        {
           "type": "full" | "incremental",
            "data": ResumeData,
            "update": UpdateRequest (for incremental),
            "currentLatex": str (for incremental),
            "template_path": str (required)
        }
    """
    try:
        result = await generate_latex(request)
        print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LaTeX generation failed: {str(e)}")

from pydantic import BaseModel

class LatexRequest(BaseModel):
    latexCode: str

# Support both with and without trailing slash for frontend compatibility
@app.post("/api/compile-latex/")
async def compile_latex_endpoint(request: LatexRequest):
    latex_code = request.latexCode
    if not latex_code:
        raise HTTPException(status_code=400, detail="LaTeX code is required")

    try:
        #print(latex_code)
        pdf_bytes = await compile_latex_to_pdf(latex_code)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=resume.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF compilation failed: {str(e)}")
@app.post("/api/generate-final-pdf")
async def generate_final_pdf_endpoint(resume_data: dict):
    """
    Generate final high-quality PDF directly from resume data
    """
    try:
        # Generate LaTeX
        latex_request = {
            "type": "full",
            "data": resume_data
        }
        
        latex_result = await generate_latex(latex_request)
        
        if not latex_result.get("success"):
            raise HTTPException(status_code=500, detail="LaTeX generation failed")
        
        # Compile to PDF
        pdf_bytes = await compile_latex_to_pdf(latex_result["latexCode"])
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=resume.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Final PDF generation failed: {str(e)}")

async def compile_latex_to_pdf(latex_code: str) -> bytes:
    """
    Compile LaTeX code to PDF using pdflatex available on PATH.
    Tries common macOS TeX Live locations as fallbacks.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tex_file = temp_path / "resume.tex"
        
        # Write LaTeX to file
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        
        pdflatex_path = "/usr/local/texlive/2023/bin/universal-darwin/pdflatex"

        # Run pdflatex twice (for references/TOC)
        for run in [1, 2]:
            process = await asyncio.create_subprocess_exec(
                pdflatex_path,
                '-interaction=nonstopmode',
                '-halt-on-error',  # Truly stop on critical errors
                '-output-directory', str(temp_path),
                str(tex_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_path
            )
            
            stdout, stderr = await process.communicate()
            
            # Only fail on actual errors, not warnings
            if process.returncode != 0 and b'Output written' not in stdout:
                error_msg = stderr.decode() if stderr else stdout.decode()
                raise Exception(f"pdflatex compilation failed: {error_msg}")
        
        # Verify PDF exists
        pdf_file = temp_path / "resume.pdf"
        if not pdf_file.exists():
            raise Exception("PDF file was not generated")
        
        return pdf_file.read_bytes()
# Alternative compilation using latexmk for better reliability
async def compile_latex_to_pdf_latexmk(latex_code: str) -> bytes:
    """
    Alternative compilation using latexmk (more reliable)
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tex_file = temp_path / "resume.tex"
        
        # Write LaTeX to file
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        
        # Compile with latexmk
        process = await asyncio.create_subprocess_exec(
            'latexmk',
            '-pdf',
            '-interaction=nonstopmode',
            '-output-directory=' + str(temp_path),
            str(tex_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=temp_path
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else stdout.decode()
            raise Exception(f"latexmk compilation failed: {error_msg}")
        
        # Read the generated PDF
        pdf_file = temp_path / "resume.pdf"
        if not pdf_file.exists():
            raise Exception("PDF file was not generated")
        
        with open(pdf_file, 'rb') as f:
            return f.read()

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Check if LaTeX compilation tools are available"""
    try:
        # Check for pdflatex
        process = await asyncio.create_subprocess_exec(
            'pdflatex', '--version',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        pdflatex_available = process.returncode == 0
        
        # Check for latexmk
        process = await asyncio.create_subprocess_exec(
            'latexmk', '--version',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        latexmk_available = process.returncode == 0
        
        return {
            "status": "healthy",
            "latex_tools": {
                "pdflatex": pdflatex_available,
                "latexmk": latexmk_available
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "latex_tools": {
                "pdflatex": False,
                "latexmk": False
            }
        }


# async def test_compile_latex_to_pdf():
#     minimal_latex = r"""
#     \documentclass{article}
#     \begin{document}
#     Hello, World!
#     \end{document}
#     """
#     try:
#         pdf_bytes = await compile_latex_to_pdf(minimal_latex)
#         assert isinstance(pdf_bytes, bytes), "Output is not bytes"
#         assert len(pdf_bytes) > 0, "PDF output is empty"

#         # Save PDF to disk
#         output_path = "output_test.pdf"
#         with open(output_path, "wb") as f:
#             f.write(pdf_bytes)
#         print(f"Test passed: PDF generated and saved to {output_path}")
#     except Exception as e:
#         print(f"Test failed: {e}")


# if __name__ == "__main__":
#     asyncio.run(test_compile_latex_to_pdf())

if __name__ == "__main__":
    #await compile_latex_to_pdf("\\documentclass[a4paper,10pt]{article}\n\\usepackage[margin=1in]{geometry}\n\\usepackage{enumitem}\n\\usepackage{hyperref}\n\\usepackage{titlesec}\n\\usepackage{parskip}\n\\titleformat{\\section}{\\Large\\bfseries}{}{0em}{} \\titlespacing{\\section}{0em}{1em}{0.5em}\n\\titleformat{\\subsection}[runin]{\\bfseries}{}{0em}{} \\titlespacing{\\subsection}{0em}{0em}{0.5em}\n\\begin{document}\n\n\\begin{center}\n\\textbf{\\LARGE [INSERT NAME HERE]} \\\\\n\\textit{Professional Title / Role} \\\\\n\\end{center}\n\n\\section*{About Me}\n\\textit{I am Amy, a dedicated professional with a passion for excellence and a commitment to enhancing the customer experience.}\n\n\\end{document}")
    
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
