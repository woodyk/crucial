#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_render_threejs.py
# Description: Integration test for full-page canvas_render_threejs
# Author: Ms. White
# Updated: 2025-05-07

import requests
import json

API_KEY = "demo-key"  # Replace if needed
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def create_canvas():
    payload = {
        "name": "ThreeJS Render Test",
        "x": 800,
        "y": 600,
        "color": "#000000"
    }
    response = requests.post(f"{BASE_URL}/canvas/create", headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("canvas_id")

def render_threejs(canvas_id):
    # Lightweight rotating cube using Three.js
    html_script = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ThreeJS Canvas</title>
        <style>
            body { margin: 0; overflow: hidden; }
            canvas { display: block; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/three@0.150.1/build/three.min.js"></script>
    </head>
    <body>
        <script>
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer();
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            const geometry = new THREE.BoxGeometry();
            const material = new THREE.MeshBasicMaterial({ color: 0x0077ff });
            const cube = new THREE.Mesh(geometry, material);
            scene.add(cube);

            camera.position.z = 5;

            function animate() {
                requestAnimationFrame(animate);
                cube.rotation.x += 0.01;
                cube.rotation.y += 0.01;
                renderer.render(scene, camera);
            }

            animate();
        </script>
    </body>
    </html>
    """

    payload = {
        "action": "canvas_render_threejs",
        "params": {
            "canvas_id": canvas_id,
            "script": html_script
        }
    }

    response = requests.post(f"{BASE_URL}/canvas", headers=HEADERS, json=payload)
    response.raise_for_status()
    return canvas_id

def main():
    canvas_id = create_canvas()
    if not canvas_id:
        print("Canvas creation failed.")
        return

    try:
        render_threejs(canvas_id)
        print(f"[✓] Three.js scene rendered.")
        print(f"[→] View at: {BASE_URL}/?id={canvas_id}")
    except Exception as e:
        print(f"[!] Error rendering ThreeJS: {e}")

if __name__ == "__main__":
    main()

