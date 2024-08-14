# Clear Screen
Nothing exciting, just filling the screen with a solid color.

## Performance:
| Machine              | Pygame   | PyKrasue (AZDO OpenGL) | PyKrasue (Modern OpenGL) |
|---|---:|---:|---:|
| Asus Craptop         |  320 fps |  650 fps | 500 fps |
| MacBook Pro (M1 Pro) | 780 fps | Not Supported | 120 fps |
| Gaming PC (RTX 3070) | 1400 fps | 8700 fps | 8500 fps |

For some reason GLFW framerate is locked on macOS.