from Displayable import DisplayableObject
from Displayable import AnimatedSpriteObject
from GameObject import GameObject, Door

__author__ = 'Tangil'

import planes
import planes.gui
import planes.gui.tmb
import random
import Places
import Player
import pygame
import Util
from pygame.locals import *
import Constants
import GameData
import GuiElements

def bing(*args):
    pass

class Game():
    """
    Sets the main non graphical objects of a game: the town graph, the current town, the player, the npc, the objects
    Note that ideally only this class manipulates the objects from GameData
    """

    def __init__(self):
        pass

    @classmethod
    def start_new_game(cls, number_town):
        Util.DebugEvent("Building new world")
        GameData.town_graph = Places.TownGraph([Places.Town(random.randint(2,7)) for x in range(number_town)])

        Util.DebugEvent("Choosing the initial town")
        GameData.current_town = random.choice(GameData.town_graph.towns)
        GameData.current_town.build_tile_map()

        Util.DebugEvent("Setting up player")
        GameData.player = Player.Player(GameData.current_town,
                                        graphical_representation=AnimatedSpriteObject(Constants.DAWNLIKE_STYLE,
                                                                                      "Characters", "Player", (0, 0)),
                           position_on_tile=GameData.current_town.tile_map.default_start_player_position,)

        Util.DebugEvent("Setting up objects in the towns...")
        for town in GameData.town_graph.towns:
            for i in range(5):
                image_coordinate_x = [x*16 for x in range(0, 7)]
                image_coordinate_y = [y*16 for y in (3, 4, 7, 8)]
                coordinates = (random.choice(image_coordinate_x), random.choice(image_coordinate_y))
                # npc = Player.TraderNPC(town,
                #                        position_on_tile=town.tile_map.get_place_in_building(Places.Building.TRADING_POST),
                #                        graphical_representation=Player.AnimatedSpriteObject(True, "Characters", "Player", coordinates))
                npc = Player.NonPlayableCharacter(town,
                                       position_on_tile=(i * 1, i * 2),
                                       graphical_representation=AnimatedSpriteObject(Constants.DAWNLIKE_STYLE,
                                                                                     "Characters", "Player",
                                                                                     coordinates))

                town.npc_list.append(npc)

            for i in range(25):
                """
                 name,
                 object_type,
                 weight=None,
                 volume=None,
                 regular_value=None,
                 action_when_player=None,
                 equipment=None,
                 usable_part=None,
                 breakable_parts=None,
                 part_of_inventory=None,
                 displayable_object=None):
                """

                an_object = GameObject("A leftover object",
                                       GameObject.JUNK,
                                       weight=random.randint(1, 10),
                                       volume=random.randint(1, 5),
                                       regular_value=random.randint(2, 10),
                                       displayable_object=DisplayableObject(town=town,
                                                                            movable=False,
                                                                            blocking=False,
                                                                            position_on_tile=(
                                                                            random.randint(0, town.tile_map.max_x - 1),
                                                                            random.randint(0, town.tile_map.max_y - 1)),
                                                                            graphical_representation=AnimatedSpriteObject(
                                                                                Constants.DAWNLIKE_STYLE, "Objects",
                                                                                "Ground", (16, 48)),
                                                                            delayed_register=True))
                town.register_object(an_object)
                # a door is an open object
            for room in town.tile_map.rooms:
                for door in room.doors:
                    town.register_object(Door(town, door[1], door[0], closed=True, locked=False))

        Util.DebugEvent("Setting up objects in the other places (To be done later)...")

    @classmethod
    def get_current_place_original_image(cls):
        return GameData.current_town.tile_map.surface_memory

    @classmethod
    def assign_surface_to_displayable_objects(cls, town, surface_to_draw, surface_memory):
        GameData.player.graphical_representation.set_surface(surface_to_draw, surface_memory)
        for a_town in GameData.town_graph.towns:
            if a_town.name == town.name:
                for npc in a_town.npc_list:
                    npc.graphical_representation.set_surface(surface_to_draw, surface_memory)
                for an_object in a_town.game_object_list:
                    an_object.displayable_object.graphical_representation.set_surface(surface_to_draw, surface_memory)

    @classmethod
    def save_game(cls, file_name):
        # TODO
        """
        Save the GameData objects
        :param file_name: where to store the data
        :return: none
        """
        pass

    @classmethod
    def load_game(cls, file_name):
        # TODO
        """
        Load the GameData objects
        :param file_name: where to load the data
        :return: none
        """
        pass

def test(*args, **kwargs):
    print("Dummy : args={} kwargs={}".format(args, kwargs))

