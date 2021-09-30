from lux.game_objects import CityTile
import math, sys
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate

DIRECTIONS = Constants.DIRECTIONS
game_state = None

logfile = "agent.log"

open(logfile,"w")

build_location = None
unit_started_to_move = False


def get_nearest_resource(height,width):
        resource_tiles: list[Cell] = []
        for y in range(height):
            for x in range(width):
                cell = game_state.map.get_cell(x, y)
                if cell.has_resource():
                    resource_tiles.append(cell)
        return resource_tiles
    
def check_avalaibility(nearest_city_tile,player):
    #N,S,E,W,NW,SE,SW,NW
    dirs = [(1,0), (0,1), (-1,0), (0,-1),(1,-1), (-1,1), (-1,-1),(1,1)]
    for d in dirs:
        potential_square = game_state.map.get_cell(nearest_city_tile.pos.x+d[0],nearest_city_tile.pos.y+d[1])
        if potential_square.resource == None and potential_square.road == 0 and potential_square.citytile == None:
            return potential_square
    return None
        


def build_city(player,nearest_city_tile,unit):
    global build_location
    last_city_tile = list(player.cities.values())[-1].citytiles[-1]
    # available = True
    # unit.
    available = check_avalaibility(last_city_tile,player)
    build_location = available
    
        
def get_nearest_city_tile(player,unit):
    closest_dist = math.inf
    for k, city in player.cities.items():
        for city_tile in city.citytiles:
            dist = city_tile.pos.distance_to(unit.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_city_tile = city_tile
    return closest_city_tile





def agent(observation, configuration):
    global build_location
    global game_state

    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])
    
    actions = []

    ### AI Code goes down here! ### 
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height


    
    resource_tiles = get_nearest_resource(height,width)

    # we iterate over all our units and do something with them
    for unit in player.units:
        if unit.is_worker() and unit.can_act():
            closest_dist = math.inf
            closest_resource_tile = None
            
            if unit.get_cargo_space_left() > 0 and player.city_tile_count == len(player.units) and build_location == None:
                # if the unit is a worker and we have space in cargo, lets find the nearest resource tile and try to mine it
                for resource_tile in resource_tiles:
                    if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
                    if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
                    dist = resource_tile.pos.distance_to(unit.pos)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_resource_tile = resource_tile
                if closest_resource_tile is not None:
                    actions.append(unit.move(unit.pos.direction_to(closest_resource_tile.pos)))

                with open(logfile,"a") as f:
                        f.write('Nothing to do \n')
            # elif unit.get_cargo_space_left() >= 100 and player.city_tile_count != player.units.count():
            elif unit.get_cargo_space_left()  == 0 and  unit.is_worker() and  player.city_tile_count == len(player.units) and build_location == None: 
                    nearest_city_tile = get_nearest_city_tile(player,unit)
                    build_city(player,nearest_city_tile,unit)
                
            
            elif build_location:
                if unit.pos == build_location.pos and unit.can_act():
                    actions.append(unit.build_city())
                    with open(logfile,"a") as f:
                        f.write(str(build_location.pos)+' Completed Building\n')
                    build_location = None
                    continue
                move_dir = unit.pos.direction_to(build_location.pos)
                actions.append(unit.move(move_dir))

            else:
                # if unit is a worker and there is no cargo space left, and we have cities, lets return to them
                if len(player.cities) > 0:
                    closest_dist = math.inf
                    closest_city_tile = get_nearest_city_tile(player,unit)
                    if closest_city_tile is not None:
                        move_dir = unit.pos.direction_to(closest_city_tile.pos)
                        actions.append(unit.move(move_dir))

    if player.city_tile_count != len(player.units):
            for k, city in player.cities.items():
                for city_tile in city.citytiles:
                    if city_tile.can_act():
                        actions.append(city_tile.build_worker())


            
    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions
