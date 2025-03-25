import sweet as sw
import pygame as pg
from pygame.locals import K_w, K_s, K_a, K_d, K_SPACE
from linalg import *
import math as m
import random as rd
import interface
from collision import collision_with

global_id = 0

window_size = (1200, 675)
sw.window.set_size(window_size)
sw.window.set_title("Space Shooter")
sw.window.build()
sw.keyboard.add_extra_keys([K_w, K_s, K_a, K_d, K_SPACE])

pg.mixer.init()

game = ""

class Game(sw.Entity):
    def __init__(self):
        super().__init__("Enemy", (0, 0, 0), None, False, has_tick=True, has_draw=True)
        self.scene = "menu"
        self.game_type = "fight"
        self.game_level = "funk_infernal"
        global game
        game = self

        self.objects = []
        self.entities = []
        self.object_groups = {}
        self.player = Player((window_size[0] / 2, window_size[1] / 2, 0))

        sw.camera.set_cam_pos("main", (window_size[0] / 2, window_size[1] / 2))

        self.time = 0
        
        self.font = {
            "rb_36": pg.font.Font("Game\\fonts\\Roboto.ttf", 36),
            "rb_18": pg.font.Font("Game\\fonts\\Roboto.ttf", 18),
            "st_54": pg.font.Font("Game\\fonts\\Strengthen.ttf", 54),
            }
        self.texts = {
            "title": self.font["st_54"].render("Space Shooter", True, (255, 255, 255)),
            "play": self.font["rb_36"].render("Jogar", True, (255, 255, 255)),
            "editor": self.font["rb_36"].render("Editor", True, (255, 255, 255)),
            "quit": self.font["rb_36"].render("Sair", True, (255, 255, 255)),
            "game_over": self.font["rb_36"].render("Você morreu...", True, (255, 255, 255)),
            "again": self.font["rb_36"].render("Tentar novamente", True, (255, 255, 255)),
            "return": self.font["rb_36"].render("Voltar ao menu", True, (255, 255, 255)),
        }

        self.points_jump = 0
        self.previous_points = 0

        self.point_sum = 0

        self.max_spawn_time = 300

        self.pos = (0, 0)
        self.size = window_size

        self.play_button = interface.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["play"],
            "action": interface.play_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 50),
                "post_pos": (window_size[0] / 2, window_size[1] / 2),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })
        self.editor_button = interface.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["editor"],
            "action": interface.editor_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 100),
                "post_pos": (window_size[0] / 2, window_size[1] / 2 + 50),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })
        self.quit_button = interface.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["quit"],
            "action": interface.quit_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 150),
                "post_pos": (window_size[0] / 2, window_size[1] / 2 + 100),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })
        self.menu_button = interface.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["return"],
            "action": interface.menu_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 100),
                "post_pos": (window_size[0] / 4, window_size[1] / 2),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })
        self.replay_button = interface.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["again"],
            "action": interface.replay_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 100),
                "post_pos": (window_size[0] * 3 / 4, window_size[1] / 2),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })

        self.timeline = interface.Interface(self, (0, window_size[1] - 100), (window_size[0], 100), {
            "name": "container",
            "color": (20, 20, 20),
            "action": interface.none_func,
            "content": {"pos": (10, 10), "size": (50, 80), "information": {
                "name": "container",
                "color": (40, 40, 40),
                "action": interface.none_func,
                "border_radius": 10,
            }}
        })

    def reset_game(self):
        self.player.points = 0
        self.player.alive = True
        self.player.life = 100
        self.objects = [self.player]
        self.entities = [self.player]
        self.object_groups = {"player": [self.player]}
        self.time = 0
        self.player.pos = Vector(window_size[0] / 2, window_size[1] / 2)
        self.player.pos_speed = Vector(0, 0)
        self.point_sum = 0

    def tick(self):
        if self.scene == "menu":
            self.menu_tick()
        elif self.scene == "game":
            self.game_tick()
        elif self.scene == "editor":
            self.editor_tick()
        elif self.scene == "death":
            self.death_tick()

    def draw(self):
        if self.scene == "menu":
            self.menu_draw()
        elif self.scene == "game":
            self.game_draw()
        elif self.scene == "editor":
            self.editor_draw()
        elif self.scene == "death":
            self.death_draw()
        
    def menu_tick(self):
        self.time += 1
        if self.time < 140:
            self.play_button.update_anim(self.time / 100)
            self.editor_button.update_anim((self.time - 20) / 100)
            self.quit_button.update_anim((self.time - 40) / 100)

        self.play_button.tick()
        self.editor_button.tick()
        self.quit_button.tick()
        
    def menu_draw(self):
        t = min(self.time / 70, 1)
        t = sw.transition.ease(sw.enums.EASE_QUADRATIC, t)
        
        transform_title = pg.transform.scale(self.texts["title"], (self.texts["title"].get_width() * t, self.texts["title"].get_height() * t))
        sw.window.buffer.blit(transform_title, ((window_size[0] - transform_title.get_width()) / 2, 20))

        self.play_button.draw()
        self.editor_button.draw()
        self.quit_button.draw()

    def death_tick(self):
        self.time += 1
        self.menu_button.update_anim(self.time / 70)
        self.replay_button.update_anim(self.time / 70)

        self.menu_button.tick()
        self.replay_button.tick()

    def death_draw(self):
        sw.window.buffer.blit(self.texts["game_over"], ((window_size[0] - self.texts["game_over"].get_width()) / 2, 20))
        if self.point_sum < self.player.points:
            self.point_sum += 1
        points = self.font["rb_36"].render(f"Pontos: {self.point_sum}", True, (255, 255, 255))
        sw.window.buffer.blit(points, ((window_size[0] - points.get_width()) / 2, 100))

        self.replay_button.draw()
        self.menu_button.draw()

    def game_tick(self):
        self.time += 1
        if self.time > 300 and not pg.mixer.music.get_busy():
            if self.game_level == "funk_infernal":
                pg.mixer.music.load("Game\\musics\\funk_infernal.mp3")
                pg.mixer.music.play()

        self.max_spawn_time = max(10, m.floor(300 - self.time / 10))
        if self.time % self.max_spawn_time == 0:
            edge = rd.randint(0, 3)
            if edge == 0:
                edge_line = [Vector(-20, -20), Vector(-20, window_size[1])]
            if edge == 1:
                edge_line = [Vector(-20, window_size[1] + 20), Vector(window_size[0] + 20, window_size[1] + 20)]
            if edge == 2:
                edge_line = [Vector(window_size[0] + 20, window_size[1] + 20), Vector(window_size[0], -20)]
            if edge == 3:
                edge_line = [Vector(window_size[0] + 20, -20), Vector(-20, -20)]
            enemy_pos = edge_line[0] + (edge_line[1] - edge_line[0]) * rd.random()
            
            Enemy((enemy_pos[0], enemy_pos[1]))
            # Asteroid((rd.random() * window_size[0], rd.random() * window_size[1]))

        for entity in self.objects:
            entity.tick() 

    def game_draw(self):
        for entity in self.objects:
            entity.draw()

        if not self.previous_points == self.player.points:
            self.points_jump = 1
        self.points_jump = max(0, self.points_jump - 0.1)
        points = self.font["rb_18"].render(f"Pontos: {self.player.points}", True, (255, 255, 255))
        points = pg.transform.scale(points, (points.get_width() * (1 + self.points_jump / 10), points.get_height() * (1 + self.points_jump / 10)))
        sw.window.buffer.blit(points, (20, 20))
        self.previous_points = self.player.points

        pg.draw.rect(sw.window.buffer, (255, 255, 255), (window_size[0] - 100, 20, 80, 20), 2)
        pg.draw.rect(sw.window.buffer, (255, 255, 255), (window_size[0] - 95, 25, 70 * self.player.life / 100, 10))

    def editor_tick(self):
        pass

    def editor_draw(self):
        self.timeline.draw()

