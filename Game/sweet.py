import pygame as pg
from pygame.locals import K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN, K_RIGHT, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_LALT, K_LCTRL, K_LSHIFT, K_ESCAPE, K_TAB, K_b, K_c, K_e, K_f, K_g, K_h, K_i, K_j, K_l, K_m, K_n, K_o, K_p, K_q, K_r, K_t, K_u, K_v, K_x, K_y, K_z
import math as m
import numpy as np
from typing import TypeVar, NewType, Union, Tuple
from enum import Enum

pg.init()

# fix ret surface
#test a lot with collisions, calc and transition functions.
# fix fucking camera add needing a zero for the object argument
# Fix naming, review code meticulously

# Entity instances identifier
_global_id: int = 0

# Mathematical types
number = TypeVar("number", int, float)
ndlist = TypeVar("ndlist", int, float, np.ndarray, tuple)
point = Tuple[number, number]

# Enum types
search = NewType("search", int)
mask = NewType("mask", int)
alignment = NewType("alignment", int)
interpolation = NewType("interpolation", int)
masktype = NewType("masktype", int)
searchtype = NewType("searchtype", int)
alignment = NewType("alignment", int)

# Tool types
entity = NewType("entity", object)
target = TypeVar("target", object, str)
groupname = TypeVar("groupname", str, bool)
# imagelist = NewType("imagelist", list[list[str, str, bool]])

class enums(Enum):
    # Binary search index usage
    CLASS_ID = 1

    # False value that is not integer type
    FALSE = "_false"

    # Mask types
    CIRCLE = 1
    POLYGON = 2
    POINT = 3
    BOX = 4
    STROKE = 5

    # Universal group name
    UNIVERSAL = "_universal"

    # Transition types
    EASE_QUADRATIC = 1
    EASE_IN_QUADRATIC = 2
    EASE_OUT_QUADRATIC = 3
    EASE_CUBIC = 4
    EASE_IN_CUBIC = 5
    EASE_OUT_CUBIC = 6
    EASE_QUARTIC = 7
    EASE_IN_QUARTIC = 8
    EASE_OUT_QUARTIC = 9
    GLANCE = 10

    # Image offset types
    CENTER = "_center"
    CENTER_TOP = "_center_top"
    CENTER_LEFT = "_center_left"
    CENTER_RIGHT = "_center_right"
    CENTER_BOTTOM = "_center_bottom"
    TOP_LEFT = "_top_left"
    TOP_RIGHT = "_top_right"
    BOTTOM_LEFT = "_bottom_left"
    BOTTOM_RIGHT = "_bottom_right"
    # Idea: turn this above into tuples of their pos, then multiply their values with the size of the image

FPS: int = 60

M_LEFT: int = 0
M_MIDDLE: int = 1
M_RIGHT: int = 2

# Group math operations into a single class
class calc:
    def clamp(x: ndlist, a: number, b: number) -> ndlist:
        x = np.array(x)
        return np.clip(x, a, b)

    def sign(x: ndlist) -> ndlist:
        x = np.array(x)
        return np.sign(x)

    def distance(a: ndlist, b: ndlist) -> float:
        a = np.array(a)
        b = np.array(b)
        return np.linalg.norm(a - b)
    
    def dot(a: ndlist, b: ndlist) -> float:
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b)

    def normalize(a, b):
        a = np.array(a)
        b = np.array(b)
        c = b - a
        return c / np.linalg.norm(c)

    def determinant(space: np.ndarray) -> float:
        return np.linalg.det(space)

    def cross_2d(a: point, b: point) -> float:
        linspace: np.ndarray = np.vstack((a, b))
        return np.linalg.det(linspace)

    def angle(a: point, b: point) -> float:
        a = np.array((a[0], -a[1]))
        b = np.array((b[0], -b[1]))
        centered_vector: np.ndarray = b - a
        magnitude: number = calc.distance(a, b)
        i_vector: np.ndarray = np.array([1, 0])

        if magnitude == 0:
            return 0

        if b[1] > a[1]:
            return np.arccos(np.dot(centered_vector, i_vector) / magnitude)
    
        return 2 * m.pi - np.arccos(np.dot(centered_vector, i_vector) / magnitude)

class transition:
    def unlerp(a: ndlist, b: ndlist, value: number, clamped=True) -> float:
        a = np.array(a)
        b = np.array(b)
        if np.any(a == b):
            raise ValueError("B = A?")
        
        if clamped:
            return calc.clamp((value - a) / (b - a), 0, 1)
        
        return (value - a) / (b - a)

    def lerp(a: ndlist, b: ndlist, t: float, clamped=True) -> np.ndarray:
        a = np.array(a)
        b = np.array(b)
        if clamped:
            t = calc.clamp(t, 0, 1)
    
        return a + (b - a) * t
    
    def ease(transition_type: interpolation, t: float) -> float:
        t = calc.clamp(t, 0, 1)
        if transition_type == enums.EASE_QUADRATIC:
            return 2 * t * t if t < 0.5 else 1 - 2 * (t - 1) ** 2
        elif transition_type == enums.EASE_IN_QUADRATIC:
            return t * t
        elif transition_type == enums.EASE_OUT_QUADRATIC:
            return 1 - (t - 1) ** 2
        elif transition_type == enums.EASE_CUBIC:
            return 4 * t * t * t if t < 0.5 else 1 + 4 * (t - 1) ** 3
        elif transition_type == enums.EASE_IN_CUBIC:
            return t * t * t
        elif transition_type == enums.EASE_OUT_CUBIC:
            return 1 + (t - 1) ** 3
        elif transition_type == enums.EASE_QUARTIC:
            return 8 * t * t * t * t if t < 0.5 else 1 - 8 * (t - 1) ** 4
        elif transition_type == enums.EASE_IN_QUARTIC:
            return t * t * t * 4
        elif transition_type == enums.EASE_OUT_QUARTIC:
            return 1 - (t - 1) ** 4
        elif transition_type == enums.GLANCE:
            return 1 / 2 - 2 * (t - 1 / 2) ** 2 if t < 0.5 else 1 / 2 + 2 * (t - 1 / 2) ** 2

