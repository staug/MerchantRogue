__author__ = 'Tangil'

import random
import Util
import Constants
import pygame
import os
import math
import GameData


class DisplayableObject(object):

    def __init__(self, town=None, movable=True, blocking=False, position_on_tile=(0, 0),
                 graphical_representation = None, surface_to_draw = None, surface_memory = None, delayed_register=False):
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
        self.graphical_representation.graphical_move(self.position_on_tile, new_tile_position)
        self.town.tile_map.map[self.position_on_tile].unregister_object(self)
        self.position_on_tile = new_tile_position
        self.town.tile_map.map[self.position_on_tile].register_object(self)
        self.town.tile_map.map[self.position_on_tile].call_action(player=self)
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
    def __init__(self, movable, animation_folder, animation_file, animation_coordinates_in_file,
                 surface_to_draw=None, surface_memory=None):
        if animation_file:
            self.animation = Util.PygAnimation(
                [(Constants.IMAGE_RESOURCE_FOLDER + animation_folder + os.sep +
                  animation_file + ".png", animation_coordinates_in_file, 1.0)]
            )
        self.movable = movable
        self.owner = None

        self.surface_to_draw = surface_to_draw
        self.surface_memory = surface_memory

    def graphical_move(self, old_tile_position, new_tile_position):
        old_pos_x = old_tile_position[0] * Constants.TILE_SIZE
        old_pos_y = old_tile_position[1] * Constants.TILE_SIZE
        self.surface_to_draw.blit(self.surface_memory, (old_pos_x, old_pos_y),
                                  pygame.Rect((old_pos_x, old_pos_y), (Constants.TILE_SIZE, Constants.TILE_SIZE)))
        new_pos_x = new_tile_position[0] * Constants.TILE_SIZE
        new_pos_y = new_tile_position[1] * Constants.TILE_SIZE
        self.animation.blit(self.surface_to_draw, (new_pos_x, new_pos_y))

    def draw(self):
        image_pos = (self.owner.position_on_tile[0] * Constants.TILE_SIZE, self.owner.position_on_tile[1] * Constants.TILE_SIZE)
        self.animation.blit(self.surface_to_draw, image_pos)

    def set_surface(self, surface_to_draw, surface_memory):
        self.surface_to_draw = surface_to_draw
        self.surface_memory = surface_memory


class AnimatedSpriteObject(SpriteObject):
    """
    An animated object
    """
    def __init__(self, movable, animation_folder, animation_file, animation_coordinates_in_file,
                 surface_to_draw=None, surface_memory=None):
        super().__init__(movable, animation_folder, None, None,
                         surface_to_draw=surface_to_draw, surface_memory=surface_memory)
        self.animation = Util.PygAnimation(
            [(str(Constants.IMAGE_RESOURCE_FOLDER + animation_folder + os.sep + animation_file + "0.png"),
              animation_coordinates_in_file, 0.2),
             (str(Constants.IMAGE_RESOURCE_FOLDER + animation_folder + os.sep + animation_file + "1.png"),
              animation_coordinates_in_file, 0.2)]
        )
        self.animation.play()


class Player(DisplayableObject):

    def __init__(self, town, position_on_tile=(0, 0), graphical_representation = None,
                 surface_to_draw=None, surface_memory=None):
        super().__init__(town, movable=True, position_on_tile=position_on_tile,
                         graphical_representation=graphical_representation,
                         surface_to_draw=surface_to_draw, surface_memory=surface_memory)

        self.wealth = 0

        # TEST
        body = InventoryObject("Own body", slots=5)
        #body.store(GameObject("A Stuff"), 2)
        #body.store(GameObject("Another Stuff"), 3)

        bag = InventoryObject("A bag", slots=2, container_weight=3)
        #bag.store(GameObject("A Stuff"), 5)
        # END TEST
        self.inventory_list = [body, bag]

        m1 = Mercenary("A guy")
        m2 = Mercenary("Another guy")
        m3 = Mercenary("A 3rd guy")
        self.mercenaries = [m1, m2, m3]


    def travel_to(self, other_town):
        self.town = other_town

    def buy(self, money):
        if money > self.wealth:
            raise Exception("Not enough money")
        self.wealth -= money

    def sell(self, money):
        self.wealth += money

    def list_container(self):
        result = ""
        for container in self.inventory_list:
            result += str(container)
        return result

    def store(self, good_quantity, container=None):
        """
        Store the good in the first available container...
        :param good_quantity: a tuple containing the good object and the quantity bought
        :return nothing
        :raise InventoryFull if there is no space left
        """
        quantity = good_quantity[1]
        good = good_quantity[0]
        store = False
        if container:
            if container.can_store(quantity):
                container.store(good, quantity)
                store = True
        else:
            for container in self.inventory_list:
                if not store and container.can_store(quantity):
                    container.store(good, quantity)
                    store = True
        if not store:
            raise InventoryObject.InventoryFull("{} cannot be stored".format(str(good)))

    def hire(self, mercenary):
        self.mercenaries.append(mercenary)

    def fire(self, mercenary):
        self.mercenaries.remove(mercenary)

    def pickup(self):
        game_object = None
        for an_object in self.town.game_object_list:
            if an_object.position_on_tile == self.position_on_tile:
                game_object = an_object
                break
        if not game_object:
            Util.Event("There is nothing there!")
            return
        try:
            self.store((game_object, 1))
            self.town.game_object_list.remove(game_object)
        except InventoryObject.InventoryFull as e:
            Util.Event(e.message)


