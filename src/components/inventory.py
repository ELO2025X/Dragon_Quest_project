# DragonQuest/src/components/inventory.py
from components.component import Component

class InventoryComponent(Component):
    def __init__(self, owner, items=None, equipment=None):
        super().__init__(owner)
        self.items = items if items is not None else []
        self.equipment = equipment if equipment is not None else {"weapon": None, "armor": None, "accessory": None}

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def equip(self, item):
        if item.slot in self.equipment:
            self.unequip(item.slot)
            self.equipment[item.slot] = item
            self.items.remove(item)
            return True
        return False

    def unequip(self, slot):
        if slot in self.equipment and self.equipment[slot]:
            item = self.equipment[slot]
            self.equipment[slot] = None
            self.add_item(item)
            return True
        return False