class const:
    pi: float = 3.1415926535

class window:
    width: int = 800
    height: int = 600
    title: str = "untitled"

    def set_size(size: tuple) -> None:
        window.width = size[0]
        window.height = size[1]
        camera.set_cam_scale("main", (window.width, window.height))

    def set_title(title: str) -> None:
        window.title = title

    def set_background(col: tuple) -> None:
        color.__setattr__("_background", col)

    def build() -> None:
        window.display = pg.display.set_mode((window.width, window.height), pg.DOUBLEBUF)
        pg.display.set_caption(window.title)

        window.buffer = pg.surface.Surface((window.width, window.height))

class image:
    stock: dict = {}

    def get(key: str) -> pg.Surface:
        return image.stock[key]

    def archive(images) -> None:
        for img in images:
            image.stock[img[1]] = pg.image.load(img[0])
            if img[2]:
                image.stock[img[1]].convert_alpha()
            else:
                image.stock[img[1]].convert()

class sound:
    pass
    # paths = [
    #     ["audios\\effect.m4a", "kratos"],
    #     ["audios\\song.mp3", "internet moms"],
    # ]
    # sound = {}
    # for i in range(len(paths)):
    #     key = paths[i][1]
    #     path = paths[i][0]
    #     sound[key] = pg.mixer.music.load(path)

class color:
    white: tuple = (255, 255, 255)
    black: tuple = (0, 0, 0)
    pure_red: tuple = (255, 0, 0)
    pure_green: tuple = (0, 255, 0)
    pure_blue: tuple = (0, 0, 255)
    cyan: tuple = (0, 255, 255)
    magenta: tuple = (255, 0, 255)
    yellow: tuple = (255, 255, 0)
    ultramarine_blue: tuple = (0, 85, 255)
    dead_blue: tuple = (48, 73, 122)
    spring_green: tuple = (0, 255, 157)
    dark_gray: tuple = (70, 70, 70)
    gray: tuple = (127, 127, 127)
    light_gray: tuple = (190, 190, 190)
    orange: tuple = (255, 127, 0)
    purple: tuple = (127, 0, 255)
    pastel_purple: tuple = (200, 145, 255)
    pastel_green: tuple = (173, 255, 184)
    pastel_blue: tuple = (163, 163, 255)
    pastel_yellow: tuple = (255, 255, 150)
    pastel_red: tuple = (255, 161, 161)
    pastel_cyan: tuple = (161, 227, 255)
    pastel_orange: tuple = (255, 197, 150)
    pastel_magenta: tuple = (255, 153, 226)
    brown: tuple = (102, 53, 12)
    sky_blue: tuple = (66, 186, 255)

    _background: tuple = (0, 0, 0)

    def set_background(rgb: tuple) -> None:
        color._background = rgb

class keyboard:
    _current_keys: list = pg.key.get_pressed()
    _used_keys: list = [K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN, K_RIGHT, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_LALT, K_LCTRL, K_LSHIFT, K_ESCAPE, K_TAB]
    _used_keys.sort()
    _key_pressing: dict = {}
    _key_pressed: dict = {}
    _key_released: dict = {}
    type_key: dict = {}
    type_key_hold: dict = {}
    for used_key in _used_keys:
        _key_pressing[used_key] = False
        _key_pressed[used_key] = False
        _key_released[used_key] = False

    _alphabet: list = [K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_l, K_m, K_n, K_o, K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z]
    _numeric: list = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]

    def add_extra_keys(keys: list) -> None:
        for key in keys:
            index: int = binary_search(keyboard._used_keys, len(keyboard._used_keys), 0, key)
            if index >= 0:
                keyboard._used_keys.insert(index, key)
                keyboard._key_pressing[key] = False
                keyboard._key_pressed[key] = False
                keyboard._key_released[key] = False

    def add_alphabet_keys() -> None:
        keyboard.add_extra_keys(keyboard._alphabet)

    def add_numeric_keys() -> None:
        keyboard.add_extra_keys(keyboard._numeric)

    def pressing(key: int) -> bool:
        return keyboard._key_pressing[key]
        
    def pressed(key: int) -> bool:
        return keyboard._key_pressed[key]

    def released(key: int) -> bool:
        return keyboard._key_released[key]

    def _update() -> None:
        for key in keyboard._used_keys:
            event_key: bool = keyboard._current_keys[key]

            if event_key and not keyboard._key_pressing[key]:
                keyboard._key_pressed[key] = True
            else:
                keyboard._key_pressed[key] = False
                
            if not event_key and keyboard._key_pressing[key]:
                keyboard._key_released[key] = True
            else:
                keyboard._key_released[key] = False

            keyboard._key_pressing[key] = event_key

class rat:
    _current_button: list = pg.mouse.get_pressed()
    _button_pressing: list = [False] * 3
    _button_pressed: list = [False] * 3
    _button_released: list = [False] * 3
    x: number = 0
    y: number = 0
    roll_x: number = 0
    roll_y: number = 0

    def pressing(key: int) -> bool:
        return rat._button_pressing[key]

    def pressed(key: int) -> bool:
        return rat._button_pressed[key]

    def released(key: int) -> bool:
        return rat._button_released[key]

    def _update() -> None:
        for button in range(3):
            event_button: bool = rat._current_button[button]
            if event_button and not rat._button_pressing[button]:
                rat._button_pressed[button] = True
            else:
                rat._button_pressed[button] = False
                
            if not event_button and rat._button_pressing[button]:
                rat._button_released[button] = True
            else:
                rat._button_released[button] = False
            
            rat._button_pressing[button] = event_button

