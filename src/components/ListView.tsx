import { useState } from 'react';
import { Task, User } from '../types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Progress } from './ui/progress';
import { AlertCircle, Search, ArrowUpDown, Download } from 'lucide-react';

interface ListViewProps {
  tasks: Task[];
  users: User[];
  onTaskClick: (task: Task) => void;
}

export function ListView({ tasks, users, onTaskClick }: ListViewProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'dueDate' | 'priority' | 'progress'>('dueDate');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || task.status === filterStatus;
    const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  const sortedTasks = [...filteredTasks].sort((a, b) => {
    let comparison = 0;

    switch (sortBy) {
      case 'dueDate':
        comparison = new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
        break;
      case 'priority':
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        comparison = priorityOrder[b.priority] - priorityOrder[a.priority];
        break;
      case 'progress':
        comparison = a.progress - b.progress;
        break;
    }

    return sortOrder === 'asc' ? comparison : -comparison;
  });

  const toggleSort = (field: 'dueDate' | 'priority' | 'progress') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { label: string; className: string }> = {
      todo: { label: 'To Do', className: 'bg-gray-100 text-gray-800' },
      'in-progress': { label: 'In Progress', className: 'bg-blue-100 text-blue-800' },
      review: { label: 'Review', className: 'bg-yellow-100 text-yellow-800' },
      done: { label: 'Done', className: 'bg-green-100 text-green-800' },
    };

    const variant = variants[status] || variants.todo;
    return <Badge className={variant.className}>{variant.label}</Badge>;
  };

  const getPriorityBadge = (priority: string) => {
    const variants: Record<string, { className: string }> = {
      high: { className: 'bg-red-100 text-red-800' },
      medium: { className: 'bg-yellow-100 text-yellow-800' },
      low: { className: 'bg-blue-100 text-blue-800' },
    };

    const variant = variants[priority] || variants.low;
    return <Badge className={variant.className}>{priority}</Badge>;
  };

  const exportToCSV = () => {
    const headers = ['Title', 'Status', 'Priority', 'Assignee', 'Due Date', 'Progress'];
    const rows = sortedTasks.map((task) => {
      const assignee = users.find((u) => u.id === task.assigneeId);
      return [
        task.title,
        task.status,
        task.priority,
        assignee?.name || 'Unassigned',
        new Date(task.dueDate).toLocaleDateString(),
        `${task.progress}%`,
      ];
    });

    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'tasks.csv';
    a.click();
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2>Task List</h2>
        <p className="text-gray-600">Comprehensive view of all tasks</p>
      </div>

      <div className="mb-6 flex flex-wrap gap-4">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="todo">To Do</SelectItem>
            <SelectItem value="in-progress">In Progress</SelectItem>
            <SelectItem value="review">Review</SelectItem>
            <SelectItem value="done">Done</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterPriority} onValueChange={setFilterPriority}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priorities</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>

        <Button onClick={exportToCSV} variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>

      <div className="rounded-lg border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40px]"></TableHead>
              <TableHead>Task</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>
                <button
                  onClick={() => toggleSort('priority')}
                  className="flex items-center gap-1 hover:text-gray-900"
                >
                  Priority
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </TableHead>
              <TableHead>Assignee</TableHead>
              <TableHead>
                <button
                  onClick={() => toggleSort('dueDate')}
                  className="flex items-center gap-1 hover:text-gray-900"
                >
                  Due Date
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </TableHead>
              <TableHead>
                <button
                  onClick={() => toggleSort('progress')}
                  className="flex items-center gap-1 hover:text-gray-900"
                >
                  Progress
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </TableHead>
              <TableHead>Tags</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedTasks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-gray-500 py-8">
                  No tasks found
                </TableCell>
              </TableRow>
            ) : (
              sortedTasks.map((task) => {
                const assignee = users.find((u) => u.id === task.assigneeId);
                const isOverdue = new Date(task.dueDate) < new Date() && task.status !== 'done';

                return (
                  <TableRow
                    key={task.id}
                    onClick={() => onTaskClick(task)}
                    className="cursor-pointer hover:bg-gray-50"
                  >
                    <TableCell>
                      {task.isBlocked && <AlertCircle className="w-4 h-4 text-red-500" />}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span>{task.title}</span>
                        {task.isMilestone && (
                          <Badge variant="outline" className="text-xs">
                            Milestone
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(task.status)}</TableCell>
                    <TableCell>{getPriorityBadge(task.priority)}</TableCell>
                    <TableCell>
                      {assignee ? (
                        <div className="flex items-center gap-2">
                          <Avatar className="w-6 h-6">
                            <AvatarFallback className="text-xs">
                              {assignee.name.split(' ').map((n) => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <span className="text-sm">{assignee.name}</span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">Unassigned</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <span className={isOverdue ? 'text-red-600' : ''}>
                        {new Date(task.dueDate).toLocaleDateString()}
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Progress value={task.progress} className="w-20 h-2" />
                        <span className="text-sm text-gray-600">{task.progress}%</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {task.tags.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {task.tags.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{task.tags.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      <div className="mt-4 text-sm text-gray-600">
        Showing {sortedTasks.length} of {tasks.length} tasks
      </div>
    </div>
  );
}
