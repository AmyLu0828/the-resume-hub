import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { AboutMe, UpdateMessage } from '@/types/resume';
import { Sparkles, RotateCcw } from 'lucide-react';
import { useState, useEffect } from 'react';

interface AboutMeSectionProps {
  data: AboutMe;
  onUpdate: (update: UpdateMessage) => void;
  onPolish: (section: string, entryId: string, content: any) => void;
  isPolishing?: boolean;
}

export function AboutMeSection({ data, onUpdate, onPolish, isPolishing }: AboutMeSectionProps) {
  const [showPolished, setShowPolished] = useState(false);

  // Automatically show polished text when it becomes available
  useEffect(() => {
    if (data.polishedDescription && data.polishedDescription.trim().length > 0) {
      setShowPolished(false);
    }
  }, [data.polishedDescription]);

  const handleChange = (description: string) => {
    onUpdate({
      section: 'aboutMe',
      entryId: 'about',
      changeType: 'update',
      content: {
        description,
        polishedDescription: data.polishedDescription
      },
      triggerLatex: false,
    });
  };

  const handleSubmit = () => {
    onUpdate({
      section: 'aboutMe',
      entryId: 'about',
      changeType: 'update',
      content: {
        description: data.description,
        polishedDescription: data.polishedDescription
      },
      triggerLatex: true,
    });
  };

  const handlePolish = () => {
    onPolish('aboutMe', 'about', data);
  };

  const handleUsePolished = () => {
    if (data.polishedDescription) {
      onUpdate({
        section: 'aboutMe',
        entryId: 'about',
        changeType: 'update',
        content: {
          description: data.polishedDescription,
          polishedDescription: data.polishedDescription
        }
      });
      setShowPolished(true);
    }
  };

  const handleRevert = () => {
    setShowPolished(false);
  };

  const currentDescription = showPolished && data.polishedDescription
    ? data.polishedDescription
    : data.description;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <Label htmlFor="about-description" className="text-sm font-medium">
            About Me
          </Label>
          <p className="text-xs text-muted-foreground mt-1">
            Write a brief description about yourself, your goals, and what makes you unique.
          </p>
        </div>
        <div className="flex gap-2">
          {data.polishedDescription && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRevert}
                disabled={!showPolished}
                className="text-xs"
              >
                <RotateCcw className="h-3 w-3 mr-1" />
                Original
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleUsePolished}
                disabled={showPolished}
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
            onClick={handlePolish}
            disabled={isPolishing || !data.description.trim()}
            className="text-xs"
          >
            {isPolishing ? (
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
            variant="default"
            size="sm"
            onClick={handleSubmit}
            disabled={!data.description.trim()}
            className="text-xs"
          >
            Submit About Me
          </Button>
        </div>
      </div>

      <Textarea
        id="about-description"
        placeholder="I am a passionate professional with expertise in..."
        value={currentDescription}
        onChange={(e) => handleChange(e.target.value)}
        className="min-h-[120px] resize-none transition-smooth"
        rows={5}
      />

      {data.polishedDescription && (
        <div className="text-xs text-muted-foreground">
          {showPolished ? (
            <span className="text-blue-600">Showing AI-polished version</span>
          ) : (
            <span>AI-polished version available - click "Use Polished" to apply</span>
          )}
        </div>
      )}
    </div>
  );
}