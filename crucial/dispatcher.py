#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: dispatcher.py
# Description: Crucial dispatcher for routing schema actions to canvas methods
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-06 22:21:47

import os
import json
from pathlib import Path
from importlib import import_module
from crucial.canvas import Canvas
from crucial.db import get_db_connection
from crucial.config import CONFIG
from fastapi import HTTPException


class Dispatcher:
    """
    Resolves `canvas_*` actions based on loaded schemas and Canvas instance map.
    """

    def __init__(self):
        self.schemas = {}
        self.methods = {}
        self.load_schemas()

    def load_schemas(self):
        schema_dir = Path(__file__).parent / "schema"
        for file in schema_dir.glob("canvas_*.json"):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                name = data["name"]
                self.schemas[name] = data
                method_name = name.replace("canvas_", "")
                self.methods[name] = method_name
            except Exception as e:
                continue  # Log skipped schema if necessary

    def get_schema(self, action):
        return self.schemas.get(action)


    def get_canvas(self, object_uri):
        resolved_id = Canvas.resolve_id(object_uri)
        cur = get_db_connection().cursor()
        cur.execute("SELECT * FROM canvases WHERE id = ?", (resolved_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Canvas {object_uri} not found.")
        canvas = Canvas.__new__(Canvas)
        canvas.id = row["id"]
        canvas.human_id = row["human_id"]
        canvas.name = row["name"]
        canvas.width = row["width"]
        canvas.height = row["height"]
        canvas.bg_color = row["background"]
        canvas.created_at = row["created_at"]
        return canvas

    def dispatch(self, action, params):
        if action not in self.methods:
            raise HTTPException(status_code=404, detail=f"Unknown action: {action}")

        method_name = self.methods[action]

        # Handle canvas creation
        if action == "canvas_create":
            canvas = Canvas(
                name=params["name"],
                width=params["x"],
                height=params["y"],
                bg_color=params["color"]
            )
            return {"canvas_id": canvas.id, "metadata": canvas.__dict__}

        if "object_uri" not in params:
            raise HTTPException(status_code=400, detail="Missing canvas object_uri")

        canvas = self.get_canvas(params["object_uri"])

        # Special case for render_threejs (requires ordered args)
        if action == "canvas_render_threejs":
            return Canvas.render_threejs(params["object_uri"], params["script"])

        method = getattr(canvas, method_name, None)
        if not method:
            raise HTTPException(status_code=500, detail=f"No method {method_name} in Canvas")

        result = method(**{k: v for k, v in params.items() if k != "object_uri"})
        return {"status": "ok", "canvas_id": canvas.id}

