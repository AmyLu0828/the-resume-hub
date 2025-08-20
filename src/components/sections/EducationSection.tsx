import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Education, UpdateMessage } from '@/types/resume';
import { Plus, Trash2, Calendar, Sparkles, RotateCcw } from 'lucide-react';
import { useState, useEffect } from 'react';

interface EducationSectionProps {
  data: Education[];
  onUpdate: (update: UpdateMessage) => void;
  onPolish: (section: string, entryId: string, content: any) => void;
  isPolishing?: string | null;
}

export function EducationSection({ data, onUpdate, onPolish, isPolishing }: EducationSectionProps) {
  const [newEducation, setNewEducation] = useState<Omit<Education, 'id'>>({
    degree: '',
    institution: '',
    startDate: '',
    endDate: '',
    description: ''
  });
  const [showPolished, setShowPolished] = useState<{ [key: string]: boolean }>({});
  const [isPolishingNew, setIsPolishingNew] = useState(false);

  // Automatically show polished description for entries when it becomes available
  useEffect(() => {
    const updated: { [key: string]: boolean } = { ...showPolished };
    let changed = false;
    for (const edu of data) {
      if (edu.polishedDescription && !updated[edu.id]) {
        updated[edu.id] = true;
        changed = true;
      }
    }
    if (changed) setShowPolished(updated);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  const handleAdd = () => {
    if (newEducation.degree && newEducation.institution) {
      const education: Education = {
        id: `edu_${Date.now()}`,
        ...newEducation
      };

      onUpdate({
        section: 'education',
        entryId: education.id,
        changeType: 'add',
        content: education,
        triggerLatex: true,
      });

      setNewEducation({
        degree: '',
        institution: '',
        startDate: '',
        endDate: '',
        description: ''
      });
    }
  };

  const handleUpdate = (id: string, field: keyof Education, value: string) => {
    const education = data.find(e => e.id === id);
    if (education) {
      const updated = { ...education, [field]: value };
      onUpdate({
        section: 'education',
        entryId: id,
        changeType: 'update',
        content: updated,
        triggerLatex: false,
      });
    }
  };

  const handleDelete = (id: string) => {
    onUpdate({
      section: 'education',
      entryId: id,
      changeType: 'delete',
      content: null,
      triggerLatex: true,
    });
  };

  const handlePolish = (education: Education) => {
    onPolish('education', education.id, education);
  };

  const handleUsePolished = (education: Education) => {
    if (education.polishedDescription) {
      onUpdate({
        section: 'education',
        entryId: education.id,
        changeType: 'update',
        content: {
          ...education,
          description: education.polishedDescription
        }
      });
      setShowPolished(prev => ({ ...prev, [education.id]: false }));
    }
  };

  const handleRevert = (educationId: string) => {
    setShowPolished(prev => ({ ...prev, [educationId]: false }));
  };

  const togglePolished = (educationId: string) => {
    setShowPolished(prev => ({ ...prev, [educationId]: !prev[educationId] }));
  };

  const polishNewDraft = async () => {
    if (!newEducation.description.trim()) return;
    setIsPolishingNew(true);
    try {
      const res = await fetch('/api/polish-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ section: 'education', entryId: 'new-education', content: newEducation }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.message || 'Polish failed');

      const envelope = data.improvedContent ?? data.content ?? data;
      const normalized = envelope && typeof envelope === 'object' && 'content' in envelope ? envelope.content : envelope;
      const improvedText = normalized?.polishedDescription ?? normalized?.description ?? '';

      if (improvedText) {
        setNewEducation(prev => ({ ...prev, description: improvedText }));
      }
    } catch (e) {
      console.error('Error polishing draft education:', e);
    } finally {
      setIsPolishingNew(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Existing education entries */}
      {data.map((education) => {
        const isShowingPolished = showPolished[education.id];
        const currentDescription = isShowingPolished && education.polishedDescription
          ? education.polishedDescription
          : education.description;

        return (
          <Card key={education.id} className="p-6 transition-smooth hover:shadow-soft">
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
                  <div>
                    <Label className="text-sm font-medium">Degree</Label>
                    <Input
                      value={education.degree}
                      onChange={(e) => handleUpdate(education.id, 'degree', e.target.value)}
                      placeholder="Bachelor of Science in Computer Science"
                      className="transition-smooth"
                    />
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Institution</Label>
                    <Input
                      value={education.institution}
                      onChange={(e) => handleUpdate(education.id, 'institution', e.target.value)}
                      placeholder="University Name"
                      className="transition-smooth"
                    />
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  {education.polishedDescription && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRevert(education.id)}
                        disabled={!isShowingPolished}
                        className="text-xs"
                      >
                        <RotateCcw className="h-3 w-3 mr-1" />
                        Original
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleUsePolished(education)}
                        disabled={isShowingPolished}
                        className="text-xs"
                      >
                        <Sparkles className="h-3 w-3 mr-1" />
                        Use Polished
                      </Button>
                    </>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePolish(education)}
                    disabled={isPolishing === education.id || !education.description.trim()}
                    className="text-xs"
                  >
                    {isPolishing === education.id ? (
                      <>
                        <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary mr-1"></div>
                        Polishing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-3 w-3 mr-1" />
                        Polish
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handleDelete(education.id)}
                    className="text-destructive hover:text-destructive-foreground hover:bg-destructive transition-smooth"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Start Date
                  </Label>
                  <Input
                    type="month"
                    value={education.startDate}
                    onChange={(e) => handleUpdate(education.id, 'startDate', e.target.value)}
                    className="transition-smooth"
                  />
                </div>
                <div>
                  <Label className="text-sm font-medium flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    End Date
                  </Label>
                  <Input
                    type="month"
                    value={education.endDate}
                    onChange={(e) => handleUpdate(education.id, 'endDate', e.target.value)}
                    className="transition-smooth"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-sm font-medium">Description</Label>
                  {education.polishedDescription && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => togglePolished(education.id)}
                      className="text-xs h-6 px-2"
                    >
                      {isShowingPolished ? 'Show Original' : 'Show Polished'}
                    </Button>
                  )}
                </div>
                <Textarea
                  value={currentDescription}
                  onChange={(e) => handleUpdate(education.id, 'description', e.target.value)}
                  placeholder="Relevant coursework, achievements, GPA, etc."
                  className="transition-smooth"
                  rows={3}
                />
                {education.polishedDescription && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {isShowingPolished ? (
                      <span className="text-blue-600">Showing AI-polished version</span>
                    ) : (
                      <span>AI-polished version available - click "Show Polished" to view</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </Card>
        );
      })}

      {/* Add new education */}
      <Card className="p-6 border-dashed border-2 transition-smooth hover:border-primary/50">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">Degree</Label>
              <Input
                value={newEducation.degree}
                onChange={(e) => setNewEducation(prev => ({ ...prev, degree: e.target.value }))}
                placeholder="Bachelor of Science in Computer Science"
                className="transition-smooth"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Institution</Label>
              <Input
                value={newEducation.institution}
                onChange={(e) => setNewEducation(prev => ({ ...prev, institution: e.target.value }))}
                placeholder="University Name"
                className="transition-smooth"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Start Date
              </Label>
              <Input
                type="month"
                value={newEducation.startDate}
                onChange={(e) => setNewEducation(prev => ({ ...prev, startDate: e.target.value }))}
                className="transition-smooth"
              />
            </div>
            <div>
              <Label className="text-sm font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                End Date
              </Label>
              <Input
                type="month"
                value={newEducation.endDate}
                onChange={(e) => setNewEducation(prev => ({ ...prev, endDate: e.target.value }))}
                className="transition-smooth"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <Label className="text-sm font-medium">Description</Label>
              <Button
                variant="ghost"
                size="sm"
                onClick={polishNewDraft}
                disabled={isPolishingNew || !newEducation.description.trim()}
                className="text-xs h-6 px-2"
              >
                {isPolishingNew ? (
                  <>
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary mr-1"></div>
                    Polishing...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3 w-3 mr-1" />
                    Polish
                  </>
                )}
              </Button>
            </div>
            <Textarea
              value={newEducation.description}
              onChange={(e) => setNewEducation(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Relevant coursework, achievements, GPA, etc."
              className="transition-smooth"
              rows={3}
            />
          </div>

          <Button
            onClick={handleAdd}
            disabled={!newEducation.degree || !newEducation.institution}
            className="bg-gradient-primary hover:opacity-90 transition-smooth"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Education
          </Button>
        </div>
      </Card>
    </div>
  );
}
