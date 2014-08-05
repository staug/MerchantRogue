__author__ = 'Tangil'

"""
Constants for the game
"""
import os
from pygame.locals import USEREVENT

GAME_WINDOW_SIZE = (1024, 768)
PLACE_WINDOW_SIZE = (640, 480)

DAWNLIKE_IMAGE_RESOURCE_FOLDER = str(os.curdir + os.sep + "resources" + os.sep + "img" + os.sep + "Dawnlike" + os.sep)
DAWNLIKE_TYPE = "DAWNLIKE"
DAWNLIKE_TILE_SIZE = (16, 16)

TILE_SIZE = (32, 32)

DISPLAY_EVENT = USEREVENT + 1
DEBUG_EVENT = USEREVENT + 2

