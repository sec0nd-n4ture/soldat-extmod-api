from enum import Enum, auto

class ShaderLayer(Enum):
    BACKGROUND = 0
    PROPS_0 = auto()
    PLAYERS = auto()
    PROPS_1 = auto()
    POLY = auto()
    PROPS_2 = auto()
    INTERFACE = auto()
    POST_PROCESS = auto()


class ShaderType(Enum):
    GL_FRAGMENT_SHADER = 0x8b30
    GL_VERTEX_SHADER = 0x8b31
    GL_COMPUTE_SHADER = 0x91b9
    GL_TESS_EVALUATION_SHADER = 0x8e87
    GL_TESS_CONTROL_SHADER = 0x8e88
    GL_GEOMETRY_SHADER = 0x8dd9

GL_TEXTURE0 = 0x84c0
GL_TEXTURE1 = 0x84c1
GL_TEXTURE2 = 0x84c2

GL_TEXTURE_2D = 0xde1