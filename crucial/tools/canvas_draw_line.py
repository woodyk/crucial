#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: canvas_draw_line.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-07 12:40:26
import requests

def canvas_draw_line(canvas_id, start_x, start_y, end_x, end_y, color, width):
    payload = {
        "action": "canvas_draw_line",
        "canvas_id": canvas_id,
        "start_x": start_x,
        "start_y": start_y,
        "end_x": end_x,
        "end_y": end_y,
        "color": color,
        "width": width
    }
    headers = {"x-api-key": "demo-key"}
    return requests.post("http://localhost:8000/canvas/draw_line", json=payload, headers=headers)
