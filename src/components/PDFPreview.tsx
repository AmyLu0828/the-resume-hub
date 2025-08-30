//PDFPreview.tsx - FIXED VERSION
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ResumeData } from '@/types/resume';
import { FileText, Eye, RefreshCw, Code, CheckCircle } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

interface PDFPreviewProps {
  data: ResumeData;
  // FIXED: Change to explicit trigger instead of auto-detection
  onSubmitUpdate?: {
    section: string;
    entryId: string;
    changeType: string;
    timestamp: number;
  } | null;
}

export function PDFPreview({ data, onSubmitUpdate }: PDFPreviewProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [latexCode, setLatexCode] = useState<string>('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLatex, setShowLatex] = useState(true);
  const [compileStats, setCompileStats] = useState({ updates: 0, lastDuration: 0 });
  const [hasGeneratedPreview, setHasGeneratedPreview] = useState(false);
  const [isTemplateScraped, setIsTemplateScraped] = useState(false);
  const [isScrapingTemplate, setIsScrapingTemplate] = useState(false);

  const isInitializedRef = useRef(false);

  // FIXED: Remove automatic change detection - only use explicit triggers
  const scrapeTemplate = async () => {
    if (isTemplateScraped) return;

    try {
      console.log("Scraping template...");
      setIsScrapingTemplate(true);
      const response = await fetch('/api/template/scrape', { method: 'POST' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      if (result.success) {
        setIsTemplateScraped(true);
        console.log("Template scraped successfully");
      } else {
        throw new Error(result.error || 'Template scraping failed');
      }
    } catch (err) {
      console.error('Error scraping template:', err);
      setError(err instanceof Error ? err.message : 'Failed to scrape template');
    } finally {
      setIsScrapingTemplate(false);
    }
  };

  const initializeLatex = async () => {
    if (!hasData(data) || !isTemplateScraped) {
      console.log("No data or template not scraped");
      return;
    }

    console.log("Starting header initialization...");
    setIsUpdating(true);
    setError(null);

    try {
      await scrapeTemplate();

      const headerPayload = {
        type: 'header',
        action: 'update',
        data: {
          name: data.name,
          contact: data.contact,
        },
      };

      const response = await fetch('/api/latex-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(headerPayload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log("Header update result:", result);

      if (result.success && result.latexCode) {
        setLatexCode(result.latexCode);
        isInitializedRef.current = true;
        setHasGeneratedPreview(true);
        console.log("Header initialization completed successfully");
      } else {
        throw new Error(result.error || 'No LaTeX code returned from header update');
      }
    } catch (err) {
      console.error('Error initializing header:', err);
      setError(err instanceof Error ? err.message : 'Failed to initialize header');
    } finally {
      setIsUpdating(false);
    }
  };

  const updateLatexSection = async (updateInfo: any) => {
    if (!isTemplateScraped) {
      console.log("Template not scraped, scraping first...");
      await scrapeTemplate();
    }

    if (!isInitializedRef.current) {
      console.log("Not initialized, falling back to header initialization");
      await initializeLatex();
      return;
    }

    console.log("Starting section update...");
    console.log("Update info received:", JSON.stringify(updateInfo, null, 2));
    
    setIsUpdating(true);
    setError(null);
    const startTime = performance.now();

    try {
      let sectionData;
      const sectionName = updateInfo.section;
      
      console.log("Section name:", sectionName);
      console.log("Current data keys:", Object.keys(data));
      
      switch (sectionName) {
        case 'aboutMe':
          sectionData = data.aboutMe;
          break;
        case 'education':
          sectionData = data.education;
          break;
        case 'experience':
          sectionData = data.experience;
          break;
        case 'skills':
          sectionData = data.skills;
          break;
        case 'customSections':
          sectionData = data.customSections;
          break;
        default:
          console.warn("Unknown section:", sectionName);
          sectionData = null;
      }
      
      console.log("Section data extracted:", JSON.stringify(sectionData, null, 2));

      const sectionPayload = {
        type: 'section',
        action: updateInfo.changeType,
        data: {
          section: updateInfo.section,
          entry: sectionData,
        },
      };

      console.log("Payload being sent:", JSON.stringify(sectionPayload, null, 2));

      const response = await fetch('/api/latex-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sectionPayload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Backend error response:", errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log("Backend response:", result);

      if (result.success && result.latexCode) {
        setLatexCode(result.latexCode);

        const duration = performance.now() - startTime;
        setCompileStats(prev => ({
          updates: prev.updates + 1,
          lastDuration: Math.round(duration)
        }));
        console.log("Section update completed successfully");
      } else {
        throw new Error(result.error || 'No LaTeX code returned from section update');
      }
    } catch (err) {
      console.error('Error updating section:', err);
      console.log("Falling back to header regeneration...");
      await initializeLatex();
    } finally {
      setIsUpdating(false);
    }
  };

  // FIXED: Only process explicit submit triggers, not data changes
  useEffect(() => {
    if (!onSubmitUpdate) {
      return;
    }

    console.log("Processing explicit submit update:", onSubmitUpdate);
    
    if (onSubmitUpdate.section === 'header') {
      initializeLatex();
    } else {
      updateLatexSection(onSubmitUpdate);
    }
    
  }, [onSubmitUpdate]); // FIXED: Only depend on explicit submit triggers

  // FIXED: Add method to manually trigger updates (call this from parent on submit)
  const handleManualUpdate = async (section: string, changeType: string = 'update') => {
    console.log(`Manual update triggered for section: ${section}`);
    
    const updateInfo = {
      section,
      entryId: 'current',
      changeType,
      timestamp: Date.now()
    };

    if (section === 'header') {
      await initializeLatex();
    } else {
      await updateLatexSection(updateInfo);
    }
  };

  // Rest of your existing helper functions...
  const hasData = (resumeData: ResumeData) => {
    return (
      resumeData.name.firstName ||
      resumeData.name.lastName ||
      resumeData.aboutMe.description ||
      resumeData.contact.length > 0 ||
      resumeData.education.length > 0 ||
      resumeData.experience.length > 0 ||
      resumeData.skills.length > 0 ||
      resumeData.customSections.length > 0
    );
  };

  const copyLatexCode = () => {
    if (latexCode) {
      navigator.clipboard.writeText(latexCode);
    }
  };

  const generatePdf = async () => {
    try {
      setIsUpdating(true);
      const response = await fetch('/api/generate-final-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Failed to generate PDF: ${text}`);
      }
      const blob = await response.blob();
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
      setShowLatex(false);
      setHasGeneratedPreview(true);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setIsUpdating(false);
    }
  };

  useEffect(() => {
    return () => {
      if (pdfUrl) {
        console.log("Cleaning up PDF URL on component unmount");
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

  return (
    <div className="h-full flex flex-col">
      {/* Header with controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Eye className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Resume Preview</h3>
          {compileStats.updates > 0 && hasGeneratedPreview && (
            <div className="text-xs text-gray-500 flex gap-2">
              <span>{compileStats.updates} updates</span>
              <span>({compileStats.lastDuration}ms)</span>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            variant={isTemplateScraped ? "default" : "outline"}
            size="sm"
            onClick={scrapeTemplate}
            disabled={isScrapingTemplate || isTemplateScraped}
            className="transition-all"
          >
            {isScrapingTemplate ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Scraping...
              </>
            ) : isTemplateScraped ? (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Template Scraped
              </>
            ) : (
              'Scrape Template'
            )}
          </Button>

          <Button
            variant={showLatex ? "default" : "outline"}
            size="sm"
            onClick={() => setShowLatex(true)}
            className="transition-all"
          >
            <Code className="h-4 w-4 mr-2" />
            Show LaTeX
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={generatePdf}
            disabled={isUpdating || !hasData(data)}
            className="transition-all hover:bg-primary hover:text-primary-foreground"
          >
            {isUpdating ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Generating PDF...
              </>
            ) : (
              'Generate PDF'
            )}
          </Button>
        </div>
      </div>

      {/* Preview area - Your existing JSX */}
      <Card className="flex-1 overflow-hidden bg-white shadow-lg">
        {error ? (
          <div className="h-full flex items-center justify-center text-center p-8">
            <div className="text-red-600 max-w-md">
              <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium mb-2">Generation Error</p>
              <p className="text-sm text-gray-600 mb-4 whitespace-pre-wrap">{error}</p>
              <Button onClick={initializeLatex} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </div>
        ) : !hasData(data) ? (
          <div className="h-full flex items-center justify-center text-center p-8">
            <div className="text-gray-500">
              <FileText className="h-16 w-16 mx-auto mb-4 opacity-30" />
              <h3 className="text-xl font-medium mb-2">Your Resume Preview</h3>
              <p className="text-gray-400">
                Start filling out your information to see a live LaTeX preview
              </p>
            </div>
          </div>
        ) : isUpdating ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <RefreshCw className="h-12 w-12 mx-auto mb-4 animate-spin text-primary" />
              <p className="text-lg text-gray-600">
                {isInitializedRef.current ? 'Updating LaTeX...' : 'Generating LaTeX...'}
              </p>
              <p className="text-sm text-gray-400 mt-1">
                {isInitializedRef.current ? 'Section update in progress' : 'Header initialization'}
              </p>
            </div>
          </div>
        ) : !hasGeneratedPreview ? (
          <div className="h-full flex items-center justify-center text-center p-8">
            <div className="text-gray-500">
              <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">Waiting for content</p>
              <p className="text-sm text-gray-400 mb-4">
                Submit or add content in any section to generate LaTeX
              </p>
            </div>
          </div>
        ) : showLatex && latexCode ? (
          <div className="h-full flex flex-col p-4">
            <div className="flex justify-between items-center mb-2">
              <h4 className="font-medium">LaTeX Source Code</h4>
              <Button size="sm" variant="outline" onClick={copyLatexCode}>
                Copy Code
              </Button>
            </div>
            <div className="flex-1 overflow-auto bg-gray-50 rounded border">
              <pre className="text-xs p-4 whitespace-pre-wrap font-mono">
                <code>{latexCode}</code>
              </pre>
            </div>
          </div>
        ) : pdfUrl ? (
          <div className="h-full relative">
            <iframe
              src={pdfUrl}
              className="w-full h-full border-0"
              title="Resume PDF Preview"
              onLoad={() => console.log("PDF iframe loaded successfully")}
              onError={(e) => {
                console.error("PDF iframe load error:", e);
                setError("Failed to load PDF in preview");
              }}
            />
            {isUpdating && (
              <div className="absolute top-2 right-2 bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs flex items-center">
                <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                Updating...
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-center p-8">
            <div className="text-gray-500">
              <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <div className="text-lg mb-2">Processing...</div>
              <div className="text-sm text-gray-400 mb-4">
                Your resume preview is being prepared
              </div>
              <Button onClick={initializeLatex} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Regenerate
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

// FIXED: Updated parent component integration example
/*
// In your parent component (wherever PDFPreview is used):

const [submitTrigger, setSubmitTrigger] = useState(null);

// When "Submit Header" button is clicked:
const handleSubmitHeader = () => {
  setSubmitTrigger({
    section: 'header',
    entryId: 'current',
    changeType: 'update',
    timestamp: Date.now()
  });
};

// When "Submit About Me" button is clicked:
const handleSubmitAboutMe = () => {
  setSubmitTrigger({
    section: 'aboutMe',
    entryId: 'current',
    changeType: 'update',
    timestamp: Date.now()
  });
};

// Usage:
<PDFPreview data={resumeData} onSubmitUpdate={submitTrigger} />
*/