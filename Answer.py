import sys
import math

# Deliver more amadeusium to hq (left side of the map) than your opponent. Use radars to find amadeusium but beware of traps!

# height: size of the map
width, height = [int(i) for i in input().split()]

NONE = -1
ROBOT_ALLY = 0
ROBOT_ENEMY = 1
HOLE = 1
RADAR = 2
TRAP = 3
AMADEUSIUM = 4


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, pos):
        return abs(self.x - pos.x) + abs(self.y - pos.y)
        

class Entity(Pos):
    def __init__(self, x, y, type, id):
        super().__init__(x, y)
        self.type = type
        self.id = id


class Robot(Entity):
    def __init__(self, x, y, type, id, item):
        super().__init__(x, y, type, id)
        self.item = item

    def is_dead(self):
        return self.x == -1 and self.y == -1
    
    def in_HQ(self):
        return self.x == 0
        
    def get_position(self):
        return [self.x, self.y]
        
    def has_item(self):
        return self.item

    @staticmethod
    def move(x, y, message=""):
        print(f"MOVE {x} {y} {message}")

    @staticmethod
    def wait(message=""):
        print(f"WAIT {message}")

    @staticmethod
    def dig(x, y, message=""):
        print(f"DIG {x} {y} {message}")

    @staticmethod
    def request(requested_item, message=""):
        if requested_item == RADAR:
            print(f"REQUEST RADAR {message}")
        elif requested_item == TRAP:
            print(f"REQUEST TRAP {message}")
        else:
            raise Exception(f"Unknown item {requested_item}")


class Cell(Pos):
    def __init__(self, x, y, amadeusium, hole):
        super().__init__(x, y)
        self.amadeusium = amadeusium
        self.hole = hole
        self.bomb = 0
        self.radar = 0
        self.is_mine = [False, "?"]

    def has_hole(self):
        return self.hole == HOLE
        
    def has_bomb(self):
        return self.bomb == 1
        
    def has_radar(self):
        return self.radar == 1
    
    def is_cell_mine(self):
        if self.is_mine[0] == True:
            if self.is_mine[1] == "?":
                return True
            else:
                if int(self.is_mine[1]) == int(self.amadeusium):
                    return True
                else:
                    return False                
        else:
            return False

    def update(self, amadeusium, hole):
        self.amadeusium = amadeusium
        self.hole = hole


class Grid:
    def __init__(self):
        self.cells = []
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(x, y, 0, 0))

    def get_cell(self, x, y):
        if width > x >= 0 and height > y >= 0:
            return self.cells[x + width * y]
        return None


class Game:
    def __init__(self):
        self.grid = Grid()
        self.my_score = 0
        self.enemy_score = 0
        self.radar_cooldown = 0
        self.trap_cooldown = 0
        self.radars = []
        self.traps = []
        self.my_robots = []
        self.enemy_robots = []    
        self.turn = 0

    def reset(self):
        self.radars = []
        self.traps = []
        self.my_robots = []
        self.enemy_robots = []
        self.turn += 1


game = Game()