class NonPlayableCharacter(DisplayableObject):

    def __init__(self, town, position_on_tile=(0, 0),
                 graphical_representation = None, surface_to_draw=None, surface_memory=None,
                 default_action_list=None, action_when_player=None):
        super().__init__(town, movable=True, position_on_tile=position_on_tile,
                         graphical_representation=graphical_representation,
                         surface_to_draw=surface_to_draw, surface_memory=surface_memory)
        if not default_action_list:
            self.default_action_list = [self.get_close_to_player]
        else:
            self.default_action_list = default_action_list
        if not action_when_player:
            self.action_when_player = [self.speak_garbage]
        else:
            self.action_when_player = action_when_player

    def take_action(self):
        dx = GameData.player.position_on_tile[0] - self.position_on_tile[0]
        dy = GameData.player.position_on_tile[1] - self.position_on_tile[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance < 2 and len(self.action_when_player) > 0:
            random.choice(self.action_when_player)()
        elif len(self.default_action_list) > 0:
            random.choice(self.default_action_list)()
        else:
            self.wander()

    def speak_garbage(self):
        Util.Event("Hello player!")
        self.action_when_player.remove(self.speak_garbage)
        self.default_action_list.remove(self.get_close_to_player)

    def wander(self):
        self.move(random.randint(-1, 1), random.randint(-1, 1), ignore_message=True)

    def do_nothing(self):
        pass

    def get_close_to_player(self):
        #vector from this object to the target, and distance
        dx = GameData.player.position_on_tile[0] - self.position_on_tile[0]
        dy = GameData.player.position_on_tile[1] - self.position_on_tile[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy, ignore_message=True)

    def stay_in_room(self):
        old_building = self.town.tile_map.map[self.position_on_tile].room
        old_position = self.position_on_tile
        self.wander()
        if not old_building or self.town.tile_map.map[self.position_on_tile].room != old_building:
            self.move_to(old_position, ignore_message=True)


class TraderNPC(NonPlayableCharacter):

    def trade_with_player(self):
        building = self.town.tile_map.map[self.position_on_tile].room
        message = ""
        if building and building.goods_available:
            message += "Available: {}".format([str(game_object.name) for game_object in building.goods_available])
        if building and building.gold:
            message += "\n Gold available: {}".format(building.gold)
        Util.Event(message)

    def __init__(self, town, position_on_tile=(0,0),
                 graphical_representation = None, surface_to_draw=None, surface_memory=None):
        super().__init__(town, position_on_tile=position_on_tile, graphical_representation=graphical_representation,
                     surface_to_draw=surface_to_draw, surface_memory=surface_memory,
                     default_action_list=[self.stay_in_room], action_when_player=[self.trade_with_player])
        self.friendliness_setting = random.randint(-10, 10)

class InventoryObject(object):

    QUANTITY_SLOT = 1
    OBJECT_SLOT = 0

    class InventoryFull(Exception):
        def __init__(self, message=None, error=None):
            if not message:
                message = "This object cannot store more things"
            super().__init__(self, message)
            self.message = message

    class ObjectNotFound(Exception):
        def __init__(self, message=None, error=None):
            if not message:
                message = "This object is not part of this container"
            super().__init__(self, message)
            self.message = message

    def __init__(self, name, slots=-1, container_weight=0):
        self.name = name
        self.slots = slots
        self.contains = {}
        self.container_weight = container_weight

    def store(self, game_object, quantity):
        if quantity > self.free_slots:
            raise InventoryObject.InventoryFull("Only {} free slots remaining".format(self.free_slots))
        old_qty = 0
        if str(game_object) in self.contains.keys():
            old_qty = self.contains[str(game_object)][InventoryObject.QUANTITY_SLOT]
        self.contains[str(game_object)] = (game_object, old_qty + quantity)

    def remove(self, game_object_name, quantity):
        if game_object_name not in self.contains.keys():
            raise InventoryObject.ObjectNotFound("{} not found".format(game_object_name))
        good_quantity = self.contains[game_object_name]
        if good_quantity[InventoryObject.QUANTITY_SLOT] < quantity:
            raise InventoryObject.ObjectNotFound("{} {} not found".format(str(quantity), game_object_name))
        else:
            self.contains[game_object_name] = (good_quantity[InventoryObject.OBJECT_SLOT],
                                               good_quantity[InventoryObject.QUANTITY_SLOT] - quantity)

    def transfer_to(self, other_inventory_object, keep_in=False):
        try:
            for object_quantity in self.contains.values():
                other_inventory_object.store(object_quantity[InventoryObject.OBJECT_SLOT],
                                             object_quantity[InventoryObject.QUANTITY_SLOT])
                if not keep_in:
                    self.remove(str(object_quantity[InventoryObject.OBJECT_SLOT]),
                                object_quantity[InventoryObject.QUANTITY_SLOT])
        except InventoryObject.InventoryFull:
            raise InventoryObject.InventoryFull("Only {} free slots remaining".format(other_inventory_object.free_slots))

    def can_store(self, quantity):
        if self.free_slots >= quantity:
            return True
        else:
            return False

    def __str__(self):
        '''
        String representation of the container, mainly for debug purpose
        :return:
        '''
        result = "Container {} (Slots: {}- Free: {}, Weight: {}, Carried Weight: {})\nContains:".format(
            self.name, self.slots, self.free_slots, self.container_weight, self.weight
        )
        for good_quantity in self.contains.values():
            result += "\n\t{} {}".format(good_quantity[1], good_quantity[0])
        return result

    @property
    def free_slots(self):
        free = self.slots
        for game_object_quantity in self.contains.values():
            free -= game_object_quantity[1]
        return free

    @property
    def weight(self):
        weight=self.container_weight
        for good_quantity in self.contains.values():
            weight += good_quantity[InventoryObject.QUANTITY_SLOT] * good_quantity[InventoryObject.OBJECT_SLOT].weight
        return weight


class UnlimitedInventory(InventoryObject):

    def store(self, game_object, quantity):
        old_qty = 0
        if str(game_object) in self.contains.keys():
            old_qty = self.contains[str(game_object)][InventoryObject.QUANTITY_SLOT]
        self.contains[str(game_object)] = (game_object, old_qty + quantity)

    def can_store(self, quantity):
        return True

    @property
    def free_slots(self):
        return self.slots


class GameObject(DisplayableObject):

    """
    A Game object can be displayed on screen, picked up in inventory and later removed
    A Game object can also be a trap
    """

    def __init__(self, name, town, position_on_tile=(0, 0),
                 graphical_representation = None, surface_to_draw = None, surface_memory = None, action_when_player=None, delayed_register=False):
        super().__init__(town, movable=False, position_on_tile=position_on_tile, graphical_representation=graphical_representation,surface_to_draw=surface_to_draw, surface_memory = surface_memory, delayed_register=delayed_register)

        self.name = name
        self.weight = random.randint(1, 10)
        self.regular_value = random.randint(1, 100)
        if action_when_player:
            self.action_when_player = action_when_player
        else:
            self.action_when_player = [self.pickup]

    def pickup(self):
        pass

    def __str__(self):
        return self.name


class Mercenary(object):

    def __init__(self, name):
        self.name = name
        self.category = random.choice(["Warrior", "Mage", "Paladin", "Thief"])
        self.hp = random.randint(20, 25)
        self.mp = random.randint(15, 20)
        self.attack = random.randint(1, 20)
        self.defense = random.randint(1, 20)