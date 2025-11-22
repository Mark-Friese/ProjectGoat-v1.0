import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { Card } from './ui/card';
import { User } from '../types';
import { Mail, Shield, Users, Calendar } from 'lucide-react';
import { Button } from './ui/button';
import { Avatar, AvatarFallback } from './ui/avatar';

interface UserProfileDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userId: string | null;
  users: User[];
}

export function UserProfileDialog({
  open,
  onOpenChange,
  userId,
  users,
}: UserProfileDialogProps) {
  // Find the selected user
  const user = users.find(u => u.id === userId);

  if (!user) {
    return null;
  }

  // Role colors
  const roleColors = {
    admin: 'bg-purple-100 text-purple-800',
    member: 'bg-blue-100 text-blue-800',
    viewer: 'bg-gray-100 text-gray-800',
  };

  const getRoleIcon = (role: string) => {
    if (role === 'admin') return Shield;
    return Users;
  };

  const RoleIcon = getRoleIcon(user.role);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Team Member Profile</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* User Header */}
          <div className="flex flex-col items-center text-center pb-4 border-b">
            <Avatar className="w-24 h-24 mb-4">
              <AvatarFallback className="text-3xl bg-blue-600 text-white">
                {user.name.split(' ').map((n) => n[0]).join('')}
              </AvatarFallback>
            </Avatar>

            <h2 className="text-2xl font-bold mb-2">{user.name}</h2>

            <div className="flex items-center gap-2 mb-3">
              <Badge className={roleColors[user.role as keyof typeof roleColors]}>
                <RoleIcon className="w-3 h-3 mr-1" />
                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </Badge>

              {user.availability ? (
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  Available
                </Badge>
              ) : (
                <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                  Out of Office
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-2 text-gray-600">
              <Mail className="w-4 h-4" />
              <span>{user.email}</span>
            </div>
          </div>

          {/* Profile Details */}
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Profile Information</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Role</span>
                <span className="font-medium">
                  {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-600">Status</span>
                <span className={`font-medium ${user.availability ? 'text-green-600' : 'text-orange-600'}`}>
                  {user.availability ? 'Available' : 'Out of Office'}
                </span>
              </div>

              {user.avatar && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Avatar</span>
                  <span className="font-medium">{user.avatar}</span>
                </div>
              )}
            </div>
          </Card>

          {/* Role Permissions */}
          <Card className="p-4 bg-gray-50">
            <h3 className="font-semibold mb-2 text-sm">Role Permissions</h3>
            <p className="text-xs text-gray-600">
              {user.role === 'admin' &&
                'Full access to all features, can manage team members, projects, and settings'}
              {user.role === 'member' &&
                'Can create and edit tasks, participate in projects, and collaborate with team'}
              {user.role === 'viewer' &&
                'Read-only access to projects and tasks, can view reports and dashboards'}
            </p>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2 border-t">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
