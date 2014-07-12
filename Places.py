__author__ = 'Tangil'
"""
Town, places and other map functions
# TODO: Optimize the walls: some walls show up as regular floor.
"""

import random
import Util
import Player
import pygame


class Building(object):

    UNKNOWN = "unknown"
    GATE = "gate"
    TRADING_POST = "trading_post"
    BANK = "bank"
    TAVERN = "tavern"
    MERCENARY_GUILD = "mercenary_guild"
    BLACKSMITH = "blacksmith"
    STABLES = "stables"
    TOWNHOUSE = "townhouse"

    def __init__(self, town):
        self.decoration_list = {}
        self.town = town
        self.name = Building.UNKNOWN

    def action_pane(self):
        pass


class TradingPost(Building):

    def __init__(self, town):
        super().__init__(town)
        self.name = Building.TRADING_POST

        self.gold = random.randint(1, 200)
        self.goods_available = [Player.GameObject(Util.MName().new(), town, delayed_register=True) for x in range(random.randint(1, 5))]

        self.decoration_list = {
            "1x1": [("Decor", True, (0, 64)), ("Decor", True, (16, 64)), ("Decor", True, (32, 64)),
                    ("Decor", True, (0, 112)), ("Decor", True, (16, 112), (16, 128)), ("Decor", True, (32, 112))],
            "1x3": [("Decor", True, (0, 160))]
        }

    def action_pane(self):
        pass


class Town(object):
    """
    A Town is the main place of the game. A town hosts buildings, hosts NPCs, hosts gameobjects.
    """

    def __init__(self, building_number, make_map=False, render_map=False):
        self.name = Util.MName().new()
        self.npc_list = []
        self.game_object_list = []
        self.available_paths = []
        #self.buildings = {"Gate":Gate(self), "Title":Title(self), "Trading Post":TradingPost(self)}
        self.buildings = [TradingPost(self), TradingPost(self)]
        size = (50, 50)
        if 4 < building_number <= 6:
            size = (65, 65)
        elif 6 < building_number:
            size = (80, 80)
        self.tile_map = TownTileMap(self, size, make_map=make_map, render_map=render_map)
        self.player_position=(1, 1)

        # TODO: Add some random objects in there...

    def __str__(self):
        return self.name

    def add_path(self, path):
        self.available_paths.append(path)

    def build_tile_map(self):
        size = (50, 50)
        if 4 < len(self.buildings) <= 6:
            size = (65, 65)
        elif 6 < len(self.buildings):
            size = (80, 80)
        self.tile_map = TownTileMap(self, size, make_map=True, render_map=True)


class Path(object):
    """ A Path links two towns. Note that due to Geography, path from A to B may be different from B to A...
    """
    def __init__(self, origin, destination, days):
        self.origin_town = origin
        self.destination_town = destination
        self.days = days

    def __str__(self):
        return "to {} in {} days.".format(self.destination_town, str(self.days))


