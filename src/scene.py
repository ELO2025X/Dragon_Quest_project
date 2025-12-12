import pygame
import numpy as np
from settings import *
from game_state import GameState
from battle import Battle

class BaseScene(GameState):
    def __init__(self, manager, **kwargs):
        super().__init__(manager)

    def handle_input(self, event):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError

class TitleScene(BaseScene):
    def __init__(self, manager, **kwargs):
        super().__init__(manager)
        self.font_title = pygame.font.Font(None, 100)
        self.font_sub = pygame.font.Font(None, 40)
        self.font_inst = pygame.font.Font(None, 30)

    def handle_input(self, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.manager.game.change_scene("world")
            if event.key == pygame.K_ESCAPE:
                self.manager.game.quit()

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(BLACK)
        
        title_text = self.font_title.render("SERPENT'S QUEST", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(WIDTH/2, HEIGHT/4))
        surface.blit(title_text, title_rect)
        
        sub_text = self.font_sub.render("The Lumina Shard", True, WHITE)
        sub_rect = sub_text.get_rect(center=(WIDTH/2, HEIGHT/4 + 60))
        surface.blit(sub_text, sub_rect)
        
        inst_text = self.font_inst.render("Press SPACE to Start", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH/2, HEIGHT * 3/4))
        surface.blit(inst_text, inst_rect)

class WorldScene(BaseScene):
    def __init__(self, manager, **kwargs):
        super().__init__(manager)
        
    def handle_input(self, event):
        game = self.manager.game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.quit() # Or open menu
            
            if not game.in_dialogue:
                if event.key == pygame.K_SPACE:
                    if not game.check_npc_interaction():
                        # Check for object interaction
                        hits = pygame.sprite.spritecollide(game.player, game.interactables, False)
                        for hit in hits:
                            if hasattr(hit, 'interact'):
                                hit.interact()
                                break # Interact with one object at a time
                
                if event.key == pygame.K_F10:
                    game.debug = not game.debug
                if game.debug:
                    if event.key == pygame.K_F1:
                        game.player.level_up()
                    if event.key == pygame.K_F2:
                        game.player.noclip = not getattr(game.player, 'noclip', False)
                    if event.key == pygame.K_F3:
                        if game.save_manager:
                            game.save_manager.save_game()
                    if event.key == pygame.K_F4:
                        if hasattr(game, 'quest_manager'):
                            game.quest_manager.flags['test_flag'] = True
                    if event.key == pygame.K_F6:
                        # Trigger Bud Light Boogie Duo
                        daryl = game.create_enemy("daryl_ledeay")
                        george = game.create_enemy("chicken_george")
                        game.change_scene("combat", enemies=[daryl, george])

            elif game.in_dialogue:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    game.in_dialogue = False
                    game.current_npc = None

    def update(self, dt):
        game = self.manager.game
        if not game.in_battle:
            game.all_sprites.update(dt)
            game.camera.update(game.player)
            
            grid_x = int(game.player.hit_rect.centerx / TILESIZE)
            grid_y = int(game.player.hit_rect.centery / TILESIZE)
            
            # Check for exiting the map boundaries (Infinite World)
            if grid_x < 0 or grid_x >= game.map.world_width or grid_y < 0 or grid_y >= game.map.world_height:
                # Determine direction
                direction = ""
                if grid_x < 0: direction = "west"
                elif grid_x >= game.map.world_width: direction = "east"
                elif grid_y < 0: direction = "north"
                elif grid_y >= game.map.world_height: direction = "south"
                
                # Generate new sector
                biome = random.choice(["forest", "desert", "snow"])
                sector_data = game.world_gen.generate_sector(biome)
                new_map_id = sector_data["id"]
                game.maps[new_map_id] = sector_data
                
                # Calculate new spawn based on direction (enter from opposite side)
                new_spawn_x, new_spawn_y = 10, 10
                if direction == "west": new_spawn_x, new_spawn_y = sector_data["width"] - 2, grid_y
                elif direction == "east": new_spawn_x, new_spawn_y = 1, grid_y
                elif direction == "north": new_spawn_x, new_spawn_y = grid_x, sector_data["height"] - 2
                elif direction == "south": new_spawn_x, new_spawn_y = grid_x, 1
                
                # Clamp spawn values
                new_spawn_x = max(1, min(sector_data["width"]-2, new_spawn_x))
                new_spawn_y = max(1, min(sector_data["height"]-2, new_spawn_y))
                
                game.load_map(new_map_id, new_spawn_x, new_spawn_y)
                game.message_log.log_system(f"Entered {biome} sector")
            
            # Standard Exit Check
            exit_point = game.map.check_exit(grid_x, grid_y)
            if exit_point:
                game.load_map(exit_point["target_map"], exit_point["spawn_x"], exit_point["spawn_y"])
            
            hits = pygame.sprite.spritecollide(game.player, game.enemies, False, pygame.sprite.collide_rect_ratio(1.2))
            if hits:
                self.manager.game.change_scene("combat", enemies=hits)

            # Pickup Collision
            hits = pygame.sprite.spritecollide(game.player, game.pickups, True)
            for hit in hits:
                if hit.type == "potion":
                    game.player.combat.heal(20)
                    game.message_log.log_system("Picked up Potion! +20 HP")
                    game.sound_manager.play("magic") # Use magic sound for now
                elif hit.type == "ether":
                    game.player.combat.restore_mp(10)
                    game.message_log.log_system("Picked up Ether! +10 MP")
                    game.sound_manager.play("magic")
                elif hit.type == "gold":
                    game.player.gold += 50
                    game.message_log.log_system("Picked up Gold! +50 G")
                    game.sound_manager.play("menu") # Coin sound?
                elif hit.type == "powerup_str":
                    game.player.combat.stats[0] += 1 # Strength
                    game.message_log.log_system("Strength Up! +1 STR")
                    game.sound_manager.play("magic")
                elif hit.type == "powerup_spd":
                    game.player.combat.stats[3] += 1 # Agility
                    # Update speed if needed? MovementComponent might need refresh?
                    # game.player.movement.speed ... usually calculated from agility?
                    # Currently strict speed in MovementComponent.
                    # Let's just log it.
                    game.message_log.log_system("Agility Up! +1 AGI")
                    game.sound_manager.play("magic")

    def draw(self, surface):
        game = self.manager.game
        surface.fill(BLACK)
        game.map.draw(surface, game.camera)
        for sprite in game.all_sprites:
            surface.blit(sprite.image, game.camera.apply(sprite))
            
        if game.debug:
            game.draw_debug()

