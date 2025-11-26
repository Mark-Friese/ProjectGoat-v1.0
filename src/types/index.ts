export type Priority = 'low' | 'medium' | 'high';
export type TaskStatus = 'todo' | 'in-progress' | 'review' | 'done';
export type UserRole = 'admin' | 'member' | 'viewer';
export type AccountType = 'single' | 'multi';

// ==================== Team Types ====================

export interface Team {
  id: string;
  name: string;
  accountType: AccountType;
  createdAt: Date;
  isArchived: boolean;
}

export interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
  availability: boolean;
  joinedAt: Date;
}

export interface Invitation {
  id: string;
  email: string;
  role: UserRole;
  invitedByName: string;
  expiresAt: Date;
  createdAt: Date;
}

export interface InvitationDetails {
  teamName: string;
  teamAccountType: AccountType;
  invitedByName: string;
  email: string;
  role: UserRole;
  expiresAt: Date;
}

// ==================== Auth Types ====================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  sessionId: string;
  csrfToken: string;
  user: User;
  team: Team;
  teams: Team[];
}

export interface RegisterRequest {
  teamName: string;
  accountType: AccountType;
  admin: {
    name: string;
    email: string;
    password: string;
  };
}

export interface RegisterResponse {
  sessionId: string;
  csrfToken: string;
  user: User;
  team: Team;
}

export interface SessionResponse {
  user: User | null;
  team: Team | null;
  teams: Team[];
  authenticated: boolean;
}

export interface InvitationAcceptRequest {
  name: string;
  password: string;
}

export interface CreateTeamMemberRequest {
  name: string;
  email: string;
  password: string;
  role: UserRole;
}

// ==================== User Types ====================

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
  availability: boolean;
}

export interface Comment {
  id: string;
  userId: string;
  text: string;
  timestamp: Date;
}

export interface Blocker {
  description: string;
  createdAt: Date;
  resolvedAt?: Date;
  resolutionNotes?: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  assigneeId?: string;
  startDate: Date;
  dueDate: Date;
  progress: number;
  tags: string[];
  isBlocked: boolean;
  blocker?: Blocker;
  isMilestone: boolean;
  dependencies: string[];
  storyPoints?: number;
  parentId?: string;
  comments: Comment[];
  projectId: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  startDate: Date;
  endDate: Date;
  color: string;
}

export interface Sprint {
  id: string;
  name: string;
  startDate: Date;
  endDate: Date;
  goals: string[];
  taskIds: string[];
  velocity: number;
}

export interface Risk {
  id: string;
  title: string;
  description: string;
  probability: Priority;
  impact: Priority;
  ownerId: string;
  mitigation: string;
  status: 'open' | 'mitigated' | 'closed';
}

export interface Issue {
  id: string;
  title: string;
  description: string;
  priority: Priority;
  assigneeId: string;
  status: 'open' | 'in-progress' | 'resolved';
  relatedTaskIds: string[];
  createdAt: Date;
  resolvedAt?: Date;
}
