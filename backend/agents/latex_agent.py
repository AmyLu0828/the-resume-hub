"""
LaTeX Generator Agent for Resume Builder
Uses Pydantic AI to generate and incrementally update LaTeX code for resume sections.
Works with parsed templates from simple_template_parser_agent for consistent formatting.
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

# Import the template parser agent
from .simple_template_parser_agent import analyze_template_file

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
    template_path: Optional[str] = None  # Path to template file

class LaTeXGenerationResult(BaseModel):
    success: bool
    latexCode: str
    sections: Optional[Dict[str, str]] = None
    updatedSections: Optional[Dict[str, str]] = None
    template_used: Optional[str] = None
    error: Optional[str] = None

# Updated system prompts for template-based generation
system_prompt_full = """
You are an expert LaTeX content generator that creates professional resumes using pre-analyzed templates.

**Your Task:**
Generate complete LaTeX code by filling a template with user resume data while preserving the template's exact structure and formatting.

**Critical Requirements:**
1. ALWAYS include \\usepackage{url} in the preamble - this is mandatory
2. Make sure that the code you generate matches with the template's structure exactly
3. Use proper LaTeX escaping for special characters: & → \\&, % → \\%, $ → \\$, # → \\#, _ → \\_
4. You do not have to keep sections that do not have data yet
5. Maintain professional appearance and structure
6. Follow the template's custom commands and formatting rules
7. Preserve spacing and layout patterns from the original template
8. Replace placeholder text with actual user data while maintaining formatting

**Template Integration:**
- Use the provided template as the base structure
- Replace placeholders like "Placeholder for experience name 1" with actual user data
- Maintain all custom commands (\\CVSubheading, \\CVItem, etc.) exactly as defined
- Keep the same spacing, fonts, and layout structure
- Only modify content, never the template structure itself

**Output Requirements:**
Return complete, compilable LaTeX code that exactly matches the template's style and structure.

**Response Format:**
{
  "success": true,
  "latexCode": "complete LaTeX document here",
  "sections": {
    "header": "LaTeX for header section",
    "education": "LaTeX for education section",
    "experience": "LaTeX for experience section",
    "skills": "LaTeX for skills section"
  },
  "template_used": "template_name"
}
"""

system_prompt_incremental = """
You are an expert LaTeX generator that handles incremental updates to template-based resumes.

**Your Task:**
Update specific sections of existing LaTeX code based on change requests while maintaining the template's exact structure and formatting consistency.

**Critical Requirements:**
1. ALWAYS ensure \\usepackage{url} remains in the preamble
2. Preserve the template's formatting patterns exactly
3. Only modify the specified section while keeping everything else unchanged
4. Use the template's custom commands and patterns consistently
5. Handle LaTeX escaping properly
6. Maintain exact spacing patterns from template

**Update Types:**
- "update": Replace the specific section with new content
- "add": Add new entries to the appropriate section
- "delete": Remove specific entries from sections

**Template Consistency:**
- Maintain exact spacing patterns from template
- Use same custom commands as defined in template
- Preserve formatting rules for dates, names, descriptions, etc.
- Keep section structure and hierarchy identical
- Only change content, never the template structure

**Change Types:**
- name: Update header with name information
- aboutMe: Update summary/objective section
- contact: Update contact information in header
- experience: Update work experience entries
- education: Update education entries  
- skills: Update skills section
- customSections: Update custom resume sections

