import { test, expect } from '@playwright/test';

test.describe('Telemedicine', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="email"]', 'doctor@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Welcome')).toBeVisible();
  });

  test('should display telemedicine dashboard', async ({ page }) => {
    await page.goto('/telemedicine');
    await expect(page.locator('text=Telemedicine Sessions')).toBeVisible();
  });

  test('should create new telemedicine session', async ({ page }) => {
    await page.goto('/telemedicine');
    await page.click('text=New Session');

    // Fill session details
    await page.fill('input[name="patientId"]', '123');
    await page.fill('input[name="chiefComplaint"]', 'Headache and dizziness');
    await page.selectOption('select[name="sessionType"]', 'video');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Session created successfully')).toBeVisible();
  });

  test('should join telemedicine session', async ({ page }) => {
    await page.goto('/telemedicine/session/test-session-123');

    // Should show session interface
    await expect(page.locator('text=Telemedicine Session')).toBeVisible();
    await expect(page.locator('button[aria-label="Start Video"]')).toBeVisible();
    await expect(page.locator('button[aria-label="Start Audio"]')).toBeVisible();
  });

  test('should send message in session', async ({ page }) => {
    await page.goto('/telemedicine/session/test-session-123');

    await page.fill('input[placeholder*="message"]', 'Hello, how are you feeling?');
    await page.click('button[aria-label="Send Message"]');

    await expect(page.locator('text=Hello, how are you feeling?')).toBeVisible();
  });

  test('should complete telemedicine session', async ({ page }) => {
    await page.goto('/telemedicine/session/test-session-123');

    // Fill medical details
    await page.fill('textarea[name="diagnosis"]', 'Migraine headache');
    await page.fill('textarea[name="treatmentPlan"]', 'Prescribe sumatriptan');
    await page.fill('textarea[name="followUpInstructions"]', 'Follow up in 2 weeks');

    await page.click('button[text="Complete Session"]');

    await expect(page.locator('text=Session completed successfully')).toBeVisible();
  });

  test('should submit session feedback', async ({ page }) => {
    await page.goto('/telemedicine/session/test-session-123/feedback');

    // Rate session
    await page.click('button[aria-label="5 stars"]');
    await page.fill('textarea[name="feedback"]', 'Excellent consultation, very helpful.');

    await page.click('button[text="Submit Feedback"]');

    await expect(page.locator('text=Thank you for your feedback')).toBeVisible();
  });
});

test.describe('Waiting Room', () => {
  test('should join waiting room', async ({ page }) => {
    await page.goto('/telemedicine/session/test-session-123');
    await page.click('button[text="Join Waiting Room"]');

    await expect(page.locator('text=Waiting for doctor...')).toBeVisible();
    await expect(page.locator('text=Estimated wait time:')).toBeVisible();
  });

  test('doctor should admit patient from waiting room', async ({ page }) => {
    await page.goto('/telemedicine/session/test-session-123/waiting-room');

    await page.click('button[text="Admit Patient"]');

    await expect(page.locator('text=Patient admitted successfully')).toBeVisible();
  });
});