if __name__ == '__main__':

    # INITIALIZATION ....
    # Step 1 - Video Output init
    pygame.init()
    print("Setting up clock")
    clock = pygame.time.Clock()

    # Step 2 - Main Game Screen
    print("Creating surface")
    screen = planes.Display(Constants.GAME_WINDOW_SIZE)
    GameData.display = screen
    Game.start_new_game(20)

    # Step 3 - Finish the graphical init for this town.
    main_image = GuiElements.ImagePlane("Main Image", pygame.Rect((0, 0), Constants.PLACE_WINDOW_SIZE), Constants.TILE_SIZE,
                                   image_size=GameData.current_town.tile_map.surface_memory.get_rect().size)
    main_image.image.blit(GameData.current_town.tile_map.surface_memory, (0, 0))
    screen.sub(main_image)
    main_image.set_camera(Constants.PLACE_WINDOW_SIZE)
    main_image.move_camera_tile_center(GameData.player.position_on_tile)
    main_image.draggable = False
    main_image.grab = True
    Game.assign_surface_to_displayable_objects(GameData.current_town,
                                                       main_image.image,
                                                       GameData.current_town.tile_map.surface_memory)

    # END INITIALIZATION
    print("All objects init done - starting main loop")

    #pygame.mouse.set_cursor(*pygame.cursors.diamond)

    #screen.sub(GuiElements.KenneyPopupLabelCancel("This is a very very long message.\nI test wrapper.\nAgain a very very long sentecne that never ends\nShort.", style=GuiElements.KENNEY_CONTAINER_STYLE_INCLUDED))
    #screen.sub(GuiElements.KenneyGetStringDialog("Enter your very big name", test, style=GuiElements.KENNEY_CONTAINER_STYLE_INCLUDED))
    #screen.sub(planes.gui.OptionSelector("test", ["test1", "test2"], test))
    screen.sub(GuiElements.KenneyOptionButton(use_image=True, width=5, height=5))
    screen.sub(GuiElements.KenneyWidgetIconButton(test, Constants.ICON_IMAGE_RESOURCE_FOLDER+"help_16x16.png", pos=(200,200)))
    while True:

        player_took_action = False

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                print("got pygame.QUIT, terminating")
                raise SystemExit
            if event.type == Constants.DISPLAY_EVENT:
                print(event.message)
                event_box = GuiElements.KenneyPopupLabelCancel(event.message)
                screen.sub(event_box)
                event_box.rect.top = 100
                event_box.rect.centerx=screen.rect.centerx
            if event.type == Constants.DEBUG_EVENT:
                print(event.message)
            if event.type == KEYDOWN:  #TODO: make sure no extra text box is active?
                if event.type == KEYDOWN and event.key == K_RIGHT:
                    GameData.player.move(1, 0)
                    player_took_action = True
                    main_image.move_camera_tile_center(GameData.player.position_on_tile)
                if event.type == KEYDOWN and event.key == K_UP:
                    GameData.player.move(0, -1)
                    player_took_action = True
                    main_image.move_camera_tile_center(GameData.player.position_on_tile)
                if event.type == KEYDOWN and event.key == K_DOWN:
                    GameData.player.move(0, 1)
                    player_took_action = True
                    main_image.move_camera_tile_center(GameData.player.position_on_tile)
                if event.type == KEYDOWN and event.key == K_LEFT:
                    GameData.player.move(-1, 0)
                    player_took_action = True
                    main_image.move_camera_tile_center(GameData.player.position_on_tile)
                if event.type == KEYDOWN and event.key == K_p:
                    GameData.player.pickup()
                    player_took_action = True
                if event.type == KEYDOWN and event.key == K_i:
                    Util.Event(GameData.player.list_container())
                    player_took_action = True
                if event.type == KEYDOWN and event.key == K_t:
                    main_image.move_camera(y=-1)
                if event.type == KEYDOWN and event.key == K_g:
                    main_image.move_camera(y=1)
                if event.type == KEYDOWN and event.key == K_f:
                    main_image.move_camera(x=-1)
                if event.type == KEYDOWN and event.key == K_h:
                    main_image.move_camera(x=1)

        if player_took_action:
            for npc in GameData.current_town.npc_list:
                npc.take_action()

        for npc in GameData.current_town.npc_list:
            npc.draw()

        for game_object in GameData.current_town.game_object_list:
            game_object.draw()

        GameData.player.draw()

        # test_anim.blit(main_image.image, (pos_x, pos_y))

        screen.process(events)
        screen.update()
        screen.render()


        pygame.display.flip()
        clock.tick(25)