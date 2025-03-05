import sweet as sw
import pygame as pg
from pygame.locals import K_w, K_s, K_a, K_d, K_SPACE
from linalg import Vector, Matrix
import math as m
import random as rd
import buttons

global_id = 0

window_size = (1200, 675)
sw.window.set_size(window_size)
sw.window.set_title("Space Shooter")
sw.window.build()
sw.keyboard.add_extra_keys([K_w, K_s, K_a, K_d, K_SPACE])

game = ""

class Game(sw.Entity):
    def __init__(self):
        super().__init__("Enemy", (0, 0, 0), None, False, has_tick=True, has_draw=True)
        self.scene = "menu"
        global game
        game = self

        self.objects = []
        self.player = Player((window_size[0] / 2, window_size[1] / 2, 0))
        self.entities = [self.player]

        self.time = 0
        
        self.font = {
            "rb_36": pg.font.Font("Game\\fonts\\Roboto.ttf", 36),
            "rb_18": pg.font.Font("Game\\fonts\\Roboto.ttf", 18),
            "st_54": pg.font.Font("Game\\fonts\\Strengthen.ttf", 54),
            }
        self.texts = {
            "title": self.font["st_54"].render("Space Shooter", True, (255, 255, 255)),
            "play": self.font["rb_36"].render("Jogar", True, (255, 255, 255)),
            "quit": self.font["rb_36"].render("Sair", True, (255, 255, 255)),
            "game_over": self.font["rb_36"].render("Você morreu...", True, (255, 255, 255)),
            "again": self.font["rb_36"].render("Tentar novamente", True, (255, 255, 255)),
            "return": self.font["rb_36"].render("Voltar ao menu", True, (255, 255, 255)),
        }
        self.play_pos = (0, 0)
        self.quit_pos = (0, 0)
        self.play_color = (0, 0, 0)
        self.quit_color = (0, 0, 0)

        self.return_pos = (0, 0)
        self.again_pos = (0, 0)
        self.return_color = (0, 0, 0)
        self.again_color = (0, 0, 0)

        self.points_jump = 0
        self.previous_points = 0

        self.point_sum = 0

        self.max_spawn_time = 300

        self.play_button = buttons.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["play"],
            "action": buttons.play_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 50),
                "post_pos": (window_size[0] / 2, window_size[1] / 2),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })
        self.quit_button = buttons.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["quit"],
            "action": buttons.quit_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 100),
                "post_pos": (window_size[0] / 2, window_size[1] / 2 + 50),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })
        self.menu_button = buttons.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["return"],
            "action": buttons.menu_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 100),
                "post_pos": (window_size[0] / 4, window_size[1] / 2),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })
        self.replay_button = buttons.Button(self, 0, [200, 0], {
            "name": "basic",
            "text": self.texts["again"],
            "action": buttons.replay_func,
            "animation": {
                "pre_pos": (window_size[0] / 2, window_size[1] + 100),
                "post_pos": (window_size[0] * 3 / 4, window_size[1] / 2),
                "ease_type": sw.enums.EASE_QUADRATIC,
            }
        })

    def reset_game(self):
        self.player.points = 0
        self.player.alive = True
        self.player.life = 100
        self.objects = [self.player]
        self.entities = [self.player]
        self.time = 0
        self.player.pos = Vector(window_size[0] / 2, window_size[1] / 2)
        self.player.pos_speed = Vector(0, 0)
        self.point_sum = 0

    def tick(self):
        if self.scene == "menu":
            self.menu_tick()
        elif self.scene == "game":
            self.game_tick()
        elif self.scene == "death":
            self.death_tick()

    def draw(self):
        if self.scene == "menu":
            self.menu_draw()
        elif self.scene == "game":
            self.game_draw()
        elif self.scene == "death":
            self.death_draw()
        
    def menu_tick(self):
        self.time += 1
        if self.time < 130:
            self.play_button.update_anim(self.time / 100)
            self.quit_button.update_anim((self.time - 30) / 100)

        self.play_button.tick()
        self.quit_button.tick()
        
    def menu_draw(self):
        t = min(self.time / 70, 1)
        t = sw.transition.ease(sw.enums.EASE_QUADRATIC, t)
        
        transform_title = pg.transform.scale(self.texts["title"], (self.texts["title"].get_width() * t, self.texts["title"].get_height() * t))
        sw.window.buffer.blit(transform_title, ((window_size[0] - transform_title.get_width()) / 2, 20))

        self.play_button.draw()
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

            self.entities.append(Enemy((enemy_pos[0], enemy_pos[1], 0)))

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

