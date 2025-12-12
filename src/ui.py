import pygame
from settings import *

class UIElement:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font_large = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.font_battle = pygame.font.Font(None, 24)

class HUD(UIElement):
    def __init__(self, game):
        super().__init__(game)
        self.height = 60
        self.width = WIDTH

    def draw(self):
        # Blue gradient background
        for i in range(self.height):
            color_value = int(20 + (i / self.height) * 30)
            pygame.draw.line(self.screen, (0, 0, color_value), (0, i), (self.width, i))
        
        pygame.draw.line(self.screen, (255, 215, 0), (0, self.height - 2), (self.width, self.height - 2), 3)
        
        name_text = self.font_large.render(f"{self.game.player.name}", True, WHITE)
        level_text = self.font_small.render(f"Lv.{self.game.player.level}", True, (255, 215, 0))
        self.screen.blit(name_text, (15, 10))
        self.screen.blit(level_text, (15, 35))
        
        # HP Bar
        hp_x = 120
        hp_label = self.font_small.render("HP", True, WHITE)
        self.screen.blit(hp_label, (hp_x, 12))
        
        bar_width = 120
        bar_height = 12
        hp_percent = self.game.player.combat.hp / self.game.player.combat.max_hp
        pygame.draw.rect(self.screen, (60, 60, 60), (hp_x, 32, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 200, 0), (hp_x, 32, int(bar_width * hp_percent), bar_height))
        pygame.draw.rect(self.screen, WHITE, (hp_x, 32, bar_width, bar_height), 1)
        
        hp_text = self.font_small.render(f"{self.game.player.combat.hp}/{self.game.player.combat.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (hp_x, 48))

        # Job Info
        job_x = 260
        job_label = self.font_small.render("Job", True, WHITE)
        self.screen.blit(job_label, (job_x, 12))
        job_name_text = self.font_small.render(f"{self.game.player.job.capitalize()}", True, (255, 215, 0))
        self.screen.blit(job_name_text, (job_x, 35))

        # JP Info
        jp_x = 360
        jp_label = self.font_small.render("JP", True, WHITE)
        self.screen.blit(jp_label, (jp_x, 12))
        jp_text = self.font_small.render(f"{int(self.game.player.jp)}", True, WHITE)
        self.screen.blit(jp_text, (jp_x, 35))

class DialogueBox(UIElement):
    def __init__(self, game):
        super().__init__(game)
        self.height = 150
        self.width = WIDTH - 40
        self.x = 20
        self.y = HEIGHT - self.height - 20

    def draw(self, text):
        pygame.draw.rect(self.screen, BLACK, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, WHITE, (self.x, self.y, self.width, self.height), 4)
        
        # Ensure text is a string
        text = text if isinstance(text, str) else str(text)
        
        # Word wrapping
        words = text.split(' ')
        lines = []
        current_line = ""
        max_width = self.width - 40
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.font_large.render(test_line, True, WHITE)
            if test_surface.get_width() > max_width:
                if current_line:
                    lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    lines.append(word)
                    current_line = ""
            else:
                current_line = test_line
                
        if current_line:
            lines.append(current_line.strip())
        
        # Draw lines (max 4 lines visible at once)
        max_lines = 4
        y_offset = self.y + 15
        line_height = 30
        
        for i, line in enumerate(lines[:max_lines]):
            text_surface = self.font_large.render(line, True, WHITE)
            self.screen.blit(text_surface, (self.x + 20, y_offset + i * line_height))
            
        # Show indicator if there's more text
        if len(lines) > max_lines:
            indicator = self.font_large.render("[SPACE to continue...]", True, (255, 255, 100))
            self.screen.blit(indicator, (self.x + 20, self.y + self.height - 30))

class BattleUI(UIElement):
    def __init__(self, game):
        super().__init__(game)
        self.width = 500
        self.height = 250
        self.x = (WIDTH - self.width) // 2
        self.y = HEIGHT - self.height - 20

    def draw(self, battle):
        self.draw_battle(self.screen, battle)

    def draw_battle(self, surface, battle):
        # Draw blue gradient background (Dragon Quest style) for the battle area
        ui_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Main Window Background (Dark Blue to Black Gradient)
        for i in range(ui_rect.height):
            color_val = int(10 + (i / ui_rect.height) * 40)
            pygame.draw.line(surface, (0, 0, color_val), (ui_rect.x, ui_rect.y + i), (ui_rect.x + ui_rect.width, ui_rect.y + i))
        
        # Ornate Border (Double border style)
        pygame.draw.rect(surface, (255, 255, 255), ui_rect, 6) # Outer White
        pygame.draw.rect(surface, (0, 0, 0), ui_rect, 4)       # Inner Black gap
        pygame.draw.rect(surface, (255, 215, 0), (ui_rect.x + 4, ui_rect.y + 4, ui_rect.width - 8, ui_rect.height - 8), 2) # Inner Gold
        
        # Draw message area
        msg_lines = battle.message.split('\n')
        for i, line in enumerate(msg_lines):
            self.draw_text_with_shadow(surface, line, self.font_large, ui_rect.x + 30, ui_rect.y + 30 + i * 35)
        
        # Stats Area (Lower Section)
        stats_y = ui_rect.y + 110
        pygame.draw.line(surface, (255, 255, 255), (ui_rect.x + 20, stats_y - 10), (ui_rect.x + ui_rect.width - 20, stats_y - 10), 1)

        # Player Stats (Left Side)
        p_x = ui_rect.x + 30
        self.draw_text_with_shadow(surface, f"Hero Lv.{battle.player.level}", self.font_battle, p_x, stats_y, (200, 200, 255))
        
        # HP Bar Background
        bar_width = 160
        bar_height = 16
        pygame.draw.rect(surface, (60, 60, 60), (p_x, stats_y + 30, bar_width, bar_height))
        
        # HP Bar Fill
        hp_pct = max(0, min(1, battle.player.combat.hp / battle.player.combat.max_hp))
        curr_hp_rec = pygame.Rect(p_x, stats_y + 30, int(bar_width * hp_pct), bar_height)
        
        hp_color = (0, 200, 0) if hp_pct > 0.5 else (200, 200, 0) if hp_pct > 0.2 else (200, 0, 0)
        pygame.draw.rect(surface, hp_color, curr_hp_rec)
        pygame.draw.rect(surface, WHITE, (p_x, stats_y + 30, bar_width, bar_height), 1)
        
        self.draw_text_with_shadow(surface, f"HP: {battle.player.combat.hp}/{battle.player.combat.max_hp}", self.font_small, p_x + 5, stats_y + 31, WHITE)

        # MP Bar
        mp_y = stats_y + 55
        pygame.draw.rect(surface, (60, 60, 60), (p_x, mp_y, bar_width, bar_height))
        mp_pct = max(0, min(1, battle.player.combat.mp / battle.player.combat.max_mp))
        curr_mp_rec = pygame.Rect(p_x, mp_y, int(bar_width * mp_pct), bar_height)
        pygame.draw.rect(surface, (50, 50, 255), curr_mp_rec)
        pygame.draw.rect(surface, WHITE, (p_x, mp_y, bar_width, bar_height), 1)
        
        self.draw_text_with_shadow(surface, f"MP: {battle.player.combat.mp}/{battle.player.combat.max_mp}", self.font_small, p_x + 5, mp_y + 1, WHITE)

        # Menus
        if battle.state == "main_menu":
            self.draw_battle_menu(surface, battle.current_state, ui_rect.x + 240, ui_rect.y + 30)
        elif battle.state == "target_selection":
             self.draw_target_selection(surface, battle, ui_rect.x + 240, ui_rect.y + 30)
        elif battle.state == "magic_menu":
             self.draw_magic_menu(surface, battle.current_state, ui_rect.x + 240, ui_rect.y + 30)
        elif battle.state == "item_menu":
             self.draw_item_menu(surface, battle.current_state, ui_rect.x + 240, ui_rect.y + 30)

    def draw_text_with_shadow(self, surface, text, font, x, y, color=WHITE, shadow_color=(0, 0, 0)):
        shadow_surf = font.render(str(text), True, shadow_color)
        text_surf = font.render(str(text), True, color)
        surface.blit(shadow_surf, (x + 2, y + 2))
        surface.blit(text_surf, (x, y))
        return text_surf.get_width(), text_surf.get_height()

    def draw_battle_menu(self, surface, state, x, y):
        for i, option in enumerate(state.options):
            color = (255, 215, 0) if i == state.selected_option else WHITE
            prefix = "> " if i == state.selected_option else "  "
            self.draw_text_with_shadow(surface, f"{prefix}{option}", self.font_large, x, y + i * 30, color)

    def draw_target_selection(self, surface, battle, x, y):
        self.draw_text_with_shadow(surface, "Select Target:", self.font_large, x, y, WHITE)
        for i, enemy in enumerate(battle.enemies):
            color = (255, 100, 100) if i == battle.current_state.selected_target else WHITE
            prefix = "> " if i == battle.current_state.selected_target else "  "
            self.draw_text_with_shadow(surface, f"{prefix}{enemy.name}", self.font_large, x, y + 30 + i * 30, color)
            
            # Draw cursor over enemy sprite
            if i == battle.current_state.selected_target:
                pygame.draw.polygon(surface, (255, 0, 0), [
                    (enemy.rect.centerx, enemy.rect.top - 10),
                    (enemy.rect.centerx - 10, enemy.rect.top - 30),
                    (enemy.rect.centerx + 10, enemy.rect.top - 30)
                ])

    def draw_magic_menu(self, surface, state, x, y):
        # Background for menu
        # pygame.draw.rect(surface, (0, 0, 50), (x - 10, y - 10, 220, 200)) # Optional styling
        
        visible_count = 5
        start_idx = max(0, state.selected_magic - 2)
        end_idx = min(len(state.spells) + 1, start_idx + visible_count)
        
        for i in range(start_idx, end_idx):
            display_idx = i - start_idx
            if i == len(state.spells):
                text = "Back"
                cost = ""
            else:
                spell_id = state.spells[i]
                spell = state.spell_db.get_spell(spell_id)
                text = spell.name
                cost = f"{spell.cost} MP"
                
            color = (255, 215, 0) if i == state.selected_magic else WHITE
            prefix = "> " if i == state.selected_magic else "  "
            
            self.draw_text_with_shadow(surface, f"{prefix}{text}", self.font_battle, x, y + display_idx * 30, color)
            if cost:
                self.draw_text_with_shadow(surface, cost, self.font_small, x + 150, y + display_idx * 30 + 5, (100, 200, 255))

    def draw_item_menu(self, surface, state, x, y):
        visible_count = 5
        start_idx = max(0, state.selected_item - 2)
        end_idx = min(len(state.item_names) + 1, start_idx + visible_count)
        
        for i in range(start_idx, end_idx):
            display_idx = i - start_idx
            if i == len(state.item_names):
                text = "Back"
                qty = ""
            else:
                item_name = state.item_names[i]
                count = len(state.grouped_items[item_name])
                text = item_name
                qty = f"x{count}"
                
            color = (255, 215, 0) if i == state.selected_item else WHITE
            prefix = "> " if i == state.selected_item else "  "
            
            self.draw_text_with_shadow(surface, f"{prefix}{text}", self.font_battle, x, y + display_idx * 30, color)
            if qty:
                self.draw_text_with_shadow(surface, qty, self.font_small, x + 180, y + display_idx * 30 + 5, (200, 200, 200))


class MessageLog:
    def __init__(self, x, y, width, height, font_size=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.messages = [] # List of (text, color, timestamp) tuples
        self.font = pygame.font.Font(None, font_size)
        self.max_messages = 10
        self.message_lifetime = 5.0 # Messages fade after 5 seconds
        self.bg_color = (0, 0, 0, 150) # Semi-transparent black

    def add_message(self, text, color=WHITE):
        import time
        self.messages.append((text, color, time.time()))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
            
    def update(self):
        import time
        current_time = time.time()
        # Remove messages older than lifetime
        self.messages = [(text, color, timestamp) for text, color, timestamp in self.messages 
                        if current_time - timestamp < self.message_lifetime]


    def draw(self, surface):
        if not self.messages:
            return  # Don't draw empty box
            
        # Draw background
        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(150)
        s.fill(BLACK)
        surface.blit(s, (self.rect.x, self.rect.y))
        
        # Draw border
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 1)
        
        # Draw messages
        y_offset = 5
        for text, color, timestamp in self.messages:
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (self.rect.x + 5, self.rect.y + y_offset))
            y_offset += 20


    def log_anomaly(self, text):
        self.add_message(f"[ANOMALY] {text}", (0, 255, 255)) # Cyan

    def log_combat(self, text):
        self.add_message(f"[COMBAT] {text}", (255, 100, 100)) # Red

    def log_system(self, text):
        self.add_message(f"[SYSTEM] {text}", (200, 200, 200)) # Grey

