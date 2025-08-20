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
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(base_url=os.environ.get('BASE_URL')))

# Template analysis result models
class LatexCommand(BaseModel):
    name: str
    parameters: List[str]
    description: str
    usage_pattern: str

class SectionStructure(BaseModel):
    name: str  # e.g., "Education", "Experience", "Skills"
    latex_command: str  # e.g., "\section{Education}"
    entry_pattern: str  # How individual entries are formatted
    required_fields: List[str]  # What data fields this section needs
    optional_fields: List[str]
    formatting_rules: List[str]

class TemplateSchema(BaseModel):
    template_name: str
    document_class: str
    packages: List[str]
    custom_commands: List[LatexCommand]
    header_structure: Dict[str, Any]
    sections: List[SectionStructure]
    formatting_patterns: Dict[str, str]
    spacing_rules: Dict[str, str]
    date_format: str
    special_requirements: List[str]

class TemplateAnalysisResult(BaseModel):
    success: bool
    template_schema: Optional[TemplateSchema] = None
    analysis_notes: Optional[str] = None
    error: Optional[str] = None

system_prompt = """
You are an expert LaTeX template analyzer. Your job is to analyze LaTeX template files and extract their structure, patterns, and formatting rules to create a comprehensive template schema.

**Your Task:**
Analyze the provided LaTeX template and extract:
1. Document structure (documentclass, packages, custom commands)
2. Section organization and hierarchy
3. Formatting patterns for different content types
4. Data field mappings (what resume data goes where)
5. Styling and spacing rules
6. Custom LaTeX commands and their usage

**Critical Requirements:**
- ALWAYS ensure \usepackage{url} is included in packages list
- Identify all custom commands (like \CVSubheading, \CVItem, etc.)
- Map resume data fields to template sections
- Extract formatting patterns for dates, names, positions, etc.
- Note any special styling or layout requirements
- Preserve the professional appearance and structure

**Analysis Focus Areas:**
1. **Header Section**: How name, contact info, and personal details are formatted
2. **Content Sections**: Education, Experience, Skills, etc. - their structure and entry patterns
3. **Custom Commands**: Any special LaTeX commands defined in the template
4. **Formatting Rules**: How different data types (dates, lists, descriptions) are styled
5. **Layout Structure**: Spacing, alignment, and visual organization

**Output Format:**
Return a complete TemplateSchema with all extracted information organized for easy use by a content generation system.

**Example Data Mapping:**
- Resume "firstName" + "lastName" → Template name formatting
- Resume "experience.position" → Template job title formatting
- Resume "education.degree" → Template degree formatting
- etc.

Be thorough and precise - this schema will be used to generate professional resumes matching the template's exact style.
"""

template_parser_agent = Agent(
    model=model,
    output_type=TemplateAnalysisResult,
    system_prompt=system_prompt
)