class TownGraph(object):

    def __init__(self, towns):

        self.towns = towns
        if len(towns) <= 3:
            num_paths = random.randint(len(towns) - 1, (len(towns) * (len(towns) - 1)) / 2)
        else:
            num_paths = random.randint(len(towns) - 1, len(towns) * 2)

        # internal purpose...
        self._edges = []
        self._edge_set = set()
        self.build_graph(num_paths)

        for edge in self._edges:
            edge[0].add_path(Path(edge[0], edge[1], random.randint(1, 10)))
            edge[1].add_path(Path(edge[1], edge[0], random.randint(1, 10)))

    def build_graph(self, num_paths):
        # Building algorithm process using random walk from https://gist.github.com/bwbaugh/4602818
        # Create two partitions, source and target. Initially store all nodes in S.
        source, target = set(self.towns), set()

        # Pick a random node, and mark it as visited and the current node.
        current_node = random.sample(source, 1).pop()
        source.remove(current_node)
        target.add(current_node)
        # Create a random connected graph.
        while source:
            # Randomly pick the next node from the neighbors of the current node.
            # As we are generating a connected graph, we assume a complete graph.
            neighbor_node = random.sample(self.towns, 1).pop()
            # If the new node hasn't been visited, add the edge from current to new.
            if neighbor_node not in target:
                edge = (current_node, neighbor_node)
                self.add_edge(edge)
                source.remove(neighbor_node)
                target.add(neighbor_node)
            # Set the new node as the current node.
            current_node = neighbor_node

        # Add random edges until the number of desired edges is reached.
        self.add_random_edges(num_paths)

    def add_edge(self, edge):
        """Add the edge if the graph type allows it."""
        if edge not in self._edge_set:
            self._edges.append(edge)
            self._edge_set.add(edge)
            self._edge_set.add(edge[::-1])  # add other direction to set.
            return True
        return False

    def make_random_edge(self):
        """Generate a random edge between any two nodes in the graph."""
        random_edge = tuple(random.sample(self.towns, 2))
        return random_edge

    def add_random_edges(self, total_edges):
        """Add random edges until the number of desired edges is reached."""
        while len(self._edges) < total_edges:
            self.add_edge(self.make_random_edge())

    def __str__(self):
        result = "Number of towns: {}\n".format(len(self.towns))
        for town in self.towns:
            result += "Town: {}\n".format(town)
            for path in town.available_paths:
                result += "{}\n".format(str(path))
            result += "\n"
        return result


def test_message(**kwargs):
    print("Test 1")
    Util.Event("Wowwww")
    print("Test2")