# Search Radar Territory
def radarSearch(robot, game):
    score = game.my_score - game.enemy_score
    min_distance = 450
    bestSpotX = 0
    bestSpotY = 0    
    
    # Prioritize veins with no holes
    for radar in game.radars:
        for i in range (radar.x - 4, radar.x + 5):
            for j in range (radar.y - 4, radar.y + 5):
                if i >= 1 and i < 30 and j >= 0 and j < 15:
                    cell = game.grid.get_cell(i, j)
                    amad = cell.amadeusium
                    if amad != "?":
                        if int(amad) > 0 and cell.has_hole() == False:
                            distance = robot.distance(Pos(i, j))
                            if distance <= min_distance:
                                min_distance = distance
                                bestSpotX = i
                                bestSpotY = j
                                    
    if min_distance < 450 and score >= 2:
        return [bestSpotX, bestSpotY, min_distance]
    
    # Then, all the rest
    else:
        for radar in game.radars:
            for i in range (radar.x - 4, radar.x + 5):
                for j in range (radar.y - 4, radar.y + 5):
                    if i >= 1 and i < 30 and j >= 0 and j < 15:
                        cell = game.grid.get_cell(i, j)
                        amad = cell.amadeusium
                        if amad != "?":
                            if int(amad) > 0 and cell.has_bomb() == False:
                                distance = robot.distance(Pos(i, j))
                                if distance <= min_distance:     
                                    # LAST Check, if we are losing, go, else check if has hole and is my cell
                                    if cell.has_hole() == False or cell.is_cell_mine() == True:
                                        min_distance = distance
                                        bestSpotX = i
                                        bestSpotY = j
                                    elif score <= 0 and game.turn >= 190:
                                        min_distance = distance
                                        bestSpotX = i
                                        bestSpotY = j
                                    elif game.turn >= 160 and cell.is_mine[0] == True and score < 0:
                                        min_distance = distance
                                        bestSpotX = i
                                        bestSpotY = j
                                    else:
                                        continue
                                    
        return [bestSpotX, bestSpotY, min_distance]
    
    
# Function to bury RADARS at specific places on the map
def buryRadars(game, radarNumber):    
    # we need 12 radars
    radar_spots = [(9, 7), (4,3), (14, 3), (4, 11),  (14, 11), (19, 7), (24, 3), (24, 11), (1, 7), (29, 7), \
    (8, 0), (8, 14), (19, 0), (19, 14)]
    
    for spot in radar_spots:
        cell = game.grid.get_cell(spot[0], spot[1])
        # If there is NO hole there, OK
        if cell.has_radar() == False and cell.has_hole() == False:                
            return [cell.x, cell.y]            
        # if there IS a hole
        else:
            # But it's mine, DIG
            if cell.has_radar() == False and cell.is_cell_mine() == True and cell.has_bomb() == False:
                return [cell.x, cell.y]
            # else check for X+1, Y and X+1, Y+1. If neither, skip this spot
            elif cell.has_radar() == False and cell.has_hole() == True:
                i = 0                
                while i < 4:
                    i += 1
                    second_spots = [(cell.x + i, cell.y), (cell.x, cell.y + i), (cell.x - i, cell.y), (cell.x, cell.y - i), \
                    (cell.x + i, cell.y + i), (cell.x - i, cell.y - i), (cell.x - i, cell.y + i), (cell.x + i, cell.y - i)]
                    
                    for sec_spot in second_spots:
                        if sec_spot[0] >= 1 and sec_spot[0] < 30 and sec_spot[1] >= 0 and sec_spot[1] < 15:
                            cell = game.grid.get_cell(sec_spot[0], sec_spot[1])
                            if cell.has_hole() == False:
                                return [cell.x, cell.y]
                            elif cell.is_cell_mine() == True and cell.has_radar() == False:
                                return [cell.x, cell.y]
                            elif cell.has_radar() == True:
                                i = 5
                                break
                            else:
                                continue
                            
                                
#                if spot[0] != 29:
#                    cell = game.grid.get_cell(spot[0]+1, spot[1])
#                    if cell.has_hole() == False:
#                        return [cell.x, cell.y]
#                    else:
#                        if cell.has_radar() == False:
#                            cell = game.grid.get_cell(spot[0]+1, spot[1]+1)
#                            if cell.has_hole() == False:
#                                return [cell.x, cell.y]
#                            else:
#                                continue
#                        else:
#                            continue
                    
    # worst case
    x = 14
    y = 7
    cell = game.grid.get_cell(x, y)
    while (cell.has_hole()):
        x += 1
        cell = game.grid.get_cell(x, y)
    return [x, y]
                
