import { test, expect } from '@playwright/test';

test.describe('OmniFunnel AI Visibility Platform Functionality', () => {
  
  test('homepage loads and shows service status', async ({ page }) => {
    await page.goto('/');
    
    // Check title and main heading
    await expect(page).toHaveTitle(/OmniFunnel/);
    await expect(page.locator('h1')).toContainText('OmniFunnel AI Visibility');
    
    // Check navigation buttons exist
    await expect(page.locator('text=AI Score™')).toBeVisible();
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator('text=Start Tracking')).toBeVisible();
    
    // Check service status section
    await expect(page.locator('text=Service Status')).toBeVisible();
    await expect(page.locator('text=AI Engines')).toBeVisible();
  });

  test('can navigate to tracking page and create site', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to tracking page
    await page.click('text=Start Tracking');
    await expect(page.url()).toContain('/tracking');
    
    // Check tracking page elements
    await expect(page.locator('h1')).toContainText('AI Visibility Tracking');
    await expect(page.locator('text=Sites')).toBeVisible();
    
    // Try to create a site
    await page.click('text=+ Add Site');
    
    // Fill site form
    await page.fill('input[placeholder="Domain (e.g., example.com)"]', 'testcompany.com');
    await page.selectOption('select', 'wordpress');
    
    // Submit form
    await page.click('button:text("Create Site")');
    
    // Wait for site to appear in list
    await expect(page.locator('text=testcompany.com')).toBeVisible({ timeout: 5000 });
  });

  test('can create cluster after creating site', async ({ page }) => {
    await page.goto('/tracking');
    
    // Create site first
    await page.click('text=+ Add Site');
    await page.fill('input[placeholder="Domain (e.g., example.com)"]', 'demo-site.com');
    await page.click('button:text("Create Site")');
    await expect(page.locator('text=demo-site.com')).toBeVisible();
    
    // Select the site
    await page.click('text=demo-site.com');
    
    // Create cluster
    await page.click('text=+ Add Cluster');
    
    // Fill cluster form
    await page.fill('input[placeholder="Cluster name"]', 'AI SEO Tools');
    await page.fill('input[placeholder="Description (optional)"]', 'Testing AI SEO tool queries');
    await page.fill('textarea[placeholder*="Seed prompt"]', 'best AI SEO tools for agencies');
    
    // Submit cluster form
    await page.click('button:text("Create Cluster")');
    
    // Wait for cluster to appear
    await expect(page.locator('text=AI SEO Tools')).toBeVisible({ timeout: 5000 });
  });

  test('can run tracking for a cluster', async ({ page }) => {
    await page.goto('/tracking');
    
    // Create site and cluster first
    await page.click('text=+ Add Site');
    await page.fill('input[placeholder="Domain (e.g., example.com)"]', 'tracking-test.com');
    await page.click('button:text("Create Site")');
    await page.click('text=tracking-test.com');
    
    await page.click('text=+ Add Cluster');
    await page.fill('input[placeholder="Cluster name"]', 'Test Cluster');
    await page.fill('textarea[placeholder*="Seed prompt"]', 'AI marketing tools');
    await page.click('button:text("Create Cluster")');
    
    // Select the cluster
    await page.click('text=Test Cluster');
    
    // Configure tracking run
    await page.selectOption('select[class*="px-3 py-2 border"]', 'chatgpt');
    await page.fill('input[type="number"]', '10');
    
    // Start tracking
    await page.click('button:text("Start AI Tracking Run")');
    
    // Check for success feedback
    await expect(page.locator('text=Recent Runs')).toBeVisible({ timeout: 10000 });
  });

  test('can view dashboard with results', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check dashboard elements
    await expect(page.locator('h1')).toContainText('AI Visibility Dashboard');
    await expect(page.locator('text=Site')).toBeVisible();
    await expect(page.locator('text=Cluster')).toBeVisible();
    await expect(page.locator('text=Engine Filter')).toBeVisible();
  });

  test('can navigate to AI Score page', async ({ page }) => {
    await page.goto('/scores');
    
    // Check scores page elements
    await expect(page.locator('h1')).toContainText('AI Visibility Score');
    await expect(page.locator('text=Track your brand\'s performance across AI engines')).toBeVisible();
    await expect(page.locator('button:text("Calculate Score")')).toBeVisible();
  });

  test('API health endpoints respond correctly', async ({ page }) => {
    // Test backend health endpoint directly
    const response = await page.request.get('http://localhost:8001/health');
    expect(response.ok()).toBeTruthy();
    
    const health = await response.json();
    expect(health.status).toBe('ok');
    expect(health.service).toBe('tracker');
    expect(health.engines).toBeDefined();
  });

  test('engines endpoint returns expected data', async ({ page }) => {
    const response = await page.request.get('http://localhost:8001/v1/engines');
    expect(response.ok()).toBeTruthy();
    
    const engines = await response.json();
    expect(engines.engines).toContain('chatgpt');
    expect(engines.engines).toContain('claude');
    expect(engines.engines).toContain('gemini');
    expect(engines.count).toBeGreaterThan(0);
  });
});