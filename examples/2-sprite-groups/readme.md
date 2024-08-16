# Sprite Groups
Draw a lot of random images to the screen at random positions

## Performance:
### Lenovo ThinkPad T490s
|    n | Pygame | PyKrasue (AZDO OpenGL) | PyKrasue (Modern OpenGL) |
|-----:|---:|---:|---:|
|    1 | 400 fps | - | 700 fps |
|    2 | 400 fps | - | 670 fps |
|    4 | 350 fps | - | 560 fps |
|    8 | 370 fps | - | 450 fps |
|   16 | 330 fps | - | 330 fps |
|   32 | 290 fps | - | 240 fps |
|   64 | 230 fps | - | 139 fps |
|  128 | 170 fps | - |  80 fps |
|  256 | 120 fps | - |  45 fps |
|  512 |  80 fps | - |  20 fps |
| 1024 |  60 fps | - |  12 fps |

Seems to work well on modern GPUs but absolutely tanks on low end systems,
find way to reduce overdraw.