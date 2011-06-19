class Cell:
    def __init__(self,isWalkable,isTransparent):
        self.type = (isWalkable, isTransparent,False) 
        self.visible = False  #All cells are invisible by default
        self.explored = False #All cells are unexplored by default
class Door:
    def __init__(self,isOpen):
        self.door = isOpen 
        self.type = (False,False,True)
        self.visible = False 
        self.explored = False
    def open(self):
        self.door = True
        self.type = (True,True,True)
    def close(self):
        self.door = False
        self.type = (False,False,True)        
