import { useState } from 'react';
import { Task, User, TaskStatus } from '../types';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { AlertCircle, Calendar, Flag } from 'lucide-react';
import { motion } from 'motion/react';

interface KanbanViewProps {
  tasks: Task[];
  users: User[];
  onTaskClick: (task: Task) => void;
  onTaskStatusChange: (taskId: string, newStatus: TaskStatus) => void;
}

const columns: { id: TaskStatus; title: string; color: string }[] = [
  { id: 'todo', title: 'To Do', color: 'bg-gray-100' },
  { id: 'in-progress', title: 'In Progress', color: 'bg-blue-100' },
  { id: 'review', title: 'Review', color: 'bg-yellow-100' },
  { id: 'done', title: 'Done', color: 'bg-green-100' },
];

export function KanbanView({ tasks, users, onTaskClick, onTaskStatusChange }: KanbanViewProps) {
  const [draggedTask, setDraggedTask] = useState<Task | null>(null);

  const handleDragStart = (task: Task) => {
    setDraggedTask(task);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (status: TaskStatus) => {
    if (draggedTask && draggedTask.status !== status) {
      onTaskStatusChange(draggedTask.id, status);
    }
    setDraggedTask(null);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const isOverdue = (task: Task) => {
    return new Date(task.dueDate) < new Date() && task.status !== 'done';
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2>Kanban Board</h2>
        <p className="text-gray-600">Drag and drop tasks to update their status</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {columns.map((column) => {
          const columnTasks = tasks.filter((task) => task.status === column.id);

          return (
            <div
              key={column.id}
              className="flex flex-col"
              onDragOver={handleDragOver}
              onDrop={() => handleDrop(column.id)}
            >
              <div className={`${column.color} p-4 rounded-t-lg`}>
                <div className="flex items-center justify-between">
                  <h3 className="text-sm">{column.title}</h3>
                  <span className="px-2 py-1 bg-white rounded text-sm">{columnTasks.length}</span>
                </div>
              </div>

              <div className="flex-1 bg-gray-50 p-4 rounded-b-lg space-y-3 min-h-[500px]">
                {columnTasks.map((task) => {
                  const assignee = users.find((u) => u.id === task.assigneeId);

                  return (
                    <motion.div
                      key={task.id}
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      <Card
                        draggable
                        onDragStart={() => handleDragStart(task)}
                        onClick={() => onTaskClick(task)}
                        className="p-4 cursor-pointer hover:shadow-lg transition-shadow border-l-4"
                        style={{
                          borderLeftColor:
                            task.priority === 'high'
                              ? '#ef4444'
                              : task.priority === 'medium'
                              ? '#f59e0b'
                              : '#3b82f6',
                        }}
                      >
                        <div className="space-y-3">
                          <div className="flex items-start justify-between gap-2">
                            <p className="flex-1">{task.title}</p>
                            {task.isBlocked && (
                              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                            )}
                          </div>

                          {task.description && (
                            <p className="text-sm text-gray-600 line-clamp-2">{task.description}</p>
                          )}

                          <div className="flex flex-wrap gap-2">
                            {task.tags.map((tag) => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>

                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Calendar className="w-4 h-4" />
                              <span className={isOverdue(task) ? 'text-red-600' : ''}>
                                {new Date(task.dueDate).toLocaleDateString('en-US', {
                                  month: 'short',
                                  day: 'numeric',
                                })}
                              </span>
                            </div>

                            {assignee && (
                              <Avatar className="w-6 h-6">
                                <AvatarFallback className="text-xs">
                                  {assignee.name.split(' ').map((n) => n[0]).join('')}
                                </AvatarFallback>
                              </Avatar>
                            )}
                          </div>

                          {task.storyPoints && (
                            <div className="flex items-center gap-2">
                              <Flag className="w-4 h-4 text-gray-400" />
                              <span className="text-sm text-gray-600">{task.storyPoints} points</span>
                            </div>
                          )}

                          {task.progress > 0 && (
                            <div className="w-full bg-gray-200 rounded-full h-1.5">
                              <div
                                className="bg-blue-600 h-1.5 rounded-full transition-all"
                                style={{ width: `${task.progress}%` }}
                              />
                            </div>
                          )}
                        </div>
                      </Card>
                    </motion.div>
                  );
                })}

                {columnTasks.length === 0 && (
                  <div className="flex items-center justify-center h-32 text-gray-400 border-2 border-dashed rounded-lg">
                    Drop tasks here
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
