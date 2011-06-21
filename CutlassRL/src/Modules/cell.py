class Cell:
    visible = False  #All cells are invisible by default
    explored = False #All cells are unexplored by default
    mob = False
    lit = False      #All cells are unlit by default
    pc = [5,5]       #Player's x and y
    def __init__(self,isWalkable,isTransparent):
        self.type = (isWalkable, isTransparent,False,)
        
class Mob(Cell):
    mob = True
    hp = 10
    name = "Mob"
    char = "M"
    id = 0
    lit = True
    color = 4
    type = (False,True,False)
    def __init__(self,name,char,undercell):
        self.name = name
        self.char = char
        self.undercell = undercell        
class Door(Cell):
    def __init__(self,isOpen):
        self.door = isOpen 
        self.type = (False,False,True)
    def open(self):
        self.door = True
        self.type = (True,True,True)
    def close(self):
        self.door = False
        self.type = (False,False,True)        
