
import sys
import os
import pygame
from unittest.mock import MagicMock

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from battle import Battle
from ui import BattleUI
from settings import WIDTH, HEIGHT

def test_ui_delegation():
    print("Verifying UI Refactor Delegation...")
    
    # Mock Game and Components
    mock_game = MagicMock()
    mock_game.screen = MagicMock()
    mock_game.battle_ui = MagicMock()
    
    # Mock Player and Enemy
    mock_player = MagicMock()
    mock_player.name = "Hero"
    mock_player.level = 1
    mock_player.combat.hp = 10
    mock_player.combat.max_hp = 10
    
    mock_enemy = MagicMock()
    mock_enemy.name = "Slime"
    
    # Initialize Battle
    battle = Battle(mock_game, mock_player, [mock_enemy])
    
    # Fake a surface
    surface = MagicMock()
    
    # Call draw
    battle.draw(surface)
    
    # Verify delegation
    # The Battle.draw calls current_state.draw
    # BattleState.draw calls game.battle_ui.draw(battle)
    
    if mock_game.battle_ui.draw.called:
        print("PASS: Battle.draw delegates to game.battle_ui.draw")
        print(f"Call args: {mock_game.battle_ui.draw.call_args}")
    else:
        print("FAIL: Battle.draw did NOT call game.battle_ui.draw")
        
    # Also verify BattleUI has the method
    real_ui = BattleUI(mock_game)
    if hasattr(real_ui, 'draw_battle'):
        print("PASS: BattleUI has draw_battle method")
    else:
        print("FAIL: BattleUI missing draw_battle method")

if __name__ == "__main__":
    pygame.init() # Needed for font init in BattleUI if we instantiated it fully, but we mocked it mostly.
    test_ui_delegation()
