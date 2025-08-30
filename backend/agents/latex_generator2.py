"""
Latex Generator Orchestrator - FIXED VERSION

Key fixes:
1. Preserve previously rendered header when updating sections
2. Better state management to ensure incremental updates work correctly
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import os
import traceback
from .multi_agent_generator import generate_latex_content
from .header_agent import HeaderAgent
from .section_agent import SectionAgent
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class GeneratorCaches:
    preamble_cache: str = ""
    header_cache: str = ""
    sections_cache: str = ""
    footer_cache: str = ""


class LatexGenerator:
    def __init__(self, template_path: Optional[str] = None) -> None:
        self.header_agent = HeaderAgent()
        self.section_agent = SectionAgent()
        self.caches = GeneratorCaches()
        # FIXED: Keep track of rendered content separately + section ordering
        self.current_header: str = ""  # This holds the RENDERED header content
        self.current_sections: str = ""  # This holds the RENDERED sections content
        
        # FIXED: Add ordered sections management
        self.section_order = ["aboutMe", "education", "experience", "skills", "customSections"]
        self.rendered_sections: Dict[str, str] = {}  # Track individual sections
        
        self.current_latex: str = ""
        self.template_path = template_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "templates", "default_resume.tex"
        )

    def combine_sections_in_order(self) -> str:
        """FIXED: Combine sections in proper order"""
        ordered_content = []
        
        for section_name in self.section_order:
            if section_name in self.rendered_sections:
                section_content = self.rendered_sections[section_name]
                if section_content and section_content.strip():
                    ordered_content.append(section_content)
                    logger.info("Added %s section (%d chars)", section_name, len(section_content))
        
        combined_sections = "\n\n".join(ordered_content)
        logger.info("Total sections combined: %d sections, %d characters", 
                   len(ordered_content), len(combined_sections))
        return combined_sections

    def combine_parts(self):
        """Combine all parts into full LaTeX document"""
        # FIXED: Use properly ordered sections
        self.current_sections = self.combine_sections_in_order()
        
        combined = "".join([
            self.caches.preamble_cache,
            "\n",
            self.current_header,  # Use the RENDERED header, not template
            "\n", 
            self.current_sections,  # Use the ORDERED sections
            "\n",
            self.caches.footer_cache,
        ])
        logger.info("Combined LaTeX length: %d characters", len(combined))
        logger.info("Header content length: %d, Sections content length: %d", 
                   len(self.current_header), len(self.current_sections))
        return combined

    def scrape_template(self, template_path: Optional[str] = None) -> GeneratorCaches:
        path = template_path or self.template_path
        logger.info("Scraping template from %s", path)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError as e:
            logger.error("Template file not found: %s", path)
            raise ValueError(f"Template file not found: {path}") from e
        
        part1_idx = content.find("%PART 1")
        part2_idx = content.find("%PART 2")
        part3_idx = content.find("%PART 3")
        end_doc_idx = content.rfind("\\end{document}")

        if part1_idx == -1 or part2_idx == -1 or part3_idx == -1:
            logger.error("Template missing required %PART markers (1/2/3)")
            logger.error("Content preview: %s", content[:500])
            raise ValueError("Template missing required %PART markers (1/2/3)")

        logger.info("Found PART markers: 1 at %d, 2 at %d, 3 at %d", part1_idx, part2_idx, part3_idx)
        
        preamble = content[part1_idx:part2_idx].strip()
        header = content[part2_idx:part3_idx].strip()
        sections = content[part3_idx:end_doc_idx if end_doc_idx != -1 else None].strip()
        footer = "\\end{document}"

        # Store the TEMPLATE parts (not rendered content)
        self.caches.preamble_cache = preamble
        self.caches.header_cache = header
        self.caches.sections_cache = sections
        self.caches.footer_cache = footer

        # FIXED: Don't override current_latex here if we already have rendered content
        if not self.current_header and not self.current_sections:
            self.current_latex = self.combine_parts()
            
        logger.info("Template scraped successfully - preamble: %d chars, header: %d chars, sections: %d chars", 
                   len(preamble), len(header), len(sections))

        return self.caches

    async def update_header(self, data: Dict[str, Any]) -> str:
        logger.info("Starting header update with data: %s", data)
        
        if not self.caches.header_cache or not self.caches.preamble_cache:
            logger.info("Caches empty, scraping template first")
            self.scrape_template()

        try:
            # Generate RENDERED header content using the template
            rendered_header_block = await generate_latex_content(
                request = data, 
                template = self.caches.header_cache,  # Use template as base
                type = "header",
            )
            logger.info("Header rendered successfully: %d characters", len(rendered_header_block))
            
            # FIXED: Store the RENDERED content
            self.current_header = rendered_header_block

            # Combine with existing sections (if any)
            combined = self.combine_parts()
            self.current_latex = combined
            logger.info("Header update completed, total LaTeX: %d chars", len(combined))
            return combined
            
        except Exception as e:
            logger.error("Error in update_header: %s", str(e))
            logger.error("Traceback: %s", traceback.format_exc())
            raise

    async def update_sections(self, action: str, data: Dict[str, Any]) -> str:
        logger.info("Starting section update - action: %s, data: %s", action, data)
        
        # Ensure we have cached template parts
        if not self.caches.preamble_cache:
            logger.info("No preamble cache, scraping template first")
            self.scrape_template()

        try:
            section_name = data.get('section', 'unknown')
            logger.info("Updating section: %s", section_name)
            
            # FIXED: Generate individual section content
            section_latex = await generate_latex_content(
                request = data,
                template = self.caches.sections_cache,  # Use template as base
                type = "section",
                current = self.rendered_sections.get(section_name, ""),  # Pass existing section content
            )
            
            logger.info("Section rendered successfully: %d characters", len(section_latex))
            
            # FIXED: Store the individual section (maintains order)
            self.rendered_sections[section_name] = section_latex
            logger.info("Stored section '%s', total sections: %d", section_name, len(self.rendered_sections))
            
            # FIXED: Rebuild combined document with proper ordering
            combined = self.combine_parts()
            self.current_latex = combined
            logger.info("Section update completed, total LaTeX: %d chars", len(combined))
            logger.info("Header preserved: %s", "Yes" if self.current_header else "No")
            logger.info("Sections in order: %s", list(self.rendered_sections.keys()))
            return combined
            
        except Exception as e:
            logger.error("Error in update_sections: %s", str(e))
            logger.error("Traceback: %s", traceback.format_exc())
            raise

    async def handle_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Handling request: %s", req)
        
        try:
            req_type = req.get("type")  # "header" | "section" | "scrape"
            action = req.get("action")
            data = req.get("data", {})

            logger.info("Request type: %s, action: %s, data keys: %s", 
                       req_type, action, list(data.keys()) if isinstance(data, dict) else type(data))

            if req_type == "scrape":
                logger.info("Processing scrape request")
                self.scrape_template()
                return {"success": True, "message": "Template scraped and cached."}

            if req_type == "header":
                logger.info("Processing header request")
                latex = await self.update_header(data)
                return {"success": True, "latexCode": latex}

            if req_type == "section":
                logger.info("Processing section request")
                latex = await self.update_sections(action, data)
                return {"success": True, "latexCode": latex}

            logger.warning("Unknown request type: %s", req_type)
            return {"success": False, "error": f"Unknown request type: {req_type}"}
            
        except Exception as e:
            logger.error("Error in handle_request: %s", str(e))
            logger.error("Traceback: %s", traceback.format_exc())
            return {"success": False, "error": f"Request handling failed: {str(e)}"}


# Convenience factory
generator_singleton = LatexGenerator()

async def test_generator():
    request = {
        "type": "section",
        "action": "update",
        "data":{
            "section": "About Me",
            "entry": "I am a software engineer with 5 years of experience.",
        }
    }
    
    result = await generator_singleton.handle_request(request)
    
    print("Generated Content:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_generator())