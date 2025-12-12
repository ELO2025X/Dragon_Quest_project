import pygame
from settings import *
from spell import SPELL_LIBRARY

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.hero_img
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(0, 0, 24, 24) # Smaller collision rect
        self.hit_rect.center = self.rect.center
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
        self.hit_rect.x = self.x + (TILESIZE - self.hit_rect.width) / 2
        self.hit_rect.y = self.y + (TILESIZE - self.hit_rect.height) / 2
        self.vx = 0
        self.vy = 0
        self.speed = 150  # Pixels per second
        
        # RPG Stats
        self.level = 1
        self.xp = 0
        self.xp_to_next = 10
        self.gold = 0
        
        # Attributes (Dragon Quest style)
        self.strength = 5
        self.defense = 3
        self.agility = 4
        self.luck = 3
        
        # Combat stats (calculated from attributes)
        self.hp = 50 + (self.level * 10)
        self.max_hp = 50 + (self.level * 10)
        self.mp = 20 + (self.level * 5)
        self.max_mp = 20 + (self.level * 5)
        self.attack = self.strength * 2 + self.level
        self.defense_power = self.defense * 2
        
        # Spells
        self.spells = []  # List of spell names
        self.learn_spell("Heal")  # Start with Heal spell

    def get_keys(self):
        # Don't accept input during battle
        if self.game.in_battle:
            return
            
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = self.speed
        
        # Normalize diagonal movement
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def update(self):
        self.get_keys()
        
        # Move X
        self.x += self.vx * self.game.dt
        self.hit_rect.x = self.x + (TILESIZE - self.hit_rect.width) / 2
        self.collide_with_walls('x')
        
        # Move Y
        self.y += self.vy * self.game.dt
        self.hit_rect.y = self.y + (TILESIZE - self.hit_rect.height) / 2
        self.collide_with_walls('y')
        
        # Constrain to World Bounds
        if self.hit_rect.left < 0: 
            self.x = 0 - (TILESIZE - self.hit_rect.width) / 2
        if self.hit_rect.right > self.game.map.width: 
            self.x = self.game.map.width - self.hit_rect.width - (TILESIZE - self.hit_rect.width) / 2
        if self.hit_rect.top < 0: 
            self.y = 0 - (TILESIZE - self.hit_rect.height) / 2
        if self.hit_rect.bottom > self.game.map.height: 
            self.y = self.game.map.height - self.hit_rect.height - (TILESIZE - self.hit_rect.height) / 2
            
        # Update rect position based on hit_rect
        self.rect.center = self.hit_rect.center

    def collide_with_walls(self, dir):
        # Check for collisions with map tiles
        x_start = int(self.hit_rect.left / TILESIZE)
        x_end = int(self.hit_rect.right / TILESIZE)
        y_start = int(self.hit_rect.top / TILESIZE)
        y_end = int(self.hit_rect.bottom / TILESIZE)
        
        for y in range(y_start, y_end + 1):
            for x in range(x_start, x_end + 1):
                if self.game.map.is_blocked(x, y):
                    # Noclip check
                    if getattr(self, 'noclip', False):
                        continue
                        
                    if dir == 'x':
                        if self.vx > 0: # Moving right
                            self.hit_rect.right = x * TILESIZE
                        if self.vx < 0: # Moving left
                            self.hit_rect.left = x * TILESIZE + TILESIZE
                        self.vx = 0
                        self.x = self.hit_rect.x - (TILESIZE - self.hit_rect.width) / 2
                    if dir == 'y':
                        if self.vy > 0: # Moving down
                            self.hit_rect.bottom = y * TILESIZE
                        if self.vy < 0: # Moving up
                            self.hit_rect.top = y * TILESIZE + TILESIZE
                        self.vy = 0
                        self.y = self.hit_rect.y - (TILESIZE - self.hit_rect.height) / 2
                    return
    
    def learn_spell(self, spell_name):
        """Learn a new spell"""
        if spell_name in SPELL_LIBRARY and spell_name not in self.spells:
            self.spells.append(spell_name)
            return True
        return False

    def level_up(self):
        """Level up the player (can be called by debug)"""
        self.level += 1
        self.xp = 0
        self.xp_to_next = int(self.xp_to_next * 1.5)
        
        # Stat increases
        self.strength += 2
        self.defense += 2
        self.agility += 2
        self.luck += 1
        
        # Recalculate combat stats
        self.max_hp = 50 + (self.level * 10)
        self.max_mp = 20 + (self.level * 5)
        self.attack = self.strength * 2 + self.level
        self.defense_power = self.defense * 2
        
        # Full heal
        self.hp = self.max_hp
        self.mp = self.max_mp

    def to_dict(self):
        """Serialize player data"""
        return {
            "level": self.level,
            "xp": self.xp,
            "xp_to_next": self.xp_to_next,
            "gold": self.gold,
            "strength": self.strength,
            "defense": self.defense,
            "agility": self.agility,
            "luck": self.luck,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "spells": self.spells
        }

    def from_dict(self, data):
        """Load player data"""
        self.level = data.get("level", 1)
        self.xp = data.get("xp", 0)
        self.xp_to_next = data.get("xp_to_next", 10)
        self.gold = data.get("gold", 0)
        self.strength = data.get("strength", 5)
        self.defense = data.get("defense", 3)
        self.agility = data.get("agility", 4)
        self.luck = data.get("luck", 3)
        self.hp = data.get("hp", 60)
        self.max_hp = data.get("max_hp", 60)
        self.mp = data.get("mp", 25)
        self.max_mp = data.get("max_mp", 25)
        self.spells = data.get("spells", ["Heal"])
        
        # Recalculate derived stats just in case
        self.attack = self.strength * 2 + self.level
        self.defense_power = self.defense * 2

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, enemy_type="slime"):
        self.groups = game.all_sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Load data
        enemies_data = game.data_manager.get_data("enemies")
        if enemies_data and enemy_type in enemies_data:
            data = enemies_data[enemy_type]
            self.name = data.get("name", "Unknown")
            self.hp = data.get("hp", 10)
            self.max_hp = data.get("max_hp", 10)
            # Stats: str, def, agi, luck
            stats = data.get("stats", [1, 1, 1, 1])
            self.strength = stats[0]
            self.defense = stats[1]
            self.agility = stats[2]
            self.luck = stats[3]
            self.xp_reward = data.get("xp_reward", 0)
            self.gold_reward = data.get("gold_reward", 0)
            self.scale = data.get("scale", 1)
            self.special_abilities = data.get("special_abilities", {})
            
            # Image
            img_name = data.get("image", "Slime.png")
            img = game.resource_manager.get_image(img_name)
            if img:
                self.image = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            else:
                self.image = pygame.Surface((32, 32))
                self.image.fill((255, 0, 0))
                
            # Tint (if applicable)
            if "tint" in data:
                self.image.fill(data["tint"], special_flags=pygame.BLEND_RGB_MULT)
                
        else:
            # Fallback
            self.enemy_type = enemy_type
            self.hp = 25
            self.max_hp = 25
            self.name = "Unknown"
            self.xp_reward = 0
            self.gold_reward = 0
            self.scale = 1
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 0))
            self.special_abilities = {}

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        
        # Combat component (if needed, but looks like Battle uses direct attributes or creates a component wrapper)
        # The Battle class in battle.py uses get_component(CombatComponent). 
        # But Enemy here doesn't seem to have components. 
        # Wait, battle.py line 205: enemy.get_component(CombatComponent).
        # This implies Enemy HAS a get_component method.
        # But the original code I viewed didn't show it!
        # Let me check the original code again.


    def update(self):
        # Simple AI or static
        pass
