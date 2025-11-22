import { test, expect } from '@playwright/test';

test('editing existing task shows task details', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  
  // Navigate to Kanban board
  await page.getByRole('button', { name: 'Kanban Board' }).click();
  
  // Click on existing task
  await page.getByText('Setup CI/CD pipeline').click();
  
  // Verify the task dialog opened
  await expect(page.getByRole('dialog')).toBeVisible();
  
  // Verify form fields are populated with task data
  await expect(page.getByLabel('Task Title')).toHaveValue('Setup CI/CD pipeline');
  
  // Verify description is not empty
  const description = await page.getByLabel('Description').inputValue();
  expect(description).not.toBe('');
  
  // Verify status dropdown has a value selected
  await expect(page.getByLabel('Status')).not.toBeEmpty();
});