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

VERSION = 0.01;

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
    def main_loop(self):
        """Main loop of game.
            Useless for now.
        """
        x,y = 5,5
        x1,y1 = x,y
        key = ""
        stdscr.addstr(10,10,"Hello, World!")      
        stdscr.addstr(x,y ,"@")
        stdscr.addstr(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)) #DEBUG        
        stdscr.refresh()

        while 1:
            stdscr.refresh()
            stdscr.addstr(x,y ," ")
            key = sys.stdin.read(1)
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
                
            if x1 <= 22 and x1 >= 2:
                x = x1
            else:
                x1 = x
            if y1 <= 60 and y1 >= 2:
                y = y1
            else:
                y1 = y
            stdscr.addstr(10,10,"Hello, World!")      
            stdscr.addstr(x,y ,"@")
            stdscr.addstr(0,0," " * 50) 
            stdscr.addstr(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)) #DEBUG  
            stdscr.refresh() #TODO: add printex() function!

    def end(self):
        """End of game.
            Will reset console and stop curses.
        """
        screen.endwin()
        exit()
    def debug_message(self):
        """Debug message subroutine,
            Will say something like debugmsg: XXX
        """