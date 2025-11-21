/**
 * Session Activity Monitor
 * Tracks user activity and monitors session timeout
 */

// Session timeout configuration (must match backend)
const IDLE_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
const WARNING_BEFORE_TIMEOUT_MS = 2 * 60 * 1000; // Warn 2 minutes before timeout
const SESSION_CHECK_INTERVAL_MS = 60 * 1000; // Check every minute

export type SessionTimeoutCallback = (timeRemaining: number) => void;
export type SessionExpiredCallback = () => void;

class SessionMonitor {
  private lastActivityTime: number = Date.now();
  private checkInterval: NodeJS.Timeout | null = null;
  private isActive: boolean = false;

  private timeoutWarningCallback: SessionTimeoutCallback | null = null;
  private sessionExpiredCallback: SessionExpiredCallback | null = null;

  /**
   * Start monitoring user activity
   */
  start(
    onTimeoutWarning: SessionTimeoutCallback,
    onSessionExpired: SessionExpiredCallback
  ): void {
    if (this.isActive) {
      return;
    }

    this.isActive = true;
    this.lastActivityTime = Date.now();
    this.timeoutWarningCallback = onTimeoutWarning;
    this.sessionExpiredCallback = onSessionExpired;

    // Track user activity
    this.addActivityListeners();

    // Start periodic session check
    this.checkInterval = setInterval(() => {
      this.checkSessionTimeout();
    }, SESSION_CHECK_INTERVAL_MS);
  }

  /**
   * Stop monitoring
   */
  stop(): void {
    this.isActive = false;
    this.removeActivityListeners();

    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  /**
   * Reset activity timer (called when user interacts with app)
   */
  private resetActivity = (): void => {
    this.lastActivityTime = Date.now();
  };

  /**
   * Add event listeners for user activity
   */
  private addActivityListeners(): void {
    // Mouse activity
    window.addEventListener('mousemove', this.resetActivity);
    window.addEventListener('mousedown', this.resetActivity);
    window.addEventListener('click', this.resetActivity);
    window.addEventListener('scroll', this.resetActivity);

    // Keyboard activity
    window.addEventListener('keydown', this.resetActivity);
    window.addEventListener('keypress', this.resetActivity);

    // Touch activity (for mobile)
    window.addEventListener('touchstart', this.resetActivity);
    window.addEventListener('touchmove', this.resetActivity);
  }

  /**
   * Remove event listeners
   */
  private removeActivityListeners(): void {
    window.removeEventListener('mousemove', this.resetActivity);
    window.removeEventListener('mousedown', this.resetActivity);
    window.removeEventListener('click', this.resetActivity);
    window.removeEventListener('scroll', this.resetActivity);
    window.removeEventListener('keydown', this.resetActivity);
    window.removeEventListener('keypress', this.resetActivity);
    window.removeEventListener('touchstart', this.resetActivity);
    window.removeEventListener('touchmove', this.resetActivity);
  }

  /**
   * Check if session is approaching timeout or has expired
   */
  private checkSessionTimeout(): void {
    if (!this.isActive) {
      return;
    }

    const timeSinceActivity = Date.now() - this.lastActivityTime;
    const timeRemaining = IDLE_TIMEOUT_MS - timeSinceActivity;

    if (timeRemaining <= 0) {
      // Session expired
      if (this.sessionExpiredCallback) {
        this.sessionExpiredCallback();
      }
      this.stop();
    } else if (timeRemaining <= WARNING_BEFORE_TIMEOUT_MS) {
      // Show warning
      if (this.timeoutWarningCallback) {
        this.timeoutWarningCallback(Math.floor(timeRemaining / 1000));
      }
    }
  }

  /**
   * Manually extend session (called when user clicks "Stay Logged In")
   */
  extendSession(): void {
    this.lastActivityTime = Date.now();
  }

  /**
   * Get time remaining until timeout (in seconds)
   */
  getTimeRemaining(): number {
    const timeSinceActivity = Date.now() - this.lastActivityTime;
    const timeRemaining = IDLE_TIMEOUT_MS - timeSinceActivity;
    return Math.max(0, Math.floor(timeRemaining / 1000));
  }
}

// Export singleton instance
export const sessionMonitor = new SessionMonitor();
