import { useState } from 'react';
import { Task, User } from '../types';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ChevronLeft, ChevronRight, Diamond } from 'lucide-react';

interface CalendarViewProps {
  tasks: Task[];
  users: User[];
  onTaskClick: (task: Task) => void;
}

export function CalendarView({ tasks, users, onTaskClick }: CalendarViewProps) {
  const [currentDate, setCurrentDate] = useState(new Date());

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    return { daysInMonth, startingDayOfWeek, firstDay, lastDay };
  };

  const { daysInMonth, startingDayOfWeek, firstDay, lastDay } = getDaysInMonth(currentDate);

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const getTasksForDate = (date: Date) => {
    return tasks.filter((task) => {
      const taskDate = new Date(task.dueDate);
      return (
        taskDate.getDate() === date.getDate() &&
        taskDate.getMonth() === date.getMonth() &&
        taskDate.getFullYear() === date.getFullYear()
      );
    });
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  };

  const weeks: (Date | null)[][] = [];
  let currentWeek: (Date | null)[] = [];

  // Add empty cells for days before the first of the month
  for (let i = 0; i < startingDayOfWeek; i++) {
    currentWeek.push(null);
  }

  // Add all days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    currentWeek.push(date);

    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  }

  // Add remaining days to complete the last week
  if (currentWeek.length > 0) {
    while (currentWeek.length < 7) {
      currentWeek.push(null);
    }
    weeks.push(currentWeek);
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2>Calendar View</h2>
          <p className="text-gray-600">Task due dates and milestones</p>
        </div>

        <div className="flex items-center gap-4">
          <Button onClick={previousMonth} variant="outline" size="sm">
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <div className="min-w-[200px] text-center">
            <p>
              {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </p>
          </div>
          <Button onClick={nextMonth} variant="outline" size="sm">
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Card className="overflow-hidden">
        <div className="grid grid-cols-7 bg-gray-50 border-b">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div key={day} className="p-3 text-center border-r last:border-r-0">
              <p className="text-sm">{day}</p>
            </div>
          ))}
        </div>

        <div>
          {weeks.map((week, weekIndex) => (
            <div key={weekIndex} className="grid grid-cols-7 border-b last:border-b-0">
              {week.map((date, dayIndex) => {
                const dateTasks = date ? getTasksForDate(date) : [];
                const isTodayDate = date ? isToday(date) : false;

                return (
                  <div
                    key={dayIndex}
                    className={`min-h-[120px] p-2 border-r last:border-r-0 ${
                      date ? 'bg-white' : 'bg-gray-50'
                    } ${isTodayDate ? 'bg-blue-50' : ''}`}
                  >
                    {date && (
                      <>
                        <div
                          className={`text-sm mb-2 ${
                            isTodayDate
                              ? 'w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center'
                              : ''
                          }`}
                        >
                          {date.getDate()}
                        </div>

                        <div className="space-y-1">
                          {dateTasks.slice(0, 3).map((task) => {
                            const assignee = users.find((u) => u.id === task.assigneeId);

                            return (
                              <button
                                key={task.id}
                                onClick={() => onTaskClick(task)}
                                className={`w-full text-left px-2 py-1 rounded text-xs hover:opacity-80 transition-opacity ${
                                  task.isMilestone
                                    ? 'bg-purple-100 text-purple-800 border border-purple-300'
                                    : 'bg-gray-100 text-gray-800 border'
                                }`}
                              >
                                <div className="flex items-center gap-1">
                                  {task.isMilestone && <Diamond className="w-3 h-3" />}
                                  <span className="truncate flex-1">{task.title}</span>
                                  <div
                                    className={`w-2 h-2 rounded-full ${getPriorityColor(
                                      task.priority
                                    )}`}
                                  />
                                </div>
                              </button>
                            );
                          })}

                          {dateTasks.length > 3 && (
                            <div className="text-xs text-gray-500 px-2">
                              +{dateTasks.length - 3} more
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </Card>

      <div className="mt-4 flex items-center gap-6 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <span>High Priority</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <span>Medium Priority</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span>Low Priority</span>
        </div>
        <div className="flex items-center gap-2">
          <Diamond className="w-4 h-4 text-purple-500" />
          <span>Milestone</span>
        </div>
      </div>
    </div>
  );
}
