import pygame
import os
import random

class MusicPlayer:
    def __init__(self, game):
        self.game = game
        self.music_folder = os.path.join(os.path.dirname(__file__), 'assets')
        
        # Categorized playlists
        self.playlists = {
            "exploration": [
                "Aerthos's Embrace.wav",
                "Oakhaven's Hearth.wav",
                "Oakhaven's Hearth (1).wav"
            ],
            "battle": [
                # Ideally we'd have a specific battle track. 
                # For now using a placeholder or reusing an intense-sounding one if available.
                # If no specific battle track, we can keep the current song or use a specific one.
                # Assuming "Aerthos's Embrace.wav" might be good for battle or we need a new file.
                # Let's try to find if there are other files, otherwise reuse or use placeholders.
                "Aerthos's Embrace.wav" 
            ]
        }
        
        self.current_playlist = []
        self.current_song = None
        self.current_state = "exploration" # exploration, battle
        self.volume = 0.5
        
        # pygame.mixer.music.set_volume(self.volume)
        
    def set_mode(self, mode):
        if mode not in self.playlists:
            return
            
        if self.current_state == mode and pygame.mixer.music.get_busy():
            return # Already playing correct mood
            
        self.current_state = mode
        self.current_playlist = self.playlists[mode][:]
        random.shuffle(self.current_playlist)
        self.play_next()

    def play_battle_music(self):
        self.set_mode("battle")

    def play_exploration_music(self):
        self.set_mode("exploration")

    def play_next(self):
        if not self.playlists.get(self.current_state):
            return
            
        # Refill playlist if empty
        if not self.current_playlist:
            self.current_playlist = self.playlists[self.current_state][:]
            random.shuffle(self.current_playlist)
            
            # Avoid repeating the last song if possible
            if self.current_song and self.current_playlist and self.current_playlist[0] == self.current_song and len(self.current_playlist) > 1:
                self.current_playlist.append(self.current_playlist.pop(0))
        
        if not self.current_playlist: return

        next_song = self.current_playlist.pop(0)
        self.current_song = next_song
        full_path = os.path.join(self.music_folder, next_song)
        
        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play()
            # print(f"Now playing ({self.current_state}): {next_song}")
        except pygame.error as e:
            print(f"Error playing {next_song}: {e}")

    def update(self):
        # Check if music is playing
        if not pygame.mixer.music.get_busy():
            self.play_next()
            
    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

class SoundManager:
    def __init__(self, game):
        self.game = game
        self.sfx_folder = os.path.join(os.path.dirname(__file__), 'assets', 'sfx')
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        sfx_files = ["attack.wav", "magic.wav", "text_blip.wav", "menu.wav"]
        for filename in sfx_files:
            path = os.path.join(self.sfx_folder, filename)
            if os.path.exists(path):
                try:
                    name = os.path.splitext(filename)[0]
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.4)
                except pygame.error as e:
                    print(f"Error loading SFX {filename}: {e}")
                    
    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

