#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: canvas.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-07 12:15:35
# Modified: 2025-05-07 13:28:37
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: canvas.py
# Description: Crucial Canvas class with DB-integrated action logging
# Author: Ms. White
# Updated: 2025-05-07

import json
import uuid
import sys
from datetime import datetime
from crucial.config import CONFIG, get_logger
from crucial.db import get_db_connection
from crucial.utils.human_id import generate_human_id

logger = get_logger(__name__)

class Canvas:
    def __init__(self, name, width, height, bg_color):
        self.id = str(uuid.uuid4())
        self.name = name
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.created_at = datetime.utcnow().isoformat()
        self._init_db()
        logger.info("Initialized canvas '%s' (%s) %dx%d bg=%s",
                    self.name, self.id, self.width, self.height, self.bg_color)

    def _init_db(self):
        conn = get_db_connection()
        cur = conn.cursor()
        self.human_id = generate_human_id()
        cur.execute(
            "INSERT INTO canvases (id, human_id, name, width, height, background, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.id, self.human_id, self.name, self.width, self.height, self.bg_color, self.created_at)
        )
        conn.commit()
        logger.debug("Canvas DB entry created: %s", self.id)

    def _store_action(self, action_type, parameters, overwrite=False):
        logger.info("Canvas[%s] action: %s(%s)", self.id, action_type, parameters)
        conn = get_db_connection()
        cur = conn.cursor()
        if overwrite:
            cur.execute("DELETE FROM actions WHERE canvas_id = ?", (self.id,))
            logger.debug("Canvas[%s] previous actions cleared (overwrite=True)", self.id)
        timestamp = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO actions (canvas_id, timestamp, action, params) VALUES (?, ?, ?, ?)",
            (self.id, timestamp, action_type, json.dumps(parameters))
        )
        conn.commit()
        logger.debug("Canvas[%s] action logged: %s", self.id, action_type)

    def _mark_type(self, type_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(canvases)")
        columns = {row[1] for row in cur.fetchall()}
        if "canvas_type" not in columns:
            cur.execute("ALTER TABLE canvases ADD COLUMN canvas_type TEXT")
            logger.debug("Added 'canvas_type' column to canvases table")
        cur.execute("UPDATE canvases SET canvas_type = ? WHERE id = ?", (type_name, self.id))
        conn.commit()
        logger.info("Canvas[%s] type marked as: %s", self.id, type_name)

    # Core drawing methods
    def clear(self, canvas_id): self._store_action("canvas_clear", {"canvas_id": canvas_id})
    def draw_line(self, **kwargs): self._store_action("canvas_draw_line", kwargs)
    def draw_circle(self, **kwargs): self._store_action("canvas_draw_circle", kwargs)
    def draw_rectangle(self, **kwargs): self._store_action("canvas_draw_rectangle", kwargs)
    def draw_text(self, **kwargs): self._store_action("canvas_draw_text", kwargs)
    def draw_arc(self, **kwargs): self._store_action("canvas_draw_arc", kwargs)
    def draw_bezier(self, **kwargs): self._store_action("canvas_draw_bezier", kwargs)
    def draw_polygon(self, **kwargs): self._store_action("canvas_draw_polygon", kwargs)
    def draw_point(self, **kwargs): self._store_action("canvas_draw_point", kwargs)

    # Canvas transforms
    def rotate(self, **kwargs): self._store_action("canvas_rotate", kwargs)
    def scale(self, **kwargs): self._store_action("canvas_scale", kwargs)
    def translate(self, **kwargs): self._store_action("canvas_translate", kwargs)
    def save(self, **kwargs): self._store_action("canvas_save", kwargs)
    def set_background(self, **kwargs): self._store_action("canvas_set_background", kwargs)

    # Graphing methods
    def graph_bar(self, **kwargs): self._store_action("canvas_graph_bar", kwargs)
    def graph_line(self, **kwargs): self._store_action("canvas_graph_line", kwargs)
    def graph_pie(self, **kwargs): self._store_action("canvas_graph_pie", kwargs)
    def graph_scatter(self, **kwargs): self._store_action("canvas_graph_scatter", kwargs)
    def graph_histogram(self, **kwargs): self._store_action("canvas_graph_histogram", kwargs)
    def graph_heatmap(self, **kwargs): self._store_action("canvas_graph_heatmap", kwargs)

    @staticmethod
    def create(name: str, width: int, height: int, bg_color: str):
        """
        Factory method to create and persist a new Canvas instance.

        Args:
            name (str): Human-readable name for the canvas.
            width (int): Width in pixels.
            height (int): Height in pixels.
            bg_color (str): Background color in hex.

        Returns:
            Canvas: A fully initialized Canvas object saved to DB.
        """
        canvas = Canvas(name, width, height, bg_color)
        return canvas


    @staticmethod
    def render_threejs(canvas_id, script):
        canvas = Canvas.from_id(canvas_id)
        if not canvas:
            logger.error("Canvas not found for render_threejs: %s", canvas_id)
            raise ValueError(f"Canvas not found: {canvas_id}")
        canvas._mark_type("threejs")
        canvas._store_action("canvas_render_threejs", {
            "canvas_id": canvas.id,
            "script": script
        }, overwrite=True)
        logger.info("Canvas[%s] rendered via ThreeJS", canvas.id)

    @staticmethod
    def resolve_id(identifier: str) -> str:
        """
        Resolve either a canvas UUID or a human ID to an internal canvas ID.
        """
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM canvases WHERE human_id = ?", (identifier,))
        row = cur.fetchone()
        if row:
            logger.debug("Resolved human_id %s → %s", identifier, row["id"])
            return row["id"]
        logger.debug("Assuming %s is UUID", identifier)
        return identifier

    @staticmethod
    def from_id(canvas_id: str):
        resolved_id = Canvas.resolve_id(canvas_id)
        cur = get_db_connection().cursor()
        cur.execute("SELECT * FROM canvases WHERE id = ?", (resolved_id,))
        row = cur.fetchone()
        if not row:
            logger.warning("Canvas not found for ID: %s", canvas_id)
            return None
        canvas = Canvas.__new__(Canvas)
        canvas.id = row["id"]
        canvas.human_id = row["human_id"]
        canvas.name = row["name"]
        canvas.width = row["width"]
        canvas.height = row["height"]
        canvas.bg_color = row["background"]
        canvas.created_at = row["created_at"]
        logger.debug("Canvas object loaded: %s (%s)", canvas.name, canvas.id)
        return canvas

