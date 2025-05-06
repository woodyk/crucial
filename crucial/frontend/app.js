import { config } from './config.js';

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const canvasNameDiv = document.createElement('div');
document.body.appendChild(canvasNameDiv);

let canvasId = new URLSearchParams(window.location.search).get('id');
if (!canvasId) {
    canvasId = window.location.pathname.split('/').pop();
}
if (!canvasId) throw new Error("No canvas id");

canvasNameDiv.style.position = 'absolute';
canvasNameDiv.style[config.canvasName.position.replace('-', '')] = '10px';
canvasNameDiv.style.color = config.canvasName.color;
canvasNameDiv.style.font = config.canvasName.font;
canvasNameDiv.style.opacity = 0;

let history = [];
let renderedIndex = 0;
let isFramed = false;

function createFrame(width, height) {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.style.background = `url(${config.transparencyGrid.backgroundImage})`;
    document.body.style.backgroundSize = config.transparencyGrid.backgroundSize;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function fadeInBackground(color, duration) {
    let step = 0;
    const steps = 30;
    const interval = duration / steps;
    const [r, g, b] = hexToRgb(color);
    const intervalId = setInterval(() => {
        let alpha = (++step) / steps;
        ctx.fillStyle = `rgba(${r},${g},${b},${alpha})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (step >= steps) clearInterval(intervalId);
    }, interval);
}

function showCanvasName(name) {
    if (!config.canvasName.show) return;
    canvasNameDiv.innerText = name;
    canvasNameDiv.style.transition = `opacity ${config.canvasName.fadeDuration}ms ease`;
    canvasNameDiv.style.opacity = 1;
}

// ====================== Render Registry =======================

const renderRegistry = {
    'canvas_create': renderCreate,
    'canvas_draw_line': renderDrawLine,
    'canvas_draw_circle': renderCircle,
    'canvas_draw_rectangle': renderRectangle,
    'canvas_draw_text': renderText,
    'canvas_draw_point': renderPoint
};

// ====================== Render Functions ======================

function renderCreate(entry) {
    const { name, x, y, color } = entry.params;
    if (!isFramed) {
        createFrame(x, y);
        isFramed = true;
        fadeInBackground(color, config.backgroundFadeDuration);
        setTimeout(() => showCanvasName(name), config.backgroundFadeDuration);
    }
}

function renderDrawLine(entry) {
    const { start_x, start_y, end_x, end_y, color, width } = entry.params;
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.beginPath();
    ctx.moveTo(start_x, start_y);
    ctx.lineTo(end_x, end_y);
    ctx.stroke();
}

function renderCircle(entry) {
    const { center_x, center_y, radius, color, fill } = entry.params;
    ctx.beginPath();
    ctx.arc(center_x, center_y, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = color;
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.stroke();
}

function renderRectangle(entry) {
    const { x, y, width, height, color, fill } = entry.params;
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.strokeStyle = color;
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.stroke();
}

function renderText(entry) {
    const { text, x, y, font, size, color } = entry.params;
    ctx.font = `${size}px ${font}`;
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);
}

function renderPoint(entry) {
    const { x, y, color, radius } = entry.params;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
}

// ====================== Dispatcher & Polling ======================

function renderNextAction() {
    if (renderedIndex >= history.length) return;
    const entry = history[renderedIndex++];
    const fn = renderRegistry[entry.action];
    if (fn) fn(entry);
    else console.warn("Unknown action:", entry.action);
}

function hexToRgb(hex) {
    const parsed = hex.startsWith('#') ? hex.slice(1) : hex;
    const bigint = parseInt(parsed, 16);
    return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
}

function pollHistory() {
    fetch(`/object/${canvasId}/history`)
        .then(r => r.json())
        .then(actions => {
            if (actions.length > history.length) {
                history = actions;
                renderNextAction(); // play one frame per poll tick
            }
        });
}

setInterval(pollHistory, config.pollIntervalMs);
