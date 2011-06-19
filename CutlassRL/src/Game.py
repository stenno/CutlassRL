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
    def mainloop(self):
        """Mainloop of game.
            Useless for now.
        """
        while 1:
            try:
                key = sys.stdin.read(1)
            except KeyboardInterrupt:
                self.end()
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