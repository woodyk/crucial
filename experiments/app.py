#!/usr/bin/env python3
#
# app.py

from flask import Flask, request
from threading import Thread
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Point3, Vec3, Vec4
from panda3d.core import Shader
from panda3d.core import Texture, TextureStage
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import LightAttrib
from panda3d.core import PerspectiveLens
from panda3d.core import TextNode
from panda3d.core import LPoint3, LVector3
from panda3d.core import BitMask32
from panda3d.core import loadPrcFileData, LineSegs, GeomNode
from panda3d.core import MouseButton
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename, ExecutionEnvironment
from panda3d.core import NodePath, Camera, TextNode
from panda3d.core import Point3
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from math import sin, cos, pi
import matplotlib.colors as mcolors
import uuid
import json
import sys

class GameApp(ShowBase):
    def __init__(self, resolution=(1280, 720), fps=60):
        # Set the resolution.
        loadPrcFileData("", "win-size 1280 720")  # Set the resolution to 1280x720.

        # Set the FPS.
        loadPrcFileData("", "clock-mode limited")  # Limit the frame rate.
        loadPrcFileData("", "clock-frame-rate 60")  # Set the frame rate to 60 FPS.

        ShowBase.__init__(self)

        # Set the camera's position and focus.
        self.camera.setPos(0, -10, 0)
        self.camera.lookAt(0, 0, 0)

        # Set up the task manager.
        self.taskMgr.add(self.update, "updateTask")

        # Disable the default mouse controls.
        self.disableMouse()

        # Add the task that will update the camera position each frame.
        self.taskMgr.add(self.update_camera, "update_camera")

        # Create the reference stick.
        self.create_reference_stick()

        # Set up the keyboard controls.
        self.accept('shift-=', self.zoom_in)  # Zoom in when shift and + are pressed.
        self.accept('shift--', self.zoom_out)  # Zoom out when shift and - are pressed.

        # Set up the keyboard control.
        self.accept('shift-a', self.reveal_all_objects)

        # Set up the keyboard control.
        self.accept('shift-c', self.center_camera)

        # Set the background color to black.
        self.setBackgroundColor(0, 0, 0)  # RGB values for black.

        # Set up a dictionary to hold game objects.
        self.game_objects = {}

        # Initialize the objects dictionary.
        self.objects = {}

    def center_camera(self):
        # Set the camera's position and focus to the origin.
        self.camera.setPos(0, -10, 0)
        self.camera.lookAt(0, 0, 0)

    def reveal_all_objects(self):
        # Loop over all objects and make them visible.
        for obj in self.render.get_children():
            obj.show()

    def zoom_in(self):
        # Move the camera closer to the origin.
        self.camera.setY(self.camera.getY() + 1)

    def zoom_out(self):
        # Move the camera further from the origin.
        self.camera.setY(self.camera.getY() - 1)

    def update_camera(self, task):
        # Check if the zoom in key is down.
        if self.mouseWatcherNode.is_button_down('shift-='):
            self.zoom_in()

        # Check if the zoom out key is down.
        if self.mouseWatcherNode.is_button_down('shift--'):
            self.zoom_out()

        # Use the shift-right-arrow and shift-left-arrow keys to pan.
        if self.mouseWatcherNode.is_button_down('shift-arrow_right'):
            self.pan_right()
        elif self.mouseWatcherNode.is_button_down('shift-arrow_left'):
            self.pan_left()

        # Check if the right mouse button is down.
        if self.mouseWatcherNode.hasMouse() and self.mouseWatcherNode.is_button_down(MouseButton.three()):
            # Get the mouse position.
            x = self.mouseWatcherNode.get_mouse_x()
            y = self.mouseWatcherNode.get_mouse_y()

            # Use the mouse position to rotate the camera.
            self.camera.setHpr(x * 360, y * 360, 0)

            # Use the mouse wheel to zoom in and out.
            if self.mouseWatcherNode.is_button_down(MouseButton.wheel_up()):
                self.zoom_in()
            elif self.mouseWatcherNode.is_button_down(MouseButton.wheel_down()):
                self.zoom_out()

        return Task.cont

    def create_reference_stick(self):
        # Create the lines for the x, y, and z axes.
        x_line = LineSegs()
        x_line.set_thickness(5)  # Set the thickness to 2.
        x_line.set_color(0, 0, 1, 1)  # Blue.
        x_line.draw_to(5000, 0, 0)  # Set the length to 5.
        y_line = LineSegs()
        y_line.set_thickness(5)  # Set the thickness to 2.
        y_line.set_color(1, 1, 0, 1)  # Yellow.
        y_line.draw_to(0, 5000, 0)  # Set the length to 5.
        z_line = LineSegs()
        z_line.set_thickness(5)  # Set the thickness to 2.
        z_line.set_color(1, 0, 0, 1)  # Red.
        z_line.draw_to(0, 0, 5000)  # Set the length to 5.

        # Create the node paths for the lines.
        x_node = NodePath(x_line.create())
        y_node = NodePath(y_line.create())
        z_node = NodePath(z_line.create())

        # Attach the lines to the render.
        x_node.reparent_to(self.render)
        y_node.reparent_to(self.render)
        z_node.reparent_to(self.render)

    def update(self, task):
        dt = globalClock.getDt()

        # Update game objects here.

        return Task.cont

    def create_object(self, json_data):
        # Check if 'object_name' is in json_data. If not, create one using a UUID.
        object_name = json_data.get('object_name') + '_' + str(uuid.uuid4())
        if not object_name:
            object_name = str(uuid.uuid4())
            json_data['object_name'] = object_name

        # Parse the JSON and create a game object based on the instructions.
        object_type = json_data.get('object_type')

        # Ensure object_attributes is defined
        object_attributes = json_data.get('object_attributes', {})

        # Check if the object already exists
        existing_object = self.game_objects.get(object_name)
        if existing_object:
            game_object = existing_object
        else:
            # Create the appropriate object based on the object type.
            if object_type == 'sphere':
                radius = object_attributes.get('radius', 1)
                slices = object_attributes.get('slices', 20)
                stacks = object_attributes.get('stacks', 20)
                game_object = self.make_sphere(radius, slices, stacks)
            elif object_type == 'cube':
                size = object_attributes.get('size', 1)
                game_object = self.make_cube(size)
            elif object_type == 'circle':
                size_attrib = object_attributes.get('object_size')
                radius = size_attrib.get('radius', 1)
                slices = size_attrib.get('slices', 20)
                game_object = self.make_circle(radius, slices)
            elif object_type == 'triangle':
                size = object_attributes.get('size', 1)
                game_object = self.make_triangle(size)
            elif object_type == 'rectangle':
                width = object_attributes.get('width', 1)
                height = object_attributes.get('height', 1)
                game_object = self.make_rectangle(width, height)
            else:
                return None  # Invalid object type.

        # Convert required colors
        color = object_attributes.get('object_color', 'white')
        color_rgba = self.convert_to_rgba(color)
        game_object.setColor(Vec4(*color_rgba))  # Set the color or default to white.

        # Scale the object
        #game_object.setScale(object_attributes.get('object_size', 1))  # Set the scale or default to 1.

        # Position the object
        init_pos = object_attributes.get('object_init', {'x': 0, 'y': 0, 'z': 0})
        init_pos = [init_pos.get('x', 0), init_pos.get('y', 0), init_pos.get('z', 0)]
        game_object.setPos(Point3(*init_pos))  # Set the initial position or default to (0, 0, 0).

        # Set the object rotation
        rotation = object_attributes.get('object_rotation', {'heading': 0, 'pitch': 0, 'roll': 0})
        rotation = [rotation.get('heading', 0), rotation.get('pitch', 0), rotation.get('roll', 0)]
        game_object.setHpr(Vec3(*rotation))  # Set the rotation or default to (0, 0, 0).

        # Set the objects transparency
        game_object.setTransparency(object_attributes.get('object_visibility', True))  # Set the visibility or default to True.

        # Set the other attributes if they're defined.
        if 'object_texture' in object_attributes:
            texture = self.loader.loadTexture(object_attributes['object_texture'])
            game_object.setTexture(texture, 1)

        if 'object_physics' in object_attributes:
            physics = object_attributes['object_physics']
            # TODO: Apply the physics properties to the game object.

        if 'object_parent' in object_attributes:
            parent = self.game_objects.get(object_attributes['object_parent'])
            if parent:
                game_object.reparentTo(parent)

        if 'object_children' in object_attributes:
            children = object_attributes['object_children']
            for child_name in children:
                child = self.game_objects.get(child_name)
                if child:
                    child.reparentTo(game_object)

        if 'object_lighting' in object_attributes:
            lighting = object_attributes['object_lighting']
            # Create a directional light.
            dlight = DirectionalLight('dlight')
            dlight.setColor(Vec4(1, 1, 1, 1))  # Set the color of the light.
            dlnp = render.attachNewNode(dlight)  # Attach the light to the render.
            dlnp.setHpr(0, -60, 0)  # Set the direction of the light.
            game_object.setLight(dlnp)  # Attach the light to the game object.

        if 'object_animation' in object_attributes:
            animation = self.loader.loadModel(object_attributes['object_animation'])
            # Assume the animation file contains a single animation named "anim".
            game_object.loop("anim")  # Start playing the animation in a loop.

        if 'object_sound' in object_attributes:
            sound = self.loader.loadSfx(object_attributes['object_sound'])
            sound.setLoop(True)  # Set the sound to loop continuously.
            sound.play()  # Start playing the sound.
            game_object.setPythonTag('sound', sound)  # Attach the sound to the game object.

        if 'object_control' in object_attributes:
            control = object_attributes['object_control']
            controller_type = control.get('controller_type')
            controller_inputs = control.get('controller_inputs', {})
            for input, action in controller_inputs.items():
                if controller_type == 'keyboard':
                    self.accept(input, self.perform_action, [game_object, action])
                elif controller_type == 'mouse':
                    # TODO: Set up mouse controls.
                    pass
                elif controller_type == 'joystick':
                    # TODO: Set up joystick controls.
                    pass
                else:
                    return None  # Invalid controller type.

        if 'object_state' in object_attributes:
            state = object_attributes['object_state']
            # TODO: Apply the state to the game object.

        if 'object_action' in object_attributes:
            action = object_attributes['object_action']
            # TODO: Apply the action to the game object.

        if 'object_reaction' in object_attributes:
            reaction = object_attributes['object_reaction']
            # TODO: Apply the reaction to the game object.

        # Add the object to the scene graph.
        game_object.reparentTo(self.render)

        self.game_objects[object_name] = game_object

        # Store the JSON document in memory.
        self.objects[object_name] = json_data

        # Return the JSON representation of the created object.
        return json.dumps({
            'object_name': object_name,
            'object_type': object_type,
            'object_attributes': object_attributes
        })

    def read_object(self, object_name):
        # Return the JSON document for the game object with the given name.
        return self.objects.get(object_name)

    def update_object(self, json_data):
        object_data = self.create_object(json_data)
        return object_data

    def delete_object(self, object_name):
        # Find the game object with the given name.
        game_object = self.find("**/" + object_name)
        if game_object is None:
            return None  # No game object with the given name was found.

        # Remove the game object from the scene graph.
        game_object.removeNode()

        # Remove the JSON document for the game object from the game_objects dictionary.
        del self.game_objects[object_name]
        del self.objects[object_name]

    def perform_action(self, game_object, action):
        if action == 'up':
            game_object.setPos(game_object.getPos() + Vec3(0, 1, 0))
        elif action == 'down':
            game_object.setPos(game_object.getPos() + Vec3(0, -1, 0))
        elif action == 'left':
            game_object.setPos(game_object.getPos() + Vec3(-1, 0, 0))
        elif action == 'right':
            game_object.setPos(game_object.getPos() + Vec3(1, 0, 0))
        elif action == 'strafe_left':
            game_object.setPos(game_object.getPos() + Vec3(-1, 0, 0))
        elif action == 'strafe_right':
            game_object.setPos(game_object.getPos() + Vec3(1, 0, 0))
        elif action == 'jump':
            # TODO: Make the game object jump.
            pass
        elif action == 'shoot':
            # TODO: Make the game object shoot.
            pass
        elif action == 'explode':
            # TODO: Make the game object explode.
            pass
        elif action == 'interact':
            # TODO: Interact with the objects object_reaction ability
            pass
        else:
            print(f"Unknown action: {action}")

    def make_sphere(self, radius, slices, stacks):
        format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData('sphere', format, Geom.UHStatic)
        vdata.setNumRows((slices + 1) * (stacks + 1))

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')

        for stack in range(stacks + 1):
            stack_frac = stack / float(stacks)
            stack_angle = pi * stack_frac
            z = radius * cos(stack_angle)
            circle_radius = radius * sin(stack_angle)

            for slice in range(slices + 1):
                slice_frac = slice / float(slices)
                slice_angle = 2 * pi * slice_frac
                x = circle_radius * sin(slice_angle)
                y = circle_radius * cos(slice_angle)

                vertex.addData3(x, y, z)
                normal.addData3(x, y, z)

        geom = Geom(vdata)
        for stack in range(stacks):
            for slice in range(slices):
                v0 = stack * (slices + 1) + slice
                v1 = ((stack + 1) * (slices + 1) + slice)
                v2 = ((stack + 1) * (slices + 1) + (slice + 1))
                v3 = (stack * (slices + 1) + (slice + 1))

                prim = GeomTriangles(Geom.UHStatic)
                prim.addVertices(v0, v1, v2)
                prim.addVertices(v0, v2, v3)
                geom.addPrimitive(prim)

        node = GeomNode('sphere')
        node.addGeom(geom)

        return NodePath(node)

    def make_cube(self, size):
        format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData('cube', format, Geom.UHStatic)
        vdata.setNumRows(24)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')

        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                for k in range(-1, 2, 2):
                    vertex.addData3(size * i, size * j, size * k)
                    normal.addData3(i, j, k)

        geom = Geom(vdata)
        for i in range(6):
            prim = GeomTriangles(Geom.UHStatic)
            prim.addVertices(i * 4, i * 4 + 1, i * 4 + 2)
            prim.addVertices(i * 4, i * 4 + 2, i * 4 + 3)
            geom.addPrimitive(prim)

        node = GeomNode('cube')
        node.addGeom(geom)

        return NodePath(node)

    def make_circle(self, radius, slices):
        format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData('circle', format, Geom.UHStatic)
        vdata.setNumRows(slices + 2)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')

        vertex.addData3(0, 0, 0)
        normal.addData3(0, 0, 1)

        for slice in range(slices + 1):
            slice_frac = slice / float(slices)
            slice_angle = 2 * pi * slice_frac
            x = radius * sin(slice_angle)
            y = radius * cos(slice_angle)

            vertex.addData3(x, y, 0)
            normal.addData3(0, 0, 1)

        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        for slice in range(slices):
            prim.addVertices(0, slice + 1, slice + 2)
        geom.addPrimitive(prim)

        node = GeomNode('circle')
        node.addGeom(geom)

        return NodePath(node)

    # For triangle and rectangle, we can use the CardMaker class
    def make_triangle(self, size):
        cm = CardMaker('triangle')
        cm.setFrame(Point3(-size, 0, -size), Point3(size, 0, -size), Point3(0, 0, size))
        return NodePath(cm.generate())

    def make_rectangle(self, width, height):
        cm = CardMaker('rectangle')
        cm.setFrame(-width / 2, width / 2, -height / 2, height / 2)
        return NodePath(cm.generate())

    def convert_to_rgba(self, color):
        if color.startswith('#'):  # If the color is a hex color code
            color = color.lstrip('#')
            return tuple(int(color[i:i+2], 16)/255 for i in (0, 2, 4)) + (1,)  # Alpha is set to 1
        else:  # If the color is a color name
            rgb = mcolors.to_rgb(color)  # Convert the color name to RGB
            return rgb + (1,)  # Add alpha

