import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { NameSection } from './sections/NameSection';
import { AboutMeSection } from './sections/AboutMeSection';
import { EducationSection } from './sections/EducationSection';
import { ExperienceSection } from './sections/ExperienceSection';
import { ContactSection } from './sections/ContactSection';
import { SkillsSection } from './sections/SkillsSection';
import { CustomSectionsSection } from './sections/CustomSectionsSection';
import { PDFPreview } from './PDFPreview';
import { ResumeData, UpdateMessage } from '@/types/resume';
import { FileText, User, GraduationCap, Briefcase, Phone, Code, Settings, Download } from 'lucide-react';

const initialData: ResumeData = {
  name: { firstName: '', lastName: '' },
  aboutMe: { description: '', polishedDescription: '' },
  education: [],
  experience: [],
  contact: [],
  skills: [],
  customSections: []
};

export function ResumeBuilder() {
  const [resumeData, setResumeData] = useState<ResumeData>(initialData);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [isPolishing, setIsPolishing] = useState<string | null>(null); // Track which section is being polished

  const handleUpdate = (update: UpdateMessage) => {
    setResumeData(prev => {
      const newData = { ...prev };

      switch (update.section) {
        case 'name':
          newData.name = update.content;
          break;
        case 'aboutMe':
          newData.aboutMe = update.content;
          break;
        case 'education':
          if (update.changeType === 'add') {
            newData.education.push(update.content);
          } else if (update.changeType === 'update') {
            const eduIndex = newData.education.findIndex(e => e.id === update.entryId);
            if (eduIndex >= 0) newData.education[eduIndex] = update.content;
          } else if (update.changeType === 'delete') {
            newData.education = newData.education.filter(e => e.id !== update.entryId);
          }
          break;
        case 'experience':
          if (update.changeType === 'add') {
            newData.experience.push(update.content);
          } else if (update.changeType === 'update') {
            const expIndex = newData.experience.findIndex(e => e.id === update.entryId);
            if (expIndex >= 0) newData.experience[expIndex] = update.content;
          } else if (update.changeType === 'delete') {
            newData.experience = newData.experience.filter(e => e.id !== update.entryId);
          }
          break;
        case 'contact':
          if (update.changeType === 'add') {
            newData.contact.push(update.content);
          } else if (update.changeType === 'update') {
            const contactIndex = newData.contact.findIndex(c => c.id === update.entryId);
            if (contactIndex >= 0) newData.contact[contactIndex] = update.content;
          } else if (update.changeType === 'delete') {
            newData.contact = newData.contact.filter(c => c.id !== update.entryId);
          }
          break;
        case 'skills':
          if (update.changeType === 'add') {
            newData.skills.push(update.content);
          } else if (update.changeType === 'update') {
            const skillIndex = newData.skills.findIndex(s => s.id === update.entryId);
            if (skillIndex >= 0) newData.skills[skillIndex] = update.content;
          } else if (update.changeType === 'delete') {
            newData.skills = newData.skills.filter(s => s.id !== update.entryId);
          }
          break;
        case 'customSections':
          if (update.changeType === 'add') {
            newData.customSections.push(update.content);
          } else if (update.changeType === 'update') {
            const customIndex = newData.customSections.findIndex(c => c.id === update.entryId);
            if (customIndex >= 0) newData.customSections[customIndex] = update.content;
          } else if (update.changeType === 'delete') {
            newData.customSections = newData.customSections.filter(c => c.id !== update.entryId);
          }
          break;
      }

      return newData;
    });

    // Store update for potential backend sync (not sending immediately)
    console.log('Update stored locally:', update);
  };

  const handlePolish = async (section: string, entryId: string, content: any) => {
    setIsPolishing(entryId);
    try {
      const res = await fetch('/api/polish-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ section, entryId, content }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.message || 'Polish failed');

      // Normalize backend payload: sometimes returns the whole envelope with a nested `content`
      const envelope = data.improvedContent ?? data.content ?? data;
      const normalized = envelope && typeof envelope === 'object' && 'content' in envelope
        ? envelope.content
        : envelope;

      const getImprovedText = (obj: any) =>
        obj?.polishedDescription ?? obj?.description ?? obj?.summary ?? obj?.text ?? '';

      const improvedText = getImprovedText(normalized);

      setResumeData(prev => {
        const newData = { ...prev };

        switch (section) {
          case 'aboutMe': {
            if (improvedText) {
              newData.aboutMe.polishedDescription = improvedText;
              newData.aboutMe.description = improvedText; // show immediately in textarea
            }
            break;
          }
          case 'education': {
            const i = newData.education.findIndex(e => e.id === entryId);
            if (i >= 0 && improvedText) {
              newData.education[i].polishedDescription = improvedText;
              newData.education[i].description = improvedText; // show immediately
            }
            break;
          }
          case 'experience': {
            const i = newData.experience.findIndex(e => e.id === entryId);
            if (i >= 0 && improvedText) {
              newData.experience[i].polishedDescription = improvedText;
              newData.experience[i].description = improvedText; // show immediately
            }
            break;
          }
          case 'customSections': {
            const i = newData.customSections.findIndex(c => c.id === entryId);
            if (i >= 0) {
              const improvedContentText = normalized?.content ?? improvedText;
              if (improvedContentText) {
                newData.customSections[i].content = improvedContentText; // show immediately
              }
            }
            break;
          }
          default:
            break;
        }

        return newData;
      });
    } catch (error) {
      console.error('Error polishing content:', error);
    } finally {
      setIsPolishing(null);
    }
  };

  const handleGeneratePDF = async () => {
    setIsGeneratingPDF(true);
    try {
      // TODO: Send resumeData to backend for PDF generation
      console.log('Sending resume data to backend for PDF generation:', resumeData);

      // TODO: Replace this with actual API call
      // const response = await fetch('/api/generate-pdf', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(resumeData)
      // });

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      console.log('PDF generation completed (placeholder)');
    } catch (error) {
      console.error('Error generating PDF:', error);
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-secondary">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative p-4 bg-gradient-primary rounded-2xl shadow-glow transition-bounce hover:scale-105">
              <FileText className="h-10 w-10 text-white" />
              <div className="absolute inset-0 bg-gradient-primary rounded-2xl blur opacity-30 -z-10"></div>
            </div>
            <div>
              <h1 className="text-5xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
                The Resume Hub
              </h1>
              <div className="h-1 w-20 bg-gradient-accent rounded-full mx-auto"></div>
            </div>
          </div>
          <p className="text-muted-foreground text-xl max-w-3xl mx-auto leading-relaxed">
            Create professional resumes with AI assistance. Fill in your information and watch your resume come to life in real-time.
          </p>
        </div>

        {/* Generate PDF Button */}
        <div className="mb-6 text-center">
          <Button
            onClick={handleGeneratePDF}
            disabled={isGeneratingPDF}
            className="bg-gradient-primary hover:opacity-90 transition-smooth px-8 py-3 text-lg"
          >
            {isGeneratingPDF ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Generating PDF...
              </>
            ) : (
              <>
                <Download className="h-5 w-5 mr-2" />
                Generate PDF
              </>
            )}
          </Button>
        </div>

        {/* Two-column layout */}
        <div className="grid lg:grid-cols-2 gap-8 h-[calc(100vh-300px)]">
          {/* Left column - Form sections */}
          <Card className="p-6 shadow-medium">
            <ScrollArea className="h-full pr-4">
              <div className="space-y-8">
                <div className="flex items-center gap-3 pb-4 border-b">
                  <User className="h-5 w-5 text-primary" />
                  <h2 className="text-xl font-semibold">Resume Information</h2>
                </div>

                <NameSection
                  data={resumeData.name}
                  onUpdate={handleUpdate}
                />

                <AboutMeSection
                  data={resumeData.aboutMe}
                  onUpdate={handleUpdate}
                  onPolish={handlePolish}
                  isPolishing={isPolishing === 'about'}
                />

                <div className="flex items-center gap-3 pt-4">
                  <Phone className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-medium">Contact Information</h3>
                </div>
                <ContactSection
                  data={resumeData.contact}
                  onUpdate={handleUpdate}
                />

                <div className="flex items-center gap-3 pt-4">
                  <GraduationCap className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-medium">Education</h3>
                </div>
                <EducationSection
                  data={resumeData.education}
                  onUpdate={handleUpdate}
                  onPolish={handlePolish}
                  isPolishing={isPolishing}
                />

                <div className="flex items-center gap-3 pt-4">
                  <Briefcase className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-medium">Experience</h3>
                </div>
                <ExperienceSection
                  data={resumeData.experience}
                  onUpdate={handleUpdate}
                  onPolish={handlePolish}
                  isPolishing={isPolishing}
                />

                <div className="flex items-center gap-3 pt-4">
                  <Code className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-medium">Skills</h3>
                </div>
                <SkillsSection
                  data={resumeData.skills}
                  onUpdate={handleUpdate}
                />

                <div className="flex items-center gap-3 pt-4">
                  <Settings className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-medium">Custom Sections</h3>
                </div>
                <CustomSectionsSection
                  data={resumeData.customSections}
                  onUpdate={handleUpdate}
                />
              </div>
            </ScrollArea>
          </Card>

          {/* Right column - PDF preview */}
          <Card className="p-6 shadow-medium">
            <PDFPreview data={resumeData} />
          </Card>
        </div>
      </div>
    </div>
  );
}