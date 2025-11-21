import { test, expect } from '@playwright/test';

/**
 * Authentication Flow E2E Tests
 * Tests the complete user authentication journey
 */

test.describe('Authentication', () => {
  test.beforeEach(async ({ page, context }) => {
    // Clear browser storage and cookies to ensure fresh state
    await context.clearCookies();

    // Navigate to page first
    await page.goto('/');

    // Clear storage after page loads
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // Reload page to apply cleared storage
    await page.reload();
  });

  test('should display login screen on initial load', async ({ page }) => {
    // Should show ProjectGoat logo and title
    await expect(page.locator('text=ProjectGoat')).toBeVisible();

    // Should have email and password inputs
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();

    // Should have login button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Fill in login form
    await page.fill('input[type="email"]', 'sarah@example.com');
    await page.fill('input[type="password"]', 'password123');

    // Click login button
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });

    // Should show user name
    await expect(page.locator('text=Sarah Chen')).toBeVisible();

    // Should show navigation menu
    await expect(page.locator('text=Kanban Board')).toBeVisible();
    await expect(page.locator('text=Task List')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in login form with wrong password
    await page.fill('input[type="email"]', 'sarah@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');

    // Click login button
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('text=/invalid email or password/i')).toBeVisible({ timeout: 5000 });

    // Should still be on login page
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[type="email"]', 'sarah@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });

    // Click logout button (look for LogOut icon or button)
    await page.click('[aria-label="Logout"], button:has-text("Logout"), button:has-text("Log out")');

    // Should redirect back to login page
    await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=ProjectGoat')).toBeVisible();
  });

  test('should persist session across page reloads', async ({ page }) => {
    // Login
    await page.fill('input[type="email"]', 'sarah@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });

    // Reload page
    await page.reload();

    // Should still be logged in and see dashboard
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Sarah Chen')).toBeVisible();
  });
});
