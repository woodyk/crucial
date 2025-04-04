#!/usr/bin/env python3
#
# pygame_app.py

import sys
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
        selected_index = False 
        object_keys = []
        current_index = 0
        
        while running:
            # Update object_keys
            object_keys = list(self.game_objects.keys())
            
            if not selected_index:
                selected_index = object_keys[0] 

            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    point = pygame.mouse.get_pos()
                    for game_object in self.game_objects.values():
                        if game_object.contains_point(point):
                            # The object has been clicked on
                            game_object.selected = True
                            selected_index = game_object.name
                elif event.type == KEYDOWN:
                    if event.key == K_TAB:
                        # Deselect the current object
                        self.game_objects[selected_index].selected = False
                        # Cycle to the next object
                        current_index = object_keys.index(selected_index)
                        selected_index = object_keys[(current_index + 1) % len(object_keys)]
                        # Select the new object
                        self.game_objects[selected_index].selected = True
                        print(f"Tab pressed: {selected_index} {current_index}")
                    elif event.key == K_q:
                        running = False

            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[K_UP]:
                dy = -5
            if keys[K_DOWN]:
                dy = 5
            if keys[K_LEFT]:
                dx = -5
            if keys[K_RIGHT]:
                dx = 5
            if self.game_objects[selected_index].selected:
                self.game_objects[selected_index].move(dx, dy)

            self.screen.fill((0, 0, 0))
            self.update()
            pygame.display.flip()
        pygame.quit()

    def update(self):
        for game_object in self.game_objects.values():
            game_object.draw(self.screen)

    def create_object(self, json_data):
        new_uuid = str(uuid.uuid4())
        object_name = json_data.get('object_name', new_uuid)
        if object_name not in self.objects:
            if object_name != new_uuid:
                object_name = object_name + "_" + new_uuid

        object_type = json_data.get('object_type')
        object_attributes = json_data.get('object_attributes', {})
        color = object_attributes.get('object_color', (255, 255, 255))
        position = object_attributes.get('object_init', (0, 0))
        control = object_attributes.get('object_control', False)
        text = object_attributes.get('object_text', None)
        text_color = object_attributes.get('object_text_color', 'white')
        if object_type == 'circle':
            # object_size = radius
            object_size = object_attributes.get('object_size', 10)
            game_object = Circle(object_name, color, position, object_size)
        elif object_type == 'square':
            # object_size = length
            object_size = object_attributes.get('object_size', 10)
            game_object = Square(object_name, color, position, object_size)
        elif object_type == 'triangle':
            # object_size = length
            object_size = object_attributes.get('object_size', 10)
            game_object = Triangle(object_name, color, position, object_size)
        elif object_type == 'polygon':
            points = object_attributes.get('object_size', [(0, 0), (50, 0), (25, 50)])
            game_object = Polygon(object_name, color, position, points)
        elif object_type == 'line':
            # object_size = end_position 
            end_position = object_attributes.get('object_end', [100, 100])
            game_object = Line(object_name, color, position, end_position)
        elif object_type == 'ellipse':
            # object_size = height, width
            size = object_attributes.get('object_size', [10, 20])
            game_object = Ellipse(object_name, color, position, size)
        elif object_type == 'rectangle':
            # object_size = height, width
            size = object_attributes.get('object_size', [10, 20])
            game_object = Rectangle(object_name, color, position, size)
        else:
            return None

        # Enable controls if true
        if control:
            game_object.control = True

        # Assign text if it is set
        if text is not None:
            game_object.set_text(text, text_color)

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
        self.control = False
        self.selected = False
        self.text = None

    def draw(self, surface):
        if self.text is not None:
            self.text.position = self.position
            self.text.draw(surface)

    def move(self, dx, dy):
        self.position = (self.position[0] + dx, self.position[1] + dy)
        if self.text is not None:
            self.text.position = self.position

    def contains_point(self, point):
        # This should be implemented in each subclass
        raise NotImplementedError

    def set_text(self, text, color, font_name="couriernew", font_size=16):
        self.text = Text(self.name + "_text", color, self.position, text, font_name, font_size)

class Rectangle(GameObject):
    def __init__(self, name, color, position, size):
        super().__init__(name, color, position)
        self.size = size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1]))

    def contains_point(self, point):
        x, y = point
        return self.position[0] <= x <= self.position[0] + self.size[0] and self.position[1] <= y <= self.position[1] + self.size[1]

