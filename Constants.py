__author__ = 'Tangil'

"""
Constants for the game
"""
import os

from pygame.locals import USEREVENT


GAME_WINDOW_SIZE = (600, 600)
# PLACE_WINDOW_SIZE = (640, 480)
PLACE_WINDOW_SIZE = GAME_WINDOW_SIZE
TILE_SIZE = (16, 16)

DISPLAY_EVENT = USEREVENT + 1
DEBUG_EVENT = USEREVENT + 2

# STYLE INFORMATION
DAWNLIKE_IMAGE_RESOURCE_FOLDER = str(os.curdir + os.sep + "resources" + os.sep + "img" + os.sep + "Dawnlike" + os.sep)
DAWNLIKE_STYLE = "DAWNLIKE"
DAWNLIKE_TILE_SIZE = (16, 16)

ORYX_IMAGE_RESOURCE_FOLDER = str(os.curdir + os.sep + "resources" + os.sep + "img" + os.sep + "Oryx_Megapack" + os.sep)
ORYX_STYLE = "DAWNLIKE"
ORYX_TILE_SIZE = (24, 24)

ICON_IMAGE_RESOURCE_FOLDER = str(os.curdir + os.sep + "resources" + os.sep + "img" + os.sep + "GameIcons" + os.sep)

DEFAULT_RESOURCE_STYLE = DAWNLIKE_STYLE

KENNEY_IMAGE_RESOURCE_FOLDER = str(
    os.curdir + os.sep + "resources" + os.sep + "img" + os.sep + "Kenney" + os.sep + "UIPack" + os.sep)
KENNEY_COLOR_BEIGE = "beige"
KENNEY_COLOR_GREY = "grey"
KENNEY_COLOR_BROWN = "brown"
KENNEY_COLOR_BLUE = "blue"

DEFAULT_WIDGET_STYLE = None  # Will be set later
DEFAULT_CONTAINER_STYLE = None  # Will be set later

FONT_FOLDER = str(os.curdir + os.sep + "resources" + os.sep + "font" + os.sep)

# CALL ACTION RESULT
# This is a set of possible result of the call action method (on objects or npc)
PREVENT_MOVEMENT = "action_prevent_movement"
