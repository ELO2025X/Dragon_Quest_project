import pygame

class Animation:
    def __init__(self, frames, duration=0.1, loop=True):
        self.frames = frames
        self.duration = duration
        self.loop = loop
        self.frame_index = 0
        self.timer = 0
        self.finished = False

    def reset(self):
        self.frame_index = 0
        self.timer = 0
        self.finished = False

    def update(self, dt):
        if self.finished:
            return self.frames[-1]

        self.timer += dt
        if self.timer >= self.duration:
            self.timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.frames) - 1
                    self.finished = True
        
        return self.frames[self.frame_index]

    def get_current_frame(self):
        return self.frames[self.frame_index]

class AnimationController:
    def __init__(self, default_state="idle"):
        self.animations = {}
        self.current_state = default_state
        self.current_animation = None
        self.flip_x = False

    def add_animation(self, name, animation):
        self.animations[name] = animation
        if self.current_animation is None:
            self.current_animation = animation

    def set_state(self, state):
        if state != self.current_state:
            self.current_state = state
            if state in self.animations:
                self.current_animation = self.animations[state]
                self.current_animation.reset()

    def update(self, dt):
        if self.current_animation:
            frame = self.current_animation.update(dt)
            if self.flip_x:
                return pygame.transform.flip(frame, True, False)
            return frame
        return None
