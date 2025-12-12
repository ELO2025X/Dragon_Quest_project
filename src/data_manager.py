# DragonQuest/src/data_manager.py
import pygame
import json
import os

class DataManager:
    def __init__(self, game):
        self.game = game
        self.data = {}

    def load_data(self):
        game_folder = os.path.dirname(__file__)
        data_folder = os.path.join(game_folder, 'data')
        
        for filename in os.listdir(data_folder):
            if filename.endswith(".json"):
                name = os.path.splitext(filename)[0]
                path = os.path.join(data_folder, filename)
                with open(path, 'r') as f:
                    self.data[name] = json.load(f)

    def get_data(self, name):
        return self.data.get(name)
