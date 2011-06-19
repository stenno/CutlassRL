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

SOLID       = 0
TRANSPARENT = 1
WALKABLE    = 2
EXPLORED    = 3 

import sys
try:
    import libtcodpy as libtcod # Loading libtcod library
except ImportError:
    print "Libtcod is missing."
    exit()
try:
    import curses               # Game will use curses to draw things
    screen = curses;
except ImportError:
    print "Curses library is missing."
    exit()
stdscr = screen.initscr()
class Game:                # Main game class
    def __init__(self):
        """Initializer of Game class.
            Will start curses.
        """
        screen.curs_set(0)
        screen.cbreak()
        screen.start_color()
        screen.use_default_colors()
        stdscr.keypad(1)
        
        #Color pairs
        screen.init_pair(1,1,-1) #Red on default

    def main_loop(self):
        """Main loop of game.
            Drawing things, generating map, playing
        """
        global map
        global tcodmap
        global x,y
        x,y = 5,5
        x1,y1 = x,y
        key = ""
        map = []  
        tcodmap = libtcod.map_new(MAP_H,MAP_W)
        for mapx in xrange(MAP_W+1):
            map.append([])
            for mapy in xrange(MAP_H+1):
                r = SOLID
                if mapx <= 21 and mapx >= 2 and mapy <= 60 and mapy >= 2:
                    r = TRANSPARENT + WALKABLE
                map[mapx].append(r)
                if r == SOLID:
                    libtcod.map_set_properties(tcodmap,mapy,mapx,False,False)
                else:
                    libtcod.map_set_properties(tcodmap,mapy,mapx,True,True)
        
        libtcod.map_compute_fov(tcodmap,y,x,5,True,\
                                libtcod.FOV_SHADOW)                       
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
            if map[x1][y1] != SOLID:
                x,y = x1,y1
                libtcod.map_compute_fov(tcodmap,y,x,5,True,\
                                        libtcod.FOV_SHADOW)                
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
        global map 
        mapx,mapy=0,0 
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):
                if map[mapx][mapy] == SOLID:
                    mchar = "#"
                if map[mapx][mapy] == TRANSPARENT + WALKABLE:
                    mchar = "."
                if mapx <= 22 and mapx >= 1 and mapy <= 61 and mapy >= 1:
                    if not(libtcod.map_is_in_fov(tcodmap, mapy, mapx)):
                        mchar = " "
                    self.printex(mapx,mapy,mchar,refresh=False)