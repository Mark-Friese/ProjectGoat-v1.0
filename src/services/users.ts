/**
 * User API Service
 * Handles all user-related API calls
 */

import { User, UserRole } from '../types';
import * as api from './api';

/**
 * Get all users
 */
export async function getUsers(): Promise<User[]> {
  return api.get<User[]>('/users');
}

/**
 * Get a specific user by ID
 */
export async function getUser(id: string): Promise<User> {
  return api.get<User>(`/users/${id}`);
}

/**
 * Generate a unique user ID
 */
function generateUserId(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);
  return `u${timestamp}${random}`;
}

/**
 * Create a new user
 */
export async function createUser(user: Partial<User>): Promise<User> {
  const data: any = { ...user };

  // Backend requires an ID - generate one if not provided
  if (!data.id) {
    data.id = generateUserId();
  }

  return api.post<User>('/users', data);
}

/**
 * Update an existing user
 */
export async function updateUser(id: string, user: Partial<User>): Promise<User> {
  return api.put<User>(`/users/${id}`, user);
}
