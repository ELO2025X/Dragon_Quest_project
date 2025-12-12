import pygame
import json
import os
from settings import *

class DialogueManager:
    def __init__(self, game):
        self.game = game
        self.dialogue_data = {}
        self.load_dialogue()
        
    def load_dialogue(self):
        path = os.path.join(os.path.dirname(__file__), 'dialogue.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.dialogue_data = json.load(f)
                
    def get_dialogue(self, npc_id):
        if npc_id not in self.dialogue_data:
            return "..."
            
        npc_data = self.dialogue_data[npc_id]
        
        # Check flags to determine which dialogue to show
        # This is a simple priority system: check specific flags first
        
        # Example: Check for quest completion or active state
        # For now, we'll implement a basic check based on the JSON structure
        # We expect keys like "with_pendant", "quest_active", etc.
        # We need to map game flags to these keys
        
        flags = self.game.quest_manager.flags
        
        # Iterate through keys in npc_data to find a matching flag
        # This assumes keys in JSON match flag names, except "default"
        for key in npc_data:
            if key == "default":
                continue
            if flags.get(key, False):
                # Found a matching flag that is true
                # Check if there's a "next" or if this is the one
                # For simple logic, return this one
                return self.process_dialogue_entry(npc_data[key])
                
        return self.process_dialogue_entry(npc_data.get("default", {"text": "..."}))

    def process_dialogue_entry(self, entry):
        # Set flag if specified
        if "flag_set" in entry:
            flag = entry["flag_set"]
            self.game.quest_manager.flags[flag] = True
            self.game.logger.log(f"Flag set: {flag}")
            
        # Ensure text is a list for multi-page support
        text = entry["text"]
        if isinstance(text, str):
            return [text]
        return text

class DialogueBox:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.text = ""
        self.npc_name = ""
        
    def show(self, npc_name, text):
        """Display dialogue from an NPC"""
        self.active = True
        self.active = True
        self.npc_name = npc_name
        self.pages = text if isinstance(text, list) else [text]
        self.page_index = 0
        self.text = self.pages[self.page_index]
        if hasattr(self.game, 'sound_manager'): self.game.sound_manager.play("text_blip")
    
    def hide(self):
        """Close the dialogue box"""
        self.active = False
    
    def handle_input(self, event):
        """Handle user input while dialogue is open"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.page_index += 1
                if self.page_index < len(self.pages):
                    self.text = self.pages[self.page_index]
                    if hasattr(self.game, 'sound_manager'): self.game.sound_manager.play("text_blip")
                else:
                    self.hide()
                return True
        return False
    
    def draw(self, screen):
        """Draw the dialogue box"""
        if not self.active:
            return
        
        box_width = 600
        box_height = 150
        box_x = (WIDTH - box_width) // 2
        box_y = HEIGHT - box_height - 20
        
        # Blue gradient background
        for i in range(box_height):
            color_value = int(20 + (i / box_height) * 40)
            pygame.draw.line(screen, (0, 0, color_value), (box_x, box_y + i), (box_x + box_width, box_y + i))
        
        # Border
        pygame.draw.rect(screen, (255, 215, 0), (box_x, box_y, box_width, box_height), 4)
        pygame.draw.rect(screen, WHITE, (box_x + 2, box_y + 2, box_width - 4, box_height - 4), 2)
        
        # NPC name
        font_large = pygame.font.Font(None, 32)
        name_surface = font_large.render(self.npc_name, True, (255, 215, 0))
        screen.blit(name_surface, (box_x + 20, box_y + 15))
        
        # Dialogue text with word wrap
        font_small = pygame.font.Font(None, 24)
        words = self.text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if font_small.size(test_line)[0] > box_width - 40:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        y_offset = box_y + 55
        for line in lines[:3]:  # Max 3 lines
            text_surface = font_small.render(line, True, WHITE)
            screen.blit(text_surface, (box_x + 20, y_offset))
            y_offset += 30
        
        # Prompt
        prompt = font_small.render("Press Enter to continue...", True, (200, 200, 200))
        screen.blit(prompt, (box_x + box_width - 250, box_y + box_height - 35))
