#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: canvas.py
# Author: Ms. White
# Description: Crucial Canvas class with DB-integrated action logging and WebSocket broadcasts
# Created: 2025-05-07
# Modified: 2025-05-09 23:48:49

import os
import json
import uuid
import asyncio
from datetime import datetime
from crucial.config import CONFIG, get_logger
from crucial.db import get_db_connection
from crucial.utils.human_id import generate_human_id

# External reference (injected at runtime in server.py)
# canvas_subscribers = {}  # populated via FastAPI WebSocket route

logger = get_logger(__name__)

class Canvas:
    def __init__(self, name, width, height, bg_color):
        self.id = str(uuid.uuid4())
        self.name = name
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
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

        # WebSocket broadcast (if enabled and active)
        asyncio.create_task(self._broadcast(action_type, parameters, timestamp))

    async def _broadcast(self, action, params, timestamp):
        message = json.dumps({
            "action": action,
            "params": params,
            "timestamp": timestamp
        })
        clients = list(canvas_subscribers.get(self.id, []))
        for ws in clients:
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.warning("WebSocket send failed: %s", e)

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

    # Drawing primitives
    def clear(self, canvas_id):
        self._store_action("clear", {"canvas_id": canvas_id})  # Optional trace
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM actions WHERE canvas_id = ?", (canvas_id,))
        conn.commit()
        logger.info("Canvas[%s] actions purged after clear marker", canvas_id)

    def draw_line(self, **kwargs): self._store_action("draw_line", kwargs)
    def draw_circle(self, **kwargs): self._store_action("draw_circle", kwargs)
    def draw_rectangle(self, **kwargs): self._store_action("draw_rectangle", kwargs)
    def draw_text(self, **kwargs): self._store_action("draw_text", kwargs)
    def draw_arc(self, **kwargs): self._store_action("draw_arc", kwargs)
    def draw_bezier(self, **kwargs): self._store_action("draw_bezier", kwargs)
    def draw_polygon(self, **kwargs): self._store_action("draw_polygon", kwargs)
    def draw_point(self, **kwargs): self._store_action("draw_point", kwargs)
    def draw_gradient(self, **kwargs): self._store_action("draw_gradient", kwargs)
    def draw_path(self, **kwargs): self._store_action("draw_path", kwargs)
    def draw_spline(self, **kwargs): self._store_action("draw_spline", kwargs)
    def draw_turtle(self, **kwargs): self._store_action("draw_turtle", kwargs)
    def draw_raster(self, **kwargs): self._store_action("draw_raster", kwargs)

    # Transforms
    def rotate(self, **kwargs): self._store_action("rotate", kwargs)
    def scale(self, **kwargs): self._store_action("scale", kwargs)
    def translate(self, **kwargs): self._store_action("translate", kwargs)
    def set_background(self, **kwargs): self._store_action("set_background", kwargs)

    # Graphs
    def graph_bar(self, **kwargs): self._store_action("graph_bar", kwargs)
    def graph_line(self, **kwargs): self._store_action("graph_line", kwargs)
    def graph_pie(self, **kwargs): self._store_action("graph_pie", kwargs)
    def graph_scatter(self, **kwargs): self._store_action("graph_scatter", kwargs)
    def graph_histogram(self, **kwargs): self._store_action("graph_histogram", kwargs)
    def graph_heatmap(self, **kwargs): self._store_action("graph_heatmap", kwargs)
    def graph_area(self, **kwargs): self._store_action("graph_area", kwargs)
    def graph_bubble(self, **kwargs): self._store_action("graph_bubble", kwargs)
    def graph_donut(self, **kwargs): self._store_action("graph_donut", kwargs)
    def graph_gauge(self, **kwargs): self._store_action("graph_gauge", kwargs)
    def graph_radar(self, **kwargs): self._store_action("graph_radar", kwargs)
    def graph_wordcloud(self, **kwargs): self._store_action("graph_wordcloud", kwargs)

    def load_actions(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT action, params FROM actions WHERE canvas_id = ? ORDER BY timestamp ASC",
            (self.id,)
        )
        self.actions = []
        for row in cur.fetchall():
            try:
                action = row["action"]
                params = json.loads(row["params"])
                self.actions.append({"action": action, "params": params})
            except Exception as e:
                logger.warning("Failed to decode action row: %s", e)

    @staticmethod
    def create(**kwargs):
        name = kwargs.get("name", "Untitled")
        width = kwargs.get("x", 800)
        height = kwargs.get("y", 600)
        color = kwargs.get("color", "#000000")
        canvas = Canvas(name, width, height, color)
        return {
            "status": "created",
            "canvas_id": canvas.id,
            "human_id": canvas.human_id,
            "metadata": canvas.__dict__
        }

        return Canvas(name, width, height, bg_color)

    @staticmethod
    def load(canvas_id: str) -> "Canvas":
        resolved_id = Canvas.resolve_id(canvas_id)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM canvases WHERE id = ?", (resolved_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Canvas {canvas_id} not found.")
        canvas = Canvas(
            name=row["name"],
            width=row["width"],
            height=row["height"],
            bg_color=row["background"]
        )
        canvas.id = row["id"]
        canvas.human_id = row["human_id"]
        return canvas

    @staticmethod
    def render_threejs(canvas, script):
        if not canvas:
            logger.error("Canvas not found for render_threejs")
            raise ValueError("Canvas is required")
        canvas._mark_type("threejs")
        canvas._store_action("render_threejs", {
            "canvas_id": canvas.id,
            "script": script
        }, overwrite=True)
        logger.info("Canvas[%s] rendered via ThreeJS", canvas.id)

    @staticmethod
    def resolve_id(identifier: str) -> str:
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

def set_canvas_subscribers(ref):
    global canvas_subscribers
    canvas_subscribers = ref

