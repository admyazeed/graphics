import numpy as np
import pygame as pg
from Geometry import Geometry
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from Texture import Texture


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


def orthographic(left, right, bottom, top, near, far):
    return np.array(
        [
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1],
        ],
        dtype=np.float32,
    )


def normalize(v):
    return v / np.linalg.norm(v)


def lookAt(eye, target, up):
    forward = normalize(target - eye)
    right = normalize(np.cross(forward, up))
    true_up = np.cross(right, forward)

    return np.array(
        [
            [right[0], right[1], right[2], -np.dot(right, eye)],
            [true_up[0], true_up[1], true_up[2], -np.dot(true_up, eye)],
            [-forward[0], -forward[1], -forward[2], np.dot(forward, eye)],
            [0, 0, 0, 1],
        ],
        dtype=np.float32,
    )


class OpenGLWindow:
    def __init__(self):
        self.triangle = None
        self.clock = pg.time.Clock()
        self.time = 0
        self.earth_speed = 1
        self.isPaused = False
        self.camera_angle = 0
        self.camera_height = 2
        self.camera_radius = 3

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

        # Get uniform locations
        glUseProgram(self.shader)
        self.modelLoc = glGetUniformLocation(self.shader, "model")
        self.colorLoc = glGetUniformLocation(self.shader, "objectColor")
        self.viewLoc = glGetUniformLocation(self.shader, "view")
        self.projLoc = glGetUniformLocation(self.shader, "projection")
        self.textureLoc = glGetUniformLocation(self.shader, "imageTexture")

        glUniform1i(self.textureLoc, 0)

        self.sun = Geometry("./resources/sphere.txt")
        self.earth = Geometry("./resources/sphere.txt")
        self.moon = Geometry("./resources/sphere.txt")

        self.sun_texture = Texture("./resources/sun_texture.png")
        self.earth_texture = Texture("./resources/earth_texture.png")
        self.moon_texture = Texture("./resources/moon_texture.png")

        print("Setup complete!")

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)

        # Update the rotation angle each frame, accounting for different framerates
        dt = self.clock.tick(60) / 1000.0
        if not self.isPaused:
            self.time += self.earth_speed * dt
            self.time %= 2 * np.pi  # wrap around angle when it hits 360 degrees

        # Setup camera
        camX = self.camera_radius * np.cos(self.camera_angle)
        camZ = self.camera_radius * np.sin(self.camera_angle)
        eye = np.array([camX, self.camera_height, camZ], dtype=np.float32)
        target = np.array([0, 0, 0], dtype=np.float32)
        up = np.array([0, 1, 0], dtype=np.float32)

        # Create view matrix
        view = lookAt(eye, target, up)
        projection = orthographic(-2, 2, -2, 2, 0.1, 100)

        # Upload projection and view matrices
        glUniformMatrix4fv(self.viewLoc, 1, GL_TRUE, view)
        glUniformMatrix4fv(self.projLoc, 1, GL_TRUE, projection)

        # Create planet matrices
        sun_model = scale(0.1)
        earth_model = rotate(self.time) @ transform(0.65, 0, 0) @ scale(0.04)
        moon_model = (
            earth_model @ rotate(self.time * 2) @ transform(6, 0, 0) @ scale(0.4)
        )

        # Draw sun
        glActiveTexture(GL_TEXTURE0)
        self.sun_texture.bind()

        glUniformMatrix4fv(self.modelLoc, 1, GL_TRUE, sun_model)
        glUniform3f(self.colorLoc, 1.0, 0.8, 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sun.vertexCount)

        # Draw earth
        glActiveTexture(GL_TEXTURE0)
        self.earth_texture.bind()

        glUniformMatrix4fv(self.modelLoc, 1, GL_TRUE, earth_model)
        glUniform3f(self.colorLoc, 0, 0, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, self.earth.vertexCount)

        # Draw moon
        glActiveTexture(GL_TEXTURE0)
        self.moon_texture.bind()

        glUniformMatrix4fv(self.modelLoc, 1, GL_TRUE, moon_model)
        glUniform3f(self.colorLoc, 0.8, 0.8, 0.8)
        glDrawArrays(GL_TRIANGLES, 0, self.moon.vertexCount)

        # Swap the front and back buffers on the window, effectively putting what we just "drew"
        # Onto the screen (whereas previously it only existed in memory)
        pg.display.flip()

    def cleanup(self):
        glDeleteVertexArrays(1, (self.vao,))
        self.sun.cleanup()
        self.earth.cleanup()
        self.moon.cleanup()
