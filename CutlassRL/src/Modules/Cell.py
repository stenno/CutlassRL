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

from Modules.Constants import *  #Import constants
import random

class Cell:
    __slots__ = ("visible","explored","type","mob","stairs","sdoor","door",\
                 "item","lit","fval","color","plain_cell","changed")
    visible = False  #All cells are invisible by default
    explored = False #All cells are unexplored by default
    mob = False
    plain_cell = False
    stairs = False
    sdoor = False
    item = False
    boulder = False
    door= False
    lit = False      #All cells are unlit by default
    fval = 0
    color = 4
    corner = False
    changed = True
    ccells = []
    def __init__(self,isWalkable,isTransparent):
        self.type = (isWalkable, isTransparent)
        if isWalkable and isTransparent:
            self.color = 1
        self.plain_cell = True
    def char(self):
        if self.type[0]:
            return '.'
        else:
            return '#'
    
class Stair(Cell):
    up = False
    color = 1
    lit = True
    stairs = True
    type = [True,True]
    def __init__(self,isUp):
        self.up = isUp
    def char(self):
        if self.up:
            return "<"
        else:
            return ">"
    def move(self):
        if self.up:
            return -1
        else:
            return 1
class Mob(Cell):
    speed = 100
    energy = 0
    mob = True
    hp = 10
    name = "Mob"
    chr = "M"
    infra = True
    lit = False
    infra_y = True
    phasing = False
    color = 4
    type = (False,True)
    has_turn = False
    damage = 2
    def __init__(self,name,char,undercell):
        self.name = name
        self.chr = char
        self.undercell = undercell
        self.lit = undercell.lit        

    def char(self):
        return self.chr

class Newt(Mob):
    def __init__(self,name,char,undercell):
        self.name = name
        self.chr = char
        self.undercell = undercell        
    hp = 10
    speed = 50
    infra_y = False
    name = "Newt"
    chr = ":"
    color = 4
    damage = 3

class Leprechaun(Mob):
    def __init__(self,undercell):
        self.undercell = undercell        
    hp = 25
    speed = 150
    name = "Leprechaun"
    chr = "l"
    infra = True
    infray_y = True
    color = GREEN
    damage = 2

class Ghost(Mob):
    def __init__(self,undercell):
        self.undercell = undercell        
    hp = 50
    speed = 30
    name = "Ghost"
    chr = " "
    phasing = True
    infra = True
    infra_y = False
    color = GREEN
    damage = 5
    phasing = False


class altar(Mob):
    def __init__(self,char):
        self.chr = char
    mob = False
    name = "Altar"
    type = [True,True]
    chr = "="
    lit = True
    color = 6
    def char(self):
        return self.chr

class Door(Cell):
    opened = True
    door = True
    locked = False
    def __init__(self,isOpen,locked):
        self.opened = isOpen 
        self.locked = locked
        if self.opened:
            self.type = (True,True)
        else:
            self.type = (False,False)
    def open(self):
        self.opened = True
        self.type = (True,True)
    def close(self):
        self.opened = False
        self.type = (False,False)        
    def char(self):
        if self.type[0]:
            return '-'
        else:
            return '+'

class secretDoor(Cell):
    known = False
    sdoor = True
    def __init__(self):
        self.type = [False,False]
    def  char(self):
            return "#"
        
class item(Mob): #Yeah, it is funny :D
    mob = False
    item = True
    chr = "$"
    name = "Gold"
    color = 4
    type = [True,True]
    def __init__(self,name,char,undercell):
        self.name = name
        self.chr = char
        self.undercell = undercell        
        self.howmany = random.randint(4,10)

class cutlass(item): 
    chr = "|"
    name = "The Dark Cutlass"
    color = 6
    type = [True,True]

class Boulder(item):
    type = [False,False]
    color = WHITE
    item = False
    boulder = True
    lit = False
    def char(self):
        return '0'
    def __init__(self,undercell):
        self.undercell = undercell        
    