class Mask:
    def __init__(self, mask_type: masktype, information: list) -> None:
        if mask_type == enums.FALSE:
            return
        
        self.mask_type: masktype = mask_type
        self.bound_box: list = []
        self.adapt_mask(information, mask_type)

    def adapt_mask(self, information: list, mask_type=enums.FALSE) -> None:
        self.information = information
        
        if not mask_type == enums.FALSE:
            mask_type = self.mask_type

        if self.mask_type == enums.CIRCLE:
            self.bound_box = [
                (information[0] - information[2], information[1] - information[2]),
                (information[0] + information[2], information[1] - information[2]),
                (information[0] + information[2], information[1] + information[2]),
                (information[0] - information[2], information[1] + information[2]),
            ]

        elif self.mask_type == enums.POLYGON:
            x_points: list = [information[i][0] for i in range(len(information))]
            y_points: list = [information[i][1] for i in range(len(information))]
            self.bound_box = [
                (min(x_points), min(y_points)),
                (max(x_points), min(y_points)),
                (max(x_points), max(y_points)),
                (min(x_points), max(y_points)),
            ]

        elif self.mask_type == enums.BOX:
            self.bound_box = information
        
        elif self.mask_type == enums.POINT:
            self.bound_box = [
                information,
                information,
                information,
                information,
                ]
            
        elif self.mask_type == enums.STROKE:
            self.bound_box = [
                (min(information[0][0], information[1][0]) - information[2], min(information[0][1], information[1][1]) - information[2]),
                (max(information[0][0], information[1][0]) + information[2], min(information[0][1], information[1][1]) - information[2]),
                (max(information[0][0], information[1][0]) + information[2], max(information[0][1], information[1][1]) + information[2]),
                (min(information[0][0], information[1][0]) - information[2], max(information[0][1], information[1][1]) + information[2]),
            ]

class camera:
    _current_camera: str = "main"
    view: dict = {}

    def __init__(self) -> None:
        self.new_cam("main", (0, 0), (window.height, window.width), 0)

    class cam:
        def __init__(self, pos: point, scale: point, angle: number) -> None:
            self.x: number = pos[0]
            self.y: number = pos[1]
            self.width: number = scale[0]
            self.height: number = scale[1]
            self.angle: number = angle

    def new_cam(self, identifier: str, pos: point, scale: point, angle: number) -> None:
        camera.view[identifier] = camera.cam(pos, scale, angle)

    def set_cam_pos(identifier: str, pos: point) -> None:
        camera.view[identifier].x = pos[0]
        camera.view[identifier].y = pos[1]

    def set_cam_scale(identifier: str, scale: point) -> None:
        camera.view[identifier].width = scale[0]
        camera.view[identifier].height = scale[1]

    def set_cam_angle(identifier: str, angle: number) -> None:
        camera.view[identifier].angle = angle

    def get_cam_pos(identifier: str) -> point:
        return (camera.view[identifier].x, camera.view[identifier].y)
        
    def get_cam_scale(identifier: str) -> point:
        return (camera.view[identifier].width, camera.view[identifier].height)

    def get_cam_angle(identifier: str) -> number:
        return camera.view[identifier].angle

    def set_current_cam(cam: str) -> None:
        camera._current_camera = cam

    def get_cam(identifier: str) -> entity:
        return camera.view[identifier]

camera()

class Entity:
    def __init__(self, name: str, pos: tuple, sprite: str=False, mask: Mask=False, depth: int=enums.FALSE, universal: bool=False, show: bool=True, has_draw: bool=False, has_tick: bool=False) -> None:
        init_object(self, name, pos, depth, universal, sprite=sprite, mask=mask, show=show, has_draw=has_draw, has_tick=has_tick)
    
    def __str__(self) -> str:
        return f"{self.name_id} | id: {self.class_id}"

    def draw(self) -> None:
        pass

    def tick(self) -> None:
        pass

class layer:
    content_layers: list = []
    content_layers_len: int = 0
    layers: dict = {}
    layers_len: dict = {}
    
    def build() -> None:
        for current_layer in layer.content_layers:
            for sub_layer in layer.layers[current_layer]:
                if sub_layer.show:
                    sub_layer.draw()
        


    def add_to_layer(instance: entity) -> None:
        layer_proximity: int = instance.depth
        object_id: int = instance.class_id
        instance.layer_location = layer_proximity

        if layer.layers.get(layer_proximity) == None:
            layer.layers[layer_proximity] = [instance]
            layer.layers_len[layer_proximity] = 1
        else:
            layer_len = len(layer.layers[layer_proximity])
            index: int = binary_search(layer.layers[layer_proximity], layer_len, 0, object_id, enums.CLASS_ID)
            layer.layers[layer_proximity].insert(index, instance)
            layer.layers_len[layer_proximity] += 1


        c_layers_len: int = len(layer.content_layers)
        
        if c_layers_len == 0:
            layer.content_layers.append(layer_proximity)
            layer.content_layers_len += 1
            return
        
        index: int = binary_search(layer.content_layers, layer.content_layers_len, 0, layer_proximity)
        if index < 0:
            return

        layer.content_layers.insert(index, layer_proximity)
        layer.content_layers_len += 1

    def remove_from_layer(instance: entity) -> None:
        layer_proximity: int = instance.layer_location
        object_id: int = instance.class_id

        if layer.layers_len[layer_proximity] == 1:
            layer.layers.pop(layer_proximity)
            
            index: int = binary_search(layer.content_layers, layer.content_layers_len, 0, layer_proximity)
            layer.content_layers.pop(-index - 1)
            layer.content_layers_len -= 1
            return
                
        layer_len: int = len(layer.layers[layer_proximity])
        index: int = binary_search(layer.layers[layer_proximity], layer_len, 0, object_id, enums.CLASS_ID)
        layer.layers[layer_proximity].pop(-index - 1)
        layer.layers_len[layer_proximity] -= 1

    def layer_update(instance: entity) -> None:
        layer.remove_from_layer(instance)
        layer.add_to_layer(instance)

