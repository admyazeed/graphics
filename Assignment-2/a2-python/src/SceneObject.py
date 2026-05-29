import numpy as np
from OpenGL.GL import *


class SceneObject:
    def __init__(self, geometry, texture):
        self.geometry = geometry
        self.texture = texture
        self.model = np.identity(4, dtype=np.float32)  # 4x4 identity matrix

    def draw(self, modelLoc):
        self.texture.bind()
        glUniformMatrix4fv(modelLoc, 1, GL_TRUE, self.model)
        glDrawArrays(GL_TRIANGLES, 0, self.geometry.vertexCount)

    def cleanup(self):
        self.geometry.cleanup()
        self.texture.cleanup()
