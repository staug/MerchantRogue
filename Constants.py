__author__ = 'Tangil'

"""
Constants for the game
"""
import os
from pygame.locals import USEREVENT

GAME_WINDOW_SIZE = (1024, 768)
PLACE_WINDOW_SIZE = (640, 480)

IMAGE_RESOURCE_FOLDER_DAWNLIKE = str(os.curdir + os.sep + "resources" + os.sep + "img" + os.sep + "Dawnlike" + os.sep)
TILE_SIZE = (16, 16)

DISPLAY_EVENT = USEREVENT + 1
DEBUG_EVENT = USEREVENT + 2

