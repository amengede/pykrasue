import krasue as ks
import time

class Game(ks.Invocation):

    
    def __init__(self, width: int, height: int):
        
        super().__init__(width, height)
        self.set_clear_color((32, 64, 64))

        # timing
        self.last_time = time.time()
        self.current_time = time.time()
        self.fps = 0

    def on_update(self) -> None:

        self.current_time = time.time()
        delta = self.current_time - self.last_time
        if (delta > 1):
            self.set_title(f"framerate: {int(self.fps / delta)}")
            self.fps = 0
            self.last_time = self.current_time

    def on_draw(self) -> None:

        self.fps += 1

game = Game(1280, 800)
game.run()