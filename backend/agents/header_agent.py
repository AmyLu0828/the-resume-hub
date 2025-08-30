"""
HeaderAgent: Pydantic-AI powered agent to render the header block using user data.

Inputs:
- header_template_block (from PART 2 of template)
- user data (name, contacts)

Output:
- rendered header LaTeX block
"""

from typing import Dict, Any
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os


class HeaderRenderResult(BaseModel):
    rendered: str


model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(base_url=os.environ.get('BASE_URL')))

system_prompt = """
You are a LaTeX header rendering agent. Your task is to take a LaTeX header block template and user data, and render the header with the provided user information.
You are given:
1) The exact header minipage/tikz block from the template which includes example name and contacts
2) User data (name, contacts)

Task:
- Replace the shown example values in the header block with user data while preserving ALL formatting and LaTeX commands
- DO NOT keep any custom data from the header template
- Keep the structure (minipages, tikz, href formats) identical
- Do not invent new commands; only replace textual values (name, phone, email, links)
- Return JSON: {"rendered": "<header block>"}
"""


header_agent = Agent(
    model=model,
    output_type=HeaderRenderResult,
    system_prompt=system_prompt
)


class HeaderAgent:
    async def render_header(self, header_template_block: str, data: Dict[str, Any]) -> str:
        prompt = f"""
        Here is the header template block:
        ```
        {header_template_block}
        ```
        And here is the user data:
        ```
        {data}
        ```
        Your task is to render the header block using the provided user data.
        """

        result = await header_agent.run(prompt)
        return result.output.rendered


