# -*- coding: utf-8 -*-
#     This file is part of CutlassRL.
#
#    CutlassRL is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CutlassRL is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CutlassRL.  If not, see <http://www.gnu.org/licenses/>.
#    Copyright (c) init

import random
import sys

from Modules.constants import *
from Modules import cell as lcell

class levGen:
    boulders = []
    def createRoom(self,room):
        lit = random.randint(0,1)
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.lmap[y][x].type =  True,True
                if lit:
                    self.lmap[y][x].lit = True
                    for x2 in xrange(-1,2):
                        for y2 in xrange(-1,2):
                            self.lmap[y + y2][x + x2].lit = True
    def vCorridor(self,y1,y2,x):
        boulder = False
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.lmap[y][x].type =  True,True
            if not random.randint(0,40) and not boulder:
                boulder = True
                self.boulders.append((y,x))
    def hCorridor(self,x1,x2,y):
        boulder = False
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.lmap[y][x].type = True,True
            if not random.randint(0,40) and not boulder:
                boulder = True
                self.boulders.append((y,x))
    def generateLevel(self,lmap):
        global playerx, playery
        self.lmap = lmap
        rooms = []
        num_rooms = 0
        playerx, playery = 0,0
        
        for line in lmap:
            for tile in line:
                tile.type = [False,False]
                
        for r in range(MAX_ROOMS):
            #random width and height
            w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            #random position without going out of the boundaries of the map
            x = random.randint(2, MAX_H + 1 - w - 1)
            y = random.randint(2, MAX_W + 1 - h - 1)
     
            new_room = Rect(x, y, w, h)
     
            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break
            if not failed:
                self.createRoom(new_room)
                (new_x, new_y) = new_room.center()
                if num_rooms == 0:
                    #this is the first room, where the player starts at
                    playerx = new_x
                    playery = new_y
                    prev_x, prev_y = new_x, new_y
                else:
                    (prev_x, prev_y) = rooms[num_rooms-1].center()
                if random.randint(0, 1) == 1:
                    #first move horizontally, then vertically
                    self.hCorridor(prev_x, new_x, prev_y)
                    self.vCorridor(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    self.vCorridor(prev_y, new_y, prev_x)
                    self.hCorridor(prev_x, new_x, new_y)
                rooms.append(new_room)
                num_rooms += 1
        for room in rooms:
            for x in xrange(room.x1,room.x2):
                for y in xrange(room.y1 + 1,room.y2 - 1):
                    if self.lmap[y][x].type[0] and x == room.x1 or x ==\
                     room.x2 or y == room.y1 or y == room.y2:
                        if not self.lmap[y + 1][x].type[0] and\
                        not self.lmap[y - 1][x].type[0] or\
                        not self.lmap[y][x - 1].type[0] and\
                        not self.lmap[y][x + 1].type[0]:
                            if not random.randint(0,5):
                                if not random.randint(0,3):
                                    lit = self.lmap[y][x].lit;
                                    self.lmap[y][x] = lcell.secretDoor()
                                    self.lmap[y][x].lit = lit
                                else:
                                    lit = self.lmap[y][x].lit;
                                    self.lmap[y][x] = lcell.Door(False)
                                    self.lmap[y][x].lit = lit
                            else:
                                lit = self.lmap[y][x].lit;
                                self.lmap[y][x] = lcell.Door(True)
                                self.lmap[y][x].lit = lit
        for boulder in self.boulders:
            if not random.randint(0,5):
                self.lmap[boulder[0]][boulder[1]] = lcell.Boulder(self.lmap\
                                                      [boulder[0]][boulder[1]])
        (x1,y1) = rooms[0].center()
        rn = random.randint(1,len(rooms) - 1)
        (x,y) = rooms[rn].center()
        ych = random.randint(-5,5)
        xch = random.randint(-5,5)
        while not self.lmap[y + ych][x + xch].type[0] and (ych,xch) !=\
         (0,0): 
            ych = random.randint(-5,5)
            xch = random.randint(-5,5)
        lit = self.lmap[y + ych][x + xch].lit
        self.lmap[y + ych][x + xch] = lcell.Stair(False)
        self.lmap[y + ych][x + xch].lit = lit
        
        ych = random.randint(-5,5)
        xch = random.randint(-5,5)
        while not self.lmap[y1 + ych][x1 + xch].type[0] and (ych,xch) !=\
             (0,0): 
            ych = random.randint(-5,5)
            xch = random.randint(-5,5)
        lit = self.lmap[y1 + ych][x1 + xch].lit
        self.lmap[y1 + ych][x1 + xch] = lcell.Stair(True)
        self.lmap[y1 + ych][x1 + xch].lit = lit
        playerx = x1 + xch
        playery = y1 + ych
        self.oMap()
        return lmap,playerx,playery
        
    def near(self,x1,y1,x2,y2):
        if x1 - x2 >= -1 and x1 - x2 <= 1 and\
                    y1 - y2 >= -1 and y1 - y2 <= 1:
            return True
        else:
            return False

    def oMap(self):
        self.flood(0,0,5,0,self.lmap)
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                if self.lmap[mapx][mapy].fval == 5:
                    self.lmap[mapx][mapy] = self.lmap[0][0]

    def flood(self,x,y,v,d,gamemap):
        """Recursive floodfill function"""
        sys.setrecursionlimit(2000)
        if not gamemap[x][y].type[0]:
            return  0
        gamemap[x][y].fval = v
        self.flood(x + 1,y,v,d,gamemap)
        self.flood(x + 1,y + 1,v,d,gamemap)
        self.flood(x - 1,y,v,d,gamemap)
        self.flood(x - 1,y - 1,v,d,gamemap)
        self.flood(x,y + 1,v,d,gamemap)
        self.flood(x,y - 1,v,d,gamemap)
        self.flood(x + 1,y - 1,v,d,gamemap)
        self.flood(x - 1,y + 1,v,d,gamemap)
        return


class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)