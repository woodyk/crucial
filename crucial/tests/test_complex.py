#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_complex.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-07 18:23:00
# Modified: 2025-05-07 23:56:28
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_complex.py
# Description: Generates a highly complex image using the Crucial API
# Author: Ms. White
# Updated: 2025-05-07

import requests
import random
import math  # Import the math module for trigonometric functions

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
        "name": "Complex Image Test",
        "x": 1000,
        "y": 800,
        "color": "#ffffff"
    }
    response = requests.post(f"{BASE_URL}/canvas/create", json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["canvas_id"]

def test_complex_rendering():
    canvas_id = create_canvas()
    print(f"[✓] Canvas created: {canvas_id}")

    # Draw a complex background with arcs
    for i in range(0, 360, 10):
        post_canvas_action("draw_arc", {
            "canvas_id": canvas_id,
            "center_x": 500,
            "center_y": 400,
            "radius": 300,
            "start_angle": i,
            "end_angle": i + 5,
            "color": f'#{random.randint(0, 0xFFFFFF):06x}',
            "width": 10
        })

    # Draw a series of random circles
    for _ in range(20):
        post_canvas_action("draw_circle", {
            "canvas_id": canvas_id,
            "center_x": random.randint(50, 950),
            "center_y": random.randint(50, 750),
            "radius": random.randint(20, 70),
            "color": f'#{random.randint(0, 0xFFFFFF):06x}',
            "fill": f'#{random.randint(0, 0xFFFFFF):06x}'
        })

    # Draw lines forming a star shape
    for i in range(0, 360, 36):
        post_canvas_action("draw_line", {
            "canvas_id": canvas_id,
            "start_x": 500,
            "start_y": 400,
            "end_x": int(500 + 400 * random.uniform(0.5, 1) * math.cos(math.radians(i))),  # Use math.cos
            "end_y": int(400 + 400 * random.uniform(0.5, 1) * math.sin(math.radians(i))),  # Use math.sin
            "color": f'#{random.randint(0, 0xFFFFFF):06x}',
            "width": 4
        })

    # Draw polygons of varying sizes
    for _ in range(5):
        points = [[random.randint(100, 900), random.randint(100, 700)] for _ in range(3, 6)]
        post_canvas_action("draw_polygon", {
            "canvas_id": canvas_id,
            "points": points,
            "color": f'#{random.randint(0, 0xFFFFFF):06x}',
            "fill": f'#{random.randint(0, 0xFFFFFF):06x}'
        })

    # Draw text
    post_canvas_action("draw_text", {
        "canvas_id": canvas_id,
        "text": "Creative Canvas Rendering!",
        "x": 200,
        "y": 50,
        "font": "Arial",
        "size": 30,
        "color": "#000080"
    })

    print("[✓] Complex image rendered successfully.")
    print(f"[→] View at: {BASE_URL}/?id={canvas_id}")

if __name__ == "__main__":
    test_complex_rendering()
