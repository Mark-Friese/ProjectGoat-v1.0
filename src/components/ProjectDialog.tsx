import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Project } from '../types';
import { Calendar } from 'lucide-react';

interface ProjectDialogProps {
  open: boolean;
  onClose: () => void;
  project?: Project;
  onSave: (project: Partial<Project>) => void;
}

const predefinedColors = [
  { name: 'Blue', value: '#3b82f6' },
  { name: 'Purple', value: '#a855f7' },
  { name: 'Pink', value: '#ec4899' },
  { name: 'Red', value: '#ef4444' },
  { name: 'Orange', value: '#f97316' },
  { name: 'Yellow', value: '#eab308' },
  { name: 'Green', value: '#22c55e' },
  { name: 'Teal', value: '#14b8a6' },
  { name: 'Cyan', value: '#06b6d4' },
  { name: 'Indigo', value: '#6366f1' },
];

export function ProjectDialog({ open, onClose, project, onSave }: ProjectDialogProps) {
  const [formData, setFormData] = useState<Partial<Project>>({
    name: '',
    description: '',
    startDate: new Date(),
    endDate: new Date(new Date().setMonth(new Date().getMonth() + 3)), // Default 3 months
    color: predefinedColors[0].value,
  });

  // Sync formData with project prop whenever it changes
  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name,
        description: project.description,
        startDate: project.startDate,
        endDate: project.endDate,
        color: project.color,
      });
    } else {
      // Reset form for new project
      setFormData({
        name: '',
        description: '',
        startDate: new Date(),
        endDate: new Date(new Date().setMonth(new Date().getMonth() + 3)),
        color: predefinedColors[0].value,
      });
    }
  }, [project]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
    onClose();
  };

  const formatDateForInput = (date: Date) => {
    return new Date(date).toISOString().split('T')[0];
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{project ? 'Edit Project' : 'Create New Project'}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            {/* Name */}
            <div>
              <Label htmlFor="name">Project Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter project name..."
                required
              />
            </div>

            {/* Description */}
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Enter project description..."
                rows={3}
              />
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="startDate">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Start Date *
                </Label>
                <Input
                  id="startDate"
                  type="date"
                  value={formatDateForInput(formData.startDate || new Date())}
                  onChange={(e) =>
                    setFormData({ ...formData, startDate: new Date(e.target.value) })
                  }
                  required
                />
              </div>

              <div>
                <Label htmlFor="endDate">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  End Date *
                </Label>
                <Input
                  id="endDate"
                  type="date"
                  value={formatDateForInput(formData.endDate || new Date())}
                  onChange={(e) =>
                    setFormData({ ...formData, endDate: new Date(e.target.value) })
                  }
                  required
                />
              </div>
            </div>

            {/* Color Selection */}
            <div>
              <Label>Project Color *</Label>
              <div className="grid grid-cols-5 gap-3 mt-2">
                {predefinedColors.map((color) => (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, color: color.value })}
                    className={`flex flex-col items-center gap-2 p-3 rounded-lg border-2 transition-all hover:shadow-md ${
                      formData.color === color.value
                        ? 'border-gray-900 shadow-md'
                        : 'border-gray-200'
                    }`}
                  >
                    <div
                      className="w-8 h-8 rounded-full"
                      style={{ backgroundColor: color.value }}
                    />
                    <span className="text-xs text-gray-600">{color.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">{project ? 'Update Project' : 'Create Project'}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
