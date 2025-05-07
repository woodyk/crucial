#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: dispatcher.py
# Description: Crucial dispatcher for routing schema actions to canvas methods
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-07 13:27:54

import os
import json
from pathlib import Path
from importlib import import_module
from crucial.canvas import Canvas
from crucial.db import get_db_connection
from crucial.config import CONFIG, get_logger
from fastapi import HTTPException

logger = get_logger(__name__)


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
                logger.warning("Failed to load schema %s: %s", file.name, e)

        logger.info("Loaded %d canvas schemas", len(self.schemas))

    def get_schema(self, action):
        return self.schemas.get(action)

    def get_canvas(self, canvas_id):
        resolved_id = Canvas.resolve_id(canvas_id)
        cur = get_db_connection().cursor()
        cur.execute("SELECT * FROM canvases WHERE id = ?", (resolved_id,))
        row = cur.fetchone()
        if not row:
            logger.warning("Canvas not found: %s", canvas_id)
            raise HTTPException(status_code=404, detail=f"Canvas {canvas_id} not found.")
        canvas = Canvas.__new__(Canvas)
        canvas.id = row["id"]
        canvas.human_id = row["human_id"]
        canvas.name = row["name"]
        canvas.width = row["width"]
        canvas.height = row["height"]
        canvas.bg_color = row["background"]
        canvas.created_at = row["created_at"]
        logger.debug("Canvas resolved: %s (%s)", canvas.name, canvas.id)
        return canvas

    def dispatch(self, action, params):
        logger.debug("Dispatching action: %s with params: %s", action, params)

        if not action.startswith("canvas_"):
            logger.warning("Invalid action name (must start with canvas_): %s", action)
            raise HTTPException(status_code=400, detail="Invalid action name format")

        if action not in self.methods:
            logger.warning("Unknown canvas action: %s", action)
            raise HTTPException(status_code=404, detail=f"Unknown action: {action}")

        method_name = self.methods[action]

        if action == "canvas_create":
            logger.info("Dispatching canvas_create for: %s", params.get("name"))
            try:
                canvas = Canvas.create(
                    name=params["name"],
                    width=params["x"],
                    height=params["y"],
                    bg_color=params["color"]
                )
            except KeyError as e:
                logger.error("Missing canvas_create parameter: %s", str(e))
                raise HTTPException(status_code=422, detail=f"Missing parameter: {str(e)}")
            return {"canvas_id": canvas.id, "metadata": canvas.__dict__}

        if "canvas_id" not in params:
            logger.warning("Missing canvas_id in params for action: %s", action)
            raise HTTPException(status_code=400, detail="Missing canvas_id in parameters")

        canvas = self.get_canvas(params["canvas_id"])

        if action == "canvas_render_threejs":
            try:
                return Canvas.render_threejs(params["canvas_id"], params["script"])
            except Exception as e:
                logger.exception("Error executing render_threejs: %s", e)
                raise HTTPException(status_code=422, detail=str(e))

        method = getattr(canvas, method_name, None)
        if not method:
            logger.error("Method not implemented: %s", method_name)
            raise HTTPException(status_code=404, detail=f"Method not implemented: {method_name}")

        try:
            result = method(**params)
            logger.info("Action executed: %s on canvas %s", action, canvas.id)
            return {"status": "ok", "canvas_id": canvas.id}
        except KeyError as e:
            logger.error("Missing parameter for %s: %s", action, str(e))
            raise HTTPException(status_code=422, detail=f"Missing parameter: {str(e)}")
        except Exception as e:
            logger.exception("Unhandled error in action %s on canvas %s", action, canvas.id)
            raise HTTPException(status_code=500, detail="Internal server error")

