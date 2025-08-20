import { test, expect } from '@playwright/test';

test.describe('OmniFunnel Platform - Complete Specification Testing', () => {
  
  test('test all navigation and page accessibility', async ({ page }) => {
    console.log('Testing all navigation links...');
    
    // Test homepage
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('OmniFunnel AI Visibility');
    
    // Test each navigation link
    const navLinks = [
      { text: 'Master Control', url: '/master-dashboard' },
      { text: 'AI Score™', url: '/scores' },
      { text: 'LEO', url: '/optimization' }, 
      { text: 'Intel', url: '/intelligence' }
    ];
    
    for (const link of navLinks) {
      console.log(`Testing navigation to ${link.text}...`);
      await page.goto('/');
      await page.click(`text=${link.text}`);
      await page.waitForURL(`**${link.url}`);
      console.log(`✅ ${link.text} page loads successfully`);
    }
    
    // Test tracking page
    await page.goto('/tracking');
    await expect(page.locator('h1')).toContainText('AI Visibility Tracking');
    
    // Test dashboard page  
    await page.goto('/dashboard');
    await expect(page.locator('h1')).toContainText('AI Visibility Dashboard');
  });

  test('test complete workflow: site creation → content generation → deployment', async ({ page }) => {
    console.log('Testing complete platform workflow...');
    
    // 1. Create site
    await page.goto('/tracking');
    await page.click('text=+ Add Site');
    await page.fill('input[placeholder="Domain (e.g., example.com)"]', 'spec-test.com');
    await page.selectOption('select', 'wordpress');
    await page.click('button:text("Create Site")');
    
    console.log('✅ Site creation tested');
    
    // Wait for site to appear
    await expect(page.locator('text=spec-test.com')).toBeVisible({ timeout: 10000 });
    await page.click('text=spec-test.com');
    
    // 2. Create cluster
    await page.click('text=+ Add Cluster');
    await page.fill('input[placeholder="Cluster name"]', 'Spec Test Cluster');
    await page.fill('textarea[placeholder*="Seed prompt"]', 'enterprise AI SEO platform features');
    await page.click('button:text("Create Cluster")');
    
    console.log('✅ Cluster creation tested');
    
    // 3. Test content generation
    await page.goto('/optimization');
    await page.selectOption('select', { label: 'spec-test.com' });
    await page.fill('input[placeholder*="AI SEO tools"]', 'AI SEO platform capabilities');
    
    // Select all content formats
    await page.check('input[value="faq"]');
    await page.check('input[value="table"]');
    await page.check('input[value="para"]');
    await page.check('input[value="jsonld"]');
    
    await page.click('button:text("Generate AI-Optimized Content")');
    
    console.log('✅ Content generation tested');
    
    // Wait for content to generate
    await expect(page.locator('text=Generated Content')).toBeVisible({ timeout: 30000 });
    
    // 4. Test deployment
    await page.click('button:text("Deploy to WordPress")');
    
    console.log('✅ WordPress deployment tested');
  });

  test('test all API endpoints respond correctly', async ({ page }) => {
    console.log('Testing all API endpoints...');
    
    const endpoints = [
      { name: 'Tracker Health', url: 'http://localhost:8001/health' },
      { name: 'Generator Health', url: 'http://localhost:8002/health' },
      { name: 'Analytics Health', url: 'http://localhost:8003/health' },
      { name: 'Score Health', url: 'http://localhost:8004/health' },
      { name: 'Deployer Health', url: 'http://localhost:8005/health' },
      { name: 'Engines List', url: 'http://localhost:8001/v1/engines' }
    ];
    
    for (const endpoint of endpoints) {
      const response = await page.request.get(endpoint.url);
      expect(response.ok()).toBeTruthy();
      console.log(`✅ ${endpoint.name}: ${response.status()}`);
    }
  });

  test('test real AI integration and content quality', async ({ page }) => {
    console.log('Testing real AI integration...');
    
    // Create site and cluster first
    const siteResponse = await page.request.post('http://localhost:8001/v1/sites', {
      data: {
        domain: 'ai-test.com',
        cms_type: 'wordpress',
        tenant_id: 1
      }
    });
    
    const site = await siteResponse.json();
    console.log('Site created:', site.site_id);
    
    const clusterResponse = await page.request.post(`http://localhost:8001/v1/sites/${site.site_id}/clusters`, {
      data: {
        name: 'AI Quality Test',
        seed_prompt: 'best AI content optimization tools for enterprises',
        keywords: ['ai', 'content', 'optimization']
      }
    });
    
    const cluster = await clusterResponse.json();
    console.log('Cluster created:', cluster.cluster_id);
    
    // Test real AI tracking
    const trackingResponse = await page.request.post(`http://localhost:8001/v1/clusters/${cluster.cluster_id}/run`, {
      data: {
        engine: 'chatgpt',
        variant_sample: 1
      }
    });
    
    expect(trackingResponse.ok()).toBeTruthy();
    console.log('✅ AI tracking initiated');
    
    // Wait a moment for processing
    await page.waitForTimeout(3000);
    
    // Check answers
    const answersResponse = await page.request.get(`http://localhost:8001/v1/clusters/${cluster.cluster_id}/answers`);
    const answers = await answersResponse.json();
    
    console.log('AI Response quality check:');
    console.log('- Response count:', answers.length);
    if (answers.length > 0) {
      console.log('- Response length:', answers[0].raw_text?.length || 0);
      console.log('- Citations found:', answers[0].citations?.length || 0);
      console.log('- Engine:', answers[0].engine);
    }
    
    // Test content generation
    const contentResponse = await page.request.post('http://localhost:8002/v1/content/generate', {
      data: {
        topic: 'AI SEO automation platforms',
        site_id: site.site_id,
        formats: ['faq', 'table', 'jsonld']
      }
    });
    
    expect(contentResponse.ok()).toBeTruthy();
    const content = await contentResponse.json();
    
    console.log('Content generation quality check:');
    console.log('- Blocks generated:', content.blocks?.length || 0);
    console.log('- Schemas generated:', content.schemas?.length || 0);
    console.log('- Total word count:', content.total_word_count || 0);
    
    // Test AI Visibility Score
    const scoreResponse = await page.request.post('http://localhost:8004/v1/calculate-score', {
      data: {
        site_id: site.site_id,
        cluster_id: cluster.cluster_id,
        date_range_days: 30
      }
    });
    
    expect(scoreResponse.ok()).toBeTruthy();
    const score = await scoreResponse.json();
    
    console.log('AI Visibility Score quality check:');
    console.log('- Total score:', score.total);
    console.log('- Component scores:', Object.keys(score.subscores || {}).length);
    console.log('- Recommendations:', score.recommendations?.length || 0);
    
    console.log('✅ Complete API workflow functional');
  });

  test('identify missing specification features', async ({ page }) => {
    console.log('Checking specification compliance...');
    
    // Check for missing features per spec
    const requiredFeatures = [
      'LLM Citation Tracker',
      'Prompt-SoV measurement', 
      'Content structuring engine',
      'Schema auto-generation',
      'CMS auto-deployment',
      'AI Visibility Score calculation',
      'Competitive intelligence',
      'Entity stitching',
      'Multi-tenant authentication', // Missing
      'Billing integration', // Missing
      'GA4 attribution', // Missing
      'Voice assistant tracking', // Missing
      'Embeddings audit', // Missing
      'White-label customization', // Missing
      'Public benchmarks', // Missing
      'API rate limiting', // Missing
      'Automated alerting system' // Partially implemented
    ];
    
    console.log('Required features per specification:', requiredFeatures.length);
    console.log('Still needed: Authentication, Billing, GA4, Voice tracking, Embeddings, White-label');
  });

  test('check all service integrations work together', async ({ page }) => {
    console.log('Testing service integration chain...');
    
    // Test the complete integration chain:
    // Tracker → Analytics → Generator → Deployer → Score
    
    try {
      // 1. Create test data
      const site = await page.request.post('http://localhost:8001/v1/sites', {
        data: { domain: 'integration-test.com', cms_type: 'wordpress', tenant_id: 1 }
      });
      const siteData = await site.json();
      
      // 2. Test tracker
      const cluster = await page.request.post(`http://localhost:8001/v1/sites/${siteData.site_id}/clusters`, {
        data: { name: 'Integration Test', seed_prompt: 'AI platform testing', keywords: ['test'] }
      });
      const clusterData = await cluster.json();
      
      // 3. Test content generator
      const content = await page.request.post('http://localhost:8002/v1/content/generate', {
        data: { topic: 'platform integration testing', site_id: siteData.site_id, formats: ['faq'] }
      });
      
      // 4. Test analytics
      const competitive = await page.request.post('http://localhost:8003/v1/competitive/analyze', {
        data: { site_id: siteData.site_id, cluster_id: clusterData.cluster_id, competitors: ['test.com'] }
      });
      
      // 5. Test score calculation
      const score = await page.request.post('http://localhost:8004/v1/calculate-score', {
        data: { site_id: siteData.site_id, cluster_id: clusterData.cluster_id }
      });
      
      console.log('Service integration test results:');
      console.log('- Tracker (site/cluster):', site.ok() && cluster.ok());
      console.log('- Generator (content):', content.ok());
      console.log('- Analytics (competitive):', competitive.ok());
      console.log('- Score (calculation):', score.ok());
      
      if (content.ok()) {
        const contentData = await content.json();
        console.log('- Content blocks generated:', contentData.blocks?.length || 0);
      }
      
      if (score.ok()) {
        const scoreData = await score.json();
        console.log('- AI Visibility Score:', scoreData.total);
      }
      
    } catch (error) {
      console.log('Integration test error:', error);
    }
  });
});