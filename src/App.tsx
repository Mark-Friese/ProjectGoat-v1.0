import { useState, useEffect } from 'react';
import { Task, User, Project, TaskStatus, Risk, Issue, Team } from './types';
import logo from './assets/logo/project-goat-logo.svg';
import * as taskService from './services/tasks';
import * as userService from './services/users';
import * as projectService from './services/projects';
import * as riskService from './services/risks';
import * as issueService from './services/issues';
import * as authService from './services/auth';
import { LoginScreen } from './components/LoginScreen';
import { RegistrationScreen } from './components/RegistrationScreen';
import { InvitationAcceptScreen } from './components/InvitationAcceptScreen';
import { ChangePasswordDialog } from './components/ChangePasswordDialog';
import { SessionTimeoutDialog } from './components/SessionTimeoutDialog';
import { sessionMonitor } from './utils/session-monitor';
import { DashboardView } from './components/DashboardView';
import { KanbanView } from './components/KanbanView';
import { ListView } from './components/ListView';
import { GanttView } from './components/GanttView';
import { CalendarView } from './components/CalendarView';
import { WorkloadView } from './components/WorkloadView';
import { TeamView } from './components/TeamView';
import { ReportsView } from './components/ReportsView';
import { ProfileView } from './components/ProfileView';
import { ProjectsView } from './components/ProjectsView';
import { TeamSettingsView } from './components/TeamSettingsView';
import { TeamSwitcher } from './components/TeamSwitcher';
import { TaskDialog } from './components/TaskDialog';
import { ViewModeToggle } from './components/ViewModeToggle';
import { ProjectSelector } from './components/ProjectSelector';
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
  LogOut,
  KeyRound,
  UserCircle,
  Briefcase,
  Settings,
} from 'lucide-react';

type View = 'dashboard' | 'kanban' | 'list' | 'gantt' | 'calendar' | 'workload' | 'team' | 'reports' | 'profile' | 'projects' | 'team-settings';
type AuthScreen = 'login' | 'register' | 'invitation';

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
  { id: 'projects', label: 'Projects', icon: Briefcase },
  { id: 'workload', label: 'Team Workload', icon: Users },
  { id: 'team', label: 'Team Members', icon: Users },
  { id: 'reports', label: 'Reports', icon: BarChart3 },
  { id: 'profile', label: 'My Profile', icon: UserCircle },
  { id: 'team-settings', label: 'Team Settings', icon: Settings },
];