class GameObject:
    def __init__(self, object_type, pos, speed, angle, color, max_life, mask=False, groups=[], physics={}):
        game.objects.append(self)
        game.entities.append(self)
        global global_id
        self.id = global_id
        global_id += 1
        self.angle = angle
        self.pos = Vector(pos[0], pos[1])
        self.pos_speed = Vector(speed[0], speed[1])
        self.color = color
        self.damage_color = (255, 0, 0)
        self.max_life = max_life
        self.life = max_life
        self.damaged = 0
        self.alive = True
        self.mask = mask
        if len(physics):
            self.mass = physics["mass"]
            self.inverse_mass = 1 / self.mass
            self.inertia_momentum = physics["inertia_momentum"]
            self.angle_speed = physics["angle_speed"]
            self.restitution = physics["restitution"]

        self.groups_in = groups
        for group in groups:
            if game.object_groups.get(group) == None:
                game.object_groups[group] = [self]
            else:
                game.object_groups[group].append(self)

        self.object_type = object_type

class Player(GameObject):
    def __init__(self, pos):
        mask = Matrix([
               Vector(10, 0),
               Vector(-5, 5),
               Vector(-5, -5),
        ])
        super().__init__("player", pos, (0, 0), 0, (255, 0, 255), 100, mask, ["player", "object"], physics={"angle_speed": 0, "mass": 15, "inertia_momentum": 10, "restitution": .1})
        self.update_vertices()
        self.radius = 7
        self.speed = 0.4
        self.fire_cooldown = 0
        self.max_fire_cooldown = 5
        self.fire_speed = 15
        self.damage = 50
        self.points = 0

    def draw(self):
        self.update_vertices()
        final_color = list(sw.transition.lerp(self.color, self.damage_color, self.damaged))
        sw.polygon_transform(sw.window.buffer, self.display_vertices, final_color)

    def update_vertices(self):
        self.display_vertices = self.mask.rigid_transform(self.pos, self.angle)

    def tick(self):
        self.pos += self.pos_speed
        self.pos.x = max(0, min(window_size[0], self.pos.x))
        self.pos.y = max(0, min(window_size[1], self.pos.y))
        self.pos_speed *= 0.9
        self.angle = m.degrees(sw.calc.angle(sw.coord_transform(self.pos.to_list()), (sw.rat.x, sw.rat.y)))

        if sw.keyboard.pressing(K_w):
            self.pos_speed += Vector(0, -self.speed)
        if sw.keyboard.pressing(K_s):
            self.pos_speed += Vector(0, self.speed)
        if sw.keyboard.pressing(K_a):
            self.pos_speed += Vector(-self.speed, 0)
        if sw.keyboard.pressing(K_d): 
            self.pos_speed += Vector(self.speed, 0)
        
        self.fire_cooldown -= 1
        if sw.rat.released(sw.M_LEFT):
            if self.fire_cooldown <= 0:
                self.update_vertices()
                Laser(self.display_vertices[0], Matrix([Vector(self.fire_speed, 0)]).rigid_transform(Vector(0, 0), self.angle)[0], self.damage, self)
                self.fire_cooldown = self.max_fire_cooldown

        self.damaged = max(self.damaged - 0.02, 0)

        # if self.life <= 0:
        #     game.scene = "death"
        #     game.time = 0

