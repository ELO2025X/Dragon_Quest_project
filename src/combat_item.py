import json
import os

class CombatItem:
    def __init__(self, item_id, data):
        self.item_id = item_id
        self.name = data.get("name", "Unknown Item")
        self.type = data.get("type", "damage") # damage, healing, restore_mp
        self.power = data.get("power", 0)
        self.element = data.get("element", "neutral")
        self.description = data.get("description", "")

class ItemDatabase:
    def __init__(self):
        self.items = {}
        self.load_items()

    def load_items(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'items.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                for item_id, item_data in data.items():
                    self.items[item_id] = CombatItem(item_id, item_data)
        else:
            print("Warning: items.json not found.")

    def get_item(self, item_id):
        return self.items.get(item_id)
