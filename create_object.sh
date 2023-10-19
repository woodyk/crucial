#!/usr/bin/env bash
#
# create_object.sh

curl -X POST -H "Content-Type: application/json" -d '{
    "action": "create",
    "object_name": "myCircle",
    "object_type": "circle",
    "object_attributes": {
        "object_rotation": {
            "x": 0,
            "y": 0,
            "z": 0
        },
        "object_scale": {
            "x": 1,
            "y": 1,
            "z": 1
        },
        "object_physics": {
            "mass": 1,
            "friction": 0.5
        },
        "object_visibility": true,
        "object_lighting": {
            "light_type": "directional",
            "light_color": [1, 1, 1, 1],
            "light_direction": [0, -60, 0]
        },
        "object_control": {
            "controller_type": "keyboard",
            "controller_inputs": {
                "up": "up",
                "down": "down",
                "left": "left",
                "right": "right"
            }
        },
        "object_color": "#FF0000",
        "object_size": 1,
        "object_state": "moveable",
        "object_init": {
            "x": 0,
            "y": 0
        },
        "object_action": "touch",
        "object_reaction": "explode"
    }
}' http://localhost:5000/object