class Enemy(GameObject):
    def __init__(self, pos):
        mask = Matrix([
               Vector(10, 0),
               Vector(-5, 5),
               Vector(-5, -5),
        ])
        super().__init__("enemy", pos, (0, 0), 0, (255, 255, 255), 100, mask, ["enemy", "object"], physics={"angle_speed": 0, "mass": 15, "inertia_momentum": 10, "restitution": .1})
        self.radius = 7
        self.speed = 0.03
        self.fire_cooldown = 0
        self.max_fire_cooldown = 20
        self.fire_speed = 15
        self.damaged = 0
        self.damage = 15
        self.linear_explosion = [
            Vector(0, 0),
            Vector(0, 0),
            Vector(0, 0),
        ]
        self.disappear_cooldown = 200
        self.update_vertices()

    def draw(self):
        self.update_vertices()
        final_color = list(sw.transition.lerp(self.color, self.damage_color, self.damaged))
        if self.alive:
            sw.polygon_transform(sw.window.buffer, self.display_vertices, final_color)
        else:
            final_color = list(sw.transition.lerp(final_color, (0, 0, 0), 1 - self.disappear_cooldown / 200))
            parts = [
                [self.display_vertices[0],
                 self.display_vertices[1],
                 self.display_vertices[2],
                ],
                [self.display_vertices[3],
                 self.display_vertices[4],
                 self.display_vertices[5],
                ],
                [self.display_vertices[6],
                 self.display_vertices[7],
                 self.display_vertices[8],
                ],
            ]
            for part in parts:
                sw.polygon_transform(sw.window.buffer, part, final_color)
            
    def update_vertices(self):
        if self.alive:
            self.display_vertices = Matrix([
                Vector(10, 0),
                Vector(-5, 5),
                Vector(-5, -5),
                ])
            self.display_vertices = self.mask.rigid_transform(self.pos, self.angle)
        else:
            self.mask = Matrix([
                self.linear_explosion[0],
                Vector(10, 0) + self.linear_explosion[0],
                Vector(-5, 5) + self.linear_explosion[0],
                self.linear_explosion[1],
                Vector(-5, 5) + self.linear_explosion[1],
                Vector(-5, -5) + self.linear_explosion[1],
                self.linear_explosion[2],
                Vector(-5, -5) + self.linear_explosion[2],
                Vector(10, 0) + self.linear_explosion[2],
                ])
            self.display_vertices = self.mask.rigid_transform(self.pos, self.angle)

    def tick(self):
        self.pos += self.pos_speed
        
        if self.alive:
            self.pos_speed *= 0.99
            player_future_pos = game.player.pos#game.player.pos + game.player.pos_speed * (self.pos.distance(game.player.pos)) / self.fire_speed
            self.angle = m.degrees(sw.calc.angle(self.pos.to_tuple(), player_future_pos.to_tuple()))
            self.pos_speed += (game.player.pos - self.pos).normalize() * self.speed

            self.fire_cooldown -= 1
            if self.fire_cooldown <= 0:
                self.update_vertices()
                Laser(self.display_vertices[0], self.pos_speed + Matrix([Vector(self.fire_speed, 0)]).rigid_transform(Vector(0, 0), self.angle)[0], self.damage, self)
                self.fire_cooldown = self.max_fire_cooldown
        else:
            self.linear_explosion[0] += Vector(m.cos(self.linear_explosion_directions[0]), -m.sin(self.linear_explosion_directions[0])) * 0.1
            self.linear_explosion[1] += Vector(m.cos(self.linear_explosion_directions[1]), -m.sin(self.linear_explosion_directions[1])) * 0.1
            self.linear_explosion[2] += Vector(m.cos(self.linear_explosion_directions[2]), -m.sin(self.linear_explosion_directions[2])) * 0.1
            self.disappear_cooldown -= 1
            if self.disappear_cooldown <= 0:
                destroy(self)

        collisions = collision_with(game, self, "enemy", True)
        if collisions:
            for collision in collisions:
                if collision.second_body.id == self.id:
                    continue

                self.damaged = 1
                collision.second_body.damaged = 1
                
                collision_resolution(self, collision)

        self.damaged = max(self.damaged - 0.02, 0)

        if self.life <= 0:
            if self.alive:
                game.player.points += 20
            
            if self.alive == True:
                self.alive = False
                self.linear_explosion_directions = [
                    math.radians(self.angle) + rd.random() * 2 * m.pi / 3,
                    math.radians(self.angle) + 4 * m.pi / 3 + rd.random() * 2 * m.pi / 3,
                    math.radians(self.angle) + 2 * m.pi / 3 + rd.random() * 2 * m.pi / 3,
                ]

