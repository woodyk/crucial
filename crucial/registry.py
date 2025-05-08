#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: registry.py
# Description: Dynamic MCP-compatible registry based on schema directory
# Author: Ms. White
# Updated: 2025-05-08

import os
import json
from crucial.config import get_logger

logger = get_logger(__name__)

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
                logger.warning("Failed to load schema: %s (%s)", filename, e)
    return {"modules": modules}


def load_all_schemas():
    """
    Return all schema definitions keyed by tool name.
    """
    schemas = {}
    for filename in sorted(os.listdir(SCHEMA_DIR)):
        if filename.endswith(".json"):
            path = os.path.join(SCHEMA_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                    name = schema.get("name")
                    if name:
                        schemas[name] = schema
            except Exception as e:
                logger.warning("Failed to load schema: %s (%s)", filename, e)
    return schemas


def get_action_to_schema():
    """
    Return a map of action_name → full JSON schema
    where action_name = filename stem (no .json).
    """
    result = {}
    for filename in sorted(os.listdir(SCHEMA_DIR)):
        if filename.endswith(".json"):
            path = os.path.join(SCHEMA_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                    result[filename.replace(".json", "")] = schema
            except Exception as e:
                logger.warning("Failed to parse schema: %s (%s)", filename, e)
    return result


def get_action_to_method():
    """
    Return a map of action_name → method_name
    where both are assumed to match schema["name"].
    """
    result = {}
    for filename in sorted(os.listdir(SCHEMA_DIR)):
        if filename.endswith(".json"):
            path = os.path.join(SCHEMA_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                    action = filename.replace(".json", "")
                    method = schema.get("name")
                    if method:
                        result[action] = method
            except Exception as e:
                logger.warning("Failed to read schema for: %s (%s)", filename, e)
    return result


if __name__ == "__main__":
    import pprint
    pprint.pprint(get_registry())

