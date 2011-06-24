class Cell:
    visible = False  #All cells are invisible by default
    explored = False #All cells are unexplored by default
    mob = False
    door= False
    lit = False      #All cells are unlit by default
    lit_by = [False, False]
    fval = 0
    def __init__(self,isWalkable,isTransparent):
        self.type = (isWalkable, isTransparent)
        
class Mob(Cell):
    mob = True
    hp = 10
    name = "Mob"
    char = "M"
    lit = True
    color = 4
    type = (False,True)
    damage = 2
    def __init__(self,name,char,undercell):
        self.name = name
        self.char = char
        self.undercell = undercell        

class Dragon(Mob):
    hp = 30
    name = "Dragon"
    char = "D"
    lit = True
    color = 2
    damage = 3

class Newt(Mob):
    hp = 10
    name = "Newt"
    char = ":"
    lit = True
    color = 4
    damage = 3

class Door(Cell):
    opened = True
    door = True
    def __init__(self,isOpen):
        self.opened = isOpen 
        self.type = (False,False)
    def open(self):
        self.opened = True
        self.type = (True,True)
    def close(self):
        self.opened = False
        self.type = (False,False)        
