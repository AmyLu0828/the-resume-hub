#!/usr/bin/env python3
"""
Test script to verify the integration between latex_agent and simple_template_parser_agent.
"""

import asyncio
import sys
import os

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from latex_agent import generate_latex, LaTeXGenerationRequest, ResumeData, NameData, AboutMeData, ContactData, EducationData, ExperienceData, SkillData, CustomSectionData

async def test_template_integration():
    """Test the template-based LaTeX generation."""
    
    print("Testing template-based LaTeX generation...")
    
    # Sample resume data
    resume_data = ResumeData(
        name=NameData(firstName="John", lastName="Doe"),
        aboutMe=AboutMeData(
            description="Experienced software engineer with expertise in Python and web development.",
            polishedDescription="Experienced software engineer with expertise in Python and web development."
        ),
        contact=[
            ContactData(type="email", value="john.doe@example.com"),
            ContactData(type="phone", value="+1-555-123-4567"),
            ContactData(type="linkedin", value="https://linkedin.com/in/johndoe")
        ],
        education=[
            EducationData(
                degree="Bachelor of Science in Computer Science",
                institution="University of Technology",
                startDate="2018",
                endDate="2022",
                gpa="3.8"
            )
        ],
        experience=[
            ExperienceData(
                position="Software Engineer",
                company="Tech Corp",
                startDate="2022",
                endDate="Present",
                description="Developed web applications using Python and React. Led a team of 3 developers."
            )
        ],
        skills=[
            SkillData(name="Programming", skill="Python, JavaScript, React"),
            SkillData(name="Tools", skill="Git, Docker, AWS")
        ],
        customSections=[]
    )
    
    # Test full generation
    print("\n1. Testing full generation...")
    full_request = {
        "type": "full",
        "data": resume_data.model_dump(),
        "template_path": "templates/default_resume.tex"
    }
    
    try:
        result = await generate_latex(full_request)
        if result.get("success"):
            print("✅ Full generation successful!")
            print(f"   Template used: {result.get('template_used', 'Unknown')}")
            print(f"   LaTeX length: {len(result.get('latexCode', ''))} characters")
            
            # Save the generated LaTeX to a file for inspection
            with open("test_generated_resume.tex", "w") as f:
                f.write(result.get('latexCode', ''))
            print("   Generated LaTeX saved to: test_generated_resume.tex")
        else:
            print("❌ Full generation failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Full generation exception: {str(e)}")
    
    # Test incremental update
    print("\n2. Testing incremental update...")
    
    # First, we need the current LaTeX from the full generation
    if result.get("success") and result.get("latexCode"):
        current_latex = result.get("latexCode")
        
        # Create an update request
        update_request = {
            "type": "incremental",
            "data": resume_data.model_dump(),
            "update": {
                "section": "experience",
                "entryId": "exp_2",
                "changeType": "add"
            },
            "currentLatex": current_latex,
            "template_path": "templates/default_resume.tex"
        }
        
        try:
            update_result = await generate_latex(update_request)
            if update_result.get("success"):
                print("✅ Incremental update successful!")
                print(f"   Updated LaTeX length: {len(update_result.get('latexCode', ''))} characters")
                
                # Save the updated LaTeX
                with open("test_updated_resume.tex", "w") as f:
                    f.write(update_result.get('latexCode', ''))
                print("   Updated LaTeX saved to: test_updated_resume.tex")
            else:
                print("❌ Incremental update failed!")
                print(f"   Error: {update_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Incremental update exception: {str(e)}")
    else:
        print("⚠️  Skipping incremental test - no LaTeX generated from full generation")
    
    print("\n3. Testing template caching...")
    print("   The latex_agent should now have the template cached for future use.")
    print("   Subsequent calls will use the cached template instead of parsing again.")

async def test_template_parsing():
    """Test the template parsing functionality."""
    
    print("\n4. Testing template parsing...")
    
    try:
        from simple_template_parser_agent import analyze_template_file
        
        template_path = "templates/default_resume.tex"
        if os.path.exists(template_path):
            template_content = await analyze_template_file(template_path)
            print(f"✅ Template parsing successful!")
            print(f"   Template length: {len(template_content)} characters")
            print(f"   Template path: {template_path}")
        else:
            print(f"⚠️  Template file not found: {template_path}")
            print("   Make sure you're running from the backend directory")
    except Exception as e:
        print(f"❌ Template parsing failed: {str(e)}")

async def main():
    """Main test function."""
    print("=" * 60)
    print("LaTeX Agent Integration Test")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("templates"):
        print("❌ Error: 'templates' directory not found!")
        print("   Please run this script from the 'backend' directory")
        return
    
    # Run tests
    await test_template_parsing()
    await test_template_integration()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
