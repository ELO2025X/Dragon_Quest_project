import pygame
import random
import numpy as np
import math
from settings import *
from animation import AnimationController, Animation
from components.combat import CombatComponent
from components.movement import MovementComponent
from components.player_input import PlayerInputComponent
from components.ai import AIComponent
from components.inventory import InventoryComponent
from components.serialization import SerializationComponent
from inventory import ITEM_TEMPLATES, SKILLS, create_item, create_random_weapon

class Character(pygame.sprite.Sprite):
    def __init__(self, game, x, y, groups):
        self.groups = groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)
        self.hit_rect = self.rect.copy()
        
        self.anim_controller = AnimationController()
        self.components = []
        self.name = "Character"
        self.noclip = False

    def add_component(self, component_class, *args, **kwargs):
        component = component_class(self, *args, **kwargs)
        self.components.append(component)
        return component

    def get_component(self, component_class):
        for component in self.components:
            if isinstance(component, component_class):
                return component
        return None

    def update(self, dt):
        for component in self.components:
            component.update(dt)
            
        # Sync image_rect with rect (logical position)
        if hasattr(self, 'image_rect'):
            self.image_rect.center = self.rect.center

        # Animation
        movement = self.get_component(MovementComponent)
        if movement:
            if movement.vx != 0 or movement.vy != 0:
                self.anim_controller.set_state("walk")
            else:
                self.anim_controller.set_state("idle")
            
            if movement.vx > 0:
                self.anim_controller.flip_x = True
            elif movement.vx < 0:
                self.anim_controller.flip_x = False
        
        frame = self.anim_controller.update(dt)
        if frame:
            self.image = frame

class Player(Character):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, game.all_sprites)
        # Load and scale player image to TILESIZE (32x32)
        self.image = game.resource_manager.load_image("Hero.png")
        if self.image:
            self.game.logger.debug("Player image loaded successfully.")
        else:
            self.game.logger.error("Failed to load Player image!")

        # Scale image using SPRITE_SCALE_FACTOR and regular scale for sharp pixels
        scaled_image_size = (TILESIZE * SPRITE_SCALE_FACTOR, TILESIZE * SPRITE_SCALE_FACTOR)
        self.image = pygame.transform.scale(self.image, scaled_image_size)

        # Setup animation using the scaled image
        self.anim_controller.add_animation("idle", Animation([self.image]))
        self.anim_controller.add_animation("walk", Animation([self.image]))
        self.anim_controller.set_state("idle")
        self.image = self.anim_controller.current_animation.get_current_frame()

        # Keep original TILESIZE rect for collision/logic, but center the larger image within it
        self.rect = pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)
        self.image_rect = self.image.get_rect(center=self.rect.center)
        self.noclip = False
        self.name = "Hero"
        # Add Components
        self.combat = self.add_component(CombatComponent, hp=50, mp=20, stats=[5, 3, 4, 3])
        self.movement = self.add_component(MovementComponent, speed=150)
        self.input = self.add_component(PlayerInputComponent)
        self.inventory = self.add_component(InventoryComponent)
        self.serializer = self.add_component(SerializationComponent)
        # Job System
        self.job = "warrior"
        self.jp = 0
        self.mastered_jobs = []
        self.xp = 0
        self.level = 1
        self.xp_to_next = 100
        self.gold = 0
        self.known_spells = ["heal", "fireball"] # Initial spells
        self.known_spells = ["heal", "fireball"] # Initial spells
        # Initial items
        self.inventory.add_item(create_item("potion"))
        self.inventory.add_item(create_item("potion"))
        self.inventory.add_item(create_item("potion"))
        self.inventory.add_item(create_item("ether"))
        self.inventory.add_item(create_item("iron_sword")) # Starter weapon

    def level_up(self):
        self.level += 1
        self.xp = 0
        self.xp_to_next = int(self.xp_to_next * 1.5)
        
        growth = np.array([2, 2, 2, 1], dtype=np.int16)
        self.combat.stats += growth
        
        self.combat.max_hp += 10
        self.combat.max_mp += 5
        self.combat.hp = self.combat.max_hp
        self.combat.mp = self.combat.max_mp

    def to_dict(self):
        return self.serializer.to_dict()

    def from_dict(self, data):
        self.serializer.from_dict(data)

