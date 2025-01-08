import numpy as np
from .shaders import *
from .texture_atlas import TextureAtlas
from ..data_types import *
from krasue.config import *

class Renderer:
    """
        Around OpenGL 4.x, a lot of the developments were focussed on improving
        performance. These "Approaching Zero Driver Overhead" features
        allowed for faster drawing of arbitrary objects.
    """
    __slots__ = (
        "_image_history", "_image_sizes", "_image_gl_id", 
        "_max_image_w", "_max_image_h",
        "_shader", "_dummy_vao", "_global_info_location", 
        "_object_info_location", "_sprite_info_location")


    def setup(self, width: int, height: int, title: str):
        """
            Builds a renderer

            Parameters:

                width, height: size of the window

                title: title for the window caption

            Returns:

                The window which will be rendered to
        """
        
        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,4)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,5)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, 
            GLFW_CONSTANTS.GLFW_TRUE)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, 
            GLFW_CONSTANTS.GLFW_FALSE)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_RESIZABLE,
            GLFW_CONSTANTS.GLFW_FALSE)
        
        window = glfw.create_window(width, height, title, None, None)
        glfw.make_context_current(window)

        #image loading stuff
        self._image_history: dict[str, int] = {}
        self._image_sizes = np.zeros(0, dtype = np.uint32)
        self._max_image_w = 0
        self._max_image_h = 0

        return window
    
    def set_clear_color(self, color: tuple[float]) -> None:
        """
            Sets the color with which to clear the screen upon update.

            Parameters:

                color: the desired clear color, in rgba form, where each
                    channel is a float in the range [0, 1.0]
        """

        glClearColor(*color)

    def load_image(self, filename: str) -> int:
        """
            Registers an image for loading.

            Parameters:

                filename: full filepath to the image to load.
            
            Returns:

                A handle to the loaded image, indicating the image's position
                within the set of loaded images.
        """

        if filename in self._image_history:
            return self._image_history[filename]

        i = len(self._image_history)
        self._image_history[filename] = i

        with Image.open(filename, mode = "r") as img:
            w, h = img.size
            self._image_sizes = np.append(self._image_sizes, (w,h))
            self._max_image_w = max(w, self._max_image_w)
            self._max_image_h = max(h, self._max_image_h)

        return i

    def after_setup(self, window) -> None:
        """
            Upload all image handles to the GPU
        """

        if len(self._image_history) > 0:

            self._image_gl_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D_ARRAY, self._image_gl_id)
            glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8, 
                        self._max_image_w, self._max_image_h, len(self._image_history))
            
            for filename, i in self._image_history.items():
                with Image.open(filename, mode = "r") as img:
                    w, h = img.size
                    data = bytes(img.convert("RGBA").tobytes())
                    glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 
                                    0, 0, i, 
                                    w, h, 0,
                                    GL_RGBA,GL_UNSIGNED_BYTE,data)
            
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_R, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    def start_drawing(self) -> None:
        """
            Perform any necessary setup before receiving draw commands
        """

        glClear(GL_COLOR_BUFFER_BIT)

    def finish_drawing(self, window) -> None:
        """
            Called once per frame to draw stuff.
            Override this function to make your game draw things.
        """

        glFlush()