class _tick:
    executes: list = []
    executes_len: int = 0

    def tick() -> None:
        for execute in _tick.executes:
            execute.tick()
    
    def add_tick(instance: entity) -> None:
        index: int = binary_search(_tick.executes, _tick.executes_len, 0, instance.class_id, enums.CLASS_ID)
        if index < 0:
            return
            
        _tick.executes.insert(index, instance)
        _tick.executes_len += 1

    def remove_tick(instance: entity) -> None:
        index: int = binary_search(_tick.executes, _tick.executes_len, 0, instance.class_id, enums.CLASS_ID)
        _tick.executes.pop(-index - 1)
        _tick.executes_len -= 1

class group:
    groups: dict = {enums.UNIVERSAL: []}
    groups_len: dict = {enums.UNIVERSAL: 0}

    def get_groups(instance: entity, group_name: groupname=False) -> list:
        # todo: Test for pointers, classes and instances
        if instance.__class__.__name__ == "type":
            if not group_name:
                return [instance.__name__]
            return 0
        if not group_name:
            return instance.groups_in
        for i in range(len(instance.groups_in)):
            if instance.groups_in[i] == group_name:
                return i
        return enums.FALSE
    
    def make_group(group_name: groupname) -> None:
        group.groups[group_name] = []
        group.groups_len[group_name] = 0

    def add_to_group(instance: entity, group_name: groupname=False) -> None:
        if group_name:
            if not group_name in instance.groups_in:
                instance.groups_in.append(group_name)
        else:
            group_name = group.get_groups(instance)[0]
        
        index: int = binary_search(group.groups[group_name], group.groups_len[group_name], 0, instance.class_id, enums.CLASS_ID)
        if index < 0:
            return
        
        group.groups[group_name].insert(index, instance)
        group.groups_len[group_name] += 1

    def remove_from_group(instance: entity, group_name: groupname=False) -> None:
        if group_name:
            for i in range(len(instance.groups_in)):
                if instance.groups_in[i] == group_name:
                    instance.groups_in.pop(i)
        else:
            group_name = group.get_groups(instance)[0]
        
        group_size: int = len(group.groups[group_name])
        if group_size > 1:
            index: int = binary_search(group.groups[group_name], group_size, 0, instance.class_id, enums.CLASS_ID)
            group.groups[group_name].pop(-index - 1)
            group.groups_len[group_name] -= 1
            return
        
        group.groups.pop(group_name)
        group.groups_len.pop(group_name)

    def move_to_group(instance: entity, group_in: str, group_to: str) -> None:
        group.remove_from_group(instance, group_in)
        group.add_to_group(instance, group_to)

class spatial_map:
    space: dict = {enums.UNIVERSAL: {}}
    space_len: dict = {enums.UNIVERSAL: {}}
    space_grid: dict = {enums.UNIVERSAL: 10}
    # def __init__(self, universal_grid):

    def add_group_map(group_name: groupname, grid_size: number) -> None:
        spatial_map.space[group_name] = {}

        spatial_map.space_grid[group_name] = grid_size
        spatial_map.space_len[group_name] = {}

        for element in group.groups[group_name]:
            spatial_map.add_object_grid(element, group_name)

    def remove_group_map(group_name: groupname) -> None:
        if spatial_map.space_grid.get(group_name):
            spatial_map.space.pop(group_name)
            spatial_map.space_grid.pop(group_name)
        
    def gridify(pos: point, grid_size: int, array_format: bool=False) -> Union[str, tuple]:
        if array_format:
           return (m.floor(pos[0] / grid_size), m.floor(pos[1] / grid_size))

        return f"{m.floor(pos[0] / grid_size)}.{m.floor(pos[1] / grid_size)}"

    def add_object_grid(instance: entity, group_name: groupname) -> None:
        if instance.mask == False:
            return

        # Cannot merge both tests because the following condition raises an error if the mask has not been defined.
        if instance.mask.mask_type == enums.FALSE:
            return
        
        bound_box: list = instance.mask.bound_box
        grid_size: number = spatial_map.space_grid[group_name]
        min_grid: point = spatial_map.gridify((bound_box[0][0] + instance.x, bound_box[0][1] + instance.y), grid_size, True)
        max_grid: point = spatial_map.gridify((bound_box[2][0] + instance.x, bound_box[2][1] + instance.y), grid_size, True)
        horizontal_intersection: int = max_grid[0] - min_grid[0]
        vertical_intersection: int = max_grid[1] - min_grid[1]

        instance.spatial_place[group_name] = []

        for sub_location_y in range(vertical_intersection + 1):
            for sub_location_x in range(horizontal_intersection + 1):
                sub_grid: point = (min_grid[0] + sub_location_x, min_grid[1] + sub_location_y)
                location: str = f"{sub_grid[0]}.{sub_grid[1]}"

                if spatial_map.space[group_name].get(location) == None:
                    spatial_map.space[group_name][location] = [instance]
                    spatial_map.space_len[group_name][location] = 1
                    continue
                index: int = binary_search(spatial_map.space[group_name][location], spatial_map.space_len[group_name][location], 0, instance.class_id, enums.CLASS_ID)
                if index >= 0:
                    spatial_map.space[group_name][location].insert(index, instance)
                    spatial_map.space_len[group_name][location] += 1
                
                instance.spatial_place[group_name].append(location)

    def remove_object_grid(instance: entity, group_name: groupname) -> None:
        if instance.spatial_place.get(group_name) == None:
            return
        
        for location in instance.spatial_place[group_name]:
            if spatial_map.space_len[group_name][location] < 2:
                spatial_map.space[group_name].pop(location)
                spatial_map.space_len[group_name].pop(location)
                continue

            index: int = binary_search(spatial_map.space[group_name][location], spatial_map.space_len[group_name][location], 0, instance.class_id, enums.CLASS_ID)
            spatial_map.space[group_name][location].pop(-index - 1)
            spatial_map.space_len[group_name][location] -= 1

        instance.spatial_place.pop(group_name)

    def update_object_grid(instance: entity, group_name: groupname) -> None:
        spatial_map.remove_object_grid(instance, group_name)
        spatial_map.add_object_grid(instance, group_name)

