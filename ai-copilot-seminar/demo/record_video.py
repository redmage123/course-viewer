#!/usr/bin/env python3
"""
Record the Langflow animation as a video using Playwright.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def record_animation():
    """Record the Langflow animation page as a video."""

    output_dir = Path(__file__).parent / "assets"
    output_dir.mkdir(exist_ok=True)

    async with async_playwright() as p:
        # Launch browser with video recording
        browser = await p.chromium.launch(headless=True)

        # Create context with video recording enabled
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(output_dir),
            record_video_size={"width": 1280, "height": 720}
        )

        page = await context.new_page()

        # Navigate to the animation page
        animation_file = Path(__file__).parent / "langflow-animation.html"
        await page.goto(f"file://{animation_file}")

        # Wait for animation to complete (7 steps × 4 seconds each + buffer)
        print("Recording animation... (30 seconds)")
        await page.wait_for_timeout(32000)

        # Close to finalize video
        await context.close()
        await browser.close()

        # Find and rename the video file
        video_files = list(output_dir.glob("*.webm"))
        if video_files:
            latest_video = max(video_files, key=lambda x: x.stat().st_mtime)
            target_path = output_dir / "langflow-screencast.webm"
            latest_video.rename(target_path)
            print(f"Video saved to: {target_path}")
            return str(target_path)
        else:
            print("No video file found")
            return None

if __name__ == "__main__":
    result = asyncio.run(record_animation())
    print(f"Recording complete: {result}")
