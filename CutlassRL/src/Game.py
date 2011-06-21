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

VERSION = 0.03;

MAP_H=80
MAP_W=24

SAVE = "game.sav"

import sys
import pickle
import os.path
import math

from Modules import *

try:
    import curses               # Game will use curses to draw things
except ImportError:
    print "Curses library is missing."
    exit()




class Game:                # Main game class
    def __init__(self):
        global screen,stdscr
        """Initializer of Game class.
            Will start curses.
        """
        screen = curses;
        stdscr = screen.initscr()
        
        screen.curs_set(0)
        screen.cbreak()
        screen.start_color()
        screen.use_default_colors()
        stdscr.keypad(1)

        #Color pairs
        screen.init_pair(1,-1,-1) #Default
        screen.init_pair(2,screen.COLOR_RED,-1) 
        screen.init_pair(3,screen.COLOR_GREEN,-1) 
        screen.init_pair(4,screen.COLOR_YELLOW,-1)
        screen.init_pair(5,screen.COLOR_BLUE,-1) 
        screen.init_pair(6,screen.COLOR_MAGENTA,-1)
        screen.init_pair(7,screen.COLOR_CYAN,-1) 
        screen.init_pair(8,screen.COLOR_WHITE,-1)

        stdscr.attron(screen.color_pair(1))
        
    def main_loop(self):
        """Main loop of game.
            Drawing things, generating map, playing
        """
        global gamemap,fovblock
        global x,y
        fovblock = False
        
        x,y = 5,5

        key = ""
        
        turns = 0
        
        gamemap = []  

        for mapx in xrange(MAP_W+1):
            gamemap.append([])
            for mapy in xrange(MAP_H+1):
                if mapx <= 21 and mapx >= 2 and mapy <= 60 and mapy >= 2:
                    gamemap[mapx].append(cell.Cell(True,True))
                else:
                    gamemap[mapx].append(cell.Cell(False,False))
        if os.path.isfile(SAVE):           
            self.load()
        x1,y1 = x,y
        fov.fieldOfView(x, y, MAP_W, MAP_H, 9, self.setVisible, self.isBlocking)                        
        self.drawmap()
        self.printex(x,y ,"@", refresh=False)
        self.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)+";T:"\
                     +str(turns)) #DEBUG 
        turn = False
        self.aStarLoadMap()
        while 1:
            self.printex(23, 0, " " * 60, refresh = False)
            key = self.readkey()
            if key == "8" or key == "k":
                x1-=1
                turn = True
            elif key == "2" or key == "j":
                x1+=1
                turn = True
            elif key == "4" or key == "h":
                y1-=1
                turn = True
            elif key == "6" or key == "l":
                y1+=1
                turn = True
            elif key == "q":
                self.end()
            elif key == "s":
                x,y = x1,y1
                self.save()
            elif key == "m":
                self.printex(23,0,"")
                stdscr.getstr()
            elif key == "r":
                self.load()
                x1,y1 = x,y
                self.resetFov()
                self.drawmap()
                fov.fieldOfView(x, y, MAP_W, MAP_H, 9, self.setVisible,\
                                 self.isBlocking)                        
                self.printex(0,0,"")
            elif key == "x":
                gamemap[x][y].type = (False,False,False)
            elif key == "d":
                gamemap[x][y] = cell.Door(True)
                gamemap[x][y].close()
            elif key == "v":
                gamemap[x][y].lit = not gamemap[x][y].lit
            elif key == "p":
                d = self.askDirection()
                rx = d[0]
                ry = d[1]
            elif key == "g":
