import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Experience, UpdateMessage } from '@/types/resume';
import { Plus, Trash2, Calendar, Tag, X, Sparkles, RotateCcw } from 'lucide-react';
import { useState, useEffect } from 'react';

interface ExperienceSectionProps {
  data: Experience[];
  onUpdate: (update: UpdateMessage) => void;
  onPolish: (section: string, entryId: string, content: any) => void;
  isPolishing?: string | null;
}

export function ExperienceSection({ data, onUpdate, onPolish, isPolishing }: ExperienceSectionProps) {
  const [newExperience, setNewExperience] = useState<Omit<Experience, 'id'>>({
    title: '',
    company: '',
    startDate: '',
    endDate: '',
    description: '',
    keywords: []
  });
  const [newKeyword, setNewKeyword] = useState('');
  const [showPolished, setShowPolished] = useState<{ [key: string]: boolean }>({});
  const [isPolishingNew, setIsPolishingNew] = useState(false);

  // Automatically show polished description for entries when it becomes available
  useEffect(() => {
    const updated: { [key: string]: boolean } = { ...showPolished };
    let changed = false;
    for (const exp of data) {
      if (exp.polishedDescription && !updated[exp.id]) {
        updated[exp.id] = true;
        changed = true;
      }
    }
    if (changed) setShowPolished(updated);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  const handleAdd = () => {
    if (newExperience.title && newExperience.company) {
      const experience: Experience = {
        id: `exp_${Date.now()}`,
        ...newExperience
      };

      onUpdate({
        section: 'experience',
        entryId: experience.id,
        changeType: 'add',
        content: experience,
        triggerLatex: true,
      });

      setNewExperience({
        title: '',
        company: '',
        startDate: '',
        endDate: '',
        description: '',
        keywords: []
      });
    }
  };

  const handleUpdate = (id: string, field: keyof Experience, value: any) => {
    const experience = data.find(e => e.id === id);
    if (experience) {
      const updated = { ...experience, [field]: value };
      onUpdate({
        section: 'experience',
        entryId: id,
        changeType: 'update',
        content: updated,
        triggerLatex: false,
      });
    }
  };

  const handleDelete = (id: string) => {
    onUpdate({
      section: 'experience',
      entryId: id,
      changeType: 'delete',
      content: null,
      triggerLatex: true,
    });
  };

  const addKeyword = (id: string, keyword: string) => {
    const experience = data.find(e => e.id === id);
    if (experience && keyword.trim() && !experience.keywords.includes(keyword.trim())) {
      const updated = { ...experience, keywords: [...experience.keywords, keyword.trim()] };
      handleUpdate(id, 'keywords', updated.keywords);
    }
  };

  const removeKeyword = (id: string, keywordToRemove: string) => {
    const experience = data.find(e => e.id === id);
    if (experience) {
      const updated = experience.keywords.filter(k => k !== keywordToRemove);
      handleUpdate(id, 'keywords', updated);
    }
  };

  const addNewKeyword = (keyword: string) => {
    if (keyword.trim() && !newExperience.keywords.includes(keyword.trim())) {
      setNewExperience(prev => ({
        ...prev,
        keywords: [...prev.keywords, keyword.trim()]
      }));
    }
  };

  const removeNewKeyword = (keywordToRemove: string) => {
    setNewExperience(prev => ({
      ...prev,
      keywords: prev.keywords.filter(k => k !== keywordToRemove)
    }));
  };

  const handlePolish = (experience: Experience) => {
    onPolish('experience', experience.id, experience);
  };

  const handleUsePolished = (experience: Experience) => {
    if (experience.polishedDescription) {
      onUpdate({
        section: 'experience',
        entryId: experience.id,
        changeType: 'update',
        content: {
          ...experience,
          description: experience.polishedDescription
        }
      });
      setShowPolished(prev => ({ ...prev, [experience.id]: false }));
    }
  };

  const handleRevert = (experienceId: string) => {
    setShowPolished(prev => ({ ...prev, [experienceId]: false }));
  };

  const togglePolished = (experienceId: string) => {
    setShowPolished(prev => ({ ...prev, [experienceId]: !prev[experienceId] }));
  };

  const polishNewDraft = async () => {
    if (!newExperience.description.trim()) return;
    setIsPolishingNew(true);
    try {
      const res = await fetch('/api/polish-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ section: 'experience', entryId: 'new-experience', content: newExperience }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.message || 'Polish failed');

      const envelope = data.improvedContent ?? data.content ?? data;
      const normalized = envelope && typeof envelope === 'object' && 'content' in envelope ? envelope.content : envelope;
      const improvedText = normalized?.polishedDescription ?? normalized?.description ?? '';

      if (improvedText) {
        setNewExperience(prev => ({ ...prev, description: improvedText }));
      }
    } catch (e) {
      console.error('Error polishing draft experience:', e);
    } finally {
      setIsPolishingNew(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Existing experience entries */}
      {data.map((experience) => {
        const isShowingPolished = showPolished[experience.id];
        const currentDescription = isShowingPolished && experience.polishedDescription
          ? experience.polishedDescription
          : experience.description;

        return (
          <Card key={experience.id} className="p-6 transition-smooth hover:shadow-soft">
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
                  <div>
                    <Label className="text-sm font-medium">Job Title</Label>
                    <Input
                      value={experience.title}
                      onChange={(e) => handleUpdate(experience.id, 'title', e.target.value)}
                      placeholder="Software Engineer"
                      className="transition-smooth"
                    />
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Company</Label>
                    <Input
                      value={experience.company}
                      onChange={(e) => handleUpdate(experience.id, 'company', e.target.value)}
                      placeholder="Company Name"
                      className="transition-smooth"
                    />
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  {experience.polishedDescription && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRevert(experience.id)}
                        disabled={!isShowingPolished}
                        className="text-xs"
                      >
                        <RotateCcw className="h-3 w-3 mr-1" />
                        Original
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleUsePolished(experience)}
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
                    onClick={() => handlePolish(experience)}
                    disabled={isPolishing === experience.id || !experience.description.trim()}
                    className="text-xs"
                  >
                    {isPolishing === experience.id ? (
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
                    onClick={() => handleDelete(experience.id)}
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
                    value={experience.startDate}
                    onChange={(e) => handleUpdate(experience.id, 'startDate', e.target.value)}
                    className="transition-smooth"
                  />
                </div>
                <div>
                  <Label className="text-sm font-medium flex items:center gap-2">
                    <Calendar className="h-4 w-4" />
                    End Date
                  </Label>
                  <Input
                    type="month"
                    value={experience.endDate}
                    onChange={(e) => handleUpdate(experience.id, 'endDate', e.target.value)}
                    className="transition-smooth"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-sm font-medium">Description</Label>
                  {experience.polishedDescription && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => togglePolished(experience.id)}
                      className="text-xs h-6 px-2"
                    >
                      {isShowingPolished ? 'Show Original' : 'Show Polished'}
                    </Button>
                  )}
                </div>
                <Textarea
                  value={currentDescription}
                  onChange={(e) => handleUpdate(experience.id, 'description', e.target.value)}
                  placeholder="Describe your role, responsibilities, and achievements..."
                  className="transition-smooth"
                  rows={4}
                />
                {experience.polishedDescription && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {isShowingPolished ? (
                      <span className="text-blue-600">Showing AI-polished version</span>
                    ) : (
                      <span>AI-polished version available - click "Show Polished" to view</span>
                    )}
                  </div>
                )}
              </div>

              <div>
                <Label className="text-sm font-medium flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  Keywords
                </Label>
                <div className="flex flex-wrap gap-2 mt-2 mb-3">
                  {experience.keywords.map((keyword) => (
                    <Badge key={keyword} variant="secondary" className="transition-smooth hover:bg-destructive hover:text-destructive-foreground">
                      {keyword}
                      <X
                        className="h-3 w-3 ml-1 cursor-pointer"
                        onClick={() => removeKeyword(experience.id, keyword)}
                      />
                    </Badge>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add keyword"
                    className="transition-smooth"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        const target = e.target as HTMLInputElement;
                        addKeyword(experience.id, target.value);
                        target.value = '';
                      }
                    }}
                  />
                  <Button
                    variant="outline"
                    onClick={(e) => {
                      const input = (e.target as HTMLElement).parentElement?.querySelector('input') as HTMLInputElement;
                      if (input) {
                        addKeyword(experience.id, input.value);
                        input.value = '';
                      }
                    }}
                    className="transition-smooth"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        );
      })}

      {/* Add new experience */}
      <Card className="p-6 border-dashed border-2 transition-smooth hover:border-primary/50">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">Job Title</Label>
              <Input
                value={newExperience.title}
                onChange={(e) => setNewExperience(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Software Engineer"
                className="transition-smooth"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Company</Label>
              <Input
                value={newExperience.company}
                onChange={(e) => setNewExperience(prev => ({ ...prev, company: e.target.value }))}
                placeholder="Company Name"
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
                value={newExperience.startDate}
                onChange={(e) => setNewExperience(prev => ({ ...prev, startDate: e.target.value }))}
                className="transition-smooth"
              />
            </div>
            <div>
              <Label className="text-sm font-medium flex items:center gap-2">
                <Calendar className="h-4 w-4" />
                End Date
              </Label>
              <Input
                type="month"
                value={newExperience.endDate}
                onChange={(e) => setNewExperience(prev => ({ ...prev, endDate: e.target.value }))}
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
                disabled={isPolishingNew || !newExperience.description.trim()}
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
              value={newExperience.description}
              onChange={(e) => setNewExperience(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe your role, responsibilities, and achievements..."
              className="transition-smooth"
              rows={4}
            />
          </div>

          <div>
            <Label className="text-sm font-medium flex items-center gap-2">
              <Tag className="h-4 w-4" />
              Keywords
            </Label>
            <div className="flex flex-wrap gap-2 mt-2 mb-3">
              {newExperience.keywords.map((keyword) => (
                <Badge key={keyword} variant="secondary" className="transition-smooth hover:bg-destructive hover:text-destructive-foreground">
                  {keyword}
                  <X
                    className="h-3 w-3 ml-1 cursor-pointer"
                    onClick={() => removeNewKeyword(keyword)}
                  />
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Add keyword"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                className="transition-smooth"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    addNewKeyword(newKeyword);
                    setNewKeyword('');
                  }
                }}
              />
              <Button
                variant="outline"
                onClick={() => {
                  addNewKeyword(newKeyword);
                  setNewKeyword('');
                }}
                className="transition-smooth"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <Button
            onClick={handleAdd}
            disabled={!newExperience.title || !newExperience.company}
            className="bg-gradient-primary hover:opacity-90 transition-smooth"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Experience
          </Button>
        </div>
      </Card>
    </div>
  );
}
