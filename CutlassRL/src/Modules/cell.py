class Cell:
    visible = False  #All cells are invisible by default
    explored = False #All cells are unexplored by default
    mob = False
    door= False
    lit = False      #All cells are unlit by default
    lit_by = [False, False]
    fval = 0
    color = 4
    def __init__(self,isWalkable,isTransparent):
        self.type = (isWalkable, isTransparent)
    def char(self):
        if self.type[0]:
            return '.'
        else:
            return '#'
        
class Mob(Cell):
    mob = True
    hp = 10
    name = "Mob"
    chr = "M"
    lit = True
    color = 4
    type = (False,True)
    damage = 2
    def __init__(self,name,char,undercell):
        self.name = name
        self.chr = char
        self.undercell = undercell        

    def char(self):
        return self.chr

class Dragon(Mob):
    hp = 30
    name = "Dragon"
    chr = "D"
    lit = True
    color = 2
    damage = 3

class Newt(Mob):
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
        self.type = (False,False)
    def open(self):
        self.opened = True
        self.type = (True,True)
    def close(self):
        self.opened = False
        self.type = (False,False)        
    def char(self):
        if self.opened:
            return '-'
        else:
            return '+'
