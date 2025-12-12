import sys
import os
import unittest
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from world_generator import WorldGenerator

class TestMapGeneration(unittest.TestCase):
    def test_land_ratio(self):
        gen = WorldGenerator(seed=12345)
        map_data = gen.generate_world_map(width=100, height=100)
        ground = map_data["layers"]["ground"]
        
        unique, counts = np.unique(ground, return_counts=True)
        tile_counts = dict(zip(unique, counts))
        
        water_count = tile_counts.get(gen.WATER, 0)
        total_tiles = 100 * 100
        land_count = total_tiles - water_count
        land_ratio = land_count / total_tiles
        
        print(f"Land Ratio: {land_ratio:.2%}")
        
        # Expect at least 10% land
        self.assertGreater(land_ratio, 0.10, "Map has too little land!")

if __name__ == '__main__':
    unittest.main()
