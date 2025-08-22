"""
Template Parser Agent for Resume Builder
Analyzes LaTeX template files to extract structure, patterns, and reusable components.
Creates template schemas that can be used by the content generation agent.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Dict, Any, Optional, Union
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import json
import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(base_url=os.environ.get('BASE_URL')))

class ModifiedContent(BaseModel):
    content: str

system_prompt = r"""
You are a LaTeX template standardizer. Convert the given template into a standardized format:

**CRITICAL RULES:**
1. PRESERVE all document setup: \\documentclass, \\usepackage (ensure \\usepackage{url}), \\newcommand, geometry, fonts
2. KEEP the header structure intact: name formatting, contact layout, profile picture setup
3. KEEP the section structure intact: \\section, \\subsection, \\subsubsection, \\paragraph,
only replace the NAME with the following names in original formatting: DO NOT CHANGE THE FORMAT, only change the name:
   - Education
   - Experience  
   - Skills
   - Projects
   - Custom Section
4. REPLACE all custom content with placeholders such as "Placeholder for experience name 1", "Placeholder for experience description 1", etc.
5. MAINTAIN original spacing, formatting, and layout structure

**OUTPUT FORMAT:**
Return JSON: {"content": <>modified LaTeX template>}
"""

template_parser_agent = Agent(
    model=model,
    output_type=ModifiedContent,
    system_prompt=system_prompt
)

    
async def analyze_template_file(file_path: str):
    """
    Analyze a LaTeX template from a file path.
    
    Args:
        file_path: Path to the .tex template file
        
    Returns:
        TemplateAnalysisResult with extracted template schema
    """
    try:
        logger.info(f"Reading template file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            latex_content = file.read()
        
        logger.info(f"Template file read successfully, length: {len(latex_content)} characters")
        result = await template_parser_agent.run(latex_content)
        print(result)
        logger.info("Template parsing completed successfully")
        return result.output.content
        
    except FileNotFoundError:
        logger.error(f"Template file not found: {file_path}")
        return f"Template file not found: {file_path}"
    except Exception as e:
        logger.error(f"Failed to read template file: {str(e)}", exc_info=True)
        return f"Failed to read template file: {str(e)}"


# Sample usage and testing
sample_latex = r"""
\\documentclass[11pt,a4paper]{article}
\\usepackage[left=0.75in,top=0.6in,right=0.75in,bottom=0.6in]{geometry}
\\usepackage{hyperref}
\\usepackage{titlesec}
\\begin{document}
\\section{Education}
\\textbf{Degree} | Institution \\hfill Date
\\end{document}
"""

async def test_parser():
    logger.info("Starting template parser test")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, "..", "templates", "default_resume.tex")
    
    logger.info(f"Looking for template at: {template_path}")
    result = await analyze_template_file(template_path)
    
    parsed_template_path = os.path.join(current_dir, "..", "templates", "parsed_template.tex")
    logger.info(f"Saving parsed template to: {parsed_template_path}")
    
    with open(parsed_template_path, "w") as f:
        f.write(result)
    
    logger.info("Parsed template saved successfully")
    
    logger.info("Test completed")

if __name__ == "__main__":
    import asyncio
    logger.info("Script started")
    asyncio.run(test_parser())
    logger.info("Script finished")