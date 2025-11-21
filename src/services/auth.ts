/**
 * Authentication Service
 * Handles login, logout, and session management
 */

import { User } from '../types';
import * as api from './api';

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  sessionId: string;
  csrfToken: string;
  user: User;
}

interface SessionResponse {
  user: User | null;
  authenticated: boolean;
}

/**
 * Login with email and password
 */
export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/auth/login', { email, password });

  // Store session ID and CSRF token in localStorage
  if (response.sessionId) {
    localStorage.setItem('sessionId', response.sessionId);
  }
  if (response.csrfToken) {
    localStorage.setItem('csrfToken', response.csrfToken);
  }

  return response;
}

/**
 * Check if there's a valid session
 */
export async function checkSession(): Promise<SessionResponse> {
  const sessionId = localStorage.getItem('sessionId');

  const params = sessionId ? `?session_id=${sessionId}` : '';
  const response = await api.get<SessionResponse>(`/auth/session${params}`);

  return response;
}

/**
 * Logout and clear session
 */
export async function logout(): Promise<void> {
  const sessionId = localStorage.getItem('sessionId');

  if (sessionId) {
    try {
      await api.post('/auth/logout', { session_id: sessionId });
    } catch (error) {
      console.error('Logout error:', error);
    }

    localStorage.removeItem('sessionId');
    localStorage.removeItem('csrfToken');
  }
}

/**
 * Get current user from settings
 */
export async function getCurrentUser(): Promise<{ userId: string }> {
  return api.get<{ userId: string }>('/settings/current-user');
}

/**
 * Set current user in settings
 */
export async function setCurrentUser(userId: string): Promise<void> {
  await api.put('/settings/current-user', { user_id: userId });
}

/**
 * Change user password
 */
export async function changePassword(
  currentPassword: string,
  newPassword: string
): Promise<{ success: boolean; message: string }> {
  return await api.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
}
