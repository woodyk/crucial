#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: server.py
# Description: Crucial API server for handling canvas actions and MCP registry,
#              including frontend static hosting
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-06 22:06:22

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import json

from crucial.registry import get_registry
from crucial.dispatcher import Dispatcher
from crucial.db import get_db_connection
from crucial.canvas import Canvas
from crucial.auth import require_api_key_header
from crucial.config import CONFIG

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
        raise HTTPException(status_code=400, detail="Missing 'action' field")

    try:
        result = dispatcher.dispatch(action, params)
        return JSONResponse(content={"status": "ok", "result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/canvas/create")
async def create_canvas(request: Request, payload: dict):
    require_api_key_header(request.headers)
    require_api_key(request)

    name = payload.get("name", "Untitled")
    width = payload.get("x", 800)
    height = payload.get("y", 600)
    color = payload.get("color", "#000000")

    canvas = Canvas(name, width, height, color)
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
        raise HTTPException(status_code=404, detail="Canvas not found")
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
            raise HTTPException(status_code=403, detail="Invalid API key")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="API key store not found")

# ---------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import asyncio
    from uvicorn import Config, Server

    config = Config("crucial.server:app", host="0.0.0.0", port=8000, reload=True)
    server = Server(config)

    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("Shutdown signal received. Cleaning up Crucial server.")

