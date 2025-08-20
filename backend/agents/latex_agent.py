"""
LaTeX Generator Agent for Resume Builder
Uses Pydantic AI to generate and incrementally update LaTeX code for resume sections.
Processes update messages from the frontend and maintains LaTeX state.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Dict, Any, Optional, Union, Literal
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
import asyncio
load_dotenv()

model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(base_url=os.environ.get('BASE_URL')))

# Define data models for resume sections
class NameData(BaseModel):
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""

class AboutMeData(BaseModel):
    description: Optional[str] = ""
    polishedDescription: Optional[str] = ""

class ContactData(BaseModel):
    id: Optional[str] = ""
    type: Optional[str] = ""  # Email, Phone, LinkedIn, etc.
    value: Optional[str] = ""

class EducationData(BaseModel):
    id: Optional[str] = ""
    degree: Optional[str] = ""
    institution: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    graduationDate: Optional[str] = ""
    description: Optional[str] = ""
    gpa: Optional[str] = ""

class ExperienceData(BaseModel):
    id: Optional[str] = ""
    position: Optional[str] = ""
    title: Optional[str] = ""
    company: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    description: Optional[str] = ""
    keywords: Optional[List[str]] = Field(default_factory=list)

class SkillData(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    skill: Optional[str] = ""

class CustomSectionData(BaseModel):
    id: Optional[str] = ""
    title: Optional[str] = ""
    content: Optional[str] = ""

class ResumeData(BaseModel):
    name: NameData
    aboutMe: AboutMeData
    contact: List[ContactData]
    education: List[EducationData]
    experience: List[ExperienceData]
    skills: List[SkillData]
    customSections: List[CustomSectionData]

class UpdateRequest(BaseModel):
    section: str
    entryId: str
    changeType: Literal["add", "update", "delete"]

class LaTeXGenerationRequest(BaseModel):
    type: Literal["full", "incremental"]
    data: ResumeData
    update: Optional[UpdateRequest] = None
    currentLatex: Optional[str] = None

class LaTeXGenerationResult(BaseModel):
    success: bool
    latexCode: str
    sections: Optional[Dict[str, str]] = None
    updatedSections: Optional[Dict[str, str]] = None
    error: Optional[str] = None

# LaTeX Template Components
LATEX_HEADER = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[left=0.75in,top=0.6in,right=0.75in,bottom=0.6in]{geometry}
\usepackage{hyperref}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{url}

% Custom formatting
\titleformat{\section}{\large\bfseries\uppercase}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{12pt}{6pt}

\pagestyle{empty}
\setlength{\tabcolsep}{0in}

% Custom colors
\definecolor{primary}{RGB}{0, 102, 204}

\hypersetup{
    colorlinks=true,
    linkcolor=primary,
    urlcolor=primary,
    citecolor=primary
}

\begin{document}
"""

LATEX_FOOTER = r"""
\end{document}
"""

system_prompt_full = f"""
You are an expert LaTeX generator for professional resumes. Generate clean, modern, and professional LaTeX code based on resume data.

You must use this header provided:
{LATEX_HEADER}
You must use this footer provided:
{LATEX_FOOTER}

**Your Task:**
Generate complete LaTeX resume code that:
1. Uses professional formatting with clean typography
2. Organizes information logically (Header, Summary, Experience, Education, Skills, etc.)
3. Handles missing data gracefully (skip empty sections)
4. Uses consistent spacing and alignment
5. Is ATS-friendly and printer-friendly
6. Includes proper LaTeX escaping for special characters

**Guidelines:**
- DO NOT CHANGE HEADER OR FOOTER
- Use \\textbf{{}} for bold text, \\textit{{}} for italic
- Escape special characters: & → \\&, % → \\%, $ → \\$, # → \\#, _ → \\_
- Use \\href{{url}}{{text}} for links
- Keep consistent date formatting
- Use bullet points for descriptions
- Maintain professional tone throughout

**Structure your response as JSON with:**
{{
  "success": true,
  "latexCode": "complete LaTeX code here",
  "sections": {{
    "header": "LaTeX code for header section",
    "summary": "LaTeX code for about me section", 
    "experience": "LaTeX code for experience section",
    "education": "LaTeX code for education section",
    "skills": "LaTeX code for skills section",
    "custom": "LaTeX code for custom sections"
  }}
}}
"""

system_prompt_incremental = f"""
You are an expert LaTeX generator that handles incremental updates to resume sections.

**Your Task:**
Update specific sections of existing LaTeX code based on change requests while maintaining consistency.

You must use this header provided:
{LATEX_HEADER}
You must use this footer provided:
{LATEX_FOOTER}

**Guidelines:**
1. **For "update" changes**: Replace the specific section with new content
2. **For "add" changes**: Add new entries to the appropriate section
3. **For "delete" changes**: Remove specific entries from sections
4. Maintain consistent formatting with existing code
5. Preserve all other sections unchanged
6. Handle LaTeX escaping properly

**Change Types:**
- name: Update header with name information
- aboutMe: Update summary/objective section
- contact: Update contact information in header
- experience: Update work experience entries
- education: Update education entries  
- skills: Update skills section
- customSections: Update custom resume sections

**Structure your response as JSON with:**
{{
  "success": true,
  "latexCode": "complete updated LaTeX code",
  "updatedSections": {{
    "section_name": "updated LaTeX code for this section only"
  }}
}}
"""

