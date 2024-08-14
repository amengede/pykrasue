# A Crash Course in Krasue
First you must invoke a Krasue, it manages a GLFW window and a GPU Renderer (currently just OpenGL, but Vulkan support will be added in future). The GPU renderer has a very simple job, to draw sprites on the screen, but it uses GPU-Driven rendering to do that as quickly as possible.

Some resources are classes (such as sprite groups) and some are stored internally and then managed via integer ids (such as images). Under the hood the systems are data oriented, with the aim of presenting a user friendly interface.

Making Krasue run games for you is simple, extend the invocation class and implement your own update and drawing functions.

[readme](../readme.md)