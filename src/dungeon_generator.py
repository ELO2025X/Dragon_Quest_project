import json
import os
import random
import numpy as np
from settings import *
import pygame

class Segment:
    def __init__(self, data):
        self.id = data['id']
        self.type = data['type']
        self.width = data['width']
        self.height = data['height']
        self.grid_raw = data['grid'] # List of strings
        self.exits = data['exits'] # List of dicts
        
        # Convert grid to numpy
        self.layout = np.zeros((self.height, self.width), dtype=np.int8)
        self.collision = np.ones((self.height, self.width), dtype=np.int8)
        
        for r, row in enumerate(self.grid_raw):
            for c, char in enumerate(row):
                if char == '#':
                    self.layout[r][c] = 5 # WALL
                    self.collision[r][c] = 1
                else:
                    self.layout[r][c] = 6 # FLOOR
                    self.collision[r][c] = 0
                    
    def rotate(self, rotations=1):
        """Rotate the segment 90 degrees clockwise N times"""
        for _ in range(rotations):
            self.layout = np.rot90(self.layout, k=-1)
            self.collision = np.rot90(self.collision, k=-1)
            self.width, self.height = self.height, self.width
            
            # Rotate exits
            new_exits = []
            for ex in self.exits:
                nx, ny = self.width - 1 - ex['y'], ex['x']
                
                # Rotate direction
                dirs = ["NORTH", "EAST", "SOUTH", "WEST"]
                try:
                   idx = dirs.index(ex['direction'])
                   new_dir = dirs[(idx + 1) % 4]
                except:
                   new_dir = ex['direction']
                   
                new_exits.append({"x": nx, "y": ny, "direction": new_dir})
            self.exits = new_exits

class SegmentGenerator:
    def __init__(self, seed=None):
        self.seed = seed if seed else random.randint(0, 10000)
        random.seed(self.seed)
        self.WALL = 5
        self.FLOOR = 6
        self.segments = self.load_segments()
        
    def load_segments(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'segments.json')
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return [Segment(s) for s in data['segments']]
        except FileNotFoundError:
            print(f"Warning: Segments file not found at {path}")
            return []

    def generate_dungeon(self, width=60, height=60, max_segments=15):
        # Initialize map
        ground = np.full((height, width), self.WALL, dtype=np.int8)
        collision = np.ones((height, width), dtype=np.int8)
        decoration = np.zeros((height, width), dtype=np.int8)
        
        placed_segments = []
        open_exits = [] # List of tuples: (map_x, map_y, direction, required_entry_dir)
        
        # 1. Place Start Segment (e.g., a room)
        start_seg = self.get_segment_by_type("room")
        if not start_seg: return None
        
        start_x = width // 2 - start_seg.width // 2
        start_y = height // 2 - start_seg.height // 2
        
        self.place_segment(ground, collision, start_seg, start_x, start_y)
        placed_segments.append(start_seg)
        
        # Add exits to open list
        for ex in start_seg.exits:
             open_exits.append((start_x + ex['x'], start_y + ex['y'], ex['direction']))
             
        # 2. Iteratively place segments
        failures = 0
        while len(placed_segments) < max_segments and open_exits and failures < 50:
            # Pick a random exit
            exit_idx = random.randint(0, len(open_exits) - 1)
            ex_x, ex_y, ex_dir = open_exits[exit_idx]
            
            # Determine required opposite direction
            opposites = {"NORTH": "SOUTH", "SOUTH": "NORTH", "EAST": "WEST", "WEST": "EAST"}
            req_entry = opposites.get(ex_dir)
            
            # Pick a random segment (maybe prioritize corridors if just left a room)
            candidate = random.choice(self.segments)
            
            # Try to align a matching exit
            # We need to find an exit on the candidate that points in 'req_entry' direction
            # If not found, try rotating
            success = False
            best_rotation = 0
            matching_exit = None
            
            # HACK: Create a deep copy or re-instantiate because we are mutating via rotate in loop
            # For simplicity, let's just rotate the one we have and rotate back if fail? 
            # Better: re-instantiate from raw list or clone.
            # Lazy approach: Try 4 rotations
            import copy
            test_seg = copy.deepcopy(candidate)
            
            for r in range(4):
                for seg_ex in test_seg.exits:
                     if seg_ex['direction'] == req_entry:
                         # Found a potential connection
                         # Calculate placement top-left
                         # If exit is at (sx, sy), and map exit is (mx, my)
                         # Then map_top_left = mx - sx, my - sy
                         
                         tx = ex_x - seg_ex['x']
                         ty = ex_y - seg_ex['y']
                         
                         if self.can_place(ground, test_seg, tx, ty):
                             self.place_segment(ground, collision, test_seg, tx, ty)
                             placed_segments.append(test_seg)
                             
                             # Add new exits
                             del open_exits[exit_idx] # Remove used exit defined on map
                             
                             for new_ex in test_seg.exits:
                                 # Don't add the one we just connected to
                                 if new_ex is not seg_ex:
                                     open_exits.append((tx + new_ex['x'], ty + new_ex['y'], new_ex['direction']))
                                     
                             success = True
                             break
                if success: break
                test_seg.rotate()
                
            if not success:
               failures += 1
        
        # 3. Cap remaining exits (TODO: Add simple walls)
        
        # Return format matching WorldGenerator expectation
        entities = []
        # Calculate rough spawn
        spawn_x = width // 2
        spawn_y = height // 2
        
        return {
            "id": "segment_dungeon",
            "width": width,
            "height": height,
            "layers": {
                "ground": ground,
                "decoration": decoration,
                "collision": collision
            },
            "entities": entities,
            "spawn": (spawn_x, spawn_y),
            "exits": []
        }

    def get_segment_by_type(self, type_name):
        opts = [s for s in self.segments if s.type == type_name]
        return random.choice(opts) if opts else (self.segments[0] if self.segments else None)

    def can_place(self, ground, segment, x, y):
        # Check bounds
        if x < 1 or y < 1 or x + segment.width >= ground.shape[1] - 1 or y + segment.height >= ground.shape[0] - 1:
            return False
            
        # Check collision with existing floor (simplified overlap check)
        # Only check where the new segment has floor? Or strict box check?
        # Strict box check is safer for now.
        region = ground[y:y+segment.height, x:x+segment.width]
        # If any part of the region is already floor (our FLOOR ID is 6), fail.
        # But we need to allow the connection point overlapping?
        # Ideally, we allow overlap of 1 tile at the connection, but checking that is complex.
        # Instead, let's just check if the box overlaps significantly.
        
        # Count non-WALL tiles in region
        overlap = np.count_nonzero(region == self.FLOOR)
        if overlap > 0:
             # If it overlaps, it might be just the connection. 
             # For a robust generator, we'd use a mask. 
             # For this MVP, let's be strict: NO significant overlap. 
             # (This might make it hard to connect)
             return False 
             
        return True

    def place_segment(self, ground, collision, segment, x, y):
        for r in range(segment.height):
            for c in range(segment.width):
                # Don't overwrite existing floor with walls if we are merging? 
                # Our segment is a box.
                tile = segment.layout[r][c]
                if tile != 5: # If it's not a generic wall, place it
                    ground[y+r][x+c] = tile
                    collision[y+r][x+c] = segment.collision[r][c]
                elif ground[y+r][x+c] == 5: # Only overwrite wall with wall (if empty)
                     ground[y+r][x+c] = tile


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