class Circle(GameObject):
    def __init__(self, name, color, position, radius):
        super().__init__(name, color, position)
        self.radius = radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)

    def contains_point(self, point):
        x, y = point
        dist = ((self.position[0] - x) ** 2 + (self.position[1] - y) ** 2) ** 0.5
        return dist <= self.radius

class Square(GameObject):
    def __init__(self, name, color, position, size):
        super().__init__(name, color, position)
        self.size = size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.position[0], self.position[1], self.size, self.size))

    def contains_point(self, point):
        x, y = point
        return self.position[0] <= x <= self.position[0] + self.size and self.position[1] <= y <= self.position[1] + self.size

class Triangle(GameObject):
    def __init__(self, name, color, position, size):
        super().__init__(name, color, position)
        self.size = size

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, [(self.position[0], self.position[1]), (self.position[0] + self.size / 2, self.position[1] - self.size), (self.position[0] + self.size, self.position[1])])

    def contains_point(self, point):
        x, y = point
        # Define the vertices of the triangle
        v1 = self.position
        v2 = (self.position[0] + self.size / 2, self.position[1] - self.size)
        v3 = (self.position[0] + self.size, self.position[1])

        # Calculate the area of the triangle
        area = 0.5 * (-v2[1]*v3[0] + v1[1]*(-v2[0] + v3[0]) + v1[0]*(v2[1] - v3[1]) + v2[0]*v3[1])

        # Calculate the s and t parameters
        s = 1/(2*area)*(v1[1]*v3[0] - v1[0]*v3[1] + (v3[1] - v1[1])*x + (v1[0] - v3[0])*y)
        t = 1/(2*area)*(v1[0]*v2[1] - v1[1]*v2[0] + (v1[1] - v2[1])*x + (v2[0] - v1[0])*y)

        return 0 <= s <= 1 and 0 <= t <= 1 and s + t <= 1

class Polygon(GameObject):
    def __init__(self, name, color, position, points):
        super().__init__(name, color, position)
        self.points = points

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.points)

    def contains_point(self, point):
        x, y = point
        n = len(self.points)
        inside = False

        p1x, p1y = self.points[0]
        for i in range(n + 1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

class Line(GameObject):
    def __init__(self, name, color, position, end_position):
        super().__init__(name, color, position)
        self.end_position = end_position

    def draw(self, surface):
        pygame.draw.line(surface, self.color, self.position, self.end_position)

    def contains_point(self, point):
        x, y = point
        x1, y1 = self.position
        x2, y2 = self.end_position

        # Calculate the distance from the point to the line
        dist = abs((y2 - y1)*x - (x2 - x1)*y + x2*y1 - y2*x1) / ((y2 - y1)**2 + (x2 - x1)**2)**0.5

        # Consider the point to be on the line if it's very close to it
        return dist < 5  # You can adjust this value as needed

class Ellipse(GameObject):
    def __init__(self, name, color, position, size):
        super().__init__(name, color, position)
        self.size = size

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1]))

    def contains_point(self, point):
        x, y = point
        dx = x - (self.position[0] + self.size[0] / 2)
        dy = y - (self.position[1] + self.size[1] / 2)
        return (dx ** 2 / (self.size[0] / 2) ** 2) + (dy ** 2 / (self.size[1] / 2) ** 2) <= 1

class Text(GameObject):
    def __init__(self, name, color, position, text, font_name='couriernew', font_size=16):
        super().__init__(name, color, position)
        self.text = text
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_color = color

    def draw(self, surface):
        text_surface = self.font.render(self.text, True, self.font_color)
        surface.blit(text_surface, self.position)

    def contains_point(self, point):
        # Text objects are not interactive, so they don't contain points
        return False

class Group(GameObject):
    def __init__(self, name, color, position):
        super().__init__(name, color, position)
        self.objects = []

    def draw(self, surface):
        for obj in self.objects:
            obj.draw(surface)

    def move(self, dx, dy):
        super().move(dx, dy)
        for obj in self.objects:
            obj.move(dx, dy)

    def contains_point(self, point):
        return any(obj.contains_point(point) for obj in self.objects)

    def add(self, obj):
        self.objects.append(obj)

    def remove(self, obj):
        self.objects.remove(obj)

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

game = GameApp(resolution=(1024, 768), fps=5)
game.create_object({
    "object_name": "myCircle",
    "object_type": "circle",
    "object_attributes": {
        "object_color": 'blue',
        "object_size":  20, 
        "object_init": [100, 100]
    }
})

# Pass the GameApp instance to APIApp
api = APIApp(game)

# Start the API in a separate thread
api_thread = Thread(target=api.run)
api_thread.start()

# Start the game
game.run()
