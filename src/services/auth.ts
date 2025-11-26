/**
 * Authentication Service
 * Handles login, logout, registration, and session management
 */

import {
  User,
  Team,
  TeamMember,
  Invitation,
  InvitationDetails,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  SessionResponse,
  CreateTeamMemberRequest,
  UserRole,
} from '../types';
import * as api from './api';

// ==================== Authentication ====================

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
 * Register a new team with admin user
 */
export async function register(request: RegisterRequest): Promise<RegisterResponse> {
  const response = await api.post<RegisterResponse>('/auth/register', request);

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
 * Change user password
 */
export async function changePassword(
  currentPassword: string,
  newPassword: string
): Promise<{ success: boolean; message: string; csrfToken: string }> {
  const response = await api.post<{ success: boolean; message: string; csrfToken: string }>(
    '/auth/change-password',
    {
      current_password: currentPassword,
      new_password: newPassword,
    }
  );

  // Update CSRF token if provided
  if (response.csrfToken) {
    localStorage.setItem('csrfToken', response.csrfToken);
  }

  return response;
}

// ==================== User Profile ====================

export interface LoginHistoryEntry {
  ipAddress?: string;
  userAgent?: string;
  attemptedAt: string;
  success: boolean;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  createdAt?: string;
  lastLoginAt?: string;
  passwordChangedAt?: string;
  loginHistory: LoginHistoryEntry[];
}

/**
 * Get current user's profile with login history
 */
export async function getProfile(): Promise<UserProfile> {
  return await api.get<UserProfile>('/users/me');
}

/**
 * Update current user's profile
 */
export async function updateProfile(data: {
  name?: string;
  email?: string;
}): Promise<User> {
  return await api.put<User>('/users/me', data);
}

// ==================== Team Management ====================

/**
 * Get current team info
 */
export async function getCurrentTeam(): Promise<Team> {
  return await api.get<Team>('/teams/current');
}

/**
 * Update current team
 */
export async function updateTeam(name: string): Promise<Team> {
  return await api.put<Team>('/teams/current', { name });
}

/**
 * Switch to a different team
 */
export async function switchTeam(teamId: string): Promise<{ team: Team }> {
  return await api.post<{ team: Team }>('/teams/switch', { teamId });
}

/**
 * Archive (soft delete) current team
 */
export async function archiveTeam(): Promise<Team> {
  return await api.del<Team>('/teams/current');
}

// ==================== Team Members ====================

/**
 * Get all members of current team
 */
export async function getTeamMembers(): Promise<TeamMember[]> {
  return await api.get<TeamMember[]>('/teams/current/members');
}

/**
 * Create a new member directly (admin only)
 */
export async function createTeamMember(data: CreateTeamMemberRequest): Promise<TeamMember> {
  return await api.post<TeamMember>('/teams/current/members', data);
}

/**
 * Update a member's role
 */
export async function updateMemberRole(userId: string, role: UserRole): Promise<TeamMember> {
  return await api.put<TeamMember>(`/teams/current/members/${userId}`, { role });
}

/**
 * Remove a member from team
 */
export async function removeMember(
  userId: string,
  taskAction: 'unassign' | 'reassign_admin' | 'keep' = 'unassign'
): Promise<void> {
  await api.del<void>(`/teams/current/members/${userId}?taskAction=${taskAction}`);
}

// ==================== Invitations ====================

/**
 * Get pending invitations for current team
 */
export async function getInvitations(): Promise<Invitation[]> {
  return await api.get<Invitation[]>('/invitations');
}

/**
 * Create a new invitation
 */
export async function createInvitation(
  email: string,
  role: UserRole = 'member'
): Promise<Invitation> {
  return await api.post<Invitation>('/invitations', { email, role });
}

/**
 * Revoke an invitation
 */
export async function revokeInvitation(invitationId: string): Promise<void> {
  await api.del<void>(`/invitations/${invitationId}`);
}

/**
 * Get invitation details by token (public endpoint)
 */
export async function getInvitationDetails(token: string): Promise<InvitationDetails> {
  return await api.get<InvitationDetails>(`/invitations/accept/${token}`);
}

/**
 * Accept an invitation
 */
export async function acceptInvitation(
  token: string,
  name: string,
  password: string
): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>(`/invitations/accept/${token}`, {
    name,
    password,
  });

  // Store session ID and CSRF token in localStorage
  if (response.sessionId) {
    localStorage.setItem('sessionId', response.sessionId);
  }
  if (response.csrfToken) {
    localStorage.setItem('csrfToken', response.csrfToken);
  }

  return response;
}

// ==================== Legacy functions (for backward compatibility) ====================

/**
 * Get current user from settings
 * @deprecated Use checkSession() instead
 */
export async function getCurrentUser(): Promise<{ userId: string }> {
  return api.get<{ userId: string }>('/settings/current-user');
}

/**
 * Set current user in settings
 * @deprecated Use login() instead
 */
export async function setCurrentUser(userId: string): Promise<void> {
  await api.put('/settings/current-user', { user_id: userId });
}
