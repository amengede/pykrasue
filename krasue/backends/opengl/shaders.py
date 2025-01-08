from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

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
