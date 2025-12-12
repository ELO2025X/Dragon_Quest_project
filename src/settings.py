import pygame

# Game Settings
WIDTH = 800
HEIGHT = 600
FPS = 60
TITLE = "Serpent's Quest"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)     # Hero
GREEN = (0, 255, 0)    # Slime
DARKGREY = (40, 40, 40)
GRASS_COLOR = (34, 139, 34)
DIRT_COLOR = (139, 69, 19)
WATER_COLOR = (65, 105, 225)

# Tile Settings
TILESIZE = 32
SPRITE_RENDER_SIZE = 16
SPRITE_SCALE_FACTOR = 2
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Debug Settings
DEBUG_MODE = False # Toggled with F10
DEBUG_COLOR = (255, 0, 255) # Magenta for debug visuals
DEBUG_TEXT_COLOR = (0, 255, 255) # Cyan for text