class CommandConsole:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.text = ""
        self.font = pygame.font.Font(None, 24)
        self.rect = pygame.Rect(10, HEIGHT - 40, WIDTH - 20, 30)
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def toggle(self):
        self.active = not self.active
        self.text = "" # Clear text on toggle? Or keep it? Let's clear for now.
        if self.active and hasattr(self.game, 'player'):
            # Stop player movement when typing
            self.game.player.vx = 0
            self.game.player.vy = 0
            
    def handle_input(self, event):
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.text:
                    self.game.process_command(self.text)
                self.toggle()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.toggle()
            else:
                self.text += event.unicode
                
    def draw(self, surface):
        if not self.active:
            return
            
        # Draw background
        pygame.draw.rect(surface, (0, 0, 0, 200), self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        # Draw text
        txt_surface = self.font.render(f"> {self.text}", True, WHITE)
        surface.blit(txt_surface, (self.rect.x + 5, self.rect.y + 8))
        
        # Draw cursor
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.rect.x + 5 + txt_surface.get_width()
            pygame.draw.line(surface, WHITE, (cursor_x, self.rect.y + 5), (cursor_x, self.rect.y + 25), 2)

class JobMenu(UIElement):
    def __init__(self, game):
        super().__init__(game)
        self.width = 400
        self.height = 400  # Increased height
        self.x = (WIDTH - self.width) // 2
        self.y = (HEIGHT - self.height) // 2
        self.unlock_buttons = []
        self.master_button_rect = None
        self.job_change_buttons = []

    def draw(self):
        # Draw a background
        pygame.draw.rect(self.screen, BLACK, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, WHITE, (self.x, self.y, self.width, self.height), 2)

        # Title
        title_text = self.font_large.render("Job Menu", True, WHITE)
        self.screen.blit(title_text, (self.x + 10, self.y + 10))

        # Job Info
        job_name = self.game.player.job.capitalize()
        job_text = self.font_small.render(f"Job: {job_name}", True, WHITE)
        self.screen.blit(job_text, (self.x + 10, self.y + 50))

        jp_text = self.font_small.render(f"JP: {int(self.game.player.jp)}", True, WHITE)
        self.screen.blit(jp_text, (self.x + 10, self.y + 80))

        # Skills
        skills_title = self.font_large.render("Skills", True, WHITE)
        self.screen.blit(skills_title, (self.x + 10, self.y + 120))
        
        self.unlock_buttons.clear()
        self.master_button_rect = None
        current_job_id = self.game.player.job
        if current_job_id in self.game.job_data:
            skills = self.game.job_data[current_job_id]["skills"]
            y_offset = self.y + 150
            for i, skill in enumerate(skills):
                skill_name = skill["name"]
                jp_cost = skill["jp_cost"]
                
                skill_text = self.font_small.render(f"{skill_name} ({jp_cost} JP)", True, WHITE)
                self.screen.blit(skill_text, (self.x + 10, y_offset + i * 30))

                is_unlocked = skill_name in self.game.player.skills
                if is_unlocked:
                    unlocked_text = self.font_small.render("Learned", True, (0, 255, 0))
                    self.screen.blit(unlocked_text, (self.x + self.width - 100, y_offset + i * 30))
                else:
                    can_afford = self.game.player.jp >= jp_cost
                    color = (255, 215, 0) if can_afford else (100, 100, 100)
                    unlock_button_rect = pygame.Rect(self.x + self.width - 100, y_offset + i * 30, 80, 25)
                    pygame.draw.rect(self.screen, color, unlock_button_rect, 2)
                    unlock_text = self.font_small.render("Unlock", True, color)
                    self.screen.blit(unlock_text, (self.x + self.width - 90, y_offset + i * 30 + 5))
                    self.unlock_buttons.append((unlock_button_rect, skill))

            # Mastery
            unlocked_job_skills = [s for s in skills if s["name"] in self.game.player.skills]
            if len(unlocked_job_skills) == len(skills):
                mastery_y = self.y + self.height - 90
                if current_job_id not in self.game.player.mastered_jobs:
                    self.master_button_rect = pygame.Rect(self.x + (self.width - 150) // 2, mastery_y, 150, 30)
                    pygame.draw.rect(self.screen, (255, 215, 0), self.master_button_rect, 2)
                    master_text = self.font_small.render("Master Job", True, (255, 215, 0))
                    self.screen.blit(master_text, (self.x + (self.width - 150) // 2 + 30, mastery_y + 5))
                else:
                    mastered_text = self.font_small.render("Job Mastered!", True, (0, 255, 0))
                    self.screen.blit(mastered_text, (self.x + (self.width - 150) // 2 + 20, mastery_y + 5))
        
        # Job Change Buttons
        self.job_change_buttons.clear()
        job_change_y = self.y + self.height - 50
        all_jobs = list(self.game.job_data.keys())
        for i, job_id in enumerate(all_jobs):
            button_x = self.x + 10 + i * 90
            rect = pygame.Rect(button_x, job_change_y, 80, 30)
            
            is_current = job_id == self.game.player.job
            color = (50, 50, 150) if is_current else (0, 0, 200)
            pygame.draw.rect(self.screen, color, rect)
            
            job_name_text = self.font_small.render(self.game.job_data[job_id]["name"], True, WHITE)
            self.screen.blit(job_name_text, (button_x + 10, job_change_y + 5))
            
            if not is_current:
                self.job_change_buttons.append((rect, job_id))


    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_j or event.key == pygame.K_ESCAPE:
                self.game.job_menu_active = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                for rect, skill in self.unlock_buttons:
                    if rect.collidepoint(event.pos):
                        self.unlock_skill(skill)
                        return
                
                if self.master_button_rect and self.master_button_rect.collidepoint(event.pos):
                    self.master_job()
                    return

                for rect, job_id in self.job_change_buttons:
                    if rect.collidepoint(event.pos):
                        self.change_job(job_id)
                        return

    def unlock_skill(self, skill):
        skill_name = skill["name"]
        jp_cost = skill["jp_cost"]
        player = self.game.player

        if skill_name not in player.skills and player.jp >= jp_cost:
            player.jp -= jp_cost
            player.skills.append(skill_name)
            self.game.sound_manager.play('magic')

    def master_job(self):
        player = self.game.player
        current_job_id = player.job
        
        if current_job_id not in player.mastered_jobs:
            job_skills = self.game.job_data[current_job_id]["skills"]
            unlocked_job_skills = [s for s in job_skills if s["name"] in player.skills]
            if len(unlocked_job_skills) == len(job_skills):
                player.mastered_jobs.append(current_job_id)
                self.game.message_log.log_system(f"Job {current_job_id.capitalize()} mastered!")
                # For now, no prestige bonus is applied.

    def change_job(self, job_id):
        player = self.game.player
        if player.job != job_id:
            player.job = job_id
            player.jp = 0 # Reset JP on job change
            self.game.message_log.log_system(f"Changed job to {job_id.capitalize()}.")
