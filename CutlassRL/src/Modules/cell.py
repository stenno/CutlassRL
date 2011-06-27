class Cell:
    __slots__ = ("visible","explored","type","mob","stairs","sdoor","door",\
                 "item","lit","fval","color")
    visible = False  #All cells are invisible by default
    explored = False #All cells are unexplored by default
    mob = False
    stairs = False
    sdoor = False
    item = False
    door= False
    lit = False      #All cells are unlit by default
    fval = 0
    color = 4
    def __init__(self,isWalkable,isTransparent):
        self.type = (isWalkable, isTransparent)
    def char(self):
        if self.type[0]:
            return '.'
        else:
            return '#'
class Stair(Cell):
    up = False
    color = 1
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
    mob = True
    hp = 10
    name = "Mob"
    chr = "M"
    lit = True
    color = 4
    type = (False,True)
    has_turn = False
    damage = 2
    def __init__(self,name,char,undercell):
        self.name = name
        self.chr = char
        self.undercell = undercell        

    def char(self):
        return self.chr

class Newt(Mob):
    def __init__(self,name,char,undercell):
        self.name = name
        self.chr = char
        self.undercell = undercell        
    hp = 10
    name = "Newt"
    chr = ":"
    lit = True
    color = 4
    damage = 3

class Door(Cell):
    opened = True
    door = True
    def __init__(self,isOpen):
        self.opened = isOpen 
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
    color = 4
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
    type = (True,True)
    