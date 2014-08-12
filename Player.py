__author__ = 'Tangil'

import random
import math
import Constants
import Util
import GameData
from Displayable import DisplayableObject


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
            if an_object.displayable_object and an_object.displayable_object.position_on_tile == self.position_on_tile:
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

    def __init__(self, town, name=None, position_on_tile=(0, 0),
                 graphical_representation = None, surface_to_draw=None, surface_memory=None,
                 default_action_list=None, action_when_player=None, action_when_other_npc=None):
        super().__init__(town, movable=True, position_on_tile=position_on_tile,
                         graphical_representation=graphical_representation,
                         surface_to_draw=surface_to_draw, surface_memory=surface_memory)
        if not default_action_list:
            self.default_action_list = [self.get_close_to_player]
        else:
            self.default_action_list = default_action_list
        if not action_when_player:
            self.action_when_player = self.speak_garbage
        else:
            self.action_when_player = action_when_player
        if not action_when_other_npc:
            self.action_when_other_npc = self.do_nothing
        else:
            self.action_when_player = action_when_other_npc
        self.blocking = True

        if not name:
            name = "NPC"+str(id(self))
        self.name=name

    def call_action(self, **kwargs):
        trigger = kwargs.pop("trigger")
        if trigger and isinstance(trigger, NonPlayableCharacter):
            if self.action_when_other_npc:
                return self.action_when_npc(source=self, **kwargs)
        elif self.action_when_player:
            return self.action_when_player(source=self, **kwargs)
        return True

    def take_action(self):
        dx = GameData.player.position_on_tile[0] - self.position_on_tile[0]
        dy = GameData.player.position_on_tile[1] - self.position_on_tile[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance < 2 and isinstance(self.action_when_other_npc, list) and len(self.action_when_player) > 0:
            random.choice(self.action_when_player)(source=self)
        elif distance < 2 and self.action_when_player:
            self.action_when_player(source=self)
        elif len(self.default_action_list) > 0:
            random.choice(self.default_action_list)(source=self)
        else:
            self.wander(source=self)

    def speak_garbage(self, **kwargs):
        Util.Event("Hello player!")
        self.action_when_player = self.do_nothing
        self.default_action_list.remove(self.get_close_to_player)
        return [Constants.PREVENT_MOVEMENT]

    def wander(self, **kwargs):
        self.move(random.randint(-1, 1), random.randint(-1, 1), ignore_message=True)

    def do_nothing(self, **kwargs):
        print("{} was told to do nothing".format(self.name))
        pass

    def get_close_to_player(self, **kwargs):
        #vector from this object to the target, and distance
        dx = GameData.player.position_on_tile[0] - self.position_on_tile[0]
        dy = GameData.player.position_on_tile[1] - self.position_on_tile[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy, ignore_message=True)

    def stay_in_room(self, **kwargs):
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

    def __init__(self, town, position_on_tile=(0, 0),
                 graphical_representation = None, surface_to_draw=None, surface_memory=None):
        super().__init__(town, position_on_tile=position_on_tile, graphical_representation=graphical_representation,
                         surface_to_draw=surface_to_draw, surface_memory=surface_memory,
                         default_action_list=[self.stay_in_room], action_when_player=[self.trade_with_player])
        self.friendliness_setting = random.randint(-10, 10)

class InventoryObject(object):

    QUANTITY_SLOT = 1
    OBJECT_SLOT = 0

    class InventoryFull(Exception):
        def __init__(self, message=None):
            if not message:
                message = "This object cannot store more things"
            super().__init__(self, message)
            self.message = message

    class ObjectNotFound(Exception):
        def __init__(self, message=None):
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
        """
        :return: String representation of the container, mainly for debug purpose
        """
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


class Mercenary(object):

    def __init__(self, name):
        self.name = name
        self.category = random.choice(["Warrior", "Mage", "Paladin", "Thief"])
        self.hp = random.randint(20, 25)
        self.mp = random.randint(15, 20)
        self.attack = random.randint(1, 20)
        self.defense = random.randint(1, 20)