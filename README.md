# Unleash the Geek
From the coding challenge on CodinGame, sponsored by Amadeus!

## Rank 757 / 2162 - Silver League

### Started with the Starter AI from this link: https://gist.github.com/CGjupoulton/e93512f74336aeef97a2c2a52b381e20

Goal

Amadeusium is a rare and valuable crystal ore which is only found on inhospitable planets. As one of two competing mining companies, you must control the robots on-site to unearth as much ore as you can.
Deliver more Amadeusium than your opponent!

Rules

Both players control a team of several robots. The teams start out at the same points on the map, at the headquarters. The robots can use radars from the headquarters to detect and mine Amadeusium veins. They may also trap certain areas of the map with EMP traps. These can be triggered by robots which are then rendered inoperable.

The map

The game is played on a grid 30 cells wide by 15 cells high. The coordinates x=0, y=0 corresponds to the top left cell.

The first column of cells is considered to be part of the headquarters. This is where Amadeusium ore must be returned to once mined and where objects are requested.

The cells that contain Amadeusium ore are called vein cells. Veins are not visible to the players unless they are within the range of the player's radar. There are no vein cells in the headquarters.

Robots can drill a hole on any cell (except the headquarters'). Holes are visible to both players and do not impede movement.

Robots

Each robot can hold 1 item in its inventory.

A robot may:

    REQUEST an item from the headquarters.
    MOVE towards a given cell.
    DIG on a cell. This will, in order:
        Create a hole on this cell if there isn't one already.
        Bury any item the robot is holding into the hole.
        If digging on a vein cell and ore was not buried on step 2, place one unit of ore into the robot's inventory.
    WAIT to do nothing. 

Details:

    Robots may only dig on the cell they occupy or neighbouring cells. Cells have 4 neighbours: up, left, right, and down.
    Robots on any cell part of the headquarters will automatically deliver any ore it is holding.
    Robots can occupy the same cell.
    Robots cannot leave the grid.
    Robots' inventories are not visible to the opponent.

Items

Amadeusium Ore is considered an item and should be delivered to the headquarters to score 1 point.

At the headquarters, robots may request one of two possible items: a RADAR or a TRAP.

If an item is taken from the headquarters, that item will no longer be available for the robots of the same team for 5 turns.

A trap buried inside a hole will go off if any robot uses the DIG command on the cell it is buried in. The EMP pulse destroys any robots on the cell or on the 4 neighbouring cells. Any other trap caught in the pulse will also go off, causing a chain reaction.

A radar buried inside a hole will grant the ability to see the amount of buried ore in veins within a range of 4 cells, for the team which buried it. If an opponent robot uses the DIG on the cell the radar is buried in, the radar is destroyed.

Action order for one turn

    If DIG commands would trigger Traps, they go off.
    The other DIG commands are resolved.
    REQUEST commands are resolved.
    Request timers are decremented.
    MOVE and WAIT commands are resolved.
    Ore is delivered to the headquarters.

Victory Conditions

    After 200 rounds, your team has delivered the most Amadeusium ore.
    You have delivered more ore than your opponent and they have no more active robots.

Defeat Conditions

    Your program does not provide one valid command per robot in time, including destroyed robots.

  Technical Details

    Robots can insert ore into a cell, the cell becomes a vein.
    Each robot, radar and trap has a unique id.
    Receiving an item from the headquarters will destroy any item a robot may already be holding.
    When several robots of the same team request an item, robots with no item will be given priority for the request.
    Traps have no effect on buried radars and ore.
    If a robot holding an item is destroyed, the item is lost.
