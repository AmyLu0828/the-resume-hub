import asyncio
import httpx
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"  # Update if your server runs on a different URL/port
ENDPOINT = f"{BASE_URL}/api/compile-latex/"
TEST_LATEX = "\n\\documentclass[11pt,a4paper]{article}\n\\usepackage[left=0.75in,top=0.6in,right=0.75in,bottom=0.6in]{geometry}\n\\usepackage{enumitem}\n\\usepackage{hyperref}\n\\usepackage{titlesec}\n\\usepackage{xcolor}\n\\usepackage{url}\n\n% Custom formatting\n\\titleformat{\\section}{\\large\\bfseries\\uppercase}{}{0em}{}[\\titlerule]\n\\titlespacing{\\section}{0pt}{12pt}{6pt}\n\n\\pagestyle{empty}\n\\setlength{\\tabcolsep}{0in}\n\n% Custom colors\n\\definecolor{primary}{RGB}{0, 102, 204}\n\n\\hypersetup{\n    colorlinks=true,\n    linkcolor=primary,\n    urlcolor=primary,\n    citecolor=primary\n}\n\n\\begin{document}\n\n\\section{Summary}\nhi\n\n\n\\end{document}\n"

async def test_compile_latex():
    async with httpx.AsyncClient() as client:
        print(f"Testing LaTeX compilation endpoint: {ENDPOINT}")

        # Test 1: Successful compilation
        print("\n=== Test 1: Successful compilation ===")
        try:
            response = await client.post(
                ENDPOINT,
                json={"latexCode": TEST_LATEX},
                timeout=30.0
            )
            
            print(f"Status code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Disposition: {response.headers.get('content-disposition')}")
            print(f"Response length: {len(response.content)} bytes")
            
            assert response.status_code == 200
            assert response.headers.get("content-type") == "application/pdf"
            assert "inline; filename=resume.pdf" in response.headers.get("content-disposition", "")
            assert len(response.content) > 1000  # Ensure reasonable PDF size
            
            # Save the PDF for manual inspection
            os.makedirs("test_outputs", exist_ok=True)
            pdf_path = Path("test_outputs") / "test_output.pdf"
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            print(f"✓ Success! PDF saved to {pdf_path}")
            
        except Exception as e:
            print(f"✗ Test 1 failed: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(test_compile_latex())