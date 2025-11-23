import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  // Recording...
});await page.goto('http://localhost:3000/');
await page.getByRole('button', { name: 'My Profile' }).click();
await page.locator('div').filter({ hasText: 'Failed to load profileRetry' }).nth(3).click();
await page.getByRole('button', { name: 'Retry' }).click();