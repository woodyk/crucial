#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: human_id.py
# Author: Wadih Khairallah
# Description: 
# Created: 2025-05-06 20:49:02
# Modified: 2025-05-06 22:28:26

import random
import uuid
from hashlib import sha256

from pathlib import Path

ADJ_PATH = Path(__file__).parent / "words" / "adjectives.txt"
NOUN_PATH = Path(__file__).parent / "words" / "nouns.txt"

ADJECTIVES = ADJ_PATH.read_text().splitlines()
NOUNS = NOUN_PATH.read_text().splitlines()

def generate_human_id() -> str:
    """
    Generate a fully random human-readable ID in the form: adjective-noun-###.
    Example: 'brisk-vortex-197'
    """
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    suffix = random.randint(0, 999)
    return f"{adjective}-{noun}-{suffix:03d}"

'''
def generate_human_id(seed: str = None, deterministic: bool = False) -> str:
    """
    Generate a human-friendly ID. If `deterministic` is True, use SHA256(seed).
    Otherwise, use full random selection.
    """
    if deterministic and seed:
        digest = sha256(seed.encode()).digest()
        a_index = int.from_bytes(digest[0:2], 'big') % len(ADJECTIVES)
        n_index = int.from_bytes(digest[2:4], 'big') % len(NOUNS)
        suffix = int.from_bytes(digest[4:6], 'big') % 1000
        return f"{ADJECTIVES[a_index]}-{NOUNS[n_index]}-{suffix:03d}"
    else:
        adjective = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)
        suffix = random.randint(0, 999)
        return f"{adjective}-{noun}-{suffix:03d}"
'''
