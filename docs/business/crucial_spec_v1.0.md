# Crucial: A Modular Visual Interface for Language-Based Drawing and Communication

## Overview

Crucial is a modular drawing engine and interface designed to bridge
large language models (LLMs) and human users through real-time visual
communication. It allows LLMs to express ideas via drawing, sketching,
and dynamic rendering through a standardized set of tool-call functions.
Crucial is intended to serve both creative and technical applications —
from freeform artistic illustrations to precise graph-based data
presentations.

Crucial integrates with the EchoAI CLI and may also function as a
standalone library and REST service for external clients.

## Vision

The goal of Crucial is to:
  - Provide a consistent set of drawing primitives that LLMs can use
    via tool calls.
  - Enable real-time visual feedback for users in a canvas interface.
  - Make the rendering experience fluid, expressive, and aesthetically
    engaging.
  - Support graphing and data visualization through extensible tools.
  - Maintain full modularity for future extension into animation,
    interactivity, and 3D rendering.

## Components

The project is divided into the following modular components:

### 1. `server.py` (API Endpoint Layer)
    - Hosts the REST API used by tools to trigger drawing events.
    - Receives JSON payloads for each tool call and dispatches to the
      Crucial canvas engine.
    - Built using FastAPI (recommended) or Flask for simplicity.

### 2. `canvas.py` (Crucial Class)
    - Core class that encapsulates the canvas state and drawing methods.
    - Interprets tool call parameters and executes drawing operations.
    - May internally call animation or state tracking modules.
    - Manages rendering queue and sends updates to the frontend.

### 3. `tools/` (LLM Tool Functions)
    - Contains one Python file per LLM-compatible tool call.
    - Each script defines a callable function (e.g. `canvas_draw_line`)
      that sends an HTTP request to the API with structured parameters.
    - LLMs invoke these directly through OpenAI-style function calling.

    Example tools:
        tools/canvas_draw_line.py
        tools/canvas_draw_circle.py
        tools/canvas_clear.py

### 4. `frontend/` (Electron/Web Canvas Viewer)
    - Hosts the drawing canvas that users can view in real time.
    - Built with HTML/JS and wrapped with Electron to enable local
      execution.
    - Renders updates streamed or pushed from the API backend.
    - May include an optional simulation of stroke-by-stroke drawing.

### 5. `static/` and `schema/` (Assets and Function Signatures)
    - `static/`: Stores JS, CSS, and images for the frontend.
    - `schema/`: Contains OpenAPI-compatible definitions of each tool
      function, allowing LLMs to call them predictably.

## Canvas Tool Function Table

The following primitives are available as LLM-accessible tools:

| Function Name              | Description                                | Parameters                              |
|---------------------------|--------------------------------------------|-----------------------------------------|
| canvas_draw_line          | Draw a straight line                       | start_x, start_y, end_x, end_y, color, width |
| canvas_draw_circle        | Draw a perfect circle                      | center_x, center_y, radius, color, fill |
| canvas_draw_ellipse       | Draw an ellipse                            | center_x, center_y, radius_x, radius_y, color, fill |
| canvas_draw_square        | Draw a square                              | x, y, size, color, fill                 |
| canvas_draw_rectangle     | Draw a rectangle                           | x, y, width, height, color, fill        |
| canvas_draw_polygon       | Draw a polygon                             | points (list of (x, y)), color, fill    |
| canvas_draw_arc           | Draw a circular arc                        | center_x, center_y, radius, start_angle, end_angle, color, width |
| canvas_draw_bezier        | Draw a Bezier curve                        | control_points (list of (x, y)), color, width |
| canvas_draw_point         | Draw a point or dot                        | x, y, color, radius                     |
| canvas_draw_text          | Draw text                                  | text, x, y, font, size, color           |
| canvas_draw_grid          | Draw a coordinate grid                     | spacing, color, thickness               |
| canvas_clear              | Clear the canvas                           | (no parameters)                         |
| canvas_save               | Save canvas to image file                  | file_path, format                       |
| canvas_resize             | Resize the canvas                          | new_width, new_height                   |
| canvas_translate          | Translate origin of canvas                 | dx, dy                                  |
| canvas_rotate             | Rotate canvas space                        | angle_in_degrees                        |
| canvas_scale              | Scale canvas content                       | scale_x, scale_y                        |
| canvas_set_background     | Set background color                       | color                                   |
| canvas_render_threejs     | Render a raw Three.js script               | script (JavaScript string)              |

## Graphing Tool (Planned Extension)

Crucial will extend into structured visualization by supporting the
following graph-oriented tools:

| Function Name              | Description                                  | Parameters                          |
|---------------------------|----------------------------------------------|-------------------------------------|
| canvas_graph_bar          | Draw a bar chart                             | data, position, colors              |
| canvas_graph_line         | Draw a line chart                            | data, axis_config, color            |
| canvas_graph_pie          | Draw a pie chart                             | data, center_x, center_y, radius    |
| canvas_graph_histogram    | Draw a histogram                             | values, bins, position, normalize   |
| canvas_graph_heatmap      | Draw a heatmap matrix                        | matrix, labels, color_map           |
| canvas_graph_scatter      | Draw a scatter plot                          | points, color, axis_config          |

## Development Plan

1. **Project Initialization**
    - Scaffold project structure with server, canvas, tools, and frontend.
    - Choose FastAPI for REST and set up CORS for frontend access.

2. **Canvas Class (crucial/canvas.py)**
    - Implement drawing surface (e.g., PIL or Cairo).
    - Expose methods: draw_line, draw_circle, clear, save, etc.

3. **REST API (crucial/server.py)**
    - Define endpoints for each tool function.
    - Receive and validate JSON payloads and pass to Crucial class.

4. **Frontend Canvas (crucial/frontend/)**
    - Build web viewer using HTML5 canvas + WebSocket/REST polling.
    - Wrap with Electron to enable local app deployment.

5. **LLM Tool Modules (crucial/tools/)**
    - Each script defines one callable LLM tool, POSTing to the API.
    - Validate and format parameters; catch exceptions.

6. **Function Schemas (crucial/schema/)**
    - Write OpenAPI-compatible JSON schemas for all tools.
    - Include `examples` for LLM training and tool selection.

7. **Testing and CI**
    - Add unit tests for each canvas primitive.
    - Include integration tests for REST + drawing combination.

8. **Graphing Tool Additions**
    - Add `canvas_graph_*` function definitions and schemas.
    - Use same canvas backend; render to grid space with labels.

## Future Roadmap

- Real-time animation during drawing (stroke simulation)
- Undo/redo support
- Live collaborative drawing sessions
- SVG and vector export
- 3D Canvas primitives (cube, sphere) with animation
- Support for `p5.js`, `babylon.js` render modes

## Closing

Crucial is designed to be lightweight, expressive, and modular —
empowering LLMs to communicate visually while remaining friendly to
human developers and artists alike. It will serve as a foundation for
intelligent, graphical communication interfaces.

---
Project Owner: Wadih Khairallah
Project Name: Crucial
Project Type: Visual Interaction Library for LLMs and Humans
