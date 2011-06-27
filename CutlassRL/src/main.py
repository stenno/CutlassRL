#!/usr/bin/env python
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

# CutlassRL - a roguelike game.

import sys

from Modules.constants import *

import Game  # importing main game library

try:
    if sys.argv[1]:
        name = sys.argv[1]
    else:
        name = None
except IndexError:
    name = None
    
play = Game.Game(name)

try:
    play.main_loop()
except KeyboardInterrupt:
    play.end()

play.end()
del play
