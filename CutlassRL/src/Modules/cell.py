class Cell:
    visible = False  #All cells are invisible by default
    explored = False #All cells are unexplored by default
    mob = False
    door= False
    lit = False      #All cells are unlit by default
    pc = [5,5]       #Player's x and y
    def __init__(self,isWalkable,isTransparent):
        self.type = (isWalkable, isTransparent)
        
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
    opened = True
    def __init__(self,isOpen):
        self.opened = isOpen 
        self.type = (False,False)
    def open(self):
        self.opened = True
        self.type = (True,True)
    def close(self):
        self.opened = False
        self.type = (False,False)        
