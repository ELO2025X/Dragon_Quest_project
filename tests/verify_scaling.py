import sys
import os
import pygame
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from entities import Enemy
from settings import TILESIZE

class TestEnemyScaling(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.mock_game = MagicMock()
        self.mock_game.all_sprites = pygame.sprite.Group()
        self.mock_game.enemies = pygame.sprite.Group()
        
        # Mock DataManager
        self.mock_game.data_manager.get_data.return_value = {
            "slime": {
                "scale": 1,
                "image": "Slime.png"
            },
            "croc": {
                "scale": 2,
                "image": "Croc.png"
            }
        }
        
        # Mock ResourceManager
        # Return a 100x100 surface to simulate a high-res asset
        self.mock_image = pygame.Surface((100, 100))
        self.mock_game.resource_manager.load_image.return_value = self.mock_image

    def test_slime_scaling(self):
        enemy = Enemy(self.mock_game, 0, 0, "slime")
        # Expected size: TILESIZE * 1 = 32
        self.assertEqual(enemy.image.get_width(), TILESIZE)
        self.assertEqual(enemy.image.get_height(), TILESIZE)
        print(f"Slime size: {enemy.image.get_size()} (Expected: {TILESIZE}x{TILESIZE})")

    def test_croc_scaling(self):
        enemy = Enemy(self.mock_game, 0, 0, "croc")
        # Expected size: TILESIZE * 2 = 64
        self.assertEqual(enemy.image.get_width(), TILESIZE * 2)
        self.assertEqual(enemy.image.get_height(), TILESIZE * 2)
        print(f"Croc size: {enemy.image.get_size()} (Expected: {TILESIZE*2}x{TILESIZE*2})")

if __name__ == '__main__':
    unittest.main()
