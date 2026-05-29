import numpy as np
import pygame as pg
from Geometry import Geometry
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from SceneObject import SceneObject
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
        self.orbit_angle = 0
        self.orbit_speed = 1
        self.isPaused = False
        self.camera_angle = 0
        self.camera_height = 2
        self.camera_radius = 3
        self.sirius_angle = 0

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
        glClearColor(0, 0, 0, 1)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.shader = self.loadShaderProgram(
            "./shaders/simple.vert", "./shaders/simple.frag"
        )

        # Get uniform locations
        glUseProgram(self.shader)
        self.modelLoc = glGetUniformLocation(self.shader, "model")
        self.viewLoc = glGetUniformLocation(self.shader, "view")
        self.projLoc = glGetUniformLocation(self.shader, "projection")
        self.textureLoc = glGetUniformLocation(self.shader, "imageTexture")
        self.viewPosLoc = glGetUniformLocation(self.shader, "viewPos")
        self.sunLightPosLoc = glGetUniformLocation(self.shader, "sunLightPos")
        self.sunLightColorLoc = glGetUniformLocation(self.shader, "sunLightColor")
        self.siriusPosLoc = glGetUniformLocation(self.shader, "siriusPos")
        self.siriusColorLoc = glGetUniformLocation(self.shader, "siriusColor")

        glUniform1i(self.textureLoc, 0)

        self.sun = SceneObject(
            Geometry("./resources/sphere.txt"), Texture("./resources/sun_texture.png")
        )
        self.earth = SceneObject(
            Geometry("./resources/sphere.txt"), Texture("./resources/earth_texture.png")
        )
        self.moon = SceneObject(
            Geometry("./resources/sphere.txt"), Texture("./resources/moon_texture.png")
        )
        self.sirius = SceneObject(
            Geometry("./resources/sphere.txt"),
            Texture("./resources/sirius_texture.png"),
        )  # Second light

        print("Setup complete!")

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear buffers
        glUseProgram(self.shader)

        # Update the rotation angle each frame, accounting for different framerates
        dt = self.clock.tick(60) / 1000.0
        if not self.isPaused:
            self.orbit_angle += self.orbit_speed * dt
            self.orbit_angle %= 2 * np.pi  # wrap around angle when it hits 360 degrees
            self.sirius_angle += dt
            self.sirius_angle %= 2 * np.pi

        # Setup camera
        camX = self.camera_radius * np.cos(self.camera_angle)
        camZ = self.camera_radius * np.sin(self.camera_angle)
        eye = np.array([camX, self.camera_height, camZ], dtype=np.float32)
        target = np.array([0, 0, 0], dtype=np.float32)
        up = np.array([0, 1, 0], dtype=np.float32)

        # Setup lighting
        glUniform3fv(self.viewPosLoc, 1, eye)
        glUniform3f(self.sunLightPosLoc, 0.0, 0.0, 0.0)  # Sun position
        glUniform3f(self.sunLightColorLoc, 1.0, 0.9, 0.6)  # Yellowish colour

        ## Second light
        sirius_pos = np.array(
            [
                1.5 * np.cos(self.sirius_angle),
                0.5,
                1.5 * np.sin(self.sirius_angle),
            ],
            dtype=np.float32,
        )
        glUniform3fv(self.siriusPosLoc, 1, sirius_pos)
        glUniform3f(self.siriusColorLoc, 0.2, 0.4, 1.0)  # Bluish colour

        # Create view matrix
        view = lookAt(eye, target, up)
        projection = orthographic(-2, 2, -2, 2, 0.1, 100)

        # Upload projection and view matrices
        glUniformMatrix4fv(self.viewLoc, 1, GL_TRUE, view)
        glUniformMatrix4fv(self.projLoc, 1, GL_TRUE, projection)

        # Create transformation matrices
        self.sun.model = scale(0.1)
        self.earth.model = (
            rotate(self.orbit_angle) @ transform(0.65, 0, 0) @ scale(0.04)
        )
        self.moon.model = (
            self.earth.model
            @ rotate(self.orbit_angle * 2)
            @ transform(6, 0, 0)
            @ scale(0.4)
        )
        self.sirius.model = transform(
            sirius_pos[0], sirius_pos[1], sirius_pos[2]
        ) @ scale(0.02)

        glActiveTexture(GL_TEXTURE0)
        self.sun.draw(self.modelLoc)
        self.earth.draw(self.modelLoc)
        self.moon.draw(self.modelLoc)
        self.sirius.draw(self.modelLoc)

        pg.display.flip()

    def cleanup(self):
        glDeleteVertexArrays(1, (self.vao,))
        self.sun.cleanup()
        self.earth.cleanup()
        self.moon.cleanup()
        self.sirius.cleanup()
