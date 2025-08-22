"""
Template Content Generator Agent for Resume Builder
Uses parsed template schemas to generate LaTeX code with user resume data.
Works in conjunction with the Template Parser Agent to create template-driven resumes.
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

# Import the template parser models
from template_parser_agent import TemplateSchema, TemplateParserAgent

load_dotenv()

model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(base_url=os.environ.get('BASE_URL')))

# Resume data models (same as original)
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

class TemplateGenerationRequest(BaseModel):
    type: Literal["full", "incremental"]
    template_schema: TemplateSchema
    resume_data: ResumeData
    update: Optional[UpdateRequest] = None
    current_latex: Optional[str] = None

class TemplateGenerationResult(BaseModel):
    success: bool
    latex_code: str
    sections: Optional[Dict[str, str]] = None
    updated_sections: Optional[Dict[str, str]] = None
    template_used: Optional[str] = None
    error: Optional[str] = None

system_prompt_full = """
You are an expert LaTeX content generator that creates professional resumes using pre-analyzed template schemas.

**Your Task:**
Generate complete LaTeX code by filling a template schema with user resume data while preserving the template's exact structure and formatting.

**Critical Requirements:**
1. ALWAYS include \\usepackage{url} in the preamble - this is mandatory
2. Follow the template schema exactly - preserve all formatting patterns
3. Use proper LaTeX escaping for special characters: & → \\&, % → \\%, $ → \\$, # → \\#, _ → \\_
4. Handle missing data gracefully (skip empty sections/fields)
5. Maintain professional appearance and structure
6. Follow the template's custom commands and formatting rules exactly
7. Preserve spacing and layout patterns from the original template

**Template Schema Structure:**
- document_class: LaTeX document class to use
- packages: List of required packages (ensure 'url' is included)
- custom_commands: Custom LaTeX commands defined in template
- header_structure: How to format name and contact information
- sections: List of resume sections with their formatting patterns
- formatting_patterns: Specific formatting rules for different content types
- date_format: How dates should be formatted
- spacing_rules: Spacing and layout requirements

**Data Mapping:**
Map resume data fields to template patterns:
- name.firstName + name.lastName → template header name format
- contact[] → template contact information layout
- experience[] → template job entry format using custom commands
- education[] → template education entry format
- skills[] → template skills section format
- etc.

**Output Requirements:**
Return complete, compilable LaTeX code that exactly matches the template's style and structure.

