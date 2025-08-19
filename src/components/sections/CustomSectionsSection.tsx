import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Trash2, Plus, Settings } from 'lucide-react';
import { CustomSection, UpdateMessage } from '@/types/resume';

interface CustomSectionsSectionProps {
  data: CustomSection[];
  onUpdate: (update: UpdateMessage) => void;
}

export function CustomSectionsSection({ data, onUpdate }: CustomSectionsSectionProps) {
  const [sections, setSections] = useState<CustomSection[]>(data);

  const addSection = () => {
    const newSection: CustomSection = {
      id: Date.now().toString(),
      title: '',
      content: ''
    };
    
    const updatedSections = [...sections, newSection];
    setSections(updatedSections);
    
    onUpdate({
      section: 'customSections',
      entryId: newSection.id,
      changeType: 'add',
      content: newSection
    });
  };

  const updateSection = (id: string, field: keyof CustomSection, value: string) => {
    const updatedSections = sections.map(section =>
      section.id === id ? { ...section, [field]: value } : section
    );
    setSections(updatedSections);
    
    const updatedSection = updatedSections.find(s => s.id === id);
    if (updatedSection) {
      onUpdate({
        section: 'customSections',
        entryId: id,
        changeType: 'update',
        content: updatedSection
      });
    }
  };

  const deleteSection = (id: string) => {
    const updatedSections = sections.filter(section => section.id !== id);
    setSections(updatedSections);
    
    onUpdate({
      section: 'customSections',
      entryId: id,
      changeType: 'delete',
      content: null
    });
  };

  return (
    <div className="space-y-4">
      {sections.map((section) => (
        <Card key={section.id} className="p-4 border-l-4 border-l-accent shadow-soft transition-smooth hover:shadow-medium">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Settings className="h-4 w-4 text-accent" />
                <span className="text-sm font-medium text-muted-foreground">Custom Section</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteSection(section.id)}
                className="text-destructive hover:text-destructive hover:bg-destructive/10 transition-smooth"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="space-y-3">
              <Input
                placeholder="Section Title (e.g., Projects, Certifications, Awards)"
                value={section.title}
                onChange={(e) => updateSection(section.id, 'title', e.target.value)}
                className="font-medium transition-smooth focus:ring-2 focus:ring-accent/20"
              />
              
              <Textarea
                placeholder="Section content..."
                value={section.content}
                onChange={(e) => updateSection(section.id, 'content', e.target.value)}
                rows={4}
                className="resize-none transition-smooth focus:ring-2 focus:ring-accent/20"
              />
            </div>
          </div>
        </Card>
      ))}
      
      <Button
        onClick={addSection}
        variant="outline"
        className="w-full border-dashed border-2 py-8 text-muted-foreground hover:text-accent hover:border-accent transition-smooth group"
      >
        <Plus className="h-5 w-5 mr-2 group-hover:scale-110 transition-transform" />
        Add Custom Section
      </Button>
    </div>
  );
}