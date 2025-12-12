import random
import numpy as np
from settings import *
import pygame

class DungeonGenerator:
    def __init__(self, seed=None):
        self.seed = seed if seed else random.randint(0, 10000)
        random.seed(self.seed)
        
        self.WALL = 5
        self.FLOOR = 6
        self.DOOR = 7 # Placeholder ID
        
    def generate_dungeon(self, width=50, height=50, num_rooms=10):
        """Generate a room-based dungeon"""
        ground = np.full((height, width), self.WALL, dtype=np.int8)
        collision = np.ones((height, width), dtype=np.int8)
        decoration = np.zeros((height, width), dtype=np.int8)
        
        rooms = []
        
        for _ in range(num_rooms):
            w = random.randint(6, 12)
            h = random.randint(6, 12)
            x = random.randint(1, width - w - 1)
            y = random.randint(1, height - h - 1)
            
            new_room = pygame.Rect(x, y, w, h)
            
            # Check overlap
            failed = False
            for other in rooms:
                if new_room.colliderect(other.inflate(2, 2)):
                    failed = True
                    break
            
            if not failed:
                self._create_room(new_room, ground, collision)
                
                if rooms:
                    # Connect to previous room
                    prev_center = rooms[-1].center
                    new_center = new_room.center
                    
                    if random.randint(0, 1):
                        self._create_h_tunnel(prev_center[0], new_center[0], prev_center[1], ground, collision)
                        self._create_v_tunnel(prev_center[1], new_center[1], new_center[0], ground, collision)
                    else:
                        self._create_v_tunnel(prev_center[1], new_center[1], prev_center[0], ground, collision)
                        self._create_h_tunnel(prev_center[0], new_center[0], new_center[1], ground, collision)
                        
                rooms.append(new_room)
                
        # Place entities
        entities = []
        
        # Start Room (First room)
        if not rooms:
            raise ValueError("No rooms could be placed – check room generation parameters.")
        start_room = rooms[0]
        spawn_x = start_room.centerx
        spawn_y = start_room.centery
        
        # Boss Room (Last room)
        boss_room = rooms[-1]
        entities.append({"type": "enemy", "name": "croc", "x": boss_room.centerx, "y": boss_room.centery})
        
        # Other rooms
        for room in rooms[1:-1]:
            # Random chance for enemies
            if random.random() < 0.7:
                num_enemies = random.randint(1, 3)
                for _ in range(num_enemies):
                    ex = random.randint(room.left + 1, room.right - 2)
                    ey = random.randint(room.top + 1, room.bottom - 2)
                    entities.append({"type": "enemy", "name": "slime", "x": ex, "y": ey})
            
            # Random chance for puzzle/chest
            if random.random() < 0.3:
                # Add a door near the chest
                entities.append({"type": "object", "class": "Door", "x": room.centerx + 2, "y": room.centery, "locked": True})
                # Add a switch that will open the door (no linking yet)
                entities.append({"type": "object", "class": "Switch", "x": room.centerx - 2, "y": room.centery, "doors": []})

        return {
            "id": "dungeon_01",
            "width": width,
            "height": height,
            "layers": {
                "ground": ground,
                "decoration": decoration,
                "collision": collision
            },
            "entities": entities,
            "spawn": (spawn_x, spawn_y),
            "exits": [] # Add exit back to world later
        }

    def _create_room(self, room, ground, collision):
        for y in range(room.top, room.bottom):
            for x in range(room.left, room.right):
                ground[y][x] = self.FLOOR
                collision[y][x] = 0

    def _create_h_tunnel(self, x1, x2, y, ground, collision):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            ground[y][x] = self.FLOOR
            collision[y][x] = 0
            # Make tunnels wider if within bounds
            if y + 1 < ground.shape[0]:
                ground[y+1][x] = self.FLOOR
                collision[y+1][x] = 0

    def _create_v_tunnel(self, y1, y2, x, ground, collision):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            ground[y][x] = self.FLOOR
            collision[y][x] = 0
            # Make tunnels wider if within bounds
            if x + 1 < ground.shape[1]:
                ground[y][x+1] = self.FLOOR
                collision[y][x+1] = 0
if __name__ == "__main__":
    dg = DungeonGenerator()
    dungeon = dg.generate_dungeon()
    print("Dungeon generated:", dungeon["id"])
    print("Spawn point:", dungeon["spawn"])
    print("Number of entities:", len(dungeon["entities"]))
