// File: app.js
// Author: Crucial
// Description: Real-time animated frontend renderer for Crucial Canvas
// Created: 2025-05-06
// Modified: 2025-05-10 02:44:05

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

function isLightColor(hex) {
    if (!hex || typeof hex !== "string" || !hex.startsWith("#")) return false;
    const c = hex.length === 4
        ? "#" + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3]
        : hex;
    const r = parseInt(c.substring(1, 3), 16);
    const g = parseInt(c.substring(3, 5), 16);
    const b = parseInt(c.substring(5, 7), 16);
    if (isNaN(r) || isNaN(g) || isNaN(b)) return false;
    const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
    return luminance > 186;
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

// Add second canvas for turtle overlay
const overlayCanvas = document.createElement("canvas");
overlayCanvas.width = canvas.width;
overlayCanvas.height = canvas.height;
overlayCanvas.style.position = "absolute";
overlayCanvas.style.left = canvas.style.left;
overlayCanvas.style.top = canvas.style.top;
overlayCanvas.style.pointerEvents = "none";
canvas.parentNode.appendChild(overlayCanvas);
const overlayCtx = overlayCanvas.getContext("2d");

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
    'draw_turtle': renderDrawTurtle,
    'draw_raster': renderDrawRaster,
    'draw_bitmap': renderDrawBitmap,

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

function startRealtimeUpdates() {
    const ws = new WebSocket(`ws://${location.host}/ws/canvas/${canvasId}`);

    ws.onmessage = async (event) => {
        const entry = JSON.parse(event.data);
        history.push(entry);
        await renderNextAction();  // or a queue/debounce
    };

    ws.onopen = () => console.log("[Crucial] WebSocket connected");
    ws.onclose = () => console.warn("[Crucial] WebSocket disconnected");
}

