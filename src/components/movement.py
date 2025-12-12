# DragonQuest/src/components/movement.py
import pygame
from components.component import Component
from settings import TILESIZE

class MovementComponent(Component):
    def __init__(self, owner, speed):
        super().__init__(owner)
        self.vx = 0
        self.vy = 0
        self.speed = speed

    def move(self, dx, dy):
        self.owner.x += dx
        self.owner.hit_rect.x = self.owner.x + (TILESIZE - self.owner.hit_rect.width) / 2
        self.collide_with_walls('x')
        
        self.owner.y += dy
        self.owner.hit_rect.y = self.owner.y + (TILESIZE - self.owner.hit_rect.height) / 2
        self.collide_with_walls('y')

        self.owner.rect.center = self.owner.hit_rect.center

    def collide_with_walls(self, dir):
        if self.owner.noclip: return
        
        x_start = int(self.owner.hit_rect.left / TILESIZE)
        x_end = int(self.owner.hit_rect.right / TILESIZE)
        y_start = int(self.owner.hit_rect.top / TILESIZE)
        y_end = int(self.owner.hit_rect.bottom / TILESIZE)
        
        for y in range(y_start, y_end + 1):
            for x in range(x_start, x_end + 1):
                if self.owner.game.map.is_blocked(x, y):
                    if dir == 'x':
                        if self.vx > 0: self.owner.hit_rect.right = x * TILESIZE
                        if self.vx < 0: self.owner.hit_rect.left = x * TILESIZE + TILESIZE
                        self.vx = 0
                        self.owner.x = self.owner.hit_rect.x - (TILESIZE - self.owner.hit_rect.width) / 2
                    if dir == 'y':
                        if self.vy > 0: self.owner.hit_rect.bottom = y * TILESIZE
                        if self.vy < 0: self.owner.hit_rect.top = y * TILESIZE + TILESIZE
                        self.vy = 0
                        self.owner.y = self.owner.hit_rect.y - (TILESIZE - self.owner.hit_rect.height) / 2
                    return

    def update(self, dt):
        self.vx, self.vy = 0, 0
        # This will be driven by an InputComponent or an AIComponent
        pass
