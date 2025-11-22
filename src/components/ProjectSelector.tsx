import { Project } from '../types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

interface ProjectSelectorProps {
  projects: Project[];
  selectedProjectId: string | null;
  onProjectChange: (projectId: string) => void;
}

export function ProjectSelector({
  projects,
  selectedProjectId,
  onProjectChange,
}: ProjectSelectorProps) {
  const selectedProject = projects.find((p) => p.id === selectedProjectId);

  if (projects.length === 0) {
    return (
      <div className="px-4 py-3">
        <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-500">No projects available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-3">
      <div className="space-y-2">
        <p className="text-xs text-gray-500 uppercase tracking-wider">Current Project</p>
        <Select value={selectedProjectId || undefined} onValueChange={onProjectChange}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a project">
              {selectedProject && (
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: selectedProject.color }}
                  />
                  <span className="truncate">{selectedProject.name}</span>
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
    </div>
  );
}
