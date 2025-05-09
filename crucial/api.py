#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: api.py
# Description: Dynamically exposes all Crucial canvas API tools as Python functions
# Author: Ms. White
# Created: 2025-05-08
# Modified: 2025-05-08 18:17:36

import os
import json
import inspect
from types import FunctionType
from crucial.registry import get_registry

__all__ = []

# Global configuration
CONFIG = {
    "url": "http://localhost:8000",
    "api_key": os.environ.get("CRUCIAL_API_KEY", "demo-key"),
    "last_canvas_id_file": os.path.join(os.path.dirname(__file__), ".last_canvas_id")
}

def _post(endpoint: str, payload: dict) -> dict:
    headers = {"x-api-key": CONFIG["api_key"]}
    url = f"{CONFIG['url']}{endpoint}"
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def _inject_canvas(payload: dict) -> dict:
    canvas_id = _get_last_canvas_id()
    if not canvas_id:
        raise ValueError("No canvas is active. Call create() first.")
    payload["canvas_id"] = canvas_id
    return payload

def _build_tool_function(name: str, params: dict, description: str = "") -> FunctionType:
    """
    Dynamically create a top-level Python function for a Crucial schema tool.
    This function will automatically call the Crucial API and include param labels.
    """
    args = []
    for key, meta in params.items():
        default = "None" if key not in params.get("required", []) else inspect._empty
        args.append((key, meta.get("type", "Any")))

    arg_str = ", ".join([f"{k}" for k, _ in args])
    doc = f'"""{description or name}\n\nParams:\n'
    for k, v in params.items():
        doc += f"  - {k} ({v.get('type', 'any')}): {v.get('description', '')}\n"
    doc += '"""'

    # Function body source code
    func_code = f"def {name}({arg_str}):\n"
    func_code += f"    {doc}\n"
    func_code += f"    payload = dict({arg_str})\n"
    if name == "create":
        func_code += f"    return _post('/canvas/create', payload)\n"
    else:
        func_code += f"    return _post('/canvas', {{'action': '{name}', 'params': _inject_canvas(payload)}})\n"

    local_ns = {}
    exec(func_code, globals(), local_ns)
    return local_ns[name]

# Auto-generate all tool functions from schema
for module in get_registry()["modules"]:
    name = module["name"]
    description = module.get("description", "")
    params = module.get("parameters", {}).get("properties", {})

    try:
        fn = _build_tool_function(name, params, description)
        globals()[name] = fn
        __all__.append(name)
    except Exception as e:
        print(f"[!] Failed to build {name}: {e}")

