import pygame as pg
from GLWindow import *


def main():
    """The main method where we create and setup our PyGame program"""

    running = True
    pg.init()
    win = OpenGLWindow()
    win.initGL()
    print(
        "Controls:\nQ: Quit\nP: Pause/Unpause\nT: Increase orbit speed\nR: Decrease orbit speed\n"
    )
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
                elif event.key == pg.K_r:
                    if win.earth_speed > 1:  # Don't let speed decrease to 0
                        win.earth_speed -= 1
                elif event.key == pg.K_t:
                    win.earth_speed += 1
                elif event.key == pg.K_p:
                    win.isPaused = not win.isPaused  # pause/unpause

    pg.quit()


if __name__ == "__main__":
    main()
