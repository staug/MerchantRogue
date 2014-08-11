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
    def __init__(self, town=None, movable=True, blocking=False, position_on_tile=(0, 0),
                 graphical_representation=None, surface_to_draw=None, surface_memory=None, delayed_register=False):
        self.town = town
        self.position_on_tile = position_on_tile
        self.movable = movable
        self.blocking = blocking

        self.graphical_representation = None
        self.set_graphical_representation(graphical_representation)

        if surface_memory and surface_to_draw:
            self.set_graphical_surface(surface_to_draw, surface_memory)

        if not delayed_register:
            self.register_object(town=town)

    def register_object(self, town=None):
        if town:
            town.tile_map.map[self.position_on_tile].register_object(self)
        elif self.town:
            self.town.tile_map.map[self.position_on_tile].register_object(self)

    def set_graphical_representation(self, graphical_representation):
        if graphical_representation:
            self.graphical_representation = graphical_representation
            self.graphical_representation.owner = self

    def set_graphical_surface(self, surface_to_draw, surface_memory):
        if self.graphical_representation:
            self.graphical_representation.set_surface(surface_to_draw, surface_memory)

    def draw(self):
        if self.graphical_representation:
            self.graphical_representation.draw()

    def move_to(self, new_tile_position, ignore_tile_blocking=False, ignore_movable=False, ignore_message=False):
        if new_tile_position not in self.town.tile_map.map.keys():
            if not ignore_message:
                Util.Event("{} not in tilemap".format(new_tile_position))
            return False
        if not ignore_movable and not self.movable:
            if not ignore_message:
                Util.Event("Tried to move a non movable object".format(self))
            return False
        if not ignore_tile_blocking and self.town.tile_map.map[new_tile_position].blocking:
            if not ignore_message:
                Util.Event("Illegal move to {}".format(new_tile_position))
            return False
        # Test to know if any objects with callbacks are in the new position
        for an_object in self.town.tile_map.map[new_tile_position].object_on_tile:
            if not an_object.call_action():
                Util.Event("The object at {} prevented the move".format(new_tile_position))
                return False

        self.graphical_representation.graphical_move(self.position_on_tile, new_tile_position)
        self.town.tile_map.map[self.position_on_tile].unregister_object(self)
        self.position_on_tile = new_tile_position
        self.town.tile_map.map[self.position_on_tile].register_object(self)
        return True

    def move(self, x_tile_offset, y_tile_offset, ignore_tile_blocking=False,
             ignore_movable=False, ignore_message=False):
        new_tile_position = (
            self.position_on_tile[0] + x_tile_offset,
            self.position_on_tile[1] + y_tile_offset
        )
        return self.move_to(new_tile_position, ignore_tile_blocking=ignore_tile_blocking,
                            ignore_movable=ignore_movable, ignore_message=ignore_message)


class SpriteObject(object):
    """
    A non animated object
    """

    def __init__(self, style, image_folder, image_file, animation_coordinates_in_file, surface_to_draw=None,
                 surface_memory=None):
        if image_file:
            if style == Constants.DAWNLIKE_STYLE:
                self.animation = Util.PygAnimation(
                    [(Constants.DAWNLIKE_IMAGE_RESOURCE_FOLDER + image_folder + os.sep + image_file + ".png",
                      animation_coordinates_in_file, 1.0, Constants.DAWNLIKE_TILE_SIZE, Constants.TILE_SIZE)]
                )
                self.animation.play()
        self.owner = None

        self.surface_to_draw = surface_to_draw
        self.surface_memory = surface_memory

    def graphical_move(self, old_tile_position, new_tile_position):
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

    def __init__(self, style, animation_folder, animation_file, animation_coordinates_in_file, surface_to_draw=None,
                 surface_memory=None):
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

        super().__init__(style, animation_folder, None, None, surface_to_draw=surface_to_draw,
                         surface_memory=surface_memory)
        if style == Constants.DAWNLIKE_STYLE:
            # Dawnlike settings: 16x16, the first image of the animation is in one file called "0"
            self.animation = Util.PygAnimation(
                [(str(Constants.DAWNLIKE_IMAGE_RESOURCE_FOLDER + animation_folder + os.sep + animation_file + "0.png"),
                  animation_coordinates_in_file, 0.2, Constants.DAWNLIKE_TILE_SIZE, Constants.TILE_SIZE),
                 (str(Constants.DAWNLIKE_IMAGE_RESOURCE_FOLDER + animation_folder + os.sep + animation_file + "1.png"),
                  animation_coordinates_in_file, 0.2, Constants.DAWNLIKE_TILE_SIZE, Constants.TILE_SIZE)]
            )
            self.animation.play()
        else:
            raise Exception("Origin type unknown" + style)