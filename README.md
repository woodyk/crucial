# Game Object Configuration

This document describes the JSON object used to configure game objects.

## JSON Object

The JSON object has the following structure:

```json
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
    "q": "strafe_left",
    "e": "strafe_right",
    "space": "jump"
   }
  },
  "object_color": "#0000FF",
  "object_size": 1,
  "object_state": "moveable",
  "object_init": {
   "x": 0,
   "y": 0,
   "z": 0
  },
  "object_action": "touch",
  "object_reaction": "explode"
 }
}
```

## Attributes

- `action`: The action to perform. create, read, update, delete
- `object_name`: The name of the game object. This should be unique.
- `object_type`: The type of the game object. This can be "sphere", "cube", "square", "circle", "triangle", or "rectangle".
- `object_attributes`: An object that specifies the attributes of the game object.

### Object Attributes

- `object_texture`: The path to the texture file for the game object.
- `object_rotation`: An object that specifies the rotation of the game object in degrees around the x, y, and z axes.
- `object_scale`: An object that specifies the scale of the game object along the x, y, and z axes.
- `object_physics`: An object that specifies the physics properties of the game object.
- `object_visibility`: A boolean that specifies whether the game object is visible.
- `object_parent`: The name of the parent game object.
- `object_children`: An array of names of the child game objects.
- `object_lighting`: An object that specifies the lighting properties of the game object.
- `object_animation`: The path to the animation file for the game object.
- `object_sound`: The path to the sound file for the game object.
- `object_control`: An object that specifies the control properties of the game object.
- `object_color`: The color of the game object in hexadecimal format.
- `object_size`: The size of the game object.
- `object_state`: The state of the game object.
- `object_init`: An object that specifies the initial position of the game object.
- `object_action`: The action that the game object performs.
- `object_reaction`: The reaction of the game object to an action.

### Lighting Attributes

- `light_type`: The type of light. This can be "ambient", "directional", "point", or "spotlight".
- `light_color`: An array of four numbers representing the red, green, blue, and alpha components of the color.
- `light_direction`: An array of three numbers representing the heading, pitch, and roll of the light. This property is only used for directional lights and spotlights.
- `light_position`: An array of three numbers representing the x, y, and z coordinates of the light. This property is only used for point lights and spotlights.

### Control Attributes

- `controller_type`: The type of controller to use. This can be "keyboard", "mouse", "joystick", etc.
- `controller_inputs`: A dictionary that maps the inputs of the controller to actions. The keys of the dictionary are the names of the inputs, and the values are the names of the actions.

#### Actions

The following actions are currently supported:

- `up`: Move the game object up.
- `down`: Move the game object down.
- `left`: Move the game object left.
- `right`: Move the game object right.
- `strafe_left`: Move the game object left without changing its orientation.
- `strafe_right`: Move the game object right without changing its orientation.
- `jump`: Make the game object jump.
- `shoot`: Make the game object shoot.
- `explode`: Make the game object explode.
- `interact`: Trigger an objects object_raction attribute

Please note that the actual effect of each action depends on the specific game and game object. For example, in a 2D game, the `up` action might move the game object up on the screen, while in a 3D game, it might move the game object forward.

#### Example

Here's an example of how you might define the `object_control` attribute in the JSON object:

```json
"object_control": {
 "controller_type": "keyboard",
 "controller_inputs": {
  "w": "up",
  "a": "left",
  "s": "down",
  "d": "right",
  "q": "strafe_left",
  "e": "strafe_right",
  "space": "jump"
 }
}
```

