import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
import time

BACKEND_AZDO_OGL = 0

RENDER_BEHAVIOR_EACH_FRAME = 0
RENDER_BEHAVIOR_CONSERVATIVE = 1


class Invocation:
    """
        Represents top level program control.
        More or less creates a window and rendering backend,
        and gives slots for behavior extension.
    """
    __slots__ = ("_window", "_renderer")

    
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
            self._renderer = OpenGLAZDOEveryFrameRenderer()
            self._window = self._renderer.setup(width, height, title)
    
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

        glfw.set_window_title(self._window, title)

    def run(self) -> None:
        """
            Start the game's main loop.
        """

        while (not glfw.window_should_close(self._window)):

            if (glfw.get_key(
                self._window, 
                GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS):

                glfw.set_window_should_close(self._window, GLFW_CONSTANTS.GLFW_TRUE)
            
            glfw.poll_events()

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

class OpenGLAZDOEveryFrameRenderer:
    """
        Around OpenGL 4.x, a lot of the developments were focussed on improving
        performance. These "Approaching Zero Driver Overhead" features
        allowed for faster drawing of arbitrary objects.
    """

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
        
        window = glfw.create_window(width, height, title, None, None)
        glfw.make_context_current(window)
        return window
    
    def set_clear_color(self, color: tuple[float]) -> None:
        """
            Sets the color with which to clear the screen upon update.

            Parameters:

                color: the desired clear color, in rgba form, where each
                    channel is a float in the range [0, 1.0]
        """

        glClearColor(*color)

    def start_drawing(self) -> None:
        """
            Perform any necessary setup before receiving draw commands
        """

        glClear(GL_COLOR_BUFFER_BIT)

    def finish_drawing(self) -> None:
        """
            Called once per frame to draw stuff.
            Override this function to make your game draw things.
        """

        glFlush()