def projectile_hit(self):
    collisions = collision_with(game, self, "object", True)
    
    if collisions:
        for collision in collisions:
            entity = collision.second_body

            if entity.id == self.owner.id:
                continue
            elif ((entity.object_type == "player") or ("enemy" in entity.groups_in)) and entity.life > 0:
                entity.damaged = min(1, entity.damaged + self.damage / entity.max_life)
                entity.life -= self.damage
                destroy(self)
            elif entity.object_type == "asteroid":
                entity.pos_speed += self.pos_speed * 10 / entity.mass
                entity.damaged = min(1, entity.damaged + self.damage / entity.max_life)
                destroy(self)

def contact_point(face, body_b):
    closest_contact_distance: float = float("inf")
    closest_contact_point: Vector = Vector(0, 0)

    for second_vertex in body_b.display_vertices:
        compare_vertex = second_vertex + body_b.pos
        face_vector = face[1] - face[0]
        interpolation_multiplier = face_vector.dot(compare_vertex - face[0]) / face_vector.magnitude() ** 2

        closest_point = face[1] * interpolation_multiplier + face[0] * (1 - interpolation_multiplier)

        offset = closest_point.distance(compare_vertex)

        if offset < closest_contact_distance:
            closest_contact_distance = offset
            closest_contact_point = closest_point.to_tuple()
        
    return closest_contact_point

