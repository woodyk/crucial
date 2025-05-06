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
}

graph: {
    bar: {
        defaultColor: "#3498db",
        labelFont: "12px sans-serif",
        labelColor: "#ffffff"
    }
},

    animateShapes: true,
    shapeAnimationSpeed: 1.0,
    ghostBrushEnabled: true,
    ghostBrushStyle: {
        color: "#ffffff88",
        sizeFactor: 1.0,
        outline: true
    },
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
