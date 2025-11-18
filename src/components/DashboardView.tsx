import { Task, User, Project } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { AlertCircle, CheckCircle, Clock, TrendingUp, Users, Calendar } from 'lucide-react';

interface DashboardViewProps {
  tasks: Task[];
  users: User[];
  projects: Project[];
}

export function DashboardView({ tasks, users, projects }: DashboardViewProps) {
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.status === 'done').length;
  const inProgressTasks = tasks.filter((t) => t.status === 'in-progress').length;
  const blockedTasks = tasks.filter((t) => t.isBlocked).length;
  const overdueTasks = tasks.filter((t) => new Date(t.dueDate) < new Date() && t.status !== 'done').length;

  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const statusData = [
    { name: 'To Do', value: tasks.filter((t) => t.status === 'todo').length, color: '#94a3b8' },
    { name: 'In Progress', value: inProgressTasks, color: '#3b82f6' },
    { name: 'Review', value: tasks.filter((t) => t.status === 'review').length, color: '#f59e0b' },
    { name: 'Done', value: completedTasks, color: '#10b981' },
  ];

  const tasksByAssignee = users.map((user) => ({
    name: user.name.split(' ')[0],
    tasks: tasks.filter((t) => t.assigneeId === user.id).length,
    completed: tasks.filter((t) => t.assigneeId === user.id && t.status === 'done').length,
  }));

  const priorityData = [
    { name: 'High', value: tasks.filter((t) => t.priority === 'high').length },
    { name: 'Medium', value: tasks.filter((t) => t.priority === 'medium').length },
    { name: 'Low', value: tasks.filter((t) => t.priority === 'low').length },
  ];

  const upcomingMilestones = tasks
    .filter((t) => t.isMilestone && t.status !== 'done')
    .sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime())
    .slice(0, 3);

  const recentActivity = tasks
    .filter((t) => t.comments.length > 0)
    .flatMap((t) => t.comments.map((c) => ({ ...c, task: t })))
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 5);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2>Project Dashboard</h2>
        <p className="text-gray-600">Overview of all projects and team activity</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Total Tasks</p>
                <p className="text-3xl mt-2">{totalTasks}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Completion Rate</p>
                <p className="text-3xl mt-2">{completionRate}%</p>
              </div>
              <TrendingUp className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Overdue</p>
                <p className="text-3xl mt-2">{overdueTasks}</p>
              </div>
              <Clock className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Blocked</p>
                <p className="text-3xl mt-2">{blockedTasks}</p>
              </div>
              <AlertCircle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Task Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tasks by Team Member</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tasksByAssignee}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="tasks" fill="#3b82f6" name="Total Tasks" />
                <Bar dataKey="completed" fill="#10b981" name="Completed" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Priority Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={priorityData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" />
                <Tooltip />
                <Bar dataKey="value" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Upcoming Milestones</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {upcomingMilestones.length === 0 ? (
                <p className="text-gray-500">No upcoming milestones</p>
              ) : (
                upcomingMilestones.map((milestone) => (
                  <div key={milestone.id} className="flex items-start gap-3 p-3 border rounded-lg">
                    <Calendar className="w-5 h-5 text-blue-500 mt-0.5" />
                    <div className="flex-1">
                      <p>{milestone.title}</p>
                      <p className="text-sm text-gray-600">
                        Due: {new Date(milestone.dueDate).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Blocked Tasks Alert */}
      {blockedTasks > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              Blocked Tasks Requiring Attention
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {tasks
                .filter((t) => t.isBlocked)
                .map((task) => {
                  const assignee = users.find((u) => u.id === task.assigneeId);
                  const blockedDays = task.blocker
                    ? Math.floor((new Date().getTime() - new Date(task.blocker.createdAt).getTime()) / (1000 * 60 * 60 * 24))
                    : 0;

                  return (
                    <div key={task.id} className="flex items-start gap-3 p-3 bg-white border border-red-200 rounded-lg">
                      <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                      <div className="flex-1">
                        <p>{task.title}</p>
                        <p className="text-sm text-gray-600 mt-1">{task.blocker?.description}</p>
                        <div className="flex items-center gap-3 mt-2">
                          <span className="text-sm text-gray-500">Assignee: {assignee?.name}</span>
                          <span className="text-sm text-red-600">Blocked for {blockedDays} days</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentActivity.length === 0 ? (
              <p className="text-gray-500">No recent activity</p>
            ) : (
              recentActivity.map((activity, index) => {
                const user = users.find((u) => u.id === activity.userId);
                return (
                  <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                      {user?.name.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">
                        <span>{user?.name}</span> commented on{' '}
                        <span>{activity.task.title}</span>
                      </p>
                      <p className="text-sm text-gray-600 mt-1">{activity.text}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(activity.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
