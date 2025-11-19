/**
 * Project API Service
 * Handles all project-related API calls
 */

import { Project } from '../types';
import * as api from './api';

/**
 * Convert API project data to frontend Project type
 */
function parseProject(data: any): Project {
  return {
    ...data,
    startDate: api.parseDate(data.startDate),
    endDate: api.parseDate(data.endDate),
  };
}

/**
 * Convert frontend Project to API format
 */
function serializeProject(project: Partial<Project>): any {
  const data: any = { ...project };

  if (data.startDate) {
    data.startDate = api.formatDate(data.startDate);
  }
  if (data.endDate) {
    data.endDate = api.formatDate(data.endDate);
  }

  return data;
}

/**
 * Get all projects
 */
export async function getProjects(): Promise<Project[]> {
  const data = await api.get<any[]>('/projects');
  return data.map(parseProject);
}

/**
 * Get a specific project by ID
 */
export async function getProject(id: string): Promise<Project> {
  const data = await api.get<any>(`/projects/${id}`);
  return parseProject(data);
}

/**
 * Generate a unique project ID
 */
function generateProjectId(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);
  return `p${timestamp}${random}`;
}

/**
 * Create a new project
 */
export async function createProject(project: Partial<Project>): Promise<Project> {
  const data = serializeProject(project);

  // Backend requires an ID - generate one if not provided
  if (!data.id) {
    data.id = generateProjectId();
  }

  const response = await api.post<any>('/projects', data);
  return parseProject(response);
}

/**
 * Update an existing project
 */
export async function updateProject(id: string, project: Partial<Project>): Promise<Project> {
  const data = serializeProject(project);
  const response = await api.put<any>(`/projects/${id}`, data);
  return parseProject(response);
}

/**
 * Delete a project
 */
export async function deleteProject(id: string): Promise<void> {
  await api.del(`/projects/${id}`);
}
