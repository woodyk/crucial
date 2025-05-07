#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: canvas.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-06 17:30:59
# Modified: 2025-05-06 22:29:23
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: canvas.py
# Description: Crucial Canvas class with DB-integrated action logging
# Author: Ms. White
# Updated: 2025-05-07

import json
import uuid
from datetime import datetime
from crucial.config import CONFIG
from crucial.db import get_db_connection
from crucial.utils.human_id import generate_human_id

class Canvas:
    def __init__(self, name, width, height, bg_color):
        self.id = str(uuid.uuid4())
        self.name = name
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.created_at = datetime.utcnow().isoformat()
        self._init_db()

    def _init_db(self):
        conn = get_db_connection()
        cur = conn.cursor()
        self.human_id = generate_human_id()
        cur.execute(
            "INSERT INTO canvases (id, human_id, name, width, height, background, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.id, self.human_id, self.name, self.width, self.height, self.bg_color, self.created_at)
        )
        conn.commit()

    def _store_action(self, action_type, parameters, overwrite=False):
        conn = get_db_connection()
        cur = conn.cursor()
        if overwrite:
            cur.execute("DELETE FROM actions WHERE canvas_id = ?", (self.id,))
        timestamp = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO actions (canvas_id, timestamp, action, params) VALUES (?, ?, ?, ?)",
            (self.id, timestamp, action_type, json.dumps(parameters))
        )
        conn.commit()


    def _mark_type(self, type_name):
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if 'canvas_type' column already exists
        cur.execute("PRAGMA table_info(canvases)")
        columns = {row[1] for row in cur.fetchall()}
        if "canvas_type" not in columns:
            cur.execute("ALTER TABLE canvases ADD COLUMN canvas_type TEXT")

        cur.execute("UPDATE canvases SET canvas_type = ? WHERE id = ?", (type_name, self.id))
        conn.commit()


    # Core drawing methods
    def clear(self, object_uri):
        self._store_action("canvas_clear", {"object_uri": object_uri})

    def draw_line(self, **kwargs):
        self._store_action("canvas_draw_line", kwargs)

    def draw_circle(self, **kwargs):
        self._store_action("canvas_draw_circle", kwargs)

    def draw_rectangle(self, **kwargs):
        self._store_action("canvas_draw_rectangle", kwargs)

    def draw_text(self, **kwargs):
        self._store_action("canvas_draw_text", kwargs)

    def draw_arc(self, **kwargs):
        self._store_action("canvas_draw_arc", kwargs)

    def draw_bezier(self, **kwargs):
        self._store_action("canvas_draw_bezier", kwargs)

    def draw_polygon(self, **kwargs):
        self._store_action("canvas_draw_polygon", kwargs)

    def draw_point(self, **kwargs):
        self._store_action("canvas_draw_point", kwargs)

    def rotate(self, **kwargs):
        self._store_action("canvas_rotate", kwargs)

    def scale(self, **kwargs):
        self._store_action("canvas_scale", kwargs)

    def translate(self, **kwargs):
        self._store_action("canvas_translate", kwargs)

    def save(self, **kwargs):
        self._store_action("canvas_save", kwargs)

    def set_background(self, **kwargs):
        self._store_action("canvas_set_background", kwargs)

    # Graphing methods
    def graph_bar(self, **kwargs):
        self._store_action("canvas_graph_bar", kwargs)

    def graph_line(self, **kwargs):
        self._store_action("canvas_graph_line", kwargs)

    def graph_pie(self, **kwargs):
        self._store_action("canvas_graph_pie", kwargs)

    def graph_scatter(self, **kwargs):
        self._store_action("canvas_graph_scatter", kwargs)

    def graph_histogram(self, **kwargs):
        self._store_action("canvas_graph_histogram", kwargs)

    def graph_heatmap(self, **kwargs):
        self._store_action("canvas_graph_heatmap", kwargs)


    @staticmethod
    def render_threejs(object_uri, script):
        """
        Render ThreeJS into a canvas. Accepts either UUID or human_id.
        """
        canvas = Canvas.from_id(object_uri)
        if not canvas:
            raise ValueError(f"Canvas not found: {object_uri}")
        canvas._mark_type("threejs")
        canvas._store_action("canvas_render_threejs", {
            "object_uri": canvas.id,  # Always store resolved UUID
            "script": script
        }, overwrite=True)


    @staticmethod
    def resolve_id(identifier: str) -> str:
        """
        Attempts to resolve a human-readable canvas ID to a full UUID.
        If not found, assumes identifier is already a UUID.
        """
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM canvases WHERE human_id = ?", (identifier,))
        row = cur.fetchone()
        if row:
            return row["id"]
        return identifier


    @staticmethod
    def from_id(canvas_id: str):
        """
        Loads a Canvas object from DB using either UUID or human-readable ID.
        """
        resolved_id = Canvas.resolve_id(canvas_id)
        cur = get_db_connection().cursor()
        cur.execute("SELECT * FROM canvases WHERE id = ?", (resolved_id,))
        row = cur.fetchone()
        if not row:
            return None
        canvas = Canvas.__new__(Canvas)  # Bypass __init__
        canvas.id = row["id"]
        canvas.human_id = row["human_id"]
        canvas.name = row["name"]
        canvas.width = row["width"]
        canvas.height = row["height"]
        canvas.bg_color = row["background"]
        canvas.created_at = row["created_at"]
        return canvas

