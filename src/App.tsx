import { useState } from 'react';
import { Task, User, Project, TaskStatus } from './types';
import logo from './assets/logo/project-goat-logo.png';
import { mockTasks, mockUsers, mockProjects, mockRisks, mockIssues } from './data/mockData';
import { DashboardView } from './components/DashboardView';
import { KanbanView } from './components/KanbanView';
import { ListView } from './components/ListView';
import { GanttView } from './components/GanttView';
import { CalendarView } from './components/CalendarView';
import { WorkloadView } from './components/WorkloadView';
import { TeamView } from './components/TeamView';
import { ReportsView } from './components/ReportsView';
import { TaskDialog } from './components/TaskDialog';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import {
  LayoutDashboard,
  KanbanSquare,
  List,
  GanttChartSquare,
  Calendar,
  Users,
  BarChart3,
  Plus,
  Menu,
  X,
} from 'lucide-react';

type View = 'dashboard' | 'kanban' | 'list' | 'gantt' | 'calendar' | 'workload' | 'team' | 'reports';

interface NavigationItem {
  id: View;
  label: string;
  icon: typeof LayoutDashboard;
}

const navigationItems: NavigationItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'kanban', label: 'Kanban Board', icon: KanbanSquare },
  { id: 'list', label: 'Task List', icon: List },
  { id: 'gantt', label: 'Gantt Chart', icon: GanttChartSquare },
  { id: 'calendar', label: 'Calendar', icon: Calendar },
  { id: 'workload', label: 'Team Workload', icon: Users },
  { id: 'team', label: 'Team Members', icon: Users },
  { id: 'reports', label: 'Reports', icon: BarChart3 },
];

export default function App() {
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const [tasks, setTasks] = useState<Task[]>(mockTasks);
  const [users] = useState<User[]>(mockUsers);
  const [projects] = useState<Project[]>(mockProjects);
  const [selectedTask, setSelectedTask] = useState<Task | undefined>();
  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsTaskDialogOpen(true);
  };

  const handleCreateTask = () => {
    setSelectedTask(undefined);
    setIsTaskDialogOpen(true);
  };

  const handleSaveTask = (taskData: Partial<Task>) => {
    if (selectedTask) {
      // Update existing task
      setTasks(tasks.map((t) => (t.id === selectedTask.id ? { ...t, ...taskData } : t)));
    } else {
      // Create new task
      const newTask: Task = {
        id: `t${tasks.length + 1}`,
        title: taskData.title || '',
        description: taskData.description || '',
        status: taskData.status || 'todo',
        priority: taskData.priority || 'medium',
        assigneeId: taskData.assigneeId,
        startDate: taskData.startDate || new Date(),
        dueDate: taskData.dueDate || new Date(),
        progress: taskData.progress || 0,
        tags: taskData.tags || [],
        isBlocked: taskData.isBlocked || false,
        blocker: taskData.blocker,
        isMilestone: taskData.isMilestone || false,
        dependencies: taskData.dependencies || [],
        storyPoints: taskData.storyPoints,
        comments: taskData.comments || [],
        projectId: taskData.projectId || projects[0].id,
      };
      setTasks([...tasks, newTask]);
    }
  };

  const handleTaskStatusChange = (taskId: string, newStatus: TaskStatus) => {
    setTasks(tasks.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t)));
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <DashboardView tasks={tasks} users={users} projects={projects} />;
      case 'kanban':
        return (
          <KanbanView
            tasks={tasks}
            users={users}
            onTaskClick={handleTaskClick}
            onTaskStatusChange={handleTaskStatusChange}
          />
        );
      case 'list':
        return <ListView tasks={tasks} users={users} onTaskClick={handleTaskClick} />;
      case 'gantt':
        return <GanttView tasks={tasks} users={users} onTaskClick={handleTaskClick} />;
      case 'calendar':
        return <CalendarView tasks={tasks} users={users} onTaskClick={handleTaskClick} />;
      case 'workload':
        return <WorkloadView tasks={tasks} users={users} onTaskClick={handleTaskClick} />;
      case 'team':
        return <TeamView users={users} tasks={tasks} />;
      case 'reports':
        return <ReportsView tasks={tasks} users={users} risks={mockRisks} issues={mockIssues} />;
      default:
        return <DashboardView tasks={tasks} users={users} projects={projects} />;
    }
  };

  const blockedTasksCount = tasks.filter((t) => t.isBlocked).length;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r flex flex-col transform transition-transform duration-300 ease-in-out ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b">
          <div className="flex items-center gap-3">
            <img src={logo} alt="ProjectGoat Logo" className="h-10 w-auto" />
            <div className="flex flex-col">
              <span className="text-base font-semibold leading-tight">ProjectGoat</span>
              <span className="text-xs text-gray-500">by TeamGoat</span>
            </div>
          </div>
          <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Project Selector */}
        <div className="px-4 py-4 border-b">
          <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-600">Current Project</p>
            <p className="mt-1">{projects[0].name}</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;

            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentView(item.id);
                  setIsSidebarOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="flex-1 text-left">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Blocked Tasks Alert */}
        {blockedTasksCount > 0 && (
          <div className="p-4 border-t">
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">
                {blockedTasksCount} task{blockedTasksCount !== 1 ? 's' : ''} blocked
              </p>
              <button
                onClick={() => setCurrentView('list')}
                className="text-sm text-red-600 hover:underline mt-1"
              >
                View blocked tasks
              </button>
            </div>
          </div>
        )}

        {/* User Info */}
        <div className="p-4 border-t">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white">
              {users[0].name.split(' ').map((n) => n[0]).join('')}
            </div>
            <div className="flex-1">
              <p className="text-sm">{users[0].name}</p>
              <Badge className="text-xs bg-purple-100 text-purple-800">Admin</Badge>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 bg-white border-b flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-xl">
                {navigationItems.find((item) => item.id === currentView)?.label}
              </h1>
            </div>
          </div>

          <Button onClick={handleCreateTask}>
            <Plus className="w-4 h-4 mr-2" />
            New Task
          </Button>
        </header>

        {/* View Content */}
        <main className="flex-1 overflow-auto">{renderView()}</main>
      </div>

      {/* Task Dialog */}
      <TaskDialog
        open={isTaskDialogOpen}
        onClose={() => setIsTaskDialogOpen(false)}
        task={selectedTask}
        users={users}
        onSave={handleSaveTask}
      />
    </div>
  );
}
