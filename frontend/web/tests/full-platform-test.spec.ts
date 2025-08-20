import { test, expect } from '@playwright/test';

test.describe('Complete OmniFunnel Platform Functionality', () => {
  
  test('complete end-to-end workflow: site → cluster → tracking → results → score', async ({ page }) => {
    // 1. Start at homepage
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('OmniFunnel AI Visibility');
    
    // 2. Navigate to tracking
    await page.click('text=Start Tracking');
    await page.waitForURL('**/tracking');
    
    // 3. Create a site
    await page.click('text=+ Add Site');
    await page.fill('input[placeholder="Domain (e.g., example.com)"]', 'playwright-test.com');
    await page.selectOption('select', 'wordpress');
    await page.click('button:text("Create Site")');
    
    // Wait for site to appear and select it
    await expect(page.locator('text=playwright-test.com')).toBeVisible({ timeout: 10000 });
    await page.click('text=playwright-test.com');
    
    // 4. Create a cluster  
    await page.click('text=+ Add Cluster');
    await page.fill('input[placeholder="Cluster name"]', 'Playwright Test Cluster');
    await page.fill('textarea[placeholder*="Seed prompt"]', 'best AI testing tools');
    await page.click('button:text("Create Cluster")');
    
    // Wait for cluster to appear and select it
    await expect(page.locator('text=Playwright Test Cluster')).toBeVisible({ timeout: 10000 });
    await page.click('text=Playwright Test Cluster');
    
    // 5. Run AI tracking
    await page.selectOption('select[class*="px-3 py-2 border"]', 'chatgpt');
    await page.fill('input[type="number"]', '1');
    await page.click('button:text("Start AI Tracking Run")');
    
    // Wait for run completion indicator
    await expect(page.locator('text=Recent Runs')).toBeVisible({ timeout: 15000 });
    
    // 6. View results in dashboard
    await page.click('text=Dashboard', { force: true });
    await page.waitForURL('**/dashboard');
    
    // Check that we can see our site and cluster
    await page.selectOption('select', { label: 'playwright-test.com' });
    await page.selectOption('select >> nth=1', { label: 'Playwright Test Cluster' });
    
    // Should see answers
    await expect(page.locator('text=Recent Answers')).toBeVisible();
    
    // 7. Check AI Visibility Score
    await page.click('text=AI Score™');
    await page.waitForURL('**/scores');
    
    // Select our site and cluster
    await page.selectOption('select', { label: 'playwright-test.com' });
    await page.selectOption('select >> nth=1', { label: 'Playwright Test Cluster' });
    
    // Calculate score
    await page.click('button:text("Calculate Score")');
    
    // Wait for score to appear
    await expect(page.locator('text=Overall AI Visibility Score')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=Score Components')).toBeVisible();
    await expect(page.locator('text=Recommendations')).toBeVisible();
    
    console.log('✅ COMPLETE END-TO-END WORKFLOW SUCCESSFUL!');
  });

  test('API endpoints are functional', async ({ page }) => {
    // Test health endpoints
    const trackerHealth = await page.request.get('http://localhost:8001/health');
    expect(trackerHealth.ok()).toBeTruthy();
    
    const scoreHealth = await page.request.get('http://localhost:8004/health');
    expect(scoreHealth.ok()).toBeTruthy();
    
    // Test engines endpoint
    const engines = await page.request.get('http://localhost:8001/v1/engines');
    expect(engines.ok()).toBeTruthy();
    const enginesData = await engines.json();
    expect(enginesData.engines).toContain('chatgpt');
    expect(enginesData.engines).toContain('claude');
    expect(enginesData.engines).toContain('gemini');
  });

  test('real AI integration produces actual responses', async ({ page }) => {
    // Create site via API
    const siteResponse = await page.request.post('http://localhost:8001/v1/sites', {
      data: {
        domain: 'api-test.com',
        cms_type: 'wordpress', 
        tenant_id: 1
      }
    });
    expect(siteResponse.ok()).toBeTruthy();
    const site = await siteResponse.json();
    
    // Create cluster via API
    const clusterResponse = await page.request.post(`http://localhost:8001/v1/sites/${site.site_id}/clusters`, {
      data: {
        name: 'API Test Cluster',
        seed_prompt: 'top AI productivity tools',
        keywords: ['ai', 'productivity']
      }
    });
    expect(clusterResponse.ok()).toBeTruthy();
    const cluster = await clusterResponse.json();
    
    // Run tracking with real AI
    const runResponse = await page.request.post(`http://localhost:8001/v1/clusters/${cluster.cluster_id}/run`, {
      data: {
        engine: 'chatgpt',
        variant_sample: 1
      }
    });
    expect(runResponse.ok()).toBeTruthy();
    
    // Check answers were generated
    const answersResponse = await page.request.get(`http://localhost:8001/v1/clusters/${cluster.cluster_id}/answers`);
    expect(answersResponse.ok()).toBeTruthy();
    const answers = await answersResponse.json();
    
    expect(answers.length).toBeGreaterThan(0);
    expect(answers[0].raw_text).toBeTruthy();
    expect(answers[0].engine).toBe('chatgpt');
    expect(answers[0].citations).toBeDefined();
    
    console.log('✅ REAL AI INTEGRATION WORKING!');
    console.log('Response length:', answers[0].raw_text.length);
    console.log('Citations found:', answers[0].citations.length);
  });
});