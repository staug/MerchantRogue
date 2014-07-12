__author__ = 'Tangil'

import planes
import planes.gui
import planes.gui.tmb
import random
import Places
import Player
import pygame
from pygame.locals import *
import const

def bing(*args):
    pass

if __name__ == '__main__':

    # Video output
    pygame.init()
    print("Setting up clock")
    clock = pygame.time.Clock()

    # main screen
    print("Creating surface")
    screen = planes.Display((640, 480))

    num_town = 20
    # Setup world
    town_graph = Places.TownGraph([Places.Town(random.randint(2,5)) for x in range(num_town)])
    town = random.choice(town_graph.towns)
    town.build_tile_map()
    print("Town correctly setup")

    main_image = planes.ImagePlane("Main Image", pygame.Rect((0, 0), (640,480)), image_size=town.tile_map.surface_memory.get_rect().size)
    main_image.image.blit(town.tile_map.surface_memory, (0,0))
    screen.sub(main_image)
    main_image.set_camera((640,480))

    print("Screen fully initialized")

    player = Player.Player(town,
                           graphical_representation=Player.AnimatedSpriteObject(True, "Characters", "Player", (0, 0)),
                           position_on_tile=town.tile_map.default_start_player_position,
                           surface_memory=town.tile_map.surface_memory, surface_to_draw=main_image.image
    )
    main_image.move_camera_tile_center(player.position_on_tile)
    print("Player ok")

    for i in range(2):
        image_coordinate_x = [x*16 for x in range(0, 7)]
        image_coordinate_y = [y*16 for y in (3, 4, 7, 8)]
        coordinates = (random.choice(image_coordinate_x), random.choice(image_coordinate_y))
        npc = Player.TraderNPC(town,
                            position_on_tile=town.tile_map.get_place_in_building(Places.Building.TRADING_POST),
                           graphical_representation=Player.AnimatedSpriteObject(True, "Characters", "Player", coordinates),
                           surface_memory=town.tile_map.surface_memory, surface_to_draw=main_image.image)
        town.npc_list.append(npc)

    print("NPC ok")
    for i in range(25):
        an_object = Player.GameObject("A leftover object", town, position_on_tile=(random.randint(0, town.tile_map.max_x - 1), random.randint(0, town.tile_map.max_y - 1)),
                                      graphical_representation = Player.AnimatedSpriteObject(True, "Objects", "Ground", (48, 16)),
                    surface_to_draw = main_image.image, surface_memory = town.tile_map.surface_memory, delayed_register=True)
        town.game_object_list.append(an_object)
    print("Game object ok")
    print("starting main loop")

    #test2 = planes.gui.tmb.TMBOptionSelector("Destination", ["A", "B"], bing)
    #screen.sub(test2)

    while True:

        player_took_action = False

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                print("got pygame.QUIT, terminating")
                raise SystemExit
            if event.type == const.DISPLAY_EVENT:
                print(event.message)
                event_box = planes.gui.OutlinedText("Event", event.message)
                screen.sub(event_box)
                event_box.rect.top = 100
            if event.type == const.DEBUG_EVENT:
                print(event.message)
            if event.type == KEYDOWN and event.key == K_RIGHT:
                player.move(1, 0)
                player_took_action = True
                main_image.move_camera_tile_center(player.position_on_tile)
            if event.type == KEYDOWN and event.key == K_UP:
                player.move(0, -1)
                player_took_action = True
                main_image.move_camera_tile_center(player.position_on_tile)
            if event.type == KEYDOWN and event.key == K_DOWN:
                player.move(0, 1)
                player_took_action = True
                main_image.move_camera_tile_center(player.position_on_tile)
            if event.type == KEYDOWN and event.key == K_LEFT:
                player.move(-1, 0)
                player_took_action = True
                main_image.move_camera_tile_center(player.position_on_tile)
            if event.type == KEYDOWN and event.key == K_p:
                player.pickup()
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
            for npc in town.npc_list:
                npc.take_action()

        for npc in town.npc_list:
            npc.draw()

        for game_object in town.game_object_list:
            game_object.draw()

        player.draw()

        # test_anim.blit(main_image.image, (pos_x, pos_y))

        screen.process(events)
        screen.update()
        screen.render()


        pygame.display.flip()
        clock.tick(25)