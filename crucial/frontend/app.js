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
    'canvas_draw_point': renderPoint,
    'canvas_draw_arc': renderArc,
    'canvas_draw_polygon': renderPolygon,
    'canvas_clear': renderClear,
    'canvas_draw_bezier': renderBezier,
    'canvas_graph_bar': renderGraphBar,
    'canvas_graph_heatmap': renderGraphHeatmap,
    'canvas_graph_histogram': renderGraphHistogram,
    'canvas_graph_line': renderGraphLine,
    'canvas_graph_pie': renderGraphPie,
    'canvas_graph_scatter': renderGraphScatter,


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


function animateCircle(center_x, center_y, radius, color, fill, duration) {
    let step = 0;
    const steps = 60;
    const ctx2 = ctx;
    const angleStep = (2 * Math.PI) / steps;
    const brushRadius = Math.max(2, radius * 0.05);
    const interval = duration / steps;

    let drawPoints = [];

    for (let i = 0; i <= steps; i++) {
        const angle = i * angleStep;
        const x = center_x + radius * Math.cos(angle);
        const y = center_y + radius * Math.sin(angle);
        drawPoints.push({x, y});
    }

    ctx2.beginPath();
    ctx2.moveTo(drawPoints[0].x, drawPoints[0].y);

    const intervalId = setInterval(() => {
        if (step >= drawPoints.length) {
            if (fill) {
                ctx2.fillStyle = fill;
                ctx2.fill();
            }
            ctx2.strokeStyle = color;
            ctx2.stroke();
            clearInterval(intervalId);
            return;
        }

        const pt = drawPoints[step];
        ctx2.lineTo(pt.x, pt.y);

        // draw ghost brush
        if (config.drawing.ghostBrushEnabled) {
            ctx2.save();
            ctx2.beginPath();
            ctx2.arc(pt.x, pt.y, brushRadius, 0, 2 * Math.PI);
            ctx2.strokeStyle = config.drawing.brushColor;
            ctx2.stroke();
            ctx2.restore();
        }

        step++;
    }, interval);
}

function animateRectangle(x, y, width, height, color, fill, duration) {
    const ctx2 = ctx;
    const steps = 100;
    const interval = duration / steps;
    const segments = [
        { x1: x, y1: y, x2: x + width, y2: y },               // top
        { x1: x + width, y1: y, x2: x + width, y2: y + height }, // right
        { x1: x + width, y1: y + height, x2: x, y2: y + height }, // bottom
        { x1: x, y1: y + height, x2: x, y2: y }                // left
    ];

    let currentSeg = 0;
    let t = 0;

    ctx2.beginPath();
    ctx2.moveTo(x, y);

    const intervalId = setInterval(() => {
        if (currentSeg >= segments.length) {
            if (fill) {
                ctx2.fillStyle = fill;
                ctx2.fill();
            }
            ctx2.strokeStyle = color;
            ctx2.stroke();
            clearInterval(intervalId);
            return;
        }

        const seg = segments[currentSeg];
        const x = seg.x1 + (seg.x2 - seg.x1) * t;
        const y = seg.y1 + (seg.y2 - seg.y1) * t;

        ctx2.lineTo(x, y);

        if (config.drawing.ghostBrushEnabled) {
            ctx2.save();
            ctx2.beginPath();
            ctx2.arc(x, y, 3, 0, 2 * Math.PI);
            ctx2.strokeStyle = config.drawing.brushColor;
            ctx2.stroke();
            ctx2.restore();
        }

        t += 1 / (steps / 4); // divide total steps among 4 edges
        if (t >= 1) {
            t = 0;
            currentSeg++;
        }
    }, interval);
}

function renderCircle(entry) {
    const { center_x, center_y, radius, color, fill } = entry.params;
    const dur = 1000 * config.drawing.speed;
    animateCircle(center_x, center_y, radius, color, fill, dur);
}

function renderRectangle(entry) {
    const { x, y, width, height, color, fill } = entry.params;
    const dur = 1000 * config.drawing.speed;
    animateRectangle(x, y, width, height, color, fill, dur);
}


function animateArc(center_x, center_y, radius, start_angle, end_angle, color, width, duration) {
    let step = 0;
    const steps = 60;
    const ctx2 = ctx;
    const angleStep = (end_angle - start_angle) / steps;
    const brushRadius = width;
    const interval = duration / steps;

    ctx2.beginPath();
    const sx = center_x + radius * Math.cos(start_angle);
    const sy = center_y + radius * Math.sin(start_angle);
    ctx2.moveTo(sx, sy);

    const intervalId = setInterval(() => {
        if (step > steps) {
            ctx2.strokeStyle = color;
            ctx2.lineWidth = width;
            ctx2.stroke();
            clearInterval(intervalId);
            return;
        }

        const angle = start_angle + angleStep * step;
        const x = center_x + radius * Math.cos(angle);
        const y = center_y + radius * Math.sin(angle);
        ctx2.lineTo(x, y);

        if (config.drawing.ghostBrushEnabled) {
            ctx2.save();
            ctx2.beginPath();
            ctx2.arc(x, y, brushRadius, 0, 2 * Math.PI);
            ctx2.strokeStyle = config.drawing.brushColor;
            ctx2.stroke();
            ctx2.restore();
        }

        step++;
    }, interval);
}

