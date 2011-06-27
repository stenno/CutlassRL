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

from Modules.constants import *

import sys
import pickle
import os.path
import random
import gzip

from Modules import AStar
from Modules import cell
from Modules import fov
from Modules import Level
from Modules import IO

class Game:                # Main game class
    def __init__(self):
        global screen,name,wizmode
        global io
        """Initializer of Game class.
            Will start curses.
        """
        io = IO.IO()
        screen = io.retSceen()
        
        io.printex(0, 0, "What is your name? ", 3)
        screen.curs_set(1)
        
        wizmode = False

        try:
            name = screen.getstr()
        except KeyboardInterrupt:
            self.end()
        screen.curs_set(0)
        if name == "Wizard":
            wizmode = True

    def main_loop(self):
        """Main loop of game.
            Drawing things, generating map, playing
        """
        global gamemap,fovblock,turns,wizmode
        global x,y,rx,ry
        global hp,regen,maxhp
        global score,gold
        global kills
        global level
        global name,save
        global io,pstack
        
        maxhp = random.randint(20,40)
        hp = maxhp
        regen = 0

        score = 0
        gold  = 0
        kills = 0

        level = 1
                
        pstack = []
                
        fovblock = False
        
        x,y = 5,5
        rx,ry = 0,0 
        key = ""
        
        save = name + ".sav"
        
        turns = 0
        
        gamemap = []  

        for mapx in xrange(MAP_W+1):
            gamemap.append([])
            for mapy in xrange(MAP_H+1):
                if mapx <= 21 and mapx >= 2 and mapy <= 60 and mapy >= 2:
                    gamemap[mapx].append(cell.Cell(True,True))
                else:
                    gamemap[mapx].append(cell.Cell(False,False))
        if os.path.isfile(save):           
            self.load()
        else:  #level generator
            gen = Level.levGen()
            (gamemap,y,x) = gen.generateLevel(gamemap)
            self.spawnMobs()
        x1,y1 = x,y
        mapchanged = True
        fov.fieldOfView(x, y, MAP_W, MAP_H, 9, self.setVisible, self.isBlocking)                        
        self.drawmap()
        io.printex(x,y ,"@", refresh=False)
        io.printex(2, 63, name, 3)
        if wizmode:
            state = "Wizard"
        else:
            state = "Player"
        io.printex(4, 63, state, 2)
        io.printex(6, 63, " " * 10)            
        hpattr = 3
        if hp == maxhp:
            hpattr = 3
        if hp <= maxhp / 2:
            hpattr = 4
            if hp <= 5:
                hpattr = 2
        io.printex(6, 63, "HP:%d/%d" % (hp, maxhp), hpattr)
        io.printex(8, 63, "T:%d" % (turns))
        io.printex(10, 63, "Score:%d" % (score),3)
        io.printex(12, 63, "Level:%d" % (level),3)
     
        if wizmode:
            io.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)+";T:"\
                         +str(turns)+"; HP:"+str(hp)+"/"+str(maxhp)) #DEBUG 
        else:
            io.printex(0, 0,"")
        turn = False
        while hp >= 1 or wizmode:
            turn = False
            io.printex(23, 0, " " * 60, refresh = False)
            key = io.readkey()
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
                io.printex(0,0,"PRESS '!' TO QUIT:" + " " * 20,2)
                key = io.readkey()
                if key == "!":
                    self.logWrite(name, score, hp, maxhp, VERSION,"Quit",gold,kills)
                    self.end()
            elif key == "m":
                io.printex(23,0,"")
                screen.curs_set(1)
                screen.getstr()
                screen.curs_set(0)
            elif key == "s":
                x,y = x1,y1
                self.save()
            elif key == "r":
                if os.path.isfile(save):           
                    self.load()                    
                    x1,y1 = x,y
                    self.resetFlood()
                    self.floodFill()
                    self.resetFov()
                    self.drawmap()
                    fov.fieldOfView(x, y, MAP_W, MAP_H, 9, self.setVisible,\
                                    self.isBlocking)                        
                io.printex(0,0,"")
            elif key == "z":
                fovblock = not fovblock
            elif key == ";":
                io.printex(23, 0, "You")
                screen.curs_set(1)
                io.printex(x, y, "")
                cx1,cy1,cx,cy = x,y,x,y
                key = ""
                while key != ";":
                    key = io.readkey()
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
                    elif gamemap[cx][cy].stairs:
                        if gamemap[cx][cy].up:
                            type = "Staircase up"
                        else:
                            type = "Staircase down"
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
                    if gamemap[cx][cy].item:
                        type = gamemap[cx][cy].name
                    if [cx,cy] == [x,y]:
                        type = "You"
                    io.printex(23, 0, type)
                    io.printex(cx, cy, "")
                    io.printex(23, 0, " " * 20, refresh = False)                                        
                screen.curs_set(0)
            elif key == "o":
                d = self.askDirection()
                if d:
                    dx = d[0]
                    dy = d[1]
                    if gamemap[dx][dy].door:
                        gamemap[dx][dy].open()
                mapchanged = True
            elif key == "c":
                d = self.askDirection()
                if d:
                    dx = d[0]
                    dy = d[1]
                    if gamemap[dx][dy].door:
                        gamemap[dx][dy].close()
                mapchanged = True
            elif key == "w":
                turn = True
            elif key == ">" or key == "<":
                if gamemap[x][y].stairs:
                    if level == 1 and gamemap[x][y].up:
                        io.printex(0, 0, "PRESS '!' IF YOU WANT TO ESCAPE:",2)
                        key = io.readkey()
                        if key == "!":
                            killer = "Escaped"
                            self.logWrite(name, score, hp, maxhp, VERSION,\
                                          killer,gold,kills)
                            self.end()
                    else:
                        pass
                else:
                    pstack.append((23,0,"There is no stairs!",2))
            else:
                if wizmode and key == "#":
                    key = io.readkey()
                    if key == "x":
                        gamemap[x][y].type = (False,False,False)
                        mapchanged = True
                    elif key == "d":
                        gamemap[x][y] = cell.Door(True)
                        gamemap[x][y].close()
                        mapchanged = True
                    elif key == "v":
                        gamemap[x][y].lit = not gamemap[x][y].lit
                    elif key == "p":
                        d = self.askDirection()
                        rx = d[0]
                        ry = d[1]
                    elif key == "g":
                        gamemap[rx][ry] = cell.Newt("Newt",":",gamemap[rx][ry])
                        mapchanged = True
                    elif key == "!":
                        self.floodFill()
                    elif key == "e":
                        d = self.askDirection()
                        if d:
                            self.moveMob(d[0],d[1], x, y)
                        mapchanged = True
                    elif key == "@":
                        io.debug_message(gamemap[x][y].fval)
                    elif key == "f":
                        d = self.askDirection()
                        if d:
                            dx = d[0]
                            dy = d[1]
                            if gamemap[dx][dy].mob:
                                gamemap[dx][dy] = gamemap[dx][dy].undercell 
                    elif key == "a":
                        self.amnesia()
                        pstack.append((23, 0, \
                            "Thinking of Maud you forget everything else."))
                    elif key == "i":
                        d = self.askDirection()
                        if d:
                            dx = d[0]
                            dy = d[1]
                            if dx <= 21 and dx >= 2 and dy <= 60 and dy >= 2:
                                gamemap[dx][dy] = cell.Cell(True, True)
                        mapchanged = True
                    elif key == "t":
                        ucell = gamemap[x][y]
                        gamemap[x][y] = cell.Newt("Newt",":",ucell)
                        mapchanged = True
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
            else:
                turn = False                        
                if gamemap[x1][y1].door:
                    gamemap[x1][y1].open()
                    turn = True
                    mapchanged = True
                elif gamemap[x1][y1].mob:
                    pstack.append((23, 0, "You hit %s" % gamemap[x1][y1].name\
                                   ,3))
                    gamemap[x1][y1].hp -= random.randint(3,10)
                    turn = True
                x1,y1 = x,y
            if gamemap[x][y].item:
                if gamemap[x][y].name == "Gold":
                    gamemap[x][y] = gamemap[x][y].undercell
                    gold_ = random.randint(4,10)
                    score += gold_
                    gold += gold_
                    pstack.append((23, 0, "You found some gold!",4))
            #mob's turn
            if turn:
                turns += 1
                regen += random.randint(1,5)
                if regen >= 5:
                        regen = 0
                        if hp < maxhp:
                            hp += random.randint(1,3)
                            if hp > maxhp:
                                hp = maxhp
                mapx,mapy = 0,0
                for mapx in xrange(MAP_W - 1): 
                    for mapy in xrange(MAP_H):
                        gamemap[mapx][mapy].has_turn = True
                for mapx in xrange(MAP_W - 1): 
                    for mapy in xrange(MAP_H):
                        if not random.randint(0,1000):
                            if gamemap[mapx][mapy].type[0] and not self.\
                            inLos(x, y, mapx, mapy) and gamemap[mapx][mapy].fval==\
                            gamemap[x][y].fval:
                                gamemap[mapx][mapy] = cell.Newt("Newt",":",gamemap\
                                                                [mapx][mapy])
                        if mapchanged:
                            self.floodFill()
                            mapchanged = False
                        if gamemap[mapx][mapy].mob:
                            if gamemap[mapx][mapy].hp < 1:
                                pstack.append((23, 0, "You kill the %s" %
                                              gamemap[mapx][mapy].name ,3))
                                score += 5
                                kills += 1
                                gamemap[mapx][mapy] = gamemap[mapx][mapy]\
                                .undercell
                                gamemap[mapx][mapy].visible = True
                                if random.choice([True,False] + [False] * 10):
                                    gamemap[mapx][mapy] = cell.item("Gold",\
                                                        "$",gamemap[mapx][mapy])
                                mapchanged = True
                                continue
                            if self.near(x,y,mapx,mapy) and gamemap[mapx]\
                            [mapy].has_turn:
                                gamemap[mapx][mapy].has_turn = False
                                pstack.append((23, 0, "%s hits!" %\
                                        gamemap[mapx][mapy].name,2)   )
                                hp -= random.randint(1,gamemap[mapx][mapy]\
                                                    .damage)
                                if hp <= 0:
                                    killer = gamemap[mapx][mapy].name
                            else:
                                if gamemap[x][y].fval ==\
                                        gamemap[mapx][mapy].undercell.fval and\
                                        self.inLos(x, y, mapx, mapy) and\
                                        self.hasSpaceAround(mapx, mapy) and\
                                        gamemap[mapx][mapy].has_turn:
                                    mx,my = self.aStarPathfind(mapx, mapy, x, y)
                                    if self.near(mapx, mapy,mapx + mx,\
                                                 mapy + my):
                                        self.moveMob(mapx, mapy,mapx + mx,\
                                                     mapy + my)
                                        gamemap[mapx + mx][mapy + my].has_turn\
                                         = False
                                elif gamemap[x][y].fval ==\
                                        gamemap[mapx][mapy].undercell.fval and\
                                        self.hasSpaceAround(mapx, mapy) and\
                                        gamemap[mapx][mapy].has_turn and\
                                        not random.randint(0,10):
                                        mx,my = self.aStarPathfind(mapx,\
                                                                    mapy, x, y)
                                        if self.near(mapx, mapy,mapx + mx,\
                                                     mapy + my):
                                            self.moveMob(mapx, mapy,mapx + mx,\
                                                         mapy + my)
                                            gamemap[mapx + mx][mapy + my].\
                                            has_turn = False
                                else:
                                    mx,my = 0,0
                                    s = 0
                                    if self.hasSpaceAround(mapx, mapy) and\
                                    gamemap[mapx][mapy].has_turn:
                                        while not gamemap[mapx + mx][mapy + my]\
                                        .type[0]:
                                            s += 1
                                            if s >= 5:
                                                mx,my = 0,0
                                                break
                                            mx = random.choice([-1,1])
                                            my = random.choice([-1,1])
                                        self.moveMob(mapx, mapy,mapx + mx,mapy\
                                                    + my)
                                        gamemap[mapx + mx][mapy + my]\
                                        .has_turn = False
            self.resetFov()
            fov.fieldOfView(x, y, MAP_W, MAP_H, 9, self.setVisible,\
                        self.isBlocking)
            self.drawmap()
            io.printex(x,y ,"@",refresh=False)
            io.printex(0,0," " * 50,refresh=False)
            if wizmode:
                io.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)+";T:"\
                             +str(turns)+"; HP:"+str(hp)+"/"+str(maxhp)) #DEBUG 

            io.printex(4, 63, state, 2)
            io.printex(6, 63, " " * 10)            
            hpattr = 3
            if hp == maxhp:
                hpattr = 3
            if hp <= maxhp / 2:
                hpattr = 4
            if hp <= 5:
                hpattr = 2
            io.printex(6, 63, "HP:%d/%d" % (hp, maxhp), hpattr)
            io.printex(8, 63, "T:%d" % (turns))
            io.printex(10, 63, "Score:%d" % (score),3)
            io.printex(12, 63, "Level:%d" % (level),3)
            if len(pstack) > 1:
                for line in pstack:
                    (mx,my,msg,attr) = line
                    io.printex(mx,my,msg + " --More--",attr)
                    io.readkey()
                    io.printex(mx,my," " * 60,5)
            elif len(pstack) == 1:
                    (mx,my,msg,attr) = pstack[0]                
                    io.printex(mx,my,msg,attr)
            pstack = []
        else:
            io.printex(23, 0, "You died! --press any key--",2)
            self.logWrite(name, score, hp, maxhp, VERSION,killer,gold,kills)
            io.readkey()
    def end(self):
        """End of game.
            Will reset console and stop curses.
        """
        screen.endwin()
        sys.exit()
        
    def drawmap(self):  
        """Drawmap function.
            Will draw map. Working with fov.
        """
        global gamemap,screen
        global io
        mapx,mapy=0,0 
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H - 1):
                if mapx <= 22 and mapx >= 1 and mapy <= 61 and mapy >= 1:
                    if gamemap[mapx][mapy].lit and not gamemap[mapx][mapy].mob:
                        if self.inLos(mapx, mapy, x, y):
                            gamemap[mapx][mapy].visible = True
                        if gamemap[mapx][mapy].type[0]:
                            for x2 in xrange(-2,2):
                                for y2 in xrange(-2,2):
                                    if self.near(mapx,mapy,mapx + x2,mapy + y2):
                                        if gamemap[mapx][mapy].type[0]:
                                            if not gamemap[mapx+x2]\
                                            [mapy+y2].type[0]:
                                                if self.inLos(x, y, mapx, mapy)\
                                                 and (x2,y2) != (0,0) and not\
                                                  gamemap[mapx + x2]\
                                                  [mapy + y2].type[0]:
                                                    gamemap[mapx+x2][mapy+y2]\
                                                    .lit = True
                                                else:
                                                    gamemap[mapx+x2][mapy+y2]\
                                                    .lit = False
                    if gamemap[mapx][mapy].visible:
                        gamemap[mapx][mapy].explored = True
                        if gamemap[mapx][mapy].mob:
                            gamemap[mapx][mapy].undercell.explored = True
                            gamemap[mapx][mapy].explored = False
                        screen.attron(screen.A_BOLD)
                        if gamemap[mapx][mapy].type[0] and not gamemap[mapx]\
                        [mapy].item:
                            color = 1
                        else:
                            color = gamemap[mapx][mapy].color
                        io.printex(mapx, mapy, gamemap[mapx][mapy].char(),\
                           color,False)
                        screen.attroff(screen.A_BOLD)
                    elif gamemap[mapx][mapy].explored:
                        screen.attron(screen.A_DIM)
                        if gamemap[mapx][mapy].mob and not\
                         gamemap[mapx][mapy].visible:
                            if gamemap[mapx][mapy].undercell.door:
                                io.printex(mapx, mapy,"-",5,False)
                            else:
                                io.printex(mapx, mapy,".",5,False)                               
                        else: 
                            io.printex(mapx, mapy, gamemap[mapx][mapy].\
                                         char(),5,False)
                    elif gamemap[mapx][mapy].mob:
                        if gamemap[mapx][mapy].undercell.explored == True:
                            io.printex(mapx, mapy, gamemap[mapx][mapy].\
                                         undercell.char(),5,False)
                        if gamemap[mapx][mapy].lit:
                            if self.inLos(mapx, mapy, x, y):
                                screen.attron(screen.A_BOLD)
                                io.printex(mapx, mapy, gamemap[mapx][mapy]\
                                    .char(),gamemap[mapx][mapy].color,False)
                                screen.attroff(screen.A_BOLD)
                                
                    else:
                        io.printex(mapx, mapy, " ",5,False)
                        screen.attroff(screen.A_DIM)
                        
        screen.refresh()

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

    def resetFlood(self):
        global gamemap
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                gamemap[mapx][mapy].fval = 0

    def amnesia(self):
        global gamemap
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                gamemap[mapx][mapy].explored = False
 
    def askDirection(self):
        global x,y
        global io
        x1,y1 = x,y
        io.printex(23, 0, "What direction:")
        key = io.readkey()
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
            io.printex(23, 0, "Wrong direction!")
            return False
        return x1,y1
    
    def load(self):
        global gamemap,x,y,hp,turns,fovblock,rx,ry,save,wizmode
        global gold,kills,score
        saved = gzip.open(save, 'rb')
        gamemap = pickle.load(saved)
        x = gamemap[0][0].pc[0]
        y = gamemap[0][0].pc[1]
        rx = gamemap[0][0].sc[0]
        ry = gamemap[0][0].sc[1]
        gold = gamemap[0][0].gold
        kills = gamemap[0][0].kills
        score = gamemap[0][0].score
        fovblock = gamemap[0][0].fov
        turns = gamemap[0][0].turns
        hp = gamemap[0][0].hp
        pstack.append((23,0,"Loaded...",1))
        if not wizmode:
            os.remove(save)
        
    def save(self):
        global gamemap,x,y,hp,turns,fovblock,rx,ry,save,wizmode
        global gold,kills,score
        saved = gzip.open(save, 'wb')
        gamemap[0][0].gold = gold
        gamemap[0][0].kills = kills
        gamemap[0][0].score = score
        gamemap[0][0].pc = [x,y]
        gamemap[0][0].sc = [rx,ry]
        gamemap[0][0].fov = fovblock
        gamemap[0][0].hp = hp
        gamemap[0][0].turns = turns
        pickle.dump(gamemap, saved)
        pstack.append((23,0,"Saved...",1))
        if not wizmode:
            self.end()

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
        if self.near(x, y, mx, my):
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
        if len(line) <= 40:
            return ret

    def aStarPathfind(self,mx,my,yx,yy):
        global gamemap
        (mx1,my1) = AStar.getPath(mx, my, yx, yy, gamemap, MAP_W, MAP_H)
        if (mx1,my1) != (0,0):
            return mx1,my1
        else:
            return 0,0
            
    def near(self,x1,y1,x2,y2):
        if x1 - x2 >= -1 and x1 - x2 <= 1 and\
                 y1 - y2 >= -1 and y1 - y2 <= 1:
            return True
        else:
            return False
    def hasSpaceAround(self,x,y):
        global gamemap
        c = 0
        for x2 in xrange(-2,2):
            for y2 in xrange(-2,2):
                if self.near(x, y,x + x2,y + y2):
                    if not gamemap[x + x2][y + y2].type[0]:
                        c += 1
        if c >= 8:
            return False
        else:
            return True
    def floodFill(self):
        global gamemap
        x = 1
        self.resetFlood()
        for mapx in xrange(MAP_W - 1,0,-1): 
            for mapy in xrange(MAP_H,0,-1):
                if gamemap[mapx][mapy].type[0] and gamemap[mapx][mapy].fval\
                 == 0:
                    xl,yl = mapx,mapy
                    self.flood(xl,yl,x,0)
                    x += 1
    def flood(self,x,y,v,d):
        global gamemap
        sys.setrecursionlimit(2000)
        if gamemap[x][y].type[0] == False or gamemap[x][y].fval  == v or\
        gamemap[x][y].fval != d:
            return  0
        if gamemap[x][y].mob:
            gamemap[x][y].undercell.fval = v
        gamemap[x][y].fval = v
        self.flood(x + 1,y,v,d)
        self.flood(x + 1,y + 1,v,d)
        self.flood(x - 1,y,v,d)
        self.flood(x - 1,y - 1,v,d)
        self.flood(x,y + 1,v,d)
        self.flood(x,y - 1,v,d)
        self.flood(x + 1,y - 1,v,d)
        self.flood(x - 1,y + 1,v,d)
        return
    def spawnMobs(self):
        global gamemap,x,y
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                if not random.randint(0,1000):
                    if gamemap[mapx][mapy].type[0] and not self.\
                    inLos(x, y, mapx, mapy) and gamemap[mapx][mapy].fval==\
                    gamemap[x][y].fval:
                        gamemap[mapx][mapy] = cell.Newt("Newt",":",gamemap\
                                                        [mapx][mapy])
    def logWrite(self,name,score,hp,maxhp,version,death,gold,kills):
        global wizmode
        if not wizmode:
            log = open("mainlog.log","a")
            log.write(("version=%f:name=%s:score=%d:hp=%d:maxhp=%d:killer=%s:"
                    + "gold=%d:kills=%d\n") %
                      (version,name,score,hp,maxhp,death,gold,kills))
#TODO:
# plot
# wilderness/town
# npc's
# more items
# more mobs
# items stats
# ac
# dice based rng
# traps
# monster hit messages
# like Newt bittes! (not hits!)

#BUGS:
# No bugs?

#
#  __           _       _  _    ___    
# /        _/_  /  _   /  /   /   /  /
#/   /   / /   /  / // |  \  /___/  /
#\__ \__/ /_  /_ /_// _/ _/ /  \   /____