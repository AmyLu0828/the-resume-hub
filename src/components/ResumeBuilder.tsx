import { useState, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { NameSection } from './sections/NameSection';
import { AboutMeSection } from './sections/AboutMeSection';
import { EducationSection } from './sections/EducationSection';
import { ExperienceSection } from './sections/ExperienceSection';
import { ContactSection } from './sections/ContactSection';
import { SkillsSection } from './sections/SkillsSection';
import { CustomSectionsSection } from './sections/CustomSectionsSection';
import { PDFPreview } from './PDFPreview';
import { ResumeData, UpdateMessage } from '@/types/resume';
import { FileText, User, GraduationCap, Briefcase, Phone, Code, Settings, UploadCloud, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';

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
  const [isPolishing, setIsPolishing] = useState<string | null>(null);

  // FIXED: Change from lastUpdate to submitTrigger
  const [submitTrigger, setSubmitTrigger] = useState<{
    section: string;
    entryId: string;
    changeType: string;
    timestamp: number;
  } | null>(null);

  const handleUpdate = useCallback((update: UpdateMessage) => {
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

    // FIXED: Remove automatic LaTeX triggering - only manual submit now
    console.log('Data updated:', {
      section: update.section,
      changeType: update.changeType,
      entryId: update.entryId
    });

  }, []);

  // Scrape Template button handler
  const handleScrapeTemplate = async () => {
    try {
      await fetch('/api/template/scrape', { method: 'POST' });
    } catch (e) {
      console.error('Failed to scrape template', e);
    }
  };

  // FIXED: Updated header submit handler
  const handleSubmitHeader = async () => {
    console.log('Submitting header with data:', { name: resumeData.name, contact: resumeData.contact });
    
    setSubmitTrigger({
      section: 'header',
      entryId: 'header_bundle',
      changeType: 'update',
      timestamp: Date.now()
    });
  };

  // FIXED: Add section submit handlers
  const handleSubmitAboutMe = () => {
    console.log('Submitting About Me section');
    setSubmitTrigger({
      section: 'aboutMe',
      entryId: 'about',
      changeType: 'update',
      timestamp: Date.now()
    });
  };

  const handleSubmitEducation = () => {
    console.log('Submitting Education section');
    setSubmitTrigger({
      section: 'education',
      entryId: 'education',
      changeType: 'update',
      timestamp: Date.now()
    });
  };

  const handleSubmitExperience = () => {
    console.log('Submitting Experience section');
    setSubmitTrigger({
      section: 'experience',
      entryId: 'experience',
      changeType: 'update',
      timestamp: Date.now()
    });
  };

  const handleSubmitSkills = () => {
    console.log('Submitting Skills section');
    setSubmitTrigger({
      section: 'skills',
      entryId: 'skills',
      changeType: 'update',
      timestamp: Date.now()
    });
  };

  const handleSubmitCustomSections = () => {
    console.log('Submitting Custom Sections');
    setSubmitTrigger({
      section: 'customSections',
      entryId: 'customSections',
      changeType: 'update',
      timestamp: Date.now()
    });
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

      // Normalize backend payload
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
              newData.aboutMe.description = improvedText;
            }
            break;
          }
          case 'education': {
            const i = newData.education.findIndex(e => e.id === entryId);
            if (i >= 0 && improvedText) {
              newData.education[i].polishedDescription = improvedText;
              newData.education[i].description = improvedText;
            }
            break;
          }
          case 'experience': {
            const i = newData.experience.findIndex(e => e.id === entryId);
            if (i >= 0 && improvedText) {
              newData.experience[i].polishedDescription = improvedText;
              newData.experience[i].description = improvedText;
            }
            break;
          }
          case 'customSections': {
            const i = newData.customSections.findIndex(c => c.id === entryId);
            if (i >= 0) {
              const improvedContentText = normalized?.content ?? improvedText;
              if (improvedContentText) {
                newData.customSections[i].content = improvedContentText;
              }
            }
            break;
          }
          default:
            break;
        }

        return newData;
      });

      // FIXED: Auto-trigger LaTeX update after polishing
      setSubmitTrigger({
        section: section,
        entryId: entryId,
        changeType: 'update',
        timestamp: Date.now()
      });

    } catch (error) {
      console.error('Error polishing content:', error);
    } finally {
      setIsPolishing(null);
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
            Create professional resumes with AI assistance and live LaTeX preview.
            Submit each section to see updates in the preview.
          </p>
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
                  {submitTrigger && (
                    <div className="ml-auto text-xs text-green-600 flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
                      Last Update: {submitTrigger.section}
                    </div>
                  )}
                </div>

                {/* Scrape template button */}
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={handleScrapeTemplate} className="flex items-center gap-2">
                    <UploadCloud className="h-4 w-4" />
                    Scrape Template
                  </Button>
                </div>

                {/* Name + Contacts bundle with one Submit button */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50/50">
                  <div className="flex items-center gap-3 pb-4 border-b border-gray-200 mb-6">
                    <User className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-medium">Header Information</h3>
                  </div>

                  <NameSection data={resumeData.name} onUpdate={handleUpdate} />

                  <div className="flex items-center gap-3 pt-6 pb-4 border-b border-gray-200">
                    <Phone className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-medium">Contact Information</h3>
                  </div>
                  <ContactSection data={resumeData.contact} onUpdate={handleUpdate} />

                  <div className="flex justify-end pt-4">
                    <Button onClick={handleSubmitHeader} className="flex items-center gap-2">
                      <Save className="h-4 w-4" />
                      Submit Header
                    </Button>
                  </div>
                </div>

                {/* FIXED: About Me section with submit button */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50/50">
                  <AboutMeSection
                    data={resumeData.aboutMe}
                    onUpdate={handleUpdate}
                    onPolish={handlePolish}
                    isPolishing={isPolishing === 'about'}
                  />
                  <div className="flex justify-end pt-4">
                    <Button onClick={handleSubmitAboutMe} className="flex items-center gap-2">
                      <Save className="h-4 w-4" />
                      Submit About Me
                    </Button>
                  </div>
                </div>

                {/* FIXED: Education section with submit button */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50/50">
                  <div className="flex items-center gap-3 pb-4 border-b border-gray-200 mb-6">
                    <GraduationCap className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-medium">Education</h3>
                  </div>
                  <EducationSection
                    data={resumeData.education}
                    onUpdate={handleUpdate}
                    onPolish={handlePolish}
                    isPolishing={isPolishing}
                  />
                  <div className="flex justify-end pt-4">
                    <Button onClick={handleSubmitEducation} className="flex items-center gap-2">
                      <Save className="h-4 w-4" />
                      Submit Education
                    </Button>
                  </div>
                </div>

                {/* FIXED: Experience section with submit button */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50/50">
                  <div className="flex items-center gap-3 pb-4 border-b border-gray-200 mb-6">
                    <Briefcase className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-medium">Experience</h3>
                  </div>
                  <ExperienceSection
                    data={resumeData.experience}
                    onUpdate={handleUpdate}
                    onPolish={handlePolish}
                    isPolishing={isPolishing}
                  />
                  <div className="flex justify-end pt-4">
                    <Button onClick={handleSubmitExperience} className="flex items-center gap-2">
                      <Save className="h-4 w-4" />
                      Submit Experience
                    </Button>
                  </div>
                </div>

                {/* FIXED: Skills section with submit button */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50/50">
                  <div className="flex items-center gap-3 pb-4 border-b border-gray-200 mb-6">
                    <Code className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-medium">Skills</h3>
                  </div>
                  <SkillsSection
                    data={resumeData.skills}
                    onUpdate={handleUpdate}
                  />
                  <div className="flex justify-end pt-4">
                    <Button onClick={handleSubmitSkills} className="flex items-center gap-2">
                      <Save className="h-4 w-4" />
                      Submit Skills
                    </Button>
                  </div>
                </div>

                {/* FIXED: Custom Sections with submit button */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50/50">
                  <div className="flex items-center gap-3 pb-4 border-b border-gray-200 mb-6">
                    <Settings className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-medium">Custom Sections</h3>
                  </div>
                  <CustomSectionsSection
                    data={resumeData.customSections}
                    onUpdate={handleUpdate}
                  />
                  <div className="flex justify-end pt-4">
                    <Button onClick={handleSubmitCustomSections} className="flex items-center gap-2">
                      <Save className="h-4 w-4" />
                      Submit Custom Sections
                    </Button>
                  </div>
                </div>
              </div>
            </ScrollArea>
          </Card>

          {/* FIXED: Right column - PDF preview with submit-based updates */}
          <Card className="p-6 shadow-medium">
            <PDFPreview
              data={resumeData}
              onSubmitUpdate={submitTrigger}
            />
          </Card>
        </div>
      </div>
    </div>
  );
}