import requests

def canvas_draw_line(object_uri, start_x, start_y, end_x, end_y, color, width):
    payload = {
        "action": "canvas_draw_line",
        "object_uri": object_uri,
        "start_x": start_x,
        "start_y": start_y,
        "end_x": end_x,
        "end_y": end_y,
        "color": color,
        "width": width
    }
    headers = {"x-api-key": "demo-key"}
    return requests.post("http://localhost:8000/canvas/draw_line", json=payload, headers=headers)
