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
        screen.init_pair(2,1,-1) #Red on default

        stdscr.attron(screen.color_pair(1))
        
    def main_loop(self):
        """Main loop of game.
            Drawing things, generating map, playing
        """
        global map
        global x,y
        
        x,y = 5,5
        x1,y1 = x,y

        key = ""
        
        map = []  

        for mapx in xrange(MAP_W+1):
            map.append([])
            for mapy in xrange(MAP_H+1):
                if mapx <= 21 and mapx >= 2 and mapy <= 60 and mapy >= 2:
                    map[mapx].append(cell.Cell(True,True))
                else:
                    map[mapx].append(cell.Cell(False,False))
                    
        fov.fieldOfView(x, y, MAP_W, MAP_H, 5, self.setVisible, self.isBlocking)                        
        map[10][10] = cell.Door(False)
        self.drawmap()
        self.printex(x,y ,"@", refresh=False)
        self.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)) #DEBUG        
        while 1:
            self.printex(x,y ," ",refresh=False)
            key = self.readkey()
            if key == "8":
                x1-=1
            elif key == "2":
                x1+=1
            elif key == "4":
                y1-=1
            elif key == "6":
                y1+=1
            elif key == "7":
                x1-=1
                y1-=1
            elif key == "9":
                x1-=1
                y1+=1
            elif key == "1":
                x1+=1
                y1-=1
            elif key == "3":
                x1+=1
                y1+=1
            elif key == "q":
                self.end()
            elif key == ";":
                pass
            elif key == "o":
                d = self.askDirection()
                if not map[d[0]][d[1]].type[2]:
                    self.printex(0, 23, "There is no door!")
            elif key == "c":
                d = self.askDirection()
            if map[x1][y1].type[0]:
                x,y = x1,y1
                self.resetFov()
                fov.fieldOfView(x, y, MAP_W, MAP_H, 5, self.setVisible,\
                                 self.isBlocking)                        
            else:
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
                    mchar = "#"
                if map[mapx][mapy].type[1]:
                    mchar = "."
                if map[mapx][mapy].type[2]:
                    if not map[mapx][mapy].door:
                        mchar = "+"
                    if map[mapx][mapy].door:
                        mchar = "/"
                if mapx <= 22 and mapx >= 1 and mapy <= 61 and mapy >= 1:
                        if map[mapx][mapy].visible:
                            stdscr.attron(screen.A_BOLD)
                            map[mapx][mapy].explored = True
                        else:
                            if not map[mapx][mapy].explored:
                                mchar = " " 
                        self.printex(mapx,mapy,mchar,refresh=False)
                        stdscr.attroff(screen.A_BOLD)

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
        self.printex(23, 0, "What direction:",refresh = True)
        key = self.readkey()
        if key == "8":
            x1-=1
        elif key == "2":
            x1+=1
        elif key == "4":
            y1-=1
        elif key == "6":
            y1+=1
        elif key == "7":
            x1-=1
            y1-=1
        elif key == "9":
            x1-=1
            y1+=1
        elif key == "1":
            x1+=1
            y1-=1
        elif key == "3":
            x1+=1
            y1+=1
        else:
            self.printex(23, 0, "Wrong direction!",refresh = True)
            return -1
        return x1,y1