class NPC(Character):
    def __init__(self, game, x, y, name, dialogue_id, quest_id=None):
        super().__init__(game, x, y, (game.all_sprites, game.npcs))
        self.name = name
        self.dialogue_id = dialogue_id
        self.quest_id = quest_id
        
        # Load NPC image and scale to TILESIZE (32x32)
        npc_data = self.game.data_manager.get_data("npcs") if hasattr(self.game, 'data_manager') else None
        if npc_data and dialogue_id in npc_data:
            data = npc_data[dialogue_id]
            self.name = data.get("name", self.name)
            image_name = data.get("image")
            if image_name:
                self.image = game.resource_manager.load_image(image_name)
                if self.image:
                    scaled_image_size = (TILESIZE * SPRITE_SCALE_FACTOR, TILESIZE * SPRITE_SCALE_FACTOR)
                    self.image = pygame.transform.scale(self.image, scaled_image_size)
            elif "color" in data:
                scaled_image_size = (TILESIZE * SPRITE_SCALE_FACTOR, TILESIZE * SPRITE_SCALE_FACTOR)
                self.image = pygame.Surface(scaled_image_size, pygame.SRCALPHA)
                self.image.fill(data["color"])
            else:
                self.image = game.resource_manager.load_image("Hero.png")
                if self.image:
                    scaled_image_size = (TILESIZE * SPRITE_SCALE_FACTOR, TILESIZE * SPRITE_SCALE_FACTOR)
                    self.image = pygame.transform.scale(self.image, scaled_image_size)
        else:
            self.image = game.resource_manager.load_image("Hero.png")
            if self.image:
                scaled_image_size = (TILESIZE * SPRITE_SCALE_FACTOR, TILESIZE * SPRITE_SCALE_FACTOR)
                self.image = pygame.transform.scale(self.image, scaled_image_size)
        
        self.rect = pygame.Rect(self.x, self.y, TILESIZE, TILESIZE) # Logical rect
        self.image_rect = self.image.get_rect(center=self.rect.center) # Drawing rect
        
        # Add Components
        self.add_component(CombatComponent, hp=10, mp=0, stats=[1, 1, 1, 1])
        self.add_component(MovementComponent, speed=30)
        self.add_component(AIComponent)

    def interact(self):
        movement = self.get_component(MovementComponent)
        if movement:
            movement.vx = 0
            movement.vy = 0
        if hasattr(self.game, 'dialogue_manager'):
            return self.game.dialogue_manager.get_dialogue(self.dialogue_id)
        return "..."

