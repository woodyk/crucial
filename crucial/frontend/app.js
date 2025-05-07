// File: app.js
// Author: Crucial
// Description: Real-time animated frontend renderer for Crucial Canvas
// Created: 2025-05-06
// Modified: 2025-05-07 14:33:47

import { config } from './config.js';

const BASE = config.apiBase || "";

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const canvasNameDiv = document.getElementById('canvas-name');
let canvasId = new URLSearchParams(window.location.search).get('id') ||
               window.location.pathname.split('/').pop();

if (!canvasId) throw new Error("No canvas ID specified in URL");

let history = [];
let renderedIndex = 0;
let isFramed = false;

// =================== Utility =======================

function hexToRgb(hex) {
    const parsed = hex.startsWith('#') ? hex.slice(1) : hex;
    const bigint = parseInt(parsed, 16);
    return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function fadeInBackground(color, duration) {
    const [r, g, b] = hexToRgb(color);
    let step = 0;
    const steps = 30;
    const interval = duration / steps;

    const id = setInterval(() => {
        let alpha = (++step) / steps;
        ctx.fillStyle = `rgba(${r},${g},${b},${alpha})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (step >= steps) clearInterval(id);
    }, interval);
}

function showCanvasName(name) {
    if (!config.canvasName.show) return;
    canvasNameDiv.textContent = name;
    canvasNameDiv.style.font = config.canvasName.font;
    canvasNameDiv.style.color = config.canvasName.color;
    canvasNameDiv.style.opacity = 0;
    canvasNameDiv.style.transition = `opacity ${config.canvasName.fadeDuration}ms ease`;
    setTimeout(() => {
        canvasNameDiv.style.opacity = 1;
    }, config.backgroundFadeDuration);
}

// =================== Boot =======================

function createFrame(width, height) {
    canvas.width = width;
    canvas.height = height;
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    canvas.style.position = "absolute";
    canvas.style.top = "50%";
    canvas.style.left = "50%";
    canvas.style.transform = "translate(-50%, -50%)";

    document.body.style.background = `url(${config.transparencyGrid.backgroundImage})`;
    document.body.style.backgroundSize = config.transparencyGrid.backgroundSize;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

// =================== Core Loop =======================

let lastActionCount = 0;
let idlePolls = 0;


async function pollCanvasHistory() {
    const res = await fetch(`${BASE}/object/${canvasId}/history`);
    if (!res.ok) return;

    const actions = await res.json();

    // Add only new entries
    if (actions.length > renderedIndex) {
        history = actions;

        while (renderedIndex < history.length) {
            await renderNextAction();
        }
    }
}


async function renderNextAction() {
    if (renderedIndex >= history.length) return;
    const entry = history[renderedIndex++];
    const fn = renderRegistry[entry.action];
    if (fn) await fn(entry);
    else console.warn("Unknown action:", entry.action);
}

function startPolling() {
    window.pollIntervalId = setInterval(pollCanvasHistory, config.pollingIntervalMs);
}

window.addEventListener("load", async () => {
    const meta = await loadCanvasMetadata(canvasId);
    if (!meta) return;

    // Set canvas size from metadata
    createFrame(meta.width, meta.height);

    showCanvasName(meta.name);
    startPolling();
});

// =================== Render Registry =======================
const renderRegistry = {
    'canvas_create': renderCreate,
    'canvas_draw_line': renderDrawLine,
    'canvas_draw_circle': renderDrawCircle,
    'canvas_draw_rectangle': renderDrawRectangle,
    'canvas_draw_text': renderDrawText,
    'canvas_draw_point': renderDrawPoint,
    'canvas_draw_arc': renderDrawArc,
    'canvas_draw_polygon': renderDrawPolygon,
    'canvas_draw_bezier': renderDrawBezier,
    'canvas_clear': renderClear,
    'canvas_graph_bar': renderGraphBar,
    'canvas_graph_pie': renderGraphPie,
    'canvas_graph_line': renderGraphLine,
    'canvas_graph_scatter': renderGraphScatter,
    'canvas_graph_histogram': renderGraphHistogram,
    'canvas_graph_heatmap': renderGraphHeatmap,
    'canvas_render_threejs': renderThreejs
};

// ========== Shape Primitives ==========

async function renderCreate(entry) {
    const { x, y, color } = entry.params;

    if (!isFramed) {
        // Set canvas size and center it
        canvas.width = x;
        canvas.height = y;
        canvas.style.width = x + "px";
        canvas.style.height = y + "px";
        canvas.style.position = "absolute";
        canvas.style.top = "50%";
        canvas.style.left = "50%";
        canvas.style.transform = "translate(-50%, -50%)";

        // Apply transparency grid
        document.body.style.background = `url(${config.transparencyGrid.backgroundImage})`;
        document.body.style.backgroundSize = config.transparencyGrid.backgroundSize;

        // Fill background with fade-in
        fadeInBackground(color || "#111", config.backgroundFadeDuration);
        isFramed = true;
    }
}

async function renderDrawLine(entry) {
    const { start_x, start_y, end_x, end_y, color, width } = entry.params;
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.beginPath();
    ctx.moveTo(start_x, start_y);
    ctx.lineTo(end_x, end_y);
    ctx.stroke();
}

async function renderDrawCircle(entry) {
    const { center_x, center_y, radius, color, fill } = entry.params;
    ctx.beginPath();
    ctx.arc(center_x, center_y, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = color;
    ctx.stroke();
    if (fill && fill !== "none") {
        ctx.fillStyle = fill;
        ctx.fill();
    }
}

async function renderDrawRectangle(entry) {
    const { x, y, width, height, color, fill } = entry.params;
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.strokeStyle = color;
    ctx.stroke();
    if (fill && fill !== "none") {
        ctx.fillStyle = fill;
        ctx.fill();
    }
}

async function renderDrawText(entry) {
    const { text, x, y, font, size, color } = entry.params;
    ctx.save();
    ctx.font = `${size}px ${font}`;
    ctx.fillStyle = color || "#ffffff";
    ctx.fillText(text, x, y);
    ctx.restore();
}

async function renderDrawPoint(entry) {
    const { x, y, color, radius } = entry.params;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
}

async function renderDrawArc(entry) {
    const { center_x, center_y, radius, start_angle, end_angle, color, width } = entry.params;
    ctx.beginPath();
    ctx.arc(center_x, center_y, radius, start_angle, end_angle);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
}

async function renderDrawPolygon(entry) {
    const { points, color, fill } = entry.params;
    if (!points.length) return;
    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);
    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i][0], points[i][1]);
    }
    ctx.closePath();
    ctx.strokeStyle = color;
    ctx.stroke();
    if (fill && fill !== "none") {
        ctx.fillStyle = fill;
        ctx.fill();
    }
}

async function renderDrawBezier(entry) {
    const { control_points, color, width } = entry.params;
    if (control_points.length < 4) return;
    ctx.beginPath();
    ctx.moveTo(control_points[0][0], control_points[0][1]);
    ctx.bezierCurveTo(
        control_points[1][0], control_points[1][1],
        control_points[2][0], control_points[2][1],
        control_points[3][0], control_points[3][1]
    );
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
}

async function renderClear(entry) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

async function renderGraphBar(entry) {
    console.warn("renderGraphBar is not implemented");
}

async function renderGraphPie(entry) {
    const { data, center_x, center_y, radius } = entry.params;
    const total = data.reduce((sum, item) => sum + item.value, 0);
    const colors = config.graph.pie.colors || [];
    const labelFont = config.graph.pie.labelFont || "12px sans-serif";
    const labelColor = config.graph.pie.labelColor || "#ffffff";

    let startAngle = 0;

    for (let i = 0; i < data.length; i++) {
        const item = data[i];
        const sliceAngle = (item.value / total) * 2 * Math.PI;
        const endAngle = startAngle + sliceAngle;
        const color = colors[i % colors.length];

        ctx.beginPath();
        ctx.moveTo(center_x, center_y);
        ctx.arc(center_x, center_y, radius, startAngle, endAngle);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();

        const midAngle = (startAngle + endAngle) / 2;
        const labelX = center_x + (radius * 0.6) * Math.cos(midAngle);
        const labelY = center_y + (radius * 0.6) * Math.sin(midAngle);
        ctx.fillStyle = labelColor;
        ctx.font = labelFont;
        ctx.fillText(item.label, labelX, labelY);

        await sleep(300 * config.drawing.speed);
        startAngle = endAngle;
    }
}

async function renderGraphScatter(entry) {
    const { points, color } = entry.params;
    const scatterColor = color || config.graph.scatter.defaultColor || "#ffffff";

    for (let i = 0; i < points.length; i++) {
        const [x, y] = points[i];
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = scatterColor;
        ctx.fill();
        await sleep(60 * config.drawing.speed);
    }
}

async function renderGraphLine(entry) {
    const { data, axis_config, color } = entry.params;
    if (data.length < 2) return;

    ctx.strokeStyle = color || config.graph.line.defaultColor || "#00ffff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(data[0].x, data[0].y);

    for (let i = 1; i < data.length; i++) {
        ctx.lineTo(data[i].x, data[i].y);
        ctx.stroke();
        await sleep(80 * config.drawing.speed);
    }
}

async function renderGraphHistogram(entry) {
    const { values, bins = 10, normalize = false } = entry.params;
    if (!values.length) return;

    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    const barColor = config.graph.histogram.barColor || "#ff69b4";

    const min = Math.min(...values);
    const max = Math.max(...values);
    const binWidth = (max - min) / bins;
    const histogram = Array(bins).fill(0);

    for (let val of values) {
        const index = Math.min(bins - 1, Math.floor((val - min) / binWidth));
        histogram[index]++;
    }

    if (normalize) {
        const total = histogram.reduce((sum, x) => sum + x, 0);
        for (let i = 0; i < bins; i++) histogram[i] /= total;
    }

    const maxCount = Math.max(...histogram);
    const barWidth = canvasWidth / bins;

    for (let i = 0; i < bins; i++) {
        const height = (histogram[i] / maxCount) * canvasHeight * 0.8;
        const x = i * barWidth;
        const y = canvasHeight - height;
        ctx.fillStyle = barColor;
        ctx.fillRect(x, y, barWidth - 2, height);
        await sleep(80 * config.drawing.speed);
    }
}

async function renderGraphHeatmap(entry) {
    const { matrix, labels = [], color_map = "viridis" } = entry.params;
    if (!matrix.length || !matrix[0].length) return;

    const rows = matrix.length;
    const cols = matrix[0].length;
    const cellWidth = canvas.width / cols;
    const cellHeight = canvas.height / rows;

    const flat = matrix.flat();
    const min = Math.min(...flat);
    const max = Math.max(...flat);

    function getColor(value) {
        const ratio = (value - min) / (max - min);
        const gray = Math.round(ratio * 255);
        return `rgb(${gray},${gray},${gray})`;
    }

    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            const val = matrix[y][x];
            ctx.fillStyle = getColor(val);
            ctx.fillRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
        }
        await sleep(60 * config.drawing.speed);
    }
}


async function renderThreejs(entry) {
    if (window.pollIntervalId) clearInterval(window.pollIntervalId);

    // Remove only the old canvas and controls — keep canvas-name
    document.getElementById("canvas")?.remove();
    document.getElementById("controls")?.remove();
    document.getElementById("error-banner")?.remove();

    // Overlay canvas name (if still hidden)
    const meta = await loadCanvasMetadata(canvasId);
    if (meta && config.canvasName.show) {
        const nameDiv = document.getElementById("canvas-name");
        nameDiv.textContent = meta.name;
        nameDiv.style.font = config.canvasName.font;
        nameDiv.style.color = config.canvasName.color;
        nameDiv.style.opacity = 0;
        nameDiv.style.transition = `opacity ${config.canvasName.fadeDuration}ms ease`;
        setTimeout(() => {
            nameDiv.style.opacity = 1;
        }, config.backgroundFadeDuration);
    }

    // Create iframe for embedded Three.js script
    const iframe = document.createElement("iframe");
    iframe.style.zIndex = "10"; 
    iframe.style.position = "absolute";
    iframe.style.top = 0;
    iframe.style.left = 0;
    iframe.style.width = "100vw";
    iframe.style.height = "100vh";
    iframe.style.border = "none";
    iframe.style.zIndex = "999";
    iframe.allow = "fullscreen";

    iframe.srcdoc = entry.params.script;

    document.body.appendChild(iframe);
    renderedIndex = Number.MAX_SAFE_INTEGER;
}


async function loadCanvasMetadata(id) {
    const res = await fetch(`${BASE}/object/${id}`);
    if (res.status === 404) {
        displayCanvasError("This canvas ID does not exist.");
        return null;
    }
    return res.ok ? res.json() : null;
}

function displayCanvasError(message) {
    if (window.pollIntervalId) clearInterval(window.pollIntervalId);
    const banner = document.getElementById('error-banner');
    banner.textContent = message;
    banner.style.display = "block";
}

