/**
 * Issue API Service
 * Handles all issue-related API calls
 */

import { Issue } from '../types';
import * as api from './api';

interface IssueFilters {
  status?: 'open' | 'in-progress' | 'resolved';
  assignee_id?: string;
}

/**
 * Convert API issue data to frontend Issue type
 */
function parseIssue(data: any): Issue {
  return {
    ...data,
    createdAt: api.parseDate(data.createdAt),
    resolvedAt: data.resolvedAt ? api.parseDate(data.resolvedAt) : undefined,
  };
}

/**
 * Convert frontend Issue to API format
 */
function serializeIssue(issue: Partial<Issue>): any {
  const data: any = { ...issue };

  if (data.createdAt) {
    data.createdAt = api.formatDateTime(data.createdAt);
  }
  if (data.resolvedAt) {
    data.resolvedAt = api.formatDateTime(data.resolvedAt);
  }

  return data;
}

/**
 * Get all issues with optional filters
 */
export async function getIssues(filters?: IssueFilters): Promise<Issue[]> {
  const params = new URLSearchParams();

  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value));
      }
    });
  }

  const queryString = params.toString();
  const endpoint = queryString ? `/issues?${queryString}` : '/issues';

  const data = await api.get<any[]>(endpoint);
  return data.map(parseIssue);
}

/**
 * Get a specific issue by ID
 */
export async function getIssue(id: string): Promise<Issue> {
  const data = await api.get<any>(`/issues/${id}`);
  return parseIssue(data);
}

/**
 * Generate a unique issue ID
 */
function generateIssueId(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);
  return `i${timestamp}${random}`;
}

/**
 * Create a new issue
 */
export async function createIssue(issue: Partial<Issue>): Promise<Issue> {
  const data = serializeIssue(issue);

  // Backend requires an ID - generate one if not provided
  if (!data.id) {
    data.id = generateIssueId();
  }

  const response = await api.post<any>('/issues', data);
  return parseIssue(response);
}

/**
 * Update an existing issue
 */
export async function updateIssue(id: string, issue: Partial<Issue>): Promise<Issue> {
  const data = serializeIssue(issue);
  const response = await api.put<any>(`/issues/${id}`, data);
  return parseIssue(response);
}

/**
 * Resolve an issue
 */
export async function resolveIssue(id: string): Promise<Issue> {
  const response = await api.patch<any>(`/issues/${id}/resolve`, {});
  return parseIssue(response);
}

/**
 * Delete an issue
 */
export async function deleteIssue(id: string): Promise<void> {
  await api.del(`/issues/${id}`);
}
