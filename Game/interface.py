import sweet as sw
import pygame as pg
from linalg import Vector

def mouse_at(rect):
    if sw.rat.x > rect[0] and sw.rat.x < rect[0] + rect[2] and sw.rat.y > rect[1] and sw.rat.y < rect[1] + rect[3]:
        return True
    return False

class Button:
    def __init__(self, parent, pos, size, information):
        self.parent = parent
        self.pos = pos
        self.size = size
        self.display_pos = pos
        if not information.get("animation") == None:
            animation = information["animation"]
            self.pre_pos = Vector(animation["pre_pos"])
            self.post_pos = Vector(animation["post_pos"])
            self.ease_type = animation["ease_type"]
            self.display_pos = self.pre_pos
            self.transition = 0

        if information["name"] == "basic":
            self.text = information["text"]
            self.text_size = Vector(self.text.get_width(), self.text.get_height())
            if self.text_size.x > self.size[0]:
                self.size[0] = self.text_size.x
            if self.text_size.y > self.size[1]:
                self.size[1] = self.text_size.y

            self.bound_box = (self.display_pos[0] - self.size[0] / 2, self.display_pos[1] - self.size[1] / 2, self.size[0], self.size[1])

            self.action = information["action"]
            
            self.button_color_off = (0, 0, 0)
            self.button_color_on = (30, 30, 30)
            self.button_color_t = 0

    def draw(self):
        self.button_color = sw.transition.lerp(self.button_color_off, self.button_color_on, self.button_color_t)
        pg.draw.rect(sw.window.buffer, self.button_color, self.bound_box, border_radius=10)
        sw.window.buffer.blit(self.text, (self.display_pos[0] - self.text_size[0] / 2, self.display_pos[1] - self.text_size[1] / 2))

    def tick(self):
        if mouse_at(self.bound_box):
            self.button_color_t = min(1, self.button_color_t + 0.2)
            if sw.rat.pressed(sw.M_LEFT):
                self.action(self.parent)
        else:
            self.button_color_t = max(0, self.button_color_t - 0.2)
        
    def update_anim(self, transition):
        self.transition = transition
        ease_t = float(sw.transition.ease(self.ease_type, self.transition))
        self.display_pos = self.pre_pos + (self.post_pos - self.pre_pos) * ease_t
        self.bound_box = (self.display_pos[0] - self.size[0] / 2, self.display_pos[1] - self.size[1] / 2, self.size[0], self.size[1])

class Interface:
    def __init__(self, parent, pos, size, information):
        self.parent = parent
        self.pos = pos
        self.size = size
        self.display_pos = pos
        if not information.get("animation") == None:
            animation = information["animation"]
            self.pre_pos = Vector(animation["pre_pos"])
            self.post_pos = Vector(animation["post_pos"])
            self.ease_type = animation["ease_type"]
            self.display_pos = self.pre_pos
            self.transition = 0

        if information["name"] == "container":
            self.color = information["color"]
            self.action = information["action"]
            if information.get("border_radius") == None:
                self.border_radius = 0
            else:
                self.border_radius = information["border_radius"]
            if information.get("content") == None:
                self.content = None
            else:
                content_pos = (self.pos[0] + information["content"]["pos"][0], self.pos[1] + information["content"]["pos"][1])
                self.content = Interface(self, content_pos, information["content"]["size"], information["content"]["information"])
            
    def draw(self):
        pg.draw.rect(sw.window.buffer, self.color, (self.pos[0], self.pos[1], self.size[0], self.size[1]), border_radius=self.border_radius)
        if not self.content == None:
            self.content.draw()
        # self.button_color = sw.transition.lerp(self.button_color_off, self.button_color_on, self.button_color_t)
        # pg.draw.rect(sw.window.buffer, self.button_color, self.bound_box, border_radius=10)
        # sw.window.buffer.blit(self.text, (self.display_pos[0] - self.text_size[0] / 2, self.display_pos[1] - self.text_size[1] / 2))

    def tick(self):
        if mouse_at(self.bound_box):
            self.button_color_t = min(1, self.button_color_t + 0.2)
            if sw.rat.pressed(sw.M_LEFT):
                self.action(self.parent)
        else:
            self.button_color_t = max(0, self.button_color_t - 0.2)
        
    def update_anim(self, transition):
        self.transition = transition
        ease_t = float(sw.transition.ease(self.ease_type, self.transition))
        self.display_pos = self.pre_pos + (self.post_pos - self.pre_pos) * ease_t
        self.bound_box = (self.display_pos[0] - self.size[0] / 2, self.display_pos[1] - self.size[1] / 2, self.size[0], self.size[1])

def play_func(game):
    game.scene = "game"
    game.time = 0
def quit_func(game):
    sw.running = False
def menu_func(game):
    game.scene = "menu"
    game.time = 0
def replay_func(game):
    game.scene = "game"
    game.time = 0
    game.reset_game()
def editor_func(game):
    game.scene = "editor"
    game.time = 0
def none_func(game):
    return