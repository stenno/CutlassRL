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

VERSION = 0.02;

MAP_H=80
MAP_W=24

SAVE = "game.sav"

import sys

from Modules import *

try:
    import curses               # Game will use curses to draw things
except ImportError:
    print "Curses library is missing."
    exit()


screen = curses;
stdscr = screen.initscr()


class Game:                # Main game class
    def __init__(self):
        global screen,stdscr
        """Initializer of Game class.
            Will start curses.
        """
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
        global map
        global x,y
        
        x,y = 5,5

        key = ""
        
        map = []  

        for mapx in xrange(MAP_W+1):
            map.append([])
            for mapy in xrange(MAP_H+1):
                if mapx <= 21 and mapx >= 2 and mapy <= 60 and mapy >= 2:
                    map[mapx].append(cell.Cell(True,True))
                else:
                    map[mapx].append(cell.Cell(False,False))
                    
        self.load()
        x1,y1 = x,y
        fov.fieldOfView(x, y, MAP_W, MAP_H, 5, self.setVisible, self.isBlocking)                        
        self.drawmap()
        self.printex(x,y ,"@", refresh=False)
        self.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)) #DEBUG        
        while 1:
            self.printex(23, 0, " " * 20, refresh = False)
            key = self.readkey()
            if key == "8" or key == "k":
                x1-=1
            elif key == "2" or key == "j":
                x1+=1
            elif key == "4" or key == "h":
                y1-=1
            elif key == "6" or key == "l":
                y1+=1
            elif key == "q":
                self.end()
            elif key == ";":
                self.printex(23, 0, "You")
                screen.curs_set(1)
                self.printex(x, y, "")
                cx1,cy1,cx,cy = x,y,x,y
                while key != "q" or key != ";":
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
                    if not map[cx][cy].explored:
                        type = "Unexplored"
                    elif map[cx][cy].type[0] and not map[cx][cy].type[2]:
                        type = "Ground"
                    elif  not map[cx][cy].type[0] and not map[cx][cy].type[2]:
                        type = "Wall"
                    elif map[cx][cy].type[2]:
                        if map[cx][cy].door:
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
                if map[d[0]][d[1]].type[2]:
                    map[d[0]][d[1]].open()
            elif key == "c":
                d = self.askDirection()
                if map[d[0]][d[1]].type[2]:
                    map[d[0]][d[1]].close()
            else:
                if not map[x][y].type[2]:
                    if key == "7" or key == "y":
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
                    if map[x1][y1].type[2]:
                        x1,y1 = x,y

            if map[x1][y1].type[0]:
                x,y = x1,y1
                self.resetFov()
                fov.fieldOfView(x, y, MAP_W, MAP_H, 5, self.setVisible,\
                                 self.isBlocking)                        
            else:
                if map[x1][y1].type[2]:
                    map[x1][y1].open()
                x1,y1 = x,y
            self.drawmap()
            self.printex(x,y ,"@",refresh=False)
            self.printex(0,0," " * 50,refresh=False)
            self.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)) #DEBUG  

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
        key = sys.stdin.read(1)
        return key
    
    def drawmap(self):
        """Drawmap function.
            Will draw map. Working with fov.
        """
        global map,expmap,screen,stdscr
        mapx,mapy=0,0 
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):
                if not map[mapx][mapy].type[1]:
                    attr = 4;
                    mchar = "#"
                if map[mapx][mapy].type[1]:
                    attr = 1;
                    mchar = "."
                if map[mapx][mapy].type[2]:
                    if not map[mapx][mapy].door:
                        attr = 4;                        
                        mchar = "+"
                    if map[mapx][mapy].door:
                        attr = 4;
                        mchar = "-"
                if mapx <= 22 and mapx >= 1 and mapy <= 61 and mapy >= 1:
                        if map[mapx][mapy].visible:
                            stdscr.attron(screen.A_BOLD)
                            map[mapx][mapy].explored = True
                        else:
                            if not map[mapx][mapy].explored:
                                attr = 1
                                mchar = " " 
                        stdscr.attron(screen.color_pair(attr))
                        self.printex(mapx,mapy,mchar,refresh=False)
                        stdscr.attroff(screen.A_BOLD)
                        stdscr.attroff(screen.color_pair(attr))
        stdscr.refresh()

    def isBlocking(self,x,y):
        global map
        return not map[x][y].type[0]
    
    def setVisible(self,x,y):
        global map
        map[x][y].visible = True

    def resetFov(self):
        global map
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                map[mapx][mapy].visible = False
    def askDirection(self):
        global x,y
        global map
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
        global map,x,y
        save = open(SAVE,'r')
        mapx,mapy=0,0 
        mmap = []
        for mapx in xrange(22):
            mmap.append([])
            for mapy in xrange(62):
                mmap[mapx].append(save.read(1))
        mapx,mapy=0,0
         
        for mapx in xrange(22):
            for mapy in xrange(62):
                if mmap[mapx][mapy] == "2":
                    map[mapx][mapy] = cell.Door(False)
                elif mmap[mapx][mapy] == "3":
                    map[mapx][mapy] = cell.Door(True)
                elif mmap[mapx][mapy] == "0":
                    map[mapx][mapy] = cell.Cell(False,False)
                elif mmap[mapx][mapy] == "1":
                    map[mapx][mapy] = cell.Cell(True,True)
                elif mmap[mapx][mapy] == "4":
                    x,y = mapx,mapy
        save.close()
    def save(self):
        pass