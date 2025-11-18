import { Task, User } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { AlertTriangle, CheckCircle } from 'lucide-react';

interface WorkloadViewProps {
  tasks: Task[];
  users: User[];
  onTaskClick: (task: Task) => void;
}

export function WorkloadView({ tasks, users, onTaskClick }: WorkloadViewProps) {
  const getUserWorkload = (userId: string) => {
    const userTasks = tasks.filter((t) => t.assigneeId === userId);
    const totalTasks = userTasks.length;
    const completedTasks = userTasks.filter((t) => t.status === 'done').length;
    const inProgressTasks = userTasks.filter((t) => t.status === 'in-progress').length;
    const todoTasks = userTasks.filter((t) => t.status === 'todo').length;
    const blockedTasks = userTasks.filter((t) => t.isBlocked).length;
    const overdueTasks = userTasks.filter((t) => new Date(t.dueDate) < new Date() && t.status !== 'done').length;

    const totalStoryPoints = userTasks.reduce((sum, t) => sum + (t.storyPoints || 0), 0);
    const completedStoryPoints = userTasks
      .filter((t) => t.status === 'done')
      .reduce((sum, t) => sum + (t.storyPoints || 0), 0);

    return {
      totalTasks,
      completedTasks,
      inProgressTasks,
      todoTasks,
      blockedTasks,
      overdueTasks,
      totalStoryPoints,
      completedStoryPoints,
      tasks: userTasks,
    };
  };

  const workloadData = users.map((user) => {
    const workload = getUserWorkload(user.id);
    return {
      name: user.name.split(' ')[0],
      fullName: user.name,
      userId: user.id,
      tasks: workload.totalTasks,
      inProgress: workload.inProgressTasks,
      todo: workload.todoTasks,
      completed: workload.completedTasks,
      storyPoints: workload.totalStoryPoints,
    };
  });

  const getCapacityColor = (taskCount: number) => {
    if (taskCount >= 8) return '#ef4444'; // Red - overloaded
    if (taskCount >= 5) return '#f59e0b'; // Yellow - high capacity
    return '#10b981'; // Green - normal
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2>Team Workload</h2>
        <p className="text-gray-600">Capacity planning and task distribution</p>
      </div>

      {/* Workload Chart */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Task Distribution by Team Member</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={workloadData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="completed" stackId="a" fill="#10b981" name="Completed" />
              <Bar dataKey="inProgress" stackId="a" fill="#3b82f6" name="In Progress" />
              <Bar dataKey="todo" stackId="a" fill="#94a3b8" name="To Do" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Team Member Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {users.map((user) => {
          const workload = getUserWorkload(user.id);
          const completionRate =
            workload.totalTasks > 0 ? Math.round((workload.completedTasks / workload.totalTasks) * 100) : 0;

          return (
            <Card key={user.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar>
                      <AvatarFallback>
                        {user.name.split(' ').map((n) => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p>{user.name}</p>
                      <p className="text-sm text-gray-600">{user.email}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge
                      className={
                        workload.totalTasks >= 8
                          ? 'bg-red-100 text-red-800'
                          : workload.totalTasks >= 5
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }
                    >
                      {workload.totalTasks >= 8
                        ? 'High Load'
                        : workload.totalTasks >= 5
                        ? 'Medium Load'
                        : 'Normal'}
                    </Badge>
                    {!user.availability && (
                      <Badge variant="outline" className="bg-gray-100">
                        Unavailable
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <div className="space-y-4">
                  {/* Task Statistics */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="text-center">
                      <p className="text-2xl">{workload.totalTasks}</p>
                      <p className="text-xs text-gray-600">Total</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl text-blue-600">{workload.inProgressTasks}</p>
                      <p className="text-xs text-gray-600">Active</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl text-green-600">{workload.completedTasks}</p>
                      <p className="text-xs text-gray-600">Done</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl text-gray-600">{workload.totalStoryPoints}</p>
                      <p className="text-xs text-gray-600">Points</p>
                    </div>
                  </div>

                  {/* Completion Progress */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">Completion Rate</span>
                      <span className="text-sm">{completionRate}%</span>
                    </div>
                    <Progress value={completionRate} />
                  </div>

                  {/* Alerts */}
                  {(workload.blockedTasks > 0 || workload.overdueTasks > 0) && (
                    <div className="space-y-2">
                      {workload.blockedTasks > 0 && (
                        <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-2 rounded">
                          <AlertTriangle className="w-4 h-4" />
                          <span>{workload.blockedTasks} blocked task(s)</span>
                        </div>
                      )}
                      {workload.overdueTasks > 0 && (
                        <div className="flex items-center gap-2 text-sm text-orange-600 bg-orange-50 p-2 rounded">
                          <AlertTriangle className="w-4 h-4" />
                          <span>{workload.overdueTasks} overdue task(s)</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Task List */}
                  <div>
                    <p className="text-sm mb-2">Active Tasks</p>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {workload.tasks
                        .filter((t) => t.status !== 'done')
                        .slice(0, 5)
                        .map((task) => (
                          <button
                            key={task.id}
                            onClick={() => onTaskClick(task)}
                            className="w-full text-left p-2 border rounded hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-sm truncate flex-1">{task.title}</span>
                              <Badge
                                variant="outline"
                                className={
                                  task.priority === 'high'
                                    ? 'bg-red-100 text-red-800'
                                    : task.priority === 'medium'
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-blue-100 text-blue-800'
                                }
                              >
                                {task.priority}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs text-gray-600">
                                {new Date(task.dueDate).toLocaleDateString()}
                              </span>
                              {task.storyPoints && (
                                <span className="text-xs text-gray-600">{task.storyPoints} pts</span>
                              )}
                            </div>
                          </button>
                        ))}

                      {workload.tasks.filter((t) => t.status !== 'done').length > 5 && (
                        <p className="text-xs text-gray-500 text-center">
                          +{workload.tasks.filter((t) => t.status !== 'done').length - 5} more tasks
                        </p>
                      )}

                      {workload.tasks.filter((t) => t.status !== 'done').length === 0 && (
                        <div className="flex items-center justify-center gap-2 p-4 text-gray-500">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm">All tasks completed!</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
