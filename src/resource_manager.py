import pygame
import os
from settings import *

class ResourceManager:
    _instance = None

    def __new__(cls, game=None):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance.images = {}
            cls._instance.sounds = {}
            cls._instance.fonts = {}
            cls._instance.game = game # Store the game instance
            cls._instance.game_folder = os.path.dirname(__file__)
            cls._instance.assets_folder = os.path.join(cls._instance.game_folder, 'assets')
            cls._instance._load_assets()
        return cls._instance

    def _load_assets(self):
        # Load Core Assets
        self.load_image('Hero.png', scale=(SPRITE_RENDER_SIZE, SPRITE_RENDER_SIZE))
        self.load_image('Slime.png', scale=(SPRITE_RENDER_SIZE, SPRITE_RENDER_SIZE))
        self.load_image('croc_boss.png', scale=(SPRITE_RENDER_SIZE * 2, SPRITE_RENDER_SIZE * 2))
        self.load_image('Spiteful_Sprite.png', scale=(SPRITE_RENDER_SIZE, SPRITE_RENDER_SIZE))



        # Items
        item_files = {
            "Jamaican Dream": "Jamaican Dream.png",
            "Lamb's Bread": "Lamb's Bread.png",
            "SATIVA!": "SATIVA!.png"
        }
        for name, filename in item_files.items():
            self.load_image(filename, scale=(SPRITE_RENDER_SIZE, SPRITE_RENDER_SIZE))
        
        self.load_image('Grass.png', scale=(TILESIZE, TILESIZE))
        self.load_image('Dirt.png', scale=(TILESIZE, TILESIZE))
        self.load_image('Water.png', scale=(TILESIZE, TILESIZE))

    def load_image(self, filename, scale=None, alpha=True):
        if filename in self.images:
            return self.images[filename]
            
        path = os.path.join(self.assets_folder, filename)
        try:
            if alpha:
                img = pygame.image.load(path).convert_alpha()
            else:
                img = pygame.image.load(path).convert()
                
            if scale:
                img = pygame.transform.scale(img, scale)
                
            self.images[filename] = img
            return img
        except FileNotFoundError:
            self.game.logger.error(f"Image {filename} not found at {path}")
            # Return a placeholder surface
            surf = pygame.Surface((TILESIZE, TILESIZE))
            surf.fill((255, 0, 255)) # Magenta placeholder
            return surf

    def load_sound(self, filename):
        if filename in self.sounds:
            return self.sounds[filename]
            
        path = os.path.join(self.assets_folder, filename)
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[filename] = sound
            return sound
        except FileNotFoundError:
            self.game.logger.error(f"Sound {filename} not found at {path}")
            return None
            
    def get_image(self, filename):
        return self.images.get(filename)
