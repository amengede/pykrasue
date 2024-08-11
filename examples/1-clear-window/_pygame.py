import pygame as pg
import time

pg.init()
screen = pg.display.set_mode((1280, 800))

last_time = time.time()
current_time = time.time()
fps = 0

running = True
while running:

    for event in pg.event.get():
        if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            running = False

    screen.fill((32, 64, 64))
    pg.display.update()
    fps += 1

    current_time = time.time()
    delta = current_time - last_time
    if (delta > 1):
        pg.display.set_caption(f"framerate: {int(fps / delta)}")
        fps = 0
        last_time = current_time