export default function App() {
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [risks, setRisks] = useState<Risk[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [currentTeam, setCurrentTeam] = useState<Team | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authScreen, setAuthScreen] = useState<AuthScreen>('login');
  const [invitationToken, setInvitationToken] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | undefined>();
  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false);
  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState(false);
  const [isTimeoutWarningOpen, setIsTimeoutWarningOpen] = useState(false);
  const [timeoutSecondsRemaining, setTimeoutSecondsRemaining] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // View mode state for dual-perspective (Project vs Personal view)
  const [viewMode, setViewMode] = useState<'project' | 'personal'>('project');
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  // Check URL for invitation token on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const invite = urlParams.get('invite');
    if (invite) {
      setInvitationToken(invite);
      setAuthScreen('invitation');
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  // Check for session and fetch initial data
  useEffect(() => {
    const initializeApp = async () => {
      // Skip initialization if showing invitation screen
      if (authScreen === 'invitation' && invitationToken) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);

        // Check for existing session
        const sessionResponse = await authService.checkSession();

        if (sessionResponse.authenticated && sessionResponse.user) {
          // User is authenticated
          setCurrentUser(sessionResponse.user);
          setCurrentTeam(sessionResponse.team || null);
          setTeams(sessionResponse.teams || []);
          setIsAuthenticated(true);

          // Start session monitoring
          sessionMonitor.start(
            (timeRemaining) => {
              // Show timeout warning
              setTimeoutSecondsRemaining(timeRemaining);
              setIsTimeoutWarningOpen(true);
            },
            () => {
              // Session expired - auto logout
              handleSessionExpired();
            }
          );

          // Fetch all data
          const [tasksData, usersData, projectsData, risksData, issuesData] = await Promise.all([
            taskService.getTasks(),
            userService.getUsers(),
            projectService.getProjects(),
            riskService.getRisks(),
            issueService.getIssues(),
          ]);

          setTasks(tasksData);
          setUsers(usersData);
          setProjects(projectsData);
          setRisks(risksData);
          setIssues(issuesData);
        } else {
          // Not authenticated - show login screen
          setIsAuthenticated(false);
        }
      } catch (err) {
        console.error('Failed to initialize app:', err);
        setError('Failed to load data from server. Please ensure the backend is running.');
      } finally {
        setIsLoading(false);
      }
    };

    initializeApp();
  }, [authScreen, invitationToken]);

  // Load view mode and selected project from localStorage on mount
  useEffect(() => {
    const savedViewMode = localStorage.getItem('viewMode');
    const savedProjectId = localStorage.getItem('selectedProjectId');

    if (savedViewMode && (savedViewMode === 'project' || savedViewMode === 'personal')) {
      setViewMode(savedViewMode as 'project' | 'personal');
    }

    if (savedProjectId) {
      setSelectedProjectId(savedProjectId);
    }
  }, []);

  // Initialize selectedProjectId to first project when projects are loaded
  useEffect(() => {
    if (projects.length > 0 && !selectedProjectId) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  // Save view mode to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('viewMode', viewMode);
  }, [viewMode]);

  // Save selected project to localStorage when it changes
  useEffect(() => {
    if (selectedProjectId) {
      localStorage.setItem('selectedProjectId', selectedProjectId);
    }
  }, [selectedProjectId]);

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsTaskDialogOpen(true);
  };

  const handleCreateTask = () => {
    setSelectedTask(undefined);
    setIsTaskDialogOpen(true);
  };

  const handleSaveTask = async (taskData: Partial<Task>) => {
    try {
      if (selectedTask) {
        // Update existing task
        const updatedTask = await taskService.updateTask(selectedTask.id, taskData);
        setTasks(tasks.map((t) => (t.id === selectedTask.id ? updatedTask : t)));
      } else {
        // Create new task
        // For projectId, prioritize: user selection > current project > first project
        const defaultProjectId = taskData.projectId || selectedProjectId || projects[0]?.id;

        if (!defaultProjectId) {
          alert('Please select a project before creating a task.');
          return;
        }

        const newTaskData: Partial<Task> = {
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
          isMilestone: taskData.isMilestone || false,
          dependencies: taskData.dependencies || [],
          storyPoints: taskData.storyPoints,
          projectId: defaultProjectId,
        };
        const createdTask = await taskService.createTask(newTaskData);
        setTasks([...tasks, createdTask]);
      }
    } catch (err) {
      console.error('Failed to save task:', err);
      alert('Failed to save task. Please try again.');
    }
  };

  const handleTaskStatusChange = async (taskId: string, newStatus: TaskStatus) => {
    try {
      const updatedTask = await taskService.updateTaskStatus(taskId, newStatus);
      setTasks(tasks.map((t: Task) => (t.id === taskId ? updatedTask : t)));
    } catch (err) {
      console.error('Failed to update task status:', err);
      alert('Failed to update task status. Please try again.');
    }
  };

  const handleUserUpdate = (updatedUser: User) => {
    setUsers(users.map((u) => (u.id === updatedUser.id ? updatedUser : u)));

    // Update current user if it's the same user
    if (currentUser && updatedUser.id === currentUser.id) {
      setCurrentUser(updatedUser);
    }
  };

  const handleProjectCreate = async (projectData: Partial<Project>) => {
    try {
      const createdProject = await projectService.createProject(projectData);
      setProjects([...projects, createdProject]);

      // If this is the first project and no project is selected, select it
      if (projects.length === 0) {
        setSelectedProjectId(createdProject.id);
      }
    } catch (err) {
      console.error('Failed to create project:', err);
      alert('Failed to create project. Please try again.');
    }
  };

  const handleProjectUpdate = async (updatedProject: Project) => {
    try {
      const updated = await projectService.updateProject(updatedProject.id, updatedProject);
      setProjects(projects.map((p) => (p.id === updatedProject.id ? updated : p)));
    } catch (err) {
      console.error('Failed to update project:', err);
      alert('Failed to update project. Please try again.');
    }
  };

  const handleTeamUpdate = (updatedTeam: Team) => {
    setCurrentTeam(updatedTeam);
    setTeams(teams.map((t) => (t.id === updatedTeam.id ? updatedTeam : t)));
  };

  const handleTeamSwitch = async (team: Team) => {
    setCurrentTeam(team);
    setIsLoading(true);

    try {
      // Refetch all data for the new team
      const [tasksData, usersData, projectsData, risksData, issuesData] = await Promise.all([
        taskService.getTasks(),
        userService.getUsers(),
        projectService.getProjects(),
        riskService.getRisks(),
        issueService.getIssues(),
      ]);

      setTasks(tasksData);
      setUsers(usersData);
      setProjects(projectsData);
      setRisks(risksData);
      setIssues(issuesData);

      // Reset selected project
      if (projectsData.length > 0) {
        setSelectedProjectId(projectsData[0].id);
      } else {
        setSelectedProjectId(null);
      }
    } catch (err) {
      console.error('Failed to load team data:', err);
      alert('Failed to load team data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = async (user: User) => {
    // Set authentication state immediately to trigger UI update
    setCurrentUser(user);
    setIsAuthenticated(true);
    setIsLoading(true); // Show loading state while fetching data

    // Start session monitoring
    sessionMonitor.start(
      (timeRemaining) => {
        // Show timeout warning
        setTimeoutSecondsRemaining(timeRemaining);
        setIsTimeoutWarningOpen(true);
      },
      () => {
        // Session expired - auto logout
        handleSessionExpired();
      }
    );

    // Fetch session info to get team data, then fetch all data
    try {
      const sessionResponse = await authService.checkSession();
      if (sessionResponse.team) {
        setCurrentTeam(sessionResponse.team);
      }
      if (sessionResponse.teams) {
        setTeams(sessionResponse.teams);
      }

      const [tasksData, usersData, projectsData, risksData, issuesData] = await Promise.all([
        taskService.getTasks(),
        userService.getUsers(),
        projectService.getProjects(),
        riskService.getRisks(),
        issueService.getIssues(),
      ]);

      setTasks(tasksData);
      setUsers(usersData);
      setProjects(projectsData);
      setRisks(risksData);
      setIssues(issuesData);
    } catch (err) {
      console.error('Failed to fetch data after login:', err);
      setError('Failed to load data. Please refresh the page.');
    } finally {
      setIsLoading(false); // Hide loading state when done
    }
  };

  const handleRegistrationSuccess = async (user: User, team: Team) => {
    setCurrentUser(user);
    setCurrentTeam(team);
    setTeams([team]);
    setIsAuthenticated(true);
    setAuthScreen('login');
    setIsLoading(true);

    // Start session monitoring
    sessionMonitor.start(
      (timeRemaining) => {
        setTimeoutSecondsRemaining(timeRemaining);
        setIsTimeoutWarningOpen(true);
      },
      () => {
        handleSessionExpired();
      }
    );

    // Fetch initial data (will be empty for new team)
    try {
      const [tasksData, usersData, projectsData, risksData, issuesData] = await Promise.all([
        taskService.getTasks(),
        userService.getUsers(),
        projectService.getProjects(),
        riskService.getRisks(),
        issueService.getIssues(),
      ]);

      setTasks(tasksData);
      setUsers(usersData);
      setProjects(projectsData);
      setRisks(risksData);
      setIssues(issuesData);
    } catch (err) {
      console.error('Failed to fetch data after registration:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInvitationSuccess = async (user: User, team: Team) => {
    setCurrentUser(user);
    setCurrentTeam(team);
    setTeams([team]); // Will be updated by checkSession
    setIsAuthenticated(true);
    setAuthScreen('login');
    setInvitationToken(null);
    setIsLoading(true);

    // Start session monitoring
    sessionMonitor.start(
      (timeRemaining) => {
        setTimeoutSecondsRemaining(timeRemaining);
        setIsTimeoutWarningOpen(true);
      },
      () => {
        handleSessionExpired();
      }
    );

    // Fetch data and update teams list
    try {
      const sessionResponse = await authService.checkSession();
      if (sessionResponse.teams) {
        setTeams(sessionResponse.teams);
      }

      const [tasksData, usersData, projectsData, risksData, issuesData] = await Promise.all([
        taskService.getTasks(),
        userService.getUsers(),
        projectService.getProjects(),
        riskService.getRisks(),
        issueService.getIssues(),
      ]);

      setTasks(tasksData);
      setUsers(usersData);
      setProjects(projectsData);
      setRisks(risksData);
      setIssues(issuesData);
    } catch (err) {
      console.error('Failed to fetch data after invitation accept:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    // Stop session monitoring
    sessionMonitor.stop();

    await authService.logout();
    setCurrentUser(null);
    setCurrentTeam(null);
    setTeams([]);
    setIsAuthenticated(false);
    setIsTimeoutWarningOpen(false);
    setTasks([]);
    setUsers([]);
    setProjects([]);
    setRisks([]);
    setIssues([]);
    setAuthScreen('login');
  };

  const handleSessionExpired = async () => {
    // Session expired - clean logout without API call
    sessionMonitor.stop();
    setCurrentUser(null);
    setCurrentTeam(null);
    setTeams([]);
    setIsAuthenticated(false);
    setIsTimeoutWarningOpen(false);
    setTasks([]);
    setUsers([]);
    setProjects([]);
    setRisks([]);
    setIssues([]);

    // Clear stored session data
    localStorage.removeItem('sessionId');
    localStorage.removeItem('csrfToken');
  };

  const handleExtendSession = () => {
    // Extend session
    sessionMonitor.extendSession();
    setIsTimeoutWarningOpen(false);
  };

  // Filter tasks based on view mode
  const getFilteredTasks = () => {
    if (viewMode === 'personal' && currentUser) {
      // Personal view: Show only current user's tasks across all projects
      return tasks.filter(task => task.assigneeId === currentUser.id);
    } else if (viewMode === 'project' && selectedProjectId) {
      // Project view: Show all tasks for selected project
      return tasks.filter(task => task.projectId === selectedProjectId);
    }
    // Fallback: show all tasks
    return tasks;
  };

  const filteredTasks = getFilteredTasks();

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <DashboardView tasks={filteredTasks} users={users} projects={projects} />;
      case 'kanban':
        return (
          <KanbanView
            tasks={filteredTasks}
            users={users}
            projects={projects}
            viewMode={viewMode}
            onTaskClick={handleTaskClick}
            onTaskStatusChange={handleTaskStatusChange}
          />
        );
      case 'list':
        return <ListView tasks={filteredTasks} users={users} onTaskClick={handleTaskClick} />;
      case 'gantt':
        return <GanttView tasks={filteredTasks} users={users} onTaskClick={handleTaskClick} />;
      case 'calendar':
        return <CalendarView tasks={filteredTasks} users={users} onTaskClick={handleTaskClick} />;
      case 'projects':
        return (
          <ProjectsView
            projects={projects}
            tasks={tasks}
            onProjectUpdate={handleProjectUpdate}
            onProjectCreate={handleProjectCreate}
          />
        );
      case 'workload':
        return <WorkloadView tasks={filteredTasks} users={users} onTaskClick={handleTaskClick} />;
      case 'team':
        return <TeamView users={users} tasks={filteredTasks} onUserUpdate={handleUserUpdate} />;
      case 'reports':
        return <ReportsView tasks={filteredTasks} users={users} risks={risks} issues={issues} />;
      case 'profile':
        return currentUser ? (
          <ProfileView
            currentUser={currentUser}
            onPasswordChangeClick={() => setIsChangePasswordOpen(true)}
            onProfileUpdate={handleUserUpdate}
          />
        ) : null;
      case 'team-settings':
        return currentTeam && currentUser ? (
          <TeamSettingsView
            team={currentTeam}
            currentUser={currentUser}
            onTeamUpdate={handleTeamUpdate}
          />
        ) : null;
      default:
        return <DashboardView tasks={filteredTasks} users={users} projects={projects} />;
    }
  };

  const blockedTasksCount = filteredTasks.filter((t: Task) => t.isBlocked).length;

  // Show loading state
  if (isLoading && !invitationToken) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading ProjectGoat...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !invitationToken) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="max-w-md text-center p-6 bg-white rounded-lg shadow-lg">
          <div className="text-red-500 text-5xl mb-4">&#9888;</div>
          <h2 className="text-xl font-semibold mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  // Show auth screens if not authenticated
  if (!isAuthenticated) {
    if (authScreen === 'invitation' && invitationToken) {
      return (
        <InvitationAcceptScreen
          token={invitationToken}
          onAcceptSuccess={handleInvitationSuccess}
          onBackToLogin={() => {
            setInvitationToken(null);
            setAuthScreen('login');
          }}
        />
      );
    }

    if (authScreen === 'register') {
      return (
        <RegistrationScreen
          onRegistrationSuccess={handleRegistrationSuccess}
          onBackToLogin={() => setAuthScreen('login')}
        />
      );
    }

    return (
      <LoginScreen
        onLoginSuccess={handleLoginSuccess}
        onRegisterClick={() => setAuthScreen('register')}
      />
    );
  }

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

        {/* Team Switcher */}
        {currentTeam && (
          <TeamSwitcher
            currentTeam={currentTeam}
            teams={teams}
            onTeamSwitch={handleTeamSwitch}
            onTeamSettingsClick={() => {
              setCurrentView('team-settings');
              setIsSidebarOpen(false);
            }}
          />
        )}

        {/* View Mode Toggle */}
        <ViewModeToggle viewMode={viewMode} onViewModeChange={setViewMode} />

        {/* Project Selector (Project View) or Personal Label (Personal View) */}
        {viewMode === 'project' ? (
          <ProjectSelector
            projects={projects}
            selectedProjectId={selectedProjectId}
            onProjectChange={setSelectedProjectId}
          />
        ) : (
          <div className="px-4 py-3 border-b">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold">
                {currentUser?.name.split(' ').map((n) => n[0]).join('') || '?'}
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">My Tasks</p>
                <p className="text-sm font-medium">{currentUser?.name || 'Personal View'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          {navigationItems
            .filter((item) => item.id !== 'team-settings') // Team settings is accessed via TeamSwitcher
            .map((item) => {
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
        {currentUser && (
          <div className="p-4 border-t">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white">
                {currentUser.name.split(' ').map((n) => n[0]).join('')}
              </div>
              <div className="flex-1">
                <p className="text-sm">{currentUser.name}</p>
                <Badge
                  className={`text-xs ${
                    currentUser.role === 'admin'
                      ? 'bg-purple-100 text-purple-800'
                      : currentUser.role === 'member'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1)}
                </Badge>
              </div>
            </div>
            <div className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => setIsChangePasswordOpen(true)}
              >
                <KeyRound className="w-4 h-4 mr-2" />
                Change Password
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        )}
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

          {currentView !== 'team-settings' && (
            <Button onClick={handleCreateTask}>
              <Plus className="w-4 h-4 mr-2" />
              New Task
            </Button>
          )}
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
        projects={projects}
        viewMode={viewMode}
        selectedProjectId={selectedProjectId}
        onSave={handleSaveTask}
      />

      {/* Change Password Dialog */}
      <ChangePasswordDialog
        open={isChangePasswordOpen}
        onOpenChange={setIsChangePasswordOpen}
      />

      {/* Session Timeout Warning Dialog */}
      <SessionTimeoutDialog
        open={isTimeoutWarningOpen}
        timeRemaining={timeoutSecondsRemaining}
        onExtendSession={handleExtendSession}
        onLogout={handleLogout}
      />
    </div>
  );
}
