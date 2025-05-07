//
// File: config.js
// Author: Wadih Khairallah
// Description: 
// Created: 2025-05-06 18:31:13
// Modified: 2025-05-06 20:01:28
export const config = {
    apiBase: "",
    pollingIntervalMs: 1000,
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
            labelFont: "12px sans-serif",
            labelColor: "#ffffff"
        },
        pie: {
            labelFont: "12px sans-serif",
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
    },
    pollingIntervalMs: 250
};
