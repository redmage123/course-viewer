/**
 * Playwright verification script for the embedded Langflow workflow demo
 *
 * This script verifies:
 * 1. The video element exists and is properly configured
 * 2. Video sources (MP4 and WebM) are accessible
 * 3. Annotation overlay elements exist
 * 4. Video controls work correctly
 * 5. Annotations update when video plays/seeks
 */

const { test, expect } = require('@playwright/test');

test.describe('Langflow Workflow Demo Verification', () => {

    test.beforeEach(async ({ page }) => {
        // Navigate to the demo page
        // Update this URL to match your local server
        await page.goto('http://localhost:5000/ai-copilot-seminar/demo/index.html');

        // Navigate to step 3 (Build RAG Pipeline) where the video is
        await page.click('text=Step 3');
        await page.waitForTimeout(500);
    });

    test('Video element exists with correct attributes', async ({ page }) => {
        // Check video element exists
        const video = page.locator('#langflowVideo');
        await expect(video).toBeVisible();

        // Check video has data-testid for identification
        await expect(video).toHaveAttribute('data-testid', 'langflow-workflow-video');

        // Check video has loop attribute
        await expect(video).toHaveAttribute('loop', '');
    });

    test('Video sources are properly configured', async ({ page }) => {
        // Check MP4 source exists
        const mp4Source = page.locator('#langflowVideo source[type="video/mp4"]');
        await expect(mp4Source).toHaveAttribute('src', 'recordings/langflow-workflow.mp4');

        // Check WebM source exists
        const webmSource = page.locator('#langflowVideo source[type="video/webm"]');
        await expect(webmSource).toHaveAttribute('src', 'recordings/langflow-workflow.webm');
    });

    test('Annotation overlay elements exist', async ({ page }) => {
        // Check annotation container
        const annotationOverlay = page.locator('#videoAnnotation');
        await expect(annotationOverlay).toBeVisible();

        // Check step indicator
        const stepIndicator = page.locator('#annotationStep');
        await expect(stepIndicator).toContainText('Step');

        // Check title element
        const title = page.locator('#annotationTitle');
        await expect(title).toBeVisible();

        // Check text element
        const text = page.locator('#annotationText');
        await expect(text).toBeVisible();
    });

    test('Video controls exist and are functional', async ({ page }) => {
        // Check play button
        const playBtn = page.locator('#screencastPlayBtn');
        await expect(playBtn).toBeVisible();
        await expect(playBtn).toContainText('▶️');

        // Check navigation buttons
        const backBtn = page.locator('#screencastBackBtn');
        const forwardBtn = page.locator('#screencastForwardBtn');
        await expect(backBtn).toBeVisible();
        await expect(forwardBtn).toBeVisible();

        // Check step indicator
        const stepIndicator = page.locator('#screencastStepIndicator');
        await expect(stepIndicator).toContainText('Step 1 of 8');
    });

    test('Play button toggles video playback', async ({ page }) => {
        const playBtn = page.locator('#screencastPlayBtn');
        const video = page.locator('#langflowVideo');

        // Initial state should be paused
        await expect(playBtn).toContainText('▶️');

        // Click play
        await playBtn.click();
        await page.waitForTimeout(500);

        // Button should show pause icon
        await expect(playBtn).toContainText('⏸️');

        // Video should be playing (currentTime > 0 after delay)
        const currentTime = await video.evaluate(v => v.currentTime);
        expect(currentTime).toBeGreaterThan(0);

        // Click pause
        await playBtn.click();
        await expect(playBtn).toContainText('▶️');
    });

    test('Forward button advances to next annotation', async ({ page }) => {
        const forwardBtn = page.locator('#screencastForwardBtn');
        const stepIndicator = page.locator('#screencastStepIndicator');
        const annotationTitle = page.locator('#annotationTitle');

        // Initial state
        await expect(stepIndicator).toContainText('Step 1 of 8');

        // Click forward
        await forwardBtn.click();
        await page.waitForTimeout(200);

        // Should be at step 2
        await expect(stepIndicator).toContainText('Step 2 of 8');
        await expect(annotationTitle).toContainText('Load Data Flow');
    });

    test('Back button goes to previous annotation', async ({ page }) => {
        const forwardBtn = page.locator('#screencastForwardBtn');
        const backBtn = page.locator('#screencastBackBtn');
        const stepIndicator = page.locator('#screencastStepIndicator');

        // Go forward first
        await forwardBtn.click();
        await forwardBtn.click();
        await page.waitForTimeout(200);

        // Should be at step 3
        await expect(stepIndicator).toContainText('Step 3 of 8');

        // Go back
        await backBtn.click();
        await page.waitForTimeout(200);

        // Should be at step 2
        await expect(stepIndicator).toContainText('Step 2 of 8');
    });

    test('All 8 annotation steps are accessible', async ({ page }) => {
        const forwardBtn = page.locator('#screencastForwardBtn');
        const stepIndicator = page.locator('#screencastStepIndicator');

        const expectedSteps = [
            'Step 1 of 8',
            'Step 2 of 8',
            'Step 3 of 8',
            'Step 4 of 8',
            'Step 5 of 8',
            'Step 6 of 8',
            'Step 7 of 8',
            'Step 8 of 8'
        ];

        // Check step 1
        await expect(stepIndicator).toContainText(expectedSteps[0]);

        // Navigate through all steps
        for (let i = 1; i < 8; i++) {
            await forwardBtn.click();
            await page.waitForTimeout(100);
            await expect(stepIndicator).toContainText(expectedSteps[i]);
        }

        // Forward button should be disabled at last step
        await expect(forwardBtn).toBeDisabled();
    });

    test('Video files are accessible', async ({ page, request }) => {
        // Test MP4 file
        const mp4Response = await request.get('http://localhost:5000/ai-copilot-seminar/demo/recordings/langflow-workflow.mp4');
        expect(mp4Response.status()).toBe(200);
        expect(mp4Response.headers()['content-type']).toContain('video');

        // Test WebM file
        const webmResponse = await request.get('http://localhost:5000/ai-copilot-seminar/demo/recordings/langflow-workflow.webm');
        expect(webmResponse.status()).toBe(200);
        expect(webmResponse.headers()['content-type']).toContain('video');
    });

    test('Annotations contain expected content', async ({ page }) => {
        const forwardBtn = page.locator('#screencastForwardBtn');
        const annotationTitle = page.locator('#annotationTitle');
        const annotationText = page.locator('#annotationText');

        // Expected annotation content
        const expectedAnnotations = [
            { title: 'RAG Workflow Overview', textContains: 'Vector Store RAG' },
            { title: 'Load Data Flow', textContains: 'embeddings' },
            { title: 'File Component', textContains: 'documents' },
            { title: 'Split Text Component', textContains: 'Chunk' },
            { title: 'OpenAI Embeddings', textContains: 'vector' },
            { title: 'Language Model', textContains: 'GPT' },
            { title: 'Playground Chat', textContains: 'AI Copilot' },
            { title: 'Complete RAG Pipeline', textContains: 'ready' }
        ];

        // Check first annotation
        await expect(annotationTitle).toContainText(expectedAnnotations[0].title);
        await expect(annotationText).toContainText(expectedAnnotations[0].textContains);

        // Navigate and check each annotation
        for (let i = 1; i < expectedAnnotations.length; i++) {
            await forwardBtn.click();
            await page.waitForTimeout(100);
            await expect(annotationTitle).toContainText(expectedAnnotations[i].title);
            await expect(annotationText).toContainText(expectedAnnotations[i].textContains);
        }
    });
});
