export type Priority = 'low' | 'medium' | 'high';
export type TaskStatus = 'todo' | 'in-progress' | 'review' | 'done';
export type UserRole = 'admin' | 'member' | 'viewer';

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
