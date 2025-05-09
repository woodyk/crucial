#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: dispatcher.py
# Description: Action dispatcher for Crucial canvas operations
# Author: Ms. White
# Created: 2025-05-08 02:31:08
# Modified: 2025-05-08 19:15:27

import jsonschema
from fastapi import HTTPException
from importlib import import_module
from crucial.canvas import Canvas
from crucial.registry import get_action_to_schema, get_action_to_method
from crucial.config import get_logger

logger = get_logger(__name__)


class Dispatcher:
    def __init__(self):
        self.schemas = {}
        self.methods = {}
        self.load_schemas()

    def load_schemas(self):
        """
        Load all schemas and tool-to-method mappings from registry.
        """
        self.schemas = get_action_to_schema()
        self.methods = get_action_to_method()
        logger.info("Loaded %d canvas schemas from registry", len(self.schemas))

    def validate(self, action, params):
        """
        Validate tool parameters against JSON Schema.
        """
        schema = self.schemas.get(action)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Unknown action: {action}")
        try:
            jsonschema.validate(params, schema)
        except jsonschema.ValidationError as e:
            logger.warning("Validation failed for action %s: %s", action, e.message)
            raise HTTPException(status_code=400, detail=f"Validation error: {e.message}")

    def dispatch(self, action: str, params: dict) -> dict:
        """
        Dispatch an action to the appropriate Canvas method.
        """
        if action not in self.methods:
            logger.warning("Unknown or disallowed action: %s", action)
            raise HTTPException(status_code=404, detail=f"Unknown action: {action}")

        self.validate(action, params)
        method_name = self.methods[action]
        method = getattr(Canvas, method_name, None)

        if not method:
            logger.error("Canvas method not implemented: %s", method_name)
            raise HTTPException(status_code=501, detail=f"Method not implemented: {method_name}")

        # Special case: create() does not require canvas_id
        if action == "create":
            try:
                result = method(**params)
                logger.info("Canvas created successfully")
                return result
            except Exception as e:
                logger.exception("Error during canvas creation")
                raise HTTPException(status_code=500, detail=f"Create failed: {str(e)}")

        # All other actions require an existing canvas
        canvas_id = params.get("canvas_id") or params.get("object_uri")
        if not canvas_id:
            raise HTTPException(status_code=400, detail="Missing canvas_id")

        canvas = Canvas.from_id(canvas_id)
        if not canvas:
            logger.warning("[Canvas API] Canvas %s not found. (HTTP 404)", canvas_id)
            raise HTTPException(status_code=404, detail=f"Canvas not found: {canvas_id}")

        params.pop("canvas_id", None)
        logger.debug("Dispatching action: %s with params: %s", action, params)

        try:
            method(canvas, **params)
        except Exception as e:
            logger.exception("Error while executing action: %s", action)
            raise HTTPException(status_code=500, detail=f"Dispatch failure: {str(e)}")

        logger.info("Action executed: %s on canvas %s", action, canvas_id)
        return {"status": "ok", "action": action, "canvas_id": canvas_id}

