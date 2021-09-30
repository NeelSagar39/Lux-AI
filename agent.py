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

def get_nearest_resource(height,width):
        resource_tiles: list[Cell] = []
        for y in range(height):
            for x in range(width):
                cell = game_state.map.get_cell(x, y)
                if cell.has_resource():
                    resource_tiles.append(cell)
        return resource_tiles
    
def check_avalaibility(nearest_city_tile,player):
    dirs = [(1,0), (0,1), (-1,0), (0,-1),(1,-1), (-1,1), (-1,-1),(1,1)]
    potential_square = game_state.map.get_cell()
    if (nearest_city_tile[0]+1,nearest_city_tile[1]) not in player.city.citytiles:
        return (nearest_city_tile[0]+1,nearest_city_tile[1])
        


def build_city(player,nearest_city_tile,unit):
    last_city_tile = list(player.cities.values())[-1].citytiles[-1]
    available = check_avalaibility(last_city_tile,player)
    # available = True
    # unit.
    with open(logfile,"a") as f:
        f.write(str(available)+str(nearest_city_tile.pos)+'current\n')
        
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
            
            if unit.get_cargo_space_left() > 0 and player.city_tile_count == len(player.units):
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
            # elif unit.get_cargo_space_left() >= 100 and player.city_tile_count != player.units.count():
                
            elif unit.get_cargo_space_left()  == 0 and  unit.is_worker() and  player.city_tile_count == len(player.units): 
                nearest_city_tile = get_nearest_city_tile(player,unit)
                build_city(player,nearest_city_tile,unit)

            else:
                # if unit is a worker and there is no cargo space left, and we have cities, lets return to them
                if len(player.cities) > 0:
                    closest_dist = math.inf
                    closest_city_tile = get_nearest_city_tile(player,unit)
                    if closest_city_tile is not None:
                        move_dir = unit.pos.direction_to(closest_city_tile.pos)
                        actions.append(unit.move(move_dir))
            
    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions
