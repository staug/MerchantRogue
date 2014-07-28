__author__ = 'Tangil'
"""
Contains all data regarding the objects
An object may contain an equipment
An object may contain breakable parts - for crafting purposes
An object may contain a usable part - this creates temporary or permanent boost, such as potions or others.
"""
import random
import Util


class GameObject():

    # Different object types:
    JUNK = "junk"
    CRAFT = "craft"
    JEWEL = "jewel"
    POTION = "potion"
    EQUIPMENT = "equipment"
    BOOK = "book"
    # End object type

    def __init__(self,
                 name,
                 object_type,
                 blocking=False,
                 weight=None,
                 volume=None,
                 regular_value=None,
                 action_when_player=None,
                 equipment=None,
                 usable_part=None,
                 graphical_representation=None,
                 breakable_parts=None,
                 part_of_inventory=None):

        self.name = name
        self.object_type = object_type
        self.blocking = blocking
        self.graphical_representation = graphical_representation
        self.equipment = equipment
        self.breakable_parts = breakable_parts
        self.part_of_inventory = part_of_inventory
        self.usable_part = usable_part

        if weight:
            self.weight = weight
        else:
            self.weight = random.randint(1, 10)
        if volume:
            self.volume = volume
        else:
            self.volume = random.randint(1, 10)
        if regular_value:
            self.regular_value = regular_value
        else:
            self.regular_value = random.randint(1, 100)

        if action_when_player:
            self.action_when_player = action_when_player

        if self.usable_part:
            self.usable_part.owner=self
        if self.equipment:
            self.equipment.owner=self

    def destroy(self):
        #TODO test this part
        if self.equipment:
            self.equipment.unequip()
        if self.usable_part:
            self.usable_part.unuse()
        self.part_of_inventory.remove(self)

    def break_object(self):
        #TODO this function needs to replace the current object in inventory with the content of self.breakable...
        if self.equipment:
            self.equipment.unequip()
        if self.usable_part:
            self.usable_part.unuse()
        self.part_of_inventory.exchange(self, self.breakable_parts)
        pass

    def draw(self):
        if self.graphical_representation:
            self.graphical_representation.draw()

    def __str__(self):
        return self.name


class Equipment():

    # Different equipment types:
    WEAPON = "weapon"
    # End object type

    def __init__(self,
                 equipment_type,
                 owner=None,
                 durability=None,
                 effect=None,
                 body_part=None,
                 race_restriction=None):
        self.equipment_type = equipment_type
        self.durability = durability
        self.effect = effect
        self.body_part = body_part
        self.race_restriction = race_restriction
        self.owner = owner

    def equip(self):
        Util.Event("Equip function not implemented...")
        pass

    def unequip(self):
        Util.Event("Unequip function not implemented...")
        pass


class UsablePart():

    # Different usable types:
    POTION = "potion"
    SPELL = "spell"
    # End object type

    def __init__(self,
                 validity_time=None,
                 owner=None,
                 destroy_after_use=True,
                 permanent_effect=False,
                 effect=None):
        '''

        :param validity_time: The time validity (nb turns). -1 means infinite
        :param owner: The object that owns this characteristic
        :param destroy_after_use: true (default) means that the destroy function will be called after
        :param effect: the effect when the use function is called
        :param permanent_effect: the effect will continue even after the unuse function is called
        :return:
        '''
        self.owner = owner
        self.destroy_after_use = destroy_after_use
        self.effect = effect
        self.validity_time = validity_time
        self.permanent_effect = permanent_effect

    def use(self):
        #TODO
        if self.destroy_after_use:
            self.owner.destroy()
        Util.Event("Use function not implemented...")
        pass

    def unuse(self):
        #TODO
        # plan to use alo the validity: if validity = -1, then
        Util.Event("Unuse function not implemented...")
        pass