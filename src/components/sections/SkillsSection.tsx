import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Skill, UpdateMessage } from '@/types/resume';
import { Plus, X } from 'lucide-react';
import { useState } from 'react';

interface SkillsSectionProps {
  data: Skill[];
  onUpdate: (update: UpdateMessage) => void;
}

export function SkillsSection({ data, onUpdate }: SkillsSectionProps) {
  const [newSkill, setNewSkill] = useState('');

  const handleAdd = () => {
    if (newSkill.trim() && !data.some(s => s.skill.toLowerCase() === newSkill.trim().toLowerCase())) {
      const skill: Skill = {
        id: `skill_${Date.now()}`,
        skill: newSkill.trim()
      };

      onUpdate({
        section: 'skills',
        entryId: skill.id,
        changeType: 'add',
        content: skill,
        triggerLatex: true,
      });

      setNewSkill('');
    }
  };

  const handleDelete = (id: string) => {
    onUpdate({
      section: 'skills',
      entryId: id,
      changeType: 'delete',
      content: null,
      triggerLatex: true,
    });
  };

  const handleUpdate = (id: string, skill: string) => {
    const existingSkill = data.find(s => s.id === id);
    if (existingSkill) {
      const updated = { ...existingSkill, skill };
      onUpdate({
        section: 'skills',
        entryId: id,
        changeType: 'update',
        content: updated,
        triggerLatex: false,
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* Skills display */}
      {data.length > 0 && (
        <Card className="p-4 transition-smooth">
          <div className="flex flex-wrap gap-2">
            {data.map((skill) => (
              <Badge
                key={skill.id}
                variant="secondary"
                className="text-sm py-2 px-3 transition-smooth hover:bg-primary hover:text-primary-foreground cursor-pointer group"
              >
                <Input
                  value={skill.skill}
                  onChange={(e) => handleUpdate(skill.id, e.target.value)}
                  className="border-none p-0 h-auto bg-transparent text-inherit focus:ring-0 focus:outline-none min-w-[60px] max-w-[120px]"
                  onBlur={(e) => {
                    if (!e.target.value.trim()) {
                      handleDelete(skill.id);
                    }
                  }}
                />
                <X
                  className="h-3 w-3 ml-2 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(skill.id);
                  }}
                />
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Add new skill */}
      <Card className="p-4 border-dashed border-2 transition-smooth hover:border-primary/50">
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Skills</Label>
            <p className="text-xs text-muted-foreground">
              Add your technical and soft skills. Press Enter or click Add to include each skill.
            </p>
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="JavaScript, React, Communication, etc."
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              className="transition-smooth"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleAdd();
                }
              }}
            />
            <Button
              onClick={handleAdd}
              disabled={!newSkill.trim() || data.some(s => s.skill.toLowerCase() === newSkill.trim().toLowerCase())}
              className="bg-gradient-primary hover:opacity-90 transition-smooth"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Skill
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}