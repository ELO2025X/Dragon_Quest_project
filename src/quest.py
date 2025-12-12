class Quest:
    def __init__(self, quest_id, name, description, quest_type, target, reward_xp, reward_gold, reward_spell=None):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.quest_type = quest_type  # "kill", "talk", "find"
        self.target = target  # e.g., "slime" for kill quests
        self.progress = 0
        self.goal = 1
        self.completed = False
        self.reward_xp = reward_xp
        self.reward_gold = reward_gold
        self.reward_spell = reward_spell  # Spell name to learn
    
    def update_progress(self, amount=1):
        """Increase quest progress"""
        if self.completed: return
        self.progress += amount
        if self.progress >= self.goal:
            self.completed = True

    def check_condition(self, player):
        """Check if quest condition is met (for 'find' quests)"""
        if self.completed: return True
        
        if self.quest_type == "find":
            # Check player inventory for target item
            # Assuming target is item_id
            count = player.inventory_items.get(self.target, 0)
            self.progress = count
            if self.progress >= self.goal:
                self.completed = True
                return True
        return False

class QuestManager:
    def __init__(self, game):
        self.game = game
        self.active_quests = []
        self.completed_quests = []
        self.flags = {}  # Story flags
        # Load quests from JSON file if present
        self.available_quests = self._load_quests_from_file()

    def _load_quests_from_file(self):
        """Load quest definitions from src/data/quests.json"""
        import json, os
        quests = {}
        # For now, hardcode extended quests to avoid file dependency issues during this step
        # In a full implementation, this would load from JSON
        return self._create_default_quests()

    def _create_default_quests(self):
        """Define default quests"""
        quests = {
            1: Quest(
                quest_id=1,
                name="Slime Slayer",
                description="Defeat 5 slimes to prove your worth!",
                quest_type="kill",
                target="slime",
                reward_xp=50,
                reward_gold=25,
                reward_spell="heal"
            ),
            2: Quest(
                quest_id=2,
                name="Meet the Wizard",
                description="Find and talk to the Wizard in the northern town.",
                quest_type="talk",
                target="wizard",
                reward_xp=30,
                reward_gold=15,
                reward_spell="fireball"
            ),
            3: Quest(
                quest_id=3,
                name="Potion Master",
                description="Bring 3 Potions to the Merchant.",
                quest_type="find",
                target="potion",
                reward_xp=100,
                reward_gold=50
            )
        }
        quests[1].goal = 5
        quests[3].goal = 3
        return quests
    
    def accept_quest(self, quest_id):
        """Add a quest to active quests"""
        if quest_id in self.available_quests:
            quest = self.available_quests[quest_id]
            if quest not in self.active_quests and quest not in self.completed_quests:
                self.active_quests.append(quest)
                print(f"Accepted quest: {quest.name}")
                return True
        return False
    
    def update_kill_quest(self, enemy_type):
        """Update progress for kill quests"""
        for quest in self.active_quests:
            if quest.quest_type == "kill" and quest.target.lower() in enemy_type.lower():
                quest.update_progress()
                if quest.completed:
                    print(f"Quest Complete: {quest.name}")
    
    def check_quests(self, player):
        """Check all active quests for completion (mainly for 'find' type)"""
        for quest in self.active_quests:
            if quest.check_condition(player):
                print(f"Quest Complete: {quest.name}")

    def complete_quest(self, quest_id, player):
        """Complete a quest and give rewards"""
        quest = None
        for q in self.active_quests:
            if q.quest_id == quest_id:
                quest = q
                break
        
        if quest and quest.completed:
            # Give rewards
            player.xp += quest.reward_xp
            player.gold += quest.reward_gold
            
            # Learn spell if reward
            if quest.reward_spell:
                if quest.reward_spell not in player.known_spells:
                    player.known_spells.append(quest.reward_spell)
                    print(f"Learned spell: {quest.reward_spell}")
            
            # Move to completed
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)
            self.flags[f"quest_{quest_id}_completed"] = True
            
            return True
        return False
