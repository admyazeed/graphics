import numpy as np
import pygame as pg
from Geometry import Geometry
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


def scale(s):
    return np.array(
        [[s, 0, 0, 0], [0, s, 0, 0], [0, 0, s, 0], [0, 0, 0, 1]],
        dtype=np.float32,
    )


def transform(x, y, z):
    return np.array(
        [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]],
        dtype=np.float32,
    )


def rotate(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array(
        [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32
    )


class OpenGLWindow:
    def __init__(self):
        self.triangle = None
        self.clock = pg.time.Clock()
        self.time = 0

    def loadShaderProgram(self, vertex, fragment):
        with open(vertex, "r") as f:
            vertex_src = f.readlines()

        with open(fragment, "r") as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER),
        )

        return shader

    def initGL(self, screen_width=640, screen_height=640):
        pg.init()

        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 2)

        pg.display.set_mode((screen_width, screen_height), pg.OPENGL | pg.DOUBLEBUF)

        glEnable(GL_DEPTH_TEST)
        # Uncomment these two lines when perspective camera has been implemented
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)
        glClearColor(0, 0, 0, 1)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.shader = self.loadShaderProgram(
            "./shaders/simple.vert", "./shaders/simple.frag"
        )
        glUseProgram(self.shader)

        colorLoc = glGetUniformLocation(self.shader, "objectColor")
        glUniform3f(colorLoc, 1.0, 1.0, 1.0)

        # Uncomment this for model rendering
        self.sun = Geometry("./resources/sphere.txt")
        self.earth = Geometry("./resources/sphere.txt")
        self.moon = Geometry("./resources/sphere.txt")

        print("Setup complete!")

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)

        # Get model matrix and object colour from memory
        modelLoc = glGetUniformLocation(self.shader, "model")
        colorLoc = glGetUniformLocation(self.shader, "objectColor")

        # Update the rotation angle each frame, accounting for different framerates
        dt = self.clock.tick() / 1000.0
        self.time += dt
        self.time %= 2 * np.pi  # wrap around angle when it hits 360 degrees

        # Create planet matrices
        sun_model = scale(0.1)
        earth_model = rotate(self.time) @ transform(0.65, 0, 0) @ scale(0.04)
        moon_model = earth_model @ rotate(self.time) @ transform(6, 0, 0) @ scale(0.4)

        # Draw sun
        glUniformMatrix4fv(modelLoc, 1, GL_TRUE, sun_model)
        glUniform3f(colorLoc, 1.0, 0.8, 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sun.vertexCount)

        # Draw earth
        glUniformMatrix4fv(modelLoc, 1, GL_TRUE, earth_model)
        glUniform3f(colorLoc, 0, 0, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, self.earth.vertexCount)

        # Draw moon
        glUniformMatrix4fv(modelLoc, 1, GL_TRUE, moon_model)
        glUniform3f(colorLoc, 0.8, 0.8, 0.8)
        glDrawArrays(GL_TRIANGLES, 0, self.moon.vertexCount)

        # Swap the front and back buffers on the window, effectively putting what we just "drew"
        # Onto the screen (whereas previously it only existed in memory)
        pg.display.flip()

    def cleanup(self):
        glDeleteVertexArrays(1, (self.vao,))
        self.sun.cleanup()
        self.earth.cleanup()
        self.moon.cleanup()
