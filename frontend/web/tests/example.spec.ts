import { test, expect } from '@playwright/test';

test('homepage loads correctly', async ({ page }) => {
  await page.goto('/');
  
  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/OmniFunnel/);
});

test('basic navigation', async ({ page }) => {
  await page.goto('/');
  
  // Check that the page loads without errors
  await expect(page.locator('body')).toBeVisible();
});