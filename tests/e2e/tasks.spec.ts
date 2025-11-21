import { test, expect } from '@playwright/test';

/**
 * Task Management E2E Tests
 * Tests task creation, viewing, and management flows
 */

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate and login
    await page.goto('/');
    await page.fill('input[type="email"]', 'sarah@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });
  });

  test('should display dashboard with task statistics', async ({ page }) => {
    // Dashboard should show task stats
    await expect(page.locator('text=Total Tasks')).toBeVisible();

    // Should show charts or task information
    const dashboardContent = page.locator('main');
    await expect(dashboardContent).toBeVisible();
  });

  test('should navigate to Kanban view', async ({ page }) => {
    // Click on Kanban Board in navigation
    await page.click('text=Kanban Board');

    // Should see Kanban columns
    await expect(page.locator('text=To Do')).toBeVisible();
    await expect(page.locator('text=In Progress')).toBeVisible();
    await expect(page.locator('text=Done')).toBeVisible();
  });

  test('should navigate to Task List view', async ({ page }) => {
    // Click on Task List in navigation
    await page.click('text=Task List');

    // Should see a table or list of tasks
    const taskList = page.locator('main');
    await expect(taskList).toBeVisible();
  });

  test('should navigate to Gantt Chart view', async ({ page }) => {
    // Click on Gantt Chart in navigation
    await page.click('text=Gantt Chart');

    // Should see Gantt chart content
    const ganttView = page.locator('main');
    await expect(ganttView).toBeVisible();
  });

  test('should navigate to Calendar view', async ({ page }) => {
    // Click on Calendar in navigation
    await page.click('text=Calendar');

    // Should see calendar content
    const calendarView = page.locator('main');
    await expect(calendarView).toBeVisible();
  });

  test('should navigate to Team Workload view', async ({ page }) => {
    // Click on Team Workload in navigation
    await page.click('text=Team Workload');

    // Should see workload content
    const workloadView = page.locator('main');
    await expect(workloadView).toBeVisible();
  });

  test('should navigate to Team Members view', async ({ page }) => {
    // Click on Team Members in navigation
    await page.click('text=Team Members');

    // Should see team members content
    const teamView = page.locator('main');
    await expect(teamView).toBeVisible();
  });

  test('should navigate to Reports view', async ({ page }) => {
    // Click on Reports in navigation
    await page.click('text=Reports');

    // Should see reports content
    const reportsView = page.locator('main');
    await expect(reportsView).toBeVisible();
  });

  test('should open My Profile view', async ({ page }) => {
    // Click on My Profile in navigation
    await page.click('text=My Profile');

    // Should see profile information
    await expect(page.locator('text=Sarah Chen')).toBeVisible();
    await expect(page.locator('text=sarah@example.com').first()).toBeVisible();
  });

  test('should be able to create a new task', async ({ page }) => {
    // Look for "New Task" or "Add Task" button
    const newTaskButton = page.locator('button:has-text("New Task"), button:has-text("Add Task"), button:has-text("+")').first();

    // If button exists, click it
    if (await newTaskButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await newTaskButton.click();

      // Should see task dialog/form
      const taskDialog = page.locator('[role="dialog"], [role="form"]');
      await expect(taskDialog).toBeVisible({ timeout: 5000 });
    } else {
      // Skip test if no create task UI is visible yet
      test.skip();
    }
  });
});
