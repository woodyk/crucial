//
// File: config.js
// Author: Wadih Khairallah
// Description: Crucial canvas frontend configuration
// Created: 2025-05-06
// Modified: 2025-05-08 15:26:51

export const config = {
    apiBase: "",
    pollingIntervalMs: 250,
    backgroundFadeDuration: 1000,

    canvasName: {
        show: true,
        position: "top-left",
        font: "12px sans-serif",
        color: "#cccccc",
        fadeDuration: 1000
    },

    drawing: {
        speed: 1.0,
        animateShapes: true,
        ghostBrushEnabled: true,
        brushColor: "#888888"
    },

    graph: {
        bar: {
            defaultColor: "#3498db",
            labelFont: "12px Courier New",
            labelColor: "#ffffff"
        },
        pie: {
            labelFont: "12px Courier New",
            labelColor: "#ffffff",
            colors: ["#e74c3c", "#2ecc71", "#3498db", "#f1c40f", "#9b59b6", "#1abc9c"]
        },
        line: {
            defaultColor: "#00ffff"
        },
        scatter: {
            defaultColor: "#ffff00"
        },
        histogram: {
            barColor: "#ff69b4"
        },
        heatmap: {
            emptyCellColor: "#222222"
        }
    },

    transparencyGrid: {
        backgroundImage: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAQAAACoWZ6PAAAAFklEQVR4AWNgYGD4z8DAwMDAwMAAAAwAAVMzCHxgAAAABJRU5ErkJggg==",
        backgroundSize: "20px 20px"
    }
};

export const themeStyles = {
    "dark": {
        background: "#000000",
        text: "#ffffff",
        accent: "#4ba3ff"
    },
    "light": {
        background: "#ffffff",
        text: "#000000",
        accent: "#0066cc"
    }
};

// ========== Color Utilities ==========

function hexToHSL(hex) {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;

    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0;
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h *= 60;
    }

    return [Math.round(h), Math.round(s * 100), Math.round(l * 100)];
}

function HSLtoHex(h, s, l) {
    s /= 100;
    l /= 100;
    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n => {
        const c = l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
        return Math.round(255 * c).toString(16).padStart(2, '0');
    };
    return `#${f(0)}${f(8)}${f(4)}`;
}

function generateCrucialShadesN(hex, count = 5) {
    const [h, s, l] = hexToHSL(hex);
    const step = 100 / (count + 1);
    return Array.from({ length: count }, (_, i) => {
        const shade = l + (i - Math.floor(count / 2)) * step;
        const clipped = Math.max(10, Math.min(90, shade));
        return HSLtoHex(h, s, clipped);
    });
}

export { hexToHSL, HSLtoHex, generateCrucialShadesN };

