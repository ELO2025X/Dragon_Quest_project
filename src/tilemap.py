import pygame
from settings import *
from world_generator import WorldGenerator

class Map:
    def __init__(self, game):
        self.game = game
        self.tile_size = TILESIZE
        self.map_data = None
        self.width = 0
        self.height = 0
        self.world_width = 0
        self.world_height = 0
        self.spawn_location = (0, 0)
        self.exits = []

    def load_map(self, map_data):
        """Load a map from the data structure"""
        self.map_data = map_data
        self.world_width = map_data["width"]
        self.world_height = map_data["height"]
        self.width = self.world_width * TILESIZE
        self.height = self.world_height * TILESIZE
        self.layers = map_data["layers"]
        self.exits = map_data.get("exits", [])
        
        # Set spawn if provided, otherwise default
        if "spawn" in map_data:
            self.spawn_location = map_data["spawn"]

    def draw(self, surface, camera):
        """Draw visible portion of map"""
        if not self.map_data:
            return

        # Calculate visible tile range
        start_x = max(0, -camera.camera.x // self.tile_size)
        end_x = min(self.world_width, (-camera.camera.x + WIDTH) // self.tile_size + 1)
        start_y = max(0, -camera.camera.y // self.tile_size)
        end_y = min(self.world_height, (-camera.camera.y + HEIGHT) // self.tile_size + 1)
        
        # Draw Ground Layer
        for row in range(start_y, end_y):
            for col in range(start_x, end_x):
                # Ground Layer
                tile = self.layers["ground"][row, col]
                self._draw_tile(surface, camera, tile, col, row)
                
                # Decoration Layer (if exists and not 0)
                if "decoration" in self.layers:
                    dec_tile = self.layers["decoration"][row, col]
                    if dec_tile != 0:
                        self._draw_tile(surface, camera, dec_tile, col, row)

    def _draw_tile(self, surface, camera, tile, col, row):
        img = None
        if tile == 0:  # GRASS
            img = self.game.resource_manager.get_image("Grass.png")
        elif tile == 1:  # DIRT
            img = self.game.resource_manager.get_image("Dirt.png")
        elif tile == 2:  # WATER
            img = self.game.resource_manager.get_image("Water.png")
        elif tile == 3:  # FOREST
            img = self.game.resource_manager.get_image("Grass.png") # Placeholder, maybe overlay?
        elif tile == 4:  # MOUNTAIN
            img = self.game.resource_manager.get_image("Dirt.png") # Placeholder
        elif tile == 5:  # WALL (Town)
            img = None 
        elif tile == 6:  # FLOOR (Town)
            img = self.game.resource_manager.get_image("Grass.png") # Use grass for floor for now to distinguish from dirt walls
            
        if img:
            screen_x = col * self.tile_size + camera.camera.x
            screen_y = row * self.tile_size + camera.camera.y
            surface.blit(img, (screen_x, screen_y))
        elif tile == 5: # WALL fallback
            screen_x = col * self.tile_size + camera.camera.x
            screen_y = row * self.tile_size + camera.camera.y
            pygame.draw.rect(surface, (100, 100, 100), (screen_x, screen_y, self.tile_size, self.tile_size))
            pygame.draw.rect(surface, (50, 50, 50), (screen_x, screen_y, self.tile_size, self.tile_size), 2)

    def check_exit(self, x, y):
        """Check if the given tile coordinate is an exit"""
        for exit_point in self.exits:
            if exit_point["x"] == x and exit_point["y"] == y:
                return exit_point
        return None
        
    def is_blocked(self, x, y):
        """Check collision"""
        if not (0 <= x < self.world_width and 0 <= y < self.world_height):
            return True
            
        # Check collision layer if it exists
        if "collision" in self.layers:
            return self.layers["collision"][y, x] == 1
            
        # Fallback to tile type collision
        tile = self.layers["ground"][y, x]
        if tile == 2: # Water
            return True
            
        return False
