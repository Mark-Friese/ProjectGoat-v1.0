import { useState, useEffect } from 'react';
import { User, Team, InvitationDetails } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Input } from './ui/input';
import { PasswordInput } from './ui/password-input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { ArrowLeft, Building2, Clock, UserPlus } from 'lucide-react';
import * as authService from '../services/auth';
import logo from '../assets/logo/project-goat-logo.svg';

interface InvitationAcceptScreenProps {
  token: string;
  onAcceptSuccess: (user: User, team: Team) => void;
  onBackToLogin: () => void;
}

export function InvitationAcceptScreen({
  token,
  onAcceptSuccess,
  onBackToLogin,
}: InvitationAcceptScreenProps) {
  const [invitationDetails, setInvitationDetails] = useState<InvitationDetails | null>(null);
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passwordErrors, setPasswordErrors] = useState<string[]>([]);

  useEffect(() => {
    const fetchInvitationDetails = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const details = await authService.getInvitationDetails(token);
        setInvitationDetails(details);
      } catch (err: any) {
        console.error('Failed to fetch invitation:', err);
        if (err.status === 404) {
          setError('This invitation is invalid or has expired.');
        } else if (err.status === 410) {
          setError('This invitation has already been used.');
        } else {
          setError(err.message || 'Failed to load invitation details.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchInvitationDetails();
  }, [token]);

  const validatePassword = (pwd: string): string[] => {
    const errors: string[] = [];
    if (pwd.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(pwd)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(pwd)) errors.push('One lowercase letter');
    if (!/\d/.test(pwd)) errors.push('One number');
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) errors.push('One special character');
    return errors;
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    setPasswordErrors(validatePassword(value));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    const pwdErrors = validatePassword(password);
    if (pwdErrors.length > 0) {
      setError('Password does not meet requirements');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await authService.acceptInvitation(token, name, password);
      onAcceptSuccess(response.user, response.team);
    } catch (err: any) {
      console.error('Failed to accept invitation:', err);
      setError(err.message || 'Failed to accept invitation. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatExpiryDate = (date: Date) => {
    const expiry = new Date(date);
    const now = new Date();
    const diffMs = expiry.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays <= 0) return 'Expired';
    if (diffDays === 1) return 'Expires in 1 day';
    return `Expires in ${diffDays} days`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading invitation...</p>
        </div>
      </div>
    );
  }

  if (error && !invitationDetails) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader className="space-y-4 text-center">
            <div className="flex justify-center">
              <img src={logo} alt="ProjectGoat Logo" className="h-24 w-auto max-w-xs object-contain" />
            </div>
            <CardTitle className="text-2xl">Invalid Invitation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-center">
              <p className="text-red-800">{error}</p>
            </div>
            <Button
              variant="outline"
              className="w-full"
              onClick={onBackToLogin}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-8">
      <Card className="w-full max-w-lg shadow-lg">
        <CardHeader className="space-y-4 text-center">
          <div className="flex justify-center">
            <img src={logo} alt="ProjectGoat Logo" className="h-24 w-auto max-w-xs object-contain" />
          </div>
          <CardTitle className="text-2xl">Join {invitationDetails?.teamName}</CardTitle>
          <CardDescription>
            You've been invited to join a team on ProjectGoat
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Invitation Details */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg space-y-3">
            <div className="flex items-center gap-3">
              <Building2 className="w-5 h-5 text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">Team</p>
                <p className="font-medium">{invitationDetails?.teamName}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <UserPlus className="w-5 h-5 text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">Invited by</p>
                <p className="font-medium">{invitationDetails?.invitedByName}</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Clock className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Your role</p>
                  <Badge
                    className={
                      invitationDetails?.role === 'admin'
                        ? 'bg-purple-100 text-purple-800'
                        : invitationDetails?.role === 'member'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }
                  >
                    {invitationDetails?.role.charAt(0).toUpperCase() +
                      (invitationDetails?.role.slice(1) || '')}
                  </Badge>
                </div>
              </div>
              {invitationDetails?.expiresAt && (
                <span className="text-xs text-gray-500">
                  {formatExpiryDate(invitationDetails.expiresAt)}
                </span>
              )}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">
                Create Your Account
              </h3>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={invitationDetails?.email || ''}
                  disabled
                  className="bg-gray-100"
                />
                <p className="text-xs text-gray-500">
                  This is the email address the invitation was sent to
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="name">Your Name</Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  disabled={isSubmitting}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <PasswordInput
                  id="password"
                  placeholder="Create a strong password"
                  value={password}
                  onChange={(e) => handlePasswordChange(e.target.value)}
                  required
                  disabled={isSubmitting}
                />
                {password && passwordErrors.length > 0 && (
                  <div className="text-xs space-y-1">
                    <p className="text-gray-500">Password requirements:</p>
                    {[
                      'At least 8 characters',
                      'One uppercase letter',
                      'One lowercase letter',
                      'One number',
                      'One special character',
                    ].map((req) => (
                      <p
                        key={req}
                        className={
                          passwordErrors.includes(req) ? 'text-red-500' : 'text-green-500'
                        }
                      >
                        {passwordErrors.includes(req) ? '✗' : '✓'} {req}
                      </p>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <PasswordInput
                  id="confirmPassword"
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={isSubmitting}
                />
                {confirmPassword && password !== confirmPassword && (
                  <p className="text-xs text-red-500">Passwords do not match</p>
                )}
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
                {error}
              </div>
            )}

            <div className="space-y-3">
              <Button
                type="submit"
                className="w-full bg-[#01782B] hover:bg-[#016123] text-white"
                disabled={
                  isSubmitting || passwordErrors.length > 0 || password !== confirmPassword
                }
              >
                {isSubmitting ? 'Joining Team...' : 'Accept Invitation & Join'}
              </Button>

              <Button
                type="button"
                variant="ghost"
                className="w-full"
                onClick={onBackToLogin}
                disabled={isSubmitting}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Login
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
