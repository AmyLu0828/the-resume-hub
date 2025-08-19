"""
Improvement Agent for Resume Builder
Uses Pydantic AI to enhance and polish resume content for better impact and clarity.
Processes individual update messages from the frontend in real-time.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Dict, Any, Optional, Union, Literal
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import json
import os
from dotenv import load_dotenv

load_dotenv()

model = OpenAIModel('gpt-4o-mini', provider=OpenAIProvider(base_url=os.environ.get('BASE_URL')))

# Define the update message structure from frontend
class UpdateMessage(BaseModel):
    section: str
    entryId: str
    changeType: Literal["add", "update", "delete"]
    content: Dict[str, Any]

# Define content models for different sections
class NameContent(BaseModel):
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""

class AboutMeContent(BaseModel):
    description: Optional[str] = ""

class ContactContent(BaseModel):
    id: Optional[str] = ""
    type: Optional[str] = ""  # Email, Phone, LinkedIn, etc.
    value: Optional[str] = ""

class EducationContent(BaseModel):
    id: Optional[str] = ""
    degree: Optional[str] = ""
    institution: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    description: Optional[str] = ""

class ExperienceContent(BaseModel):
    id: Optional[str] = ""
    title: Optional[str] = ""
    company: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    description: Optional[str] = ""
    keywords: Optional[List[str]] = Field(default_factory=list)

class SkillContent(BaseModel):
    id: Optional[str] = ""
    skill: Optional[str] = ""

class CustomSectionContent(BaseModel):
    id: Optional[str] = ""
    title: Optional[str] = ""
    content: Optional[str] = ""

# Result type that matches input structure exactly
class ImprovedUpdateMessage(BaseModel):
    """Result type for improved update messages - matches input structure exactly"""
    section: str
    entryId: str
    changeType: Literal["add", "update", "delete"]
    content: Dict[str, Any]

system_prompt = """
You are an expert resume improvement AI assistant. Your job is to enhance resume content to make it more professional, impactful, and compelling while maintaining accuracy and authenticity.

**Your Goals:**
1. **Polish descriptions** - Make experiences and accomplishments stand out with powerful, action-oriented language
2. **Improve clarity and coherency** - Ensure all content flows well and is easy to understand
3. **Highlight key words** - Incorporate relevant industry keywords and skills naturally
4. **Remove unnecessary information** - Keep content concise and focused on value-add information
5. **Correct grammar and style** - Fix any grammatical errors and improve professional tone

**Guidelines:**
- Use strong action verbs (achieved, developed, implemented, led, optimized, etc.)
- Focus on what the user did rather than what they learned
- Keep language professional yet engaging
- Maintain the original meaning and truthfulness of all content
- Ensure consistency in tense and format across similar sections
- Make descriptions specific and concrete rather than vague
- Prioritize the most impressive and relevant information

**IMPORTANT:** 
- Only improve the text content, never change IDs, dates, or structural information
- If content is already well-written, make minimal changes
- Preserve all original keys and structure exactly
- Do not hallucinate data: leave unknown fields with placeholder values if the user's content is not complete
- Do not be overly artificial: avoid excessive buzzwords or unnatural phrases

