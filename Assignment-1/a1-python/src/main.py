import time

import pygame as pg
from GLWindow import *


def main():
    """The main method where we create and setup our PyGame program"""

    running = True
    pg.init()
    win = OpenGLWindow()
    win.initGL()
    while running:
        win.render()
        for event in pg.event.get():  # Grab all of the input events detected by PyGame
            if event.type == pg.QUIT:  # This event triggers when the window is closed
                running = False
            elif event.type == pg.KEYDOWN:
                if (
                    event.key == pg.K_q
                ):  # This event triggers when the q key is pressed down
                    running = False
        time.sleep(0.3)

    pg.quit()


if __name__ == "__main__":
    main()
