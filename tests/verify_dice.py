
import sys
import os
import pygame
from unittest.mock import MagicMock

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from battle import Battle, TacticalPauseState
from dice import DicePool

def verify_dice_mechanic():
    print("Verifying One Card Dungeon (Dice System)...")
    
    # 1. Test Dice Pool
    pool = DicePool(3)
    print("Dice Pool Initialized with 3 dice.")
    assert len(pool.dice) == 3
    
    # Test Roll
    print("Rolling dice...")
    pool.roll_all()
    values = [d.value for d in pool.dice]
    print(f"Values: {values}")
    assert all(1 <= v <= 6 for v in values)
    
    # Test Allocation
    print("Allocating Die 0 to Attack...")
    pool.allocate(0, 'attack')
    assert pool.allocations[0] == 'attack'
    assert pool.get_total_bonus('attack') == pool.dice[0].value
    
    # 2. Test Battle Integration
    mock_game = MagicMock()
    mock_player = MagicMock()
    mock_game.battle_ui = MagicMock()
    
    battle = Battle(mock_game, mock_player, [])
    
    # Ensure it starts in tactical pause
    print(f"Initial State: {battle.state}")
    assert battle.state == "tactical_pause"
    assert isinstance(battle.current_state, TacticalPauseState)
    assert hasattr(battle, 'dice_pool')
    
    # Simulate Confirm
    print("Simulating Confirm Allocation...")
    battle.current_state.confirm_allocation()
    
    # Should move to main_menu
    print(f"New State: {battle.state}")
    assert battle.state == "main_menu"
    
    # Check Bonuses
    print(f"Battle Bonuses: {battle.current_bonuses}")
    # Bonuses might be 0 if we didn't allocate anything in the test simulation above (default state)
    # Let's allocate one manually before confirm for rigorous test
    battle.change_state("tactical_pause")
    battle.dice_pool.allocate(0, 'defense')
    val = battle.dice_pool.dice[0].value
    battle.current_state.confirm_allocation()
    
    assert battle.current_bonuses['defense'] == val
    print(f"Defense Bonus Verified: {val}")
    
    print("Dice System Verification: PASS")

if __name__ == "__main__":
    pygame.init()
    verify_dice_mechanic()
