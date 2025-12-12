import pygame
from settings import *

class InteractiveObject(pygame.sprite.Sprite):
    def __init__(self, game, x, y, groups, name):
        super().__init__(groups)
        self.game = game
        self.name = name
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill((150, 150, 150)) # Default grey
        self.interactable = True
        self.solid = True

    def interact(self):
        print(f"Interacted with {self.name}")
        return False

    def update(self):
        pass

class PushBlock(InteractiveObject):
    def __init__(self, game, x, y, groups):
        super().__init__(game, x, y, groups, "Push Block")
        self.image.fill((100, 50, 0)) # Brown
        pygame.draw.rect(self.image, (80, 40, 0), (2, 2, TILESIZE-4, TILESIZE-4), 2)

    def interact(self):
        # Calculate push direction based on player position
        dx = self.rect.centerx - self.game.player.rect.centerx
        dy = self.rect.centery - self.game.player.rect.centery
        
        push_x, push_y = 0, 0
        if abs(dx) > abs(dy):
            push_x = 1 if dx > 0 else -1
        else:
            push_y = 1 if dy > 0 else -1
            
        target_x = self.x + push_x * TILESIZE
        target_y = self.y + push_y * TILESIZE
        
        # Check collision
        grid_x = int(target_x / TILESIZE)
        grid_y = int(target_y / TILESIZE)
        
        if not self.game.map.is_blocked(grid_x, grid_y):
            # Check for other objects
            blocked = False
            test_rect = pygame.Rect(target_x, target_y, TILESIZE, TILESIZE)
            for sprite in self.game.interactables:
                if sprite != self and sprite.rect.colliderect(test_rect):
                    blocked = True
                    break
            
            if not blocked:
                self.x = target_x
                self.y = target_y
                self.rect.x = self.x
                self.rect.y = self.y
                self.game.sound_manager.play('step') # Placeholder sound
                return True
        
        return False

class Switch(InteractiveObject):
    def __init__(self, game, x, y, groups, on_trigger=None):
        super().__init__(game, x, y, groups, "Switch")
        self.image.fill((50, 50, 50))
        pygame.draw.circle(self.image, (200, 0, 0), (TILESIZE//2, TILESIZE//2), 10)
        self.activated = False
        self.solid = False # Can walk over it
        self.on_trigger = on_trigger

    def update(self):
        # Check if something is standing on it
        hit = False
        if self.rect.colliderect(self.game.player.rect):
            hit = True
        else:
            for sprite in self.game.interactables:
                if isinstance(sprite, PushBlock) and self.rect.colliderect(sprite.rect):
                    hit = True
                    break
        
        if hit and not self.activated:
            self.activated = True
            pygame.draw.circle(self.image, (0, 200, 0), (TILESIZE//2, TILESIZE//2), 10)
            self.game.sound_manager.play('menu') # Click sound
            if self.on_trigger:
                self.on_trigger(True)
        elif not hit and self.activated:
            self.activated = False
            pygame.draw.circle(self.image, (200, 0, 0), (TILESIZE//2, TILESIZE//2), 10)
            if self.on_trigger:
                self.on_trigger(False)

class Door(InteractiveObject):
    def __init__(self, game, x, y, groups, locked=True):
        super().__init__(game, x, y, groups, "Door")
        self.locked = locked
        self.solid = locked
        self.image.fill((100, 100, 100))  # Grey door
        if not locked:
            self.open()

    def open(self):
        self.locked = False
        self.solid = False
        self.image.fill((150, 200, 150))  # Light green open door
        self.interactable = True
        # Optionally play sound
        self.game.sound_manager.play('door')
        return True

    def interact(self):
        if self.locked:
            # Door is locked; maybe play a sound
            self.game.sound_manager.play('locked')
            return False
        else:
            return self.open()

# Updated Switch to accept doors to open
class Switch(InteractiveObject):
    def __init__(self, game, x, y, groups, doors=None, on_trigger=None):
        super().__init__(game, x, y, groups, "Switch")
        self.image.fill((50, 50, 50))
        pygame.draw.circle(self.image, (200, 0, 0), (TILESIZE//2, TILESIZE//2), 10)
        self.activated = False
        self.solid = False  # Can walk over it
        self.on_trigger = on_trigger
        self.doors = doors or []

    def update(self):
        # Check if something is standing on it
        hit = False
        if self.rect.colliderect(self.game.player.rect):
            hit = True
        else:
            for sprite in self.game.interactables:
                if isinstance(sprite, PushBlock) and self.rect.colliderect(sprite.rect):
                    hit = True
                    break
        if hit and not self.activated:
            self.activated = True
            pygame.draw.circle(self.image, (0, 200, 0), (TILESIZE//2, TILESIZE//2), 10)
            self.game.sound_manager.play('menu')
            # Open associated doors
            for door in self.doors:
                door.open()
            if self.on_trigger:
                self.on_trigger(True)
        elif not hit and self.activated:
            self.activated = False
            pygame.draw.circle(self.image, (200, 0, 0), (TILESIZE//2, TILESIZE//2), 10)
            if self.on_trigger:
                self.on_trigger(False)