class TemplateParserAgent:
    """
    Template Parser Agent that analyzes LaTeX template files and extracts their structure.
    """
    
    def __init__(self):
        self.parser_agent = template_parser_agent
        self.template_cache = {}
    
    def ensure_url_package(self, packages: List[str]) -> List[str]:
        """Ensure \usepackage{url} is included in packages"""
        url_variants = ['url', '{url}', '\\usepackage{url}']
        has_url = any(any(variant in pkg for variant in url_variants) for pkg in packages)
        
        if not has_url:
            packages.append('url')
        
        return packages
    
    def extract_basic_structure(self, latex_content: str) -> Dict[str, Any]:
        """
        Extract basic LaTeX structure using regex patterns as fallback.
        """
        basic_info = {
            'document_class': '',
            'packages': [],
            'custom_commands': [],
            'sections_found': []
        }
        
        # Extract document class
        doc_class_match = re.search(r'\\documentclass(?:\[.*?\])?\{([^}]+)\}', latex_content)
        if doc_class_match:
            basic_info['document_class'] = doc_class_match.group(1)
        
        # Extract packages
        package_matches = re.findall(r'\\usepackage(?:\[.*?\])?\{([^}]+)\}', latex_content)
        basic_info['packages'] = package_matches
        
        # Extract custom command definitions
        custom_cmd_matches = re.findall(r'\\newcommand\{\\([^}]+)\}', latex_content)
        basic_info['custom_commands'] = custom_cmd_matches
        
        # Extract sections
        section_matches = re.findall(r'\\section\{([^}]+)\}', latex_content)
        basic_info['sections_found'] = section_matches
        
        return basic_info
    
    async def analyze_template(self, latex_content: str, template_name: str = "Custom Template") -> TemplateAnalysisResult:
        """
        Analyze a LaTeX template and extract its structure and patterns.
        
        Args:
            latex_content: Raw LaTeX template content
            template_name: Name to identify this template
            
        Returns:
            TemplateAnalysisResult with extracted template schema
        """
        try:
            # First, do basic regex extraction as context
            basic_structure = self.extract_basic_structure(latex_content)
            
            prompt = f"""
            Analyze this LaTeX template and create a comprehensive template schema:
            
            **Template Name**: {template_name}
            
            **LaTeX Template Content:**
            ```latex
            {latex_content}
            ```
            
            **Basic Structure Detected:**
            - Document Class: {basic_structure['document_class']}
            - Packages Found: {', '.join(basic_structure['packages'])}
            - Custom Commands: {', '.join(basic_structure['custom_commands'])}
            - Sections Found: {', '.join(basic_structure['sections_found'])}
            
            **Please provide a detailed analysis including:**
            1. Complete package list (ensure 'url' package is included)
            2. All custom commands with their parameters and usage patterns
            3. Section structures and how they map to resume data
            4. Formatting patterns for different content types
            5. Header structure and contact information layout
            6. Date formatting patterns
            7. Spacing and styling rules
            8. Any special requirements or dependencies
            
            **Resume Data Fields to Consider:**
            - name: firstName, lastName
            - contact: email, phone, linkedin, github, website
            - aboutMe: description, summary
            - education: degree, institution, startDate, endDate, gpa, description
            - experience: position, company, startDate, endDate, description
            - skills: name/skill categories
            - customSections: title, content
            
            Create a complete TemplateSchema that captures all the template's structure and formatting rules.
            """
            
            result = await self.parser_agent.run(prompt)
            
            if result.output.success and result.output.template_schema:
                # Ensure URL package is included
                if result.output.template_schema.packages:
                    result.output.template_schema.packages = self.ensure_url_package(
                        result.output.template_schema.packages
                    )
                
                # Cache the result
                self.template_cache[template_name] = result.output.template_schema
                
            return result.output
            
        except Exception as e:
            return TemplateAnalysisResult(
                success=False,
                error=f"Template analysis failed: {str(e)}"
            )
    
    def get_cached_template(self, template_name: str) -> Optional[TemplateSchema]:
        """Get a cached template schema"""
        return self.template_cache.get(template_name)
    
    def list_cached_templates(self) -> List[str]:
        """List all cached template names"""
        return list(self.template_cache.keys())
    
    async def analyze_template_file(self, file_path: str) -> TemplateAnalysisResult:
        """
        Analyze a LaTeX template from a file path.
        
        Args:
            file_path: Path to the .tex template file
            
        Returns:
            TemplateAnalysisResult with extracted template schema
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                latex_content = file.read()
            
            template_name = os.path.splitext(os.path.basename(file_path))[0]
            return await self.analyze_template(latex_content, template_name)
            
        except FileNotFoundError:
            return TemplateAnalysisResult(
                success=False,
                error=f"Template file not found: {file_path}"
            )
        except Exception as e:
            return TemplateAnalysisResult(
                success=False,
                error=f"Failed to read template file: {str(e)}"
            )

# Create global instance
template_parser = TemplateParserAgent()

# Convenience function for easy import and use
async def parse_template(latex_content: str, template_name: str = "Custom Template") -> Dict[str, Any]:
    """
    Convenience function to parse a LaTeX template.
    
    Args:
        latex_content: Raw LaTeX template content
        template_name: Name to identify this template
    
    Returns:
        Dictionary with template analysis result
    """
    try:
        result = await template_parser.analyze_template(latex_content, template_name)
        return result.model_dump()
    except Exception as e:
        return {
            "success": False,
            "error": f"Template parsing failed: {str(e)}"
        }

async def parse_template_file(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse a LaTeX template from file.
    
    Args:
        file_path: Path to the .tex template file
    
    Returns:
        Dictionary with template analysis result
    """
    try:
        result = await template_parser.analyze_template_file(file_path)
        return result.model_dump()
    except Exception as e:
        return {
            "success": False,
            "error": f"Template file parsing failed: {str(e)}"
        }

# Sample usage and testing
sample_latex = """
\\documentclass[11pt,a4paper]{article}
\\usepackage[left=0.75in,top=0.6in,right=0.75in,bottom=0.6in]{geometry}
\\usepackage{hyperref}
\\usepackage{titlesec}
\\begin{document}
\\section{Education}
\\textbf{Degree} | Institution \\hfill Date
\\end{document}
"""

# Uncomment for testing
# async def test_parser():
#     result = await parse_template(sample_latex, "Simple Template")
#     print("Success:", result.get("success"))
#     if result.get("success"):
#         schema = result.get("template_schema")
#         print("Packages:", schema.get("packages"))
#         print("Sections:", [s.get("name") for s in schema.get("sections", [])])

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(test_parser())