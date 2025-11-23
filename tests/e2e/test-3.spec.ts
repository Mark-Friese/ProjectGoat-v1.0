import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:3001/');
  await page.getByRole('button', { name: 'Team Members' }).click();
  await page.getByRole('button', { name: 'View Profile' }).first().click();
});
