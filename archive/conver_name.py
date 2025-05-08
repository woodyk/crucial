#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: conver_name.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-07 23:44:11
#!/usr/bin/env python3
# File: strip_canvas_prefix_from_names.py
# Description: Removes 'canvas_' prefix from schema["name"] across all schema files
# Author: Ms. White

import os
import json

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schema")

def patch_schema_names():
    changed = 0
    for file in os.listdir(SCHEMA_DIR):
        if not file.endswith(".json"):
            continue

        path = os.path.join(SCHEMA_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        name = schema.get("name")
        if not name or not name.startswith("canvas_"):
            continue

        short_name = name.replace("canvas_", "", 1)
        schema["name"] = short_name

        with open(path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
        print(f"[✓] Updated {file}: name → {short_name}")
        changed += 1

    print(f"\n{changed} schemas updated.")

if __name__ == "__main__":
    patch_schema_names()

