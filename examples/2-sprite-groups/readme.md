# Sprite Groups
Draw a lot of random images to the screen at random positions

## Performance:

### Yoga
|    n | Pygame | PyKrasue (Modern OpenGL) |
|-----:|---:|---:|
|    1 | 60 fps | 350 fps |
|    2 | 60 fps | 350 fps |
|    4 | 60 fps | 350 fps |
|    8 | 60 fps | 300 fps |
|   16 | 55 fps | 300 fps |
|   32 | 45 fps | 250 fps |
|   64 | 35 fps | 150 fps |
|  128 | 25 fps | 130 fps |
|  256 | 16 fps | 60 fps |
|  512 | 10 fps | 40 fps |
| 1024 | 5 fps | 23 fps |

### Asus
|    n | Pygame | PyKrasue (Modern OpenGL) |
|-----:|---:|---:|
|    1 | 300 fps | 600 fps |
|    2 | 300 fps | 600 fps |
|    4 | 300 fps | 600 fps |
|    8 | 250 fps | 575 fps |
|   16 | 200 fps | 500 fps |
|   32 | 180 fps | 400 fps |
|   64 | 100 fps | 250 fps |
|  128 | 70 fps | 140 fps |
|  256 | 40 fps | 85 fps |
|  512 | 22 fps | 44 fps |
| 1024 | 12 fps | 24 fps |

### Thinkpad
|    n | Pygame | PyKrasue (Modern OpenGL) |
|-----:|---:|---:|
|    1 | 588 fps | 1800 fps |
|    2 | 588 fps | 1800 fps |
|    4 | 555 fps | 1700 fps |
|    8 | 520 fps | 1700 fps |
|   16 | 500 fps | 1500 fps |
|   32 | 384 fps | 1100 fps |
|   64 | 300 fps | 850 fps |
|  128 | 220 fps | 550 fps |
|  256 | 150 fps | 370 fps |
|  512 | 100 fps | 200 fps |
| 1024 | 65 fps | 110 fps |

### MSI
|    n | Pygame | PyKrasue (Modern OpenGL) |
|-----:|---:|---:|
|    1 | 1200 fps | 1650 fps |
|    2 | 1200 fps | 1650 fps |
|    4 | 1100 fps | 1650 fps |
|    8 | 1000 fps | 1500 fps |
|   16 | 900 fps | 1400 fps |
|   32 | 700 fps | 1750 fps |
|   64 | 600 fps | 1400 fps |
|  128 | 450 fps | 1200 fps |
|  256 | 300 fps | 900 fps |
|  512 | 200 fps | 600 fps |
| 1024 | 100 fps | 440 fps |

### Brewery
|    n | Pygame | PyKrasue (Modern OpenGL) |
|-----:|---:|---:|
|    1 | 1650 fps | 4150 fps |
|    2 | 1650 fps | 4100 fps |
|    4 | 1650 fps | 4050 fps |
|    8 | 1500 fps | 3900 fps |
|   16 | 1250 fps | 3900 fps |
|   32 | 1000 fps | 3900 fps |
|   64 | 700 fps | 3800 fps |
|  128 | 500 fps | 3600 fps |
|  256 | 300 fps | 2600 fps |
|  512 | 165 fps | 1450 fps |
| 1024 | 90 fps | 950 fps |