def door_closed(**kwargs):
    if kwargs["tile"].characteristics["closed"] == "true":
        Util.Event("This door is closed")
    else:
        Util.Event("This door is open")

    kwargs["tile"].characteristics["closed"] = "false"
    door_open_source_file = pygame.image.load('./resources/img/Objects/Door1.png').convert_alpha()
    x = kwargs["tile"].position[0]
    y = kwargs["tile"].position[1]

    if kwargs["tile"].characteristics["orientation"] == "horizontal":
        kwargs["player"].graphical_representation.surface_memory.blit(door_open_source_file.subsurface(pygame.Rect((0,0), (16,16))),
                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
        kwargs["player"].graphical_representation.surface_to_draw.blit(door_open_source_file.subsurface(pygame.Rect((0,0), (16,16))),
                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
    else:
        kwargs["player"].graphical_representation.surface_memory.blit(door_open_source_file.subsurface(pygame.Rect((16,0), (16,16))),
                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
        kwargs["player"].graphical_representation.surface_to_draw.blit(door_open_source_file.subsurface(pygame.Rect((16,0), (16,16))),
                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))

    Util.Event("This door is now open")


class Tile(object):

    UNKNOWN = "unknown"
    FLOOR = "floor"
    WALL = "wall"
    PATH = "path"
    GRASS = "grass"
    DIRT = "dirt"
    WATER = "water"
    ROCK = "rock"
    DOOR = "door"

    TILE_SIZE = 16

    def __init__(self, position, floor_type, tile_map_owner,
                 specific_action_callback=None, specific_action_around_callback=None, decoration_type=None):
        self.floor_type = floor_type
        self.specific_action_callback = specific_action_callback
        self.specific_action_around_callback = specific_action_around_callback
        self.decoration_type = decoration_type
        self.room = None
        self.characteristics = {}
        self.position = position
        self.tile_map_owner = tile_map_owner
        self.object_on_tile = []
        self.decoration_blocking = False

    def call_action(self, **kwargs):
        if self.specific_action_callback:
            self.specific_action_callback(tile=self, **kwargs)

    def set_door(self, horizontal=True):
        self.floor_type = Tile.DOOR
        self.decoration_type = Tile.DOOR
        if horizontal:
            self.characteristics = {"orientation": "horizontal", "closed": "true"}
        else:
            self.characteristics = {"orientation": "vertical", "closed": "true"}
        self.specific_action_callback = door_closed

    def register_object(self, an_object):
        self.object_on_tile.append(an_object)

    def unregister_object(self, an_object):
        self.object_on_tile.remove(an_object)


    @property
    def blocking(self):
        return self.floor_type in (Tile.WATER, Tile.WALL, Tile.ROCK) \
               or len(self.object_on_tile) or self.decoration_blocking


class TileMap(object):

    def __init__(self, size, make_map=False, render_map=False):
        self.max_x = size[0]
        self.max_y = size[1]
        self.map = {}
        self.surface_memory = None

        for x in range(self.max_x):
            for y in range(self.max_y):
                self.map[(x, y)] = Tile((x, y), Tile.UNKNOWN, self)


        if make_map:
            self.make_map()
        if render_map:
            self.render()

    def make_map(self):
        pass

    def render(self):
        pass

    def compute_tile_weight(self, x, y, terrain_type):
        count = 0
        if y - 1 >= 0 and self.map[(x, y - 1)].floor_type == terrain_type:
            count += 1
        if x + 1 < self.max_x and self.map[(x + 1, y)].floor_type == terrain_type:
            count += 2
        if y + 1 < self.max_y and self.map[(x, y + 1)].floor_type == terrain_type:
            count += 4
        if x - 1 >= 0 and self.map[(x - 1, y)].floor_type == terrain_type:
            count += 8
        return count


class TownTileMap(TileMap):

    def __init__(self, town, size, make_map=False, render_map=False):
        super().__init__(size, make_map=False, render_map=False)

        self.town = town
        self.surface_memory = None
        self.rooms = []
        self.default_start_player_position = (0, 0)

        if make_map or render_map:
            self.make_map()
        if render_map:
            self.render()

    def get_place_in_building(self, building_name):
        default = (0, 0)
        for room in self.rooms:
            if room.building.name == building_name:
                for trials in range (100):
                    place = random.choice(room.places)
                    if self.map[place].floor_type == Tile.FLOOR and not self.map[place].blocking:
                        return place
                return default
        print("Warning: room type not found!!")
        return default

    def make_map(self):

        def prepare_ground():
            # Reset all!
            for x in range(self.max_x):
                for y in range(self.max_y):
                    self.map[(x, y)] = Tile((x, y), Tile.UNKNOWN, self)

            # First: prepare the land with Dirt and Grass
            # Use the IslandMaze algo... http://www.evilscience.co.uk/?p=53

            def check_cell(x_val, y_val):
                if 0 <= x_val < self.max_x and 0 <= y_val < self.max_y:
                    if self.map[(x_val, y_val)].floor_type == Tile.GRASS:
                        return True
                return False

            def examine_neighbours(x_val, y_val):
                count = 0
                for var_x in (-1, 0, 1):
                    for var_y in (-1, 0, 1):
                        if check_cell(x_val + var_x, y_val + var_y):
                            count += 1
                return count

            for x in range(self.max_x):
                for y in range(self.max_y):
                    if random.randint(0, 100) < 55:
                        self.map[(x, y)].floor_type = Tile.GRASS
                    else:
                        self.map[(x, y)].floor_type = Tile.DIRT

            # Pick random cells
            for i in range(4000):
                random_x = random.randint(0, self.max_x - 1)
                random_y = random.randint(0, self.max_y - 1)
                if examine_neighbours(random_x, random_y) > 4:
                    self.map[(random_x, random_y)].floor_type = Tile.GRASS
                else:
                    self.map[(random_x, random_y)].floor_type = Tile.DIRT

        def add_shape(center_x, center_y, terrain_type):
            x = center_x
            y = center_y
            for an_iteration in range(100):
                if random.randint(1, 4) == 1 and x-1 >= 0:
                    x -= 1
                    self.map[(x, y)].floor_type = terrain_type
                if random.randint(1, 4) == 1 and x+1 < self.max_x:
                    x += 1
                    self.map[(x, y)].floor_type = terrain_type
                if random.randint(1, 4) == 1 and y-1 >= 0:
                    y -= 1
                    self.map[(x, y)].floor_type = terrain_type
                if random.randint(1, 4) == 1 and y+1 < self.max_y:
                    y += 1
                    self.map[(x, y)].floor_type = terrain_type

        class Room(object):

            def __init__(self, width, height, top_x, top_y, building):
                self.places = []
                self.doors = []
                self.building = building
                for x_coord in range(top_x, width + top_x):
                    for y_coord in range(top_y, height + top_y):
                        self.places.append((x_coord, y_coord))
                additions = random.randint(1, 4)
                for i in range(additions):
                    # Add an extra room: pick a coordinate, and build from that
                    origin = random.choice(self.places)
                    addition_width = max(width + random.randint(-3, 0), 3)
                    addition_height = max(height + random.randint(-3, 0), 3)
                    for x_coord in range(origin[0], addition_width + origin[0]):
                        for y_coord in range(origin[1], addition_height + origin[1]):
                            self.places.append((x_coord, y_coord))

            def can_place(self, tile_map):
                # Step 1: make sure the ground is not blocked
                for place in self.places:
                    if place not in tile_map.keys() or tile_map[place].blocking:
                        return False
                # Step 2: leave a two block path around the building
                for place in self.places:
                    (x, y) = place
                    for x_var in (-2, -1, 0, 1, 2):
                        for y_var in (-2, -1, 0, 1, 2):
                            test_place = (x + x_var, y + y_var)
                            if test_place not in self.places and (test_place not in tile_map.keys()
                                                                  or tile_map[test_place].blocking):
                                return False
                return True

            def compute_tile_weight(self, x, y, terrain_type_list, map, max_x, max_y):
                count = 0
                if y - 1 >= 0 and map[(x, y - 1)].floor_type in terrain_type_list:
                    count += 1
                if x + 1 < max_x and map[(x + 1, y)].floor_type in terrain_type_list:
                    count += 2
                if y + 1 < max_y and map[(x, y + 1)].floor_type in terrain_type_list:
                    count += 4
                if x - 1 >= 0 and map[(x - 1, y)].floor_type in terrain_type_list:
                    count += 8
                return count

            def carve(self, tile_map, max_x, max_y):
                for place in self.places:
                    tile_map[place].floor_type = Tile.FLOOR
                    tile_map[place].room = self.building
                for place in self.places:
                    if self.compute_tile_weight(place[0], place[1], (Tile.FLOOR, Tile.WALL),
                                                tile_map, max_x, max_y) != 15:
                        tile_map[place].floor_type = Tile.WALL

            def place_door(self, tile_map, max_x, max_y):
                #nb_doors = random.randint(1, 3)
                nb_doors = 1
                nb_placed = 0
                while nb_placed < nb_doors:
                    place = random.choice(self.places)
                    weight = self.compute_tile_weight(place[0], place[1],
                                                (Tile.FLOOR, Tile.WALL), tile_map, max_x, max_y)
                    if weight in (7, 11, 14, 13):
                        if weight in (7, 13):
                            tile_map[place].set_door(horizontal=False)
                        else:
                            tile_map[place].set_door(horizontal=True)
                        self.doors.append(place)
                        nb_placed += 1

            def add_deco(self, tile_map, max_x, max_y):
                for i in range(10):
                    place = random.choice(self.places)
                    weight = self.compute_tile_weight(place[0], place[1], (Tile.FLOOR), tile_map, max_x, max_y)
                    if tile_map[place].floor_type == Tile.FLOOR and not tile_map[place].decoration_type and weight == 15:
                        tile_map[place].decoration_type = random.choice(self.building.decoration_list["1x1"])
                        if tile_map[place].decoration_type[1]:
                            tile_map[place].decoration_blocking = True

        need_rebuild = True

        while need_rebuild:

            # Main process - Ground
            print("Generating ground")
            prepare_ground()
            # Main process - Lake
            print("Generating lake and rocks")
            for k in range(random.randint(1, 3)):
                add_shape(random.randint(0, self.max_x - 1), random.randint(0, self.max_y - 1), Tile.WATER)
                add_shape(random.randint(0, self.max_x - 1), random.randint(0, self.max_y - 1), Tile.ROCK)
            # Main process - Room
            room_placed = []
            trials = 0
            print("Placing rooms")
            while len(room_placed) < len(self.town.buildings) and trials < 100:
                a_room = Room(10 + random.randint(-3, 1),
                              10 + random.randint(-3, 1),
                              random.randint(self.max_x // 5, self.max_x - self.max_x // 5),
                              random.randint(self.max_y // 5, self.max_y - self.max_y // 5),
                              self.town.buildings[len(room_placed)])
                if a_room.can_place(self.map):
                    a_room.carve(self.map, self.max_x, self.max_y)
                    a_room.place_door(self.map, self.max_x, self.max_y)
                    room_placed.append(a_room)
                trials += 1

            if trials >= 100:
                print("Unable to place town in the allocated time - Regenerating")
            else:
                # Successfully placed all the rooms
                need_rebuild = False
                print("Successfully built after {} trials".format(trials))
                for room in room_placed:
                    door1 = room.doors[0]
                    door2 = random.choice(room_placed).doors[0]
                    while door1[0] == door2[0] and door1[1] == door2[1]:
                        door2 = random.choice(room_placed).doors[0]
                    astar = Util.AStar(Util.SQ_MapHandler(self.map, self.max_x, self.max_y))
                    p = astar.findPath(Util.SQ_Location(door1[0], door1[1]), Util.SQ_Location(door2[0], door2[1]))

                    if not p:
                        # impossible to connect the room: reject and restart from scratch
                        print("One path not made... Regenerating".format(trials))
                        need_rebuild = True
                    else:
                        possible_starts = []
                        for n in p.nodes:
                            if self.map[(n.location.x, n.location.y)].floor_type not in (
                                    Tile.FLOOR, Tile.DOOR, Tile.PATH
                            ):
                                self.map[(n.location.x, n.location.y)].floor_type = Tile.PATH
                                possible_starts.append((n.location.x, n.location.y))
                        if len(possible_starts) > 0:
                            self.default_start_player_position = random.choice(possible_starts)


            # finish building it - Now redecorating
            for room in room_placed:
                room.add_deco(self.map, self.max_x, self.max_y)
            # and adding the room to the official list of room
            for room in room_placed:
                self.rooms.append(room)

    def render(self):

        def build_floor_tile_array(floor_source_file, origin_x, origin_y):
            return [
                floor_source_file.subsurface(pygame.Rect((origin_x + 5 * 16, origin_y + 0 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 3 * 16, origin_y + 2 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 4 * 16, origin_y + 1 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 0 * 16, origin_y + 2 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 3 * 16, origin_y + 0 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 3 * 16, origin_y + 1 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 0 * 16, origin_y + 0 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 0 * 16, origin_y + 1 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 6 * 16, origin_y + 1 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 2 * 16, origin_y + 2 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 5 * 16, origin_y + 1 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 1 * 16, origin_y + 2 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 2 * 16, origin_y + 0 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 2 * 16, origin_y + 1 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 1 * 16, origin_y + 0 * 16), (16, 16))),
                floor_source_file.subsurface(pygame.Rect((origin_x + 1 * 16, origin_y + 1 * 16), (16, 16)))
            ]

        def build_wall_tile_array(wall_source_file, origin_x, origin_y):
            return [
                wall_source_file.subsurface(pygame.Rect((origin_x + 3 * 16, origin_y + 0 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 1 * 16, origin_y + 1 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 1 * 16, origin_y + 0 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 0 * 16, origin_y + 2 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 0 * 16, origin_y + 1 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 0 * 16, origin_y + 1 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 0 * 16, origin_y + 0 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 3 * 16, origin_y + 1 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 1 * 16, origin_y + 0 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 2 * 16, origin_y + 2 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 1 * 16, origin_y + 0 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 4 * 16, origin_y + 2 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 2 * 16, origin_y + 0 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 5 * 16, origin_y + 1 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 4 * 16, origin_y + 1 * 16), (16, 16))),
                wall_source_file.subsurface(pygame.Rect((origin_x + 4 * 16, origin_y + 2 * 16), (16, 16))),
            ]

        if not self.surface_memory:

            self.surface_memory = pygame.Surface((self.max_x * Tile.TILE_SIZE, self.max_y * Tile.TILE_SIZE))

            wall_source_file = pygame.image.load('./resources/img/Objects/Wall.png').convert_alpha()
            floor_source_file = pygame.image.load('./resources/img/Objects/Floor.png').convert_alpha()
            door_closed_source_file = pygame.image.load('./resources/img/Objects/Door0.png').convert_alpha()
            door_open_source_file = pygame.image.load('./resources/img/Objects/Door0.png').convert_alpha()

            dirt_image = build_floor_tile_array(floor_source_file, 0, 288)
            floor_image = build_floor_tile_array(floor_source_file, 112, 288)
            grass_image = build_floor_tile_array(floor_source_file, 112, 96)
            water_image = build_floor_tile_array(floor_source_file, 224, 288)
            rock_image = build_floor_tile_array(floor_source_file, 224, 96)
            path_image = build_floor_tile_array(floor_source_file, 0, 96)

            wall_image = build_wall_tile_array(wall_source_file, 112, 48)

            for x in range(self.max_x):
                for y in range(self.max_y):
                    if self.map[(x, y)].floor_type == Tile.GRASS:
                        self.surface_memory.blit(grass_image[self.compute_tile_weight(x, y, Tile.GRASS)],
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                    elif self.map[(x, y)].floor_type == Tile.WATER:
                        self.surface_memory.blit(water_image[self.compute_tile_weight(x, y, Tile.WATER)],
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                    elif self.map[(x, y)].floor_type == Tile.ROCK:
                        self.surface_memory.blit(rock_image[self.compute_tile_weight(x, y, Tile.ROCK)],
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                    elif self.map[(x, y)].floor_type == Tile.WALL:
                        self.surface_memory.blit(wall_image[self.compute_tile_weight(x, y, Tile.WALL)],
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                    elif self.map[(x, y)].floor_type == Tile.PATH:
                        self.surface_memory.blit(path_image[self.compute_tile_weight(x, y, Tile.PATH)],
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                    elif self.map[(x, y)].floor_type == Tile.DIRT:
                        self.surface_memory.blit(dirt_image[self.compute_tile_weight(x, y, Tile.DIRT)],
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                    elif self.map[(x, y)].floor_type == Tile.FLOOR:
                        self.surface_memory.blit(floor_image[self.compute_tile_weight(x, y, Tile.FLOOR)],
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                    elif self.map[(x, y)].floor_type == Tile.DOOR:
                        # for a door we do the regular floor, and decorate later
                        self.surface_memory.blit(floor_image[self.compute_tile_weight(x, y, Tile.FLOOR)],
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))

                    # Now add the decoration...
                    if self.map[(x, y)].decoration_type:
                        if self.map[(x, y)].decoration_type == Tile.DOOR:
                            if self.map[(x, y)].characteristics["orientation"] == "horizontal":
                                self.surface_memory.blit(door_closed_source_file.subsurface(pygame.Rect((0,0), (16,16))),
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                            else:
                                self.surface_memory.blit(door_closed_source_file.subsurface(pygame.Rect((16,0), (16,16))),
                                                 (x * Tile.TILE_SIZE, y * Tile.TILE_SIZE))
                        else:
                            Player.DisplayableObject(self.town, movable=False, position_on_tile=(x,y),
                                                     graphical_representation=Player.AnimatedSpriteObject(False, "Objects", self.map[(x, y)].decoration_type[0], self.map[(x, y)].decoration_type[2]),
                                                     surface_to_draw=self.surface_memory, surface_memory=self.surface_memory).draw()
