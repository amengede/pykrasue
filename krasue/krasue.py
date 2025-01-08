from .config import *
import numpy as np
import krasue.backends.opengl.modern as ogl_modern
import krasue.backends.opengl.azdo as ogl_azdo
from krasue.backends.data_types import *

BACKEND_AZDO_OGL = 0
BACKEND_MODERN_OGL = 1

RENDER_BEHAVIOR_EACH_FRAME = 0
RENDER_BEHAVIOR_CONSERVATIVE = 1

class Invocation:
    """
        Represents top level program control.
        More or less creates a window and rendering backend,
        and gives slots for behavior extension.
    """
    __slots__ = ("_renderer", )

    
    def __init__(self, width: int, height: int, 
                 title: str = "A spooky window",
                 backend: int = BACKEND_AZDO_OGL,
                 behavior: int = RENDER_BEHAVIOR_EACH_FRAME):
        """
            Invoke a krasue (very spooky, your exorcism license is
            up to date, right?)

            Parameters:

                width, height: size of the window

                title: title for the window caption

                backend: which sort of renderer the window
                    should use

                behavior: how hard to push the renderer.
                    Current options are to draw every frame
                    (good for understanding compute power, but
                    clogs the GPU with non-useful work)
                    or to render conservatively
                    (reduces non-visible renders, frees up CPU time
                    on main thread)
        """
        
        if (backend == BACKEND_AZDO_OGL and behavior == RENDER_BEHAVIOR_EACH_FRAME):
            self._renderer = ogl_azdo.Renderer()
            self._renderer.setup(width, height, title)
        if (backend == BACKEND_MODERN_OGL and behavior == RENDER_BEHAVIOR_EACH_FRAME):
            self._renderer = ogl_modern.Renderer()
            self._renderer.setup(width, height, title)
        
        self.on_setup()
        self._renderer.after_setup()

    def on_setup(self) -> None:
        """
            Override this method to implement any resource creation.
        """

        pass
    
    def new_object(self, filename: str) -> int:
        """
            Creates a new object.

            Parameters:

                filename: full filepath to associated image.
            
            Returns:

                The ID of the new object.
        """

        return self._renderer.load_image(filename)

    def set_clear_color(self, color: tuple[int]) -> None:
        """
            Sets the color with which to clear the screen upon update.

            Parameters:

                color: the desired clear color, in rgb form, where each
                    channel is an integer in the range [0, 255]
        """

        color = (
            min(1.0, max(0.0, color[0] / 255)), 
            min(1.0, max(0.0, color[1] / 255)), 
            min(1.0, max(0.0, color[2] / 255)), 1.0)
        self._renderer.set_clear_color(color)
    
    def set_title(self, title: str) -> None:
        """
            Set the title in the window's titlebar.

            Parameters:

                title: the title for the window.
        """

        pg.display.set_caption(title)

    def run(self) -> None:
        """
            Start the game's main loop.
        """

        running = True
        while (running):

            for event in pg.event.get():
                if event.type == pg.KEYDOWN \
                    and event.key == pg.K_ESCAPE:
                
                    running = False

            self.on_update()

            self._renderer.start_drawing()
            self.on_draw()
            self._renderer.finish_drawing()

    def on_update(self) -> None:
        """
            Called once per frame to update stuff (and things).
            Override this function to implement your game's update behavior.
        """

        pass

    def on_draw(self) -> None:
        """
            Called once per frame to draw stuff.
            Override this function to make your game draw things.
        """

        pass

class SpriteGroup:
    """
        A group of sprites, can hold an arbitrary number of sprites
        of different types.
    """
    __slots__ = (
        "_renderer", "_object_types", "_transforms",
        "_size", "_capacity", "_id")

    
    def __init__(self, invocation: Invocation):
        """
            Invoke a krasue (very spooky, your exorcism license is
            up to date, right?)

            Parameters:

                width, height: size of the window

                title: title for the window caption

                backend: which sort of renderer the window
                    should use

                behavior: how hard to push the renderer.
                    Current options are to draw every frame
                    (good for understanding compute power, but
                    clogs the GPU with non-useful work)
                    or to render conservatively
                    (reduces non-visible renders, frees up CPU time
                    on main thread)
        """
        
        self._renderer = invocation._renderer
        
        self._object_types = np.zeros(1, dtype=np.uint32)
        self._transforms = np.zeros(1, dtype=DATA_TYPE_TRANSFORM)

        self._size = 0
        self._capacity = 1
    
    def add(self, object_type: int, 
            x: float = 0.0, y: float = 0.0, 
            scale: float = 1.0, rotate: float = 0.0) -> int:
        """
            Adds a new sprite to this group

            Parameters:

                object_type: the image index representing the sprite
                x,y: center position of the sprite, default is (0,0)
                scale: scale of the sprite, default is 1.0
                rotate: angle of the sprite, default is 0.0
            
            Returns:

                The index of the sprite within the group, this can be used to
                later remove the sprite.
        """

        #position to insert at
        i = self._size

        #resize if needed
        if self._size >= self._capacity:
            new_object_types = np.zeros(self._capacity * 2, dtype=np.uint32)
            new_object_types[:self._size] = self._object_types[:]
            self._object_types = new_object_types

            new_transforms = np.zeros(self._capacity * 2, dtype=DATA_TYPE_TRANSFORM)
            new_transforms[:self._size] = self._transforms[:]
            self._transforms = new_transforms

            self._capacity = len(self._object_types)
        
        #insert
        self._object_types[i] = object_type
        self._transforms[i]['x'] = x
        self._transforms[i]['y'] = y
        self._transforms[i]['scale'] = scale
        self._transforms[i]['rotation'] = rotate
        self._size += 1

        return i

    def remove(self, i: int):
        """
            destroys the sprite at index i, maintains the order of the
            other sprites in the group.
        """
        
        np.delete(self._object_types, i)
        np.delete(self._transforms, np.s_[4 * i : 4 * (i + 1)])
        self._size -= 1

    def draw(self) -> None:
        """
            draw the sprite group
        """

        self._renderer.draw_sprite_group(self._id)

    def inscribe(self) -> None:
        """
            Register this sprite group with the renderer, duplicates info and uploads
            it to the GPU.
        """

        self._id = self._renderer.register_sprite_group(
            self._object_types, self._transforms, self._size)