/**
 * Task API Service
 * Handles all task-related API calls
 */

import { Task, TaskStatus } from '../types';
import * as api from './api';

interface TaskFilters {
  project_id?: string;
  assignee_id?: string;
  status?: TaskStatus;
  is_blocked?: boolean;
  limit?: number;
  offset?: number;
}

/**
 * Convert API task data to frontend Task type
 */
function parseTask(data: any): Task {
  return {
    ...data,
    startDate: api.parseDate(data.startDate),
    dueDate: api.parseDate(data.dueDate),
    comments: data.comments.map((comment: any) => ({
      ...comment,
      timestamp: api.parseDate(comment.timestamp),
    })),
    blocker: data.blocker
      ? {
          ...data.blocker,
          createdAt: api.parseDate(data.blocker.createdAt),
          resolvedAt: data.blocker.resolvedAt ? api.parseDate(data.blocker.resolvedAt) : undefined,
        }
      : undefined,
  };
}

/**
 * Convert frontend Task to API format
 */
function serializeTask(task: Partial<Task>): any {
  const data: any = { ...task };

  if (data.startDate) {
    data.startDate = api.formatDate(data.startDate);
  }
  if (data.dueDate) {
    data.dueDate = api.formatDate(data.dueDate);
  }

  // Remove fields that shouldn't be sent to API
  delete data.comments;
  delete data.blocker;

  return data;
}

/**
 * Get all tasks with optional filters
 */
export async function getTasks(filters?: TaskFilters): Promise<Task[]> {
  const params = new URLSearchParams();

  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value));
      }
    });
  }

  const queryString = params.toString();
  const endpoint = queryString ? `/tasks?${queryString}` : '/tasks';

  const data = await api.get<any[]>(endpoint);
  return data.map(parseTask);
}

/**
 * Get a specific task by ID
 */
export async function getTask(id: string): Promise<Task> {
  const data = await api.get<any>(`/tasks/${id}`);
  return parseTask(data);
}

/**
 * Generate a unique task ID
 */
function generateTaskId(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);
  return `t${timestamp}${random}`;
}

/**
 * Create a new task
 */
export async function createTask(task: Partial<Task>): Promise<Task> {
  const data = serializeTask(task);

  // Backend requires an ID - generate one if not provided
  if (!data.id) {
    data.id = generateTaskId();
  }

  const response = await api.post<any>('/tasks', data);
  return parseTask(response);
}

/**
 * Update an existing task
 */
export async function updateTask(id: string, task: Partial<Task>): Promise<Task> {
  const data = serializeTask(task);
  const response = await api.put<any>(`/tasks/${id}`, data);
  return parseTask(response);
}

/**
 * Update task status only
 */
export async function updateTaskStatus(id: string, status: TaskStatus): Promise<Task> {
  const response = await api.patch<any>(`/tasks/${id}/status`, { status });
  return parseTask(response);
}

/**
 * Delete a task
 */
export async function deleteTask(id: string): Promise<void> {
  await api.del(`/tasks/${id}`);
}

/**
 * Add a comment to a task
 */
export async function addComment(
  taskId: string,
  userId: string,
  text: string
): Promise<void> {
  await api.post(`/tasks/${taskId}/comments`, { userId, text });
}

/**
 * Delete a comment
 */
export async function deleteComment(commentId: string): Promise<void> {
  await api.del(`/comments/${commentId}`);
}

/**
 * Add a blocker to a task
 */
export async function addBlocker(taskId: string, description: string): Promise<void> {
  await api.post(`/tasks/${taskId}/blocker`, { description });
}

/**
 * Resolve a blocker
 */
export async function resolveBlocker(
  blockerId: string,
  resolutionNotes: string
): Promise<void> {
  await api.put(`/blockers/${blockerId}/resolve`, { resolutionNotes });
}

/**
 * Remove a blocker
 */
export async function removeBlocker(blockerId: string): Promise<void> {
  await api.del(`/blockers/${blockerId}`);
}
