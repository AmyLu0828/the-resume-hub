import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Contact, UpdateMessage } from '@/types/resume';
import { Plus, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface ContactSectionProps {
  data: Contact[];
  onUpdate: (update: UpdateMessage) => void;
}

const contactTypes = [
  'Email',
  'Phone',
  'LinkedIn',
  'GitHub',
  'Website',
  'Address'
];

export function ContactSection({ data, onUpdate }: ContactSectionProps) {
  const [newContact, setNewContact] = useState<Omit<Contact, 'id'>>({
    type: '',
    value: ''
  });

  const handleAdd = () => {
    if (newContact.type && newContact.value) {
      const contact: Contact = {
        id: `contact_${Date.now()}`,
        ...newContact
      };

      onUpdate({
        section: 'contact',
        entryId: contact.id,
        changeType: 'add',
        content: contact,
        // Do NOT trigger LaTeX on add; use bundled submit button instead
        triggerLatex: false,
      });

      setNewContact({ type: '', value: '' });
    }
  };

  const handleUpdate = (id: string, field: keyof Contact, value: string) => {
    const contact = data.find(c => c.id === id);
    if (contact) {
      const updated = { ...contact, [field]: value };
      onUpdate({
        section: 'contact',
        entryId: id,
        changeType: 'update',
        content: updated,
        triggerLatex: false,
      });
    }
  };

  const handleDelete = (id: string) => {
    onUpdate({
      section: 'contact',
      entryId: id,
      changeType: 'delete',
      content: null,
      // Do NOT trigger LaTeX on delete; use bundled submit button instead
      triggerLatex: false,
    });
  };

  return (
    <div className="space-y-4">
      {/* Existing contacts */}
      {data.map((contact) => (
        <Card key={contact.id} className="p-4 transition-smooth hover:shadow-soft">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <Label className="text-sm font-medium">Type</Label>
              <Select
                value={contact.type}
                onValueChange={(value) => handleUpdate(contact.id, 'type', value)}
              >
                <SelectTrigger className="transition-smooth">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {contactTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-sm font-medium">Value</Label>
              <Input
                value={contact.value}
                onChange={(e) => handleUpdate(contact.id, 'value', e.target.value)}
                placeholder="Enter contact information"
                className="transition-smooth"
              />
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={() => handleDelete(contact.id)}
              className="text-destructive hover:text-destructive-foreground hover:bg-destructive transition-smooth"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </Card>
      ))}

      {/* Add new contact */}
      <Card className="p-4 border-dashed border-2 transition-smooth hover:border-primary/50">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <Label className="text-sm font-medium">Type</Label>
            <Select
              value={newContact.type}
              onValueChange={(value) => setNewContact(prev => ({ ...prev, type: value }))}
            >
              <SelectTrigger className="transition-smooth">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {contactTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label className="text-sm font-medium">Value</Label>
            <Input
              value={newContact.value}
              onChange={(e) => setNewContact(prev => ({ ...prev, value: e.target.value }))}
              placeholder="Enter contact information"
              className="transition-smooth"
            />
          </div>
          <Button
            onClick={handleAdd}
            disabled={!newContact.type || !newContact.value}
            className="bg-gradient-primary hover:opacity-90 transition-smooth"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Contact
          </Button>
        </div>
      </Card>
    </div>
  );
}
