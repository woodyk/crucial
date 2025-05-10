#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: loader.py
# Author: Ms. White 
# Description: Generates Crucial-compatible typed functions and returns them for LLM integration.
# Created: 2025-05-08
# Modified: 2025-05-09 20:35:00

import json
from typing import Optional
from fastapi.responses import Response
from crucial.registry import get_registry

def crucial_python_loader(base_url: str) -> Response:
    """
    Generate Python client functions for registered Crucial tools with typing and LLM-aligned returns.

    Returns:
        Response: A plain text response containing valid Python code.
    """
    registry = get_registry()
    functions = []
    exported_names = []

    header = f'''\
# Auto-generated Crucial client from {base_url}/python
import requests
from typing import Optional

BASE_URL = "{base_url}"
API_KEY = "<INSERT-YOUR-API-KEY-HERE>"

LAST_CANVAS_ID = None
'''

    type_map = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict"
    }

    for module in registry.get("modules", []):
        original_name = module["name"]
        name = f"canvas_{original_name}"
        exported_names.append(name)
        schema = module.get("parameters", {})
        props = schema.get("properties", {})
        required = schema.get("required", [])
        desc = module.get("description", "No description.")

        required_keys = [k for k in required if k in props]
        optional_keys = [k for k in props if k not in required]

        sig_parts = []
        for k in required_keys:
            json_type = props[k].get("type", "string")
            pytype = type_map.get(json_type, "Any")
            sig_parts.append(f"{k}: {pytype}")
        for k in optional_keys:
            json_type = props[k].get("type", "string")
            pytype = type_map.get(json_type, "Any")
            sig_parts.append(f"{k}: Optional[{pytype}] = None")

        signature = ", ".join(sig_parts)
        param_dict = ",\n        ".join(f'"{k}": {k}' for k in props)

        docstring_lines = [
            f'"""',
            f"{desc.strip()}",
            "",
            "Args:"
        ]
        for k in required_keys + optional_keys:
            t = props[k].get("type", "any")
            d = props[k].get("description", "").strip()
            pytype = type_map.get(t, "Any")
            optional = k not in required
            type_repr = f"Optional[{pytype}]" if optional else pytype
            docstring_lines.append(f"    {k} ({type_repr}): {d or 'Parameter.'}")
        docstring_lines += [
            "",
            "Returns:",
            "    dict: {",
            '        "status": "success" or "error",',
            '        "action": str,',
            '        "data": dict (if success),',
            '        "error": str (if failure),',
            '        "suggestion": str (if applicable)',
            "    }",
            '"""'
        ]
        docstring = "\n".join(docstring_lines)

        if original_name == "create":
            fn = f'''
def {name}({signature}):
    global LAST_CANVAS_ID
    {docstring}
    payload = {{
        {param_dict}
    }}
    headers = {{
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }}
    try:
        r = requests.post(f"{{BASE_URL}}/canvas/create", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        LAST_CANVAS_ID = data.get("canvas_id")
        return {{
            "status": "success",
            "action": "create",
            "data": data
        }}
    except Exception as e:
        return {{
            "status": "error",
            "action": "create",
            "error": str(e),
            "suggestion": "Check API key, network connection, or payload format."
        }}
'''.strip()
        else:
            fn = f'''
def {name}({signature}):
    {docstring}
    payload = {{
        "action": "{original_name}",
        "params": {{
            {param_dict}
        }}
    }}
    headers = {{
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }}
    try:
        r = requests.post(f"{{BASE_URL}}/canvas", json=payload, headers=headers)
        r.raise_for_status()
        return {{
            "status": "success",
            "action": "{original_name}",
            "data": r.json()
        }}
    except Exception as e:
        return {{
            "status": "error",
            "action": "{original_name}",
            "error": str(e),
            "suggestion": "Check API key, network connection, or request format."
        }}
'''.strip()

        functions.append(fn)

    # Append open_canvas utility
    open_canvas_fn = '''
def open_canvas(canvas_id: str):
    """
    Open the default web browser to the canvas URL for the given canvas_id.

    Args:
        canvas_id (str): The unique ID of the canvas to view.

    Returns:
        dict: {
            "status": "success" or "error",
            "action": "open_canvas",
            "data": {
                "url": str
            },
            "error": str (if failure),
            "suggestion": str (if applicable)
        }
    """
    import webbrowser
    try:
        url = f"{BASE_URL}/canvas/{canvas_id}"
        webbrowser.open(url, new=0)
        return {
            "status": "success",
            "action": "open_canvas",
            "data": {"url": url}
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "open_canvas",
            "error": str(e),
            "suggestion": "Ensure a default browser is available and the URL is well-formed."
        }
'''.strip()

    functions.append(open_canvas_fn)
    exported_names.append("open_canvas")

    export_dict = "\n".join([
        f'    "{name}": {name},' for name in exported_names
    ])

    footer = f'''
__all__ = [{", ".join(f'"{n}"' for n in exported_names)}]
'''.strip()

    full_code = header + "\n\n" + "\n\n".join(functions) + "\n\n" + footer
    return Response(content=full_code, media_type="text/plain")