class APIApp:
    def __init__(self, game):
        self.app = Flask(__name__)
        self.game = game 

        self.app.add_url_rule('/object', 'create_object', self.create_object, methods=['POST'])
        self.app.add_url_rule('/object/<name>', 'read_object', self.read_object, methods=['GET'])
        self.app.add_url_rule('/object/<name>', 'update_object', self.update_object, methods=['PUT'])
        self.app.add_url_rule('/object/<name>', 'delete_object', self.delete_object, methods=['DELETE'])

    def create_object(self):
        json_data = request.get_json()
        self.game.create_object(json_data)
        return 'Object created', 201

    def read_object(self, name):
        self.game.read_object(name)
        return 'Object read', 200

    def update_object(self, name):
        json_data = request.get_json()
        self.game.update_object(name, json_data)
        return 'Object updated', 200

    def delete_object(self, name):
        self.game.delete_object(name)
        return 'Object deleted', 200

    def run(self):
        self.app.run()

game = GameApp(resolution=(1024, 768), fps=30)  # Create an instance of GameApp
api = APIApp(game)  # Pass the GameApp instance to APIApp

# Start the API in a separate thread
api_thread = Thread(target=api.run)
api_thread.start()

game.create_object({
    "object_name": "myCircle",
    "object_type": "circle",
    "object_attributes": {
        "object_color": "red",
        "object_size": {
            "radius": 1,
            "slices": 20
        },
        "object_init": {
            "x": 0,
            "y": 0,
            "z": 0
        }
    }
})



# Start the game
game.run()

# Example object document
'''
{
    "action": "create",
    "object_name": "myObject",
    "object_type": "sphere",
    "object_attributes": {
        "object_texture": "path/to/texture.png",
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
        "object_parent": "parentObject",
        "object_children": ["child1", "child2"],
        "object_lighting": {
           "light_type": "directional",
           "light_color": [1, 1, 1, 1],
           "light_direction": [0, -60, 0]
        },
        "object_animation": "path/to/animation.egg",
        "object_sound": "path/to/sound.wav",
        "object_control": {
           "controller_type": "keyboard",
           "controller_inputs": {
               "w": "up",
               "a": "left",
               "s": "down",
               "d": "right",
               "space": "jump"
           }
        }
        "object_color": "#0000FF",
        "object_size": 1,
        "object_state": "moveable",
        "object_init": {
            "x": 0,
            "y": 0
        },
        "object_action": "touch",
        "object_reaction": "explode"
    }
}
'''