window.addEventListener("load", async () => {
    const meta = await loadCanvasMetadata(canvasId);
    if (!meta) return;

    createFrame(meta.width, meta.height);
    showCanvasName(meta.name);

    // Load and render full canvas history first
    const res = await fetch(`/object/${canvasId}/history`);
    if (res.ok) {
        history = await res.json();
        while (renderedIndex < history.length) {
            await renderNextAction();
        }
    }

    // Then start listening for live actions
    startRealtimeUpdates();
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

async function renderDrawTurtle(entry) {
    const {
        commands,
        start_x = 0,
        start_y = 0,
        start_heading = 0,
        pen_color = "#000000",
        pen_width = 2
    } = entry.params;

    let x = start_x;
    let y = start_y;
    let angle = start_heading;
    let penDown = true;
    let currentColor = pen_color;
    let currentWidth = pen_width;

    ctx.strokeStyle = currentColor;
    ctx.lineWidth = currentWidth;

    function drawTurtleHead(x, y, angleDeg) {
        overlayCtx.clearRect(0, 0, canvas.width, canvas.height);
        const rad = -angleDeg * Math.PI / 180;

        overlayCtx.save();
        overlayCtx.translate(x, y);
        overlayCtx.rotate(rad);
        overlayCtx.fillStyle = "#ff6600";
        overlayCtx.beginPath();
        overlayCtx.moveTo(0, 0);
        overlayCtx.lineTo(-8, -5);
        overlayCtx.lineTo(-8, 5);
        overlayCtx.closePath();
        overlayCtx.fill();
        overlayCtx.restore();
    }

    drawTurtleHead(x, y, angle);

    for (let cmd of commands) {
        let instruction, arg;

        if (typeof cmd === "string") {
            const parts = cmd.trim().split(/\s+/);
            instruction = parts[0].toLowerCase();
            arg = parts.length > 1 ? parts.slice(1).join(" ") : null;
        } else if (Array.isArray(cmd)) {
            instruction = String(cmd[0]).toLowerCase();
            arg = cmd.length > 1 ? cmd[1] : null;
        } else {
            console.warn("Invalid turtle command:", cmd);
            continue;
        }

        const num = parseFloat(arg);
        const coords = typeof arg === "string" ? arg.split(",").map(Number) : [];

        switch (instruction) {
            case "forward":
            case "backward":
                {
                    const rad = angle * Math.PI / 180;
                    const dir = instruction === "forward" ? 1 : -1;
                    const dist = isNaN(num) ? 0 : num;
                    const newX = x + dir * Math.cos(rad) * dist;
                    const newY = y - dir * Math.sin(rad) * dist;

                    if (penDown) {
                        ctx.beginPath();
                        ctx.moveTo(x, y);
                        ctx.lineTo(newX, newY);
                        ctx.stroke();
                    }

                    x = newX;
                    y = newY;
                }
                break;

            case "left":
                angle = (angle + num) % 360;
                break;

            case "right":
                angle = (angle - num + 360) % 360;
                break;

            case "goto":
                if (Array.isArray(arg) && arg.length === 2) {
                    const [gx, gy] = arg;
                    if (penDown) {
                        ctx.beginPath();
                        ctx.moveTo(x, y);
                        ctx.lineTo(gx, gy);
                        ctx.stroke();
                    }
                    x = gx;
                    y = gy;
                } else if (coords.length === 2) {
                    const [gx, gy] = coords;
                    if (penDown) {
                        ctx.beginPath();
                        ctx.moveTo(x, y);
                        ctx.lineTo(gx, gy);
                        ctx.stroke();
                    }
                    x = gx;
                    y = gy;
                }
                break;

            case "setheading":
                angle = parseFloat(arg);
                break;

            case "penup":
                penDown = false;
                break;

            case "pendown":
                penDown = true;
                break;

            case "setcolor":
                currentColor = String(arg);
                ctx.strokeStyle = currentColor;
                break;

            case "setwidth":
                currentWidth = parseInt(arg, 10);
                ctx.lineWidth = currentWidth;
                break;

            default:
                console.warn("Unknown turtle command:", instruction, arg);
        }

        drawTurtleHead(x, y, angle);
        await sleep(100 * config.drawing.speed);
    }

    drawTurtleHead(x, y, angle);
}

async function renderDrawRaster(entry) {
    const { pixels } = entry.params;

    if (!Array.isArray(pixels)) {
        console.warn("Invalid draw_raster payload:", entry);
        return;
    }

    const drawDelay = 2 * config.drawing.speed;
    const pixelLimit = 500; // max pixels to animate before skipping delay
    const animateRandomly = true;

    const drawOrder = [...pixels];

    if (animateRandomly) {
        for (let i = drawOrder.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [drawOrder[i], drawOrder[j]] = [drawOrder[j], drawOrder[i]];
        }
    }

    for (let i = 0; i < drawOrder.length; i++) {
        const { x, y, color } = drawOrder[i];
        ctx.fillStyle = color;
        ctx.fillRect(x, y, 1, 1);

        if (i < pixelLimit) {
            await sleep(drawDelay);
        }
    }
}

function renderDrawBitmap(entry) {
    const { x, y, width, height, rgba } = entry.params;

    if (!rgba || typeof rgba !== "string" || width <= 0 || height <= 0) {
        console.warn("Invalid draw_bitmap parameters", entry);
        return;
    }

    try {
        const raw = atob(rgba);
        const expectedBytes = width * height * 4;

        if (raw.length !== expectedBytes) {
            console.warn("draw_bitmap: RGBA length mismatch", {
                width,
                height,
                expected: expectedBytes,
                actual: raw.length
            });
            return;
        }

        const imageData = ctx.createImageData(width, height);
        for (let i = 0; i < expectedBytes; i++) {
            imageData.data[i] = raw.charCodeAt(i);
        }

        ctx.putImageData(imageData, x, y);
    } catch (err) {
        console.error("draw_bitmap decoding error", err);
    }
}


async function renderClear(entry) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

async function renderGraphBar(entry) {
    const {
        labels,
        values,
        color,
        title = ""
    } = entry.params;

    const theme = entry.params.theme ?? "dark";
    const transparent = entry.params.transparent ?? false;

    if (!labels || !values || labels.length !== values.length || labels.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const barColors = generateCrucialShadesN(color, labels.length);

    const margin = 40;
    const titlePad = title ? 30 : 0;
    const spacing = 10;
    const chartWidth = canvas.width - 2 * margin;
    const chartHeight = canvas.height - 2 * margin - titlePad;
    const barWidth = (chartWidth - spacing * (labels.length - 1)) / labels.length;
    const maxValue = Math.max(...values);

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    // Bars + Labels
    for (let i = 0; i < labels.length; i++) {
        const x = margin + i * (barWidth + spacing);
        const barHeight = (values[i] / maxValue) * chartHeight;
        const y = canvas.height - margin - barHeight;

        const radius = Math.min(barWidth, barHeight) * 0.15;

        ctx.fillStyle = barColors[i];
        ctx.beginPath();
        ctx.moveTo(x, y + barHeight);                         // bottom-left
        ctx.lineTo(x, y + radius);                            // up to top-left corner
        ctx.arcTo(x, y, x + radius, y, radius);               // top-left corner
        ctx.lineTo(x + barWidth - radius, y);                 // across top
        ctx.arcTo(x + barWidth, y, x + barWidth, y + radius, radius); // top-right corner
        ctx.lineTo(x + barWidth, y + barHeight);              // down to bottom-right
        ctx.closePath();
        ctx.fill();

        // Label
        ctx.fillStyle = style.text;
        ctx.font = config.graph.bar.labelFont;
        ctx.textAlign = "center";
        ctx.fillText(labels[i], x + barWidth / 2, canvas.height - margin + 14);

        await sleep(40 * config.drawing.speed);
    }
}


function drawSmoothLine(ctx, points, tension = 0.5) {
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);

    for (let i = 0; i < points.length - 1; i++) {
        const p0 = points[i > 0 ? i - 1 : i];
        const p1 = points[i];
        const p2 = points[i + 1];
        const p3 = points[i + 2 < points.length ? i + 2 : i + 1];

        const cp1x = p1.x + (p2.x - p0.x) / 6 * tension;
        const cp1y = p1.y + (p2.y - p0.y) / 6 * tension;

        const cp2x = p2.x - (p3.x - p1.x) / 6 * tension;
        const cp2y = p2.y - (p3.y - p1.y) / 6 * tension;

        ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
    }

    ctx.stroke();
}

async function renderGraphLine(entry) {
    const {
        x_values,
        y_values,
        color,
        title = "",
        x_label = "",
        y_label = ""
    } = entry.params;

    const theme = entry.params.theme ?? "dark";
    const transparent = entry.params.transparent ?? false;

    if (!x_values || !y_values || x_values.length !== y_values.length || x_values.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const stroke = generateCrucialShadesN(color, 1)[0];

    const margin = 40;
    const titlePad = title ? 30 : 0;
    const chartWidth = canvas.width - 2 * margin;
    const chartHeight = canvas.height - 2 * margin - titlePad;

    const minX = Math.min(...x_values);
    const maxX = Math.max(...x_values);
    const minY = Math.min(...y_values);
    const maxY = Math.max(...y_values);

    const scaleX = val => margin + ((val - minX) / (maxX - minX || 1)) * chartWidth;
    const scaleY = val => canvas.height - margin - ((val - minY) / (maxY - minY || 1)) * chartHeight;

    const points = x_values.map((x, i) => ({
        x: scaleX(x),
        y: scaleY(y_values[i])
    }));

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    // Grid
    ctx.strokeStyle = style.grid;
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 1;

    for (let i = 0; i < x_values.length; i++) {
        const x = scaleX(x_values[i]);
        ctx.beginPath();
        ctx.moveTo(x, margin);
        ctx.lineTo(x, canvas.height - margin);
        ctx.stroke();
    }

    const steps = 5;
    for (let j = 0; j <= steps; j++) {
        const y = margin + titlePad + (chartHeight * j / steps);
        ctx.beginPath();
        ctx.moveTo(margin, y);
        ctx.lineTo(canvas.width - margin, y);
        ctx.stroke();
    }

    ctx.setLineDash([]);

    // Smooth line
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 2;
    drawSmoothLine(ctx, points, 0.5);  // ← uses shared global function

    // Axis labels
    if (x_label) {
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(x_label, canvas.width / 2, canvas.height - 8);
    }

    if (y_label) {
        ctx.save();
        ctx.translate(12, canvas.height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.textAlign = "center";
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.fillText(y_label, 0, 0);
        ctx.restore();
    }
}

async function renderGraphPie(entry) {
    const {
        labels,
        values,
        color,
        title = ""
    } = entry.params;

    const theme = entry.params.theme ?? "dark";
    const transparent = entry.params.transparent ?? false;

    if (!labels || !values || labels.length !== values.length || labels.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const shades = generateCrucialShadesN(color, labels.length);

    const margin = 40;
    const radius = Math.min(canvas.width, canvas.height) / 2 - margin;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2 + 10;
    const total = values.reduce((a, b) => a + b, 0);

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

    let angleStart = -Math.PI / 2;

    for (let i = 0; i < labels.length; i++) {
        const angle = (values[i] / total) * Math.PI * 2;
        const angleEnd = angleStart + angle;

        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, angleStart, angleEnd);
        ctx.closePath();
        ctx.fillStyle = shades[i];
        ctx.fill();

        const midAngle = angleStart + angle / 2;
        const labelX = centerX + Math.cos(midAngle) * radius * 0.7;
        const labelY = centerY + Math.sin(midAngle) * radius * 0.7;

        const textColor = isLightColor(shades[i]) ? "#000000" : "#ffffff";
        ctx.fillStyle = textColor;
        ctx.font = config.graph.pie.labelFont;
        ctx.textAlign = "center";
        ctx.fillText(labels[i], labelX, labelY);

        angleStart = angleEnd;

        await sleep(20 * config.drawing.speed);
    }
}

async function renderGraphDonut(entry) {
    const {
        labels,
        values,
        color,
        title = ""
    } = entry.params;

    const theme = entry.params.theme ?? "dark";
    const transparent = entry.params.transparent ?? false;

    if (!labels || !values || labels.length !== values.length || labels.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const shades = generateCrucialShadesN(color, labels.length);

    const margin = 40;
    const outerRadius = Math.min(canvas.width, canvas.height) / 2 - margin;
    const innerRadius = outerRadius * 0.55;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2 + 10;
    const total = values.reduce((a, b) => a + b, 0);

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    let angleStart = -Math.PI / 2;

    for (let i = 0; i < labels.length; i++) {
        const angle = (values[i] / total) * Math.PI * 2;
        const angleEnd = angleStart + angle;

        ctx.beginPath();
        ctx.arc(centerX, centerY, outerRadius, angleStart, angleEnd);
        ctx.arc(centerX, centerY, innerRadius, angleEnd, angleStart, true);
        ctx.closePath();
        ctx.fillStyle = shades[i];
        ctx.fill();

        // Slice label
        const midAngle = angleStart + angle / 2;
        const labelX = centerX + Math.cos(midAngle) * (outerRadius + innerRadius) / 2;
        const labelY = centerY + Math.sin(midAngle) * (outerRadius + innerRadius) / 2;

        const textColor = isLightColor(shades[i]) ? "#000000" : "#ffffff";
        ctx.fillStyle = textColor;
        ctx.font = config.graph.pie.labelFont;
        ctx.textAlign = "center";
        ctx.fillText(labels[i], labelX, labelY);

        angleStart = angleEnd;

        await sleep(20 * config.drawing.speed);
    }

    // Center highlight value
    const topValue = Math.max(...values);
    const topLabel = labels[values.indexOf(topValue)];

    ctx.fillStyle = style.text;
    ctx.font = "bold 16px Courier New";
    ctx.textAlign = "center";
    ctx.fillText(topLabel, centerX, centerY + 6);
}


async function renderGraphHeatmap(entry) {
    const {
        matrix,
        color,
        theme = "dark",
        title = "",
        transparent = false
    } = entry.params;

    if (!matrix || !Array.isArray(matrix) || matrix.length === 0 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const tint = generateCrucialShadesN(color, 100); // Up to 100 shades for safety

    const margin = 40;
    const titlePad = title ? 30 : 0;
    const width = canvas.width - 2 * margin;
    const height = canvas.height - 2 * margin - titlePad;

    const rows = matrix.length;
    const cols = matrix[0].length;
    const cellWidth = width / cols;
    const cellHeight = height / rows;

    let min = Infinity;
    let max = -Infinity;

    for (let row of matrix) {
        for (let val of row) {
            if (val < min) min = val;
            if (val > max) max = val;
        }
    }

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title with correct theme text color
    if (title) {
        ctx.fillStyle = style.text;  // Fixed: use theme-defined text color
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            const value = matrix[y][x];
            const norm = (value - min) / (max - min || 1);
            const shadeIdx = Math.floor(norm * (tint.length - 1));
            ctx.fillStyle = tint[shadeIdx];
            ctx.fillRect(
                margin + x * cellWidth,
                margin + titlePad + y * cellHeight,
                cellWidth,
                cellHeight
            );
            await sleep(2 * config.drawing.speed);
        }
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
    const {
        x_values,
        y_values,
        color,
        theme = "dark",
        title = "",
        transparent = false,
        x_label = "",
        y_label = ""
    } = entry.params;

    if (!x_values || !y_values || x_values.length !== y_values.length || x_values.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const pointColor = generateCrucialShadesN(color, 1)[0];

    const margin = 40;
    const titlePad = title ? 30 : 0;
    const chartWidth = canvas.width - 2 * margin;
    const chartHeight = canvas.height - 2 * margin - titlePad;

    const minX = Math.min(...x_values);
    const maxX = Math.max(...x_values);
    const minY = Math.min(...y_values);
    const maxY = Math.max(...y_values);

    const scaleX = val => margin + ((val - minX) / (maxX - minX || 1)) * chartWidth;
    const scaleY = val => canvas.height - margin - ((val - minY) / (maxY - minY || 1)) * chartHeight;

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    // Grid lines
    ctx.strokeStyle = style.grid || "#444";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);

    for (let i = 0; i < x_values.length; i++) {
        const x = scaleX(x_values[i]);
        ctx.beginPath();
        ctx.moveTo(x, margin);
        ctx.lineTo(x, canvas.height - margin);
        ctx.stroke();
    }

    const steps = 5;
    for (let j = 0; j <= steps; j++) {
        const yVal = minY + (j / steps) * (maxY - minY);
        const y = scaleY(yVal);
        ctx.beginPath();
        ctx.moveTo(margin, y);
        ctx.lineTo(canvas.width - margin, y);
        ctx.stroke();
    }

    ctx.setLineDash([]);

    // Points
    for (let i = 0; i < x_values.length; i++) {
        const x = scaleX(x_values[i]);
        const y = scaleY(y_values[i]);
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = pointColor;
        ctx.fill();
        await sleep(20 * config.drawing.speed);
    }

    // Axis labels
    if (x_label) {
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(x_label, canvas.width / 2, canvas.height - 8);
    }

    if (y_label) {
        ctx.save();
        ctx.translate(12, canvas.height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.textAlign = "center";
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.fillText(y_label, 0, 0);
        ctx.restore();
    }
}

async function renderGraphBubble(entry) {
    const {
        x_values,
        y_values,
        sizes,
        color,
        theme = "dark",
        title = "",
        transparent = false,
        x_label = "",
        y_label = ""
    } = entry.params;

    if (!x_values || !y_values || !sizes ||
        x_values.length !== y_values.length ||
        x_values.length !== sizes.length ||
        x_values.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const bubbleColor = generateCrucialShadesN(color, 1)[0];

    const margin = 40;
    const titlePad = title ? 30 : 0;
    const chartWidth = canvas.width - 2 * margin;
    const chartHeight = canvas.height - 2 * margin - titlePad;

    const minX = Math.min(...x_values);
    const maxX = Math.max(...x_values);
    const minY = Math.min(...y_values);
    const maxY = Math.max(...y_values);
    const minSize = Math.min(...sizes);
    const maxSize = Math.max(...sizes);

    const scaleX = val => margin + ((val - minX) / (maxX - minX || 1)) * chartWidth;
    const scaleY = val => canvas.height - margin - ((val - minY) / (maxY - minY || 1)) * chartHeight;
    const scaleR = val => 5 + ((val - minSize) / (maxSize - minSize || 1)) * 30;

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    // Grid
    ctx.strokeStyle = style.grid || "#444";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);

    for (let i = 0; i < x_values.length; i++) {
        const x = scaleX(x_values[i]);
        ctx.beginPath();
        ctx.moveTo(x, margin);
        ctx.lineTo(x, canvas.height - margin);
        ctx.stroke();
    }

    const steps = 5;
    for (let j = 0; j <= steps; j++) {
        const y = margin + titlePad + (chartHeight * j / steps);
        ctx.beginPath();
        ctx.moveTo(margin, y);
        ctx.lineTo(canvas.width - margin, y);
        ctx.stroke();
    }

    ctx.setLineDash([]);

    // Bubbles
    for (let i = 0; i < x_values.length; i++) {
        const x = scaleX(x_values[i]);
        const y = scaleY(y_values[i]);
        const r = scaleR(sizes[i]);

        ctx.beginPath();
        ctx.arc(x, y, r, 0, 2 * Math.PI);
        ctx.fillStyle = bubbleColor;
        ctx.fill();

        await sleep(40 * config.drawing.speed);
    }

    // Labels
    if (x_label) {
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(x_label, canvas.width / 2, canvas.height - 8);
    }

    if (y_label) {
        ctx.save();
        ctx.translate(12, canvas.height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.textAlign = "center";
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.fillText(y_label, 0, 0);
        ctx.restore();
    }
}

async function renderGraphArea(entry) {
    const {
        x_values,
        y_values,
        color,
        title = "",
        x_label = "",
        y_label = ""
    } = entry.params;

    const theme = entry.params.theme ?? "dark";
    const transparent = entry.params.transparent ?? false;

    if (!x_values || !y_values || x_values.length !== y_values.length || x_values.length < 2 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const stroke = generateCrucialShadesN(color, 1)[0];

    const margin = 40;
    const titlePad = title ? 30 : 0;
    const chartWidth = canvas.width - 2 * margin;
    const chartHeight = canvas.height - 2 * margin - titlePad;

    const minX = Math.min(...x_values);
    const maxX = Math.max(...x_values);
    const minY = Math.min(...y_values);
    const maxY = Math.max(...y_values);

    const scaleX = val => margin + ((val - minX) / (maxX - minX || 1)) * chartWidth;
    const scaleY = val => canvas.height - margin - ((val - minY) / (maxY - minY || 1)) * chartHeight;

    const points = x_values.map((x, i) => ({
        x: scaleX(x),
        y: scaleY(y_values[i])
    }));

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    // Grid
    ctx.strokeStyle = style.grid;
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 1;

    for (let i = 0; i < x_values.length; i++) {
        const x = scaleX(x_values[i]);
        ctx.beginPath();
        ctx.moveTo(x, margin);
        ctx.lineTo(x, canvas.height - margin);
        ctx.stroke();
    }

    const steps = 5;
    for (let j = 0; j <= steps; j++) {
        const y = margin + titlePad + (chartHeight * j / steps);
        ctx.beginPath();
        ctx.moveTo(margin, y);
        ctx.lineTo(canvas.width - margin, y);
        ctx.stroke();
    }

    ctx.setLineDash([]);

    // Fill Area Under Curve
    ctx.beginPath();
    ctx.moveTo(points[0].x, canvas.height - margin);
    ctx.lineTo(points[0].x, points[0].y);

    for (let i = 0; i < points.length - 1; i++) {
        const p0 = points[i > 0 ? i - 1 : i];
        const p1 = points[i];
        const p2 = points[i + 1];
        const p3 = points[i + 2 < points.length ? i + 2 : i + 1];

        const cp1x = p1.x + (p2.x - p0.x) / 6 * 0.5;
        const cp1y = p1.y + (p2.y - p0.y) / 6 * 0.5;
        const cp2x = p2.x - (p3.x - p1.x) / 6 * 0.5;
        const cp2y = p2.y - (p3.y - p1.y) / 6 * 0.5;

        ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
    }

    ctx.lineTo(points.at(-1).x, canvas.height - margin);
    ctx.closePath();
    ctx.fillStyle = stroke + "33";
    ctx.fill();

    // Draw the smoothed top line
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 2;
    drawSmoothLine(ctx, points);

    // Axis labels
    if (x_label) {
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(x_label, canvas.width / 2, canvas.height - 8);
    }

    if (y_label) {
        ctx.save();
        ctx.translate(12, canvas.height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.textAlign = "center";
        ctx.fillStyle = style.text;
        ctx.font = "12px Courier New";
        ctx.fillText(y_label, 0, 0);
        ctx.restore();
    }
}


async function renderGraphRadar(entry) {
    const {
        labels,
        values,
        color,
        title = ""
    } = entry.params;

    const theme = entry.params.theme ?? "dark";
    const transparent = entry.params.transparent ?? false;

    if (!labels || !values || labels.length !== values.length || labels.length < 3 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const stroke = generateCrucialShadesN(color, 1)[0];

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2 + 10;
    const radius = Math.min(canvas.width, canvas.height) / 2 - 50;
    const angleStep = (2 * Math.PI) / labels.length;
    const maxValue = Math.max(...values);

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, 40);
    }

    // Radar grid: concentric rings + spokes
    const levels = 5;

    ctx.strokeStyle = style.grid;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);

    for (let l = 1; l <= levels; l++) {
        const r = (radius * l) / levels;
        ctx.beginPath();
        for (let i = 0; i <= labels.length; i++) {
            const angle = i * angleStep;
            const x = centerX + r * Math.cos(angle);
            const y = centerY + r * Math.sin(angle);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.stroke();
    }

    for (let i = 0; i < labels.length; i++) {
        const angle = i * angleStep;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(x, y);
        ctx.stroke();
    }

    ctx.setLineDash([]);

    // Radar shape
    const radarPoints = values.map((v, i) => {
        const r = (v / maxValue) * radius;
        const angle = i * angleStep;
        return {
            x: centerX + r * Math.cos(angle),
            y: centerY + r * Math.sin(angle)
        };
    });

    // Fill shape
    ctx.beginPath();
    ctx.moveTo(radarPoints[0].x, radarPoints[0].y);
    for (let p of radarPoints.slice(1)) {
        ctx.lineTo(p.x, p.y);
    }
    ctx.closePath();
    ctx.fillStyle = stroke + "33";
    ctx.fill();

    // Outline
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(radarPoints[0].x, radarPoints[0].y);
    for (let p of radarPoints.slice(1)) {
        ctx.lineTo(p.x, p.y);
    }
    ctx.closePath();
    ctx.stroke();

    // Labels
    ctx.fillStyle = style.text;
    ctx.font = "12px Courier New";
    ctx.textAlign = "center";
    for (let i = 0; i < labels.length; i++) {
        const angle = i * angleStep;
        const x = centerX + (radius + 20) * Math.cos(angle);
        const y = centerY + (radius + 20) * Math.sin(angle);
        ctx.fillText(labels[i], x, y);
    }
}

async function renderGraphGauge(entry) {
    const {
        value,
        label,
        color,
        title = ""
    } = entry.params;

    const theme = entry.params.theme ?? "dark";
    const transparent = entry.params.transparent ?? false;

    if (typeof value !== "number" || value < 0 || value > 100 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const stroke = generateCrucialShadesN(color, 1)[0];
    const arcWidth = 30;
    const margin = 40;

    const centerX = canvas.width / 2;
    const radius = Math.min(canvas.width, canvas.height) / 2 - margin;

    // Adjust centerY to visually center arc + label block
    const arcHeight = radius + arcWidth / 2;
    const textHeight = 40;
    const totalHeight = arcHeight + textHeight;
    const centerY = (canvas.height / 2) + (arcHeight - textHeight / 2) / 2;

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 20px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, centerX, margin);
    }

    // Gauge background (full arc in dim grid color)
    ctx.beginPath();
    ctx.lineWidth = arcWidth;
    ctx.lineCap = "round";
    ctx.strokeStyle = style.grid;
    ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
    ctx.stroke();

    // Gauge value arc (overlay)
    const valueAngle = Math.PI + (Math.PI * value / 100);
    ctx.beginPath();
    ctx.strokeStyle = stroke;
    ctx.arc(centerX, centerY, radius, Math.PI, valueAngle);
    ctx.stroke();

    // Value %
    ctx.fillStyle = style.text;
    ctx.font = "bold 28px Courier New";
    ctx.textAlign = "center";
    ctx.fillText(`${value.toFixed(0)}%`, centerX, centerY + 10);

    // Lower Label
    if (label) {
        ctx.font = "14px Courier New";
        ctx.fillText(label, centerX, centerY + 36);
    }
}

async function renderGraphWordcloud(entry) {
    const {
        word_texts,
        word_values,
        color,
        theme = "dark",
        title = "",
        transparent = false
    } = entry.params;

    if (!word_texts || !word_values || word_texts.length !== word_values.length || word_texts.length === 0 || !color) return;

    const style = themeStyles[theme] || themeStyles["dark"];
    const shades = generateCrucialShadesN(color, word_texts.length);

    const margin = 40;
    const titlePad = title ? 30 : 0;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    const minVal = Math.min(...word_values);
    const maxVal = Math.max(...word_values);

    // Background
    if (!transparent) {
        ctx.fillStyle = style.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Title
    if (title) {
        ctx.fillStyle = style.text;
        ctx.font = "bold 18px Courier New";
        ctx.textAlign = "center";
        ctx.fillText(title, canvas.width / 2, margin);
    }

    // Prepare word list sorted by size
    const wordList = word_texts.map((text, i) => ({
        text,
        value: word_values[i],
        color: shades[i]
    })).sort((a, b) => b.value - a.value);

    // Occupancy map for collision detection
    const placedWords = [];

    function checkOverlap(x, y, w, h) {
        return placedWords.some(word => {
            return !(
                x + w < word.x || word.x + word.w < x ||
                y + h < word.y || word.y + word.h < y
            );
        });
    }

    function placeOnSpiral(wordWidth, wordHeight) {
        let angle = 0;
        let radius = 0;
        const spiralStep = 4;
        const angleStep = 0.2;

        while (radius < Math.max(canvas.width, canvas.height)) {
            const x = centerX + radius * Math.cos(angle) - wordWidth / 2;
            const y = centerY + radius * Math.sin(angle) + wordHeight / 2;

            if (
                x > margin &&
                y > margin + titlePad &&
                x + wordWidth < canvas.width - margin &&
                y + wordHeight < canvas.height - margin
            ) {
                if (!checkOverlap(x, y - wordHeight, wordWidth, wordHeight)) {
                    return { x, y };
                }
            }

            angle += angleStep;
            radius += spiralStep * angleStep;
        }

        return null;
    }

    for (let i = 0; i < wordList.length; i++) {
        const { text, value, color } = wordList[i];

        const fontSize = 14 + ((value - minVal) / (maxVal - minVal || 1)) * 36;
        ctx.font = `bold ${fontSize}px Courier New`;
        const wordWidth = ctx.measureText(text).width;
        const wordHeight = fontSize;

        const position = placeOnSpiral(wordWidth, wordHeight);
        if (position) {
            ctx.fillStyle = color;
            ctx.textAlign = "left";
            ctx.fillText(text, position.x, position.y);
            placedWords.push({
                x: position.x,
                y: position.y - wordHeight,
                w: wordWidth,
                h: wordHeight
            });

            await sleep(10 * config.drawing.speed);
        }
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
