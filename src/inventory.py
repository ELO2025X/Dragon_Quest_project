# inventory.py
import json
import os
import random
import copy

def load_items():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'items.json')
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            return json.load(f)
    return {}

# Global Templates
ITEM_TEMPLATES = load_items()

# Affix Definitions
AFFIXES = {
    "Sharp": {"stats": {"strength": 2}, "cost_mult": 1.2},
    "Heavy": {"stats": {"strength": 4, "agility": -2}, "cost_mult": 1.3},
    "Quick": {"stats": {"agility": 3}, "cost_mult": 1.2},
    "Mystic": {"stats": {"intelligence": 3}, "cost_mult": 1.4},
    "Broken": {"stats": {"strength": -1}, "cost_mult": 0.5},
    "Legendary": {"stats": {"strength": 5, "agility": 5, "intelligence": 5}, "cost_mult": 3.0}
}

class Item:
    def __init__(self, item_id, template=None):
        self.item_id = item_id
        if template is None:
            template = ITEM_TEMPLATES.get(item_id, {})
        
        self.name = template.get("name", "Unknown Item")
        self.type = template.get("type", "misc")
        self.slot = self.type # Map type to slot for equipment logic
        self.stats = copy.deepcopy(template.get("stats", {}))
        self.power = template.get("power", 0)
        self.element = template.get("element", None)
        self.effect = template.get("effect", None)
        self.description = template.get("description", "")
        self.icon = template.get("icon", None)
        self.affix = None
        
    def add_affix(self, affix_name):
        if affix_name in AFFIXES:
            self.affix = affix_name
            data = AFFIXES[affix_name]
            
            # Update Name
            self.name = f"{affix_name} {self.name}"
            
            # Update Stats
            for stat, val in data["stats"].items():
                self.stats[stat] = self.stats.get(stat, 0) + val
                
            # Update Description
            stat_str = ", ".join([f"{k} {'+' if v>0 else ''}{v}" for k,v in data["stats"].items()])
            self.description += f" ({stat_str})"

def create_item(item_id):
    """Factory method to create a basic item."""
    if item_id in ITEM_TEMPLATES:
        return Item(item_id)
    return None

def create_random_weapon(base_types=None):
    """Creates a weapon with a random affix."""
    if base_types is None:
        # Filter for weapons in templates
        base_types = [k for k, v in ITEM_TEMPLATES.items() if v.get("type") == "weapon"]
    
    if not base_types:
        return None
        
    item_id = random.choice(base_types)
    item = Item(item_id)
    
    # 50% chance for an affix
    if random.random() < 0.5:
        affix = random.choice(list(AFFIXES.keys()))
        item.add_affix(affix)
        
    return item

# Skill definitions (Kept as is for now)
SKILLS = {
    "Heal": {
        "type": "spell",
        "mp_cost": 5,
        "effect": lambda player: player.heal(20)
    },
    "Fireball": {
        "type": "spell",
        "mp_cost": 10,
        "effect": None 
    },
    "Sword Mastery": {
        "type": "passive",
        "stat_bonus": {"strength": 1}
    },
    "Stealth": {
        "type": "passive",
        "stat_bonus": {"agility": 1}
    }
}
