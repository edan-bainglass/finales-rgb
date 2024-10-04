#!/usr/bin/env python

# Avoid useless prompt when loading pygame
from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import time
import sys


def show_fullscreen_color(rgb_color, duration):
    """
    Pass RGB color as 3 integers (0 to 255).
    Duration is in seconds: None for just returning immediately leaving the color on the screen.
    You need to call pygame.quit() to close the window.
    """
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    running = True

    ## Hide the mouse cursor
    # Temporarily disabled to facilitate debugging in case of problems
    # pygame.mouse.set_visible(False)

    start = time.time()
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                # Stop also on click
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill(rgb_color)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

        if duration is None:
            return
        if time.time() - start > duration:
            running = False

    pygame.quit()


def stop_pygame():
    pygame.quit()


if __name__ == "__main__":
    # Example usage
    # rgb_color = (255, 0, 0)  # Red color
    rgb_color = (int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    assert all(
        0 <= c <= 255 for c in rgb_color
    ), "RGB color values must be in the range [0, 255]"
    if len(sys.argv) >= 5:
        duration = int(sys.argv[4])
    else:
        duration = 2  # Display for XX seconds
    show_fullscreen_color(rgb_color, duration)
