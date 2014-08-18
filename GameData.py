__author__ = 'Tangil'
"""
This is a specific module that gather all shared data across the different modules.
It is mainly used as a repository for the objects that the game manipulates.
"""

# Game Objects
"""
This holds all the first line objects that may be callable in the game. First line objects are objets that are callable.
Any other list holding objects will only use their name.
The key is the object name. The value is the object itself.
"""
game_dict = {}


def register_object(an_object):
    """
    Store an object in the main dictionary. Also store its id in the town if it is relevant.
    :param an_object: the object to be stored, will be indexed with its id attribute
    :return: nothing
    """
    assert hasattr(an_object, "name"), "Object {} has no id attribute"
    if hasattr(an_object, "town") and an_object.town:
        an_object.town.register_thing(an_object)
    else:
        print("no town attribute for " + str(an_object))
    game_dict[an_object.id] = an_object
    return


def object_exist(name):
    """
    Test if an object exists currently
    :param name: the object name to test
    :return: True if the object exists, False otherwise
    """
    if not name in game_dict.keys():
        print("Warning: tried to lookup an object that was not there?")
        return False
    return True


player = None
town_graph = None
current_town = None
time_ticker = None

# Graphical Objects
display = None  # The parent plane
surface_to_draw = None
surface_memory = None
