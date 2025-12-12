import pygame
from settings import *

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y, name, dialogue_id, quest_id=None):
        self.groups = game.all_sprites, game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.name = name
        self.dialogue_id = dialogue_id
        self.quest_id = quest_id
        
        # Use hero sprite for now (placeholder)
        self.image = game.hero_img.copy()
        # Tint it to make it different
        self.image.fill((200, 200, 255), special_flags=pygame.BLEND_RGB_MULT)
        
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
    
    def interact(self):
        """Called when player talks to this NPC"""
        # Fetch dynamic dialogue from manager
        if hasattr(self.game, 'dialogue_manager'):
            return self.game.dialogue_manager.get_dialogue(self.dialogue_id)
        return "..."
