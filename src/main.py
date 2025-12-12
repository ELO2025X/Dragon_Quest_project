import pygame
import sys
import os
from settings import *
from entities import Player, Enemy, NPC
from tilemap import Map
from battle import Battle
from camera import Camera
from quest import QuestManager
from world_generator import WorldGenerator
from logger import Logger
from save_manager import SaveManager
from dialogue import DialogueManager
from scene import TitleScene, WorldScene, CombatScene
from ui import MessageLog, CommandConsole, HUD, DialogueBox, BattleUI, JobMenu
from animation import Animation
from audio import MusicPlayer, SoundManager
from resource_manager import ResourceManager
from data_manager import DataManager
from game_state import GameStateManager
from input_handler import InputHandler
from renderer import Renderer

# Global variable to hold the Game instance for the exception handler
game_instance = None

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log KeyboardInterrupt, just exit cleanly
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Ensure the logger is initialized and accessible
    if globals().get('game_instance') and game_instance.logger:
        game_instance.logger.error("Unhandled exception caught by custom handler!", exc_info=(exc_type, exc_value, exc_traceback))
    else:
        # Fallback if logger is not available
        print("FATAL ERROR: Unhandled exception, and logger not available!")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    # Attempt a clean shutdown
    if globals().get('game_instance') and hasattr(game_instance, 'playing') and game_instance.playing:
        game_instance.quit()
    elif 'pygame' in sys.modules:
        pygame.quit()
    sys.exit(1)

sys.excepthook = handle_exception

