import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PIL import Image
import numpy as np

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
        if (backend == BACKEND_MODERN_OGL and behavior == RENDER_BEHAVIOR_EACH_FRAME):
            self._renderer = ModernOpenGLEveryFrameRenderer()
            self._window = self._renderer.setup(width, height, title)
        
        self.on_setup()
        self._renderer.after_setup(self._window)

    def on_setup(self) -> None:
        """
            Override this method to implement any resource creation.
        """

        pass
    
    def load_image(self, filename: str) -> int:
        """
            Loads an image into memory.

            Parameters:

                filename: full filepath to the image to load.
            
            Returns:

                A handle to the loaded image, indicating the image's position
                within the set of loaded images.
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
            self._renderer.finish_drawing(self._window)

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
        self._transforms = np.zeros(4, dtype=np.float32)

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
            new_object_types[0:self._size] = self._object_types[:]
            self._object_types = new_object_types

            new_transforms = np.zeros(self._capacity * 8, dtype=np.float32)
            new_transforms[0:self._size * 4] = self._transforms[:]
            self._transforms = new_transforms

            self._capacity = len(self._object_types)
        
        #insert
        self._object_types[i] = object_type
        self._transforms[4 * i] = x
        self._transforms[4 * i + 1] = y
        self._transforms[4 * i + 2] = scale
        self._transforms[4 * i + 3] = rotate
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
#---- Renderers ----#
#---- OpenGL    ----#
#region
class OpenGLAZDOEveryFrameRenderer:
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

    def after_setup(self) -> None:
        """
            Upload all image handles to the GPU
        """

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

    def finish_drawing(self) -> None:
        """
            Called once per frame to draw stuff.
            Override this function to make your game draw things.
        """

        glFlush()

class ModernOpenGLEveryFrameRenderer:
    """
        OpenGL 3.3 renderer. Can do instanced rendering but not indirect.
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
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
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

        self._max_image_w = 0
        self._max_image_h = 0
        self._image_history: dict[str, int] = {}
        self._image_sizes = np.zeros(0, dtype = np.uint32)
        self._sprite_groups = []

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
            self._image_sizes = np.append(self._image_sizes, (w / 2, h / 2))
            self._max_image_w = max(w, self._max_image_w)
            self._max_image_h = max(h, self._max_image_h)

        return i
    
    def after_setup(self, window) -> None:
        """
            Upload all image handles to the GPU

            Parameters:

                window: the glfw window we'll be rendering to.
        """

        self._image_gl_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self._image_gl_id)
        glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8, 
                       self._max_image_w, self._max_image_h, len(self._image_history))
        
        for filename, i in self._image_history.items():
            with Image.open(filename, mode = "r") as img:
                w, h = img.size
                img = img.convert("RGBA")
                img_data = bytes(img.tobytes())
                glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 
                                0, 0, i, 
                                w, h, 1,
                                GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_R, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        vertex_src = """
#version 330
uniform vec4 screenSize_maxSize;
layout(location=0) in vec2 imageSize;
layout(location=1) in float objectType;
layout(location=2) in vec2 center;
layout(location=3) in float scale;
layout(location=4) in float rotation;

out vec3 fragTexCoord;

const vec2[4] coords = vec2[](
    vec2(-1, -1),
    vec2( 1, -1),
    vec2( 1,  1),
    vec2(-1,  1));

void main() {
    vec2 pos = coords[gl_VertexID];

    //scale
    pos.x = imageSize.x * scale * pos.x;
    pos.y = imageSize.y * scale * pos.y;

    //rotate
    float c = cos(radians(rotation));
    float s = sin(radians(rotation));
    float x = pos.x * c - pos.y * s;
    float y = pos.x * s + pos.y * c;
    pos.x = x;
    pos.y = y;

    //translate
    pos = pos + center;

    //convert to NDC
    //pos = (pos - screenSize_maxSize.xy);
    pos.x = (pos.x - screenSize_maxSize.x) / screenSize_maxSize.x;
    pos.y = (pos.y - screenSize_maxSize.y) / screenSize_maxSize.y;

    gl_Position = vec4(pos, 0.0, 1.0);

    pos = 0.5 * (coords[gl_VertexID] + vec2(1.0));
    pos.x = pos.x * imageSize.x / screenSize_maxSize.z;
    pos.y = pos.y * imageSize.y / screenSize_maxSize.w;
    pos.y = pos.y * -1;
    fragTexCoord = vec3(pos, objectType);
}
"""

        fragment_src = """
#version 330
uniform sampler2DArray material;

in vec3 fragTexCoord;

out vec4 color;

void main() {
    vec4 sampled = texture(material, fragTexCoord);

    if (sampled.a < 0.1) {
        discard;
    }

    color = sampled;
}
"""
        info = (
            (GL_VERTEX_SHADER, vertex_src),
            (GL_FRAGMENT_SHADER, fragment_src)
        )
        self._dummy_vao = glGenVertexArrays(1)
        glBindVertexArray(self._dummy_vao)
        self._shader = create_shader_program(info)
        glUseProgram(self._shader)
        self._global_info_location = glGetUniformLocation(self._shader, "screenSize_maxSize")
        self._object_info_location = glGetUniformLocation(self._shader, "imageSize_objectType")
        self._sprite_info_location = glGetUniformLocation(self._shader, "center_scale_rotate")

        w,h = glfw.get_framebuffer_size(window)
        global_info = np.array((w / 2, h / 2, self._max_image_w / 2, self._max_image_h / 2), dtype=np.uint32)
        glUniform4fv(self._global_info_location, 1, global_info)

    def start_drawing(self) -> None:
        """
            Perform any necessary setup before receiving draw commands
        """

        glClear(GL_COLOR_BUFFER_BIT)

    def register_sprite_group(self, object_types: np.ndarray, 
                              transforms: np.ndarray, size: int) -> None:
        
        buffer = np.zeros(7 * size, np.float32)
        for i in range(size):
            #object_type
            object_type = object_types[i]
            #image size: x
            buffer[7 * i]       = self._image_sizes[2*object_type]
            #image size: y
            buffer[7 * i + 1]   = self._image_sizes[2*object_type + 1]
            buffer[7 * i + 2]   = object_type

            #center: x
            buffer[7 * i + 3]   = transforms[4*i]
            #center: y
            buffer[7 * i + 4]   = transforms[4*i + 1]
            #scale
            buffer[7 * i + 5]   = transforms[4*i + 2]
            #rotation
            buffer[7 * i + 6]   = transforms[4*i + 3]
        
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)
        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)

        glBufferData(GL_ARRAY_BUFFER, size * 28, buffer, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribDivisor(0,1)

        glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)
        glVertexAttribDivisor(1,1)

        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribDivisor(2,1)

        glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(20))
        glEnableVertexAttribArray(3)
        glVertexAttribDivisor(3,1)

        glVertexAttribPointer(4, 1, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(24))
        glEnableVertexAttribArray(4)
        glVertexAttribDivisor(4,1)

        id = len(self._sprite_groups)
        self._sprite_groups.append((VAO, VBO, size))
        return id

    def draw_sprite_group(self, id: int) -> None:
        """
            Draw a set of sprites.

            Parameters:

                object_types: the image types for each sprite

                transform_infos: the transform for each sprite

                count: how many sprites to draw from the group
        """

        VAO, _ ,size = self._sprite_groups[id]
        glBindVertexArray(VAO)
        glDrawArraysInstanced(GL_TRIANGLE_FAN, 0, 4, size)

    def finish_drawing(self, window) -> None:
        """
            Called once per frame to draw stuff.
            Override this function to make your game draw things.
        """

        glFlush()
        #glfw.swap_buffers(window)

def create_shader_program(module_info: tuple[tuple[int, str]]) -> int:
    """
        Create an OpenGL shader program.

        Parameters:

            module_info: holds the source code and module types
    """

    modules = []

    for description in module_info:
        modules.append(create_shader_module(description))

    shader = compileProgram(*modules)

    for module in modules:
        glDeleteShader(module)

    return shader

def create_shader_module(module_info: tuple[int, str]) -> int:
    """
        Create an OpenGL shader module

        Parameters:

            module_info: describes the filenames and their module types.
    """

    module_type, src = module_info

    return compileShader(src, module_type)

#endregion
#-------------------#
