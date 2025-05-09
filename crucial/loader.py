#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: loader.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-08 20:20:02
# Modified: 2025-05-08 20:22:24
# loader.py

import json
from typing import Optional
from fastapi.responses import Response
from crucial.registry import get_registry

def crucial_python_loader(base_url: str) -> Response:
    """
    Generates a Python script containing all registered Crucial tools as typed Python functions.
    """
    registry = get_registry()
    functions = []

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

        # Build parameter dict entries
        param_dict = ",\n        ".join(f'"{k}": {k}' for k in props)

        docstring = f'"""{desc.strip()}\n\nParameters:\n'
        for k in required_keys + optional_keys:
            t = props[k].get("type", "any")
            d = props[k].get("description", "")
            req = "required" if k in required else "optional"
            docstring += f"  - {k} ({t}, {req}): {d}\n"
        docstring += '"""'

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
    r = requests.post(f"{{BASE_URL}}/canvas/create", json=payload, headers=headers)
    r.raise_for_status()
    data = r.json()
    LAST_CANVAS_ID = data.get("canvas_id")
    return data
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
    r = requests.post(f"{{BASE_URL}}/canvas", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()
'''.strip()

        functions.append(fn)

    full_code = header + "\n\n" + "\n\n".join(functions)
    return Response(content=full_code, media_type="text/plain")