class Game:
    def __init__(self):
        pygame.init()
        # Web Compatibility: FULLSCREEN can be tricky with pygbag's canvas handling.
        # Using SCALED only or just windowed is safer for initial debug.
        # also removing SCALED for now to reduce variables, though SCALED is usually fine.
        flags = pygame.SCALED if sys.platform != 'emscripten' else 0 
        # Actually, let's try simple windowed first.
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.logger = Logger()
        print("Game Initialized - Window Created")
        
        # Core Components
        self.resource_manager = ResourceManager(self)
        self.data_manager = DataManager(self)
        self.data_manager.load_data()
        
        self.game_state_manager = GameStateManager(self)
        self.input_handler = InputHandler(self)
        self.renderer = Renderer(self)
        
        self.save_manager = SaveManager(self)
        self.message_log = MessageLog(WIDTH - 310, HEIGHT - 220, 300, 210)
        self.console = CommandConsole(self)
        self.hud = HUD(self)
        self.dialogue_box = DialogueBox(self)
        self.battle_ui = BattleUI(self)
        self.job_menu = JobMenu(self)
        self.music_player = MusicPlayer(self)
        self.sound_manager = SoundManager(self)
        self.music_player.play_next()
        
        self.in_battle = False
        self.battle = None
        self.in_dialogue = False
        self.job_menu_active = False
        self.dialogue_text = ""
        self.map = None
        
        self.register_states()
        self.game_state_manager.change_state("title")

    def register_states(self):
        self.game_state_manager.register_state("title", TitleScene)
        self.game_state_manager.register_state("world", WorldScene)
        self.game_state_manager.register_state("combat", CombatScene)

    def change_scene(self, scene_name, **kwargs):
        if scene_name == "world":
            if self.map is None:
                self.new()
            world_scene = WorldScene(self.game_state_manager)
            self.game_state_manager.change_state(scene_name, state_instance=world_scene, **kwargs)
        else:
            self.game_state_manager.change_state(scene_name, **kwargs)

        if scene_name == "combat":
            self.in_battle = True
            self.battle = self.game_state_manager.current_state.battle_system
        else:
            self.in_battle = False
            self.battle = None

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.quest_manager = QuestManager(self)
        self.dialogue_manager = DialogueManager(self)
        self.map = Map(self)
        self.world_gen = WorldGenerator()
        from dungeon_generator import DungeonGenerator
        self.dungeon_gen = DungeonGenerator()
        
        self.interactables = pygame.sprite.Group()
        
        self.maps = {
            "world_map": self.world_gen.generate_world_map(),
            "town_01": self.world_gen.generate_town_map(),
            "dungeon_01": self.dungeon_gen.generate_dungeon()
        }
        self.load_map("world_map")
        
        self.in_dialogue = False
        self.dialogue_text = ""
        self.current_npc = None
        self.debug = False
        
        self.camera = Camera(self.map.world_width * TILESIZE, self.map.world_height * TILESIZE)
        
        spawn_x, spawn_y = self.map.spawn_location
        self.player = Player(self, spawn_x, spawn_y)
        
        self.logger.debug(f"Game.new - Spawn Location: ({spawn_x}, {spawn_y})")
        # self.dump_map_around_player(spawn_x, spawn_y)
        
        self.populate_map(self.current_map_id)

    def load_map(self, map_id, spawn_x=None, spawn_y=None):
        self.current_map_id = map_id
        map_data = self.maps[map_id]
        self.logger.debug(f"Loading map '{map_id}'")
        self.map.load_map(map_data)
        
        if hasattr(self, 'camera'):
            self.camera = Camera(self.map.world_width * TILESIZE, self.map.world_height * TILESIZE)
        
        if spawn_x is not None and spawn_y is not None and hasattr(self, 'player'):
            self.logger.debug(f"Spawning player at grid ({spawn_x}, {spawn_y}) -> pixel ({spawn_x * TILESIZE}, {spawn_y * TILESIZE})")
            self.player.x = spawn_x * TILESIZE
            self.player.y = spawn_y * TILESIZE
            self.player.rect.y = spawn_y * TILESIZE
            self.player.hit_rect.center = self.player.rect.center
            
            # Debug: Dump map around player
            self.dump_map_around_player(spawn_x, spawn_y)
            
        self.populate_map(map_id)

    def dump_map_around_player(self, px, py, radius=10):
        self.logger.debug(f"\n--- MAP DUMP AROUND ({px}, {py}) ---")
        start_x = max(0, px - radius)
        end_x = min(self.map.world_width, px + radius + 1)
        start_y = max(0, py - radius)
        end_y = min(self.map.world_height, py + radius + 1)
        
        for y in range(start_y, end_y):
            line = ""
            for x in range(start_x, end_x):
                if x == px and y == py:
                    line += "P" # Player
                elif self.map.layers["ground"][y, x] == 2: # WATER
                    line += "~"
                elif self.map.layers["ground"][y, x] == 0: # GRASS
                    line += "."
                elif self.map.layers["ground"][y, x] == 1: # DIRT
                    line += ":"
                elif self.map.layers["ground"][y, x] == 3: # FOREST
                    line += "T"
                elif self.map.layers["ground"][y, x] == 4: # MOUNTAIN
                    line += "^"
                elif self.map.layers["ground"][y, x] == 5: # WALL
                    line += "#"
                else:
                    line += "?"
            self.logger.debug(f"{y:3d} | {line}")
        self.logger.debug("-----------------------------------\n")

    def populate_map(self, map_id):
        if hasattr(self, 'all_sprites'):
            for sprite in self.all_sprites:
                if hasattr(self, 'player') and sprite == self.player:
                    continue
                if hasattr(self, 'followers') and sprite in self.followers:
                    continue
                sprite.kill()
            # self.all_sprites.empty() # Do not empty, as we kept the player
            
        if hasattr(self, 'enemies'):
            for sprite in self.enemies:
                sprite.kill()
            self.enemies.empty()
        if hasattr(self, 'npcs'):
            for sprite in self.npcs:
                sprite.kill()
            self.npcs.empty()
        if hasattr(self, 'interactables'):
            for sprite in self.interactables:
                sprite.kill()
            self.interactables.empty()

        if map_id in self.maps and "entities" in self.maps[map_id]:
            entity_data = self.maps[map_id]["entities"]
        else:
            entity_data = self.world_gen.get_map_entities(map_id, self.map.world_width, self.map.world_height, self.map.is_blocked)

        for entity in entity_data:
            if entity["type"] == "enemy":
                Enemy(self, entity["x"], entity["y"], entity["name"])
            elif entity["type"] == "npc":
                NPC(self, entity["x"], entity["y"], entity["name"], entity["dialogue_id"], entity.get("quest_id"))
            elif entity["type"] == "pickup":
                Pickup(self, entity["x"], entity["y"], entity["pickup_type"])
            elif entity["type"] == "object":
                from interaction import Chest, Switch, PushBlock, Door
                cls_name = entity.get("class")
                if cls_name == "Chest":
                    Chest(self, entity["x"], entity["y"], (self.all_sprites, self.interactables), entity.get("content"))
                elif cls_name == "Switch":
                    Switch(self, entity["x"], entity["y"], (self.all_sprites, self.interactables), doors=None)
                elif cls_name == "PushBlock":
                    PushBlock(self, entity["x"], entity["y"], (self.all_sprites, self.interactables))
                elif cls_name == "Door":
                    Door(self, entity["x"], entity["y"], (self.all_sprites, self.interactables), locked=entity.get("locked", True))
        
        switches = [s for s in self.interactables if isinstance(s, Switch)]
        doors = [d for d in self.interactables if isinstance(d, Door)]
        for sw in switches:
            sw.doors = doors

    async def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
            
            # Simple heartbeat for web debugging
            if hasattr(self, 'frame_count'):
                self.frame_count += 1
            else:
                self.frame_count = 0
            
            if self.frame_count % 120 == 0:
                print(f"Heartbeat: Frame {self.frame_count}, State: {self.game_state_manager.current_state}")

            await asyncio.sleep(0)

    def quit(self):
        pygame.quit()
        sys.exit()

    def events(self):
        self.input_handler.process_events()

    def update(self):
        self.music_player.update()
        self.message_log.update()
        self.game_state_manager.update(self.dt)

        if hasattr(self, 'player') and isinstance(self.game_state_manager.current_state, WorldScene):
            self.player.jp += 1 * self.dt

    def draw(self):
        self.renderer.draw()

    def process_command(self, text):
        parts = text.split()
        if not parts: return
        
        command = parts[0].lower()
        args = parts[1:]
        
        if command == "/heal":
            self.player.combat.hp = self.player.combat.max_hp
            self.player.combat.mp = self.player.combat.max_mp
            self.message_log.log_system("Fully healed player.")
            
        elif command == "/spawn":
            if args:
                enemy_type = args[0]
                Enemy(self, int(self.player.x / TILESIZE) + 2, int(self.player.y / TILESIZE), enemy_type)
                self.message_log.log_system(f"Spawned {enemy_type}")
            else:
                self.message_log.log_system("Usage: /spawn <type>")
                
        elif command == "/give":
            if args:
                item_name = " ".join(args)
                self.message_log.log_system(f"Gave {item_name} (Not fully implemented)")
            else:
                self.message_log.log_system("Usage: /give <item_name>")
        
        else:
            self.message_log.log_system(f"Unknown command: {command}")

    def create_enemy(self, enemy_type):
        return Enemy(self, 0, 0, enemy_type)

    def check_npc_interaction(self):
        hits = pygame.sprite.spritecollide(self.player, self.npcs, False)
        if hits:
            npc = hits[0]
            self.in_dialogue = True
            self.current_npc = npc
            dialogue_response = npc.interact()
            
            if isinstance(dialogue_response, list):
                self.dialogue_text = " ".join(dialogue_response)
            else:
                self.dialogue_text = dialogue_response
            
            if npc.quest_id:
                if self.quest_manager.accept_quest(npc.quest_id):
                    self.dialogue_text += " (Quest Accepted!)"
            return True
        return False

    def draw_debug(self):
        pygame.draw.rect(self.screen, DEBUG_COLOR, self.camera.apply(self.player), 1)

if __name__ == "__main__":
    print("MAIN: Starting Execution")
    try:
        import asyncio
        game_instance = Game() # Assign to global
        print("MAIN: Game Instance Created")
        asyncio.run(game_instance.run())
    except Exception as e:
        print(f"FATAL ERROR in main: {e}")
        import traceback
        traceback.print_exc()
