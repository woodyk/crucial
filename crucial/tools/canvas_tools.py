"""
    Crucial Canvas Tools – LLM-Compatible
    -------------------------------------
    Unified function set for LLMs to control the Crucial canvas engine.
"""

import os
import json
import requests
from typing import List, Dict, Optional, Tuple

# Global configuration
CONFIG = {
    "url": "http://localhost:8000",
    "api_key": os.environ.get("CRUCIAL_API_KEY", "demo-key"),
    "last_canvas_id_file": os.path.join(os.path.dirname(__file__), ".last_canvas_id")
}

# === Internal utilities ===

def _get_last_canvas_id() -> Optional[str]:
    try:
        with open(CONFIG["last_canvas_id_file"], "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def _set_last_canvas_id(canvas_id: str) -> None:
    with open(CONFIG["last_canvas_id_file"], "w") as f:
        f.write(canvas_id.strip())

def _post(endpoint: str, payload: dict) -> dict:
    headers = {"x-api-key": CONFIG["api_key"]}
    url = f"{CONFIG['url']}{endpoint}"
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def _inject_canvas(payload: dict) -> dict:
    canvas_id = _get_last_canvas_id()
    if not canvas_id:
        raise ValueError("No canvas is active. Call canvas_create() first.")
    payload["canvas_id"] = canvas_id
    return payload

# === LLM Tool Functions ===

def canvas_create(name: str, x: int, y: int, color: str) -> dict:
    """Create a new canvas and persist its session ID.

    Args:
        name (str): Human-readable name for the canvas.
        x (int): Width of the canvas in pixels.
        y (int): Height of the canvas in pixels.
        color (str): Background color (e.g., "#ffffff").

    Returns:
        dict: Canvas metadata including canvas_id and dimensions.
    """
    payload = {"name": name, "x": x, "y": y, "color": color}
    result = _post("/canvas/create", payload)
    canvas_id = result.get("canvas_id")
    if not canvas_id:
        raise RuntimeError("Canvas creation failed.")
    _set_last_canvas_id(canvas_id)
    print(f"[✓] Created: {canvas_id}")
# Modified: 2025-05-07 12:42:06
    print(f"[🔗] View: {CONFIG['url']}/?id={canvas_id}")
    return result

def canvas_clear() -> dict:
    """Clear all content from the current canvas.

    Returns:
        dict: API response confirming the clear operation.
    """
    return _post("/canvas/clear", _inject_canvas({}))

def canvas_draw_line(start_x: int, start_y: int, end_x: int, end_y: int, color: str, width: int) -> dict:
    """Draw a line between two points.

    Args:
        start_x (int): X coordinate of the start.
        start_y (int): Y coordinate of the start.
        end_x (int): X coordinate of the end.
        end_y (int): Y coordinate of the end.
        color (str): Line color in hex.
        width (int): Line thickness.

    Returns:
        dict: API response for draw_line.
    """
    return _post("/canvas/draw_line", _inject_canvas({
        "start_x": start_x,
        "start_y": start_y,
        "end_x": end_x,
        "end_y": end_y,
        "color": color,
        "width": width
    }))

def canvas_draw_circle(center_x: int, center_y: int, radius: int, color: str, fill: str) -> dict:
    """Draw a circle on the canvas.

    Args:
        center_x (int): X coordinate of the center.
        center_y (int): Y coordinate of the center.
        radius (int): Radius of the circle.
        color (str): Stroke color.
        fill (str): Fill color.

    Returns:
        dict: API response for draw_circle.
    """
    return _post("/canvas/draw_circle", _inject_canvas({
        "center_x": center_x,
        "center_y": center_y,
        "radius": radius,
        "color": color,
        "fill": fill
    }))

def canvas_draw_rectangle(x: int, y: int, width: int, height: int, color: str, fill: str) -> dict:
    """Draw a rectangle on the canvas.

    Args:
        x (int): X coordinate of top-left.
        y (int): Y coordinate of top-left.
        width (int): Width of the rectangle.
        height (int): Height of the rectangle.
        color (str): Stroke color.
        fill (str): Fill color.

    Returns:
        dict: API response for draw_rectangle.
    """
    return _post("/canvas/draw_rectangle", _inject_canvas({
        "x": x, "y": y, "width": width, "height": height,
        "color": color, "fill": fill
    }))

def canvas_draw_polygon(points: List[Tuple[float, float]], color: str, fill: str) -> dict:
    """Draw a polygon with the specified vertices.

    Args:
        points (List[Tuple[float, float]]): List of vertex coordinates.
        color (str): Stroke color.
        fill (str): Fill color.

    Returns:
        dict: API response for draw_polygon.
    """
    return _post("/canvas/draw_polygon", _inject_canvas({
        "points": points, "color": color, "fill": fill
    }))

def canvas_draw_arc(center_x: int, center_y: int, radius: int, start_angle: float, end_angle: float, color: str, width: int) -> dict:
    """Draw a circular arc.

    Args:
        center_x (int): X center.
        center_y (int): Y center.
        radius (int): Arc radius.
        start_angle (float): Start angle in degrees.
        end_angle (float): End angle in degrees.
        color (str): Stroke color.
        width (int): Stroke width.

    Returns:
        dict: API response for draw_arc.
    """
    return _post("/canvas/draw_arc", _inject_canvas({
        "center_x": center_x,
        "center_y": center_y,
        "radius": radius,
        "start_angle": start_angle,
        "end_angle": end_angle,
        "color": color,
        "width": width
    }))

def canvas_draw_bezier(control_points: List[Tuple[float, float]], color: str, width: int) -> dict:
    """Draw a bezier curve.

    Args:
        control_points (List[Tuple[float, float]]): Control point list.
        color (str): Curve color.
        width (int): Stroke width.

    Returns:
        dict: API response for draw_bezier.
    """
    return _post("/canvas/draw_bezier", _inject_canvas({
        "control_points": control_points,
        "color": color,
        "width": width
    }))

def canvas_draw_point(x: int, y: int, color: str, radius: int) -> dict:
    """Draw a point or dot.

    Args:
        x (int): X coordinate.
        y (int): Y coordinate.
        color (str): Dot color.
        radius (int): Dot size.

    Returns:
        dict: API response for draw_point.
    """
    return _post("/canvas/draw_point", _inject_canvas({
        "x": x, "y": y, "color": color, "radius": radius
    }))

def canvas_draw_text(text: str, x: int, y: int, font: str, size: int, color: str) -> dict:
    """Draw text on the canvas.

    Args:
        text (str): Text content.
        x (int): X position.
        y (int): Y position.
        font (str): Font family.
        size (int): Font size.
        color (str): Text color.

    Returns:
        dict: API response for draw_text.
    """
    return _post("/canvas/draw_text", _inject_canvas({
        "text": text,
        "x": x,
        "y": y,
        "font": font,
        "size": size,
        "color": color
    }))

def canvas_set_background(color: str) -> dict:
    """Set the canvas background color.

    Args:
        color (str): Background color in hex.

    Returns:
        dict: API response for background change.
    """
    return _post("/canvas/set_background", _inject_canvas({"color": color}))

def canvas_translate(dx: float, dy: float) -> dict:
    """Translate the canvas space.

    Args:
        dx (float): Shift along X axis.
        dy (float): Shift along Y axis.

    Returns:
        dict: API response for translate.
    """
    return _post("/canvas/translate", _inject_canvas({"dx": dx, "dy": dy}))

def canvas_rotate(angle_in_degrees: float) -> dict:
    """Rotate the canvas space.

    Args:
        angle_in_degrees (float): Angle to rotate.

    Returns:
        dict: API response for rotate.
    """
    return _post("/canvas/rotate", _inject_canvas({"angle_in_degrees": angle_in_degrees}))

def canvas_scale(scale_x: float, scale_y: float) -> dict:
    """Scale the canvas space.

    Args:
        scale_x (float): X-axis scale factor.
        scale_y (float): Y-axis scale factor.

    Returns:
        dict: API response for scale.
    """
    return _post("/canvas/scale", _inject_canvas({"scale_x": scale_x, "scale_y": scale_y}))

def canvas_save(file_path: str, format: str) -> dict:
    """Save the canvas to a file.

    Args:
        file_path (str): Path to save.
        format (str): File format.

    Returns:
        dict: API response for save.
    """
    return _post("/canvas/save", _inject_canvas({"file_path": file_path, "format": format}))

def canvas_render_threejs(script: str) -> dict:
    """Inject a Three.js script to render.

    Args:
        script (str): JavaScript source code.

    Returns:
        dict: API response for render.
    """
    return _post("/canvas/render_threejs", _inject_canvas({"script": script}))

def canvas_graph_bar(data: List[Dict], position: Optional[str] = None, colors: Optional[List[str]] = None) -> dict:
    """Draw a bar chart.

    Args:
        data (List[Dict]): Chart data.
        position (Optional[str]): Position.
        colors (Optional[List[str]]): Bar colors.

    Returns:
        dict: API response for graph_bar.
    """
    return _post("/canvas/graph_bar", _inject_canvas({
        "data": data, "position": position, "colors": colors
    }))

def canvas_graph_line(data: List[Dict], axis_config: Optional[Dict] = None, color: Optional[str] = None) -> dict:
    """Draw a line graph.

    Args:
        data (List[Dict]): Data points.
        axis_config (Optional[Dict]): Axis options.
        color (Optional[str]): Line color.

    Returns:
        dict: API response for graph_line.
    """
    return _post("/canvas/graph_line", _inject_canvas({
        "data": data, "axis_config": axis_config, "color": color
    }))

def canvas_graph_pie(data: List[Dict], center_x: int, center_y: int, radius: int) -> dict:
    """Draw a pie chart.

    Args:
        data (List[Dict]): Pie slices.
        center_x (int): Center X.
        center_y (int): Center Y.
        radius (int): Radius.

    Returns:
        dict: API response for graph_pie.
    """
    return _post("/canvas/graph_pie", _inject_canvas({
        "data": data, "center_x": center_x, "center_y": center_y, "radius": radius
    }))

def canvas_graph_scatter(points: List[Tuple[float, float]], color: Optional[str] = None, axis_config: Optional[Dict] = None) -> dict:
    """Draw a scatter plot.

    Args:
        points (List[Tuple]): Data points.
        color (Optional[str]): Dot color.
        axis_config (Optional[Dict]): Axes.

    Returns:
        dict: API response for graph_scatter.
    """
    return _post("/canvas/graph_scatter", _inject_canvas({
        "points": points, "color": color, "axis_config": axis_config
    }))

def canvas_graph_histogram(values: List[float], bins: Optional[int] = None, normalize: Optional[bool] = None) -> dict:
    """Draw a histogram.

    Args:
        values (List[float]): Input data.
        bins (Optional[int]): Bin count.
        normalize (Optional[bool]): Normalize data.

    Returns:
        dict: API response for graph_histogram.
    """
    return _post("/canvas/graph_histogram", _inject_canvas({
        "values": values, "bins": bins, "normalize": normalize
    }))

def canvas_graph_heatmap(matrix: List[List[float]], labels: Optional[List[str]] = None, color_map: Optional[str] = None) -> dict:
    """Draw a heatmap.

    Args:
        matrix (List[List[float]]): Data grid.
        labels (Optional[List[str]]): Axis labels.
        color_map (Optional[str]): Colormap.

    Returns:
        dict: API response for graph_heatmap.
    """
    return _post("/canvas/graph_heatmap", _inject_canvas({
        "matrix": matrix, "labels": labels, "color_map": color_map
    }))