Return ONLY a single JSON object (no code fences, no prose) with EXACTLY these keys:
{
  "section": "<same as input>",
  "entryId": "<same as input>",
  "changeType": "<same as input>",
  "content": { ...same keys as input.content, improved text... }
}
"""

# Create the improvement agent with proper output type
improvement_agent = Agent(
    model=model,
    output_type=ImprovedUpdateMessage,
    system_prompt=system_prompt
)

class ImprovementAgent:
    """
    Main improvement agent class that processes individual update messages from frontend.
    """
    
    def __init__(self):
        self.agent = improvement_agent
    
    async def improve_update_message(self, update_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Improve content from a single update message.
        
        Args:
            update_message: Dictionary with format:
                {
                    "section": "experience",
                    "entryId": "exp_123", 
                    "changeType": "update",
                    "content": { "title": "...", "description": "...", ... }
                }
                
        Returns:
            Dictionary with same structure but improved content
        """
        try:
            # Validate the update message structure
            update = UpdateMessage.model_validate(update_message)
            
            # Skip improvement for delete operations or empty content
            if update.changeType == "delete" or not update.content:
                return update_message
            
            # Skip if content only has structural fields (id, dates) without text to improve
            text_fields = self._get_text_fields(update.content)
            if not text_fields:
                return update_message
            
            # Create section-specific improvement prompts
            section_context = self._get_section_context(update.section)
            content_json = json.dumps(update.content, indent=2)
            
            prompt = f"""
            {section_context}
            
            Please improve the following content for a resume {update.section} section:
            
            {content_json}
            
            Focus on enhancing text fields like descriptions, titles, and other narrative content.
            Keep all IDs, dates, and structural information exactly the same.
            If the content is already professional, make only minor improvements.
            """
            
            # Get improved content from the agent
            result = await self.agent.run(prompt)
            
            result_json = {
                "section": update.section,
                "entryId": update.entryId,
                "changeType": update.changeType,
                "content": result.output
            }
            #print(result_json)
            # Return the improved update message as a dictionary
            return result_json
            
        except Exception as e:
            print(f"Error improving update message: {e}")
            # Return original update message if improvement fails
            return update_message

    def _get_text_fields(self, content: Dict[str, Any]) -> List[str]:
        """Identify text fields that can be improved."""
        text_fields = []
        for key, value in content.items():
            if isinstance(value, str) and value.strip() and key not in ['id', 'startDate', 'endDate']:
                text_fields.append(key)
        return text_fields

    def _get_section_context(self, section: str) -> str:
        """Get section-specific context for better improvements."""
        contexts = {
            "experience": """
            This is work experience content. Focus on:
            - Starting descriptions with strong action verbs
            - Highlighting achievements and quantifiable results
            - Using professional terminology if the user's content is too casual, but keep it natural
            - Making accomplishments stand out
            - Keeping job titles professional and clear
            """,
            "education": """
            This is education content. Focus on:
            - Highlighting relevant coursework or projects
            - Including academic achievements or honors
            - Making descriptions concise and relevant
            - Emphasizing skills gained or knowledge acquired
            - Keeping degree and institution names accurate
            """,
            "aboutMe": """
            This is an "About Me" section. Focus on:
            - Creating a compelling professional summary
            - Highlighting unique value propositions
            - Keeping it concise but impactful (2-4 sentences)
            - Focusing on career highlights and professional strengths
            """,
            "skills": """
            This is a skills section. Focus on:
            - Using industry-standard terminology
            - Prioritizing most relevant and advanced skills
            - Ensuring professional presentation
            - Keeping skill names clear and recognizable
            """,
            "contact": """
            This is contact information. Focus on:
            - Ensuring professional formatting
            - Using standard labels (Email, Phone, LinkedIn, etc.)
            - Maintaining clarity and accuracy
            """,
            "customSections": """
            This is a custom resume section. Focus on:
            - Making the title clear and professional
            - Enhancing content for maximum impact
            - Ensuring relevance to career goals
            """,
            "name": """
            This is name information. Focus on:
            - Ensuring proper capitalization
            - Maintaining professional presentation
            """
        }
        return contexts.get(section, "This is resume content that should be professional and impactful.")

# Create a global instance
improvement_agent_instance = ImprovementAgent()

# Convenience function for easy import and use
async def improve_update(update_message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to improve an individual update message.
    
    Args:
        update_message: Frontend update message in format:
            {
                "section": "experience",
                "entryId": "exp_123",
                "changeType": "update", 
                "content": { ... }
            }
    
    Returns:
        Improved update message with same structure
    """
    return await improvement_agent_instance.improve_update_message(update_message)

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Example update messages for testing
    test_updates = [
        # {
        #     "section": "experience",
        #     "entryId": "exp_123",
        #     "changeType": "update",
        #     "content": {
        #         "id": "exp_123",
        #         "title": "Software Developer",
        #         "company": "Tech Company",
        #         "startDate": "2022-06-01",
        #         "endDate": "2024-01-01",
        #         "description": "Worked on web applications using JavaScript and Python. Fixed bugs and added features.",
        #         "keywords": ["JavaScript", "Python", "web development"]
        #     }
        # },
        {
            "section": "aboutMe", 
            "entryId": "single",
            "changeType": "update",
            "content": {
                "description": "I am a software developer with experience in web development."
            }
        },
        # {
        #     "section": "education",
        #     "entryId": "edu_456",
        #     "changeType": "add",
        #     "content": {
        #         "id": "edu_456",
        #         "degree": "Bachelor of Science in Computer Science",
        #         "institution": "State University", 
        #         "startDate": "2018-09-01",
        #         "endDate": "2022-05-01",
        #         "description": "Studied computer science and programming."
        #     }
        # }
    ]
    
    async def test_improvements():
        print("Testing improvement agent with individual update messages:\n")
        
        for i, update in enumerate(test_updates):
            print(f"=== Test {i+1}: {update['section']} {update['changeType']} ===")
            print("Original update:")
            print(json.dumps(update, indent=2))
            
            try:
                improved = await improve_update(update)
                
                print("\nImproved update:")
                print(improved)
            except Exception as e:
                print(f"\nError during improvement: {e}")
                print("Returned original update message")
            
            print("\n" + "-"*60 + "\n")
    
    # Uncomment to test
    #asyncio.run(test_improvements())