class Enemy(Character):
    def __init__(self, game, x, y, enemy_type="slime"):
        super().__init__(game, x, y, (game.all_sprites, game.enemies))
        self.enemy_type = enemy_type
        
        enemy_data = self.game.data_manager.get_data("enemies")
        if enemy_data and enemy_type in enemy_data:
            data = enemy_data[enemy_type]
            self.name = data.get("name", "Enemy")
            self.special_abilities = data.get("special_abilities", [])
            self.attack_type = data.get("attack_type", "melee")
            
            self.add_component(CombatComponent, 
                               hp=data.get("max_hp", 10), 
                               mp=0, 
                               stats=data.get("stats", [1, 1, 1, 1]),
                               xp_reward=data.get("xp_reward", 0),
                               gold_reward=data.get("gold_reward", 0))
            self.add_component(MovementComponent, speed=30)
            self.add_component(AIComponent)

            image_name = data.get("image")
            scale_factor = data.get("scale", 1)
            
            img = game.resource_manager.load_image(image_name)
            
            # Apply scaling relative to TILESIZE to prevent massive sprites
            target_width = int(TILESIZE * scale_factor * SPRITE_SCALE_FACTOR)
            target_height = int(TILESIZE * scale_factor * SPRITE_SCALE_FACTOR)
            img = pygame.transform.scale(img, (target_width, target_height))

            if "tint" in data:
                tint_color = data["tint"]
                tinted_img = img.copy()
                tint_surface = pygame.Surface(tinted_img.get_size(), pygame.SRCALPHA)
                tint_surface.fill(tint_color)
                tinted_img.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                img = tinted_img
                
            self.scale = scale_factor

            self.anim_controller.add_animation("idle", Animation([img]))
            self.anim_controller.add_animation("walk", Animation([img]))
            self.anim_controller.set_state("idle")
            self.image = self.anim_controller.current_animation.get_current_frame()
        else:
            self.game.logger.warning(f"Enemy type '{enemy_type}' not found in data.")
            self.name = "Unknown"
            self.add_component(CombatComponent, hp=10, mp=0, stats=[1, 1, 1, 1])
            self.add_component(MovementComponent, speed=30)
            self.add_component(AIComponent)
            img = game.resource_manager.load_image("Slime.png")
            scaled_image_size = (TILESIZE * SPRITE_SCALE_FACTOR, TILESIZE * SPRITE_SCALE_FACTOR)
            img = pygame.transform.scale(img, scaled_image_size)
            self.anim_controller.add_animation("idle", Animation([img]))
            self.anim_controller.add_animation("walk", Animation([img]))
            self.anim_controller.set_state("idle")
            self.image = self.anim_controller.current_animation.get_current_frame()

        self.rect = pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)
        self.image_rect = self.image.get_rect(center=self.rect.center)
        
        hitbox_data = None
        if enemy_data and enemy_type in enemy_data:
             hitbox_data = enemy_data[enemy_type].get("hitbox")

        if hitbox_data:
            w = hitbox_data.get("width", self.rect.width)
            h = hitbox_data.get("height", self.rect.height)
            self.hit_rect = pygame.Rect(0, 0, w, h)
            self.hit_rect.center = self.rect.center
        else:
            self.hit_rect = self.rect.copy()

class Pickup(pygame.sprite.Sprite):
    def __init__(self, game, x, y, type="potion"):
        """
        x, y: Tile coordinates
        type: "potion", "ether", "gold", "powerup_str", "powerup_spd"
        """
        self.groups = game.all_sprites, game.pickups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)
        
        # Load image based on type
        # For now, using procedural colored squares if images missing, or existing icons
        if type == "potion":
            color = (255, 50, 50) # Red
        elif type == "ether":
            color = (50, 50, 255) # Blue
        elif type == "gold":
            color = (255, 215, 0) # Gold
        elif type == "powerup_str":
            color = (255, 100, 0) # Orange
        elif type == "powerup_spd":
            color = (0, 255, 255) # Cyan
        else:
            color = (255, 255, 255)

        # Try loading an image first (assuming standard naming convention)
        image_name = f"{type}.png"
        self.image = None
        if hasattr(self.game, 'resource_manager'):
             self.image = self.game.resource_manager.load_image(image_name)
        
        if self.image:
             scaled_size = (int(TILESIZE * 0.8), int(TILESIZE * 0.8))
             self.image = pygame.transform.scale(self.image, scaled_size)
             self.rect = self.image.get_rect()
             self.rect.center = (self.x + TILESIZE // 2, self.y + TILESIZE // 2)
        else:
            # Fallback to colored rect
            self.image = pygame.Surface((TILESIZE // 2, TILESIZE // 2))
            self.image.fill(color)
            self.rect = self.image.get_rect()
            self.rect.center = (self.x + TILESIZE // 2, self.y + TILESIZE // 2)

        self.bob_offset = 0
        self.bob_speed = 5
        self.base_y = self.rect.centery

    def update(self, dt):
        # Bobbing animation
        self.bob_offset += self.bob_speed * dt
        self.rect.centery = self.base_y + math.sin(self.bob_offset) * 5
