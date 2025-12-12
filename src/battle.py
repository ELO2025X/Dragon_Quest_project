import pygame
import random
import numpy as np
import math
from settings import *
from components.combat import CombatComponent
from spell import SpellDatabase
from combat_item import ItemDatabase
from combat_effects import FlashEffect, DamageNumber, ScreenShake
from typing import List, Dict, Optional, Any, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game
    from entities import Entity


class BattleState:
    def __init__(self, battle: 'Battle'):
        self.battle = battle

    def handle_input(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        self.battle.game.battle_ui.draw(self.battle)

class MainMenuState(BattleState):
    def __init__(self, battle):
        super().__init__(battle)
        self.options = ["Attack", "Magic", "Items", "Run"]
        self.selected_option = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("menu")
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("menu")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.execute_option()

    def execute_option(self):
        if self.options[self.selected_option] == "Attack":
            if len(self.battle.enemies) > 1:
                self.battle.change_state("target_selection")
            else:
                self.battle.change_state("player_attack", target_index=0)
        elif self.options[self.selected_option] == "Magic":
            self.battle.change_state("magic_menu")
        elif self.options[self.selected_option] == "Items":
            self.battle.change_state("item_menu")
        elif self.options[self.selected_option] == "Run":
            self.battle.change_state("run")

class TargetSelectionState(BattleState):
    def __init__(self, battle, **kwargs):
        super().__init__(battle)
        self.selected_target = 0
        self.spell = kwargs.get('spell')
        self.item = kwargs.get('item')

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_target = (self.selected_target - 1) % len(self.battle.enemies)
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("menu")
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_target = (self.selected_target + 1) % len(self.battle.enemies)
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("menu")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if 'spell' in self.__dict__: # Check if spell was passed in kwargs (stored in self) - wait, kwargs are not auto-stored.
                     # Need to store kwargs in init
                     pass
                
                # Re-implement TargetSelection to handle spells/items
                if hasattr(self, 'spell'):
                    self.battle.change_state("player_magic_attack", target_index=self.selected_target, spell=self.spell)
                elif hasattr(self, 'item'):
                    self.battle.change_state("player_item_attack", target_index=self.selected_target, item=self.item)
                else:
                    self.battle.change_state("player_attack", target_index=self.selected_target)
            elif event.key == pygame.K_ESCAPE:
                self.battle.change_state("main_menu")

class PlayerAttackState(BattleState):
    def __init__(self, battle, target_index):
        super().__init__(battle)
        self.target_index = target_index
        self.player_attack()

    def player_attack(self):
        target_enemy = self.battle.enemies[self.target_index]
        attack_power = self.battle.player.combat.get_attribute("strength") * 2 + self.battle.player.level
        defense_power = target_enemy.get_component(CombatComponent).get_attribute("defense") * 2
        
        base_damage = np.subtract(attack_power, defense_power)
        base_damage = np.maximum(1, base_damage)
        
        crit_chance = self.battle.player.combat.get_attribute("luck") * 0.02
        is_crit = random.random() < crit_chance
        
        if is_crit:
            base_damage *= 2
            self.battle.message = "Critical Hit! "
        else:
            self.battle.message = ""
        
        damage = int(base_damage + random.randint(-1, 1))
        target_enemy.get_component(CombatComponent).take_damage(damage)
        
        # Visual Effects
        self.battle.add_effect(FlashEffect(color=(255, 255, 255), duration=0.1))
        ex = self.battle.game.battle_ui.x + 280 + self.target_index * 140 + 50
        ey = self.battle.game.battle_ui.y + 110
        self.battle.add_effect(DamageNumber(damage, ex, ey, color=(255, 200, 50)))
        
        self.battle.message += f"You attack {target_enemy.name} for {damage} damage!"
        if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("attack")
        
        if hasattr(self.battle.game, 'message_log'):
            self.battle.game.message_log.log_combat(self.battle.message)

        if 'heal_on_hit' in target_enemy.special_abilities and target_enemy.get_component(CombatComponent).is_alive():
            ability = target_enemy.special_abilities['heal_on_hit']
            if random.random() < ability['chance']:
                target_enemy.get_component(CombatComponent).heal(ability['amount'])
                heal_message = f"\n{target_enemy.name} radiates a faint glow and heals for {ability['amount']} HP!"
                self.battle.message += heal_message
                if hasattr(self.battle.game, 'message_log'):
                    self.battle.game.message_log.log_combat(f"{target_enemy.name} healed itself for {ability['amount']} HP.")

        if 'call_for_help' in target_enemy.special_abilities and target_enemy.get_component(CombatComponent).is_alive():
            ability = target_enemy.special_abilities['call_for_help']
            if target_enemy.get_component(CombatComponent).hp / target_enemy.get_component(CombatComponent).max_hp < ability['hp_threshold']:
                if random.random() < ability['chance'] and len(self.battle.enemies) < 3:
                    new_enemy_type = ability['enemy_type']
                    new_enemy = self.battle.game.create_enemy(new_enemy_type)
                    self.battle.enemies.append(new_enemy)
                    self.battle.message += f"\n{target_enemy.name} calls for help!"
                    if hasattr(self.battle.game, 'message_log'):
                        self.battle.game.message_log.log_combat(f"{target_enemy.name} called for help!")

        if target_enemy.get_component(CombatComponent).hp <= 0:
            defeated_enemy = self.battle.enemies.pop(self.target_index)
            self.battle.rewards["xp"] += defeated_enemy.get_component(CombatComponent).xp_reward
            self.battle.rewards["gold"] += defeated_enemy.get_component(CombatComponent).gold_reward
            
            # Handle Loot
            if hasattr(defeated_enemy, 'loot') and defeated_enemy.loot:
                if "items" not in self.battle.rewards:
                    self.battle.rewards["items"] = []
                self.battle.rewards["items"].extend(defeated_enemy.loot)
                self.battle.message += f"\nDropped {', '.join(defeated_enemy.loot)}!"
                
                # Add to player inventory
                from inventory import create_item
                for item_name in defeated_enemy.loot:
                    new_item = create_item(item_name)
                    if new_item:
                        self.battle.player.inventory.add_item(new_item)

            if hasattr(self.battle.game, 'quest_manager'):
                self.battle.game.quest_manager.update_kill_quest(defeated_enemy.enemy_type)
            self.battle.message = f"{defeated_enemy.name} defeated!"
            if hasattr(self.battle.game, 'message_log'):
                self.battle.game.message_log.log_combat(f"{defeated_enemy.name} defeated!")
            defeated_enemy.kill()

            if not self.battle.enemies:
                self.battle.change_state("victory")
            else:
                self.battle.change_state("ally_turn")
        else:
            self.battle.change_state("ally_turn")

class MagicMenuState(BattleState):
    def __init__(self, battle, **kwargs):
        super().__init__(battle)
        self.spells = battle.player.known_spells # List of spell IDs
        self.selected_magic = 0
        self.spell_db = battle.spell_db

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_magic = (self.selected_magic - 1) % (len(self.spells) + 1)
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("menu")
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_magic = (self.selected_magic + 1) % (len(self.spells) + 1)
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("menu")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.execute_magic()
            elif event.key == pygame.K_ESCAPE:
                self.battle.change_state("main_menu")

    def execute_magic(self):
        if self.selected_magic == len(self.spells): # Back option
            self.battle.change_state("main_menu")
            return

        spell_id = self.spells[self.selected_magic]
        spell = self.spell_db.get_spell(spell_id)
        
        if not spell:
            return

        if self.battle.player.combat.mp >= spell.cost:
            self.battle.player.combat.mp -= spell.cost
            
            if spell.type == "healing":
                heal_amount = spell.power + self.battle.player.level * 2
                self.battle.player.combat.hp = min(self.battle.player.combat.max_hp, self.battle.player.combat.hp + heal_amount)
                self.battle.message = f"Cast {spell.name}! Recovered {heal_amount} HP!"
                if hasattr(self.battle.game, 'message_log'):
                    self.battle.game.message_log.log_combat(f"Healed for {heal_amount} HP")
                self.battle.change_state("ally_turn")
                
            elif spell.type == "damage":
                if len(self.battle.enemies) > 1:
                    self.battle.change_state("target_selection", spell=spell)
                else:
                    self.battle.change_state("player_magic_attack", target_index=0, spell=spell)
            
            elif spell.type == "status":
                 if len(self.battle.enemies) > 1:
                    self.battle.change_state("target_selection", spell=spell)
                 else:
                    self.battle.change_state("player_magic_attack", target_index=0, spell=spell)

        else:
            self.battle.message = "Not enough MP!"

class PlayerMagicAttackState(BattleState):
    def __init__(self, battle, target_index, spell):
        super().__init__(battle)
        self.target_index = target_index
        self.spell = spell
        self.cast_spell()

    def cast_spell(self):
        target_enemy = self.battle.enemies[self.target_index]
        
        if self.spell.type == "damage":
            damage = self.spell.power + self.battle.player.combat.get_attribute("strength") // 2
            # Simple element check (can be expanded)
            damage = int(damage * (1.0 + random.uniform(-0.1, 0.1)))
            target_enemy.get_component(CombatComponent).take_damage(damage)
            
            # Effects
            self.battle.add_effect(FlashEffect(color=(100, 100, 255), duration=0.2)) # Blue flash for magic
            ex = self.battle.game.battle_ui.x + 280 + self.target_index * 140 + 50
            ey = self.battle.game.battle_ui.y + 110
            self.battle.add_effect(DamageNumber(damage, ex, ey, color=(100, 150, 255)))
            
            self.battle.message = f"Cast {self.spell.name} on {target_enemy.name} for {damage} damage!"
            
        elif self.spell.type == "status":
             if random.random() < self.spell.chance:
                 target_enemy.get_component(CombatComponent).apply_status_effect(self.spell.effect, self.spell.duration)
                 self.battle.message = f"Cast {self.spell.name}! {target_enemy.name} is {self.spell.effect}!"
             else:
                 self.battle.message = f"Cast {self.spell.name}! But it failed!"

        elif self.spell.type == "multi_hit":
            hits = getattr(self.spell, 'hits', 2)
            power_mult = getattr(self.spell, 'power', 0.8)
            total_damage = 0
            
            self.battle.message = f"Cast {self.spell.name}!"
            
            for i in range(hits):
                base_dmg = self.battle.player.combat.get_attribute("strength") * power_mult
                # Defense check? Maybe reduce defense effectiveness for rapid hits or keep standard
                defense = target_enemy.get_component(CombatComponent).get_attribute("defense")
                dmg = max(1, int(base_dmg - defense / 2))
                dmg = int(dmg + random.randint(-1, 1))
                
                target_enemy.get_component(CombatComponent).take_damage(dmg)
                total_damage += dmg
                
                # Effects per hit
                self.battle.add_effect(FlashEffect(color=(255, 255, 200), duration=0.1))
                ex = self.battle.game.battle_ui.x + 280 + self.target_index * 140 + 50 + random.randint(-20, 20)
                ey = self.battle.game.battle_ui.y + 110 + random.randint(-20, 20)
                self.battle.add_effect(DamageNumber(dmg, ex, ey, color=(255, 255, 200)))
                
            self.battle.message += f"\nHit {hits} times for {total_damage} total damage!"

        if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("magic") # Assuming magic sound exists
        
        if target_enemy.get_component(CombatComponent).hp <= 0:
            defeated_enemy = self.battle.enemies.pop(self.target_index)
            self.battle.rewards["xp"] += defeated_enemy.get_component(CombatComponent).xp_reward
            self.battle.rewards["gold"] += defeated_enemy.get_component(CombatComponent).gold_reward
            if hasattr(self.battle.game, 'quest_manager'):
                self.battle.game.quest_manager.update_kill_quest(defeated_enemy.enemy_type)
            self.battle.message += f"\n{defeated_enemy.name} defeated!"
            defeated_enemy.kill()

            if not self.battle.enemies:
                self.battle.change_state("victory")
            else:
                self.battle.change_state("ally_turn")
        else:
            self.battle.change_state("ally_turn")

class ItemMenuState(BattleState):
    def __init__(self, battle, **kwargs):
        super().__init__(battle)
        # Group items by name
        self.grouped_items = {}
        for item in battle.player.inventory.items:
            # Only list usable items (potions, ether, bombs, etc.)
            # Exclude weapons/armor/misc if not usable in battle
            # For now, let's include anything with 'type' in healing/restore_mp/damage
            if item.type in ["healing", "restore_mp", "damage"]:
                if item.name not in self.grouped_items:
                    self.grouped_items[item.name] = []
                self.grouped_items[item.name].append(item)
        
        self.item_names = list(self.grouped_items.keys())
        self.selected_item = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_item = (self.selected_item - 1) % (len(self.item_names) + 1)
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("menu")
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_item = (self.selected_item + 1) % (len(self.item_names) + 1)
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("menu")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.execute_item()
            elif event.key == pygame.K_ESCAPE:
                self.battle.change_state("main_menu")

    def execute_item(self):
        if self.selected_item == len(self.item_names): # Back option
            self.battle.change_state("main_menu")
            return

        item_name = self.item_names[self.selected_item]
        items = self.grouped_items[item_name]
        
        if not items:
            return 
            
        item = items.pop() # Take one item
        self.battle.player.inventory.remove_item(item)
        
        if not items:
            self.item_names.remove(item_name)
            del self.grouped_items[item_name]
            self.selected_item = 0

        if item.type == "healing":
            self.battle.player.combat.heal(item.power)
            self.battle.message = f"Used {item.name}! Recovered {item.power} HP!"
            self.battle.change_state("ally_turn")
        elif item.type == "restore_mp":
            self.battle.player.combat.restore_mp(item.power)
            self.battle.message = f"Used {item.name}! Recovered {item.power} MP!"
            self.battle.change_state("ally_turn")
        elif item.type == "damage":
             if len(self.battle.enemies) > 1:
                self.battle.change_state("target_selection", item=item)
             else:
                self.battle.change_state("player_item_attack", target_index=0, item=item)

class PlayerItemAttackState(BattleState):
    def __init__(self, battle, target_index, item):
        super().__init__(battle)
        self.target_index = target_index
        self.item = item
        self.use_item()

    def use_item(self):
        target_enemy = self.battle.enemies[self.target_index]
        damage = self.item.power
        target_enemy.get_component(CombatComponent).take_damage(damage)
        self.battle.message = f"Used {self.item.name} on {target_enemy.name} for {damage} damage!"
        
        if target_enemy.get_component(CombatComponent).hp <= 0:
            defeated_enemy = self.battle.enemies.pop(self.target_index)
            self.battle.rewards["xp"] += defeated_enemy.get_component(CombatComponent).xp_reward
            self.battle.rewards["gold"] += defeated_enemy.get_component(CombatComponent).gold_reward
            if hasattr(self.battle.game, 'quest_manager'):
                self.battle.game.quest_manager.update_kill_quest(defeated_enemy.enemy_type)
            self.battle.message += f"\n{defeated_enemy.name} defeated!"
            defeated_enemy.kill()

            if not self.battle.enemies:
                self.battle.change_state("victory")
            else:
                self.battle.change_state("ally_turn")
        else:
            self.battle.change_state("ally_turn")

class RunState(BattleState):
    def __init__(self, battle, **kwargs):
        super().__init__(battle)
        self.run()

    def run(self):
        escape_chance = 0.5 + (self.battle.player.combat.get_attribute("agility") * 0.03)
        if random.random() < escape_chance:
            self.battle.message = "Escaped successfully!"
            self.battle.active = False
            self.battle.game.in_battle = False
            if hasattr(self.battle.game, 'message_log'):
                self.battle.game.message_log.log_combat("Escaped successfully!")
        else:
            self.battle.message = "Can't escape!"
            self.battle.change_state("ally_turn")

class AllyTurnState(BattleState):
    def __init__(self, battle, **kwargs):
        super().__init__(battle)
        self.ally_attack()

    def ally_attack(self):
        full_message = ""
        if not self.battle.allies:
            self.battle.change_state("enemy_turn")
            return

        for ally in self.battle.allies:
            if not self.battle.enemies:
                break
                
            # Drunk Logic
            roll = random.random()
            
            if roll < 0.2: # 20% Stumble/Do nothing
                actions = [
                    f"{ally.name} takes a sip of beer.",
                    f"{ally.name} stumbles and misses a turn.",
                    f"{ally.name} burps loudly.",
                    f"{ally.name} argues with a ghost.",
                    f"{ally.name} forgets where he is."
                ]
                full_message += random.choice(actions) + "\n"
                
            elif roll < 0.3: # 10% Heal Player (Toss Beer)
                heal_amount = 15
                self.battle.player.combat.heal(heal_amount)
                full_message += f"{ally.name} tosses a cold one to the Hero! Healed {heal_amount} HP!\n"
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("drink") # Placeholder
                
            elif roll < 0.4: # 10% Attack Nothing
                full_message += f"{ally.name} swings wildly at thin air!\n"
                
            else: # 60% Attack Random Enemy
                target = random.choice(self.battle.enemies)
                damage = random.randint(5, 15)
                target.get_component(CombatComponent).take_damage(damage)
                full_message += f"{ally.name} drunkenly brawls with {target.name} for {damage} damage!\n"
                
                if target.get_component(CombatComponent).hp <= 0:
                    defeated_enemy = target
                    self.battle.enemies.remove(defeated_enemy)
                    self.battle.rewards["xp"] += defeated_enemy.get_component(CombatComponent).xp_reward
                    self.battle.rewards["gold"] += defeated_enemy.get_component(CombatComponent).gold_reward
                    full_message += f"{defeated_enemy.name} was knocked out!\n"
                    defeated_enemy.kill()

        if not self.battle.enemies:
            self.battle.change_state("victory")
        else:
            self.battle.message = full_message.strip()
            # If message is empty (unlikely), just say allies are ready
            if not self.battle.message:
                self.battle.message = "The boys are ready to rumble."
            
            # We need to show the message, so maybe wait for input or just delay?
            # For now, let's just transition to enemy turn but keep the message?
            # The BattleState usually renders the message.
            # But if we switch immediately to EnemyTurn, the message might be overwritten.
            # Let's make EnemyTurn append to the message or wait?
            # Actually, standard flow here seems to be: state does action -> sets message -> changes state.
            # But if we change state immediately, the draw loop might not show it long enough.
            # However, EnemyTurn also sets message.
            # Let's chain them: Player -> Ally -> Enemy.
            # To make sure user sees Ally message, we might need a "Wait" state or just append to a log.
            # For now, I'll let EnemyTurn overwrite it, which is bad.
            # I'll make EnemyTurn append its message to the existing one if it's not empty?
            # Or better, I'll add a "AllyActionDisplay" state that waits for enter?
            # No, let's just have AllyTurnState wait for input?
            # The current system seems to be: Action -> Message -> Next State immediately.
            # Except Victory/Defeat wait for input.
            # Let's make AllyTurnState wait for input if there was an action.
            pass

        # To allow reading the funny text, let's not change state immediately if there is text.
        # But the structure calls ally_attack in __init__.
        # So we need to handle input to proceed.
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                 self.battle.change_state("enemy_turn")

class EnemyTurnState(BattleState):
    def __init__(self, battle, **kwargs):
        super().__init__(battle)
        self.enemy_attack()

    def handle_special_enemy_logic(self, enemy, full_message):
        # Daryl Ledeay Logic
        if enemy.enemy_type == "daryl_ledeay":
            # 5% Self Damage (Trip) - Reduced from 10%
            if random.random() < 0.05:
                self_dmg = int(enemy.get_component(CombatComponent).max_hp * 0.10)
                enemy.get_component(CombatComponent).take_damage(self_dmg)
                full_message += f"\n{enemy.name} trips over a garden gnome! Takes {self_dmg} damage!\nDaryl: 'Dang it! That wasn't supposed to happen!'"
                return full_message, True # Skip attack

            # 10% Critical Hit (Lucky Swing) - Reduced from 15%
            is_crit = random.random() < 0.10
            damage_mult = 2.5 if is_crit else 1.0
            if is_crit:
                full_message += f"\n{enemy.name}: 'Woooo! See that, George? Musta been the new lucky socks!'"
            return full_message, False, damage_mult

        # Chicken George Logic
        elif enemy.enemy_type == "chicken_george":
            # 20% Pity Heal
            if random.random() < 0.20:
                heal_amount = int(self.battle.player.combat.max_hp * 0.15)
                self.battle.player.combat.heal(heal_amount)
                full_message += f"\n{enemy.name} tosses a Mystery Energy Drink at you! Recovered {heal_amount} HP!\nGeorge: 'Aw, shucks. Looks like we gotta try harder.'"
                return full_message, True # Skip attack

            # 10% Bud Light Boost (Buff Daryl)
            if random.random() < 0.10:
                daryl = next((e for e in self.battle.enemies if e.enemy_type == "daryl_ledeay"), None)
                if daryl:
                    daryl.get_component(CombatComponent).stats['defense'] += 50
                    full_message += f"\n{enemy.name} shares a cold one with Daryl! Daryl's Defense rose sharply!"
                    return full_message, True # Skip attack

        return full_message, False, 1.0

    def enemy_attack(self):
        full_message = ""
        for enemy in self.battle.enemies:
            skip_attack = False
            damage_mult = 1.0
            
            # Special Logic Hook
            if enemy.enemy_type in ["daryl_ledeay", "chicken_george"]:
                res = self.handle_special_enemy_logic(enemy, full_message)
                if len(res) == 2:
                    full_message, skip_attack = res
                else:
                    full_message, skip_attack, damage_mult = res
            
            if skip_attack:
                continue
            
            # Determine Attack Type
            # Default to melee if not specified
            attack_type = getattr(enemy, 'attack_type', 'melee') 
            # In update, we should load this from data. 
            # But for now, let's assume it's set or check special_abilities/data
            # We can check specific enemy types here or rely on data loaded into the enemy object
            
            # Temporary: Mapping based on name/type if not loaded in Enemy class yet
            if "archer" in enemy.enemy_type or "ranger" in enemy.enemy_type:
                attack_type = "ranged"
            elif "wizard" in enemy.enemy_type or "mage" in enemy.enemy_type:
                attack_type = "magic"
            
            player_def = self.battle.player.combat.get_attribute("defense") * 2
            enemy_str = enemy.get_component(CombatComponent).get_attribute("strength") * 2
            enemy_int = enemy.get_component(CombatComponent).get_attribute("intelligence") * 2
            
            damage = 0
            
            if attack_type == "melee":
                damage = np.subtract(enemy_str * damage_mult, player_def // 2)
                damage = np.maximum(1, damage)
                damage = int(damage + random.randint(-1, 1))
                full_message += f"{enemy.name} attacks for {damage} damage!\n"
                
            elif attack_type == "ranged":
                # Ranged: Ignores some defense, but lower accuracy check?
                # For simplicity: varied damage, maybe critical chance
                if random.random() < 0.9: # 90% hit rate
                    damage = np.subtract(enemy_str * 0.8 * damage_mult, player_def // 4) # Armor piercing
                    damage = np.maximum(1, damage)
                    damage = int(damage + random.randint(0, 2))
                    full_message += f"{enemy.name} fires an arrow! Deals {damage} damage!\n"
                    if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("hit") # Use hit sound
                else:
                    full_message += f"{enemy.name} fires an arrow but misses!\n"
                    
            elif attack_type == "magic":
                # Magic: Uses INT, ignores Defense (maybe uses Magic Def?)
                # Select a spell
                spells = ["fireball", "ice_bolt"]
                spell = random.choice(spells)
                
                spell_dmg = enemy_int * 1.5
                damage = int(spell_dmg * damage_mult)
                
                full_message += f"{enemy.name} casts {spell}! Deals {damage} magic damage!\n"
                if hasattr(self.battle.game, 'sound_manager'): self.battle.game.sound_manager.play("magic")

            # Daryl's Lucky Cap Effect (Player)
            equipped_ids = [item.item_id for item in self.battle.player.inventory.equipment.values() if item]
            if "daryls_lucky_cap" in equipped_ids:
                 if random.random() < 0.05:
                     self.battle.player.combat.heal(1)
                     full_message += f"\nDaryl's Lucky Cap absorbs the blow! Healed 1 HP!"
                     damage = 0

            if damage > 0:
                self.battle.player.combat.take_damage(damage)
                
                # Visual Effects
                self.battle.add_effect(FlashEffect(color=(255, 50, 50), duration=0.2)) # Red flash
                px = self.battle.game.battle_ui.x + 30
                py = self.battle.game.battle_ui.y + 110
                self.battle.add_effect(DamageNumber(damage, px, py, color=(255, 50, 50)))
                
                if hasattr(self.battle.game, 'message_log'):
                    self.battle.game.message_log.log_combat(f"{enemy.name} ({attack_type}) dealt {damage} damage")
            
            if 'daze_on_attack' in enemy.special_abilities:
                ability = enemy.special_abilities['daze_on_attack']
                if random.random() < ability['chance']:
                    self.battle.player.combat.apply_status_effect("dazed", ability['duration'])
                    daze_message = f"You are dazed by {enemy.name}'s attack!"
                    full_message += daze_message + "\n"
                    if hasattr(self.battle.game, 'message_log'):
                        self.battle.game.message_log.log_combat(f"Player is dazed for {ability['duration']} turns.")
            
            if self.battle.player.combat.hp <= 0:
                self.battle.change_state("defeat")
                return

        self.battle.message = full_message.strip()
        self.battle.change_state("main_menu")

class VictoryState(BattleState):
    def __init__(self, battle, **kwargs):
        super().__init__(battle)
        self.battle.message = f"All enemies defeated!\nGained {self.battle.rewards['xp']} XP and {self.battle.rewards['gold']} Gold!\nPress Enter to continue."
        
        # Check for Bud Light Boogie Duo Defeat
        # We need to check if they were in the battle, but self.battle.enemies is empty now.
        # We can check if the rewards contain their unique loot or just assume based on context?
        # Better: Store original enemies in Battle or check a flag.
        # For now, let's check if we got the unique loot.
        if "daryls_lucky_cap" in self.battle.rewards.get("items", []):
             self.battle.message = "Daryl: 'Well, I'm tellin' ya, George, if you hadn't tripped over that third invisible iguana...'\nGeorge: 'Bawk! Don't blame the poultry, Daryl!'\n" + self.battle.message

        self.award_rewards()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.battle.active = False

    def award_rewards(self):
        self.battle.player.xp += self.battle.rewards["xp"]
        self.battle.player.gold += self.battle.rewards["gold"]
        
        while self.battle.player.xp >= self.battle.player.xp_to_next:
            self.battle.player.level_up()
            self.battle.message += f"\nLevel Up! Now Level {self.battle.player.level}!"
            if hasattr(self.battle.game, 'message_log'):
                self.battle.game.message_log.log_system(f"Level Up! reached level {self.battle.player.level}")

class DefeatState(BattleState):
    def __init__(self, battle, **kwargs):
        super().__init__(battle)
        self.battle.message = "You were defeated! Press Enter to restart."

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.battle.active = False
                self.battle.game.change_scene("title")

class Battle:
    def __init__(self, game: 'Game', player: 'Entity', enemies: List['Entity'], allies: Optional[List['Entity']] = None):
        self.game = game
        self.player = player
        self.enemies = enemies
        self.allies = allies or []
        self.active = True
        self.message = f"A wild {', '.join([e.name for e in enemies])} appeared!"
        
        # Check for Bud Light Boogie Duo
        enemy_names = [e.enemy_type for e in enemies]
        if "daryl_ledeay" in enemy_names and "chicken_george" in enemy_names:
            self.message = "Daryl: 'Well, I'll be. Lookie here, George. Looks like a pilgrim who's lost their way.'\nGeorge: 'Bawk! Squawk! Ya gotta be quicker than that, partner!'"
        
        if hasattr(self.game, 'message_log'):
            self.game.message_log.log_combat(self.message)
            
        self.rewards: Dict[str, Any] = {"xp": 0, "gold": 0}
        
        self.states: Dict[str, type] = {
            "main_menu": MainMenuState,
            "target_selection": TargetSelectionState,
            "player_attack": PlayerAttackState,
            "magic_menu": MagicMenuState,
            "player_magic_attack": PlayerMagicAttackState,
            "item_menu": ItemMenuState,
            "player_item_attack": PlayerItemAttackState,
            "run": RunState,
            "ally_turn": AllyTurnState,
            "enemy_turn": EnemyTurnState,
            "victory": VictoryState,
            "defeat": DefeatState,
        }
        self.active_effects: List[Any] = [] # List of active CombatEffects
        self.spell_db = SpellDatabase()
        self.item_db = ItemDatabase()
        self.current_state: Optional[BattleState] = None
        self.state = "main_menu" # Initialize state name
        self.change_state("main_menu")

    def add_effect(self, effect):
        self.active_effects.append(effect)

    def change_state(self, state_name: str, **kwargs):
        if state_name in self.states:
            self.state = state_name # Update state name
            self.current_state = self.states[state_name](self, **kwargs)
        else:
            print(f"Error: Unknown battle state '{state_name}'")

    def handle_input(self, event: pygame.event.Event):
        if self.current_state:
            self.current_state.handle_input(event)

    def update(self, dt: float):
        if self.current_state:
            self.current_state.update(dt)
        
        # Update Effects
        for effect in self.active_effects[:]:
            effect.update(dt)
            if effect.finished:
                self.active_effects.remove(effect)

    def draw(self, surface: pygame.Surface):
        if self.current_state:
            self.current_state.draw(surface)
            
        # Draw Effects on top
        for effect in self.active_effects:
             if hasattr(effect, 'draw'):
                 effect.draw(surface)



