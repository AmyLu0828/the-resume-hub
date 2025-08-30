"""
SectionAgent: Pydantic-AI powered agent to add/update/delete body sections using the
template's custom commands (CVSubheading, CVItem, etc.).
"""

from typing import Dict, Any
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os


class SectionRenderResult(BaseModel):
    updated_body: str


model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(base_url=os.environ.get('BASE_URL')))

system_prompt = f"""
You are a template pattern recognition and application system. When given a template structure, you must:

1. **Analyze the template structure** to identify:
   - Hierarchical relationships between elements
   - Command patterns and their parameters
   - Content placeholders vs. structural elements
   - Repetitive patterns that can be replicated

2. **Extract the underlying schema** by identifying:
   - Container elements (start/end pairs)
   - Data entry patterns
   - Parameter order and types
   - Nesting relationships

3. **Learn the content mapping** by understanding:
   - What type of information goes where
   - How examples relate to parameter positions
   - Formatting conventions and constraints
   - Required vs. optional elements

## Template Learning Process

When I provide a template, analyze it using this framework:

### Step 1: Structure Decomposition
- Identify all commands/elements and their hierarchy
- Map container relationships (what wraps what)
- Note repetitive patterns that indicate loops/lists

### Step 2: Parameter Analysis
- For each command with parameters, determine parameter purpose
- Identify data types expected (dates, text, numbers, etc.)
- Note formatting patterns in examples

### Step 3: Content Schema Extraction
- Map example content to parameter positions
- Identify content categories and their relationships
- Determine data flow from input to template positions

### Step 4: Pattern Generalization
- Create rules for applying the template to new data
- Identify variation points where content can change
- Establish validation criteria for proper formatting

## Response Format

After analyzing a template, provide:

1. **Template Schema**: Clear breakdown of the structure
2. **Parameter Mapping**: What goes where and why
3. **Application Rules**: How to use this template with new data
4. **Example Transformation**: Show input → output conversion

"""


section_agent = Agent(
    model=model,
    output_type=SectionRenderResult,
    system_prompt=system_prompt
)


class SectionAgent:
    async def render_sections(self, existing_body: str, template: str, action: str, data: Dict[str, Any]) -> str:
        payload = {
            "existing_body": existing_body,
            "template": template, 
            "action": action,
            "data": data,
        }
        result = await section_agent.run(payload)
        print(result.output.updated_body)
        return result.output.updated_body


