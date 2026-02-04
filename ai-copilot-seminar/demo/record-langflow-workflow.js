/**
 * Playwright script to record building a RAG workflow in Langflow
 * This creates a video recording of the entire workflow creation process
 */

const { chromium } = require('playwright');
const path = require('path');

const LANGFLOW_URL = 'http://localhost:7860';
const VIDEO_DIR = path.join(__dirname, 'recordings');

// Workflow steps with annotations
const WORKFLOW_STEPS = [
    {
        step: 1,
        title: "Open Langflow and Select Template",
        description: "Start with the Vector Store RAG template as our foundation",
        action: "select_template"
    },
    {
        step: 2,
        title: "Explore the Load Data Flow",
        description: "This flow loads documents, splits them into chunks, and stores embeddings",
        action: "explore_load_flow"
    },
    {
        step: 3,
        title: "Configure File Component",
        description: "Select your knowledge documents (PDFs, TXT files)",
        action: "configure_file"
    },
    {
        step: 4,
        title: "Configure Text Splitter",
        description: "Set chunk size (1000) and overlap (200) for optimal retrieval",
        action: "configure_splitter"
    },
    {
        step: 5,
        title: "Configure Embeddings",
        description: "Use OpenAI's text-embedding-3-small model",
        action: "configure_embeddings"
    },
    {
        step: 6,
        title: "Explore the Retriever Flow",
        description: "This flow handles user queries and generates responses",
        action: "explore_retriever_flow"
    },
    {
        step: 7,
        title: "Configure Language Model",
        description: "Connect GPT-4o-mini for generating answers",
        action: "configure_llm"
    },
    {
        step: 8,
        title: "Test in Playground",
        description: "Open the Playground to chat with your AI Copilot",
        action: "open_playground"
    }
];

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function recordWorkflow() {
    console.log('Starting Langflow workflow recording...');

    const browser = await chromium.launch({
        headless: true,  // Run headless for server environment
        slowMo: 50  // Slow down for better recording
    });

    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        recordVideo: {
            dir: VIDEO_DIR,
            size: { width: 1920, height: 1080 }
        }
    });

    const page = await context.newPage();

    // Step timestamps for annotations
    const timestamps = [];
    const startTime = Date.now();

    try {
        // Navigate to Langflow
        console.log('Step 1: Opening Langflow...');
        timestamps.push({ step: 1, time: Date.now() - startTime });
        await page.goto(LANGFLOW_URL, { waitUntil: 'networkidle' });
        await sleep(2000);

        // Click on "New Flow" or select template
        console.log('Step 2: Selecting Vector Store RAG template...');
        timestamps.push({ step: 2, time: Date.now() - startTime });

        // Look for the Vector Store RAG in starter projects
        const vectorStoreCard = page.locator('text=Vector Store RAG').first();
        if (await vectorStoreCard.isVisible()) {
            await vectorStoreCard.click();
            await sleep(2000);
        }

        // Wait for canvas to load
        await page.waitForSelector('[data-testid="react-flow-canvas"]', { timeout: 10000 }).catch(() => {});
        await sleep(2000);

        // Step 3: Zoom to fit to see the whole flow
        console.log('Step 3: Viewing the complete flow...');
        timestamps.push({ step: 3, time: Date.now() - startTime });
        await page.keyboard.press('Control+1');  // Zoom to fit
        await sleep(2000);

        // Step 4: Click on File component
        console.log('Step 4: Exploring File component...');
        timestamps.push({ step: 4, time: Date.now() - startTime });
        const fileNode = page.locator('button:has-text("File")').first();
        if (await fileNode.isVisible()) {
            await fileNode.click();
            await sleep(1500);
        }

        // Step 5: Click on Split Text component
        console.log('Step 5: Exploring Split Text component...');
        timestamps.push({ step: 5, time: Date.now() - startTime });
        const splitNode = page.locator('button:has-text("Split Text")').first();
        if (await splitNode.isVisible()) {
            await splitNode.click();
            await sleep(1500);
        }

        // Step 6: Click on OpenAI Embeddings
        console.log('Step 6: Exploring Embeddings component...');
        timestamps.push({ step: 6, time: Date.now() - startTime });
        const embeddingsNode = page.locator('button:has-text("OpenAI Embeddings")').first();
        if (await embeddingsNode.isVisible()) {
            await embeddingsNode.click();
            await sleep(1500);
        }

        // Step 7: Click on Language Model
        console.log('Step 7: Exploring Language Model component...');
        timestamps.push({ step: 7, time: Date.now() - startTime });
        const llmNode = page.locator('button:has-text("Language Model")').first();
        if (await llmNode.isVisible()) {
            await llmNode.click();
            await sleep(1500);
        }

        // Step 8: Open Playground
        console.log('Step 8: Opening Playground...');
        timestamps.push({ step: 8, time: Date.now() - startTime });
        const playgroundBtn = page.locator('button:has-text("Playground")');
        if (await playgroundBtn.isVisible()) {
            await playgroundBtn.click();
            await sleep(3000);
        }

        // Close playground
        const closeBtn = page.locator('button:has-text("Close")');
        if (await closeBtn.isVisible()) {
            await closeBtn.click();
            await sleep(1000);
        }

        // Final view
        console.log('Recording complete!');
        await page.keyboard.press('Control+1');  // Zoom to fit
        await sleep(2000);

    } catch (error) {
        console.error('Error during recording:', error);
    }

    // Save timestamps
    const timestampsPath = path.join(VIDEO_DIR, 'timestamps.json');
    require('fs').writeFileSync(timestampsPath, JSON.stringify({
        steps: WORKFLOW_STEPS,
        timestamps: timestamps
    }, null, 2));

    // Close context to save video
    await context.close();
    await browser.close();

    console.log(`Video saved to: ${VIDEO_DIR}`);
    console.log(`Timestamps saved to: ${timestampsPath}`);
}

// Run the recording
recordWorkflow().catch(console.error);
