#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_realistic_rendering.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-07 23:57:04
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_realistic_rendering.py
# Description: Generates a detailed, realistic rendering using the Crucial API
# Author: Ms. White
# Updated: 2025-05-07

import requests
import random
import math

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
        "name": "Realistic Object Rendering",
        "x": 800,
        "y": 600,
        "color": "#ffffff"
    }
    response = requests.post(f"{BASE_URL}/canvas/create", json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["canvas_id"]

def draw_realistic_object(canvas_id):
    # Draw a sun
    post_canvas_action("draw_circle", {
        "canvas_id": canvas_id,
        "center_x": 700,
        "center_y": 100,
        "radius": 50,
        "color": "#ffdf00",
        "fill": "#ffdf00"
    })

    # Draw rays around the sun
    for angle in range(0, 360, 15):
        post_canvas_action("draw_line", {
            "canvas_id": canvas_id,
            "start_x": 700 + 50 * math.cos(math.radians(angle)),
            "start_y": 100 + 50 * math.sin(math.radians(angle)),
            "end_x": 700 + 70 * math.cos(math.radians(angle)),
            "end_y": 100 + 70 * math.sin(math.radians(angle)),
            "color": "#ffdf00",
            "width": 2
        })

    # Draw a tree trunk
    post_canvas_action("draw_rectangle", {
        "canvas_id": canvas_id,
        "x": 100,
        "y": 300,
        "width": 30,
        "height": 100,
        "color": "#8B4513",
        "fill": "#8B4513"
    })

    # Draw tree leaves
    for i in range(5):
        post_canvas_action("draw_circle", {
            "canvas_id": canvas_id,
            "center_x": 85 + random.randint(-30, 30),
            "center_y": 250 - i * 20,
            "radius": 40,
            "color": f'#{random.randint(0, 0x00FF00):06x}',
            "fill": f'#{random.randint(0, 0x00FF00):06x}'
        })

    # Draw ground
    post_canvas_action("draw_rectangle", {
        "canvas_id": canvas_id,
        "x": 0,
        "y": 400,
        "width": 800,
        "height": 200,
        "color": "#228B22",
        "fill": "#228B22"
    })

    # Draw a house
    post_canvas_action("draw_rectangle", {
        "canvas_id": canvas_id,
        "x": 500,
        "y": 350,
        "width": 200,
        "height": 150,
        "color": "#ffcc00",
        "fill": "#ffcc00"
    })

    # Draw house roof
    points = [[500, 350], [600, 250], [700, 350]]
    post_canvas_action("draw_polygon", {
        "canvas_id": canvas_id,
        "points": points,
        "color": "#8B0000",
        "fill": "#8B0000"
    })

    # Draw windows
    for x in [540, 640]:
        post_canvas_action("draw_rectangle", {
            "canvas_id": canvas_id,
            "x": x,
            "y": 400,
            "width": 40,
            "height": 40,
            "color": "#ffffff",
            "fill": "#ffffff"
        })

    # Draw door
    post_canvas_action("draw_rectangle", {
        "canvas_id": canvas_id,
        "x": 590,
        "y": 450,
        "width": 60,
        "height": 50,
        "color": "#654321",
        "fill": "#654321"
    })

    print("[✓] Realistic object rendered successfully.")
    print(f"[→] View at: {BASE_URL}/?id={canvas_id}")

if __name__ == "__main__":
    canvas_id = create_canvas()
    draw_realistic_object(canvas_id)
