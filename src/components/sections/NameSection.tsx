import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Name, UpdateMessage } from '@/types/resume';

interface NameSectionProps {
    data: Name;
    onUpdate: (update: UpdateMessage) => void;
}

export function NameSection({ data, onUpdate }: NameSectionProps) {
    const handleChange = (field: keyof Name, value: string) => {
        onUpdate({
            section: 'name',
            entryId: 'name',
            changeType: 'update',
            content: { ...data, [field]: value }
        });
    };

    return (
        <div className="space-y-4">
            <div>
                <Label className="text-sm font-medium">Full Name</Label>
                <p className="text-xs text-muted-foreground mt-1">
                    Enter your first and last name as you'd like them to appear on your resume.
                </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <Label htmlFor="first-name" className="text-sm font-medium">
                        First Name
                    </Label>
                    <Input
                        id="first-name"
                        placeholder="John"
                        value={data.firstName}
                        onChange={(e) => handleChange('firstName', e.target.value)}
                        className="transition-smooth"
                    />
                </div>
                <div>
                    <Label htmlFor="last-name" className="text-sm font-medium">
                        Last Name
                    </Label>
                    <Input
                        id="last-name"
                        placeholder="Doe"
                        value={data.lastName}
                        onChange={(e) => handleChange('lastName', e.target.value)}
                        className="transition-smooth"
                    />
                </div>
            </div>
        </div>
    );
}
