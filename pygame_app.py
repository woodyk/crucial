#!/usr/bin/env python3
#
# pygame_app.py

import pygame
import json
import uuid
from pygame.locals import *
from flask import Flask, request
from threading import Thread
from multiprocessing import Process, set_start_method

class GameApp:
    def __init__(self, resolution=(1280, 720), fps=60):
        pygame.init()
        self.screen = pygame.display.set_mode(resolution)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.game_objects = {}
        self.objects = {}

    def run(self):
        running = True
        while running:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            self.screen.fill((0, 0, 0))
            self.update()
            pygame.display.flip()
        pygame.quit()

    def update(self):
        for game_object in self.game_objects.values():
            game_object.draw(self.screen)

    def create_object(self, json_data):
        object_name = json_data.get('object_name', str(uuid.uuid4()))
        object_type = json_data.get('object_type')
        object_attributes = json_data.get('object_attributes', {})
        color = object_attributes.get('object_color', (255, 255, 255))
        position = tuple(object_attributes.get('object_init', (0, 0)))  # Convert to tuple
        if object_type == 'circle':
            obj_size = object_attributes.get('object_size')
            radius = obj_size['radius']
            game_object = Circle(object_name, color, position, radius)
        elif object_type == 'square':
            obj_size = object_attributes.get('object_size')
            size = obj_size.get('length', 100)
            game_object = Square(object_name, color, position, size)
        elif object_type == 'triangle':
            obj_size = object_attributes.get('object_size')
            size = obj_size.get('length', 100)
            game_object = Triangle(object_name, color, position, size)
        elif object_type == 'polygon':
            points = object_attributes.get('object_size', [(0, 0), (50, 0), (25, 50)])
            game_object = Polygon(object_name, color, position, points)
        elif object_type == 'line':
            end_position = tuple(object_attributes.get('object_end', (100, 100)))
            game_object = Line(object_name, color, position, end_position)
        elif object_type == 'ellipse':
            size = tuple(object_attributes.get('object_size', (50, 50)))
            game_object = Ellipse(object_name, color, position, size)
        else:
            return None

        self.game_objects[object_name] = game_object
        self.objects[object_name] = json_data
        return json.dumps({
            'object_name': object_name,
            'object_type': object_type,
            'object_attributes': object_attributes
        })

class GameObject:
    def __init__(self, name, color, position):
        self.name = name
        self.color = color
        self.position = position

    def draw(self, surface):
        pass

class Circle(GameObject):
    def __init__(self, name, color, position, radius):
        super().__init__(name, color, position)
        self.radius = radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)

class Square(GameObject):
    def __init__(self, name, color, position, size):
        super().__init__(name, color, position)
        self.size = size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.position[0], self.position[1], self.size, self.size))

class Triangle(GameObject):
    def __init__(self, name, color, position, size):
        super().__init__(name, color, position)
        self.size = size

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, [(self.position[0], self.position[1]), (self.position[0] + self.size / 2, self.position[1] - self.size), (self.position[0] + self.size, self.position[1])])

class Polygon(GameObject):
    def __init__(self, name, color, position, points):
        super().__init__(name, color, position)
        self.points = points

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.points)

class Line(GameObject):
    def __init__(self, name, color, position, end_position):
        super().__init__(name, color, position)
        self.end_position = end_position

    def draw(self, surface):
        pygame.draw.line(surface, self.color, self.position, self.end_position)

class Ellipse(GameObject):
    def __init__(self, name, color, position, size):
        super().__init__(name, color, position)
        self.size = size

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1]))

class APIApp:
    def __init__(self, game):
        self.app = Flask(__name__)
        self.app.debug = True  # Enable debug mode
        self.game = game 

        self.app.add_url_rule('/object', 'create_object', self.create_object, methods=['POST'])
        self.app.add_url_rule('/object/<name>', 'read_object', self.read_object, methods=['GET'])
        self.app.add_url_rule('/object/<name>', 'update_object', self.update_object, methods=['PUT'])
        self.app.add_url_rule('/object/<name>', 'delete_object', self.delete_object, methods=['DELETE'])

    def create_object(self):
        json_data = request.get_json()
        self.game.create_object(json_data)
        return "object created", 201

    def read_object(self, name):
        json_data = self.game.read_object(name)
        return json_data, 200

    def update_object(self, name):
        json_data = request.get_json()
        json_data =  self.game.update_object(name, json_data), 200
        return json_data, 200

    def delete_object(self, name):
        status = self.game.delete_object(name)
        return "object deleted", 200

    def run(self):
        self.app.run(use_reloader=False)  # Disable the reloader

game = GameApp(resolution=(1024, 768), fps=30)
game.create_object({
    "object_name": "myCircle",
    "object_type": "circle",
    "object_attributes": {
        "object_color": (255, 0, 0),
        "object_size": {
            "radius": 20,
        },
        "object_init": (100, 100)
    }
})

# Pass the GameApp instance to APIApp
api = APIApp(game)

# Start the API in a separate thread
api_thread = Thread(target=api.run)
api_thread.start()

# Start the game
game.run()
