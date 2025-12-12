# DragonQuest/src/components/combat.py
import numpy as np
from components.component import Component

class CombatComponent(Component):
    def __init__(self, owner, hp, mp, stats, xp_reward=0, gold_reward=0):
        super().__init__(owner)
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.stats = np.array(stats, dtype=np.int16)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.status_effects = {}

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def restore_mp(self, amount):
        self.mp += amount
        if self.mp > self.max_mp:
            self.mp = self.max_mp

    def is_alive(self):
        return self.hp > 0

    def get_attribute(self, attr):
        attr_map = {"strength": 0, "defense": 1, "agility": 2, "luck": 3}
        if attr in attr_map:
            base = self.stats[attr_map[attr]]
        else:
            base = getattr(self.owner, attr, 0)
            
        bonus = 0
        # Equipment bonuses will be handled by the InventoryComponent
        # For now, just return the base stat
        return base

    def apply_status_effect(self, effect_name, duration):
        self.status_effects[effect_name] = duration

    def has_status_effect(self, effect_name):
        return self.status_effects.get(effect_name, 0) > 0

    def update(self, dt):
        # Update status effects
        for effect, duration in list(self.status_effects.items()):
            duration -= 1
            if duration <= 0:
                del self.status_effects[effect]
            else:
                self.status_effects[effect] = duration
