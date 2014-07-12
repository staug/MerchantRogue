__author__ = 'Tangil'

import planes
import planes.gui
import planes.gui.tmb
import random
import Util
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

    npc_list = []
    for i in range(5):
        image_coordinate_x = [x*16 for x in range(0, 7)]
        image_coordinate_y = [y*16 for y in (3, 4, 7, 8)]
        coordinates = (random.choice(image_coordinate_x), random.choice(image_coordinate_y))
        npc = Player.TraderNPC(town,
                            position_on_tile=town.tile_map.get_place_in_building(Places.Building.TRADING_POST),
                           graphical_representation=Player.AnimatedSpriteObject(True, "Characters", "Player", coordinates),
                           surface_memory=town.tile_map.surface_memory, surface_to_draw=main_image.image)
        npc_list.append(npc)

    print("NPC ok")

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
            if event.type == KEYDOWN and event.key == K_RIGHT:
                # main_image.image.blit(tm.surface_memory, (pos_x, pos_y), pygame.Rect((pos_x, pos_y), (16, 16)))
                # pos_x += 16
                player.move(1, 0)
                player_took_action = True
                main_image.move_camera_tile_center(player.position_on_tile)
            if event.type == KEYDOWN and event.key == K_UP:
                # main_image.image.blit(tm.surface_memory, (pos_x, pos_y), pygame.Rect((pos_x, pos_y), (16, 16)))
                # pos_y -= 16
                player.move(0, -1)
                player_took_action = True
                main_image.move_camera_tile_center(player.position_on_tile)
            if event.type == KEYDOWN and event.key == K_DOWN:
                # main_image.image.blit(tm.surface_memory, (pos_x, pos_y), pygame.Rect((pos_x, pos_y), (16, 16)))
                # pos_y += 16
                player.move(0, 1)
                player_took_action = True
                main_image.move_camera_tile_center(player.position_on_tile)
            if event.type == KEYDOWN and event.key == K_LEFT:
                # main_image.image.blit(tm.surface_memory, (pos_x, pos_y), pygame.Rect((pos_x, pos_y), (16, 16)))
                # pos_x -= 16
                player.move(-1, 0)
                player_took_action = True
                main_image.move_camera_tile_center(player.position_on_tile)
            if event.type == KEYDOWN and event.key == K_t:
                main_image.move_camera(y=-1)
            if event.type == KEYDOWN and event.key == K_g:
                main_image.move_camera(y=1)
            if event.type == KEYDOWN and event.key == K_f:
                main_image.move_camera(x=-1)
            if event.type == KEYDOWN and event.key == K_h:
                main_image.move_camera(x=1)

        if player_took_action:
            for npc in npc_list:
                npc.take_action()

        for npc in npc_list:
            npc.draw()
        player.draw()

        # test_anim.blit(main_image.image, (pos_x, pos_y))

        screen.process(events)
        screen.update()
        screen.render()


        pygame.display.flip()
        clock.tick(25)