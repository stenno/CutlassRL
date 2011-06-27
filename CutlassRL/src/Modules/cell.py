class Cell:
    __slots__ = ("visible","explored","mob","stairs","sdoor",\
                 "item","door","lit","fval","color","type")
    visible = False  #All cells are invisible by default
    explored = False #All cells are unexplored by default
    mob = False
    stairs = False
    sdoor = False
    item = False
    type = (False,False)
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
    def __setstate__(self,state):
        pass
    def __getstate__(self):
        pass
class Stair(Cell):
    __slots__ = ("up")
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
    __slots__ = ("hp","chr","has_turn","damage","undercell")
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
    __slots__ = ("undercell")
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
    __slots__ = ("opened")
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
    __slots__ = ("known")
    known = False
    sdoor = True
    color = 4
    def __init__(self):
        self.type = [False,False]
    def  char(self):
            return "#"
        
class item(Mob): #Yeah, it is funny :D
    __slots__ = ("item")
    mob = False
    item = True
    chr = "$"
    name = "Gold"
    color = 4
    type = (True,True)
    