class Player(sw.Entity):
    def __init__(self, pos):
        game.objects.append(self)
        global global_id
        self.id = global_id
        global_id += 1
        self.radius = 7
        self.angle = 0
        self.pos = Vector(pos[0], pos[1])
        self.pos_speed = Vector(0, 0)
        self.speed = 0.4
        self.update_vertices()
        self.fire_cooldown = 0
        self.max_fire_cooldown = 5
        self.fire_speed = 15
        self.life = 100
        self.color = (255, 0, 255)
        self.damage_color = (255, 0, 0)
        self.damage = 50
        self.damaged = 0
        self.alive = True
        self.points = 0

    def draw(self):
        self.update_vertices()
        final_color = sw.transition.lerp(self.color, self.damage_color, self.damaged)
        pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[0]).to_list(), (self.pos + self.diagonals[1]).to_list())
        pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[1]).to_list(), (self.pos + self.diagonals[2]).to_list())
        pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[2]).to_list(), (self.pos + self.diagonals[0]).to_list())

    def update_vertices(self):
        self.diagonals = Matrix([
            Vector(10, 0),
            Vector(-5, 5),
            Vector(-5, -5),
            ])
        self.diagonals = self.diagonals.rigid_transform(Vector(0, 0), self.angle)

    def tick(self):
        self.pos += self.pos_speed
        self.pos.x = max(0, min(window_size[0], self.pos.x))
        self.pos.y = max(0, min(window_size[1], self.pos.y))
        self.pos_speed *= 0.9
        self.angle = m.degrees(sw.calc.angle(self.pos, (sw.rat.x, sw.rat.y)))

        if sw.keyboard.pressing(K_w):
            self.pos_speed += Vector(0, -self.speed)
        if sw.keyboard.pressing(K_s):
            self.pos_speed += Vector(0, self.speed)
        if sw.keyboard.pressing(K_a):
            self.pos_speed += Vector(-self.speed, 0)
        if sw.keyboard.pressing(K_d):
            self.pos_speed += Vector(self.speed, 0)
        
        self.fire_cooldown -= 1
        if sw.rat.pressed(sw.M_LEFT):
            if self.fire_cooldown <= 0:
                self.update_vertices()
                Projectile(self.pos + self.diagonals[0], Matrix([Vector(self.fire_speed, 0)]).rigid_transform(Vector(0, 0), self.angle)[0], self.damage, self)
                self.fire_cooldown = self.max_fire_cooldown

        self.damaged = max(self.damaged - 0.1, 0)

        if self.life <= 0:
            game.scene = "death"
            game.time = 0

class Projectile(sw.Entity):
    def __init__(self, pos, speed, damage, owner):
        global global_id
        self.id = global_id
        global_id += 1
        game.objects.append(self)
        self.radius = 2
        self.pos = Vector(pos[0], pos[1])
        self.pos_speed = speed
        self.owner = owner
        self.damage = damage

    def draw(self):
        pg.draw.circle(sw.window.buffer, (255, 255 * (0 if self.owner.id == game.player.id else 1), 255), self.pos.to_list(), 2)

    def tick(self):
        self.pos += self.pos_speed

        if self.pos.distance(self.owner.pos) > 1000:
            destroy(self)

        for entity in game.entities:
            if entity == self.owner:
                continue
            if entity.pos.distance(self.pos) < entity.radius + self.radius and entity.alive:
                entity.damaged = 1
                entity.life -= self.damage
                destroy(self)

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

