<img src="header.png"></img>

Krasue is a high performance alternative to pygame and arcade. Pygame is a wrapper around SDL, which claims to be hardware accelerated, but either isn't or isn't fast enough. Arcade claims to be faster than pygame due to its OpenGL backend, but takes far too long to load and is measurably slower. A simple OpenGL program should outperform both of them, hence Krasue.

Note: PyKrasue is still in its early days and is not yet fully featured. Examples are a good indicator of what can currently be done.
### Installation
Fresh install:
```
pip install PyKrasue
```
Krasue will be going through frequent updates for the time being, to update an existing installation run:
```
pip install --upgrade --force-reinstall PyKrasue
```
### Documentation
[Programming Model](documentation/crash_course.md)

API Reference:
* [Invocation](documentation/reference/invocation.md)
* [Sprite Group](documentation/reference/sprite_group.md)