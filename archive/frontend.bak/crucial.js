// File: app.js
// Author: Crucial
// Description: Real-time animated frontend renderer for Crucial Canvas
// Created: 2025-05-06
// Modified: 2025-05-08 17:26:22

import {
  config,
  themeStyles,
  hexToHSL,
  HSLtoHex,
  generateCrucialShadesN
} from './config.js';

const BASE = config.apiBase || "";

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const canvasNameDiv = document.getElementById('canvas-name');
//let canvasId = window.CRUCIAL_CANVAS_ID ||
//               new URLSearchParams(window.location.search).get('id') ||
//               window.location.pathname.split('/').pop();
//const canvasId = window.location.pathname.split("/").pop().replace(".png", "");
const isPngMode = window.location.pathname.endsWith(".png");
let canvasId = new URLSearchParams(window.location.search).get('id')
             || window.location.pathname.split('/').pop().replace(".png", "");




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

// =================== Render Registry =======================
const renderRegistry = {
    // Canvas primitives
    'create': renderCreate,
    'clear': renderClear,
    'draw_line': renderDrawLine,
    'draw_circle': renderDrawCircle,
    'draw_rectangle': renderDrawRectangle,
    'draw_text': renderDrawText,
    'draw_point': renderDrawPoint,
    'draw_arc': renderDrawArc,
    'draw_polygon': renderDrawPolygon,
    'draw_bezier': renderDrawBezier,
    'draw_gradient': renderDrawGradient,
    'draw_path': renderDrawPath,
    'draw_spline': renderDrawSpline,

    // Graphs & Data visualizations
    'graph_bar': renderGraphBar,
    'graph_line': renderGraphLine,
    'graph_pie': renderGraphPie,
    'graph_heatmap': renderGraphHeatmap,
    'graph_histogram': renderGraphHistogram,
    'graph_scatter': renderGraphScatter,
    'graph_bubble': renderGraphBubble,
    'graph_area': renderGraphArea,
    'graph_donut': renderGraphDonut,
    'graph_radar': renderGraphRadar,
    'graph_gauge': renderGraphGauge,
    'graph_wordcloud': renderGraphWordcloud,

    // Special
    'render_threejs': renderThreejs
};

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

    // === Finalize and emit PNG ===
    if (isPngMode) {
        setTimeout(() => {
            canvas.toBlob(blob => {
                const url = URL.createObjectURL(blob);
                const img = new Image();
                img.src = url;
                img.onload = () => {
                    document.body.innerHTML = "";
                    document.body.style.backgroundColor = "#000";
                    document.body.appendChild(img);
                };
            }, "image/png");
        }, 500); // Allow some breathing room for last frame
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

async function renderDrawGradient(entry) {
    const { x, y, width, height, start_color, end_color, type } = entry.params;

    let gradient;
    if (type === "linear") {
        gradient = ctx.createLinearGradient(x, y, x + width, y);
    } else if (type === "radial") {
        const r = Math.min(width, height) / 2;
        gradient = ctx.createRadialGradient(
            x + width / 2, y + height / 2, r / 4,
            x + width / 2, y + height / 2, r
        );
    } else {
        console.warn("Unsupported gradient type:", type);
        return;
    }

    gradient.addColorStop(0, start_color);
    gradient.addColorStop(1, end_color);

    ctx.fillStyle = gradient;
    ctx.fillRect(x, y, width, height);
}

async function renderDrawPath(entry) {
    const { points, color, width } = entry.params;
    if (!points || points.length < 2) return;

    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);
    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i][0], points[i][1]);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
}

async function renderDrawSpline(entry) {
    const { control_points, color, width } = entry.params;
    if (!control_points || control_points.length < 2) return;

    ctx.beginPath();
    ctx.moveTo(control_points[0][0], control_points[0][1]);

    for (let i = 1; i < control_points.length - 1; i++) {
        const [x0, y0] = control_points[i];
        const [x1, y1] = control_points[i + 1];
        const xc = (x0 + x1) / 2;
        const yc = (y0 + y1) / 2;
        ctx.quadraticCurveTo(x0, y0, xc, yc);
    }

    const last = control_points[control_points.length - 1];
    ctx.lineTo(last[0], last[1]);

    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
}



async function renderClear(entry) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}



