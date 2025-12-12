import sys
import os
import pygame

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock pygame for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1,1))

from spell import SpellDatabase
from combat_item import ItemDatabase
from quest import QuestManager, Quest
from entities import Player

class MockGame:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.resource_manager = MockResourceManager()
        self.logger = MockLogger()
        self.data_manager = MockDataManager()

class MockResourceManager:
    def load_image(self, name):
        return pygame.Surface((32, 32))

class MockLogger:
    def debug(self, msg): pass
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")

class MockDataManager:
    def get_data(self, key): return {}

def test_spells():
    print("Testing Spells...")
    db = SpellDatabase()
    heal = db.get_spell("heal")
    assert heal is not None
    assert heal.name == "Heal"
    assert heal.cost == 5
    print("Spells OK")

def test_items():
    print("Testing Items...")
    db = ItemDatabase()
    potion = db.get_item("potion")
    assert potion is not None
    assert potion.name == "Potion"
    assert potion.power == 30
    print("Items OK")

def test_quest_logic():
    print("Testing Quest Logic...")
    game = MockGame()
    qm = QuestManager(game)
    
    # Test Find Quest
    player = Player(game, 0, 0)
    player.inventory_items = {"potion": 0}
    
    quest = qm.available_quests[3] # Potion Master
    qm.accept_quest(3)
    
    assert not quest.completed
    
    # Give items
    player.inventory_items["potion"] = 3
    qm.check_quests(player)
    
    assert quest.completed
    print("Quest Logic OK")

if __name__ == "__main__":
    try:
        test_spells()
        test_items()
        test_quest_logic()
        print("All RPG System Tests Passed!")
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
