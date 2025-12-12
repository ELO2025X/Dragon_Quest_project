# DragonQuest/src/components/ai.py
import random
from components.component import Component
from components.movement import MovementComponent

class AIComponent(Component):
    def __init__(self, owner):
        super().__init__(owner)
        self.movement_component = self.owner.get_component(MovementComponent)
        self.wander_timer = 0
        self.wander_interval = random.uniform(1.0, 3.0)

    def update(self, dt):
        if not self.movement_component:
            return

        self.wander_timer += dt
        if self.wander_timer >= self.wander_interval:
            self.wander_timer = 0
            self.wander_interval = random.uniform(1.0, 3.0)
            
            if random.random() < 0.5:
                direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                self.movement_component.vx = direction[0] * 30
                self.movement_component.vy = direction[1] * 30
            else:
                self.movement_component.vx = 0
                self.movement_component.vy = 0
        
        dx = self.movement_component.vx * dt
        dy = self.movement_component.vy * dt
        self.movement_component.move(dx, dy)
