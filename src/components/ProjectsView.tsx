import { useState } from 'react';
import { Project, Task } from '../types';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ProjectDialog } from './ProjectDialog';
import { Calendar, Edit, CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface ProjectsViewProps {
  projects: Project[];
  tasks: Task[];
  onProjectUpdate: (project: Project) => void;
  onProjectCreate: (project: Partial<Project>) => void;
}

export function ProjectsView({
  projects,
  tasks,
  onProjectUpdate,
  onProjectCreate,
}: ProjectsViewProps) {
  const [selectedProject, setSelectedProject] = useState<Project | undefined>();
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleCreateProject = () => {
    setSelectedProject(undefined);
    setIsDialogOpen(true);
  };

  const handleEditProject = (project: Project) => {
    setSelectedProject(project);
    setIsDialogOpen(true);
  };

  const handleSaveProject = (projectData: Partial<Project>) => {
    if (selectedProject) {
      onProjectUpdate({ ...selectedProject, ...projectData });
    } else {
      onProjectCreate(projectData);
    }
    setIsDialogOpen(false);
  };

  const getProjectStats = (projectId: string) => {
    const projectTasks = tasks.filter((task) => task.projectId === projectId);
    const completed = projectTasks.filter((task) => task.status === 'done').length;
    const inProgress = projectTasks.filter((task) => task.status === 'in-progress').length;
    const blocked = projectTasks.filter((task) => task.isBlocked).length;

    return {
      total: projectTasks.length,
      completed,
      inProgress,
      blocked,
      completionRate: projectTasks.length > 0 ? Math.round((completed / projectTasks.length) * 100) : 0,
    };
  };

  const isProjectOverdue = (project: Project) => {
    return new Date(project.endDate) < new Date();
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Projects</h2>
          <p className="text-gray-600">Manage and track all your projects</p>
        </div>
        <Button onClick={handleCreateProject}>Create New Project</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => {
          const stats = getProjectStats(project.id);
          const overdue = isProjectOverdue(project);

          return (
            <Card key={project.id} className="p-6 hover:shadow-lg transition-shadow">
              {/* Project Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3 flex-1">
                  <div
                    className="w-4 h-4 rounded-full flex-shrink-0"
                    style={{ backgroundColor: project.color }}
                  />
                  <h3 className="text-lg font-semibold truncate">{project.name}</h3>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditProject(project)}
                >
                  <Edit className="w-4 h-4" />
                </Button>
              </div>

              {/* Description */}
              <p className="text-sm text-gray-600 mb-4 line-clamp-2 min-h-[2.5rem]">
                {project.description || 'No description provided'}
              </p>

              {/* Date Range */}
              <div className="mb-4 space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">
                    {new Date(project.startDate).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                    {' - '}
                    {new Date(project.endDate).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </span>
                </div>
                {overdue && (
                  <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50">
                    Overdue
                  </Badge>
                )}
              </div>

              {/* Task Stats */}
              <div className="space-y-3 mb-4 pb-4 border-b">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Total Tasks</span>
                  <span className="font-semibold">{stats.total}</span>
                </div>

                {/* Progress Bar */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-semibold">{stats.completionRate}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${stats.completionRate}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Task Status Badges */}
              <div className="flex flex-wrap gap-2">
                {stats.completed > 0 && (
                  <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    {stats.completed} Done
                  </Badge>
                )}
                {stats.inProgress > 0 && (
                  <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50">
                    <Clock className="w-3 h-3 mr-1" />
                    {stats.inProgress} In Progress
                  </Badge>
                )}
                {stats.blocked > 0 && (
                  <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    {stats.blocked} Blocked
                  </Badge>
                )}
              </div>
            </Card>
          );
        })}

        {projects.length === 0 && (
          <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
            <div className="text-gray-400 text-5xl mb-4">📁</div>
            <h3 className="text-xl font-semibold mb-2">No projects yet</h3>
            <p className="text-gray-600 mb-4">Get started by creating your first project</p>
            <Button onClick={handleCreateProject}>Create New Project</Button>
          </div>
        )}
      </div>

      {/* Project Dialog */}
      <ProjectDialog
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        project={selectedProject}
        onSave={handleSaveProject}
      />
    </div>
  );
}
