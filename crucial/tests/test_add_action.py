#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_add_action.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-08 18:05:23
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_realistic_rendering.py
# Description: Generates a detailed, realistic rendering using the Crucial API
# Author: Ms. White
# Updated: 2025-05-07

import sys
import requests
import random
import math

API_KEY = "demo-key"
BASE_URL = "http://localhost:8000"
HEADERS = {"x-api-key": API_KEY}

min_val = 0
max_val = 500

def post_canvas_action(action, params):
    response = requests.post(
        f"{BASE_URL}/canvas",
        json={"action": action, "params": params},
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()

def draw_object(canvas_id):
    post_canvas_action("draw_circle", {
        "canvas_id": canvas_id,
        "center_x": random.randint(min_val, max_val),
        "center_y": random.randint(min_val, max_val) ,
        "radius": 50,
        "color": "#ffdf00",
        "fill": "#ffdf00"
    })

    # Draw a tree trunk
    post_canvas_action("draw_rectangle", {
        "canvas_id": canvas_id,
        "x": random.randint(min_val, max_val),
        "y": random.randint(min_val, max_val),
        "width": 30,
        "height": 100,
        "color": "#8B4513",
        "fill": "#8B4513"
    })

    print("[✓] Realistic object rendered successfully.")
    print(f"[→] View at: {BASE_URL}/canvas/{canvas_id}")

if __name__ == "__main__":
    canvas_id = sys.argv[1]
    draw_object(canvas_id)
