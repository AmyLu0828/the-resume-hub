# main.py - FIXED VERSION
import sys
from typing import Dict, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os
import asyncio
from dotenv import load_dotenv
import httpx
import logfire
import pydantic_core
from openai import AsyncOpenAI
from pydantic import TypeAdapter
from typing_extensions import AsyncGenerator
from dataclasses import dataclass


class GeneratedContent(BaseModel):
    schema: str = Field(..., description="LaTeX schema based on the template")
    latex: str = Field(..., description="The actual LaTeX code with user request applied")

load_dotenv()

model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(base_url=os.environ.get('BASE_URL')))

@dataclass
class Deps:
    template: str
    type: str
    current: str

system_prompt = """
You are a LaTeX CV generator agent. You specialize in generating clean, properly formatted LaTeX code for resumes.

When generating content:
1. Analyze the template structure carefully
2. Apply the user's data to match the template format exactly
3. Ensure proper LaTeX formatting and syntax
4. Maintain consistent spacing and structure
5. Handle edge cases gracefully (empty fields, missing data, etc.)
"""

# Create the generator agent
generator_agent = Agent(
    model=model, 
    system_prompt=system_prompt, 
    deps_type=Deps,
    output_type=GeneratedContent
)

# FIXED: Better caching system
cache = {
    "header": None,
    "section": None
}

@generator_agent.system_prompt
def add_instructions(ctx: RunContext[Deps]) -> str:
    basic_prompt = f"""
    You are a LaTeX CV generator agent specialized in resume generation.

    CRITICAL INSTRUCTIONS:
    1. Generate ONLY valid LaTeX code - no placeholders, no comments
    2. Use actual data provided by the user
    3. Handle missing/empty data gracefully
    4. Maintain proper LaTeX syntax and structure
    5. Ensure consistent formatting
    """
    
    if cache[ctx.deps.type] is None:
        add_prompt = f"""
        TEMPLATE ANALYSIS AND FIRST-TIME GENERATION:
        
        Here is the {ctx.deps.type} template:
        {ctx.deps.template}
        
        Your tasks:
        1. **Analyze Structure**: Understand the LaTeX commands, environments, and formatting
        2. **Create Schema**: Document the structure pattern (for caching)
        3. **Generate Code**: Replace template content with user data
        
        EXAMPLE TRANSFORMATION:
        Template: \\textbf{{\\Huge \\scshape{{Charles Rambo}}}}
        User data: {{"name": {{"firstName": "John", "lastName": "Doe"}}}}
        Result: \\textbf{{\\Huge \\scshape{{John Doe}}}}
        
        HANDLE MISSING DATA:
        - If firstName missing: use lastName only
        - If both missing: use "Your Name"
        - If contact empty: skip that line
        - If description empty: use brief placeholder
        
        Return structured response:
        {{
            "schema": "Brief description of template structure and key LaTeX patterns",
            "latex": "Complete, ready-to-use LaTeX code with user data applied"
        }}
        """
    else: 
        add_prompt = f"""
        INCREMENTAL UPDATE USING CACHED SCHEMA:
        
        Cached template schema: {cache[ctx.deps.type]}
        
        Your task:
        - Use the cached schema to generate LaTeX code
        - Apply user data according to the established pattern
        - Ensure consistency with previous generations
        
        Return:
        {{
            "schema": "{cache[ctx.deps.type]}",
            "latex": "Complete LaTeX code with user data applied"
        }}
        """

    return "".join([basic_prompt, add_prompt])


