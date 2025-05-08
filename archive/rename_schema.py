#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: rename_schema.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-07 23:50:20

import os

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schema")

def rename_files():
    for fname in os.listdir(SCHEMA_DIR):
        if not fname.startswith("canvas_") or not fname.endswith(".json"):
            continue
        new_name = fname.replace("canvas_", "", 1)
        src = os.path.join(SCHEMA_DIR, fname)
        dst = os.path.join(SCHEMA_DIR, new_name)
        os.rename(src, dst)
        print(f"Renamed: {fname} → {new_name}")

if __name__ == "__main__":
    rename_files()