async function renderGraphBar(entry) {
    const { id, data, color, theme = "dark", title = "", transparent = false } = entry.params;
    if (!data || !data.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const colors = generateCrucialShadesN(color, data.length);

    const margin = 40;
    const titlePad = title ? 30 : 0;
    const chartWidth = canvas.width - margin * 2;
    const chartHeight = canvas.height - margin * 2 - titlePad;
    const barWidth = chartWidth / data.length;
    const maxVal = Math.max(...data.map(d => d.value));

    // Optional transparency
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.font = config.graph.bar.labelFont;

    for (let i = 0; i < data.length; i++) {
        const { label, value } = data[i];
        const x = margin + i * barWidth;
        const y = canvas.height - margin;
        const barHeight = (value / maxVal) * chartHeight;

        // Rounded bar
        const bw = barWidth * 0.8;
        const bx = x + (barWidth - bw) / 2;
        const by = y - barHeight;
        const radius = Math.max(4, bw * 0.1);

        ctx.beginPath();
        ctx.moveTo(bx + radius, by);
        ctx.lineTo(bx + bw - radius, by);
        ctx.quadraticCurveTo(bx + bw, by, bx + bw, by + radius);
        ctx.lineTo(bx + bw, y);
        ctx.lineTo(bx, y);
        ctx.lineTo(bx, by + radius);
        ctx.quadraticCurveTo(bx, by, bx + radius, by);
        ctx.closePath();

        ctx.fillStyle = colors[i % colors.length];
        ctx.fill();

        ctx.fillStyle = style.text;
        ctx.fillText(label, x + barWidth / 2, y + 14);

        await sleep(80 * config.drawing.speed);
    }
}

async function renderGraphLine(entry) {
    const { data, theme = "dark", color, title = "", transparent = false } = entry.params;
    if (!data || data.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const palette = generateCrucialShadesN(color, 1); // single line, 1 color
    const stroke = palette[0];

    const margin = 40;
    const titlePad = title ? 30 : 0;

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    ctx.beginPath();
    ctx.moveTo(data[0].x, data[0].y);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 2;

    for (let i = 1; i < data.length; i++) {
        ctx.lineTo(data[i].x, data[i].y);
        ctx.stroke();
        await sleep(60 * config.drawing.speed);
    }
}

async function renderGraphPie(entry) {
    const { data, theme = "dark", color, title = "", transparent = false } = entry.params;
    if (!data || !data.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const colors = generateCrucialShadesN(color, data.length);
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const radius = Math.min(cx, cy) * 0.8;
    const total = data.reduce((sum, d) => sum + d.value, 0);

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    let angle = 0;
    for (let i = 0; i < data.length; i++) {
        const slice = (data[i].value / total) * 2 * Math.PI;
        const end = angle + slice;

        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, radius, angle, end);
        ctx.closePath();

        ctx.fillStyle = colors[i % colors.length];
        ctx.fill();

        // Label
        const mid = (angle + end) / 2;
        const lx = cx + (radius * 0.6) * Math.cos(mid);
        const ly = cy + (radius * 0.6) * Math.sin(mid);
        ctx.fillStyle = style.text;
        ctx.font = config.graph.pie.labelFont;
        ctx.fillText(data[i].label, lx, ly);

        angle = end;
        await sleep(100 * config.drawing.speed);
    }
}

async function renderGraphHeatmap(entry) {
    const { matrix, theme = "dark", color, title = "", transparent = false } = entry.params;
    if (!matrix || !matrix.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const rows = matrix.length;
    const cols = matrix[0].length;
    const cellW = canvas.width / cols;
    const cellH = canvas.height / rows;
    const flat = matrix.flat();
    const min = Math.min(...flat);
    const max = Math.max(...flat);

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    const baseHSL = hexToHSL(color);
    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            const v = matrix[y][x];
            const norm = (v - min) / (max - min || 1); // Avoid div by 0
            const shade = HSLtoHex(baseHSL[0], baseHSL[1], 20 + norm * 50);
            ctx.fillStyle = shade;
            ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
        }
        await sleep(20 * config.drawing.speed);
    }
}

async function renderGraphHistogram(entry) {
    const { values, bins = 10, normalize = false, color, theme = "dark", title = "", transparent = false } = entry.params;
    if (!values || !values.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const width = canvas.width, height = canvas.height;
    const margin = 40;
    const titlePad = title ? 30 : 0;
    const chartHeight = height - margin * 2 - titlePad;
    const chartWidth = width - margin * 2;

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, width, height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, width / 2, margin);
    }

    const min = Math.min(...values);
    const max = Math.max(...values);
    const binSize = (max - min) / bins;
    const histogram = Array(bins).fill(0);

    for (let v of values) {
        const i = Math.min(bins - 1, Math.floor((v - min) / binSize));
        histogram[i]++;
    }

    if (normalize) {
        const total = histogram.reduce((a, b) => a + b, 0);
        for (let i = 0; i < bins; i++) histogram[i] /= total;
    }

    const maxCount = Math.max(...histogram);
    const barWidth = chartWidth / bins;
    const colors = generateCrucialShadesN(color, bins);

    for (let i = 0; i < bins; i++) {
        const x = margin + i * barWidth;
        const barH = (histogram[i] / maxCount) * chartHeight;
        const y = height - margin;

        ctx.fillStyle = colors[i];
        ctx.fillRect(x + 2, y - barH, barWidth - 4, barH);
        await sleep(30 * config.drawing.speed);
    }
}