# Function to Bury traps at the map
def buryTraps(game, trapNumber):        
    # look at map, place trap at a vein with ores > 1
    if trapNumber < 7:
        for i in range (1, 30):
            for j in range(0, 15):
                cell = game.grid.get_cell(i, j)
                if cell.amadeusium != "?" and cell.has_hole() == False:
                    if int(cell.amadeusium) > 1 and cell.has_bomb() == False:
                        return [i, j]
        
    # worst case, plant at mid
    x = 15
    y = 7
    cell = game.grid.get_cell(x, y)
    while (cell.has_hole()):
        x += 1
        cell = game.grid.get_cell(x, y)
    return [x, y]

  
# Digs around at random  
def digAround(robot, grid):
    i = 1
    while i < 10:
        x = robot.x
        y = robot.y
        spots = [(x, y), (x+i, y), (x, y+i), (x-i, y), (x, y-i), (x+i, y+i), (x-i, y+i), (x-i, y-i), (x+i, y-i)]
        for spot in spots:
            if spot[0] >= 1 and spot[0] < 30 and spot[1] >= 0 and spot[1] < 15:
                cell = grid.get_cell(spot[0], spot[1])
                distance = robot.distance(Pos(cell.x, cell.y))
                if cell.has_hole() == False and cell.amadeusium == "?":
                    if distance < 2:
                        robot.dig(cell.x, cell.y, f"Robot digs around")
                        cell.is_mine = [True, cell.amadeusium]
                        return ""
                    else:
                        robot.move(cell.x, cell.y, f"Robot moves at random")
                        return ""
        i += 1
    
    # nothing to do
    print("WAIT , Robot can't find anything to dig with given range")
    return ""
    
    
# game loop
while True:
    # my_score: Players score
    game.my_score, game.enemy_score = [int(i) for i in input().split()]
    for i in range(height):
        inputs = input().split()
        for j in range(width):
            # amadeusium: amount of amadeusium or "?" if unknown
            # hole: 1 if cell has a hole
            amadeusium = inputs[2 * j]
            hole = int(inputs[2 * j + 1])
            game.grid.get_cell(j, i).update(amadeusium, hole)
    # entity_count: number of entities visible to you
    # radar_cooldown: turns left until a new radar can be requested
    # trap_cooldown: turns left until a new trap can be requested
    entity_count, game.radar_cooldown, game.trap_cooldown = [int(i) for i in input().split()]

    game.reset()

    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for AMADEUSIUM)
        id, type, x, y, item = [int(j) for j in input().split()]

        if type == ROBOT_ALLY:
            game.my_robots.append(Robot(x, y, type, id, item))
        elif type == ROBOT_ENEMY:
            game.enemy_robots.append(Robot(x, y, type, id, item))
        elif type == TRAP:
            game.traps.append(Entity(x, y, type, id))
            # Add bomb to cell
            game.grid.get_cell(x, y).bomb = 1
        elif type == RADAR:
            game.radars.append(Entity(x, y, type, id))
            game.grid.get_cell(x, y).radar = 1

        
    for i in range(len(game.my_robots)):
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        
        # WAIT|
        # MOVE x y|REQUEST item
        # game.my_robots[i].wait(f"Starter AI {i}")
        robot = game.my_robots[i]
        radars = len(game.radars)    
        traps = len(game.traps)
# if ROBOT is DEAD
        if robot.is_dead():  
            print("WAIT Robot {i} is dead")
            