# FIXED: Enhanced generation function with better error handling
async def generate_latex_content(request: dict, template: str = None, type: str = "None", current = None):
    try:
        # Create dependencies
        if current and current.strip():
            query = f"""
            INCREMENTAL UPDATE REQUEST:
            
            Current LaTeX content:
            {current}
            
            Update request: {request}
            
            INSTRUCTIONS:
            1. Identify the specific section to update based on the request
            2. Keep ALL existing content unchanged
            3. Only modify/add the requested changes
            4. Maintain proper LaTeX structure and formatting
            5. Preserve spacing and organization
            
            Return the complete updated LaTeX with your changes integrated.
            """
        else:
            # FIXED: Better formatting of user request
            if isinstance(request, dict):
                if 'name' in request or 'contact' in request:
                    # Header generation
                    query = f"""
                    HEADER GENERATION REQUEST:
                    
                    User data: {request}
                    
                    INSTRUCTIONS:
                    1. Generate header section with name and contact information
                    2. Use proper LaTeX formatting for names (\\textbf, \\Huge, \\scshape)
                    3. Format contact info with proper spacing and links
                    4. Handle missing data gracefully
                    5. Follow the template structure exactly
                    
                    Data mapping:
                    - name.firstName + name.lastName → Full name in header
                    - contact array → Individual contact lines (email, phone, etc.)
                    """
                else:
                    # Section generation
                    query = f"""
                    SECTION GENERATION REQUEST:
                    
                    Section: {request.get('section', 'Unknown')}
                    Data: {request.get('entry', request)}
                    
                    INSTRUCTIONS:
                    1. Generate the appropriate section based on the template
                    2. Use proper LaTeX section commands
                    3. Format content according to the template structure
                    4. Handle arrays/lists properly
                    5. Maintain consistent formatting
                    """
            else:
                query = f"""
                GENERAL GENERATION REQUEST:
                
                Request: {request}
                
                Generate appropriate LaTeX code based on the template structure.
                """
        
        deps = Deps(template=template or "", type=type, current=current or "")
        
        # Run the agent
        result = await generator_agent.run(query, deps=deps)
        
        # Cache the schema if first time
        if cache[type] is None and hasattr(result.output, 'schema'):
            cache[type] = result.output.schema
        
        print(f"Generated LaTeX for {type}:")
        print("=" * 50)
        print(result.output.latex)
        print("=" * 50)
        
        return result.output.latex
        
    except Exception as e:
        print(f"Error in generate_latex_content: {str(e)}")
        # Return a safe fallback
        if type == "header":
            return """
            \\begin{center}
            \\textbf{\\LARGE [Name]} \\\\
            \\textit{[Contact Information]} \\\\
            \\end{center}
            """
        else:
            return f"""
            \\section*{{{type.title()}}}
            Content generation error: {str(e)}
            """

if __name__ == "__main__":
    request = {
        "name": {"firstName": "Zhixing", "lastName": "Lu"},
        "contact": [
            {"type": "email", "value": "amylu@example.com"},
            {"type": "phone", "value": "+345660"}
        ],
    }
    template = r"""
        \begin{comment}
    In Europe it is common to include a picture of ones self in the CV. Select
    which heading appropriate for the document you are creating.
    \end{comment}

    \begin{minipage}[c]{0.05\textwidth}
    \-\
    \end{minipage}
    \begin{minipage}[c]{0.2\textwidth}
    \begin{tikzpicture}
        \clip (0,0) circle (1.75cm);
        \node at (0,-.7) {\includegraphics[width = 9cm]{portrait}}; 
        % if necessary the picture may be moved by changing the at (coordinates)
        % width defines the 'zoom' of the picture
    \end{tikzpicture}
    \hfill\vline\hfill
    \end{minipage}
    \begin{minipage}[c]{0.4\textwidth}
        \textbf{\Huge \scshape{Charles Rambo}} \\ \vspace{1pt} 
        % \scshape sets small capital letters, remove if desired
        \small{+1 123-456-7890} \\
        \href{mailto:you@provider.com}{\underline{you@provider.com}}\\
        % Be sure to use a professional *personal* email address
        \href{https://www.linkedin.com/in/charles-rambo/}{\underline{linkedin.com/in/charles-rambo}} \\
        % you should adjust you linked in profile name to be professional and recognizable
        \href{https://github.com/fizixmastr}{\underline{github.com/fizixmastr}}
    \end{minipage}
    """
    type = "header"
    current = None
    asyncio.run(generate_latex_content(request, template, type, current))