# File: canvas.py
# Description: Crucial Canvas class – core rendering and state management
# Author: Ms. White
# Created: 2025-05-06

import uuid
from crucial.config import CONFIG
from crucial.db import get_db_connection

from datetime import datetime

class Canvas:
    """
    Core engine class representing a single Crucial canvas.
    Maintains draw state, action log, and rendering parameters.
    """

    def __init__(self, name, width, height, bg_color):
        """
        Initialize a new canvas instance.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.created_at = datetime.utcnow().isoformat()
        self.actions = []

    def to_metadata(self):
        """
        Return dictionary representation of canvas metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "bg_color": self.bg_color,
            "created_at": self.created_at
        }

    def log_action(self, action_type, parameters):
        """
        Append an action to the canvas history.
        """
        self.actions.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action_type,
            "params": parameters
        })

    def get_history(self):
        from json import loads
        """
        Return full list of actions for replay or export.
        """
        return self.actions

    def clear(self):
        """
        Clear all drawn elements from the canvas (resets actions).
        """
        self.actions.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "clear",
            "params": {}
        })

    def draw_line(self, start_x, start_y, end_x, end_y, color, width):
        """
        Draw a straight line on the canvas.
        """
        self.log_action("draw_line", {
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "color": color,
            "width": width
        })

    def draw_circle(self, center_x, center_y, radius, color, fill):
        """
        Draw a circle at the given center point.
        """
        self.log_action("draw_circle", {
            "center_x": center_x,
            "center_y": center_y,
            "radius": radius,
            "color": color,
            "fill": fill
        })

    def draw_rectangle(self, x, y, width, height, color, fill):
        """
        Draw a rectangle or square.
        """
        self.log_action("draw_rectangle", {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "color": color,
            "fill": fill
        })

    def draw_text(self, text, x, y, font, size, color):
        """
        Render text at a given position.
        """
        self.log_action("draw_text", {
            "text": text,
            "x": x,
            "y": y,
            "font": font,
            "size": size,
            "color": color
        })

    def draw_arc(self, center_x, center_y, radius, start_angle, end_angle, color, width):
        """
        Draw an arc segment of a circle.
        """
        self.log_action("draw_arc", {
            "center_x": center_x,
            "center_y": center_y,
            "radius": radius,
            "start_angle": start_angle,
            "end_angle": end_angle,
            "color": color,
            "width": width
        })

    def draw_bezier(self, control_points, color, width):
        """
        Draw a Bezier curve using control points.
        """
        self.log_action("draw_bezier", {
            "control_points": control_points,
            "color": color,
            "width": width
        })

    def draw_polygon(self, points, color, fill):
        """
        Draw a closed polygon with given vertices.
        """
        self.log_action("draw_polygon", {
            "points": points,
            "color": color,
            "fill": fill
        })

    def draw_point(self, x, y, color, radius):
        """
        Plot a point (or small circle) on the canvas.
        """
        self.log_action("draw_point", {
            "x": x,
            "y": y,
            "color": color,
            "radius": radius
        })

    def set_background(self, color):
        """
        Change the background color of the canvas.
        """
        self.bg_color = color
        self.log_action("set_background", {
            "color": color
        })

    def translate(self, dx, dy):
        """
        Translate the canvas coordinate space.
        """
        self.log_action("translate", {
            "dx": dx,
            "dy": dy
        })

    def rotate(self, angle_in_degrees):
        """
        Rotate the canvas coordinate space.
        """
        self.log_action("rotate", {
            "angle_in_degrees": angle_in_degrees
        })

    def scale(self, scale_x, scale_y):
        """
        Scale the canvas coordinate space.
        """
        self.log_action("scale", {
            "scale_x": scale_x,
            "scale_y": scale_y
        })

    def render_threejs(self, script):
        """
        Push a raw Three.js script to the canvas.
        """
        self.log_action("render_threejs", {
            "script": script
        })

    def save(self, file_path, format):
        """
        Save the canvas to a file.
        """
        self.log_action("save", {
            "file_path": file_path,
            "format": format
        })

    def graph_bar(self, data, position=None, colors=None):
        """
        Draw a bar chart on the canvas.

        Parameters:
            data (List[Dict]): List of {label: str, value: float} entries.
            position (str): Optional position setting.
            colors (List[str]): Optional list of hex colors.
        """
        self.log_action("graph_bar", {
            "data": data,
            "position": position,
            "colors": colors
        })

    def graph_line(self, data, axis_config=None, color=None):
        """
        Draw a line graph on the canvas.

        Parameters:
            data (List[Dict]): List of {x: float, y: float} points.
            axis_config (Dict): Optional axis configuration.
            color (str): Line color.
        """
        self.log_action("graph_line", {
            "data": data,
            "axis_config": axis_config,
            "color": color
        })

    def graph_pie(self, data, center_x, center_y, radius):
        """
        Draw a pie chart on the canvas.

        Parameters:
            data (List[Dict]): List of {label: str, value: float}.
            center_x (int): X coordinate of center.
            center_y (int): Y coordinate of center.
            radius (int): Radius of the pie chart.
        """
        self.log_action("graph_pie", {
            "data": data,
            "center_x": center_x,
            "center_y": center_y,
            "radius": radius
        })

    def graph_scatter(self, points, color=None, axis_config=None):
        """
        Draw a scatter plot on the canvas.

        Parameters:
            points (List[Tuple[float, float]]): Coordinates to plot.
            color (str): Optional color of points.
            axis_config (Dict): Optional axis configuration.
        """
        self.log_action("graph_scatter", {
            "points": points,
            "color": color,
            "axis_config": axis_config
        })

    def graph_histogram(self, values, bins=None, normalize=None):
        """
        Draw a histogram on the canvas.

        Parameters:
            values (List[float]): Data values.
            bins (int): Optional number of bins.
            normalize (bool): Whether to normalize frequencies.
        """
        self.log_action("graph_histogram", {
            "values": values,
            "bins": bins,
            "normalize": normalize
        })

    def graph_heatmap(self, matrix, labels=None, color_map=None):
        """
        Draw a heatmap from a 2D matrix.

        Parameters:
            matrix (List[List[float]]): 2D array of values.
            labels (List[str]): Optional axis labels.
            color_map (str): Optional color mapping preset.
        """
        self.log_action("graph_heatmap", {
            "matrix": matrix,
            "labels": labels,
            "color_map": color_map
        })

    def load_from_log(self, actions):
        """
        Load canvas state from a list of recorded actions.
        
        This enables the canvas to be reconstructed from saved history.
        """
        for entry in actions:
            action_type = entry.get("action")
            params = entry.get("params", {})
            self.log_action(action_type, params)

    def invoke(self, action_type, params):
        """
        Generic method dispatcher. Calls a matching method on this canvas
        using the action name and parameter dictionary.

        Raises NotImplementedError if the method does not exist.
        """
        if hasattr(self, action_type):
            method = getattr(self, action_type)
            return method(**params)
        raise NotImplementedError(f"Action '{action_type}' not supported in Canvas.")

    def validate_params(self, action_type, params):
        """
        Validate parameters against the schema definition for the action.
        This is optional and can be toggled via environment variable.

        Returns True if valid, raises jsonschema.ValidationError if not.
        """
        import os
        if not os.getenv("CANVAS_VALIDATE", "").lower() == "true":
            return True  # No-op unless validation is enabled

        import json
        import jsonschema
        from pathlib import Path

        schema_path = Path(__file__).parent / "schema" / f"{action_type}.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema for {action_type} not found.")

        with open(schema_path, "r") as f:
            schema = json.load(f)

        jsonschema.validate(instance=params, schema=schema["parameters"])
        return True
