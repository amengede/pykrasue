# krasue.SpriteGroup:
A group of sprites (visible objects), can hold an arbitrary number of sprites of different types.

* init
* add
* remove
* inscribe

## Initialization
```
def __init__(self, invocation: Invocation):
```
Creates a new sprite group.

* **invocation**: The main invocation (necessary in order to fetch the rendering backend in a clean way)

## Creating sprites
```
def add(self, object_type: int, 
        x: float = 0.0, y: float = 0.0, 
        scale: float = 1.0, rotate: float = 0.0) -> int:
```
Creates a new sprite and adds it to this group. Returns the index of the sprite within the group, this can be used to later remove the sprite.

* **object_type**: the image index representing the sprite
* **x,y**: center position of the sprite, default is (0,0)
* **scale**: scale of the sprite, default is 1.0
* **rotate**: angle of the sprite, default is 0.0

## Group finalization
```
def inscribe(self) -> None:
```
Register this sprite group with the renderer, duplicates info and uploads it to the GPU.
            
## Destroying sprites
```
def remove(self, i: int):
```
Destroys the sprite at index i, maintains the order of the other sprites in the group.

## Drawing the Group
```
def draw(self) -> None:
```
Draw the sprite group.