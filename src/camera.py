import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        """Apply camera offset to entity position"""
        return entity.image_rect.move(self.camera.topleft)
    
    def apply_rect(self, rect):
        """Apply camera offset to a rect"""
        return rect.move(self.camera.topleft)
    
    def update(self, target):
        """Update camera position to follow target"""
        # Center on target
        x = -target.rect.centerx + WIDTH // 2
        y = -target.rect.centery + HEIGHT // 2
        
        # Limit scrolling to map bounds
        x = min(0, x)  # Left
        y = min(0, y)  # Top
        x = max(-(self.width - WIDTH), x)  # Right
        y = max(-(self.height - HEIGHT), y)  # Bottom
        
        self.camera = pygame.Rect(x, y, self.width, self.height)
        
        # Debug logging (throttled to avoid spam, maybe every 60 frames or just once on change? 
        # For now, let's print if it's far off or just once per second equivalent)
        # Actually, let's just print it. The user can scroll up.
        # print(f"DEBUG: Camera: {self.camera.topleft}, Target: {target.rect.center}")