def set_spatial_size(value: number) -> None:
    spatial_map.space_grid[enums.UNIVERSAL] = value

def collision_with(object: entity, collisor: groupname, all: bool=False, offset: point=(0, 0), sort_list: bool=False) -> list:
    object_pos: point = (object.x + offset[0], object.y + offset[1])
    if not object.mask:
        return [False]

    if not type(collisor) == type(""):
        collisor = group.get_groups(collisor)[0]

    success: list = []

    collisor_space: dict = spatial_map.space[collisor]
    min_grid: point = spatial_map.gridify((object_pos[0] + object.mask.bound_box[0][0], object_pos[1] + object.mask.bound_box[0][1]), spatial_map.space_grid[collisor], True)
    max_grid: point = spatial_map.gridify((object_pos[0] + object.mask.bound_box[2][0], object_pos[1] + object.mask.bound_box[2][1]), spatial_map.space_grid[collisor], True)
    horizontal_intersection: int = max_grid[0] - min_grid[0]
    vertical_intersection: int = max_grid[1] - min_grid[1]

    for sub_location_y in range(vertical_intersection + 1):
        for sub_location_x in range(horizontal_intersection + 1):
            neighbour_key: str = f"{(min_grid[0] + sub_location_x)}.{(min_grid[1] + sub_location_y)}"

            if collisor_space.get(neighbour_key) == None:
                continue

            collisor_location: list = collisor_space[neighbour_key]

            for element in collisor_location:
                if not element.mask:
                    continue
                
                if collision_detection((object.mask.mask_type, element.mask.mask_type), (object.mask.information, element.mask.information), (object_pos, (element.x, element.y))):
                
                    if not all:
                        return [element]
                    
                    if not success:
                        success = [element]
                    else:
                        if sort_list:
                            index: int = binary_search(success, len(success), 0, element.class_id, enums.CLASS_ID)

                            if index >= 0:
                                success.insert(index, element)
                        else:
                            success.append(element)

    return success