**Structure your response as JSON with:**
{
  "success": true,
  "latexCode": "complete updated LaTeX code",
  "updatedSections": {
    "section_name": "updated LaTeX code for this section only"
  }
}
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
    Works with parsed templates for consistent formatting.
    """
    
    def __init__(self):
        self.full_agent = full_generation_agent
        self.incremental_agent = incremental_update_agent
        self.section_cache = {}
        self.template_cache = None
        self.template_path = None

    async def get_or_create_template(self, template_path: str) -> str:
        """
        Get template from cache or parse it using simple_template_parser_agent.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            Parsed template content
        """
        # If we have a cached template and it's the same path, use it
        if self.template_cache and self.template_path == template_path:
            return self.template_cache
        
        # Otherwise, parse the template using simple_template_parser_agent
        try:
            template_content = await analyze_template_file(template_path)
            self.template_cache = template_content
            self.template_path = template_path
            return template_content
        except Exception as e:
            raise Exception(f"Failed to parse template: {str(e)}")

    async def generate_full_latex(self, data: ResumeData, template_path: str) -> LaTeXGenerationResult:
        """
        Generate complete LaTeX code for the entire resume using a template.
        
        Args:
            data: Complete resume data
            template_path: Path to the template file
            
        Returns:
            LaTeXGenerationResult with complete LaTeX code and sections
        """
        try:
            # Get or create template
            template_content = await self.get_or_create_template(template_path)
            
            # Prepare data for the agent
            data_dict = data.model_dump()
            
            prompt = f"""
            Generate professional LaTeX resume code using this template and user data:
            
            **Template Content:**
            {template_content}
            
            **Resume Data:**
            {json.dumps(data_dict, indent=2)}
            
            **Instructions:**
            1. Use the provided template as the base structure
            2. Replace all placeholder text with actual user data while maintaining exact formatting
            3. Keep all custom commands (\\CVSubheading, \\CVItem, etc.) exactly as defined
            4. Maintain the same spacing, fonts, and layout structure
            5. Only modify content, never the template structure itself
            6. Handle empty data gracefully by keeping placeholder structure for empty sections
            7. Ensure \\usepackage{{url}} is present
            8. Use proper LaTeX escaping for special characters
            
            Create a complete, compilable LaTeX document that looks exactly like it was created with the original template.
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
                                     data: ResumeData,
                                     template_path: str) -> LaTeXGenerationResult:
        """
        Update LaTeX code incrementally based on a specific change.
        
        Args:
            current_latex: Current complete LaTeX code
            update: The specific update request
            data: Complete current resume data for context
            template_path: Path to the template file for consistency
            
        Returns:
            LaTeXGenerationResult with updated LaTeX code
        """
        try:
            # Get template for context (to ensure formatting consistency)
            template_content = await self.get_or_create_template(template_path)
            
            # Prepare the update context
            data_dict = data.model_dump()
            
            prompt = f"""
            Update the following LaTeX code based on this change while maintaining template consistency:
            
            **Template Content (for reference):**
            {template_content}
            
            **Current LaTeX:**
            {current_latex}
            
            **Change Request:**
            - Section: {update.section}
            - Entry ID: {update.entryId}
            - Change Type: {update.changeType}
            
            **Current Data Context:**
            {json.dumps(data_dict, indent=2)}
            
            **Instructions:**
            1. Use the template as a reference to maintain formatting consistency
            2. Only modify the affected section while preserving everything else
            3. Maintain exact spacing patterns and custom commands from the template
            4. Keep the same structure and layout
            5. Handle LaTeX escaping properly
            6. Ensure the updated section follows the template's formatting rules
            
            Generate the complete updated LaTeX code with the change applied.
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

    def generate_latex_manually(self, data: ResumeData, template_content: str) -> str:
        """
        Fallback manual LaTeX generation for when AI fails.
        Uses template structure but fills in content manually.
        """
        # This is a simplified fallback - in practice, you might want to implement
        # a more sophisticated template-based manual generation
        return template_content

    async def process_request(self, request: LaTeXGenerationRequest) -> LaTeXGenerationResult:
        """
        Main entry point for processing LaTeX generation requests.
        """
        if not request.template_path:
            return LaTeXGenerationResult(
                success=False,
                latexCode="",
                error="Template path is required for template-based generation"
            )
        
        if request.type == "full":
            result = await self.generate_full_latex(request.data, request.template_path)
            
            # Fallback to manual generation if AI fails
            if not result.success:
                try:
                    template_content = await self.get_or_create_template(request.template_path)
                    manual_latex = self.generate_latex_manually(request.data, template_content)
                    result = LaTeXGenerationResult(
                        success=True,
                        latexCode=manual_latex,
                        sections=self.section_cache,
                        template_used=request.template_path
                    )
                except Exception as e:
                    result = LaTeXGenerationResult(
                        success=False,
                        latexCode="",
                        error=f"Manual generation also failed: {str(e)}"
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
                request.data,
                request.template_path
            )
            
            # Fallback to full regeneration if incremental fails
            if not result.success:
                result = await self.generate_full_latex(request.data, request.template_path)
                if not result.success:
                    try:
                        template_content = await self.get_or_create_template(request.template_path)
                        manual_latex = self.generate_latex_manually(request.data, template_content)
                        result = LaTeXGenerationResult(
                            success=True,
                            latexCode=manual_latex,
                            template_used=request.template_path
                        )
                    except Exception as e:
                        result = LaTeXGenerationResult(
                            success=False,
                            latexCode="",
                            error=f"All generation methods failed: {str(e)}"
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
                "currentLatex": str (for incremental),
                "template_path": str (required)
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

# Updated sample request with template path
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
  },
  "template_path": "backend/templates/default_resume.tex"
}

# async def main():
#   result = await generate_latex(sample_req)
#   print("Success:", result.get("success"))
#   print("LaTeX length:", result.get("latexCode",""))

# if __name__ == "__main__":
#   asyncio.run(main())