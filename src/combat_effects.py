
import pygame
import random

class CombatEffect:
    def __init__(self, duration):
        self.duration = duration
        self.timer = 0
        self.finished = False

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.finished = True

    def draw(self, surface):
        pass

class FlashEffect(CombatEffect):
    def __init__(self, color=(255, 255, 255), duration=0.1):
        super().__init__(duration)
        self.color = color

    def draw(self, surface):
        s = pygame.Surface(surface.get_size())
        s.set_alpha(128) # Semi-transparent
        s.fill(self.color)
        surface.blit(s, (0, 0))

class DamageNumber(CombatEffect):
    def __init__(self, value, x, y, duration=0.8, color=(255, 255, 255)):
        super().__init__(duration)
        self.value = str(value)
        self.x = x
        self.y = y
        self.vy = -50 # Moves up
        self.color = color
        self.font = pygame.font.Font(None, 36)

    def update(self, dt):
        super().update(dt)
        self.y += self.vy * dt
        self.vy += 100 * dt # Gravity attempt? Or just slow down

    def draw(self, surface):
        text_surf = self.font.render(self.value, True, self.color)
        surface.blit(text_surf, (self.x, self.y))

class ScreenShake(CombatEffect):
    def __init__(self, intensity=5, duration=0.3):
        super().__init__(duration)
        self.intensity = intensity
        self.offset_x = 0
        self.offset_y = 0

    def update(self, dt):
        super().update(dt)
        if not self.finished:
            self.offset_x = random.randint(-self.intensity, self.intensity)
            self.offset_y = random.randint(-self.intensity, self.intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0

    # Shake is special, it needs to be applied to the render transform or offset drawing
    # Ideally Battle.draw calls this before drawing?
    # Or we verify it modifies a 'camera' offset in Battle?
