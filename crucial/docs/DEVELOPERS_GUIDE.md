# Crucial Development Guide (Schema-Based Rendering Infrastructure)

This technical reference defines the architecture, configuration, and extension
model for the Crucial project. Crucial provides real-time, visually rendered
communication via a schema-first, config-managed drawing pipeline. It is designed
to work seamlessly with both human developers and LLMs, supporting function calling,
visual timelines, and progressive animation with clarity and modularity.

---------------------------------------------------------------------
## Project Directory Overview

```text
crucial/
├── __init__.py
├── auth.py                  # API key and authentication logic
├── canvas.py                # Canvas class (core state and methods)
├── config.py                # Reads environment + default settings
├── db.py                    # SQLAlchemy connection + schema management
├── dispatcher.py            # Schema-mapped method dispatcher (MCP bridge)
├── env.example              # Deployable config sample (.env template)
├── frontend/                # Web/Electron canvas interface
│   ├── app.js               # Action player, animation + rendering logic
│   ├── config.js            # Frontend config: brush speed, colors, effects
│   └── index.html           # Canvas viewer shell
├── registry.py              # Loads schema → server tool bindings
├── schema/                  # JSON schemas for all canvas tool calls
├── server.py                # FastAPI server: routes, auth, dispatch
├── sessions/                # Canvas-specific logs, metadata, and states
├── static/                  # Optional frontend static assets
└── tools/                   # Python handlers for each LLM canvas_* function
    └── canvas_draw_line.py  # Example: line tool function

---------------------------------------------------------------------
## Schema-Driven Architecture

Every supported LLM function call originates from a `crucial/schema/*.json` file.
These files:

- Define the **function name** and **parameter structure**
- Are automatically imported by `registry.py`
- Enable server-side and frontend behavior routing
- Serve as canonical metadata for LLM tool registration (MCP-compatible)

Example: `canvas_draw_circle.json`
```json
{
    "name": "canvas_draw_circle",
    "description": "Draw a circle on the canvas",
    "parameters": {
        "type": "object",
        "properties": {
            "object_uri": { "type": "string" },
            "center_x": { "type": "integer" },
            "center_y": { "type": "integer" },
            "radius": { "type": "integer" },
            "color": { "type": "string" },
            "fill": { "type": "string" }
        },
        "required": ["object_uri", "center_x", "center_y", "radius", "color", "fill"]
    }
}
```

---------------------------------------------------------------------
## Dispatcher Layer: dispatcher.py

Crucial uses `dispatcher.py` as its runtime dispatcher and **MCP adapter**.

- It dynamically loads all `schema/*.json` and maps them to methods in `canvas.py`
- It is the canonical authority for mapping function names → callable methods
- It verifies arguments against schema and forwards them to the correct canvas method
- It supports **MCP compatibility** by exposing function signatures and JSON Schema
  metadata to upstream model agents or tool routers

### MCP Support
- Each schema defines an LLM-visible tool (name, description, parameters)
- `dispatcher.get_schema()` exposes MCP metadata for UI or AI agents
- Incoming requests use a POST JSON payload:
    ```json
    {
        "action": "canvas_draw_line",
        "params": {
            "object_uri": "abc123",
            "start_x": 10,
            ...
        }
    }
    ```

---------------------------------------------------------------------
## Configuration Layers

### 1. Python Config: `config.py` + `.env`
Sets core infrastructure values (database, security, debug):

- CRUCIAL_HOST, CRUCIAL_PORT
- DATABASE_URL
- CRUCIAL_SSL_ENABLED, CRUCIAL_SSL_CERT, CRUCIAL_SSL_KEY
- API_KEY_AUTH, API_KEYS=comma-separated list

### 2. Frontend Config: `frontend/config.js`
All user-visible and animated rendering is driven by this:

```js
export const config = {
    drawing: {
        speed: 1.0,
        animateShapes: true,
        ghostBrushEnabled: true,
        ...
    },
    graph: {
        bar: { defaultColor: "#3498db", ... },
        pie: { ... }
    },
    canvasName: {
        show: true,
        position: "top-right"
    }
};
```

---------------------------------------------------------------------
## Schema-Based Tool Workflow

A tool like `canvas_draw_polygon` is handled through:

1. `schema/canvas_draw_polygon.json` defines function signature
2. `canvas.py::draw_polygon()` implements backend behavior
3. `frontend/app.js::renderPolygon()` renders in real-time
4. `dispatcher.py` routes requests and validates args
5. `tools/` contains an optional LLM-facing Python stub for CLI/agent use

---------------------------------------------------------------------
## Frontend Architecture

The `app.js` renderer uses a `renderRegistry` object:

```js
const renderRegistry = {
    'canvas_create': renderCreate,
    'canvas_draw_line': renderDrawLine,
    ...
};
```

Each `renderFunction(entry)`:
- Extracts validated schema params
- Animates a brush or path using Three.js / HTML5 canvas
- Draws in realtime with configurable fade, easing, and brush logic

All renderers are discoverable and structured in `app.js`.

---------------------------------------------------------------------
## Crucial API Conventions

All `canvas_*` actions are routed via:

- `POST /v1/canvas/` with:
    ```json
    {
        "action": "canvas_draw_circle",
        "params": {
            "object_uri": "abc123",
            ...
        }
    }
    ```

- `GET /v1/canvas/{id}` returns all actions for playback
- Authenticated via API key in `Authorization: Bearer <key>`
- Write methods require API key. Read access is public (configurable later).

---------------------------------------------------------------------
## Design Summary

- **Schema-First**: Every tool starts with a JSON schema
- **MCP-Compatible**: Fully structured for LLM tool calling and validation
- **Dynamic Dispatch**: `dispatcher.py` routes schema to canvas implementation
- **Config Driven**: Controlled through `.env`, `config.py`, `config.js`
- **Frontend-Backed Rendering**: Animated, timed, human-readable visualizations
- **Extensible**: New tools = schema + method + render
- **Composable**: Functions are declarative, stateful, and recorded
- **Replayable**: Timeline of actions can be revisited or continued

---------------------------------------------------------------------
## Next Development Steps

- Implement remaining `canvas_graph_*` renderers
- Automate schema documentation export (for OpenAPI + LLMs)
- Add in-app timeline scrubber + replay controller
- Build plugin system for tool additions via schema pack loading
- Finalize Dockerfile and deployment scripts