# Create agents
full_generation_agent = Agent(
    model=model,
    output_type=LaTeXGenerationResult,
    system_prompt=system_prompt_full
)

incremental_update_agent = Agent(
    model=model,
    output_type=LaTeXGenerationResult,  
    system_prompt=system_prompt_incremental
)

class LaTeXGeneratorAgent:
    """
    Main LaTeX generator agent that handles both full generation and incremental updates.
    """
    
    def __init__(self):
        self.full_agent = full_generation_agent
        self.incremental_agent = incremental_update_agent
        self.section_cache = {}

    def escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        replacements = {
            '&': '\\&',
            '%': '\\%', 
            ': ': '\\',
            '#': '\\#',
            '^': '\\^{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text

    async def generate_full_latex(self, data: ResumeData) -> LaTeXGenerationResult:
        """
        Generate complete LaTeX code for the entire resume.
        
        Args:
            data: Complete resume data
            
        Returns:
            LaTeXGenerationResult with complete LaTeX code and sections
        """
        try:
            # Prepare data for the agent
            data_dict = data.model_dump()
            
            prompt = f"""
            Generate professional LaTeX resume code for the following data:
            
            {json.dumps(data_dict, indent=2)}
            
            Create a clean, modern resume layout with proper sections and formatting.
            Handle empty fields gracefully by skipping them.
            Use professional typography and consistent spacing.
            """
            
            result = await self.full_agent.run(prompt)
            
            if result.output.success:
                # Cache the sections for future incremental updates
                if result.output.sections:
                    self.section_cache = result.output.sections
                    
            return result.output
            
        except Exception as e:
            return LaTeXGenerationResult(
                success=False,
                latexCode="",
                error=f"Full generation failed: {str(e)}"
            )

    async def update_latex_incremental(self, 
                                     current_latex: str,
                                     update: UpdateRequest,
                                     data: ResumeData) -> LaTeXGenerationResult:
        """
        Update LaTeX code incrementally based on a specific change.
        
        Args:
            current_latex: Current complete LaTeX code
            update: The specific update request
            data: Complete current resume data for context
            
        Returns:
            LaTeXGenerationResult with updated LaTeX code
        """
        try:
            # Prepare the update context
            data_dict = data.model_dump()
            
            prompt = f"""
            Update the following LaTeX code based on this change:
            
            **Current LaTeX:**
            {current_latex}
            
            **Change Request:**
            - Section: {update.section}
            - Entry ID: {update.entryId}
            - Change Type: {update.changeType}
            
            **Current Data Context:**
            {json.dumps(data_dict, indent=2)}
            
            Generate the complete updated LaTeX code with the change applied.
            Only modify the affected section while preserving formatting consistency.
            """
            
            result = await self.incremental_agent.run(prompt)
            
            if result.output.success and result.output.updatedSections:
                # Update our section cache
                self.section_cache.update(result.output.updatedSections)
                
            return result.output
            
        except Exception as e:
            return LaTeXGenerationResult(
                success=False,
                latexCode=current_latex,  # Return unchanged code on error
                error=f"Incremental update failed: {str(e)}"
            )

    def generate_latex_manually(self, data: ResumeData) -> str:
        """
        Fallback manual LaTeX generation for when AI fails.
        """
        latex_parts = [LATEX_HEADER]
        
        # Header section
        if data.name.firstName or data.name.lastName:
            name = f"{data.name.firstName} {data.name.lastName}".strip()
            latex_parts.append(f"\\begin{{center}}\n{{\\Large \\textbf{{{self.escape_latex(name)}}}}}\\\\[5pt]")
            
            # Contact information
            contact_info = []
            for contact in data.contact:
                if contact.value:
                    if contact.type.lower() == 'email':
                        contact_info.append(f"\\href{{mailto:{contact.value}}}{{{self.escape_latex(contact.value)}}}")
                    elif contact.type.lower() in ['linkedin', 'website', 'github']:
                        contact_info.append(f"\\href{{{contact.value}}}{{{self.escape_latex(contact.value)}}}")
                    else:
                        contact_info.append(self.escape_latex(contact.value))
            
            if contact_info:
                latex_parts.append(" | ".join(contact_info))
            
            latex_parts.append("\\end{center}")
            latex_parts.append("")

        # Summary/About Me section  
        if data.aboutMe.description:
            latex_parts.append("\\section{Summary}")
            description = data.aboutMe.polishedDescription or data.aboutMe.description
            latex_parts.append(self.escape_latex(description))
            latex_parts.append("")

        # Experience section
        if data.experience:
            latex_parts.append("\\section{Experience}")
            for exp in data.experience:
                if exp.position or exp.company:
                    title = exp.position or exp.title or ""
                    company = exp.company or ""
                    start_date = exp.startDate or ""
                    end_date = exp.endDate or "Present"
                    
                    latex_parts.append(f"\\textbf{{{self.escape_latex(title)}}} | {self.escape_latex(company)} \\hfill {self.escape_latex(start_date)} - {self.escape_latex(end_date)}\\\\")
                    
                    if exp.description:
                        # Split description into bullet points
                        desc_lines = exp.description.split('\n')
                        if len(desc_lines) > 1:
                            latex_parts.append("\\begin{itemize}[leftmargin=*]")
                            for line in desc_lines:
                                line = line.strip()
                                if line:
                                    latex_parts.append(f"\\item {self.escape_latex(line)}")
                            latex_parts.append("\\end{itemize}")
                        else:
                            latex_parts.append(self.escape_latex(exp.description))
                    
                    latex_parts.append("\\vspace{8pt}")
            latex_parts.append("")

        # Education section
        if data.education:
            latex_parts.append("\\section{Education}")
            for edu in data.education:
                if edu.degree or edu.institution:
                    degree = edu.degree or ""
                    institution = edu.institution or ""
                    grad_date = edu.graduationDate or edu.endDate or ""
                    
                    latex_parts.append(f"\\textbf{{{self.escape_latex(degree)}}} | {self.escape_latex(institution)} \\hfill {self.escape_latex(grad_date)}\\\\")
                    
                    if edu.gpa:
                        latex_parts.append(f"GPA: {self.escape_latex(edu.gpa)}\\\\")
                    
                    if edu.description:
                        latex_parts.append(self.escape_latex(edu.description))
                    
                    latex_parts.append("\\vspace{8pt}")
            latex_parts.append("")

        # Skills section
        if data.skills:
            latex_parts.append("\\section{Skills}")
            skills_list = []
            for skill in data.skills:
                skill_name = skill.name or skill.skill
                if skill_name:
                    skills_list.append(self.escape_latex(skill_name))
            
            if skills_list:
                latex_parts.append(", ".join(skills_list))
            latex_parts.append("")

        # Custom sections
        if data.customSections:
            for section in data.customSections:
                if section.title and section.content:
                    latex_parts.append(f"\\section{{{self.escape_latex(section.title)}}}")
                    latex_parts.append(self.escape_latex(section.content))
                    latex_parts.append("")

        latex_parts.append(LATEX_FOOTER)
        
        return "\n".join(latex_parts)

    async def process_request(self, request: LaTeXGenerationRequest) -> LaTeXGenerationResult:
        """
        Main entry point for processing LaTeX generation requests.
        """
        if request.type == "full":
            result = await self.generate_full_latex(request.data)
            
            # Fallback to manual generation if AI fails
            if not result.success:
                manual_latex = self.generate_latex_manually(request.data)
                result = LaTeXGenerationResult(
                    success=True,
                    latexCode=manual_latex,
                    sections=self.section_cache
                )
            
            return result
            
        elif request.type == "incremental":
            if not request.update or not request.currentLatex:
                return LaTeXGenerationResult(
                    success=False,
                    latexCode="",
                    error="Incremental update requires update info and current LaTeX"
                )
            
            result = await self.update_latex_incremental(
                request.currentLatex,
                request.update,
                request.data
            )
            
            # Fallback to full regeneration if incremental fails
            if not result.success:
                result = await self.generate_full_latex(request.data)
                if not result.success:
                    manual_latex = self.generate_latex_manually(request.data)
                    result = LaTeXGenerationResult(
                        success=True,
                        latexCode=manual_latex
                    )
            
            return result
        
        else:
            return LaTeXGenerationResult(
                success=False,
                latexCode="",
                error=f"Unknown request type: {request.type}"
            )

# Create global instance
latex_generator = LaTeXGeneratorAgent()

# Convenience function for easy import and use
async def generate_latex(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to generate LaTeX from request data.
    
    Args:
        request_data: Dictionary with format:
            {
                "type": "full" | "incremental",
                "data": ResumeData,
                "update": UpdateRequest (for incremental),
                "currentLatex": str (for incremental)
            }
    
    Returns:
        Dictionary with LaTeX generation result
    """
    try:
        request = LaTeXGenerationRequest.model_validate(request_data)
        result = await latex_generator.process_request(request)
        print(result.model_dump())
        return result.model_dump()
    except Exception as e:
        return {
            "success": False,
            "latexCode": "",
            "error": f"Request processing failed: {str(e)}"
        }

sample_req = {
  "type": "full",
  "data": {
    "name": {"firstName": "Ada", "lastName": "Lovelace"},
    "aboutMe": {"description": "Pioneer of computing."},
    "contact": [],
    "education": [],
    "experience": [],
    "skills": [],
    "customSections": []
  }
}

# async def main():
#   result = await generate_latex(sample_req)
#   print("Success:", result.get("success"))
#   print("LaTeX length:", result.get("latexCode",""))

# if __name__ == "__main__":
#   asyncio.run(main())