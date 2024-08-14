import pygame as pg
import numpy as np

IMAGE_NAMES = (
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", 
    "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", 
    "y", "z", "za", "zb", "zc", "zd")

pg.init()
screen = pg.display.set_mode((1280, 800))
clear_color = (32, 64, 64)
clock = pg.time.Clock()

images = {}
for name in IMAGE_NAMES:
    filename = f"../sprites/{name}.png"
    raw_surface = pg.image.load(filename).convert_alpha()
    raw_rect = raw_surface.get_rect()
    w = int(0.1 * raw_rect.width)
    h = int(0.1 * raw_rect.height)
    images[name] = pg.transform.scale(raw_surface, (w,h))

object_count = 128
objects = []
for i in range(object_count):
    x = np.random.randint(0, 1280)
    y = np.random.randint(0, 800)
    code = IMAGE_NAMES[np.random.randint(0, len(IMAGE_NAMES))]
    sprite: pg.Surface = images[code]
    rect = sprite.get_rect().move(x,y)
    objects.append((sprite, rect))

done = False
while not done:

    for event in pg.event.get():
        if event.type == pg.KEYDOWN \
            and event.key == pg.K_ESCAPE:
            done = True

    screen.fill(clear_color)

    screen.fblits(objects)

    pg.display.flip()

    clock.tick()
    framerate = int(clock.get_fps())
    pg.display.set_caption(f"framrate: {framerate}")