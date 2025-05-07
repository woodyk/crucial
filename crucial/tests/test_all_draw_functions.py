#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_all_draw_functions.py
# Description: Validates all core drawing actions via the Crucial API
# Author: Ms. White
# Updated: 2025-05-07

import requests

API_KEY = "demo-key"
BASE_URL = "http://localhost:8000"
HEADERS = {"x-api-key": API_KEY}

def post_canvas_action(action, params):
    response = requests.post(
        f"{BASE_URL}/canvas",
        json={"action": action, "params": params},
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()

def create_canvas():
    payload = {
        "name": "Full Draw Test",
        "x": 1000,
        "y": 800,
        "color": "#ffffff"
    }
    response = requests.post(f"{BASE_URL}/canvas/create", json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["canvas_id"]

def test_all_draw_functions():
    canvas_id = create_canvas()
    print(f"[✓] Canvas created: {canvas_id}")

    # Line
    post_canvas_action("canvas_draw_line", {
        "canvas_id": canvas_id,
        "start_x": 50,
        "start_y": 50,
        "end_x": 300,
        "end_y": 50,
        "color": "#000000",
        "width": 2
    })

    # Circle
    post_canvas_action("canvas_draw_circle", {
        "canvas_id": canvas_id,
        "center_x": 400,
        "center_y": 150,
        "radius": 40,
        "color": "#222222",
        "fill": "#ffdddd"
    })

    # Rectangle
    post_canvas_action("canvas_draw_rectangle", {
        "canvas_id": canvas_id,
        "x": 500,
        "y": 100,
        "width": 150,
        "height": 100,
        "color": "#0000ff",
        "fill": "#add8e6"
    })

    # Polygon
    post_canvas_action("canvas_draw_polygon", {
        "canvas_id": canvas_id,
        "points": [[100, 300], [200, 350], [150, 400], [75, 370]],
        "color": "#800080",
        "fill": "#dda0dd"
    })

    # Arc
    post_canvas_action("canvas_draw_arc", {
        "canvas_id": canvas_id,
        "center_x": 700,
        "center_y": 150,
        "radius": 50,
        "start_angle": 0,
        "end_angle": 3.14,  # radians (π)
        "color": "#008000",
        "width": 3
    })

    # Bezier
    post_canvas_action("canvas_draw_bezier", {
        "canvas_id": canvas_id,
        "control_points": [[100, 500], [200, 450], [300, 550], [400, 500]],
        "color": "#ff4500",
        "width": 2
    })

    # Point
    post_canvas_action("canvas_draw_point", {
        "canvas_id": canvas_id,
        "x": 600,
        "y": 600,
        "color": "#000000",
        "radius": 3
    })

    # Text
    post_canvas_action("canvas_draw_text", {
        "canvas_id": canvas_id,
        "text": "Full Draw Test!",
        "x": 400,
        "y": 700,
        "font": "Verdana",
        "size": 26,
        "color": "#000080"
    })

    print("[✓] All draw functions tested successfully.")
    print(f"[→] View at: {BASE_URL}/?id={canvas_id}")

if __name__ == "__main__":
    test_all_draw_functions()