async function renderGraphScatter(entry) {
    const { points, color, theme = "dark", title = "", transparent = false } = entry.params;
    if (!points || !points.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    ctx.fillStyle = color;
    for (let i = 0; i < points.length; i++) {
        const { x, y } = points[i];
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
        await sleep(20 * config.drawing.speed);
    }
}

async function renderGraphBubble(entry) {
    const { bubbles, color, theme = "dark", title = "", transparent = false } = entry.params;
    if (!bubbles || !bubbles.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const palette = generateCrucialShadesN(color, bubbles.length);

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    for (let i = 0; i < bubbles.length; i++) {
        const { x, y, size } = bubbles[i];
        ctx.beginPath();
        ctx.arc(x, y, size, 0, 2 * Math.PI);
        ctx.fillStyle = palette[i % palette.length];
        ctx.fill();
        await sleep(40 * config.drawing.speed);
    }
}

async function renderGraphArea(entry) {
    const { data, color, theme = "dark", title = "", transparent = false } = entry.params;
    if (!data || data.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const stroke = generateCrucialShadesN(color, 1)[0];

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    ctx.beginPath();
    ctx.moveTo(data[0].x, canvas.height - 40);  // bottom edge
    for (let i = 0; i < data.length; i++) {
        ctx.lineTo(data[i].x, data[i].y);
    }
    ctx.lineTo(data[data.length - 1].x, canvas.height - 40);
    ctx.closePath();

    ctx.fillStyle = stroke + "44";
    ctx.fill();
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 2;
    ctx.stroke();
}

async function renderGraphRadar(entry) {
    const { labels, values, color, theme = "dark", title = "", transparent = false } = entry.params;
    if (!labels || !values || labels.length !== values.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const radius = Math.min(cx, cy) * 0.75;
    const count = labels.length;
    const max = Math.max(...values);
    const angleStep = (2 * Math.PI) / count;
    const line = generateCrucialShadesN(color, 1)[0];

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    // Axis lines
    ctx.strokeStyle = "#555";
    for (let i = 0; i < count; i++) {
        const angle = i * angleStep;
        const x = cx + radius * Math.cos(angle);
        const y = cy + radius * Math.sin(angle);
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.fillStyle = style.text;
        ctx.font = "11px Courier New";
        ctx.fillText(labels[i], x, y);
    }

    // Data polygon
    ctx.beginPath();
    for (let i = 0; i < count; i++) {
        const angle = i * angleStep;
        const r = (values[i] / max) * radius;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.strokeStyle = line;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = line + "33";
    ctx.fill();
}

async function renderGraphGauge(entry) {
    const { value, color, label = "", theme = "dark", title = "", transparent = false } = entry.params;
    if (value == null || value < 0 || value > 100 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const cx = canvas.width / 2;
    const cy = canvas.height * 0.75;
    const radius = Math.min(cx, cy) * 0.7;
    const arcColor = generateCrucialShadesN(color, 1)[0];

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    // Background arc
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, 2 * Math.PI);
    ctx.strokeStyle = "#444";
    ctx.lineWidth = 12;
    ctx.stroke();

    // Filled arc
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, Math.PI + (Math.PI * value / 100));
    ctx.strokeStyle = arcColor;
    ctx.lineWidth = 12;
    ctx.stroke();

    // Label
    ctx.fillStyle = style.text;
    ctx.font = "16px Courier New";
    ctx.fillText(`${value}%`, cx, cy - 10);
    ctx.font = "12px Courier New";
    ctx.fillText(label, cx, cy + 20);
}

async function renderGraphDonut(entry) {
    const { data, color, theme = "dark", title = "", transparent = false } = entry.params;
    if (!data || !data.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const outer = Math.min(cx, cy) * 0.8;
    const inner = outer * 0.5;
    const total = data.reduce((sum, d) => sum + d.value, 0);
    const palette = generateCrucialShadesN(color, data.length);

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    let angle = 0;
    for (let i = 0; i < data.length; i++) {
        const slice = (data[i].value / total) * 2 * Math.PI;
        const end = angle + slice;

        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, outer, angle, end);
        ctx.arc(cx, cy, inner, end, angle, true);
        ctx.closePath();

        ctx.fillStyle = palette[i];
        ctx.fill();

        const mid = (angle + end) / 2;
        const lx = cx + (outer + inner) / 2 * Math.cos(mid);
        const ly = cy + (outer + inner) / 2 * Math.sin(mid);
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.fillText(data[i].label, lx, ly);

        angle = end;
        await sleep(80 * config.drawing.speed);
    }
}


async function renderGraphWordcloud(entry) {
    const { words, color, theme = "dark", title = "", transparent = false } = entry.params;
    if (!words || !words.length || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const maxVal = Math.max(...words.map(w => w.value));
    const palette = generateCrucialShadesN(color, words.length);

    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 30);
    }

    // Crude spiral layout
    let angle = 0;
    let radius = 0;
    const step = 15;

    for (let i = 0; i < words.length; i++) {
        const word = words[i];
        const size = 10 + (word.value / maxVal) * 30;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);

        ctx.font = `${size}px Courier New`;
        ctx.fillStyle = palette[i];
        ctx.fillText(word.text, x, y);

        angle += 0.4;
        radius += step;
        await sleep(30 * config.drawing.speed);
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
