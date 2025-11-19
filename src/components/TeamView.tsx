import { useState, useEffect } from 'react';
import { User, Task, UserRole } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Users, Mail, Shield, CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import * as userService from '../services/users';

interface TeamViewProps {
  users: User[];
  tasks: Task[];
  onUserUpdate?: (user: User) => void;
}

export function TeamView({ users, tasks, onUserUpdate }: TeamViewProps) {
  const [updatingUserId, setUpdatingUserId] = useState<string | null>(null);
  const [localUsers, setLocalUsers] = useState<User[]>(users);

  // Update local users when props change
  useEffect(() => {
    setLocalUsers(users);
  }, [users]);

  const handleRoleChange = async (userId: string, newRole: UserRole) => {
    const user = localUsers.find((u) => u.id === userId);
    if (!user) return;

    try {
      setUpdatingUserId(userId);

      // Backend requires all fields for update, not just the changed field
      const updatedUser = await userService.updateUser(userId, {
        name: user.name,
        email: user.email,
        role: newRole,
        avatar: user.avatar,
        availability: user.availability,
      });

      // Update local state
      setLocalUsers(localUsers.map((u) => (u.id === userId ? updatedUser : u)));

      // Notify parent component
      if (onUserUpdate) {
        onUserUpdate(updatedUser);
      }
    } catch (error) {
      console.error('Failed to update user role:', error);
      alert('Failed to update role. Please try again.');
    } finally {
      setUpdatingUserId(null);
    }
  };

  const getUserStats = (userId: string) => {
    const userTasks = tasks.filter((t) => t.assigneeId === userId);
    return {
      total: userTasks.length,
      completed: userTasks.filter((t) => t.status === 'done').length,
      inProgress: userTasks.filter((t) => t.status === 'in-progress').length,
      blocked: userTasks.filter((t) => t.isBlocked).length,
    };
  };

  const getRoleBadge = (role: string) => {
    const variants: Record<string, { className: string; icon: typeof Shield }> = {
      admin: { className: 'bg-purple-100 text-purple-800', icon: Shield },
      member: { className: 'bg-blue-100 text-blue-800', icon: Users },
      viewer: { className: 'bg-gray-100 text-gray-800', icon: Users },
    };

    const variant = variants[role] || variants.viewer;
    const Icon = variant.icon;

    return (
      <Badge className={variant.className}>
        <Icon className="w-3 h-3 mr-1" />
        {role.charAt(0).toUpperCase() + role.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2>Team Members</h2>
          <p className="text-gray-600">Manage your team and view member profiles</p>
        </div>
        <Button>
          <Users className="w-4 h-4 mr-2" />
          Add Team Member
        </Button>
      </div>

      {/* Team Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Total Members</p>
                <p className="text-3xl mt-2">{localUsers.length}</p>
              </div>
              <Users className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Admins</p>
                <p className="text-3xl mt-2">{localUsers.filter((u) => u.role === 'admin').length}</p>
              </div>
              <Shield className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Active Members</p>
                <p className="text-3xl mt-2">{localUsers.filter((u) => u.availability).length}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Unavailable</p>
                <p className="text-3xl mt-2">{localUsers.filter((u) => !u.availability).length}</p>
              </div>
              <Clock className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team Member Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {localUsers.map((user) => {
          const stats = getUserStats(user.id);
          const completionRate = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;

          return (
            <Card key={user.id} className={!user.availability ? 'opacity-75 bg-gray-50' : ''}>
              <CardHeader>
                <div className="flex items-start gap-4">
                  <Avatar className="w-16 h-16">
                    <AvatarFallback className="text-xl">
                      {user.name.split(' ').map((n) => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p>{user.name}</p>
                        <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                          <Mail className="w-3 h-3" />
                          <span>{user.email}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      {/* Role Selector */}
                      <div className="relative">
                        <Select
                          value={user.role}
                          onValueChange={(value) => handleRoleChange(user.id, value as UserRole)}
                          disabled={updatingUserId === user.id}
                        >
                          <SelectTrigger className="h-7 text-sm min-w-[120px]">
                            <div className="flex items-center gap-1">
                              {updatingUserId === user.id ? (
                                <Loader2 className="w-3 h-3 animate-spin" />
                              ) : user.role === 'admin' ? (
                                <Shield className="w-3 h-3" />
                              ) : (
                                <Users className="w-3 h-3" />
                              )}
                              <SelectValue />
                            </div>
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="admin">
                              <div className="flex items-center gap-2">
                                <Shield className="w-3 h-3 text-purple-600" />
                                Admin
                              </div>
                            </SelectItem>
                            <SelectItem value="member">
                              <div className="flex items-center gap-2">
                                <Users className="w-3 h-3 text-blue-600" />
                                Member
                              </div>
                            </SelectItem>
                            <SelectItem value="viewer">
                              <div className="flex items-center gap-2">
                                <Users className="w-3 h-3 text-gray-600" />
                                Viewer
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      {!user.availability && (
                        <Badge variant="outline" className="bg-orange-100 text-orange-800">
                          Out of Office
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <div className="space-y-4">
                  {/* Task Statistics */}
                  <div>
                    <p className="text-sm mb-3">Task Overview</p>
                    <div className="grid grid-cols-4 gap-2">
                      <div className="text-center p-2 bg-gray-50 rounded">
                        <p className="text-xl">{stats.total}</p>
                        <p className="text-xs text-gray-600">Total</p>
                      </div>
                      <div className="text-center p-2 bg-blue-50 rounded">
                        <p className="text-xl text-blue-600">{stats.inProgress}</p>
                        <p className="text-xs text-gray-600">Active</p>
                      </div>
                      <div className="text-center p-2 bg-green-50 rounded">
                        <p className="text-xl text-green-600">{stats.completed}</p>
                        <p className="text-xs text-gray-600">Done</p>
                      </div>
                      <div className="text-center p-2 bg-red-50 rounded">
                        <p className="text-xl text-red-600">{stats.blocked}</p>
                        <p className="text-xs text-gray-600">Blocked</p>
                      </div>
                    </div>
                  </div>

                  {/* Completion Rate */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">Completion Rate</span>
                      <span className="text-sm">{completionRate}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full transition-all"
                        style={{ width: `${completionRate}%` }}
                      />
                    </div>
                  </div>

                  {/* Alerts */}
                  {stats.blocked > 0 && (
                    <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-2 rounded">
                      <AlertCircle className="w-4 h-4" />
                      <span>{stats.blocked} blocked task(s) need attention</span>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 pt-2 border-t">
                    <Button variant="outline" size="sm" className="flex-1">
                      View Profile
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1">
                      View Tasks
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Permissions Legend */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Role Permissions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-purple-500 mt-0.5" />
              <div>
                <p>Admin</p>
                <p className="text-sm text-gray-600">
                  Full access to all features, can manage team members, projects, and settings
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Users className="w-5 h-5 text-blue-500 mt-0.5" />
              <div>
                <p>Member</p>
                <p className="text-sm text-gray-600">
                  Can create and edit tasks, participate in projects, and collaborate with team
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Users className="w-5 h-5 text-gray-500 mt-0.5" />
              <div>
                <p>Viewer</p>
                <p className="text-sm text-gray-600">
                  Read-only access to projects and tasks, can view reports and dashboards
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
