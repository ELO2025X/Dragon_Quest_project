import json
import os
import random

class Spell:
    def __init__(self, spell_id, data):
        self.spell_id = spell_id
        self.name = data.get("name", "Unknown Spell")
        self.cost = data.get("cost", 0)
        self.power = data.get("power", 0)
        self.type = data.get("type", "damage") # damage, healing, status
        self.element = data.get("element", "neutral")
        self.description = data.get("description", "")
        self.effect = data.get("effect", None)
        self.duration = data.get("duration", 0)
        self.chance = data.get("chance", 1.0)

class SpellDatabase:
    def __init__(self):
        self.spells = {}
        self.load_spells()

    def load_spells(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'spells.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                for spell_id, spell_data in data.items():
                    self.spells[spell_id] = Spell(spell_id, spell_data)
        else:
            print("Warning: spells.json not found.")

    def get_spell(self, spell_id):
        return self.spells.get(spell_id)
