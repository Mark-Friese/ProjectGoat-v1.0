import { useState, useEffect } from 'react';
import { Team, TeamMember, Invitation, UserRole, User } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from './ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import {
  Building2,
  UserPlus,
  Mail,
  MoreVertical,
  Shield,
  UserMinus,
  Clock,
  Copy,
  Check,
  AlertTriangle,
} from 'lucide-react';
import { toast } from 'sonner';
import * as authService from '../services/auth';

interface TeamSettingsViewProps {
  team: Team;
  currentUser: User;
  onTeamUpdate: (team: Team) => void;
}

export function TeamSettingsView({ team, currentUser, onTeamUpdate }: TeamSettingsViewProps) {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [teamName, setTeamName] = useState(team.name);
  const [isEditingName, setIsEditingName] = useState(false);
  const [isSavingName, setIsSavingName] = useState(false);

  // Dialog states
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);
  const [isRemoveDialogOpen, setIsRemoveDialogOpen] = useState(false);
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null);

  // Invite form state
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<UserRole>('member');
  const [isInviting, setIsInviting] = useState(false);

  // Remove member state
  const [removeTaskAction, setRemoveTaskAction] = useState<'unassign' | 'reassign_admin' | 'keep'>(
    'unassign'
  );
  const [isRemoving, setIsRemoving] = useState(false);

  // Role change state
  const [newRole, setNewRole] = useState<UserRole>('member');
  const [isChangingRole, setIsChangingRole] = useState(false);

  // Copy invitation link state
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const isAdmin =
    members.find((m) => m.id === currentUser.id)?.role === 'admin' || currentUser.role === 'admin';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [membersData, invitationsData] = await Promise.all([
        authService.getTeamMembers(),
        isAdmin ? authService.getInvitations() : Promise.resolve([]),
      ]);
      setMembers(membersData);
      setInvitations(invitationsData);
    } catch (err) {
      console.error('Failed to load team data:', err);
      toast.error('Failed to load team data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveTeamName = async () => {
    if (!teamName.trim() || teamName === team.name) {
      setIsEditingName(false);
      return;
    }

    try {
      setIsSavingName(true);
      const updatedTeam = await authService.updateTeam(teamName);
      onTeamUpdate(updatedTeam);
      setIsEditingName(false);
      toast.success('Team name updated');
    } catch (err) {
      console.error('Failed to update team name:', err);
      toast.error('Failed to update team name');
    } finally {
      setIsSavingName(false);
    }
  };

  const handleInvite = async () => {
    if (!inviteEmail.trim()) return;

    try {
      setIsInviting(true);
      const invitation = await authService.createInvitation(inviteEmail, inviteRole);
      setInvitations([...invitations, invitation]);
      setInviteEmail('');
      setInviteRole('member');
      setIsInviteDialogOpen(false);
      toast.success(`Invitation sent to ${inviteEmail}`);
    } catch (err: any) {
      console.error('Failed to send invitation:', err);
      toast.error(err.message || 'Failed to send invitation');
    } finally {
      setIsInviting(false);
    }
  };

  const handleRevokeInvitation = async (invitationId: string) => {
    try {
      await authService.revokeInvitation(invitationId);
      setInvitations(invitations.filter((i) => i.id !== invitationId));
      toast.success('Invitation revoked');
    } catch (err) {
      console.error('Failed to revoke invitation:', err);
      toast.error('Failed to revoke invitation');
    }
  };

  const handleRemoveMember = async () => {
    if (!selectedMember) return;

    try {
      setIsRemoving(true);
      await authService.removeMember(selectedMember.id, removeTaskAction);
      setMembers(members.filter((m) => m.id !== selectedMember.id));
      setIsRemoveDialogOpen(false);
      setSelectedMember(null);
      toast.success(`${selectedMember.name} has been removed from the team`);
    } catch (err: any) {
      console.error('Failed to remove member:', err);
      toast.error(err.message || 'Failed to remove member');
    } finally {
      setIsRemoving(false);
    }
  };

  const handleChangeRole = async () => {
    if (!selectedMember) return;

    try {
      setIsChangingRole(true);
      const updatedMember = await authService.updateMemberRole(selectedMember.id, newRole);
      setMembers(members.map((m) => (m.id === selectedMember.id ? updatedMember : m)));
      setIsRoleDialogOpen(false);
      setSelectedMember(null);
      toast.success(`${selectedMember.name}'s role updated to ${newRole}`);
    } catch (err: any) {
      console.error('Failed to change role:', err);
      toast.error(err.message || 'Failed to change role');
    } finally {
      setIsChangingRole(false);
    }
  };

  const copyInvitationLink = (invitation: Invitation) => {
    // Construct the invitation link
    const baseUrl = window.location.origin;
    const inviteLink = `${baseUrl}?invite=${invitation.id}`;
    navigator.clipboard.writeText(inviteLink);
    setCopiedId(invitation.id);
    setTimeout(() => setCopiedId(null), 2000);
    toast.success('Invitation link copied to clipboard');
  };

  const formatDate = (date: Date | string) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      case 'member':
        return 'bg-blue-100 text-blue-800';
      case 'viewer':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Team Info Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Building2 className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <CardTitle>Team Settings</CardTitle>
              <CardDescription>Manage your team's information and members</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Team Name</Label>
            {isEditingName ? (
              <div className="flex gap-2">
                <Input
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  disabled={isSavingName}
                />
                <Button onClick={handleSaveTeamName} disabled={isSavingName}>
                  {isSavingName ? 'Saving...' : 'Save'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setTeamName(team.name);
                    setIsEditingName(false);
                  }}
                  disabled={isSavingName}
                >
                  Cancel
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-lg font-medium">{team.name}</span>
                {isAdmin && (
                  <Button variant="ghost" size="sm" onClick={() => setIsEditingName(true)}>
                    Edit
                  </Button>
                )}
              </div>
            )}
          </div>

          <div className="flex gap-4 text-sm text-gray-500">
            <div>
              <span className="font-medium">Account Type:</span>{' '}
              {team.accountType === 'multi' ? 'Multi-Team' : 'Single Team'}
            </div>
            <div>
              <span className="font-medium">Created:</span> {formatDate(team.createdAt)}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Team Members Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Team Members</CardTitle>
              <CardDescription>{members.length} member(s)</CardDescription>
            </div>
            {isAdmin && (
              <Button onClick={() => setIsInviteDialogOpen(true)}>
                <UserPlus className="w-4 h-4 mr-2" />
                Invite Member
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {members.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                    {member.name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{member.name}</span>
                      {member.id === currentUser.id && (
                        <span className="text-xs text-gray-500">(you)</span>
                      )}
                    </div>
                    <span className="text-sm text-gray-500">{member.email}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={getRoleBadgeColor(member.role)}>
                    {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                  </Badge>
                  {isAdmin && member.id !== currentUser.id && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() => {
                            setSelectedMember(member);
                            setNewRole(member.role);
                            setIsRoleDialogOpen(true);
                          }}
                        >
                          <Shield className="w-4 h-4 mr-2" />
                          Change Role
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-red-600"
                          onClick={() => {
                            setSelectedMember(member);
                            setIsRemoveDialogOpen(true);
                          }}
                        >
                          <UserMinus className="w-4 h-4 mr-2" />
                          Remove from Team
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Pending Invitations Card */}
      {isAdmin && invitations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Pending Invitations</CardTitle>
            <CardDescription>{invitations.length} pending invitation(s)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {invitations.map((invitation) => (
                <div
                  key={invitation.id}
                  className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-yellow-600" />
                    <div>
                      <span className="font-medium">{invitation.email}</span>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Badge className={getRoleBadgeColor(invitation.role)}>
                          {invitation.role}
                        </Badge>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          Expires {formatDate(invitation.expiresAt)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyInvitationLink(invitation)}
                    >
                      {copiedId === invitation.id ? (
                        <Check className="w-4 h-4" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => handleRevokeInvitation(invitation.id)}
                    >
                      Revoke
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Invite Member Dialog */}
      <Dialog open={isInviteDialogOpen} onOpenChange={setIsInviteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invite Team Member</DialogTitle>
            <DialogDescription>
              Send an invitation email to add a new member to your team.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="inviteEmail">Email Address</Label>
              <Input
                id="inviteEmail"
                type="email"
                placeholder="colleague@example.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="inviteRole">Role</Label>
              <Select value={inviteRole} onValueChange={(v) => setInviteRole(v as UserRole)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin - Full access</SelectItem>
                  <SelectItem value="member">Member - Can create and edit</SelectItem>
                  <SelectItem value="viewer">Viewer - Read-only access</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsInviteDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleInvite} disabled={isInviting || !inviteEmail.trim()}>
              {isInviting ? 'Sending...' : 'Send Invitation'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Remove Member Dialog */}
      <Dialog open={isRemoveDialogOpen} onOpenChange={setIsRemoveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              Remove Team Member
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to remove {selectedMember?.name} from the team?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>What should happen to their assigned tasks?</Label>
              <Select
                value={removeTaskAction}
                onValueChange={(v) => setRemoveTaskAction(v as typeof removeTaskAction)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="unassign">Unassign all tasks</SelectItem>
                  <SelectItem value="reassign_admin">Reassign to team admin</SelectItem>
                  <SelectItem value="keep">Keep current assignments</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsRemoveDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleRemoveMember} disabled={isRemoving}>
              {isRemoving ? 'Removing...' : 'Remove Member'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Change Role Dialog */}
      <Dialog open={isRoleDialogOpen} onOpenChange={setIsRoleDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change Member Role</DialogTitle>
            <DialogDescription>
              Update the role for {selectedMember?.name}.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="newRole">New Role</Label>
              <Select value={newRole} onValueChange={(v) => setNewRole(v as UserRole)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin - Full access</SelectItem>
                  <SelectItem value="member">Member - Can create and edit</SelectItem>
                  <SelectItem value="viewer">Viewer - Read-only access</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsRoleDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleChangeRole} disabled={isChangingRole}>
              {isChangingRole ? 'Updating...' : 'Update Role'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
