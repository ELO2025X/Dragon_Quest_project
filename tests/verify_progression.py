
import sys
import os
import random

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from inventory import create_item, create_random_weapon, Item

def verify_progression():
    print("Verifying Progression System (Affixes)...")
    
    # 1. Test basic item creation
    sword = create_item("iron_sword")
    print(f"Created Basic Item: {sword.name}")
    print(f"  Stats: {sword.stats}")
    assert sword.name == "Iron Sword"
    assert sword.stats["strength"] == 3
    
    # 2. Test Affix Generation
    print("\nGenerating Random Weapons...")
    affix_found = False
    for i in range(20):
        w = create_random_weapon()
        if w and w.affix:
            print(f"  Found Affix Weapon: {w.name}")
            print(f"  Affix: {w.affix}")
            print(f"  Stats: {w.stats}")
            print(f"  Description: {w.description}")
            affix_found = True
            break
            
    if not affix_found:
        print("  Warning: No affix generated in 20 tries (unlucky? or broken?)")
    else:
        print("Affix Generation: PASS")

if __name__ == "__main__":
    verify_progression()
