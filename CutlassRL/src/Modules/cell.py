class Cell:
    visible = False  #All cells are invisible by default
    explored = False #All cells are unexplored by default
    lit = False      #All cells are unlit by default
    pc = [5,5]       #Player's x and y
    
    def __init__(self,isWalkable,isTransparent):
        self.type = (isWalkable, isTransparent,False)
         
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
