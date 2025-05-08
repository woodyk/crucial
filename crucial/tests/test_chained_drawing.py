#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_chained_drawing.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-07 11:14:30
# Modified: 2025-05-07 23:55:48
import requests

API_KEY = "demo-key"
BASE_URL = "http://localhost:8000"
HEADERS = {"x-api-key": API_KEY}

def post_canvas(action, params):
    response = requests.post(
        f"{BASE_URL}/canvas",
        json={"action": action, "params": params},
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()

def post_create(data):
    response = requests.post(
        f"{BASE_URL}/canvas/create",
        json=data,
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()

def test_chained_canvas_draw():
    # Create canvas
    create_res = post_create({
        "name": "Chained Drawing Test",
        "x": 800,
        "y": 600,
        "color": "#ffffff"
    })
    canvas_id = create_res["canvas_id"]
    print(f"[✓] Canvas created: {canvas_id}")

    # Draw rectangle
    post_canvas("draw_rectangle", {
        "canvas_id": canvas_id,
        "x": 100,
        "y": 100,
        "width": 300,
        "height": 200,
        "color": "#000000",
        "fill": "#cccccc"
    })

    # Draw circle
    post_canvas("draw_circle", {
        "canvas_id": canvas_id,
        "center_x": 250,
        "center_y": 200,
        "radius": 50,
        "color": "#ff0000",
        "fill": "#ffaaaa"
    })

    # Draw line
    post_canvas("draw_line", {
        "canvas_id": canvas_id,
        "start_x": 0,
        "start_y": 0,
        "end_x": 800,
        "end_y": 600,
        "color": "#00aa00",
        "width": 3
    })

    # Draw text
    post_canvas("draw_text", {
        "canvas_id": canvas_id,
        "text": "Hello Crucial",
        "x": 300,
        "y": 300,
        "font": "Arial",
        "size": 24,
        "color": "#0000ff"
    })

    print("[✓] Drawing actions sent successfully.")
    print(f"[→] View at: {BASE_URL}/?id={canvas_id}")

if __name__ == "__main__":
    test_chained_canvas_draw()
