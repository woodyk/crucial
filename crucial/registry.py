# File: registry.py
# Description: Dynamic MCP-compatible registry based on schema directory
# Author: Ms. White
# Created: 2025-05-06

import json
import os

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schema")

def get_registry():
    """
    Load all tool schemas from the schema/ directory and return
    a combined MCP-compatible registry object.
    """
    modules = []

    for filename in sorted(os.listdir(SCHEMA_DIR)):
        if filename.endswith(".json"):
            filepath = os.path.join(SCHEMA_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    schema = json.load(f)
                    modules.append({
                        "name": schema.get("name"),
                        "description": schema.get("description", ""),
                        "parameters": schema.get("parameters", {})
                    })
            except Exception as e:
                print(f"Failed to load schema: {filename} ({e})")

    return {"modules": modules}

if __name__ == "__main__":
    # Preview mode for CLI debugging
    import pprint
    pprint.pprint(get_registry())