**Response Format:**
{
  "success": true,
  "latex_code": "complete LaTeX document here",
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
You are an expert LaTeX content generator that handles incremental updates to template-based resumes.

**Your Task:**
Update specific sections of existing template-based LaTeX code while maintaining the template's exact structure and formatting consistency.

**Critical Requirements:**
1. ALWAYS ensure \\usepackage{url} remains in the preamble
2. Preserve the template's formatting patterns exactly
3. Only modify the specified section while keeping everything else unchanged
4. Use the template schema to maintain formatting consistency
5. Handle LaTeX escaping properly
6. Follow the template's custom commands and patterns

**Update Types:**
- "add": Add new entries to the specified section
- "update": Modify existing entries in the section
- "delete": Remove entries from the section

**Template Consistency:**
- Maintain exact spacing patterns from template
- Use same custom commands as defined in template schema
- Preserve formatting rules for dates, names, descriptions, etc.
- Keep section structure and hierarchy identical

**Response Format:**
{
  "success": true,
  "latex_code": "complete updated LaTeX document",
  "updated_sections": {
    "section_name": "updated LaTeX for this section only"
  },
  "template_used": "template_name"
}
"""

# Create agents
full_generation_agent = Agent(
    model=model,
    output_type=TemplateGenerationResult,
    system_prompt=system_prompt_full
)

incremental_update_agent = Agent(
    model=model,
    output_type=TemplateGenerationResult,
    system_prompt=system_prompt_incremental
)

class TemplateContentGeneratorAgent:
    """
    Template Content Generator Agent that creates LaTeX code using template schemas.
    """
    
    def __init__(self):
        self.full_agent = full_generation_agent
        self.incremental_agent = incremental_update_agent
        self.template_parser = TemplateParserAgent()
        self.generation_cache = {}
    
    def escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        replacements = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
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
    
    def ensure_url_package(self, latex_code: str) -> str:
        """Ensure \\usepackage{url} is present in LaTeX code"""
        if '\\usepackage{url}' not in latex_code:
            # Check if there are any usepackage commands
            if '\\usepackage' in latex_code:
                # Find the last usepackage command and insert after it
                last_usepackage_pos = latex_code.rfind('\\usepackage')
                if last_usepackage_pos != -1:
                    # Find the end of the last usepackage command
                    end_pos = latex_code.find('}', last_usepackage_pos)
                    if end_pos != -1:
                        latex_code = latex_code[:end_pos+1] + '\n\\usepackage{url}' + latex_code[end_pos+1:]
            else:
                # Find document class and insert after it
                doc_class_match = re.search(r'(\\documentclass(?:\[.*?\])?\{[^}]+\})', latex_code)
                if doc_class_match:
                    insert_pos = doc_class_match.end()
                    latex_code = latex_code[:insert_pos] + '\n\\usepackage{url}' + latex_code[insert_pos:]
                else:
                    # Fallback: add at the beginning
                    latex_code = '\\usepackage{url}\n' + latex_code
        
        return latex_code
    
    async def generate_with_template(self, 
                                   template_schema: TemplateSchema, 
                                   resume_data: ResumeData) -> TemplateGenerationResult:
        """
        Generate complete LaTeX code using a template schema.
        
        Args:
            template_schema: Parsed template structure and rules
            resume_data: User's resume data
            
        Returns:
            TemplateGenerationResult with generated LaTeX code
        """
        try:
            # Prepare data for the agent
            schema_dict = template_schema.model_dump()
            data_dict = resume_data.model_dump()
            
            prompt = f"""
            Generate professional LaTeX resume code using this template schema and user data:
            
            **Template Schema:**
            {json.dumps(schema_dict, indent=2)}
            
            **Resume Data:**
            {json.dumps(data_dict, indent=2)}
            
            **Instructions:**
            1. Follow the template schema exactly - use the same custom commands, formatting patterns, and structure
            2. Map the resume data to the template's expected format
            3. Include ALL required packages from the template schema (plus 'url' package)
            4. Use the template's custom commands (like \\CVSubheading, \\CVItem, etc.) exactly as defined
            5. Follow the template's date formatting, spacing rules, and layout patterns
            6. Handle empty data gracefully by skipping those sections
            7. Maintain the professional appearance and structure of the original template
            
            Create a complete, compilable LaTeX document that looks exactly like it was created with the original template.
            """
            
            result = await self.full_agent.run(prompt)
            
            if result.output.success and result.output.latex_code:
                # Ensure URL package is included
                result.output.latex_code = self.ensure_url_package(result.output.latex_code)
                result.output.template_used = template_schema.template_name
                
                # Cache the result
                cache_key = f"{template_schema.template_name}_{hash(str(data_dict))}"
                self.generation_cache[cache_key] = result.output
                
            return result.output
            
        except Exception as e:
            return TemplateGenerationResult(
                success=False,
                latex_code="",
                error=f"Template-based generation failed: {str(e)}"
            )
    
    async def update_with_template(self, 
                                 template_schema: TemplateSchema,
                                 current_latex: str,
                                 update: UpdateRequest,
                                 resume_data: ResumeData) -> TemplateGenerationResult:
        """
        Update LaTeX code incrementally using template schema.
        
        Args:
            template_schema: Template structure and rules
            current_latex: Current complete LaTeX code
            update: The specific update request
            resume_data: Complete current resume data
            
        Returns:
            TemplateGenerationResult with updated LaTeX code
        """
        try:
            schema_dict = template_schema.model_dump()
            data_dict = resume_data.model_dump()
            
            prompt = f"""
            Update this LaTeX code using the template schema to maintain formatting consistency:
            
            **Template Schema:**
            {json.dumps(schema_dict, indent=2)}
            
            **Current LaTeX Code:**
            {current_latex}
            
            **Update Request:**
            - Section: {update.section}
            - Entry ID: {update.entryId}
            - Change Type: {update.changeType}
            
            **Updated Resume Data:**
            {json.dumps(data_dict, indent=2)}
            
            **Instructions:**
            1. Apply the requested change while maintaining template formatting exactly
            2. Use the template's custom commands and patterns for the updated content
            3. Preserve all other sections unchanged
            4. Ensure \\usepackage{{url}} remains in the preamble
            5. Follow the template's formatting rules for the updated section
            6. Maintain consistent spacing and layout as defined in template schema
            
            Return the complete updated LaTeX document with the change applied.
            """
            
            result = await self.incremental_agent.run(prompt)
            
            if result.output.success and result.output.latex_code:
                result.output.latex_code = self.ensure_url_package(result.output.latex_code)
                result.output.template_used = template_schema.template_name
                
            return result.output
            
        except Exception as e:
            return TemplateGenerationResult(
                success=False,
                latex_code=current_latex,  # Return unchanged on error
                error=f"Template-based incremental update failed: {str(e)}"
            )
    
    async def process_request(self, request: TemplateGenerationRequest) -> TemplateGenerationResult:
        """
        Main entry point for processing template-based LaTeX generation requests.
        """
        if request.type == "full":
            result = await self.generate_with_template(request.template_schema, request.resume_data)
            
            # Fallback to manual generation if AI fails
            if not result.success:
                fallback_latex = self.generate_fallback_latex(request.resume_data, request.template_schema.template_name)
                result = TemplateGenerationResult(
                    success=True,
                    latex_code=fallback_latex,
                    template_used=request.template_schema.template_name
                )
            
            return result
            
        elif request.type == "incremental":
            if not request.update or not request.current_latex:
                return TemplateGenerationResult(
                    success=False,
                    latex_code="",
                    error="Incremental update requires update info and current LaTeX"
                )
            
            result = await self.update_with_template(
                request.template_schema,
                request.current_latex,
                request.update,
                request.resume_data
            )
            
            # Fallback to full regeneration if incremental fails
            if not result.success:
                result = await self.generate_with_template(request.template_schema, request.resume_data)
                if not result.success:
                    fallback_latex = self.generate_fallback_latex(request.resume_data, request.template_schema.template_name)
                    result = TemplateGenerationResult(
                        success=True,
                        latex_code=fallback_latex,
                        template_used=request.template_schema.template_name
                    )
            
            return result
        
        else:
            return TemplateGenerationResult(
                success=False,
                latex_code="",
                error=f"Unknown request type: {request.type}"
            )

# Create global instance
template_content_generator = TemplateContentGeneratorAgent()

# Convenience functions for easy import and use
async def generate_with_template_schema(template_schema_dict: Dict[str, Any], 
                                      resume_data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate LaTeX using a template schema and resume data.
    
    Args:
        template_schema_dict: Template schema as dictionary
        resume_data_dict: Resume data as dictionary
    
    Returns:
        Dictionary with generation result
    """
    try:
        template_schema = TemplateSchema.model_validate(template_schema_dict)
        resume_data = ResumeData.model_validate(resume_data_dict)
        
        request = TemplateGenerationRequest(
            type="full",
            template_schema=template_schema,
            resume_data=resume_data
        )
        
        result = await template_content_generator.process_request(request)
        return result.model_dump()
        
    except Exception as e:
        return {
            "success": False,
            "latex_code": "",
            "error": f"Template generation failed: {str(e)}"
        }

async def update_with_template_schema(template_schema_dict: Dict[str, Any],
                                    current_latex: str,
                                    update_dict: Dict[str, Any],
                                    resume_data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update LaTeX using a template schema and update request.
    
    Args:
        template_schema_dict: Template schema as dictionary
        current_latex: Current LaTeX code
        update_dict: Update request as dictionary
        resume_data_dict: Resume data as dictionary
    
    Returns:
        Dictionary with update result
    """
    try:
        template_schema = TemplateSchema.model_validate(template_schema_dict)
        resume_data = ResumeData.model_validate(resume_data_dict)
        update_request = UpdateRequest.model_validate(update_dict)
        
        request = TemplateGenerationRequest(
            type="incremental",
            template_schema=template_schema,
            resume_data=resume_data,
            update=update_request,
            current_latex=current_latex
        )
        
        result = await template_content_generator.process_request(request)
        return result.model_dump()
        
    except Exception as e:
        return {
            "success": False,
            "latex_code": current_latex,
            "error": f"Template update failed: {str(e)}"
        }

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_generator():
        # Example test data
        template_schema = {
            "template_name": "test_template",
            "document_class": "article",
            "packages": ["geometry", "hyperref"],
            "custom_commands": {},
            "header_structure": "centered",
            "sections": ["experience", "education", "skills"],
            "formatting_patterns": {},
            "date_format": "MM/YYYY",
            "spacing_rules": {}
        }
        
        resume_data = {
            "name": {"firstName": "John", "lastName": "Doe"},
            "aboutMe": {"description": "Experienced software engineer", "polishedDescription": ""},
            "contact": [
                {"id": "1", "type": "email", "value": "john@example.com"},
                {"id": "2", "type": "phone", "value": "123-456-7890"}
            ],
            "education": [
                {"id": "1", "degree": "BSc Computer Science", "institution": "University of Test", "startDate": "2018", "endDate": "2022"}
            ],
            "experience": [
                {"id": "1", "position": "Software Engineer", "company": "Tech Corp", "startDate": "2022", "endDate": "Present"}
            ],
            "skills": [
                {"id": "1", "name": "Python", "skill": ""},
                {"id": "2", "name": "JavaScript", "skill": ""}
            ],
            "customSections": []
        }
        
        result = await generate_with_template_schema(template_schema, resume_data)
        print("Generation result:", result["success"])
        if result["success"]:
            print("Generated LaTeX length:", len(result["latex_code"]))
    
    asyncio.run(test_generator())