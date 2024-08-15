import krasue.krasue as ks
import time
import numpy as np

IMAGE_NAMES = (
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
    "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "za", "zb", "zc", "zd")

class Game(ks.Invocation):

    
    def __init__(self, width: int, height: int):
        
        super().__init__(width, height, backend=ks.BACKEND_MODERN_OGL)
    
    def on_setup(self):

        self.set_clear_color((32, 64, 64))

        # timing
        self.last_time = time.time()
        self.current_time = time.time()
        self.fps = 0

        images = []
        for name in IMAGE_NAMES:
            filename = f"../sprites/{name}.png"
            images.append(self.load_image(filename))
        
        self.sprite_group = ks.SpriteGroup(self)
        object_count = 128
        for i in range(object_count):
            x = np.random.randint(0, 1280)
            y = np.random.randint(0, 800)
            scale = np.random.uniform(0.05, 0.15)
            theta = np.random.randint(0, 360)
            object_type = images[np.random.randint(0, len(IMAGE_NAMES))]
            self.sprite_group.add(object_type, x, y, scale, theta)
        self.sprite_group.inscribe()


    def on_update(self) -> None:

        self.current_time = time.time()
        delta = self.current_time - self.last_time
        if (delta > 1):
            self.set_title(f"framerate: {int(self.fps / delta)}")
            self.fps = 0
            self.last_time = self.current_time

    def on_draw(self) -> None:

        self.sprite_group.draw()
        self.fps += 1

game = Game(1280, 800)
game.run()