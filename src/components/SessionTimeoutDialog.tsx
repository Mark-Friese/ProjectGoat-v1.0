import { useEffect, useState } from 'react';
import { Button } from './ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Clock } from 'lucide-react';

interface SessionTimeoutDialogProps {
  open: boolean;
  timeRemaining: number;
  onExtendSession: () => void;
  onLogout: () => void;
}

export function SessionTimeoutDialog({
  open,
  timeRemaining: initialTimeRemaining,
  onExtendSession,
  onLogout,
}: SessionTimeoutDialogProps) {
  const [timeRemaining, setTimeRemaining] = useState(initialTimeRemaining);

  useEffect(() => {
    setTimeRemaining(initialTimeRemaining);
  }, [initialTimeRemaining]);

  useEffect(() => {
    if (!open) {
      return;
    }

    // Update countdown every second
    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        const newTime = prev - 1;
        if (newTime <= 0) {
          // Time's up - auto logout
          onLogout();
          return 0;
        }
        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [open, onLogout]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent
        className="sm:max-w-[425px]"
        onPointerDownOutside={(e) => e.preventDefault()}
        onEscapeKeyDown={(e) => e.preventDefault()}
      >
        <DialogHeader>
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-yellow-600" />
            <DialogTitle>Session Timeout Warning</DialogTitle>
          </div>
          <DialogDescription>
            Your session is about to expire due to inactivity. You will be
            automatically logged out in:
          </DialogDescription>
        </DialogHeader>

        <div className="py-6">
          <div className="text-center">
            <div className="text-6xl font-bold text-yellow-600 mb-2">
              {formatTime(timeRemaining)}
            </div>
            <p className="text-sm text-gray-500">
              Click "Stay Logged In" to continue your session
            </p>
          </div>
        </div>

        <DialogFooter className="flex gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={onLogout}
            className="flex-1"
          >
            Logout Now
          </Button>
          <Button
            type="button"
            onClick={onExtendSession}
            className="flex-1"
          >
            Stay Logged In
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
