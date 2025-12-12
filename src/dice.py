import random

class Die:
    def __init__(self):
        self.value = 1
        self.locked = False
        
    def roll(self):
        if not self.locked:
            self.value = random.randint(1, 6)

class DicePool:
    def __init__(self, num_dice=3):
        self.dice = [Die() for _ in range(num_dice)]
        # Allocation: Maps die_index -> attribute_name ('str', 'def', 'spd', None)
        self.allocations = {i: None for i in range(num_dice)}
        self.roll_all()
        
    def roll_all(self):
        for die in self.dice:
            die.roll()
        # Reset allocations on re-roll? Or keep them? 
        # Typically "Tactical Pause" implies you roll then allocate.
        # So we verify fresh dice every turn.
        self.allocations = {i: None for i in range(len(self.dice))}

    def allocate(self, die_index, target):
        """target: 'attack', 'defense', 'agility', or None (unallocated)"""
        if 0 <= die_index < len(self.dice):
            self.allocations[die_index] = target
            
    def get_total_bonus(self, info_type):
        total = 0
        for i, target in self.allocations.items():
            if target == info_type:
                total += self.dice[i].value
        return total
