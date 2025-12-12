# DragonQuest/src/input_handler.py
import pygame

class InputHandler:
    def __init__(self, game):
        self.game = game

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.quit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_RETURN and not self.game.in_battle and not self.game.in_dialogue and hasattr(self.game, 'player'):
                    self.game.console.toggle()
                if event.key == pygame.K_j and not self.game.in_battle and not self.game.in_dialogue:
                    self.game.job_menu_active = not self.game.job_menu_active

            if self.game.console.active:
                self.game.console.handle_input(event)
            elif self.game.job_menu_active:
                self.game.job_menu.handle_input(event)
            elif self.game.game_state_manager:
                self.game.game_state_manager.handle_input(event)