def collision_detection(types: list, information: list, positions: list) -> bool:
    if (types[0] == enums.CIRCLE and types[1] == enums.POLYGON) or (types[0] == enums.POLYGON and types[1] == enums.CIRCLE):
        if types[0] == enums.POLYGON:
            information = [information[1], information[0]]
            positions = [positions[1], positions[0]]

        inside: bool = False
        for i in range(4):
            #todo: enable more than quadrilateral collision

            i_end: int = (i + 1) % 4
            vertex_i: tuple = (information[1][i][0] + positions[1][0], information[1][i][1] + positions[1][1])
            vertex_i_end: tuple = (information[1][i_end][0] + positions[1][0], information[1][i_end][1] + positions[1][1])

            vertex: tuple = [information[0][0] + positions[0][0], information[0][1] + positions[0][1], information[0][2]]

            if vertex_i[1] < vertex[1] and vertex[1] <= vertex_i_end[1]:
                if vertex_i[0] > vertex[0] and vertex_i_end[0] > vertex[0]:
                    inside = not inside
                elif (vertex[0] - vertex_i[0]) * (vertex[1] - vertex_i_end[1]) - (vertex[1] - vertex_i[1]) * (vertex[0] - vertex_i_end[0]) > 0:
                    inside = not inside
            elif vertex_i_end[1] < vertex[1] and vertex[1] <= vertex_i[1]:
                if vertex_i[0] > vertex[0] and vertex_i_end[0] > vertex[0]:
                    inside = not inside
                elif (vertex[0] - vertex_i[0]) * (vertex[1] - vertex_i_end[1]) - (vertex[1] - vertex_i[1]) * (vertex[0] - vertex_i_end[0]) < 0:
                    inside = not inside

            prod: tuple = (vertex_i[0] * vertex_i_end[0], vertex_i[1] * vertex_i_end[1])
            i_squared: tuple = (vertex_i[0] ** 2, vertex_i[1] ** 2)
            i_end_squared: tuple = (vertex_i_end[0] ** 2, vertex_i_end[1] ** 2)
            difference: tuple = (vertex_i[0] - vertex_i_end[0], vertex_i[1] - vertex_i_end[1])

            quotient: number = i_squared[0] - prod[0] - difference[0] * vertex[0] + i_squared[1] - prod[1] - difference[1] * vertex[1]
            divisor: number = i_squared[0] + i_end_squared[0] + i_squared[1] + i_end_squared[1] - 2 * (prod[0] + prod[1])
            nearest_interpolation: float = quotient / divisor
            bounded_nearest_interpolation: number = min(1, max(0, nearest_interpolation))

            bounded_nearest_vertex: tuple = (vertex_i[0] + bounded_nearest_interpolation * (vertex_i_end[0] - vertex_i[0]), vertex_i[1] + bounded_nearest_interpolation * (vertex_i_end[1] - vertex_i[1]))

            if (bounded_nearest_vertex[0] - vertex[0]) ** 2 + (bounded_nearest_vertex[1] - vertex[1]) ** 2 <= vertex[2] ** 2:
                return True

        if inside:
            return True
        
    elif types[0] == enums.POLYGON and types[1] == enums.POLYGON:
        #--todo: IS ASSUMING IT IS CONVEX AND IS A QUADRILATERAL
        for axis_index in range(8):
            axis_index_next: int = (axis_index + 1) % 4

            if axis_index < 4:
                axis_points: list = [
                    (information[0][axis_index][0] + positions[0][0], information[0][axis_index][1] + positions[0][1]),
                    (information[0][axis_index_next][0] + positions[0][0], information[0][axis_index_next][1] + positions[0][1]),
                ]
            else:
                axis_points: list = [
                    (information[1][axis_index - 4][0] + positions[1][0], information[1][axis_index - 4][1] + positions[1][1]),
                    (information[1][axis_index_next][0] + positions[1][0], information[1][axis_index_next][1] + positions[1][1]),
                ]
            
            point_side: list = [0, 0]
            for point_index in range(8):
                if point_index < 4:
                    point: tuple = (information[0][point_index][0] + positions[0][0], information[0][point_index][1] + positions[0][1])
                    point_side[0] += calc.sign(calc.cross_2d((point[0] - axis_points[1][0], point[1] - axis_points[1][1]), (axis_points[0][0] - axis_points[1][0],axis_points[0][1]  - axis_points[1][1])))
                else:
                    point: tuple = (information[1][point_index - 4][0] + positions[1][0], information[1][point_index - 4][1] + positions[1][1])
                    point_side[1] += calc.sign(calc.cross_2d((point[0] - axis_points[1][0], point[1] - axis_points[1][1]), (axis_points[0][0] - axis_points[1][0],axis_points[0][1]  - axis_points[1][1])))
            
                if point_index == 7:
                    if (point_side[0] == -2 and point_side[1] == 4) or (point_side[1] == -2 and point_side[0] == 4) or (point_side[0] == 2 and point_side[1] == -4) or (point_side[1] == 2 and point_side[0] == -4):
                        return False
        return True
    
    elif types[0] == enums.CIRCLE and types[1] == enums.CIRCLE:
        vertex_a: tuple = (information[0][0] + positions[0][0], information[0][1] + positions[0][1])
        vertex_b: tuple = (information[1][0] + positions[1][0], information[1][1] + positions[1][1])
        if (vertex_a[0] - vertex_b[0]) ** 2 + (vertex_a[1] - vertex_b[1]) ** 2 < (information[0][2] + information[1][2]) ** 2:
            return True
        return False
    
    elif (types[0] == enums.CIRCLE and types[1] == enums.BOX) or (types[0] == enums.BOX and types[1] == enums.CIRCLE):
        if types[0] == enums.BOX:
            information = [information[1], information[0]]
            positions = [positions[1], positions[0]]

        inside: bool = False
        for i in range(4):
            #todo: enable more than quadrilateral collision

            i_end: int = (i + 1) % 4
            vertex_i: tuple = (information[1][i][0] + positions[1][0], information[1][i][1] + positions[1][1])
            vertex_i_end: tuple = (information[1][i_end][0] + positions[1][0], information[1][i_end][1] + positions[1][1])

            vertex: list = [information[0][0] + positions[0][0], information[0][1] + positions[0][1], information[0][2]]

            if vertex_i[1] < vertex[1] and vertex[1] <= vertex_i_end[1]:
                if vertex_i[0] > vertex[0] and vertex_i_end[0] > vertex[0]:
                    inside = not inside
                elif (vertex[0] - vertex_i[0]) * (vertex[1] - vertex_i_end[1]) - (vertex[1] - vertex_i[1]) * (vertex[0] - vertex_i_end[0]) > 0:
                    inside = not inside
            elif vertex_i_end[1] < vertex[1] and vertex[1] <= vertex_i[1]:
                if vertex_i[0] > vertex[0] and vertex_i_end[0] > vertex[0]:
                    inside = not inside
                elif (vertex[0] - vertex_i[0]) * (vertex[1] - vertex_i_end[1]) - (vertex[1] - vertex_i[1]) * (vertex[0] - vertex_i_end[0]) < 0:
                    inside = not inside

            prod: tuple = (vertex_i[0] * vertex_i_end[0], vertex_i[1] * vertex_i_end[1])
            i_squared: tuple = (vertex_i[0] ** 2, vertex_i[1] ** 2)
            i_end_squared: tuple = (vertex_i_end[0] ** 2, vertex_i_end[1] ** 2)
            difference: tuple = (vertex_i[0] - vertex_i_end[0], vertex_i[1] - vertex_i_end[1])

            quotient: number = i_squared[0] - prod[0] - difference[0] * vertex[0] + i_squared[1] - prod[1] - difference[1] * vertex[1]
            divisor: number = i_squared[0] + i_end_squared[0] + i_squared[1] + i_end_squared[1] - 2 * (prod[0] + prod[1])
            nearest_interpolation: float = quotient / divisor
            bounded_nearest_interpolation: number = min(1, max(0, nearest_interpolation))

            bounded_nearest_vertex: number = (vertex_i[0] + bounded_nearest_interpolation * (vertex_i_end[0] - vertex_i[0]), vertex_i[1] + bounded_nearest_interpolation * (vertex_i_end[1] - vertex_i[1]))

            if (bounded_nearest_vertex[0] - vertex[0]) ** 2 + (bounded_nearest_vertex[1] - vertex[1]) ** 2 < vertex[2] ** 2:
                return True

        if inside:
            return True

    elif (types[0] == enums.POINT and types[1] == enums.BOX) or (types[0] == enums.BOX and types[1] == enums.POINT):
        if types[0] == enums.BOX:
            information = [information[1], information[0]]
            positions = [positions[1], positions[0]]

        if positions[1][0] + information[1][0][0] <= positions[0][0] + information[0][0] <= positions[1][0] + information[1][2][0]:
            if positions[1][1] + information[1][0][1] <= positions[0][1] + information[0][1] <= positions[1][1] + information[1][2][1]:
                return True
            
    elif (types[0] == enums.POINT and types[1] == enums.STROKE) or (types[0] == enums.STROKE and types[1] == enums.POINT):
        if types[0] == enums.STROKE:
            information = [information[1], information[0]]
            positions = [positions[1], positions[0]]
        
        vertex: tuple = (positions[0][0] + information[0][0], positions[0][1] + information[0][1])

        stroke_start: np.ndarray = np.array([positions[1][0] + information[1][0][0], positions[1][1] + information[1][0][1]])
        stroke_end: np.ndarray = np.array([positions[1][0] + information[1][1][0], positions[1][1] + information[1][1][1]])

        path_len_squared: number = (stroke_start[0] - stroke_end[0]) ** 2 + (stroke_start[1] - stroke_end[1]) ** 2 + 0.01

        closest_t: number = calc.dot((vertex[0] - stroke_start[0], vertex[1] - stroke_start[1]), (stroke_end[0] - stroke_start[0], stroke_end[1] - stroke_start[1])) / path_len_squared

        closest_vertex: tuple = transition.lerp(stroke_start, stroke_end, closest_t)

        if (vertex[0] - closest_vertex[0]) ** 2 + (vertex[1] - closest_vertex[1]) ** 2 <= information[1][2] ** 2:
            return True
    
    return False

