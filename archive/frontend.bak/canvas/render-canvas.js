//
// File: render-canvas.js
// Author: Wadih Khairallah
// Description: 
// Created: 2025-05-08 17:18:49
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    const [,, canvasId, outPath] = process.argv;
    if (!canvasId || !outPath) {
        console.error("Usage: node render-canvas.js <canvas_id> <output_path>");
        process.exit(1);
    }

    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1024, height: 768 } });
    await page.goto(`http://localhost:8000/canvas/${canvasId}.png`, { waitUntil: 'load' });
    await page.waitForTimeout(3000); // Wait for rendering to complete

    const canvas = await page.$("canvas");
    if (!canvas) {
        console.error("Canvas not found");
        process.exit(1);
    }

    await canvas.screenshot({ path: outPath });
    await browser.close();
})();

