import { Task, User, Risk, Issue } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Download, AlertTriangle, TrendingUp, FileText } from 'lucide-react';

interface ReportsViewProps {
  tasks: Task[];
  users: User[];
  risks: Risk[];
  issues: Issue[];
}

export function ReportsView({ tasks, users, risks, issues }: ReportsViewProps) {
  // Generate burndown data (simulated)
  const generateBurndownData = () => {
    const totalTasks = tasks.length;
    const data = [];
    for (let i = 0; i <= 14; i++) {
      const completedByDay = tasks.filter((t) => {
        const daysSinceStart = Math.floor(
          (new Date(t.dueDate).getTime() - new Date(tasks[0].startDate).getTime()) / (1000 * 60 * 60 * 24)
        );
        return daysSinceStart <= i && t.status === 'done';
      }).length;

      data.push({
        day: `Day ${i}`,
        ideal: Math.max(0, totalTasks - (totalTasks / 14) * i),
        actual: totalTasks - completedByDay,
      });
    }
    return data;
  };

  // Generate velocity data
  const generateVelocityData = () => {
    const sprints = ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Current'];
    return sprints.map((sprint, index) => ({
      sprint,
      planned: 20 + index * 2,
      completed: 18 + index * 1.5,
    }));
  };

  const burndownData = generateBurndownData();
  const velocityData = generateVelocityData();

  const exportReport = () => {
    const reportData = {
      generatedAt: new Date().toISOString(),
      summary: {
        totalTasks: tasks.length,
        completedTasks: tasks.filter((t) => t.status === 'done').length,
        blockedTasks: tasks.filter((t) => t.isBlocked).length,
        totalRisks: risks.length,
        totalIssues: issues.length,
      },
      tasks: tasks.map((t) => ({
        id: t.id,
        title: t.title,
        status: t.status,
        priority: t.priority,
        assignee: users.find((u) => u.id === t.assigneeId)?.name,
        dueDate: t.dueDate,
        progress: t.progress,
      })),
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `project-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2>Reports & Analytics</h2>
          <p className="text-gray-600">Track progress and analyze team performance</p>
        </div>
        <Button onClick={exportReport}>
          <Download className="w-4 h-4 mr-2" />
          Export Report
        </Button>
      </div>

      <Tabs defaultValue="burndown" className="space-y-6">
        <TabsList>
          <TabsTrigger value="burndown">Burndown Chart</TabsTrigger>
          <TabsTrigger value="velocity">Velocity</TabsTrigger>
          <TabsTrigger value="risks">Risks</TabsTrigger>
          <TabsTrigger value="issues">Issues</TabsTrigger>
        </TabsList>

        <TabsContent value="burndown" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sprint Burndown Chart</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={burndownData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="ideal" stroke="#94a3b8" strokeDasharray="5 5" name="Ideal" />
                  <Line type="monotone" dataKey="actual" stroke="#3b82f6" strokeWidth={2} name="Actual" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600">Tasks Remaining</p>
                    <p className="text-3xl mt-2">
                      {tasks.filter((t) => t.status !== 'done').length}
                    </p>
                  </div>
                  <FileText className="w-12 h-12 text-blue-500 opacity-20" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600">Completion Trend</p>
                    <p className="text-3xl mt-2 text-green-600">+12%</p>
                  </div>
                  <TrendingUp className="w-12 h-12 text-green-500 opacity-20" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600">Days Remaining</p>
                    <p className="text-3xl mt-2">7</p>
                  </div>
                  <FileText className="w-12 h-12 text-orange-500 opacity-20" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="velocity" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Team Velocity Over Sprints</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={velocityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="sprint" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="planned" fill="#94a3b8" name="Planned" />
                  <Bar dataKey="completed" fill="#10b981" name="Completed" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Story Points Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-3xl text-blue-600">
                    {tasks.reduce((sum, t) => sum + (t.storyPoints || 0), 0)}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">Total Points</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-3xl text-green-600">
                    {tasks
                      .filter((t) => t.status === 'done')
                      .reduce((sum, t) => sum + (t.storyPoints || 0), 0)}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">Completed</p>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-3xl text-yellow-600">
                    {tasks
                      .filter((t) => t.status === 'in-progress')
                      .reduce((sum, t) => sum + (t.storyPoints || 0), 0)}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">In Progress</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl text-gray-600">19.5</p>
                  <p className="text-sm text-gray-600 mt-1">Avg Velocity</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risks" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Risk Register</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Risk</TableHead>
                    <TableHead>Probability</TableHead>
                    <TableHead>Impact</TableHead>
                    <TableHead>Owner</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Mitigation</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {risks.map((risk) => {
                    const owner = users.find((u) => u.id === risk.ownerId);
                    return (
                      <TableRow key={risk.id}>
                        <TableCell>
                          <div>
                            <p>{risk.title}</p>
                            <p className="text-sm text-gray-600">{risk.description}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            className={
                              risk.probability === 'high'
                                ? 'bg-red-100 text-red-800'
                                : risk.probability === 'medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-blue-100 text-blue-800'
                            }
                          >
                            {risk.probability}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            className={
                              risk.impact === 'high'
                                ? 'bg-red-100 text-red-800'
                                : risk.impact === 'medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-blue-100 text-blue-800'
                            }
                          >
                            {risk.impact}
                          </Badge>
                        </TableCell>
                        <TableCell>{owner?.name}</TableCell>
                        <TableCell>
                          <Badge
                            className={
                              risk.status === 'open'
                                ? 'bg-red-100 text-red-800'
                                : risk.status === 'mitigated'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-gray-100 text-gray-800'
                            }
                          >
                            {risk.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-xs">
                          <p className="text-sm text-gray-600 line-clamp-2">{risk.mitigation}</p>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="issues" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Issue Log</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Issue</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Assignee</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Related Tasks</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {issues.map((issue) => {
                    const assignee = users.find((u) => u.id === issue.assigneeId);
                    return (
                      <TableRow key={issue.id}>
                        <TableCell>
                          <div>
                            <p>{issue.title}</p>
                            <p className="text-sm text-gray-600">{issue.description}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            className={
                              issue.priority === 'high'
                                ? 'bg-red-100 text-red-800'
                                : issue.priority === 'medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-blue-100 text-blue-800'
                            }
                          >
                            {issue.priority}
                          </Badge>
                        </TableCell>
                        <TableCell>{assignee?.name}</TableCell>
                        <TableCell>
                          <Badge
                            className={
                              issue.status === 'open'
                                ? 'bg-red-100 text-red-800'
                                : issue.status === 'in-progress'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-green-100 text-green-800'
                            }
                          >
                            {issue.status}
                          </Badge>
                        </TableCell>
                        <TableCell>{new Date(issue.createdAt).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {issue.relatedTaskIds.slice(0, 2).map((taskId) => {
                              const task = tasks.find((t) => t.id === taskId);
                              return task ? (
                                <Badge key={taskId} variant="outline" className="text-xs">
                                  {task.title.slice(0, 15)}...
                                </Badge>
                              ) : null;
                            })}
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