def get_class(object) -> str:
    #todo: Test for pointers, classes and instances
    if object.__class__.__name__ == "type":
        object.__name__
    return object.groups_in[0]

def rotate_array(array: list, angle: number) -> list:
    return (array[0] * m.cos(angle * m.pi / 180) + array[1] * m.sin(angle * m.pi / 180),
            -array[0] * m.sin(angle * m.pi / 180) + array[1] * m.cos(angle * m.pi / 180))

def image_transform(image: pg.Surface, surface: pg.Surface, position: point, scale: tuple = False, angle: number = False, alpha: number = enums.FALSE, color: tuple=False, origin: point = (0, 0), ret_surf: bool = False) -> pg.Surface:
    cam: camera.cam = camera.view[camera._current_camera]

    width: number = image.get_width()
    height: number = image.get_height()

    if color:
        image = image.copy()

        end_color: tuple = (min(255, color[0]), min(255, color[1]), min(255, color[2]))

        color_surf: pg.Surface = pg.surface.Surface((width, height)).convert_alpha()
        color_surf.fill((end_color[0], end_color[1], end_color[2]))
        image.blit(color_surf, (0,0), special_flags=pg.BLEND_RGB_MULT)   

    camera_ratio: tuple = (window.width / cam.width,
                    window.height / cam.height)
    angle = angle + cam.angle

    if not alpha == enums.FALSE:
        image = image.convert_alpha()
        image.set_alpha(alpha * 255)

    if not scale:
        scale = camera_ratio
    else:
        extra: tuple = (0, 0)
        if angle:
            extra = (0, 3)

        image = pg.transform.scale(image, (width * scale[0] * camera_ratio[0] + extra[0], height * scale[1] * camera_ratio[1] + extra[1]))

    if angle:
        image = pg.transform.rotate(image, angle)

    if origin == enums.CENTER:
        origin = (width / 2, height / 2)

    origin = (camera_ratio[0] * origin[0], camera_ratio[1] * origin[1])

    if not origin == enums.CENTER:
        origin = (width / 2 - origin[0],
                  height / 2 - origin[1])
        
        origin = rotate_array((origin[0] * scale[0],
                               origin[1] * scale[1]), -cam.angle + angle)

    position = (cam.x + (position[0] - cam.x) * camera_ratio[0],
                cam.y + (position[1] - cam.y) * camera_ratio[1])

    position = (position[0] + origin[0] - cam.x, 
                position[1] + origin[1] - cam.y)
    
    if cam.angle:
        position = rotate_array(position, cam.angle)
    
    half_final_width: float = image.get_width() / 2
    half_final_height: float = image.get_height() / 2

    out_bound_left: bool = position[0] + half_final_width < -window.width / 2
    out_bound_right: bool = position[0] - half_final_width > window.width / 2
    out_bound_top: bool = position[1] + half_final_height < -window.height / 2
    out_bound_bottom: bool = position[1] - half_final_height > window.height / 2
    if out_bound_right or out_bound_left or out_bound_top or out_bound_bottom:
        return

    position = (position[0] - half_final_width,
                position[1] - half_final_height)

    position = (position[0] + window.width / 2,
                position[1] + window.height / 2)
    
    surface.blit(image, position)

    return (position, (half_final_width * 2, half_final_height * 2))

def rect_transform(surface: pg.Surface, position: point, scale: tuple, color: tuple, angle: number = False, alpha: number = enums.FALSE, ret_surf: bool=False) -> pg.Surface:
    cam: camera.cam = camera.view[camera._current_camera]

    width: float = scale[0] * window.width / cam.width + 3
    height: float = scale[1] * window.height / cam.height + 3
    image: pg.Surface = pg.surface.Surface((width, height))

    image.fill(color)
            
    camera_ratio: tuple = (window.width / cam.width,
                    window.height / cam.height)
    angle = angle + cam.angle

    if not alpha == enums.FALSE:
        image = image.convert_alpha()
        image.set_alpha(alpha * 255)

    if angle:
        extra: tuple = (0, 3)
        image = pg.transform.scale(image, (width * scale[0] * camera_ratio[0] + extra[0], height * scale[1] * camera_ratio[1] + extra[1]))
        image = pg.transform.rotate(image, angle)

    position = (cam.x + (position[0] - cam.x) * camera_ratio[0],
                cam.y + (position[1] - cam.y) * camera_ratio[1])

    position = (position[0] - cam.x, 
                position[1] - cam.y)
    
    if cam.angle:
        position = rotate_array(position, cam.angle)
    
    half_final_width: number = image.get_width()
    half_final_height: number = image.get_height()

    out_bound_left: bool = position[0] + half_final_width < -window.width / 2
    out_bound_right: bool = position[0] > window.width / 2
    out_bound_top: bool = position[1] + half_final_height < -window.height / 2
    out_bound_bottom: bool = position[1] > window.height / 2
    if out_bound_right or out_bound_left or out_bound_top or out_bound_bottom:
        return

    position = (position[0] + window.width / 2,
                position[1] + window.height / 2)
    
    surface.blit(image, position)

    return (position, (half_final_width, half_final_height))

