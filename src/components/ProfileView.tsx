import { useState, useEffect } from 'react';
import { User, UserCircle, Shield, History, Edit2, Check, X } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import * as authService from '../services/auth';
import { UserProfile, LoginHistoryEntry } from '../services/auth';

type Tab = 'personal' | 'security' | 'activity';

interface ProfileViewProps {
  currentUser: User;
  onPasswordChangeClick: () => void;
  onProfileUpdate: (updatedUser: User) => void;
}

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

export function ProfileView({
  currentUser,
  onPasswordChangeClick,
  onProfileUpdate,
}: ProfileViewProps) {
  const [activeTab, setActiveTab] = useState<Tab>('personal');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const profileData = await authService.getProfile();
      setProfile(profileData);
      setEditName(profileData.name);
      setEditEmail(profileData.email);
    } catch (err: any) {
      console.error('Failed to load profile:', err);
      setError('Failed to load profile data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    if (!editName.trim() || !editEmail.trim()) {
      setError('Name and email are required');
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      const updatedUser = await authService.updateProfile({
        name: editName,
        email: editEmail,
      });

      // Update local profile state
      if (profile) {
        setProfile({
          ...profile,
          name: updatedUser.name,
          email: updatedUser.email,
        });
      }

      // Notify parent component
      onProfileUpdate(updatedUser);
      setIsEditing(false);
    } catch (err: any) {
      console.error('Failed to update profile:', err);
      setError(err.message || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancelEdit = () => {
    if (profile) {
      setEditName(profile.name);
      setEditEmail(profile.email);
    }
    setIsEditing(false);
    setError(null);
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const tabs = [
    { id: 'personal' as Tab, label: 'Personal Info', icon: UserCircle },
    { id: 'security' as Tab, label: 'Security', icon: Shield },
    { id: 'activity' as Tab, label: 'Login History', icon: History },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-red-600">Failed to load profile</p>
          <Button onClick={loadProfile} className="mt-4">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-semibold">
            {profile.name.split(' ').map((n) => n[0]).join('')}
          </div>
          <div>
            <h2 className="text-2xl font-semibold">{profile.name}</h2>
            <p className="text-gray-600">{profile.email}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="px-6">
          <div className="flex gap-4">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
              {error}
            </div>
          )}

          {activeTab === 'personal' && (
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">Personal Information</h3>
                {!isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                  >
                    <Edit2 className="w-4 h-4 mr-2" />
                    Edit
                  </Button>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  {isEditing ? (
                    <Input
                      id="name"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      disabled={isSaving}
                    />
                  ) : (
                    <p className="mt-1 text-gray-900">{profile.name}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="email">Email Address</Label>
                  {isEditing ? (
                    <Input
                      id="email"
                      type="email"
                      value={editEmail}
                      onChange={(e) => setEditEmail(e.target.value)}
                      disabled={isSaving}
                    />
                  ) : (
                    <p className="mt-1 text-gray-900">{profile.email}</p>
                  )}
                </div>

                <div>
                  <Label>Role</Label>
                  <div className="mt-1">
                    <Badge
                      className={`${
                        profile.role === 'admin'
                          ? 'bg-purple-100 text-purple-800'
                          : profile.role === 'member'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {profile.role.charAt(0).toUpperCase() + profile.role.slice(1)}
                    </Badge>
                  </div>
                </div>

                <div>
                  <Label>Account Created</Label>
                  <p className="mt-1 text-gray-600">
                    {formatDate(profile.createdAt)}
                  </p>
                </div>

                {isEditing && (
                  <div className="flex gap-2 pt-4">
                    <Button
                      onClick={handleSaveProfile}
                      disabled={isSaving}
                      className="flex-1"
                    >
                      <Check className="w-4 h-4 mr-2" />
                      {isSaving ? 'Saving...' : 'Save Changes'}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleCancelEdit}
                      disabled={isSaving}
                      className="flex-1"
                    >
                      <X className="w-4 h-4 mr-2" />
                      Cancel
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          )}

          {activeTab === 'security' && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-6">Security Settings</h3>

              <div className="space-y-6">
                <div>
                  <Label>Password</Label>
                  <p className="text-sm text-gray-600 mb-2">
                    Last changed: {formatDate(profile.passwordChangedAt)}
                  </p>
                  <Button variant="outline" onClick={onPasswordChangeClick}>
                    Change Password
                  </Button>
                </div>

                <div>
                  <Label>Last Login</Label>
                  <p className="mt-1 text-gray-900">
                    {formatDate(profile.lastLoginAt)}
                  </p>
                </div>
              </div>
            </Card>
          )}

          {activeTab === 'activity' && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-6">Recent Login Activity</h3>

              {profile.loginHistory.length === 0 ? (
                <p className="text-gray-600 text-center py-8">
                  No login history available
                </p>
              ) : (
                <div className="space-y-4">
                  {profile.loginHistory.map((entry, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${
                        entry.success
                          ? 'bg-green-50 border-green-200'
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge
                              className={
                                entry.success
                                  ? 'bg-green-600 text-white'
                                  : 'bg-red-600 text-white'
                              }
                            >
                              {entry.success ? 'Success' : 'Failed'}
                            </Badge>
                            <span className="text-sm text-gray-600">
                              {formatDate(entry.attemptedAt)}
                            </span>
                          </div>
                          {entry.ipAddress && (
                            <p className="text-sm text-gray-700">
                              IP: {entry.ipAddress}
                            </p>
                          )}
                          {entry.userAgent && (
                            <p className="text-xs text-gray-600 mt-1 truncate">
                              {entry.userAgent}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
