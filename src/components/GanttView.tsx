import { Task, User } from '../types';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Diamond, ChevronRight, ChevronDown } from 'lucide-react';
import { useState } from 'react';

interface GanttViewProps {
  tasks: Task[];
  users: User[];
  onTaskClick: (task: Task) => void;
}

export function GanttView({ tasks, users, onTaskClick }: GanttViewProps) {
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  // Calculate date range
  const allDates = tasks.flatMap((t) => [new Date(t.startDate), new Date(t.dueDate)]);
  const minDate = new Date(Math.min(...allDates.map((d) => d.getTime())));
  const maxDate = new Date(Math.max(...allDates.map((d) => d.getTime())));

  // Generate weeks for the timeline
  const weeks: Date[] = [];
  const current = new Date(minDate);
  current.setDate(current.getDate() - current.getDay()); // Start from Sunday

  while (current <= maxDate) {
    weeks.push(new Date(current));
    current.setDate(current.getDate() + 7);
  }

  const totalDays = Math.ceil((maxDate.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24)) + 7;
  const dayWidth = 40;

  const getTaskPosition = (task: Task) => {
    const start = new Date(task.startDate);
    const end = new Date(task.dueDate);
    const left = Math.ceil((start.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24)) * dayWidth;
    const duration = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    const width = Math.max(duration * dayWidth, 60);

    return { left, width };
  };

  const getTodayPosition = () => {
    const today = new Date();
    const left = Math.ceil((today.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24)) * dayWidth;
    return left;
  };

  const toggleCollapse = (taskId: string) => {
    const newCollapsed = new Set(collapsed);
    if (newCollapsed.has(taskId)) {
      newCollapsed.delete(taskId);
    } else {
      newCollapsed.add(taskId);
    }
    setCollapsed(newCollapsed);
  };

  const parentTasks = tasks.filter((t) => !t.parentId);
  const childTasks = (parentId: string) => tasks.filter((t) => t.parentId === parentId);

  const renderTask = (task: Task, depth: number = 0) => {
    const assignee = users.find((u) => u.id === task.assigneeId);
    const { left, width } = getTaskPosition(task);
    const hasChildren = tasks.some((t) => t.parentId === task.id);
    const isCollapsed = collapsed.has(task.id);

    const progressColor =
      task.status === 'done'
        ? 'bg-green-500'
        : task.status === 'in-progress'
        ? 'bg-blue-500'
        : 'bg-gray-300';

    return (
      <div key={task.id}>
        <div className="flex border-b hover:bg-gray-50">
          <div className="w-80 p-3 border-r flex items-center gap-2" style={{ paddingLeft: `${depth * 20 + 12}px` }}>
            {hasChildren && (
              <button onClick={() => toggleCollapse(task.id)} className="p-0.5 hover:bg-gray-200 rounded">
                {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate">{task.title}</p>
              {assignee && <p className="text-xs text-gray-500">{assignee.name}</p>}
            </div>
            {task.isMilestone && <Diamond className="w-4 h-4 text-blue-500" />}
          </div>

          <div className="flex-1 p-3 relative">
            {task.isMilestone ? (
              <div
                className="absolute top-1/2 transform -translate-y-1/2"
                style={{ left: `${left}px` }}
              >
                <Diamond className="w-6 h-6 fill-blue-500 text-blue-500" />
              </div>
            ) : (
              <button
                onClick={() => onTaskClick(task)}
                className="absolute top-1/2 transform -translate-y-1/2 h-8 rounded cursor-pointer hover:opacity-90 transition-opacity"
                style={{ left: `${left}px`, width: `${width}px` }}
              >
                <div className={`h-full rounded ${task.isBlocked ? 'bg-red-200' : 'bg-blue-200'}`}>
                  <div
                    className={`h-full rounded ${progressColor}`}
                    style={{ width: `${task.progress}%` }}
                  />
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xs px-2 truncate">{task.progress}%</span>
                </div>
              </button>
            )}

            {/* Dependencies */}
            {task.dependencies.map((depId) => {
              const depTask = tasks.find((t) => t.id === depId);
              if (!depTask) return null;

              const depPos = getTaskPosition(depTask);
              const taskPos = getTaskPosition(task);

              return (
                <svg
                  key={depId}
                  className="absolute top-0 left-0 pointer-events-none"
                  style={{ width: '100%', height: '100%' }}
                >
                  <line
                    x1={depPos.left + depPos.width}
                    y1="50%"
                    x2={taskPos.left}
                    y2="50%"
                    stroke="#3b82f6"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                  />
                  <defs>
                    <marker
                      id="arrowhead"
                      markerWidth="10"
                      markerHeight="10"
                      refX="9"
                      refY="3"
                      orient="auto"
                    >
                      <polygon points="0 0, 10 3, 0 6" fill="#3b82f6" />
                    </marker>
                  </defs>
                </svg>
              );
            })}
          </div>
        </div>

        {hasChildren && !isCollapsed && childTasks(task.id).map((child) => renderTask(child, depth + 1))}
      </div>
    );
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2>Gantt Chart</h2>
        <p className="text-gray-600">Timeline view of all tasks and dependencies</p>
      </div>

      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <div className="min-w-max">
            {/* Header */}
            <div className="flex border-b bg-gray-50">
              <div className="w-80 p-3 border-r">
                <p>Task Name</p>
              </div>
              <div className="flex-1 p-3">
                <div className="flex" style={{ width: `${totalDays * dayWidth}px` }}>
                  {weeks.map((week, index) => (
                    <div key={index} className="flex-shrink-0" style={{ width: `${7 * dayWidth}px` }}>
                      <p className="text-sm">
                        {week.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Timeline Grid */}
            <div className="relative">
              {/* Today marker */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-10 pointer-events-none"
                style={{ left: `${320 + getTodayPosition()}px` }}
              >
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-red-500 text-white text-xs px-2 py-0.5 rounded whitespace-nowrap">
                  Today
                </div>
              </div>

              {/* Tasks */}
              {parentTasks.map((task) => renderTask(task))}
            </div>
          </div>
        </div>
      </Card>

      <div className="mt-4 flex items-center gap-6 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-200 rounded"></div>
          <span>Not Started / In Progress</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span>Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-200 rounded"></div>
          <span>Blocked</span>
        </div>
        <div className="flex items-center gap-2">
          <Diamond className="w-4 h-4 text-blue-500" />
          <span>Milestone</span>
        </div>
      </div>
    </div>
  );
}
