"""
PDF Generation Service

This file contains:
1. LaTeX compilation logic
2. PDF file management
3. Temporary file handling
4. Error handling for compilation failures

Key functions implemented:
- compile_latex_to_pdf(latex_source: str, output_dir: str) -> str
- cleanup_temp_files(file_paths: List[str]) -> None
- validate_pdf_output(pdf_path: str) -> bool
- get_pdf_metadata(pdf_path: str) -> dict
- compress_pdf(pdf_path: str) -> str

Compilation process:
1. Write LaTeX source to temporary .tex file
2. Run pdflatex command via subprocess
3. Handle compilation errors and warnings
4. Return path to generated PDF file
5. Clean up temporary files

Dependencies:
- subprocess (for running pdflatex)
- tempfile (for temporary file management)
- pathlib (for file operations)
- PyPDF2 (for PDF validation)

System requirements:
- LaTeX distribution installed (TeX Live, MiKTeX, etc.)
- pdflatex command available in PATH
- Sufficient disk space for temporary files

Error handling for:
- LaTeX compilation failures
- Missing LaTeX installation
- Insufficient disk space
- Permission issues
- Malformed LaTeX input
"""

import subprocess
import tempfile
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import PyPDF2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFService:
    """
    Service for generating PDFs from LaTeX source
    """
    
    def __init__(self):
        self.latex_command = "pdflatex"
        self.max_compilation_attempts = 2
        
    def compile_latex_to_pdf(self, latex_source: str, output_dir: str) -> str:
        """
        Compile LaTeX source to PDF
        
        Args:
            latex_source: Complete LaTeX source code
            output_dir: Directory to store output files
            
        Returns:
            Path to generated PDF file
            
        Raises:
            RuntimeError: If compilation fails
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create temporary .tex file
        tex_file = output_path / "resume.tex"
        pdf_file = output_path / "resume.pdf"
        
        try:
            # Write LaTeX source to file
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_source)
            
            # Compile LaTeX to PDF
            self._run_pdflatex(output_path, tex_file.name)
            
            # Validate PDF was created
            if not pdf_file.exists():
                raise RuntimeError("PDF file was not created during compilation")
            
            # Validate PDF content
            if not self.validate_pdf_output(str(pdf_file)):
                raise RuntimeError("Generated PDF is invalid or corrupted")
            
            return str(pdf_file)
            
        except Exception as e:
            logger.error(f"LaTeX compilation failed: {e}")
            raise RuntimeError(f"PDF generation failed: {str(e)}")
        
        finally:
            # Clean up temporary files
            self._cleanup_temp_files(output_path)
    
    def _run_pdflatex(self, output_dir: Path, tex_filename: str) -> None:
        """
        Run pdflatex command to compile LaTeX
        
        Args:
            output_dir: Directory containing the .tex file
            tex_filename: Name of the .tex file
            
        Raises:
            RuntimeError: If compilation fails
        """
        # Check if pdflatex is available
        if not self._check_pdflatex_available():
            raise RuntimeError("pdflatex command not found. Please install a LaTeX distribution.")
        
        # pdflatex command arguments
        cmd = [
            self.latex_command,
            "-interaction=nonstopmode",  # Non-interactive mode
            "-output-directory=" + str(output_dir),
            tex_filename
        ]
        
        # Run compilation with multiple attempts
        for attempt in range(self.max_compilation_attempts):
            try:
                logger.info(f"Running pdflatex (attempt {attempt + 1})")
                
                result = subprocess.run(
                    cmd,
                    cwd=output_dir,
                    capture_output=True,
                    text=True,
                    timeout=60  # 60 second timeout
                )
                
                # Check if compilation was successful
                if result.returncode == 0:
                    logger.info("LaTeX compilation successful")
                    return
                else:
                    logger.warning(f"pdflatex returned code {result.returncode}")
                    logger.warning(f"stderr: {result.stderr}")
                    
                    # If this is the last attempt, raise error
                    if attempt == self.max_compilation_attempts - 1:
                        raise RuntimeError(f"LaTeX compilation failed after {self.max_compilation_attempts} attempts")
                    
            except subprocess.TimeoutExpired:
                logger.error("LaTeX compilation timed out")
                raise RuntimeError("LaTeX compilation timed out")
            
            except Exception as e:
                logger.error(f"Unexpected error during LaTeX compilation: {e}")
                raise RuntimeError(f"LaTeX compilation error: {str(e)}")
    
    def _check_pdflatex_available(self) -> bool:
        """
        Check if pdflatex command is available
        
        Returns:
            True if pdflatex is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.latex_command, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def validate_pdf_output(self, pdf_path: str) -> bool:
        """
        Validate that PDF file is valid and readable
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF is valid, False otherwise
        """
        try:
            if not os.path.exists(pdf_path):
                return False
            
            # Check file size
            file_size = os.path.getsize(pdf_path)
            if file_size == 0:
                return False
            
            # Try to open and read PDF
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                # Check if PDF has at least one page
                if len(pdf_reader.pages) == 0:
                    return False
                
                # Try to extract text from first page
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
                
                # Basic validation - PDF should contain some text
                if not text or len(text.strip()) < 10:
                    return False
                
            return True
            
        except Exception as e:
            logger.error(f"PDF validation failed: {e}")
            return False
    
    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'file_size': os.path.getsize(pdf_path),
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                    'modification_date': pdf_reader.metadata.get('/ModDate', '')
                }
                
                return metadata
                
        except Exception as e:
            logger.error(f"Failed to extract PDF metadata: {e}")
            return {}
    
    def compress_pdf(self, pdf_path: str) -> str:
        """
        Compress PDF file to reduce size
        
        Args:
            pdf_path: Path to original PDF file
            
        Returns:
            Path to compressed PDF file
        """
        try:
            # For now, return the original file
            # In a production environment, you might want to implement actual compression
            # using tools like ghostscript or other PDF compression libraries
            logger.info("PDF compression not implemented, returning original file")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF compression failed: {e}")
            return pdf_path
    
    def _cleanup_temp_files(self, output_dir: Path) -> None:
        """
        Clean up temporary files created during compilation
        
        Args:
            output_dir: Directory containing temporary files
        """
        try:
            # Files to remove
            temp_extensions = ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk']
            
            for ext in temp_extensions:
                temp_file = output_dir / f"resume{ext}"
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Removed temporary file: {temp_file}")
                    
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary files: {e}")
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        Clean up specific temporary files
        
        Args:
            file_paths: List of file paths to remove
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {e}")
