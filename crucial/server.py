#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: server.py
# Description: Crucial API server for handling canvas actions and MCP registry,
#              including frontend static hosting
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-08 20:16:13

import os
import json
import uvicorn

from io import BytesIO
from collections import defaultdict

from fastapi import(
    FastAPI,
    Request,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect
)
from fastapi.responses import (
    JSONResponse,
    FileResponse,
    StreamingResponse,
    Response, 
    HTMLResponse
)
from fastapi.staticfiles import StaticFiles

from crucial.registry import get_registry
from crucial.dispatcher import Dispatcher
from crucial.db import get_db_connection
from crucial.canvas import Canvas, set_canvas_subscribers
from crucial.auth import require_api_key_header
from crucial.config import CONFIG, get_logger
from crucial.loader import crucial_python_loader

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

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)  # No Content

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

@app.post("/canvas/{canvas_id}/{action}")
async def post_canvas_action_uri(request: Request, canvas_id: str, action: str, payload: dict):
    """
    Handle POST to /canvas/{canvas_id}/{action} with JSON body as params.
    Routes through the same dispatcher logic.
    """
    require_api_key_header(request.headers)
    require_api_key(request)

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    payload["canvas_id"] = canvas_id
    try:
        result = dispatcher.dispatch(action, payload)
        return JSONResponse(content={"status": "ok", "result": result})
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Dispatch failed")
        raise HTTPException(status_code=500, detail="Dispatch failure")

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
# WebSockets 
# ---------------------------------------------------------------------
# Keep track of canvas_id → set of connected WebSockets
canvas_subscribers = defaultdict(set)
set_canvas_subscribers(canvas_subscribers)

@app.websocket("/ws/canvas/{canvas_id}")
async def websocket_canvas_updates(websocket: WebSocket, canvas_id: str):
    await websocket.accept()
    canvas_subscribers[canvas_id].add(websocket)
    logger.info("WebSocket connected: canvas %s", canvas_id)

    try:
        while True:
            await websocket.receive_text()  # Optional ping from client
    except WebSocketDisconnect:
        canvas_subscribers[canvas_id].remove(websocket)
        logger.info("WebSocket disconnected: canvas %s", canvas_id)

# ---------------------------------------------------------------------
# Help 
# ---------------------------------------------------------------------
@app.get("/help", response_class=HTMLResponse)
async def help_index():
    """
    List all available canvas functions with descriptions.
    """
    registry = get_registry()
    modules = sorted(registry.get("modules", []), key=lambda m: m["name"])
    body = "<h1>Crucial API Help</h1><ul>"
    for mod in modules:
        name = mod["name"]
        desc = mod.get("description", "")
        body += f'<li><a href="/help/{name}"><code>{name}</code></a> — {desc}</li>'
    body += "</ul>"
    return HTMLResponse(content=body)


@app.get("/help/{action}", response_class=HTMLResponse)
async def help_action(action: str):
    """
    Show detailed help for a specific action.
    """
    from crucial.registry import load_all_schemas

    schemas = load_all_schemas()
    schema = schemas.get(action)

    if not schema:
        raise HTTPException(status_code=404, detail="Unknown tool/action")

    desc = schema.get("description", "")
    props = schema.get("parameters", {}).get("properties", {})
    required = schema.get("parameters", {}).get("required", [])

    html = f"<h1><code>{action}</code></h1><p>{desc}</p><h3>Parameters:</h3><ul>"
    for k, v in props.items():
        t = v.get("type", "any")
        d = v.get("description", "")
        is_required = " (required)" if k in required else ""
        html += f"<li><code>{k}</code>: <em>{t}</em>{is_required}<br>{d}</li>"
    html += "</ul>"

    example_json = {
        "action": action,
        "params": {k: f"<{t}>" for k, t in props.items()}
    }
    html += "<h3>Sample POST to /canvas</h3><pre>" + json.dumps(example_json, indent=2) + "</pre>"

    return HTMLResponse(content=html)

# ---------------------------------------------------------------------
# Python Module Autoloader
# ---------------------------------------------------------------------
@app.get("/python")
async def serve_dynamic_python_loader(request: Request):
    host = str(request.base_url).rstrip("/")
    return crucial_python_loader(base_url=host)

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


