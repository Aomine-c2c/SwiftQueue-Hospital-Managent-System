import { test, expect } from '@playwright/test';

test.describe('Queue Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@swiftqueue.com');
    await page.fill('input[name="password"]', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|queue/i);
    
    // Navigate to queue page
    await page.goto('/queue');
  });

  test('should display queue list', async ({ page }) => {
    await expect(page.locator('h1, h2')).toContainText(/queue/i);
    // Check if queue items are visible
    const queueItems = page.locator('[data-testid="queue-item"]');
    await expect(queueItems.first()).toBeVisible({ timeout: 10000 });
  });

  test('should filter queues by status', async ({ page }) => {
    await page.click('[data-testid="filter-status"]');
    await page.click('text=/waiting/i');
    
    // Verify filtered results
    const queueItems = page.locator('[data-testid="queue-item"]');
    const count = await queueItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should create new queue entry', async ({ page }) => {
    await page.click('button:has-text("Add to Queue")');
    
    // Fill form
    await page.fill('input[name="patient_name"]', 'Test Patient');
    await page.selectOption('select[name="service"]', { index: 1 });
    await page.selectOption('select[name="priority"]', 'normal');
    await page.fill('textarea[name="notes"]', 'Test notes');
    
    await page.click('button[type="submit"]');
    
    // Verify success
    await expect(page.locator('text=/success|added/i')).toBeVisible();
    await expect(page.locator('text=/Test Patient/i')).toBeVisible();
  });

  test('should update queue status', async ({ page }) => {
    // Click on first queue item
    await page.click('[data-testid="queue-item"]:first-child');
    
    // Change status
    await page.click('[data-testid="status-dropdown"]');
    await page.click('text=/in progress/i');
    
    // Verify update
    await expect(page.locator('text=/updated|success/i')).toBeVisible();
  });

  test('should delete queue entry', async ({ page }) => {
    // Click on first queue item
    await page.click('[data-testid="queue-item"]:first-child');
    
    // Delete
    await page.click('[data-testid="delete-button"]');
    await page.click('button:has-text("Confirm")');
    
    // Verify deletion
    await expect(page.locator('text=/deleted|removed/i')).toBeVisible();
  });

  test('should sort queues by priority', async ({ page }) => {
    await page.click('[data-testid="sort-by"]');
    await page.click('text=/priority/i');
    
    // Verify sorting
    const firstItem = page.locator('[data-testid="queue-item"]:first-child');
    await expect(firstItem).toContainText(/emergency|urgent/i);
  });

  test('should display wait time estimates', async ({ page }) => {
    const waitTime = page.locator('[data-testid="wait-time"]').first();
    await expect(waitTime).toBeVisible();
    await expect(waitTime).toContainText(/min|minute|hour/i);
  });
});