def collision_resolution(self, collision):
    other = collision.second_body
    other.damaged = 1
    if collision.data.main_object:
        body_a = self
    else:
        body_a = other

    contact_face = Matrix([body_a.display_vertices[collision.data.vertex_a] + body_a.pos, body_a.display_vertices[collision.data.vertex_b] + body_a.pos])
    contact_normal = contact_face[0].normal(contact_face[1])

    proportion = other.mass / (self.mass + other.mass)

    self.pos += contact_normal * collision.data.mtv * proportion
    other.pos -= contact_normal * collision.data.mtv * (1 - proportion)

class Laser(GameObject):
    def __init__(self, pos, speed, damage, owner):
        self.owner = owner
        mask = Matrix([
            Vector(0, -1),
            Vector(-30, -1),
            Vector(-30, 1),
            Vector(0, 1),
        ])
        super().__init__("laser", pos, speed, 0, (255, 255 * (0 if self.owner.id == game.player.id else 1), 255), 0, mask, ["laser", "projectile"])
        self.origin = pos
        self.length = 0
        self.damage = damage
        self.update_vertices()

    def draw(self):
        self.update_vertices()
        sw.line_transform(sw.window.buffer, self.display_vertices[0], self.display_vertices[1], self.color)

    def tick(self):
        self.pos += self.pos_speed
        self.length = min(self.origin.distance(self.pos), 30)

        if self.pos.distance(self.owner.pos) > 1000:
            destroy(self)
            return

        self.update_vertices()
        projectile_hit(self)

    def update_vertices(self):
        self.angle = math.degrees(sw.calc.angle((0, 0), self.pos_speed))
        self.display_vertices = self.mask.rigid_transform(self.pos, self.angle)