class Enemy(sw.Entity):
    def __init__(self, pos):
        game.objects.append(self)
        global global_id
        self.id = global_id
        global_id += 1
        self.radius = 7
        self.angle = 0
        self.pos = Vector(pos[0], pos[1])
        self.pos_speed = Vector(0, 0)
        self.speed = 0.01
        self.fire_cooldown = 0
        self.max_fire_cooldown = 40
        self.fire_speed = 5
        self.life = 100
        self.color = (255, 255, 255)
        self.damage_color = (255, 0, 0)
        self.damaged = 0
        self.damage = 15
        self.alive = True
        self.linear_explosion = [
            Vector(0, 0),
            Vector(0, 0),
            Vector(0, 0),
        ]
        self.linear_explosion_directions = [
            rd.random() * 2 * m.pi,
            rd.random() * 2 * m.pi,
            rd.random() * 2 * m.pi,
        ]
        self.disappear_cooldown = 200
        self.update_vertices()

    def draw(self):
        self.update_vertices()
        if self.alive:
            final_color = sw.transition.lerp(self.color, self.damage_color, self.damaged)
            pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[0]).to_list(), (self.pos + self.diagonals[1]).to_list())
            pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[1]).to_list(), (self.pos + self.diagonals[2]).to_list())
            pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[2]).to_list(), (self.pos + self.diagonals[0]).to_list())
        else:
            final_color = sw.transition.lerp(self.color, self.damage_color, self.damaged)
            final_color = sw.transition.lerp(final_color, (0, 0, 0), 1 - self.disappear_cooldown / 200)
            pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[0]).to_list(), (self.pos + self.diagonals[1]).to_list())
            pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[2]).to_list(), (self.pos + self.diagonals[3]).to_list())
            pg.draw.line(sw.window.buffer, final_color, (self.pos + self.diagonals[4]).to_list(), (self.pos + self.diagonals[5]).to_list())

    def update_vertices(self):
        if self.alive:
            self.diagonals = Matrix([
                Vector(10, 0),
                Vector(-5, 5),
                Vector(-5, -5),
                ])
            self.diagonals = self.diagonals.rigid_transform(Vector(0, 0), self.angle)
        else:
            self.diagonals = Matrix([
                Vector(10, 0) + self.linear_explosion[0],
                Vector(-5, 5) + self.linear_explosion[0],
                Vector(-5, 5) + self.linear_explosion[1],
                Vector(-5, -5) + self.linear_explosion[1],
                Vector(-5, -5) + self.linear_explosion[2],
                Vector(10, 0) + self.linear_explosion[2],
                ])
            self.diagonals = self.diagonals.rigid_transform(Vector(0, 0), self.angle)

    def tick(self):
        self.pos += self.pos_speed
        
        if self.alive:
            self.pos_speed *= 0.99
            self.angle = m.degrees(sw.calc.angle(self.pos.to_list(), game.player.pos.to_list()))
            self.pos_speed += (game.player.pos - self.pos).normalize() * self.speed

            self.fire_cooldown -= 1
            if self.fire_cooldown <= 0:
                self.update_vertices()
                Projectile(self.pos + self.diagonals[0], self.pos_speed + Matrix([Vector(self.fire_speed, 0)]).rigid_transform(Vector(0, 0), self.angle)[0], self.damage, self)
                self.fire_cooldown = self.max_fire_cooldown
        else:
            self.linear_explosion[0] += Vector(m.cos(self.linear_explosion_directions[0]), -m.sin(self.linear_explosion_directions[0])) * 0.1
            self.linear_explosion[1] += Vector(m.cos(self.linear_explosion_directions[1]), -m.sin(self.linear_explosion_directions[1])) * 0.1
            self.linear_explosion[2] += Vector(m.cos(self.linear_explosion_directions[2]), -m.sin(self.linear_explosion_directions[2])) * 0.1
            self.disappear_cooldown -= 1
            if self.disappear_cooldown <= 0:
                destroy(self)

        self.damaged = max(self.damaged - 0.1, 0)

        if self.life <= 0:
            if self.alive:
                game.player.points += 20
            
            self.alive = False

Game()

sw.start()



"""
Engine prevention text for computer problems around deleting last """