# DragonQuest/src/renderer.py
import pygame
from scene import TitleScene 

class Renderer:
    def __init__(self, game):
        self.game = game

    def draw(self):
        if self.game.game_state_manager.current_state:
            self.game.game_state_manager.draw(self.game.screen)
        
        # Draw global message log on top if not in title AND not in combat
        if not isinstance(self.game.game_state_manager.current_state, TitleScene) and not self.game.in_battle:
            self.game.message_log.draw(self.game.screen)
            self.game.console.draw(self.game.screen)
            self.game.hud.draw()
            
        if self.game.in_dialogue:
            self.game.dialogue_box.draw(self.game.dialogue_text)
            
        if self.game.in_battle and self.game.battle:
            self.game.battle_ui.draw(self.game.battle)
            
        if self.game.job_menu_active:
            self.game.job_menu.draw()

        pygame.display.flip()