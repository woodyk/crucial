# File: server.py
# Description: Crucial API server for handling canvas actions and MCP registry
# Author: Ms. White
# Created: 2025-05-06

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import json

from crucial.registry import get_registry
from crucial.dispatcher import dispatch
from crucial.db import get_db_connection

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schema")

app = FastAPI(title="Crucial API", version="0.1.0")

@app.get("/mcp/registry")
async def mcp_registry():
    """
    Return full MCP tool registry derived from schema/ directory.
    """
    return get_registry()

@app.get("/schema/{tool_name}.json")
async def get_schema(tool_name: str):
    """
    Return raw JSON schema for a given tool name.
    """
    filename = os.path.join(SCHEMA_DIR, f"{tool_name}.json")
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Schema not found")
    with open(filename, "r") as f:
        return json.load(f)

@app.post("/canvas")
async def canvas_action(request: Request, payload: dict):
    require_api_key_header(request.headers)
    require_api_key(request)
    """
    General endpoint for canvas actions. Uses 'action' key to dispatch.
    """
    action = payload.get("action")
    if not action:
        raise HTTPException(status_code=400, detail="Missing 'action' field")
    
    try:
        # Optional schema validation using Canvas
        from crucial.canvas import Canvas
from crucial.auth import require_api_key_header

from crucial.config import CONFIG

def require_api_key(request: Request):
    if not CONFIG["AUTH"]["require_api_key"]:
        return
    key = request.headers.get("x-api-key")
    try:
        with open(CONFIG["AUTH"]["keys_file"], "r") as f:
            valid_keys = set(json.load(f))
        if key not in valid_keys:
            raise HTTPException(status_code=403, detail="Invalid API key")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="API key store not found")


from crucial.canvas import Canvas
from crucial.auth import require_api_key_header

from crucial.config import CONFIG

def require_api_key(request: Request):
    if not CONFIG["AUTH"]["require_api_key"]:
        return
    key = request.headers.get("x-api-key")
    try:
        with open(CONFIG["AUTH"]["keys_file"], "r") as f:
            valid_keys = set(json.load(f))
        if key not in valid_keys:
            raise HTTPException(status_code=403, detail="Invalid API key")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="API key store not found")


@app.post("/canvas/create")
async def create_canvas(request: Request, payload: dict):
    require_api_key_header(request.headers)
    require_api_key(request)
    """
    Create a new canvas session.
    """
    name = payload.get("name", "Untitled")
    width = payload.get("x", 800)
    height = payload.get("y", 600)
    color = payload.get("color", "#000000")

    canvas = Canvas(name, width, height, color)
    
    return {"status": "created", "canvas_id": canvas.id, "metadata": canvas.to_metadata()}

@app.get("/object/{canvas_id}")
async def get_canvas_metadata(canvas_id: str):
    """
    Return metadata for a canvas by ID.
    """
    canvas = Canvas(canvas_id)
    if not canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")
    return canvas.to_metadata()

@app.get("/object/{canvas_id}/history")
async def get_canvas_history(canvas_id: str):
    """
    Return full list of actions for a canvas.
    """
    canvas = Canvas(canvas_id)
    if not canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")
    return canvas.get_history()

@app.post("/object/{canvas_id}/load")
async def load_canvas_log(request: Request, canvas_id: str, payload: dict):
    require_api_key_header(request.headers)
    require_api_key(request)
    """
    Load canvas history into a session (replay).
    """
    canvas = Canvas(canvas_id)
    if not canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")

    history = payload.get("history")
    if not isinstance(history, list):
        raise HTTPException(status_code=400, detail="Missing or invalid 'history' array")

    canvas.load_from_log(history)
    return {"status": "loaded", "canvas_id": canvas_id, "actions_loaded": len(history)}

        dummy_canvas = Canvas("validate", 1, 1, "#000000")
        dummy_canvas.validate_params(action, payload)

        result = dispatch(action, payload)
        return JSONResponse(content={"status": "ok", "result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
