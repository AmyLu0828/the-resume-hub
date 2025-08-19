"""
LaTeX Agent for Resume Template Processing

This file contains:
1. LaTeX template management system
2. Template filling logic with resume data
3. Multiple template options (professional, creative, minimal, etc.)
4. LaTeX source code generation

Key functions implemented:
- load_template(template_name: str) -> str
- fill_template(template: str, resume_data: dict) -> str
- validate_latex_source(latex_source: str) -> bool
- get_available_templates() -> List[str]
- generate_latex(resume_data: dict) -> str
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template, Environment, FileSystemLoader
import re

class LaTeXAgent:
    """
    LaTeX template processing agent for resume generation
    """
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Available templates
        self.available_templates = [
            "default_resume.tex",
            "professional_resume.tex", 
            "creative_resume.tex",
            "minimal_resume.tex"
        ]
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names"""
        return [template.replace('.tex', '') for template in self.available_templates]
    
    def load_template(self, template_name: str) -> str:
        """Load LaTeX template from file"""
        template_path = self.templates_dir / f"{template_name}.tex"
        
        if not template_path.exists():
            # Fallback to default template
            template_path = self.templates_dir / "default_resume.tex"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def generate_latex(self, resume_data: Dict[str, Any], template_name: str = "default") -> str:
        """
        Generate complete LaTeX source from resume data
        
        Args:
            resume_data: Resume data dictionary
            template_name: Name of template to use
            
        Returns:
            Complete LaTeX source code
        """
        # Load template
        template_source = self.load_template(template_name)
        
        # Process resume data for template
        processed_data = self._process_resume_data(resume_data)
        
        # Fill template
        latex_source = self.fill_template(template_source, processed_data)
        
        # Validate generated LaTeX
        if not self.validate_latex_source(latex_source):
            raise ValueError("Generated LaTeX source is invalid")
        
        return latex_source
    
    def fill_template(self, template_source: str, resume_data: Dict[str, Any]) -> str:
        """
        Fill template with resume data using Jinja2
        
        Args:
            template_source: Raw LaTeX template
            resume_data: Processed resume data
            
        Returns:
            Filled LaTeX template
        """
        template = Template(template_source)
        return template.render(**resume_data)
    
    def _process_resume_data(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process resume data for template rendering
        
        Args:
            resume_data: Raw resume data from frontend
            
        Returns:
            Processed data ready for template
        """
        processed = {}
        
        # Process name
        if 'name' in resume_data:
            name = resume_data['name']
            processed['firstName'] = self._escape_latex(name.get('firstName', ''))
            processed['lastName'] = self._escape_latex(name.get('lastName', ''))
            processed['fullName'] = f"{processed['firstName']} {processed['lastName']}".strip()
        
        # Process about me
        if 'aboutMe' in resume_data:
            about_me = resume_data['aboutMe']
            description = about_me.get('polishedDescription') or about_me.get('description', '')
            processed['aboutMe'] = self._escape_latex(description)
        
        # Process contact information
        if 'contact' in resume_data:
            processed['contact'] = []
            for contact in resume_data['contact']:
                processed['contact'].append({
                    'type': self._escape_latex(contact.get('type', '')),
                    'value': self._escape_latex(contact.get('value', ''))
                })
        
        # Process education
        if 'education' in resume_data:
            processed['education'] = []
            for edu in resume_data['education']:
                description = edu.get('polishedDescription') or edu.get('description', '')
                processed['education'].append({
                    'degree': self._escape_latex(edu.get('degree', '')),
                    'institution': self._escape_latex(edu.get('institution', '')),
                    'startDate': self._format_date(edu.get('startDate', '')),
                    'endDate': self._format_date(edu.get('endDate', '')),
                    'description': self._escape_latex(description)
                })
        
        # Process experience
        if 'experience' in resume_data:
            processed['experience'] = []
            for exp in resume_data['experience']:
                description = exp.get('polishedDescription') or exp.get('description', '')
                processed['experience'].append({
                    'title': self._escape_latex(exp.get('title', '')),
                    'company': self._escape_latex(exp.get('company', '')),
                    'startDate': self._format_date(exp.get('startDate', '')),
                    'endDate': self._format_date(exp.get('endDate', '')),
                    'description': self._escape_latex(description),
                    'keywords': [self._escape_latex(kw) for kw in exp.get('keywords', [])]
                })
        
        # Process skills
        if 'skills' in resume_data:
            processed['skills'] = [self._escape_latex(skill.get('skill', '')) for skill in resume_data['skills']]
        
        # Process custom sections
        if 'customSections' in resume_data:
            processed['customSections'] = []
            for section in resume_data['customSections']:
                processed['customSections'].append({
                    'title': self._escape_latex(section.get('title', '')),
                    'content': self._escape_latex(section.get('content', ''))
                })
        
        return processed
    
    def _escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters
        
        Args:
            text: Raw text
            
        Returns:
            LaTeX-escaped text
        """
        if not text:
            return ""
        
        # LaTeX special characters that need escaping
        latex_chars = {
            '\\': r'\textbackslash{}',
            '{': r'\{',
            '}': r'\}',
            '$': r'\$',
            '&': r'\&',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '~': r'\textasciitilde{}',
            '%': r'\%'
        }
        
        escaped_text = text
        for char, replacement in latex_chars.items():
            escaped_text = escaped_text.replace(char, replacement)
        
        return escaped_text
    
    def _format_date(self, date_str: str) -> str:
        """
        Format date string for LaTeX
        
        Args:
            date_str: Date in YYYY-MM format
            
        Returns:
            Formatted date string
        """
        if not date_str:
            return "Present"
        
        try:
            year, month = date_str.split('-')
            month_names = {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
            }
            month_name = month_names.get(month, month)
            return f"{month_name} {year}"
        except:
            return date_str
    
    def validate_latex_source(self, latex_source: str) -> bool:
        """
        Basic validation of LaTeX source
        
        Args:
            latex_source: Generated LaTeX source
            
        Returns:
            True if valid, False otherwise
        """
        if not latex_source:
            return False
        
        # Check for basic LaTeX structure
        required_elements = [
            r'\\documentclass',
            r'\\begin\{document\}',
            r'\\end\{document\}'
        ]
        
        for element in required_elements:
            if not re.search(element, latex_source):
                return False
        
        # Check for balanced braces
        brace_count = 0
        for char in latex_source:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count < 0:
                    return False
        
        return brace_count == 0
