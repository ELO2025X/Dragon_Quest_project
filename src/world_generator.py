import random
import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Callable

class WorldGenerator:
    def __init__(self, seed=None):
        self.seed = seed if seed else random.randint(0, 10000)
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        # Tile types
        self.GRASS = 0
        self.DIRT = 1
        self.WATER = 2
        self.FOREST = 3
        self.MOUNTAIN = 4
        self.WALL = 5
        self.FLOOR = 6
        
    def generate_world_map(self, width: int = 100, height: int = 100) -> Dict[str, Any]:
        """Generate the 'Inner Sea' World Map"""
        # Initialize layers using NumPy
        ground = np.full((height, width), self.WATER, dtype=np.int8)
        decoration = np.zeros((height, width), dtype=np.int8)
        collision = np.zeros((height, width), dtype=np.int8)
        
        center_x, center_y = width // 2, height // 2
        inner_radius = 15
        outer_radius = 40
        
        for y in range(height):
            for x in range(width):
                # Distance from center
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                # Inner Sea (Donut Hole)
                if dist < inner_radius:
                    ground[y][x] = self.WATER
                    collision[y][x] = 1
                    
                # Land Ring (The Donut)
                elif dist < outer_radius:
                    # Noise for terrain variety
                    noise = self._noise(x * 0.1, y * 0.1)
                    if noise > 0.2:
                        ground[y][x] = self.FOREST
                    elif noise > 0:
                        ground[y][x] = self.GRASS
                    elif noise > -0.2:
                        ground[y][x] = self.DIRT
                    else:
                        ground[y][x] = self.MOUNTAIN
                        collision[y][x] = 0 # Mountains are now walkable
                        
                # Outer Ocean
                else:
                    ground[y][x] = self.WATER
                    collision[y][x] = 1
                    
        # Debug: Count land tiles
        unique, counts = np.unique(ground, return_counts=True)
        tile_counts = dict(zip(unique, counts))
        total_tiles = width * height
        water_count = tile_counts.get(self.WATER, 0)
        land_count = total_tiles - water_count
        # print(f"DEBUG: World Gen - Land: {land_count} ({land_count/total_tiles:.1%}), Water: {water_count}")

        # Place a Town Entrance
        town_x, town_y = center_x + 20, center_y
        decoration[town_y][town_x] = self.WALL # Placeholder for town icon
        # Ensure town entrance is walkable (or at least the tile under it)
        ground[town_y][town_x] = self.GRASS
        collision[town_y][town_x] = 0
        
        # Dungeon Entrance
        dungeon_x, dungeon_y = center_x - 15, center_y + 10
        decoration[dungeon_y][dungeon_x] = self.WALL # Placeholder
        ground[dungeon_y][dungeon_x] = self.DIRT
        collision[dungeon_y][dungeon_x] = 0
        
        # Find a valid spawn point within the land ring
        # The land is between inner_radius (15) and outer_radius (40)
        spawn_x, spawn_y = center_x, center_y
        found_spawn = False
        
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(inner_radius + 2, outer_radius - 2)
            tx = int(center_x + dist * math.cos(angle))
            ty = int(center_y + dist * math.sin(angle))
            
            if 0 <= tx < width and 0 <= ty < height:
                if ground[ty][tx] in [self.GRASS, self.DIRT, self.FOREST]:
                    spawn_x, spawn_y = tx, ty
                    found_spawn = True
                    break
        
        if not found_spawn:
            print("Warning: Could not find a suitable spawn tile. Forcing land at default.")
            # Pick a spot in the ring and force it to be land
            angle = 0
            dist = (inner_radius + outer_radius) / 2
            spawn_x = int(center_x + dist * math.cos(angle))
            spawn_y = int(center_y + dist * math.sin(angle))
            ground[spawn_y][spawn_x] = self.GRASS
            collision[spawn_y][spawn_x] = 0


        return {
            "id": "world_map",
            "width": width,
            "height": height,
            "layers": {
                "ground": ground,
                "decoration": decoration,
                "collision": collision
            },
            "exits": [
                {
                    "x": town_x, "y": town_y, 
                    "target_map": "town_01", 
                    "spawn_x": 10, "spawn_y": 18 
                },
                {
                    "x": dungeon_x, "y": dungeon_y,
                    "target_map": "dungeon_01",
                    "spawn_x": 0, "spawn_y": 0 # Will be overwritten by dungeon spawn
                }
            ],
            "spawn": (spawn_x, spawn_y)
        }

    def generate_town_map(self):
        """Generate a walled town map"""
        width, height = 20, 20
        ground = np.full((height, width), self.GRASS, dtype=np.int8)
        decoration = np.zeros((height, width), dtype=np.int8)
        collision = np.zeros((height, width), dtype=np.int8)
        
        # Walls around the town
        for y in range(height):
            for x in range(width):
                if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                    ground[y][x] = self.WALL
                    collision[y][x] = 1
                    
        # Town Exit (Gate)
        ground[height-1][10] = self.DIRT
        collision[height-1][10] = 0
        
        # Buildings (Simple rectangles)
        self._add_building(ground, collision, 4, 4, 6, 5) # Inn
        self._add_building(ground, collision, 12, 4, 5, 5) # Shop
        
        return {
            "id": "town_01",
            "width": width,
            "height": height,
            "layers": {
                "ground": ground,
                "decoration": decoration,
                "collision": collision
            },
            "exits": [
                {
                    "x": 10, "y": height-1, 
                    "target_map": "world_map", 
                    "spawn_x": 70, "spawn_y": 52 # Approx world coordinates
                }
            ],
            "spawn": (10, 15)
        }

    def generate_sector(self, sector_type="forest", width=100, height=100) -> Dict[str, Any]:
        """Generate a procedural sector based on type"""
        ground = np.full((height, width), self.GRASS, dtype=np.int8)
        decoration = np.zeros((height, width), dtype=np.int8)
        collision = np.zeros((height, width), dtype=np.int8)
        
        # Ground types based on biome
        base_tile = self.GRASS
        obstacle_tile = self.MOUNTAIN
        
        if sector_type == "desert":
            base_tile = self.DIRT # Sand
            obstacle_tile = self.MOUNTAIN # Rocks
        elif sector_type == "snow":
            base_tile = self.GRASS # Snow/Tundra (Visual only for now, reusing grass logic but maybe tinted later)
            obstacle_tile = self.MOUNTAIN # Ice walls/Mountains
        elif sector_type == "forest":
            base_tile = self.GRASS
            obstacle_tile = self.FOREST # Trees
            
        # Fill ground
        ground.fill(base_tile)
        
        # Procedural obstacles (Cellular Automata or Noise)
        for y in range(height):
            for x in range(width):
                # Simple noise
                noise = self._noise(x * 0.15 + random.random(), y * 0.15 + random.random())
                if noise > 0.4:
                    ground[y][x] = obstacle_tile
                    if obstacle_tile == self.MOUNTAIN:
                        collision[y][x] = 1
                    elif obstacle_tile == self.FOREST:
                        collision[y][x] = 0 # Can walk through forest but maybe slower? (handled in movement?)
                        
        # Edges should be open or gated? For now, open but safe zone at edges
        
        return {
            "id": f"sector_{sector_type}_{random.randint(0,999)}",
            "width": width,
            "height": height,
            "layers": {
                "ground": ground,
                "decoration": decoration,
                "collision": collision
            },
            "exits": [], # Exits generated dynamically?
            "spawn": (width//2, height//2),
            "type": sector_type
        }

    def _add_building(self, ground, collision, x, y, w, h):
        for dy in range(h):
            for dx in range(w):
                ground[y+dy][x+dx] = self.FLOOR
                collision[y+dy][x+dx] = 1 # Walls/Roof
                
        # Door
        ground[y+h-1][x+w//2] = self.DIRT
        collision[y+h-1][x+w//2] = 0

    def _noise(self, x, y):
        """Simple noise function using sine waves"""
        n = math.sin(x * 12.9898 + y * 78.233 + self.seed) * 43758.5453
        return (n - math.floor(n)) * 2 - 1

    def get_map_entities(self, map_id: str, map_width: int, map_height: int, is_blocked_func: Callable[[int, int], bool]) -> List[Dict[str, Any]]:
        """Return a list of entities to spawn on the map"""
        entities = []
        
        if map_id == "world_map":
            # Removed guaranteed Croc at 8,8 as it was in the ocean
            
            for _ in range(30): # Increased number of enemies for more variety
                ex = random.randint(5, map_width - 5)
                ey = random.randint(5, map_height - 5)
                if not is_blocked_func(ex, ey):
                    roll = random.random()
                    if roll < 0.1: # 10% chance for Croc
                        entities.append({"type": "enemy", "name": "croc", "x": ex, "y": ey})
                    elif roll < 0.25: # 15% chance for Spiteful Sprite
                        entities.append({"type": "enemy", "name": "spiteful_sprite", "x": ex, "y": ey})
                    elif roll < 0.40: # 15% chance for Vexing Sprite
                        entities.append({"type": "enemy", "name": "vexing_sprite", "x": ex, "y": ey})
                    elif roll < 0.50: # 10% chance for Malicious Sprite
                        entities.append({"type": "enemy", "name": "malicious_sprite", "x": ex, "y": ey})
                    else: # 50% chance for Slime
                        entities.append({"type": "enemy", "name": "slime", "x": ex, "y": ey})
            
            # Add wandering NPCs to world map
            npc_types = [
                ("Wanderer", "wanderer"),
                ("Oracle", "oracle"),
                ("Survivor", "survivor"),
                ("Ghost Hunter", "ghost_hunter"),
                ("Hermit", "hermit")
            ]
            
            for npc_name, dialogue_id in npc_types:
                # Find a valid spawn point
                for attempt in range(10):  # Try 10 times to find valid spot
                    nx = random.randint(8, map_width - 8)
                    ny = random.randint(8, map_height - 8)
                    if not is_blocked_func(nx, ny):
                        entities.append({"type": "npc", "name": npc_name, "dialogue_id": dialogue_id, "x": nx, "y": ny})
                        break
                        
        elif map_id == "town_01":
             entities.append({"type": "npc", "name": "Elder Mira", "dialogue_id": "elder_mira", "x": 10, "y": 10, "quest_id": 1})
             entities.append({"type": "npc", "name": "Villager", "dialogue_id": "villager", "x": 15, "y": 12})
             entities.append({"type": "npc", "name": "King Valen", "dialogue_id": "king_valen", "x": 20, "y": 8})
             
        elif "sector" in map_id:
             # Procedural enemies for sectors
             for _ in range(40):
                ex = random.randint(2, map_width - 2)
                ey = random.randint(2, map_height - 2)
                if not is_blocked_func(ex, ey):
                    # Enemy types based on biome (can extrapolate from map_id string)
                    enemy_type = "slime"
                    if "desert" in map_id:
                        enemy_type = random.choice(["orc_berserker", "bat", "slime"])
                    elif "snow" in map_id:
                        enemy_type = random.choice(["dark_wizard", "skeleton_archer"])
                    elif "forest" in map_id:
                         enemy_type = random.choice(["skeleton_archer", "slime", "bat"])
                         
                    entities.append({"type": "enemy", "name": enemy_type, "x": ex, "y": ey})
             
             # Random Pickups
             for _ in range(10):
                 px = random.randint(2, map_width - 2)
                 py = random.randint(2, map_height - 2)
                 if not is_blocked_func(px, py):
                     ptype = random.choice(["potion", "ether", "gold", "powerup_str", "powerup_spd"])
                     # Pickups are not entities in this list structure usually, they are sprites. 
                     # But Main.populate_map needs to know about them?
                     # Main.populate_map iterates this list.
                     # We need to add pickup support to get_map_entities return or handle it in populate_map
                     entities.append({"type": "pickup", "pickup_type": ptype, "x": px, "y": py})

        return entities
