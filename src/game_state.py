# DragonQuest/src/game_state.py

class GameState:
    def __init__(self, manager):
        self.manager = manager

    def handle_input(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

class GameStateManager:
    def __init__(self, game):
        self.game = game
        self.states = {}
        self.current_state = None

    def register_state(self, name, state_class):
        self.states[name] = state_class

    def change_state(self, name, state_instance=None, **kwargs):
        if state_instance:
            self.current_state = state_instance
            self.game.logger.log(f"Changed game state to {name}")
        elif name in self.states:
            self.current_state = self.states[name](self, **kwargs)
            self.game.logger.log(f"Changed game state to {name}")
        else:
            self.game.logger.log(f"Error: Unknown game state '{name}'")

    def handle_input(self, event):
        if self.current_state:
            self.current_state.handle_input(event)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, screen):
        if self.current_state:
            self.current_state.draw(screen)