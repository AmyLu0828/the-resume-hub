import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ResumeData } from '@/types/resume';
import { FileText, Download, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PDFPreviewProps {
  data: ResumeData;
}

export function PDFPreview({ data }: PDFPreviewProps) {
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const [year, month] = dateString.split('-');
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${monthNames[parseInt(month) - 1]} ${year}`;
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Eye className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Live Preview</h3>
        </div>
        <Button variant="outline" size="sm" className="transition-smooth hover:bg-primary hover:text-primary-foreground">
          <Download className="h-4 w-4 mr-2" />
          Download PDF
        </Button>
      </div>

      <Card className="flex-1 p-8 overflow-auto bg-white shadow-medium transition-smooth">
        <div className="max-w-[210mm] mx-auto space-y-6 text-sm">
          {/* Header with contact info */}
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-bold text-gray-900">
              {data.name.firstName && data.name.lastName
                ? `${data.name.firstName} ${data.name.lastName}`
                : 'Your Name'}
            </h1>
            <div className="flex flex-wrap justify-center gap-3 text-gray-600">
              {data.contact.map((contact) => (
                <span key={contact.id} className="flex items-center gap-1">
                  <span className="font-medium">{contact.type}:</span>
                  {contact.value}
                </span>
              ))}
            </div>
          </div>

          {/* About Me */}
          {data.aboutMe.description && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2 border-b border-gray-200 pb-1">
                About Me
              </h2>
              <p className="text-gray-700 leading-relaxed">{data.aboutMe.description}</p>
            </div>
          )}

          {/* Experience */}
          {data.experience.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1">
                Experience
              </h2>
              <div className="space-y-4">
                {data.experience.map((exp) => (
                  <div key={exp.id} className="space-y-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900">{exp.title}</h3>
                        <p className="text-primary font-medium">{exp.company}</p>
                      </div>
                      <span className="text-gray-600 text-sm">
                        {formatDate(exp.startDate)} - {formatDate(exp.endDate) || 'Present'}
                      </span>
                    </div>
                    {exp.description && (
                      <p className="text-gray-700 leading-relaxed">{exp.description}</p>
                    )}
                    {exp.keywords.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {exp.keywords.map((keyword) => (
                          <Badge key={keyword} variant="outline" className="text-xs">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {data.education.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1">
                Education
              </h2>
              <div className="space-y-4">
                {data.education.map((edu) => (
                  <div key={edu.id} className="space-y-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900">{edu.degree}</h3>
                        <p className="text-primary font-medium">{edu.institution}</p>
                      </div>
                      <span className="text-gray-600 text-sm">
                        {formatDate(edu.startDate)} - {formatDate(edu.endDate)}
                      </span>
                    </div>
                    {edu.description && (
                      <p className="text-gray-700 leading-relaxed">{edu.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skills */}
          {data.skills.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1">
                Skills
              </h2>
              <div className="flex flex-wrap gap-2">
                {data.skills.map((skill) => (
                  <Badge key={skill.id} variant="secondary" className="text-sm">
                    {skill.skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Custom Sections */}
          {data.customSections.length > 0 && (
            <>
              {data.customSections.map((section) => (
                section.title && section.content && (
                  <div key={section.id}>
                    <h2 className="text-lg font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1">
                      {section.title}
                    </h2>
                    <p className="text-gray-700 leading-relaxed whitespace-pre-line">{section.content}</p>
                  </div>
                )
              ))}
            </>
          )}

          {/* Empty state */}
          {!data.aboutMe.description &&
            data.contact.length === 0 &&
            data.education.length === 0 &&
            data.experience.length === 0 &&
            data.skills.length === 0 &&
            data.customSections.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">Your resume preview will appear here</p>
                <p className="text-sm">Start filling out the form to see your resume come to life!</p>
              </div>
            )}
        </div>
      </Card>
    </div>
  );
}