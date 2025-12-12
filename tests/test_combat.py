
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from battle import PlayerAttackState, Battle
from components.combat import CombatComponent

class MockEntity:
    def __init__(self, name, hp, max_hp, strength, defense, level=1):
        self.name = name
        self.level = level
        self.combat = MagicMock(spec=CombatComponent)
        self.combat.hp = hp
        self.combat.max_hp = max_hp
        self.combat.get_attribute.side_effect = lambda attr: strength if attr == "strength" else (defense if attr == "defense" else (10 if attr == "luck" else 0))
        self.special_abilities = {}
        
    def get_component(self, component_type):
        return self.combat

class TestCombatLogic(unittest.TestCase):
    def setUp(self):
        self.player = MockEntity("Hero", 100, 100, strength=10, defense=5, level=5)
        self.enemy = MockEntity("Slime", 30, 30, strength=5, defense=2)
        
        self.battle = MagicMock(spec=Battle)
        self.battle.game = MagicMock()
        self.battle.player = self.player
        self.battle.enemies = [self.enemy]
        self.battle.message = ""
        self.battle.game.sound_manager = MagicMock() # Mock sound manager

    def test_damage_calculation(self):
        # Player Attack: Str(10)*2 + Lvl(5) = 25
        # Enemy Def: Def(2)*2 = 4
        # Base Damage: 21
        
        # We need to mock random to avoid crit and variation
        with patch('random.random', return_value=0.5): # No crit
            with patch('random.randint', return_value=0): # No variation
                attack_state = PlayerAttackState(self.battle, 0)
                
                # Check if take_damage was called
                self.enemy.combat.take_damage.assert_called()
                args, _ = self.enemy.combat.take_damage.call_args
                self.assertEqual(args[0], 21)
                self.assertIn("You attack Slime for 21 damage!", self.battle.message)

    def test_critical_hit(self):
        # Force crit
        with patch('random.random', return_value=0.0): # Crit!
            with patch('random.randint', return_value=0):
                attack_state = PlayerAttackState(self.battle, 0)
                
                # Base 21 * 2 = 42
                self.enemy.combat.take_damage.assert_called()
                args, _ = self.enemy.combat.take_damage.call_args
                self.assertEqual(args[0], 42)
                self.assertIn("Critical Hit!", self.battle.message)

if __name__ == '__main__':
    unittest.main()
