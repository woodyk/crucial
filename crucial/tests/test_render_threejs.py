#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_render_threejs.py
# Description: Integration test for full-page canvas_render_threejs
# Author: Ms. White
# Created: 2025-05-07
# Modified: 2025-05-06 19:42:37

import requests
import json

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "changeme"  # Replace with a valid API key
}

def create_canvas():
    payload = {
        "name": "Test Embedded ThreeJS",
        "x": 800,
        "y": 600,
        "color": "#000000"
    }
    response = requests.post(f"{BASE_URL}/canvas/create", headers=HEADERS, json=payload)
    print("Canvas Create:", response.status_code)
    try:
        data = response.json()
        print(data)
        return data.get("canvas_id")
    except Exception:
        return None

def render_threejs(canvas_id):
    html_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ThreeJS Test</title>
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
            "object_uri": canvas_id,
            "script": html_page
        }
    }

    response = requests.post(f"{BASE_URL}/canvas", headers=HEADERS, json=payload)
    print("ThreeJS Render:", response.status_code)
    print(response.json())
    print(f"\nOpen in browser: http://localhost:8000/?id={canvas_id}")

def main():
    canvas_id = create_canvas()
    if canvas_id:
        render_threejs(canvas_id)
    else:
        print("Canvas creation failed.")

if __name__ == "__main__":
    main()

