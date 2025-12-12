# DragonQuest/src/components/serialization.py
from components.component import Component
from components.combat import CombatComponent
from components.inventory import InventoryComponent

class SerializationComponent(Component):
    def __init__(self, owner):
        super().__init__(owner)
        self.combat_component = self.owner.get_component(CombatComponent)
        self.inventory_component = self.owner.get_component(InventoryComponent)

    def to_dict(self):
        if not self.combat_component or not self.inventory_component:
            return {}

        return {
            "level": self.owner.level,
            "xp": self.owner.xp,
            "gold": self.owner.gold,
            "hp": self.combat_component.hp,
            "max_hp": self.combat_component.max_hp,
            "mp": self.combat_component.mp,
            "max_mp": self.combat_component.max_mp,
            "stats": {
                "strength": self.combat_component.stats[0],
                "defense": self.combat_component.stats[1],
                "agility": self.combat_component.stats[2],
                "luck": self.combat_component.stats[3]
            },
            "skills": self.owner.skills,
            "job": self.owner.job,
            "jp": self.owner.jp,
            "mastered_jobs": self.owner.mastered_jobs,
            "status_effects": self.combat_component.status_effects,
            "inventory": self.inventory_component.items,
            "equipment": self.inventory_component.equipment,
        }

    def from_dict(self, data):
        if not self.combat_component or not self.inventory_component:
            return

        self.owner.level = data.get("level", 1)
        self.owner.xp = data.get("xp", 0)
        self.owner.gold = data.get("gold", 0)
        self.combat_component.hp = data.get("hp", 50)
        self.combat_component.max_hp = data.get("max_hp", 50)
        self.combat_component.mp = data.get("mp", 20)
        self.combat_component.max_mp = data.get("max_mp", 20)
        stats_data = data.get("stats", {})
        self.combat_component.stats[0] = stats_data.get("strength", 5)
        self.combat_component.stats[1] = stats_data.get("defense", 3)
        self.combat_component.stats[2] = stats_data.get("agility", 4)
        self.combat_component.stats[3] = stats_data.get("luck", 3)
        self.owner.skills = data.get("skills", [])
        self.owner.job = data.get("job", "warrior")
        self.owner.jp = data.get("jp", 0)
        self.owner.mastered_jobs = data.get("mastered_jobs", [])
        self.combat_component.status_effects = data.get("status_effects", {})
        self.inventory_component.items = data.get("inventory", [])
        self.inventory_component.equipment = data.get("equipment", {"weapon": None, "armor": None, "accessory": None})
