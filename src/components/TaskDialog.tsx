import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Task, Priority, TaskStatus, User, Project } from '../types';
import { Calendar, Clock, Flag, Users, AlertCircle, X, Briefcase } from 'lucide-react';
import { Progress } from './ui/progress';

interface TaskDialogProps {
  open: boolean;
  onClose: () => void;
  task?: Task;
  users: User[];
  projects?: Project[];
  viewMode?: 'project' | 'personal';
  selectedProjectId?: string | null;
  onSave: (task: Partial<Task>) => void;
}

export function TaskDialog({
  open,
  onClose,
  task,
  users,
  projects = [],
  viewMode = 'project',
  selectedProjectId = null,
  onSave
}: TaskDialogProps) {
  const [formData, setFormData] = useState<Partial<Task>>({
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    progress: 0,
    tags: [],
    isBlocked: false,
    isMilestone: false,
    dependencies: [],
    comments: [],
    projectId: selectedProjectId || undefined,
  });

  // Sync formData with task prop whenever it changes
  useEffect(() => {
    if (task) {
      // Editing existing task - populate with task data
      setFormData(task);
    } else {
      // Creating new task - reset to empty defaults
      setFormData({
        title: '',
        description: '',
        status: 'todo',
        priority: 'medium',
        progress: 0,
        tags: [],
        isBlocked: false,
        isMilestone: false,
        dependencies: [],
        comments: [],
        projectId: selectedProjectId || undefined,
      });
    }
  }, [task, selectedProjectId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
    onClose();
  };

  const priorityColors = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{task ? 'Edit Task' : 'Create New Task'}</DialogTitle>
          <DialogDescription>
            {task ? 'Update task details and track progress.' : 'Create a new task and assign it to team members.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Task Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Enter task title..."
              required
            />
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Enter task description..."
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="status">Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value: TaskStatus) => setFormData({ ...formData, status: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todo">To Do</SelectItem>
                  <SelectItem value="in-progress">In Progress</SelectItem>
                  <SelectItem value="review">Review</SelectItem>
                  <SelectItem value="done">Done</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="priority">Priority</Label>
              <Select
                value={formData.priority}
                onValueChange={(value: Priority) => setFormData({ ...formData, priority: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="startDate">Start Date</Label>
              <Input
                id="startDate"
                type="date"
                value={formData.startDate?.toISOString().split('T')[0] || ''}
                onChange={(e) => setFormData({ ...formData, startDate: new Date(e.target.value) })}
              />
            </div>

            <div>
              <Label htmlFor="dueDate">Due Date</Label>
              <Input
                id="dueDate"
                type="date"
                value={formData.dueDate?.toISOString().split('T')[0] || ''}
                onChange={(e) => setFormData({ ...formData, dueDate: new Date(e.target.value) })}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="assignee">Assignee</Label>
            <Select
              value={formData.assigneeId}
              onValueChange={(value) => setFormData({ ...formData, assigneeId: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select assignee..." />
              </SelectTrigger>
              <SelectContent>
                {users.map((user) => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="project">
              Project
              {viewMode === 'project' && (
                <span className="text-xs text-gray-500 ml-2">(locked to current project)</span>
              )}
            </Label>
            <Select
              value={formData.projectId}
              onValueChange={(value) => setFormData({ ...formData, projectId: value })}
              disabled={viewMode === 'project'}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select project...">
                  {formData.projectId && projects.find(p => p.id === formData.projectId) && (
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: projects.find(p => p.id === formData.projectId)?.color }}
                      />
                      <span>{projects.find(p => p.id === formData.projectId)?.name}</span>
                    </div>
                  )}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {projects.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: project.color }}
                      />
                      <span>{project.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="progress">Progress (%)</Label>
            <div className="flex items-center gap-4">
              <Input
                id="progress"
                type="number"
                min="0"
                max="100"
                value={formData.progress}
                onChange={(e) => setFormData({ ...formData, progress: parseInt(e.target.value) || 0 })}
                className="w-24"
              />
              <Progress value={formData.progress || 0} className="flex-1" />
            </div>
          </div>

          <div>
            <Label htmlFor="storyPoints">Story Points (Optional)</Label>
            <Input
              id="storyPoints"
              type="number"
              min="0"
              value={formData.storyPoints || ''}
              onChange={(e) => setFormData({ ...formData, storyPoints: parseInt(e.target.value) || undefined })}
              placeholder="Enter story points..."
              className="w-32"
            />
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.isMilestone}
                onChange={(e) => setFormData({ ...formData, isMilestone: e.target.checked })}
                className="rounded"
              />
              <span>Milestone</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.isBlocked}
                onChange={(e) => setFormData({ ...formData, isBlocked: e.target.checked })}
                className="rounded"
              />
              <span>Blocked</span>
            </label>
          </div>

          {formData.isBlocked && (
            <div>
              <Label htmlFor="blockerDesc">Blocker Description</Label>
              <Textarea
                id="blockerDesc"
                value={formData.blocker?.description || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    blocker: { description: e.target.value, createdAt: new Date() },
                  })
                }
                placeholder="Describe what is blocking this task..."
                rows={2}
              />
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              {task ? 'Save Changes' : 'Create Task'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
