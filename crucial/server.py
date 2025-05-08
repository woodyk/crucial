#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: server.py
# Description: Crucial API server for handling canvas actions and MCP registry,
#              including frontend static hosting
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-08 17:29:09

import os
import json
import uvicorn

from io import BytesIO
from PIL import Image, ImageDraw

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles

from crucial.registry import get_registry
from crucial.dispatcher import Dispatcher
from crucial.db import get_db_connection
from crucial.canvas import Canvas
from crucial.auth import require_api_key_header
from crucial.config import CONFIG, get_logger

logger = get_logger(__name__)

dispatcher = Dispatcher()
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schema")
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

app = FastAPI(title="Crucial API", version="0.1.0")

# ---------------------------------------------------------------------
# Serve static frontend files
# ---------------------------------------------------------------------

# Serve index.html at root
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# ---------------------------------------------------------------------
# MCP Registry & Schema Metadata
# ---------------------------------------------------------------------

@app.get("/mcp/registry")
async def mcp_registry():
    return get_registry()

@app.get("/schema/{tool_name}.json")
async def get_schema(tool_name: str):
    filename = os.path.join(SCHEMA_DIR, f"{tool_name}.json")
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Schema not found")
    with open(filename, "r") as f:
        return json.load(f)

# ---------------------------------------------------------------------
# Canvas API Endpoints
# ---------------------------------------------------------------------
@app.post("/canvas")
async def canvas_action(request: Request, payload: dict):
    require_api_key_header(request.headers)
    require_api_key(request)

    action = payload.get("action")
    params = payload.get("params", {})
    if not action:
        logger.warning("Canvas action missing 'action' field")
        raise HTTPException(status_code=400, detail="Missing 'action' field")

    try:
        result = dispatcher.dispatch(action, params)
        logger.info("Executed canvas action: %s", action)
        return JSONResponse(content={"status": "ok", "result": result})
    except HTTPException as e:
        logger.warning("[Canvas API] %s (HTTP %s)", e.detail, e.status_code)
        raise
    except Exception as e:
        logger.exception("Canvas dispatch error for action: %s", action)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/canvas")
async def serve_canvas_query(id: str = Query(None)):
    if not id:
        raise HTTPException(status_code=400, detail="Missing canvas id")
    resolved_id = Canvas.resolve_id(id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM canvases WHERE id = ? OR human_id = ?", (resolved_id, resolved_id))
    if not cur.fetchone():
        logger.warning("Viewer load failed: canvas %s not found", id)
        raise HTTPException(status_code=404, detail="Canvas not found")
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/canvas/{canvas_id}")
async def serve_canvas_view(canvas_id: str):
    resolved_id = Canvas.resolve_id(canvas_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM canvases WHERE id = ? OR human_id = ?", (resolved_id, resolved_id))
    if not cur.fetchone():
        logger.warning("Viewer load failed: canvas %s not found", canvas_id)
        raise HTTPException(status_code=404, detail="Canvas not found")
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.post("/canvas/create")
async def create_canvas(request: Request, payload: dict):
    require_api_key_header(request.headers)
    require_api_key(request)

    name = payload.get("name", "Untitled")
    width = payload.get("x", 800)
    height = payload.get("y", 600)
    color = payload.get("color", "#000000")

    canvas = Canvas(name, width, height, color)
    logger.info("Created new canvas: %s (%s) %s %sx%s", name, canvas.id, color, width, height)
    return {
        "status": "created",
        "canvas_id": canvas.id,
        "human_id": canvas.human_id,
        "metadata": canvas.__dict__
    }

@app.get("/object/{canvas_id}")
async def get_canvas_metadata(canvas_id: str):
    resolved_id = Canvas.resolve_id(canvas_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM canvases WHERE id = ?", (resolved_id,))
    row = cur.fetchone()
    if not row:
        logger.warning("Metadata fetch failed: canvas %s not found", resolved_id)
        raise HTTPException(status_code=404, detail="Canvas not found")
    logger.debug("Fetched metadata for canvas %s", resolved_id)
    return dict(row)



@app.get("/object/{canvas_id}/history")
async def get_canvas_history(canvas_id: str):
    resolved_id = Canvas.resolve_id(canvas_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp, action, params FROM actions WHERE canvas_id = ? ORDER BY timestamp ASC",
        (resolved_id,)
    )
    rows = []
    for row in cur.fetchall():
        action = dict(row)
        try:
            action["params"] = json.loads(action["params"])
        except Exception:
            action["params"] = {}
        rows.append(action)
    return rows


@app.post("/object/{canvas_id}/load")
async def load_canvas_log(request: Request, canvas_id: str, payload: dict):
    require_api_key_header(request.headers)
    require_api_key(request)

    resolved_id = Canvas.resolve_id(canvas_id)
    history = payload.get("history")
    if not isinstance(history, list):
        raise HTTPException(status_code=400, detail="Missing or invalid 'history' array")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM actions WHERE canvas_id = ?", (resolved_id,))
    for entry in history:
        cur.execute(
            "INSERT INTO actions (canvas_id, timestamp, action, params) VALUES (?, ?, ?, ?)",
            (resolved_id, entry["timestamp"], entry["action"], json.dumps(entry["params"]))
        )
    conn.commit()
    return {"status": "loaded", "canvas_id": resolved_id, "actions_loaded": len(history)}



# ---------------------------------------------------------------------
# API Key Validation
# ---------------------------------------------------------------------
def require_api_key(request: Request):
    if not CONFIG["AUTH"].get("require_api_key", True):
        return
    key = request.headers.get("x-api-key")
    try:
        with open(CONFIG["AUTH"]["keys_file"], "r") as f:
            valid_keys = set(json.load(f))
        if key not in valid_keys:
            logger.warning("Rejected request with invalid API key: %s", key)
            raise HTTPException(status_code=403, detail="Invalid API key")
    except FileNotFoundError:
        logger.error("API key file not found at %s", CONFIG["AUTH"]["keys_file"])
        raise HTTPException(status_code=500, detail="API key store not found")


# ---------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import asyncio
    from uvicorn import Config, Server

    logger.info("Starting Crucial API server...")
    config = Config("crucial.server:app", host="0.0.0.0", port=8000, reload=True)
    server = Server(config)

    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        logger.info("Shutdown signal received. Cleaning up Crucial server.")

