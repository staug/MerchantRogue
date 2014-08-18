"""
Main function to display and draw the objects and sprites on screen.
The main class is a Displayable object, which holds the basic function (draw, move_to)
A Displayable object holds a sprite, which may be animated or not.
"""
import os

import pygame

import Constants
import Util


__author__ = 'staug'


class DisplayableObject(object):
    def __init__(self, movable=True, blocking=False, position_on_tile=(0, 0), graphical_representation=None):
        self.position_on_tile = position_on_tile
        self.movable = movable
        self.blocking = blocking

        self.graphical_representation = None
        self.set_graphical_representation(graphical_representation)


    def set_graphical_representation(self, graphical_representation):
        if graphical_representation:
            self.graphical_representation = graphical_representation
            self.graphical_representation.owner = self


    def set_graphical_surface(self, surface_to_draw, surface_memory):
        assert self.graphical_representation, "No graphical representation but a set graphical surface requested"
        self.graphical_representation.set_surface(surface_to_draw, surface_memory)


    def draw(self):
        assert self.graphical_representation, "No graphical representation but a draw order requested"
        self.graphical_representation.animation.play()
        self.graphical_representation.draw()


class SpriteObject(object):
    """
    A non animated object
    """

    def __init__(self, style, image_folder, image_file, animation_coordinates_in_file):
        if image_file:
            if style == Constants.DAWNLIKE_STYLE:
                self.animation = Util.PygAnimation(
                    [(Constants.DAWNLIKE_IMAGE_RESOURCE_FOLDER + image_folder + os.sep + image_file + ".png",
                      animation_coordinates_in_file, 1.0, Constants.DAWNLIKE_TILE_SIZE, Constants.TILE_SIZE)]
                )
        self.owner = None
        self.going_right = False
        self.surface_to_draw = None
        self.surface_memory = None

    def graphical_move(self, old_tile_position, new_tile_position):
        if new_tile_position[0] < old_tile_position[0] and self.going_right:
            self.animation.flip(True, False)
            self.going_right = False
        elif new_tile_position[0] > old_tile_position[0] and not self.going_right:
            self.animation.flip(True, False)
            self.going_right = True

        old_pos_x = old_tile_position[0] * Constants.TILE_SIZE[0]
        old_pos_y = old_tile_position[1] * Constants.TILE_SIZE[1]
        self.surface_to_draw.blit(self.surface_memory, (old_pos_x, old_pos_y),
                                  pygame.Rect((old_pos_x, old_pos_y), Constants.TILE_SIZE))
        new_pos_x = new_tile_position[0] * Constants.TILE_SIZE[0]
        new_pos_y = new_tile_position[1] * Constants.TILE_SIZE[1]
        self.animation.blit(self.surface_to_draw, (new_pos_x, new_pos_y))

    def draw(self):
        image_pos = (self.owner.position_on_tile[0] * Constants.TILE_SIZE[0],
                     self.owner.position_on_tile[1] * Constants.TILE_SIZE[1])
        self.animation.blit(self.surface_to_draw, image_pos)

    def set_surface(self, surface_to_draw, surface_memory):
        self.surface_to_draw = surface_to_draw
        self.surface_memory = surface_memory


class AnimatedSpriteObject(SpriteObject):
    """
    An animated object
    """

    def __init__(self, style, animation_folder, animation_file, animation_coordinates_in_file):
        """
        Main constructor
        :param style: either Danwlike or Oryx
        :param animation_folder: the subfolder if any
        :param animation_file: the file itself
        :param animation_coordinates_in_file: the place where the sprite is
        :param surface_to_draw: the main surface (can be redefined later)
        :param surface_memory: the memory surface (can be redefined later)
        :return:
        """

        super().__init__(style, animation_folder, None, None)
        if style == Constants.DAWNLIKE_STYLE:
            # Dawnlike settings: 16x16, the first image of the animation is in one file called "0"
            self.animation = Util.PygAnimation(
                [(str(Constants.DAWNLIKE_IMAGE_RESOURCE_FOLDER + animation_folder + os.sep + animation_file + "0.png"),
                  animation_coordinates_in_file, 0.2, Constants.DAWNLIKE_TILE_SIZE, Constants.TILE_SIZE),
                 (str(Constants.DAWNLIKE_IMAGE_RESOURCE_FOLDER + animation_folder + os.sep + animation_file + "1.png"),
                  animation_coordinates_in_file, 0.2, Constants.DAWNLIKE_TILE_SIZE, Constants.TILE_SIZE)]
            )
        else:
            raise Exception("Origin type unknown" + style)