# if ALIVE
        else:            
  # ROBOT IS IN THE HQ
            if robot.in_HQ():
            # If RADAR is available, get it
                # we want 10 radars, fow now
                if game.radar_cooldown == 0 and robot.has_item() != RADAR \
                and robot.has_item() != TRAP and radars < 14:
                    robot.request(RADAR, f"Robot {i}")
                    # manually set radar cooldown to avoid stuck robots for a turn
                    game.radar_cooldown = -1
                    
            # If TRAP is available, get it        
                elif game.trap_cooldown == 0 and robot.has_item() != RADAR \
                and robot.has_item() != TRAP and traps < 7 and game.turn >= 100:
                    robot.request(TRAP, f"Robot {i}")
                    game.trap_cooldown = -1
                    
                # If Robot is carrying a Radar
                elif robot.has_item() == RADAR:
                    radar_spot = buryRadars(game, radars)
                    robot.move(radar_spot[0], radar_spot[1], f"Robot {i} moves to bury a RADAR")
                    
                elif robot.has_item() == TRAP:
                    trap_spot = buryTraps(game, traps)
                    robot.move(trap_spot[0], trap_spot[1], f"Robot {i} moves to bury a TRAP")
                        
                # If we have already burried radars
                elif radars > 0:
                    spot = radarSearch(robot, game)                
                    # Move to a Vein
                    if spot[2] < 450:
                        robot.move(spot[0], spot[1], f"Robot {i} moves to a Vein from HQ")
                    else:
                        # Else move
                        robot.move(7, robot.y, f"Robot {i}")
                # Else move
                else:
                    robot.move(7, robot.y, f"Robot {i}")
                
  # ROBOT IS IN THE FIELD
            else:                
            # Has the stuff, move back to load off
                if robot.has_item() == AMADEUSIUM:
                    robot.move(0, robot.y, f"Robot {i}, Unloading at HQ")
                    
            # Else if robot has a RADAR, burry it
                elif robot.has_item() == RADAR:
                    radar_spot = buryRadars(game, radars)
                    # If on SPOT, DIG
                    if robot.x == radar_spot[0] and robot.y == radar_spot[1]:
                        robot.dig(robot.x, robot.y, f"Robot {i} buries RADAR")
                        game.grid.get_cell(robot.x, robot.y).robot = 1
                    else:
                        robot.move(radar_spot[0], radar_spot[1], f"Robot {i} moves to RADAR spot")
                        
            # Else if robot has TRAP, burry it
                elif robot.has_item() == TRAP:
                    trap_spot = buryTraps(game, traps)
                    # If on spot, DIG
                    if robot.x == trap_spot[0] and robot.y == trap_spot[1]:
                        robot.dig(robot.x, robot.y, f"Robot {i} buries a TRAP")
                        game.grid.get_cell(robot.x, robot.y).bomb = 1
                    # Else MOVE to spot
                    else:
                        robot.move(trap_spot[0], trap_spot[1], f"Robot {i} moves to TRAP spot")
                    
            # Else dig around
                else:
                    cell = game.grid.get_cell(robot.x, robot.y)
                    cell_amad = cell.amadeusium
                    
                    # If we have already burried radars
                    if len(game.radars) > 0:    
                        spot = radarSearch(robot, game)                    
                        # If we have found a Vein Cell, within range, dig
                        if spot[2] <= 1:
                            robot.dig(spot[0], spot[1], f"Robot {i} is digging a Vein")
                            next_cell = game.grid.get_cell(spot[0], spot[1])
                            next_cell.is_mine = [True, int(next_cell.amadeusium) - 1]                          
                        elif spot[2] < 450:
                            robot.move(spot[0], spot[1], f"Robot {i} moves to a Vein")
                        else:
                            # Else REQUEST RADAR
                            if game.radar_cooldown == 0 and radars < 14:
                                robot.request(RADAR, f"Robot {i}")
                                game.radar_cooldown = -1
                            else:
                                digAround(robot, game.grid)
                    else:
                        # Else REQUEST RADAR
                        if game.radar_cooldown == 0 and radars < 14:
                            robot.request(RADAR, f"Robot {i}")
                            game.radar_cooldown = -1
                        # Request TRAP
                        else:
                            if game.trap_cooldown == 0 and traps < 7 and game.turn >= 100:
                                robot.request(TRAP, f"Robot {i}")
                                game.trap_cooldown = -1
                            else:
                                digAround(robot, game.grid)
