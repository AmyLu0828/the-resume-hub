import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ResumeData } from '@/types/resume';
import { FileText, Eye, RefreshCw, Code } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

interface PDFPreviewProps {
  data: ResumeData;
  lastUpdate?: {
    section: string;
    entryId: string;
    changeType: string;
    timestamp: number;
  } | null;
}

export function PDFPreview({ data, lastUpdate }: PDFPreviewProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [latexCode, setLatexCode] = useState<string>('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Show LaTeX by default per requirements
  const [showLatex, setShowLatex] = useState(true);
  const [compileStats, setCompileStats] = useState({ updates: 0, lastDuration: 0 });
  const [hasGeneratedPreview, setHasGeneratedPreview] = useState(false);

  // Track LaTeX sections for incremental updates
  const latexSectionsRef = useRef<Map<string, string>>(new Map());
  const isInitializedRef = useRef(false);

  // Initialize with full LaTeX generation
  const initializeLatex = async () => {
    if (!hasData(data)) {
      console.log("No data available for LaTeX generation");
      return;
    }

    console.log("Starting full LaTeX initialization...");
    setIsUpdating(true);
    setError(null);

    try {
      const response = await fetch('/api/generate-latex', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'full',
          data: data
        }),
      });

      console.log("LaTeX generation response:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("LaTeX generation failed:", errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log("LaTeX generation result:", { success: result.success, hasLatexCode: !!result.latexCode });

      if (result.success && result.latexCode) {
        setLatexCode(result.latexCode);

        // Store section mappings for future incremental updates
        if (result.sections) {
          latexSectionsRef.current = new Map(Object.entries(result.sections));
        }

        isInitializedRef.current = true;
        setHasGeneratedPreview(true);
        console.log("LaTeX initialization completed successfully");
      } else {
        throw new Error(result.error || 'No LaTeX code returned from server');
      }
    } catch (err) {
      console.error('Error initializing LaTeX:', err);
      setError(err instanceof Error ? err.message : 'Failed to initialize LaTeX');
    } finally {
      setIsUpdating(false);
    }
  };

  // Incremental LaTeX update
  const updateLatexIncremental = async (updateInfo: any) => {
    if (!isInitializedRef.current) {
      console.log("Not initialized, falling back to full generation");
      await initializeLatex();
      return;
    }

    console.log("Starting incremental LaTeX update...");
    setIsUpdating(true);
    setError(null);
    const startTime = performance.now();

    try {
      const response = await fetch('/api/generate-latex', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'incremental',
          update: updateInfo,
          currentLatex: latexCode,
          data: data
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Incremental update failed:", errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();

      if (result.success && result.latexCode) {
        setLatexCode(result.latexCode);

        // Update section mappings
        if (result.updatedSections) {
          Object.entries(result.updatedSections).forEach(([key, value]) => {
            latexSectionsRef.current.set(key, value as string);
          });
        }

        const duration = performance.now() - startTime;
        setCompileStats(prev => ({
          updates: prev.updates + 1,
          lastDuration: Math.round(duration)
        }));
        console.log("Incremental update completed successfully");
      } else {
        throw new Error(result.error || 'No LaTeX code returned from incremental update');
      }
    } catch (err) {
      console.error('Error updating LaTeX incrementally:', err);
      console.log("Falling back to full regeneration...");
      // Fallback to full regeneration
      await initializeLatex();
    } finally {
      setIsUpdating(false);
    }
  };

  // Compile LaTeX to PDF with improved error handling
  const compileToPdf = async (latex: string) => {
    if (!latex || latex.trim().length === 0) {
      console.error("No LaTeX code provided for compilation");
      setError("No LaTeX code available for compilation");
      return;
    }

    try {
      console.log("=== PDF COMPILATION STARTED ===");
      console.log("LATEX CODE LENGTH:", latex.length, "characters");

      const requestBody = { latexCode: latex };
      const startTime = Date.now();

      const response = await fetch('/api/compile-latex', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const responseTime = Date.now() - startTime;
      console.log("RESPONSE TIME:", responseTime, "ms");
      console.log("RESPONSE STATUS:", response.status, response.statusText);

      if (!response.ok) {
        let errorDetail = 'Unknown error';
        const contentType = response.headers.get('content-type');

        try {
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            errorDetail = errorData.message || errorData.error || JSON.stringify(errorData);
            console.error("ERROR RESPONSE (JSON):", errorData);
          } else {
            const errorText = await response.text();
            errorDetail = errorText.substring(0, 500);
            console.error("ERROR RESPONSE (TEXT):", errorText);
          }
        } catch (parseError) {
          console.error("Could not parse error response:", parseError);
        }

        throw new Error(`PDF compilation failed (${response.status}): ${errorDetail}`);
      }

      // Check if response is actually a PDF
      const contentType = response.headers.get('content-type');
      console.log("RESPONSE CONTENT-TYPE:", contentType);

      if (!contentType || !contentType.includes('application/pdf')) {
        console.warn("⚠️ Unexpected content type. Expected PDF, got:", contentType);
        // Still try to process as blob, but log warning
      }

      const blob = await response.blob();
      console.log("BLOB TYPE:", blob.type);
      console.log("BLOB SIZE:", blob.size, "bytes");

      if (blob.size === 0) {
        throw new Error("Received empty PDF blob");
      }

      // Additional PDF validation
      if (blob.type === 'application/pdf' || blob.type === 'application/octet-stream') {
        console.log("✓ Valid PDF blob received");
      } else {
        console.warn("⚠️ Unexpected blob type:", blob.type);
      }

      // Clean up previous URL
      if (pdfUrl) {
        console.log("Cleaning up previous PDF URL");
        URL.revokeObjectURL(pdfUrl);
      }

      const url = URL.createObjectURL(blob);
      console.log("Created object URL for PDF");
      setPdfUrl(url);
      setError(null); // Clear any previous errors

      console.log("=== PDF COMPILATION COMPLETED SUCCESSFULLY ===");

    } catch (err) {
      console.error('=== PDF COMPILATION FAILED ===');
      console.error('Error details:', err);

      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(`PDF compilation failed: ${errorMessage}`);

      // Clear PDF URL on error
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
        setPdfUrl(null);
      }
    }
  };

  // Auto-update when user-submitted changes arrive
  useEffect(() => {
    if (!hasData(data)) {
      console.log("No data, clearing preview state");
      setPdfUrl(null);
      setLatexCode('');
      isInitializedRef.current = false;
      setHasGeneratedPreview(false);
      return;
    }

    // If there is a submitted update, perform incremental (will fall back to full init)
    if (lastUpdate) {
      console.log("Processing submitted update:", lastUpdate);
      updateLatexIncremental(lastUpdate);
    }
  }, [data, lastUpdate]);

  // Cleanup URLs on unmount
  useEffect(() => {
    return () => {
      if (pdfUrl) {
        console.log("Cleaning up PDF URL on component unmount");
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

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

  // Removed download handler per requirements (no Download button)

  const copyLatexCode = () => {
    if (latexCode) {
      navigator.clipboard.writeText(latexCode);
    }
  };

  const generatePdf = async () => {
    // Generate final high-quality PDF from backend explicitly
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

      {/* Preview area */}
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
                {isInitializedRef.current ? 'Incremental update in progress' : 'Initial generation'}
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
              <p className="text-lg mb-2">Processing...</p>
              <p className="text-sm text-gray-400 mb-4">
                Your resume preview is being prepared
              </p>
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