
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import random
import pygame

# Initialize pygame for font usage
pygame.init()
pygame.font.init()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from battle import PlayerMagicAttackState, Battle
from components.combat import CombatComponent
from data_manager import DataManager

class MockSpell:
    def __init__(self, name, type, hits, power):
        self.name = name
        self.type = type
        self.hits = hits
        self.power = power
        self.element = "physical"
        self.cost = 0
        self.duration = 0
        self.chance = 1.0
        self.effect = None

class MockEntity:
    def __init__(self, name, hp, max_hp, strength, defense, level=1):
        self.name = name
        self.level = level
        self.combat = MagicMock(spec=CombatComponent)
        self.combat.hp = hp
        self.combat.max_hp = max_hp
        self.combat.get_attribute.side_effect = lambda attr: strength if attr == "strength" else (defense if attr == "defense" else 0)
        self.special_abilities = {}
        
    def get_component(self, component_type):
        return self.combat

class TestGladiatorFeatures(unittest.TestCase):
    def setUp(self):
        self.game = MagicMock()
        self.data_manager = DataManager(self.game)
        self.data_manager.load_data()
        self.player = MockEntity("Hero", 100, 100, strength=10, defense=5, level=5)
        self.enemy = MockEntity("Slime", 100, 100, strength=5, defense=2)
        
        self.battle = MagicMock(spec=Battle)
        self.battle.game = MagicMock()
        self.battle.player = self.player
        self.battle.enemies = [self.enemy]
        self.battle.message = ""
        self.battle.active_effects = []
        self.battle.game.battle_ui.x = 0
        self.battle.game.battle_ui.y = 0

    def test_json_validity(self):
        # This will fail if JSON is invalid
        jobs = self.data_manager.get_data("jobs")
        self.assertIn("gladiator", jobs)
        self.assertEqual(jobs["gladiator"]["name"], "Gladiator")
        
        spells = self.data_manager.get_data("spells")
        self.assertIn("double_slash", spells)
        self.assertEqual(spells["double_slash"]["type"], "multi_hit")

    def test_double_slash_logic(self):
        # Mock Double Slash spell
        double_slash = MockSpell("Double Slash", "multi_hit", hits=2, power=0.8)
        
        # Force no randomness for consistent damage
        # base = 10 * 0.8 = 8.
        # def = 2. dmg = 8 - 1 = 7.
        with patch('random.randint', return_value=0):
             with patch('random.random', return_value=0.5):
                state = PlayerMagicAttackState(self.battle, 0, double_slash)
                
                # Should hit 2 times
                self.assertEqual(self.enemy.combat.take_damage.call_count, 2)
                
                # Verify Battle message mentions hits
                self.assertIn("Hit 2 times", self.battle.message)

if __name__ == '__main__':
    unittest.main()
