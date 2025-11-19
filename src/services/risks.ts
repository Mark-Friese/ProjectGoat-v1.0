/**
 * Risk API Service
 * Handles all risk-related API calls
 */

import { Risk } from '../types';
import * as api from './api';

/**
 * Get all risks
 */
export async function getRisks(): Promise<Risk[]> {
  return api.get<Risk[]>('/risks');
}

/**
 * Get a specific risk by ID
 */
export async function getRisk(id: string): Promise<Risk> {
  return api.get<Risk>(`/risks/${id}`);
}

/**
 * Generate a unique risk ID
 */
function generateRiskId(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);
  return `r${timestamp}${random}`;
}

/**
 * Create a new risk
 */
export async function createRisk(risk: Partial<Risk>): Promise<Risk> {
  const data: any = { ...risk };

  // Backend requires an ID - generate one if not provided
  if (!data.id) {
    data.id = generateRiskId();
  }

  return api.post<Risk>('/risks', data);
}

/**
 * Update an existing risk
 */
export async function updateRisk(id: string, risk: Partial<Risk>): Promise<Risk> {
  return api.put<Risk>(`/risks/${id}`, risk);
}

/**
 * Delete a risk
 */
export async function deleteRisk(id: string): Promise<void> {
  await api.del(`/risks/${id}`);
}
