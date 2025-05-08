#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_graph_canvases.py
# Description: Compatibility tests for Crucial graph_* endpoints
# Author: Ms. White
# Created: 2025-05-08

import requests

API = "http://localhost:8000"

def post(action, params):
    response = requests.post(f"{API}/canvas", json={
        "action": action,
        "params": params
    })
    response.raise_for_status()
    print(f"[✓] {action} sent")
    return response

def create_canvas(name):
    response = requests.post(f"{API}/canvas/create", json={
        "name": name,
        "x": 800,
        "y": 600,
        "color": "#111111"
    })
    response.raise_for_status()
    canvas_id = response.json().get("canvas_id")
    print(f"[✓] Canvas created: {canvas_id}")
    return canvas_id

def main():
    # 1. Bar Chart
    canvas1 = create_canvas("Graph - Bar")
    post("graph_bar", {
        "canvas_id": canvas1,
        "data": [
            {"label": "A", "value": 10},
            {"label": "B", "value": 20},
            {"label": "C", "value": 15}
        ],
        "color": "#4ba3ff",
        "title": "Bar Chart",
        "theme": "dark"
    })

    # 2. Pie Chart
    canvas2 = create_canvas("Graph - Pie")
    post("graph_pie", {
        "canvas_id": canvas2,
        "data": [
            {"label": "Red", "value": 30},
            {"label": "Blue", "value": 50},
            {"label": "Green", "value": 20}
        ],
        "color": "#1abc9c",
        "title": "Pie Distribution",
        "theme": "light"
    })

    # 3. Line Graph
    canvas3 = create_canvas("Graph - Line")
    post("graph_line", {
        "canvas_id": canvas3,
        "data": [
            {"x": 0, "y": 10},
            {"x": 1, "y": 20},
            {"x": 2, "y": 12},
            {"x": 3, "y": 30}
        ],
        "color": "#ff6600",
        "title": "Line Trend",
        "theme": "dark"
    })

    # 4. Heatmap
    canvas4 = create_canvas("Graph - Heatmap")
    post("graph_heatmap", {
        "canvas_id": canvas4,
        "matrix": [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ],
        "color": "#9b59b6",
        "title": "Heatmap Grid",
        "theme": "dark"
    })

    # 5. Gauge
    canvas5 = create_canvas("Graph - Gauge")
    post("graph_gauge", {
        "canvas_id": canvas5,
        "value": 73,
        "label": "Usage %",
        "color": "#e67e22",
        "title": "Gauge Meter",
        "theme": "light"
    })

if __name__ == "__main__":
    main()

