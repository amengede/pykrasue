# krasue.Invocation
An Invocation represents top level program control. It more or less creates a window and rendering backend, and gives slots for behavior extension.

* init
* set_clear_color
* set_title
* run
* on_update
* on_draw

## Initialization
```
def __init__(self, width: int, height: int, 
            title: str = "A spooky window",
            backend: int = BACKEND_AZDO_OGL,
            behavior: int = RENDER_BEHAVIOR_EACH_FRAME,
            frametime: float = 0.0):
```
Invokes a krasue (very spooky, your exorcism license is up to date, right?)

* **width, height**: size of the window
* **title**: title for the window caption
* **backend**: which sort of renderer the window should use
* **behavior**: how hard to push the renderer. Current options are to draw every frame (good for understanding compute power, but clogs the GPU with non-useful work) or to render conservatively (reduces non-visible renders, frees up CPU time on main thread)
* **frametime**: specifies how often to render (in milliseconds) when rendering conservatively.

## Setting the background color
```
def set_clear_color(self, color: tuple[int]) -> None:
```
Sets the color with which to clear the screen upon update.

* **color**: the desired clear color, in rgb form, where each channel is an integer in the range [0, 255]

## Setting the window caption
```
def set_title(self, title: str) -> None:
```
Sets the title in the window's titlebar.

* **title**: the title for the window.

## Starting execution
```
def run(self) -> None:
```
Start the game's main loop.

## Updating
```
def on_update(self) -> None:
```
Called once per frame to update stuff (and things). Override this function to implement your game's update behavior.

## Drawing
```
def on_draw(self) -> None:
```
Called once per frame to draw stuff. Override this function to make your game draw things.

[readme](../../readme.md)