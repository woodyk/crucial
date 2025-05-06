#!/usr/bin/env bash
#
# create_object.sh

curl -X POST -H "Content-Type: application/json" -d '{
    "object_name": "myCircle",
    "object_type": "circle",
    "object_attributes": {
        "object_color": (0, 255, 0),
        "object_size": {
            "radius": 20,
        },
        "object_init": [100, 100]
    },
}' http://localhost:5000/object