class CombatScene(BaseScene):
    def __init__(self, manager, **kwargs):
        super().__init__(manager)
        enemies = kwargs.get("enemies", [])
        self.battle_system = Battle(self.manager.game, self.manager.game.player, enemies)

    def handle_input(self, event):
        self.battle_system.handle_input(event)
        if not self.battle_system.active:
            self.manager.game.change_scene("world")
            self.manager.game.in_battle = False
            self.manager.game.battle = None


    def update(self, dt):
        self.battle_system.update(dt)


    def draw(self, surface):
        game = self.manager.game
        for y in range(HEIGHT):
            if y < HEIGHT // 2:
                r = int(10 + (y / (HEIGHT // 2)) * 40)
                g = int(10 + (y / (HEIGHT // 2)) * 20)
                b = int(40 + (y / (HEIGHT // 2)) * 60)
                color = (r, g, b)
            else:
                ratio = (y - HEIGHT // 2) / (HEIGHT // 2)
                r = int(30 + ratio * 20)
                g = int(50 + ratio * 30)
                b = int(20 + ratio * 10)
                color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))
            
        pygame.draw.ellipse(surface, (40, 40, 40), (100, 250, 200, 60))
        pygame.draw.ellipse(surface, (40, 40, 40), (WIDTH - 300, 250, 200, 60))

        if game.player.image:
            # Use already scaled player image
            player_img = game.player.image
            # Position the player image
            player_pos = player_img.get_rect(center=(130 + 128/2, 150 + 128/2)) # Center at original blit position
            surface.blit(player_img, player_pos)
            
        for i, enemy in enumerate(self.battle_system.enemies):
            if enemy.image:
                # Use already scaled enemy image
                enemy_img = enemy.image
                enemy_img = pygame.transform.flip(enemy_img, True, False) # Still flip as before
                # Adjust position to center bottom based on original logic, but using current image size
                
                # Calculate the center of the original intended blit area
                original_blit_center_x = WIDTH - 270 - i * 80 + 128/2
                original_blit_center_y = 150 + i * 20 + 128/2
                
                enemy_pos = enemy_img.get_rect(center=(original_blit_center_x, original_blit_center_y))
                surface.blit(enemy_img, enemy_pos)
        
        if self.battle_system.state == "target_selection":
            if self.battle_system.enemies:
                cursor_x = WIDTH - 270 - self.battle_system.selected_target * 80 + 64
                cursor_y = 150 + self.battle_system.selected_target * 20 - 20
                pygame.draw.polygon(surface, (255, 255, 0), [(cursor_x, cursor_y), (cursor_x - 10, cursor_y - 15), (cursor_x + 10, cursor_y - 15)])
