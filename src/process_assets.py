import pygame
import os

def process_image(filename, colorkey=(0, 0, 0)):
    path = os.path.join("src", "assets", filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    try:
        image = pygame.image.load(path).convert()
        image.set_colorkey(colorkey)
        
        # Create a new surface with alpha channel
        new_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        new_image.fill((0, 0, 0, 0))
        new_image.blit(image, (0, 0))
        
        pygame.image.save(new_image, path)
        print(f"Processed {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")

def slice_tileset(filename, tile_size=32):
    path = os.path.join("src", "assets", filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    try:
        image = pygame.image.load(path).convert_alpha()
        width, height = image.get_size()
        
        count = 0
        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                rect = pygame.Rect(x, y, tile_size, tile_size)
                tile = image.subsurface(rect)
                
                tile_name = f"village_tile_{count}.png"
                tile_path = os.path.join("src", "assets", tile_name)
                pygame.image.save(tile, tile_path)
                print(f"Saved {tile_name}")
                count += 1
    except Exception as e:
        print(f"Error slicing {filename}: {e}")

def main():
    pygame.init()
    screen = pygame.display.set_mode((100, 100)) # Dummy screen for convert()
    
    # Process NPCs (assuming black background from generation, or we can try to detect corner color)
    # Since we don't know the exact background color generated, we might need to be careful.
    # Usually generated images have a specific background. If it's transparent already, this might not be needed.
    # But the user asked to "clear the background".
    # Let's assume the top-left pixel is the background color.
    
    files_to_process = ["ElderMira.png", "KingValen.png", "Villager.png"]
    
    for f in files_to_process:
        path = os.path.join("src", "assets", f)
        if os.path.exists(path):
            img = pygame.image.load(path)
            bg_color = img.get_at((0, 0))
            process_image(f, bg_color)
            
    # Slice tileset
    # First ensure it has transparency if needed, but usually tilesets are full blocks.
    # We'll just slice it.
    # Copy the generated tileset to assets first if not there.
    # (The previous step copied it as village_tileset.png? No, I didn't copy that one yet!)
    
    # Wait, I need to copy the village tileset first.
    pass

if __name__ == "__main__":
    main()
