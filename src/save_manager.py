import json
import os

class SaveManager:
    def __init__(self, game, filename='savegame.json'):
        self.game = game
        self.filename = os.path.join(os.path.dirname(__file__), filename)

    def save_game(self):
        data = {
            "hero": self.game.player.to_dict(),
            "world": {
                "map_id": self.game.current_map_id,
                "x": self.game.player.x / 32, # Save as grid coords for safety
                "y": self.game.player.y / 32
            },
            "flags": self.game.quest_manager.flags if hasattr(self.game.quest_manager, 'flags') else {}
        }
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            self.game.logger.log("Game saved successfully.")
            return True
        except Exception as e:
            self.game.logger.error(f"Failed to save game: {e}")
            return False

    def load_game(self):
        if not os.path.exists(self.filename):
            self.game.logger.warning("No save file found.")
            return False
            
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                
            # Restore World
            if "world" in data:
                self.game.load_map(data["world"]["map_id"], data["world"]["x"], data["world"]["y"])
                
            # Restore Hero
            if "hero" in data:
                self.game.player.from_dict(data["hero"])
                
            # Restore Flags
            if "flags" in data and hasattr(self.game.quest_manager, 'flags'):
                self.game.quest_manager.flags = data["flags"]
                
            self.game.logger.log("Game loaded successfully.")
            return True
        except Exception as e:
            self.game.logger.error(f"Failed to load game: {e}")
            return False