def point_transform(surface: pg.Surface, position: point, color: tuple=False, ret_surf: bool=False) -> pg.Surface:
    cam: camera.cam = camera.view[camera._current_camera]

    camera_ratio: tuple = (window.width / cam.width,
                    window.height / cam.height)

    position = (cam.x + (position[0] - cam.x) * camera_ratio[0],
                cam.y + (position[1] - cam.y) * camera_ratio[1])

    position = (position[0] - cam.x, 
                position[1] - cam.y)
    
    if cam.angle:
        position = rotate_array(position, cam.angle)

    out_bound_left: bool = position[0] < -window.width / 2
    out_bound_right: bool = position[0] > window.width / 2
    out_bound_top: bool = position[1] < -window.height / 2
    out_bound_bottom: bool = position[1] > window.height / 2
    if out_bound_right or out_bound_left or out_bound_top or out_bound_bottom:
        return

    position = (position[0] + window.width / 2,
                position[1] + window.height / 2)
    
    if not color:
        color = color.black

    # if ret_surf:
    #     return_surface: pg.Surface = pg.surface.Surface()
    pg.draw.circle(surface, color, position, 2)

def binary_search(array: list, array_len: int, position: int, value: number, app_flags: searchtype=False) -> int:
    if array_len == 0:
        return 0
    
    if array_len <= 2:
        for i in range(array_len):
            array_index: object = array[i]
            if app_flags == enums.CLASS_ID:
                array_index: int = array_index.class_id

            if array_index == value:
                return -position - i - 1
            if array_index > value:
                return position + i

        return position + array_len
    
    middle: int = array_len // 2
    middle_element: object = array[middle]
    if app_flags == enums.CLASS_ID:
        middle_element: int = middle_element.class_id

    if value == middle_element:
        return -position - middle - 1
    elif value > middle_element:
        array = array[middle + 1:]
        position += middle + 1
        new_len: int = array_len - middle - 1
    else:
        array = array[:middle]
        new_len: int = middle

    return binary_search(array, new_len, position, value, app_flags)

def init_object(instance: entity, name: str, pos: point, depth: int, universal: bool, sprite: str=False, mask: Mask=False, show: bool=False, has_draw: bool=False, has_tick: bool=False) -> None:
    global _global_id
    instance.class_id = _global_id
    _global_id += 1

    if name:
        instance.name_id = name
    else:
        instance.name_id = "__unnamed__"

    instance.dx, instance.dy, instance.dz = 0, 0, 0

    instance.x = pos[0]
    instance.y = pos[1]
    instance.z = pos[2]
    
    instance.sprite = sprite
    
    instance.mask = mask

    if depth == enums.FALSE:
        instance.depth = 0
    else:
        instance.depth = depth

    instance.groups_in = [instance.__class__.__name__]
    instance.spatial_place = {}

    instance.show = show

    if has_draw:
        layer.add_to_layer(instance)

    if group.groups.get(group.get_groups(instance)[0]) == None:
        group.make_group(group.get_groups(instance)[0])
    group.add_to_group(instance)

    if universal:
        group.add_to_group(instance, group_name=enums.UNIVERSAL)
        spatial_map.add_object_grid(instance, group_name=enums.UNIVERSAL)

    if has_tick:
        _tick.add_tick(instance)

def destroy_object(instance: entity) -> None:
    layer.remove_from_layer(instance)
    group.remove_from_group(instance)
    _tick.remove_tick(instance)
    # spatial_map.remove_object_grid(instance)
#     exec(f"""
# global {object.name_id}
# del {object.name_id}
# """)
running: bool = True

def start() -> None:
    global running
    
    window.build()

    clock: object = pg.time.Clock()

    pg.event.set_blocked(None)
    pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION, pg.MOUSEWHEEL])

    last_time = pg.time.get_ticks()

    while running:
        # Key update
        current_time = pg.time.get_ticks()
        if current_time - last_time >= 1000 / FPS:
            
            last_time = current_time
            rat.roll_x = 0
            rat.roll_y = 0

            for key in list(keyboard.type_key.keys()):
                keyboard.type_key.pop(key)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                elif event.type == pg.KEYDOWN:
                    keyboard._current_keys = pg.key.get_pressed()
                    keyboard.type_key[event.key] = True
                    keyboard.type_key_hold[event.key] = True
                
                elif event.type == pg.KEYUP:
                    keyboard._current_keys = pg.key.get_pressed()
                    keyboard.type_key_hold.pop(event.key)
                    
                elif event.type == pg.MOUSEBUTTONDOWN:
                    rat._current_button = pg.mouse.get_pressed()

                elif event.type == pg.MOUSEBUTTONUP:
                    rat._current_button = pg.mouse.get_pressed()

                elif event.type == pg.MOUSEMOTION:
                    rat.x, rat.y = pg.mouse.get_pos()

                elif event.type == pg.MOUSEWHEEL:
                    rat.roll_x = event.x
                    rat.roll_y = -event.y

            keyboard._update()
            rat._update()

            _tick.tick()

            window.buffer.fill(color._background)

            layer.build()

            window.display.blit(window.buffer, (0, 0))
            
            #Todo-- update scene todo
            pg.display.flip()

        clock.tick(FPS)

    pg.quit()