function animatePolygon(points, color, fill, duration) {
    const ctx2 = ctx;
    let step = 0;
    const totalSegments = points.length;
    const interval = duration / totalSegments;
    let current = 0;

    ctx2.beginPath();
    ctx2.moveTo(points[0][0], points[0][1]);

    const intervalId = setInterval(() => {
        if (current >= totalSegments) {
            if (fill) {
                ctx2.fillStyle = fill;
                ctx2.fill();
            }
            ctx2.strokeStyle = color;
            ctx2.stroke();
            clearInterval(intervalId);
            return;
        }

        const [x, y] = points[current];
        ctx2.lineTo(x, y);

        if (config.drawing.ghostBrushEnabled) {
            ctx2.save();
            ctx2.beginPath();
            ctx2.arc(x, y, 3, 0, 2 * Math.PI);
            ctx2.strokeStyle = config.drawing.brushColor;
            ctx2.stroke();
            ctx2.restore();
        }

        current++;
    }, interval);
}

function renderArc(entry) {
    const { center_x, center_y, radius, start_angle, end_angle, color, width } = entry.params;
    const dur = 1000 * config.drawing.speed;
    animateArc(center_x, center_y, radius, start_angle, end_angle, color, width, dur);
}

function renderPolygon(entry) {
    const { points, color, fill } = entry.params;
    const dur = 1000 * config.drawing.speed;
    animatePolygon(points, color, fill, dur);
}

function renderClear(entry) {
    ctx.save();
    ctx.globalAlpha = 1.0;
    ctx.fillStyle = "#ffffff";
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();
}

function getBezierPoint(t, points) {
    const n = points.length - 1;
    let x = 0, y = 0;
    for (let i = 0; i <= n; i++) {
        const bin = binomial(n, i);
        const pow1 = Math.pow(1 - t, n - i);
        const pow2 = Math.pow(t, i);
        x += bin * pow1 * pow2 * points[i][0];
        y += bin * pow1 * pow2 * points[i][1];
    }
    return { x, y };
}

function binomial(n, k) {
    let res = 1;
    for (let i = 0; i < k; ++i) {
        res *= (n - i) / (i + 1);
    }
    return res;
}

function animateBezier(control_points, color, width, duration) {
    const ctx2 = ctx;
    ctx2.beginPath();
    const steps = 100;
    const interval = duration / steps;
    let t = 0;
    let step = 0;

    ctx2.moveTo(control_points[0][0], control_points[0][1]);

    const intervalId = setInterval(() => {
        if (step > steps) {
            ctx2.strokeStyle = color;
            ctx2.lineWidth = width;
            ctx2.stroke();
            clearInterval(intervalId);
            return;
        }

        const { x, y } = getBezierPoint(t, control_points);
        ctx2.lineTo(x, y);

        if (config.drawing.ghostBrushEnabled) {
            ctx2.save();
            ctx2.beginPath();
            ctx2.arc(x, y, 2, 0, 2 * Math.PI);
            ctx2.strokeStyle = config.drawing.brushColor;
            ctx2.stroke();
            ctx2.restore();
        }

        t += 1 / steps;
        step++;
    }, interval);
}

function renderBezier(entry) {
    const { control_points, color, width } = entry.params;
    const dur = 1000 * config.drawing.speed;
    animateBezier(control_points, color, width, dur);
}


function renderGraphBar(entry) {
    const { data, position, colors } = entry.params;
    const ctx2 = ctx;
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;

    const margin = 50;
    const barGap = 20;
    const maxBarHeight = canvasHeight - 2 * margin;
    const barWidth = (canvasWidth - 2 * margin - barGap * (data.length - 1)) / data.length;

    const maxValue = Math.max(...data.map(d => d.value));
    let step = 0;

    function drawBar(index) {
        if (index >= data.length) return;

        const value = data[index].value;
        const label = data[index].label;
        const height = (value / maxValue) * maxBarHeight;
        const x = margin + index * (barWidth + barGap);
        const y = canvasHeight - margin - height;

        let currentHeight = 0;
        const steps = 30;
        const increment = height / steps;
        const interval = 800 / steps;

        const color = (colors && colors[index]) || config.graph.bar.defaultColor;

        const animId = setInterval(() => {
            ctx2.fillStyle = color;
            ctx2.fillRect(x, canvasHeight - margin - currentHeight, barWidth, currentHeight);

            ctx2.fillStyle = config.graph.bar.labelColor;
            ctx2.font = config.graph.bar.labelFont;
            ctx2.fillText(label, x, canvasHeight - margin + 15);

            currentHeight += increment;
            if (currentHeight >= height) {
                clearInterval(animId);
                drawBar(index + 1);
            }
        }, interval);
    }

    drawBar(0);
}

// ====================== Graph Render Placeholders ======================

// TODO: Implement canvas_graph_bar rendering (animated bar chart)
function renderGraphBar(entry) {
    console.warn("canvas_graph_bar not yet implemented");
}

// TODO: Implement canvas_graph_heatmap rendering (cell matrix color fill)
function renderGraphHeatmap(entry) {
    console.warn("canvas_graph_heatmap not yet implemented");
}

// TODO: Implement canvas_graph_histogram rendering (value bin buckets)
function renderGraphHistogram(entry) {
    console.warn("canvas_graph_histogram not yet implemented");
}

// TODO: Implement canvas_graph_line rendering (animated polyline over data)
function renderGraphLine(entry) {
    console.warn("canvas_graph_line not yet implemented");
}

// TODO: Implement canvas_graph_pie rendering (circular sector fill by label/value)
function renderGraphPie(entry) {
    console.warn("canvas_graph_pie not yet implemented");
}

// TODO: Implement canvas_graph_scatter rendering (dots in X/Y coordinate space)
function renderGraphScatter(entry) {
    console.warn("canvas_graph_scatter not yet implemented");
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
