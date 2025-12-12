# DragonQuest/src/components/player_input.py
import pygame
from components.component import Component
from components.movement import MovementComponent

class PlayerInputComponent(Component):
    def __init__(self, owner):
        super().__init__(owner)
        self.movement_component = self.owner.get_component(MovementComponent)

    def update(self, dt):
        if not self.movement_component:
            return

        self.movement_component.vx, self.movement_component.vy = 0, 0
        keys = pygame.key.get_pressed()
        
        current_speed = self.movement_component.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            current_speed *= 2

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.movement_component.vx = -current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.movement_component.vx = current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.movement_component.vy = -current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.movement_component.vy = current_speed
        
        if self.movement_component.vx != 0 and self.movement_component.vy != 0:
            self.movement_component.vx *= 0.7071
            self.movement_component.vy *= 0.7071

        dx = self.movement_component.vx * dt
        dy = self.movement_component.vy * dt
        self.movement_component.move(dx, dy)
