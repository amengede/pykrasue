from .common import *

class Renderer:
    """
        OpenGL 3.3 renderer. Can do instanced rendering but not indirect.
    """

    #__slots__ = (
    #    "_max_image_w ", "_max_image_h", "_image_history", "_image_sizes", 
    #    "_sprite_groups", "_image_gl_id", "_dummy_vao", "_shader",
    #    "_global_info_location")

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
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_RESIZABLE,
            GLFW_CONSTANTS.GLFW_FALSE)
        
        window = glfw.create_window(width, height, title, None, None)
        glfw.make_context_current(window)

        self._max_image_w = 0
        self._max_image_h = 0
        self._image_history: dict[str, int] = {}
        self._image_sizes = np.zeros(0, dtype = np.uint32)
        self._sprite_groups = []

        self._image_gl_id = 0
        self._dummy_vao = 0
        self._shader = 0
        self._global_info_location = 0
        self._object_info_location = 0
        self._sprite_info_location = 0

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

        if (len(self._image_history) > 0):

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
