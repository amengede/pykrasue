# Sprite Groups
Draw a lot of random images to the screen at random positions

## Performance:
### Lenovo ThinkPad T490s
|    n | Pygame | PyKrasue (AZDO OpenGL) | PyKrasue (Modern OpenGL) |
|-----:|---:|---:|---:|
|    1 | 400 fps | - | 750 fps |
|    2 | 400 fps | - | 640 fps |
|    4 | 350 fps | - | 540 fps |
|    8 | 370 fps | - | 440 fps |
|   16 | 330 fps | - | 330 fps |
|   32 | 290 fps | - | 260 fps |
|   64 | 230 fps | - | 175 fps |
|  128 | 170 fps | - | 130 fps |
|  256 | 120 fps | - | 100 fps |
|  512 |  80 fps | - | 100 fps |
| 1024 |  60 fps | - |  90 fps |