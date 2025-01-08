import numpy as np
from .shaders import *
from .texture_atlas import TextureAtlas
from ..data_types import *
from krasue.config import *

class Renderer:
    """
        OpenGL 3.3 renderer. Can do instanced rendering but not indirect.
    """
    __slots__ = (
        "_atlas", "_sprite_groups", "_dummy_vao", 
        "_shader", "_global_info_location",
        "_shader", "_dummy_vao", "_global_info_location")
    

    def setup(self, width: int, height: int, title: str):
        """
            Builds a renderer

            Parameters:

                width, height: size of the window

                title: title for the window caption

            Returns:

                The window which will be rendered to
        """
        
        self._set_up_pygame(width, height, title)
        self._make_objects()
        self._set_up_opengl()

    def _set_up_pygame(self, width: int, height: int, title: str) -> any:
        """
            Initialize glfw, build a new window.

            Parameters:

                width, height: size of the window

                title: title for the window caption

            Returns:

                The window which will be rendered to
        """

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, 
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((width, height), pg.OPENGL|pg.DOUBLEBUF)
        pg.display.set_caption(title)
    
    def _make_objects(self) -> None:
        """
            Construct renderer objects
        """

        self._atlas = TextureAtlas()
        self._sprite_groups = []

        self._dummy_vao = 0
        self._shader = 0
        self._global_info_location = 0
    
    def _set_up_opengl(self) -> None:
        """
            Configure any one-time OpenGL setup.
        """

        glEnable(GL_STENCIL_TEST)
        glStencilMask(0xFF)
        glStencilFunc(GL_EQUAL, 0, 0xFF)
        glStencilOp(GL_KEEP, GL_INCR, GL_INCR)

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

        return self._atlas.load_image(filename)
    
    def after_setup(self) -> None:
        """
            Upload all image handles to the GPU

            Parameters:

                window: the glfw window we'll be rendering to.
        """

        self._atlas.build()

        vertex_src = """
#version 330
uniform vec4 screenSize_maxSize;
layout(location=0) in vec2 imageSize;
layout(location=1) in vec2 texOffset;
layout(location=2) in float layer;
layout(location=3) in vec2 center;
layout(location=4) in float scale;
layout(location=5) in float rotation;

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
    pos.x = (pos.x - screenSize_maxSize.x) / screenSize_maxSize.x;
    pos.y = (pos.y - screenSize_maxSize.y) / screenSize_maxSize.y;

    gl_Position = vec4(pos, 0.0, 1.0);

    vec2 offset;
    offset.x = texOffset.x / 4096.0;
    offset.y = texOffset.y / 4096.0;
    vec2 size = 0.5 * (coords[gl_VertexID] + vec2(1.0));
    size.x = (size.x * imageSize.x) / screenSize_maxSize.z;
    size.y = (size.y * imageSize.y) / screenSize_maxSize.w;
    //pos.y = pos.y * -1;
    fragTexCoord = vec3(offset + size, layer);
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

        w,h = pg.display.get_window_size()
        max_w, max_h = self._atlas.get_max_size()
        global_info = np.array((w / 2, h / 2, max_w / 2, max_h / 2), dtype=np.uint32)
        glUniform4fv(self._global_info_location, 1, global_info)

    def start_drawing(self) -> None:
        """
            Perform any necessary setup before receiving draw commands
        """

        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    def register_sprite_group(self, object_types: np.ndarray, 
                              transforms: np.ndarray, size: int) -> None:
        
        buffer = np.zeros(size, DATA_TYPE_VERTEX)
        for i in range(size):

            read_pos = size - 1 - i
            object_type = object_types[read_pos]
            
            w, h = self._atlas.get_image_size(object_type)
            buffer[i]['imageSize_x']   = w
            buffer[i]['imageSize_y']   = h

            x,y,z = self._atlas.get_offset(object_type)
            buffer[i]['texoffset_x']   = x
            buffer[i]['texoffset_y']   = y
            buffer[i]['layer']         = z

            buffer[i]['center_x']   = transforms[read_pos]['x']
            buffer[i]['center_y']   = transforms[read_pos]['y']
            buffer[i]['scale']      = transforms[read_pos]['scale']
            buffer[i]['rotation']   = transforms[read_pos]['rotation']
        
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)
        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)

        stride = DATA_TYPE_VERTEX.itemsize
        offset = 0
        glBufferData(GL_ARRAY_BUFFER, size * stride, buffer, GL_STATIC_DRAW)

        # layout(location=0) in vec2 imageSize;
        glVertexAttribPointer(0, 2, GL_HALF_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(0)
        glVertexAttribDivisor(0,1)
        offset += 4

        # layout(location=1) in vec2 texOffset;
        glVertexAttribPointer(1, 2, GL_HALF_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(1)
        glVertexAttribDivisor(1,1)
        offset += 4

        # layout(location=2) in float layer;
        glVertexAttribPointer(2, 1, GL_UNSIGNED_BYTE, GL_FALSE, stride, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(2)
        glVertexAttribDivisor(2,1)
        offset += 1

        # layout(location=3) in vec2 center;
        glVertexAttribPointer(3, 2, GL_HALF_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(3)
        glVertexAttribDivisor(3,1)
        offset += 4

        # layout(location=4) in float scale;
        glVertexAttribPointer(4, 1, GL_HALF_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(4)
        glVertexAttribDivisor(4,1)
        offset += 2

        # layout(location=5) in float rotation;
        glVertexAttribPointer(5, 1, GL_HALF_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        glEnableVertexAttribArray(5)
        glVertexAttribDivisor(5,1)

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

    def finish_drawing(self) -> None:
        """
            Called once per frame to draw stuff.
            Override this function to make your game draw things.
        """
        pg.display.flip()
