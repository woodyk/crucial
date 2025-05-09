#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test.py
# Description: Lists all auto-generated Crucial API tool functions with parameter info
# Author: Ms. White
# Created: 2025-05-08
# Modified: 2025-05-08 18:18:24

import inspect
import importlib
from pprint import pprint

# Load all canvas API functions
"""
api = importlib.import_module("crucial.api")
"""

import crucial.api as api

print("== Crucial API Tool Functions ==")
print()

for name in getattr(api, "__all__", []):
    fn = getattr(api, name, None)
    if not fn or not callable(fn):
        continue

    sig = inspect.signature(fn)
    doc = inspect.getdoc(fn) or ""

    print(f"🧩 {name} {sig}")
    print("-" * (len(name) + len(str(sig)) + 2))

    for line in doc.splitlines():
        print(f"  {line}")

    print()