#                self.moveMob(rx, ry, rx, ry + 1)
                if self.inLos(x,y,rx,ry):
                    self.debug_message("%d : %d is in los" % (rx,ry))
                    self.readkey()
            elif key == "z":
                fovblock = not fovblock
            elif key == "e":
                d = self.askDirection()
                if d:
                    self.moveMob(d[0],d[1], x, y)
            elif key == ";":
                self.printex(23, 0, "You")
                screen.curs_set(1)
                self.printex(x, y, "")
                cx1,cy1,cx,cy = x,y,x,y
                while key != "q":
                    key = self.readkey()
                    if key == "8" or key == "k":
                        cx1-=1
                    elif key == "2" or key == "j":
                        cx1+=1
                    elif key == "4" or key == "h":
                        cy1-=1
                    elif key == "6" or key == "l":
                        cy1+=1
                    elif key == "7" or key == "y":
                        cx1-=1
                        cy1-=1
                    elif key == "9" or key == "u":
                        cx1-=1
                        cy1+=1
                    elif key == "1" or key == "b":
                        cx1+=1
                        cy1-=1
                    elif key == "3" or key == "n":
                        cx1+=1
                        cy1+=1
                    if cx1 <= 22 and cx1 >= 1 and cy1 <= 61 and cy1 >= 1:
                        cx,cy = cx1,cy1
                    else:
                        cx1,cy1 = cx,cy
                    type = ""
                    if not gamemap[cx][cy].explored:
                        type = "Unexplored"
                    elif gamemap[cx][cy].type[0] and not gamemap[cx][cy].door:
                        type = "Ground"
                    elif gamemap[cx][cy].mob:
                        if gamemap[cx][cy].visible:
                            type = gamemap[cx][cy].name
                        else:
                            if gamemap[cx][cy].undercell.type[2]:
                                type = "Open door"
                            else:
                                type = "Ground"
                    elif  not gamemap[cx][cy].type[0] and not\
                     gamemap[cx][cy].door:
                        type = "Wall"
                    elif gamemap[cx][cy].door:
                        if gamemap[cx][cy].opened:
                            type = "Open door"
                        else:
                            type = "Closed door"
                    if [cx,cy] == [x,y]:
                        type = "You"
                    self.printex(23, 0, type)
                    self.printex(cx, cy, "")
                    self.printex(23, 0, " " * 20, refresh = False)                                        
                screen.curs_set(0)
            elif key == "o":
                d = self.askDirection()
                if d:
                    dx = d[0]
                    dy = d[1]
                    if gamemap[dx][dy].door:
                        gamemap[dx][dy].open()
            elif key == "c":
                d = self.askDirection()
                if d:
                    dx = d[0]
                    dy = d[1]
                    if gamemap[dx][dy].door:
                        gamemap[dx][dy].close()
            elif key == "f":
                d = self.askDirection()
                if d:
                    dx = d[0]
                    dy = d[1]
                    if gamemap[dx][dy].mob:
                        gamemap[dx][dy] = gamemap[dx][dy].undercell 
            elif key == "a":
                self.amnesia()
                self.printex(23, 0, \
                             "Thinking of Maud you forget everything else.")
            elif key == "b":
                d = self.askDirection()
                if d:
                    dx = d[0]
                    dy = d[1]
                    if dx <= 21 and dx >= 2 and dy <= 60 and dy >= 2:
                        gamemap[dx][dy].type = (True, True)
            elif key == "t":
                ucell = gamemap[x][y]
                gamemap[x][y] = cell.Mob("Mob","M",ucell)
            elif key == "w":
                turn = True
            else:
                if not gamemap[x][y].door:
                    if key == "7" or key == "y":
                        x1-=1
                        y1-=1
                        turn = True
                    elif key == "9" or key == "u":
                        x1-=1
                        y1+=1
                        turn = True
                    elif key == "1" or key == "b":
                        x1+=1
                        y1-=1
                        turn = True
                    elif key == "3" or key == "n":
                        x1+=1
                        y1+=1
                        turn = True
                    else:
                        turn = False
                    if gamemap[x1][y1].door:
                        x1,y1 = x,y
            if gamemap[x1][y1].type[0]:
                x,y = x1,y1
                self.resetFov()
                fov.fieldOfView(x, y, MAP_W, MAP_H, 9, self.setVisible,\
                                 self.isBlocking)                        
            else:
                if gamemap[x1][y1].door:
                    gamemap[x1][y1].open()
                x1,y1 = x,y
                fov.fieldOfView(x, y, MAP_W, MAP_H, 9, self.setVisible,\
                                 self.isBlocking)
                turn = False                        
            # Mob's turn
            if turn:
                turns += 1
                mapx,mapy = 0,0
                for mapx in xrange(MAP_W - 1):
                    for mapy in xrange(MAP_H):
                        if gamemap[mapx][mapy].mob:
                            self.aStarPathfind(mapx, mapy,x,y)
            ####
            self.drawmap()
            self.printex(x,y ,"@",refresh=False)
            self.printex(0,0," " * 50,refresh=False)
            self.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)+";T:"\
                         +str(turns)) #DEBUG 

    def end(self):
        """End of game.
            Will reset console and stop curses.
        """
        screen.endwin()
        exit()
        
    def debug_message(self,msg):
        """Debug message subroutine,
            Will say something like debugmsg: XXX
        """
        stdscr.attron(screen.A_BOLD)
        self.printex(10,10,"debugmsg: %s" % msg,1)
        stdscr.attroff(screen.A_BOLD)
        
    def printex(self,x,y,text = "Someone had no words to say..." ,pair = None\
                ,refresh = True):
        """Print function.
            usage game.printex(<x of your text>,<y>,<Your text>,
            <color pair>,<refresh?>)
        """
        if pair:
            stdscr.attron(screen.color_pair(1))            
            
        stdscr.addstr(x,y,text)
        
        if refresh:
            stdscr.refresh()
            
        if pair != None:
            stdscr.attroff(screen.color_pair(pair))

    def readkey(self):
        """Readkey function.
            reads one key from stdin.
        """
        try:
            key = sys.stdin.read(1)
        except IOError:
            key = ""
        return key
    
    def drawmap(self):
        """Drawmap function.
            Will draw map. Working with fov.
        """
        global gamemap,screen,stdscr
        mapx,mapy=0,0 
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):
                if not gamemap[mapx][mapy].type[1]:
                    attr = 4;
                    mchar = "#"
                else:
                    attr = 1;
                    mchar = "."
                if gamemap[mapx][mapy].mob:
                    if not self.inLos(x, y, mapx, mapy):
                        if gamemap[mapx][mapy].undercell.door:
                            attr = 4
                            mchar = "-"
                        else:
                            attr = 1
                            mchar = "."
                    else:
                        attr = gamemap[mapx][mapy].color
                        mchar = gamemap[mapx][mapy].char                        
                if gamemap[mapx][mapy].door:
                    if not gamemap[mapx][mapy].opened:
                        attr = 4                        
                        mchar = "+"
                    else:
                        attr = 4
                        mchar = "-"
                if mapx <= 22 and mapx >= 1 and mapy <= 61 and mapy >= 1:
                        if gamemap[mapx][mapy].visible:
                            stdscr.attron(screen.A_BOLD)
                            gamemap[mapx][mapy].explored = True
                        else:
                            if not gamemap[mapx][mapy].explored:
                                    mchar = " "
                            if gamemap[mapx][mapy].lit:
                                line = self.get_line(y, x, mapy, mapx) 
                                b = 0 
                                for j in line:
                                    vis = True
                                    if b:
                                        attr = 5
                                        vis = False                                        
                                        break
                                    jy = j[0]
                                    jx = j[1]
                                    if not gamemap[jx][jy].type[1]:
                                        b = 1
                                else:
                                    if vis:
                                        stdscr.attron(screen.A_BOLD)
                                        gamemap[jx][jy].visible = True
                                        gamemap[jx][jy].explored = True
                                               
                            else:
                                attr = 5
                        stdscr.attron(screen.color_pair(attr))
                        self.printex(mapx,mapy,mchar,refresh=False)
                        stdscr.attroff(screen.A_BOLD)
                        stdscr.attroff(screen.color_pair(attr))
        stdscr.refresh()

    def isBlocking(self,x,y):
        global gamemap
        return not gamemap[x][y].type[1]

    def setVisible(self,x,y):
    
        global gamemap,fovblock
        gamemap[x][y].visible = not fovblock

    def resetFov(self):
        global gamemap
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                gamemap[mapx][mapy].visible = False

    def amnesia(self):
        global gamemap
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                gamemap[mapx][mapy].explored = False
 
    def askDirection(self):
        global x,y
        x1,y1 = x,y
        self.printex(23, 0, "What direction:")
        key = self.readkey()
        if key == "8" or key == "k":
            x1-=1
        elif key == "2" or key == "j":
            x1+=1
        elif key == "4" or key == "h":
            y1-=1
        elif key == "6" or key == "l":
            y1+=1
        elif key == "7" or key == "y":
            x1-=1
            y1-=1
        elif key == "9" or key == "u":
            x1-=1
            y1+=1
        elif key == "1" or key == "b":
            x1+=1
            y1-=1
        elif key == "3" or key == "n":
            x1+=1
            y1+=1
        else:
            self.printex(23, 0, "Wrong direction!")
            return False
        return x1,y1
    
    def load(self):
        global gamemap,x,y
        save = open(SAVE,'r')
        gamemap = pickle.load(save)
        x = gamemap[0][0].pc[0]
        y = gamemap[0][0].pc[1]
        self.printex(23,0,"Loaded...")
        
    def save(self):
        global gamemap,x,y
        save = open(SAVE,'w')
        gamemap[0][0].pc = [x,y]
        pickle.dump(gamemap, save)
        self.printex(23,0,"Saved...")

    def get_line(self,x1, y1, x2, y2):
        points = []
        issteep = abs(y2-y1) > abs(x2-x1)
        if issteep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        rev = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            rev = True
        deltax = x2 - x1
        deltay = abs(y2-y1)
        error = int(deltax / 2)
        y = y1
        ystep = None
        if y1 < y2:
            ystep = 1
        else:
            ystep = -1
        for x in range(x1, x2 + 1):
            if issteep:
                points.append((y, x))
            else:
                points.append((x, y))
            error -= deltay
            if error < 0:
                y += ystep
                error += deltax
        # Reverse the list if the coordinates were reversed
        if rev:
            points.reverse()
        return points
    def moveMob(self,x,y,mx,my):
        global gamemap
        ucell = gamemap[mx][my]
        gamemap[mx][my] = gamemap[x][y]
        gamemap[x][y] = gamemap[x][y].undercell
        gamemap[mx][my].undercell = ucell
        
    def inLos(self,x1,y1,x,y):
        global gamemap
        b = False
        ret = True
        line = self.get_line(y, x, y1, x1) 
        for j in line:
            if b:
                ret = False
            jx = j[1]
            jy = j[0]
            if not gamemap[jx][jy].type[1]:
                b = True
        else:
            return ret
        
    def aStarLoadMap(self):
        global gamemap
        global mapdata
        mapdata = []
        mapx,mapy = 0,0
        for line in gamemap:
            mapdata.append([])
            mapy = 0
            for cell in line:
                if cell.type[0]:
                    try:
                        mapdata[mapx].append(0)
                    except IndexError:
                        self.debug_message("Err, %d : %d" % (mapx,mapy))
                        self.readkey()
                else:
                    try:
                        mapdata[mapx].append(1)
                    except IndexError:
                        self.debug_message("Err, %d : %d" % (mapx,mapy))
                        self.readkey()
                mapy += 1
            mapx += 1
            

    def aStarPathfind(self,mx,my,yx,yy):
        global mapdata
        (mx1,my1) = AStar.getPath(mx, my, yx, yy, mapdata, MAP_W - 1, MAP_H - 1)
        self.moveMob(mx, my, mx + mx1, my + my1)
        self.debug_message("Moved mob to %d : %d" %(mx + mx1, my + my1))
        self.readkey()