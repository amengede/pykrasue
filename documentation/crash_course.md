# A Crash Course in Krasue
First you must invoke a Krasue, it manages a GLFW window and a GPU Renderer (currently just OpenGL, but Vulkan support will be added in future). The GPU renderer has a very simple job, to draw sprites on the screen, but it uses GPU-Driven rendering to do that as quickly as possible.

Making Krasue run games for you is simple, extend the invocation class and implement your own update and drawing functions.

[readme](../readme.md)