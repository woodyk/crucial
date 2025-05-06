// Crucial Frontend Visual Config

export const config = {
    backgroundFadeDuration: 1000,
    borderAnimationDuration: 800,
    canvasName: {
        show: true,
        position: "top-right",
        font: "12px sans-serif",
        color: "#cccccc",
        fadeDuration: 800
    },
    drawing: {
        brushFade: true,
        brushColor: "#ffffff88",
        minBrushRadius: 2,
        maxBrushRadius: 12,
        speed: 1.0
    },
    transparencyGrid: {
        backgroundImage: "../static/transparent-bg.png",
        backgroundSize: "40px 40px"
    },
    pollIntervalMs: 1000
};