class Bullet(GameObject):
    def __init__(self, pos, speed, damage, owner):
        self.owner = owner
        mask = Matrix([
            Vector(1, 0),
            Vector(-1, -1),
            Vector(-1, 1),
        ])
        super().__init__("bullet", pos, speed, 0, (255, 255 * (0 if self.owner.id == game.player.id else 1), 255), 0, mask, ["bullet", "projectile"])
        self.radius = 2
        self.damage = damage
        self.image = pg.surface.Surface((6, 6))
        pg.draw.circle(self.image, self.color, (self.image.get_width() / 2, self.image.get_height() / 2), self.image.get_width() / 2)

    def draw(self):
        sw.image_transform(self.image, sw.window.buffer, self.pos.to_tuple())

    def tick(self):
        self.pos += self.pos_speed

        if self.pos.distance(self.owner.pos) > 2000:
            destroy(self)
            return

        self.update_vertices()
        projectile_hit(self)

class Asteroid(GameObject):
    def __init__(self, pos):
        self.radius = rd.random() * 20 + 10
        points = rd.randint(5, 15)
        vertices = [Vector(rd.random() * 2 + self.radius - 1, 2 * i * math.pi / points, "polar") for i in range(points)]
        mask = Matrix(vertices)
        super().__init__("asteroid", pos, Vector(rd.random() * 5 + 5, rd.random() * 2 * math.pi, "polar"), 0, (255, 255, 255), 200, mask, ["asteroid", "object"], physics={"angle_speed": 0, "mass": math.pi * self.radius ** 2 / 20, "inertia_momentum": math.pi ** 2 * 30, "restitution": .1})
        self.angle_speed = rd.random() - 0.5
        self.update_vertices()
        self.closest = (0, 0)

    def draw(self):
        self.update_vertices()
        final_color = list(sw.transition.lerp(self.color, self.damage_color, self.damaged))
        display_coords = [self.pos + vertex for vertex in self.display_vertices]
        sw.polygon_transform(sw.window.buffer, display_coords, final_color)
        pg.draw.circle(sw.window.buffer, (0, 0, 255), self.closest, 2)

    def tick(self):
        self.pos += self.pos_speed / sw.FPS
        self.angle += self.angle_speed / sw.FPS
        self.damaged = max(self.damaged - 0.1, 0)

        collisions = collision_with(game, self, "object", True)
        if collisions:
            self.damaged = 1
            for collision in collisions:
                other = collision.second_body
                other.damaged = 1
                if collision.data.main_object:
                    body_a = self
                    body_b = other
                else:
                    body_a = other
                    body_b = self

                contact_face = Matrix([body_a.display_vertices[collision.data.vertex_a] + body_a.pos, body_a.display_vertices[collision.data.vertex_b] + body_a.pos])
                contact_normal = contact_face[0].normal(contact_face[1])

                proportion = other.mass / (self.mass + other.mass)

                self.pos += contact_normal * collision.data.mtv * proportion
                other.pos -= contact_normal * collision.data.mtv * (1 - proportion)

                self.pos_speed += other.pos_speed * proportion

    def update_vertices(self):
        self.display_vertices = self.mask.rigid_transform(Vector(0, 0), self.angle)

def destroy(instance):
    i = 0
    while i < len(game.objects):
        if game.objects[i].id == instance.id:
            game.objects.pop(i)
            i += 1
        i += 1
    i = 0
    while i < len(game.entities):
        if game.entities[i].id == instance.id:
            game.entities.pop(i)
            i += 1
        i += 1
    for group in instance.groups_in:
        i = 0
        while i < len(game.object_groups[group]):
            if game.object_groups[group][i].id == instance.id:
                game.object_groups[group].pop(i)
                i += 1
            i += 1

def draw_polygon(pos, vertices, color):
    color = list(map(int, color))
    for i in range(len(vertices)):
        sw.line_transform(sw.window.buffer, (pos + vertices[i]).to_list(), (pos + vertices[(i + 1) % len(vertices)]).to_list(), color)

def connect_lines(pos, vertices, color, connections):
    color = list(map(int, color))
    for connection in connections:
        sw.line_transform(sw.window.buffer, (pos + vertices[connection[0]]).to_list(), (pos + vertices[connection[1]]).to_list(), color)

Game()

sw.start()

"""
dummy text dummy text dummy text dummy text dummy text dummy text dummy"""