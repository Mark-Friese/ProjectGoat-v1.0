import { useState } from 'react';
import { User } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Input } from './ui/input';
import { PasswordInput } from './ui/password-input';
import { Label } from './ui/label';
import { Checkbox } from './ui/checkbox';
import { Info } from 'lucide-react';
import { toast } from 'sonner';
import * as authService from '../services/auth';
import logo from '../assets/logo/project-goat-logo.svg';

interface LoginScreenProps {
  onLoginSuccess: (user: User) => void;
  onRegisterClick?: () => void;
}

export function LoginScreen({ onLoginSuccess, onRegisterClick }: LoginScreenProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await authService.login(email, password);
      onLoginSuccess(response.user);
    } catch (err: any) {
      console.error('Login failed:', err);

      // Handle rate limiting errors (429)
      if (err.status === 429) {
        setError(err.message || 'Too many login attempts. Please try again later.');
      } else if (err.status === 403) {
        setError(err.message || 'Account has been disabled. Please contact an administrator.');
      } else {
        setError(err.message || 'Invalid email or password. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-6 text-center">
          <div className="flex justify-center">
            <img src={logo} alt="ProjectGoat Logo" className="h-32 w-auto max-w-xs object-contain" />
          </div>
          <CardTitle className="text-2xl">Welcome to ProjectGoat</CardTitle>
          <CardDescription>Sign in to access your project management dashboard</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="max-w-sm mx-auto w-full space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="sarah@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <PasswordInput
                  id="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="remember"
                    checked={rememberMe}
                    onCheckedChange={(checked) => setRememberMe(checked === true)}
                  />
                  <Label htmlFor="remember" className="text-sm cursor-pointer font-normal">
                    Remember me
                  </Label>
                </div>
                <Button
                  type="button"
                  variant="link"
                  className="text-sm px-0 h-auto"
                  onClick={() => toast.info('Password reset not implemented yet')}
                >
                  Forgot password?
                </Button>
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                className="w-full bg-[#01782B] hover:bg-[#016123] text-white"
                disabled={isLoading}
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </Button>

              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex gap-2">
                  <Info className="h-4 w-4 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-semibold text-gray-700 mb-1">Demo credentials:</p>
                    <p className="text-xs text-gray-600">Email: sarah@example.com</p>
                    <p className="text-xs text-gray-600">Password: password123</p>
                  </div>
                </div>
              </div>

              {onRegisterClick && (
                <div className="text-center pt-2">
                  <span className="text-sm text-gray-600">Don't have a team? </span>
                  <Button
                    type="button"
                    variant="link"
                    className="text-sm px-0 h-auto"
                    onClick={onRegisterClick}
                  >
                    Create one
                  </Button>
                </div>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
