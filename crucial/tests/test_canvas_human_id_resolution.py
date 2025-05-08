#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_human_id_threejs.py
# Description: Test human-readable canvas ID with ThreeJS rendering
# Author: Ms. White
# Created: 2025-05-07
# Modified: 2025-05-07 23:55:32

import requests
import json

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "changeme"  # Replace with your valid API key
}

def create_canvas():
    payload = {
        "name": "Human ID ThreeJS Test",
        "x": 640,
        "y": 480,
        "color": "#333333"
    }
    response = requests.post(f"{BASE_URL}/canvas/create", headers=HEADERS, json=payload)
    print("Create:", response.status_code)
    assert response.status_code == 200, "Canvas creation failed"
    data = response.json()
    print(json.dumps(data, indent=2))
    return data["canvas_id"], data["human_id"]

def inject_threejs(canvas_id):
    full_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ThreeJS Canvas Test</title>
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
            const material = new THREE.MeshBasicMaterial({ color: 0x00ffcc });
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
        "action": "render_threejs",
        "params": {
            "canvas_id": canvas_id,
            "script": full_html
        }
    }

    response = requests.post(f"{BASE_URL}/canvas", headers=HEADERS, json=payload)
    print(f"Render for ID: {canvas_id} → {response.status_code}")
    print(response.json())
    assert response.status_code == 200, f"Render failed for ID: {canvas_id}"


def main():
    uuid_id, human_id = create_canvas()

    print("\n--- Rendering with full UUID ---")
    inject_threejs(uuid_id)

    print("\n--- Rendering with human ID ---")
    inject_threejs(human_id)

    print("\nTest complete. View in browser:")
    print(f"http://localhost:8000/?id={human_id}")

if __name__ == "__main__":
    main()

