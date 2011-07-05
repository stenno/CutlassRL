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
#    Copyright (c) init

from Modules.Constants import *  #Import constants

import sys
import cPickle  #Used for saves
import os.path
import random
import gzip
import copy
import math

from Modules import AStar  #Pathfinding
from Modules import Cell   #Cell class
from Modules import Fov    #FOV algorithm
from Modules import Level  #Level generation
from Modules import IO     #Input/Output
from Modules import You    #Character.


class Game:                # Main game class
    def __init__(self,yname = None):  #yname = Your name
        """Initializer of Game class.
            Will start curses and ask for name.
        """
        global screen,name,wizmode,p1
        global io                      #For input/output
        io = IO.IO()
        screen = io.retSceen()

        if yname and yname.isalnum():
            name = yname
        else:
            name = ""
        screen.curs_set(1)
        wizmode = False
        while len(name) < 3:
            io.printex(0, 0, "What is your name? ", 3)
            try:
                screen.echo()
                name = screen.getstr()
                if not name.isalnum():
                    self.end()
            except KeyboardInterrupt:
                self.end()
        screen.noecho()
        screen.curs_set(0)
        if name == "Wizard":
            wizmode = True
        p1 = You.Player(name)

    def mainLoop(self):
        """Main loop of game.
            Drawing things, generating map, playing
        """
        global gamemap,fovblock,turns,wizmode,editmode
        global x,y,rx,ry,x1,y1,turn,state
        global hp,regen,maxhp,key,mstack
        global score,gold
        global kills, killer
        global level,mapchanged
        global name,save,p1,frad,mnext,addmsg
        global io
        global levs
        global chars
                
        maxhp = random.randint(20,40)  #Max hp always random
        hp = maxhp                     #Hp is at max
        regen = 0

        score = 0                       #Zero score
        gold  = 0
        kills = 0
        frad = 5

        mstack = []

        editmode = False
        addmsg = True
        
        mnext = 0

        chars = []
        
        level = 1                       #Starting level
                

        fovblock = False   #Fov is not blocked
        
        x,y = 5,5
        rx,ry = 0,0 
        key = None   #No key is pressed
        
        save = name + ".sav"
        
        turns = 0
        
        gamemap = []  

        moremobs = True
        mc = 0

        for mapx in xrange(MAP_W+1):
            gamemap.append([])
            for mapy in xrange(MAP_H+1):
                if mapx <= 20 and mapx >= 2 and mapy <= 60 and mapy >= 2:
                    gamemap[mapx].append(Cell.Cell(True,True))
                else:
                    gamemap[mapx].append(Cell.Cell(False,False))

        levs = [None,None]
        if os.path.isfile(save):           
            self.load()  #Load savefile
            levs[level] = copy.deepcopy(gamemap)
        else:  #level generator
            gen = Level.levGen()
            (gamemap,y,x) = gen.generateLevel(gamemap)
            self.spawnMobs()
        levs[0] = copy.deepcopy(gamemap)
        x1,y1 = x,y
        mapchanged = True #Map has been changed
        # Calculate fov
        self.resetFov()
        Fov.fieldOfView(x, y, MAP_W, MAP_H, frad, self.setVisible,\
                         self.isBlocking)                        
        self.drawMap()
        io.printex(x,y ,p1.char(), refresh=False) #Draw player
        io.printex(2, 63, name, 3)
        if wizmode:
            state = "Wizard"
        else:
            state = "Player"
        io.printex(4, 63, state, 2)
        io.printex(6, 63, " " * 10)            

        hpattr = GREEN
        if hp == maxhp:
            hpattr = GREEN
        if hp <= maxhp / 2:
            hpattr = YELLOW
            if hp <= 5:
                hpattr = RED

        io.printex(6, 63, "HP:%d/%d" % (hp, maxhp), hpattr)
        io.printex(8, 63, "T:%d" % (turns))
        io.printex(10, 63, "Score:%d" % (score),GREEN)
        io.printex(12, 63, "Level:%d" % (level),GREEN)
     
        if wizmode:
            io.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)+";T:"\
                         +str(turns)+"; HP:"+str(hp)+"/"+str(maxhp)) #For debug 
        else:
            io.printex(0, 0,"")
        turn = False
        p1.energy += p1.speed
        while hp >= 1 or wizmode:
            mapx,mapy = 0,0               #Start from first tile
            for mapx in xrange(MAP_W - 1):#And move to end of map 
                for mapy in xrange(MAP_H):
                    if gamemap[mapx][mapy].mob:
                        gamemap[mapx][mapy].has_turn = True #Give a turn to
                                                            # monster
            p1.energy += p1.speed
            if turn:
                turns += 1
                regen += random.randint(1,5)
                if regen >= 15:
                    regen = 0
                    if hp < maxhp:
                        hp += random.randint(1,3)
                        if hp > maxhp:
                            hp = maxhp
                    
            while p1.energy > 0:
                if key != -1 and key != None:
                    self.messageStack()
                if turn or mapchanged:
                    io.printex(0,0," " * 60,refresh=False)
                    if wizmode:
                        io.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+\
                            str(key)+";T:"+str(turns)+"; HP:"+str(hp)+"/"+\
                            str(maxhp),refresh=False) #DEBUG 
                    io.printex(4, 63, state, 2,refresh=False)
                    io.printex(6, 63, " " * 10,refresh=False)            
                    hpattr = GREEN
                    if hp == maxhp:
                        hpattr = GREEN
                    if hp <= maxhp / 2:
                        hpattr = YELLOW
                    if hp <= 5:
                        hpattr = RED
                    io.printex(6, 63, "HP:%d/%d" % (hp, maxhp), hpattr,refresh=False)
                    io.printex(8, 63, "T:%d" % (turns),refresh=False)
                    io.printex(10, 63, "Score:%d" % (score),3,refresh=False)
                    io.printex(12, 63, "Level:%d" % (level),3)
                    self.resetFov()
                    Fov.fieldOfView(x, y, MAP_W, MAP_H, frad, self.setVisible,\
                            self.isBlocking)                        
                    mnext = 0
                    self.drawMap()
                    io.printex(x,y ,p1.char())
                key = self.playerTurn() #Player's turn
            if turn:
                mc = 0
                mobs = []
                if mapchanged:
                    self.resetFlood()
                    self.floodFill()
                    mapchanged = False
                best_energy = 0
                for mapx in xrange(MAP_W - 1):
                    for mapy in xrange(MAP_H): 
                        if gamemap[mapx][mapy].mob:
                            gamemap[mapx][mapy].energy += gamemap[mapx]\
                            [mapy].speed
                            mobs.append((mapx,mapy))     
                            if gamemap[mapx][mapy].energy > best_energy:
                                best_energy = gamemap[mapx][mapy].energy
                            mc += 1
                            if mc >= MAX_MOBS:
                                moremobs= False
                            else:
                                moremobs = True
                        #TODO: Generate RANDOM monsters.
                        if not random.randint(0,10000) and moremobs:
                            if gamemap[mapx][mapy].type[0] and not gamemap\
                            [mapx][mapy].visible and gamemap[mapx][mapy]\
                            .fval==gamemap[x][y].fval: 
                                gamemap[mapx][mapy] = Cell.Newt("Newt",\
                                                ":",gamemap[mapx][mapy]) 
                                mobs.append((mapx,mapy))
                i = 0
                mapx,mapy = 0,0
                for lnum in xrange(level - 4,level + 6):
                    if lnum >= len(levs) or lnum <= len(levs):
                        continue
                    gmap = levs[lnum]
                    mc = 0
                    if gmap != None:
                        mmx = random.randint(0,MAP_W)
                        mmy = random.randint(0,MAP_H- 1)
                        if  moremobs and gmap[mmx][mmy].type[0] and\
                         not random.randint(0,50) :
                                gmap[mmx][mmy] = Cell.Newt("Newt",\
                                                ":",gmap[mmx][mmy]) 
                                mc += 1
                        for mapx in xrange(MAP_W - 1):
                            for mapy in xrange(MAP_H): 
                                if gmap[mapx][mapy].mob:
                                    mc += 1
                                if mc >= MAX_MOBS:
                                    moremobs= False
                                else:
                                    moremobs = True
                                if gmap[mapx][mapy].mob and not\
                                 random.randint(0,5):
                                    if self.hasSpaceAround(mapx,mapy):
                                        mx,my = 0,0
                                        list = []
                                        for x2 in xrange(-1,2):
                                            for y2 in xrange(-1,2):
                                                if gmap[mapx + x2]\
                                                [mapy + y2].type[0]:
                                                    list.append((x2,y2))
                                        move = random.choice(list)
                                        mx,my = move
                                        if (mx,my) != (0,0):
                                            self.moveMob(mapx, mapy,mapx +\
                                                          mx,mapy+ my,gamemap)
                while i <= best_energy and best_energy != 0:
                    id = 0
                    for mob in mobs:
                        mapx = mob[0]
                        mapy = mob[1]
                        if gamemap[mapx][mapy].mob:
                            if gamemap[mapx][mapy].energy > 0:
                                if self.hasSpaceAround(mapx,mapy):
                                    (mvx,mvy) = self.mobTurn(mapx,mapy,gamemap)
                                    mobs[id] = (mvx,mvy) 
                        id += 1
                    i += 1        
        else:
            io.printex(22, 0, " " * 100,2)
            io.printex(22, 0, "You died! --press any key--",2)
            io.readkey()
            # Write to log
            self.logWrite(name, score, hp, maxhp, VERSION,killer,gold,kills)
            io.readkey()
    def end(self):
        """End of game.
            Will reset console and stop curses.
        """
        screen.endwin()
        sys.exit()
        
    def drawMap(self):  
        """Drawmap function.
            Will draw map. Working with fov.
        """
        global gamemap,screen
        global io
        mapx,mapy=0,0 
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H - 1):
                #If cell is in map range
                if gamemap[mapx][mapy] != None and(mapx <= 22 and mapx >= 1\
                            and mapy <= 61 and mapy >= 1) and gamemap\
                            [mapx][mapy].changed:
                    gamemap[mapx][mapy].changed = False
                    if gamemap[mapx][mapy].lit:
                        if gamemap[mapx][mapy].item or\
                         gamemap[mapx][mapy].boulder:
                            gamemap[mapx][mapy].lit = gamemap[mapx][mapy].\
                            undercell.lit
                    if gamemap[mapx][mapy].lit and not gamemap[mapx][mapy].\
                    mob:
                        if self.inLos(mapx, mapy, x, y):
                            gamemap[mapx][mapy].visible = True
                    if gamemap[mapx][mapy].visible: #Visible always explored
                        gamemap[mapx][mapy].explored = True
                        if gamemap[mapx][mapy].mob:
                            gamemap[mapx][mapy].undercell.explored = True
                            gamemap[mapx][mapy].explored = False
                        if gamemap[mapx][mapy].type[0] and gamemap[mapx]\
                        [mapy].plain_cell:
                            if self.distance(x, y, mapx, mapy) <= frad / 2:
                                screen.attron(screen.A_BOLD) #Visible is bold
                                color = YELLOW
                            elif self.distance(x, y, mapx, mapy) <= frad / 1.3:
                                screen.attron(screen.A_BOLD) #Visible is bold
                                color = 1
                            else:
                                screen.attron(screen.A_DIM) #Visible is bold
                                color = 1
                                
                        else:
                            screen.attron(screen.A_BOLD) #Visible is bold
                            color = gamemap[mapx][mapy].color #Normal color
                                                                # of cell
                        io.printex(mapx, mapy, gamemap[mapx][mapy].char(),\
                           color,False) #Print cell.
                        screen.attroff(screen.A_BOLD)
                    elif gamemap[mapx][mapy].explored:
                        screen.attron(screen.A_DIM) #Explored is dim
                        if gamemap[mapx][mapy].mob and not\
                         gamemap[mapx][mapy].visible:
                            if gamemap[mapx][mapy].undercell.door:
                                io.printex(mapx, mapy,"-",5,False)
                            else:
                                io.printex(mapx, mapy,".",5,False)                               
                        else:
                            io.printex(mapx, mapy, gamemap[mapx][mapy].\
                                         char(),5,False)
                    elif gamemap[mapx][mapy].mob: #For monsters.
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
                        screen.attroff(screen.A_DIM)
                if chars and not gamemap[mapx][mapy].explored:
                    self.drawChar(mapx, mapy, level)
        screen.refresh()

    def isBlocking(self,x,y):
        """Checks if tile is blocking FOV"""
        global gamemap
        return not gamemap[x][y].type[1]

    def setVisible(self,sx,sy):
        """Sets tile as visible"""
        global gamemap,fovblock,x,y,frad
        if not gamemap[sx][sy].visible:
            if self.inCircle(x, y, frad + 1, sx, sy):
                gamemap[sx][sy].visible = not fovblock
                gamemap[sx][sy].changed = True
        if gamemap[sx][sy].mob:
                gamemap[sx][sy].changed = True

    def resetFov(self):
        """Resets FOV"""
        global gamemap
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):
                if gamemap[mapx][mapy].visible:        
                    gamemap[mapx][mapy].visible = False
                    gamemap[mapx][mapy].changed = True 
                if gamemap[mapx][mapy].mob:
                        gamemap[mapx][mapy].changed = True

    def resetFlood(self):
        """Resets flood fill"""
        global gamemap
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                gamemap[mapx][mapy].fval = 0

    def amnesia(self):
        """Reset explored cells"""
        global gamemap
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                gamemap[mapx][mapy].explored = False

    def askDirection(self):
        """Asks direction"""
        global x,y
        global io
        x1,y1 = x,y
        io.printex(23, 0, " " * 60)        
        io.printex(23, 0, "What direction:")
        key = io.readkey()
        if key == "8" or key == "k" or key == 259:
            x1-=1
        elif key == "2" or key == "j" or key == 258:
            x1+=1
        elif key == "4" or key == "h" or key == 260:
            y1-=1
        elif key == "6" or key == "l" or key == 261:
            y1+=1
        elif key == "7" or key == "y" or key == 262:
            x1-=1
            y1-=1
        elif key == "9" or key == "u" or key == 339:
            x1-=1
            y1+=1
        elif key == "1" or key == "b" or key == 360:
            x1+=1
            y1-=1
        elif key == "3" or key == "n" or key == 338:
            x1+=1
            y1+=1
        else:
            io.printex(22, 0, "Wrong direction!")
            return False, False
        return x1,y1
    def load(self):
        """Load game from save"""
        global gamemap,x,y,hp,turns,fovblock,rx,ry,save,wizmode,mstack
        global gold,kills,score,levs,level,regen,maxhp,frad,chars
        saved = gzip.open(save,"rb",-1)
        (level,info,gamemap,levs) = cPickle.load(saved)
        (gold,kills,score,x,y,rx,ry,fovblock,hp,maxhp,turns,regen,frad,chars,\
         mstack) = info
        saved.close()
        self.addMsg("Loaded...",1)
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):
                gamemap[mapx][mapy].changed = True
        if not wizmode:
            os.remove(save)
        
    def save(self):
        """Save game"""
        global gamemap,x,y,hp,turns,fovblock,rx,ry,save,wizmode
        global gold,kills,score,levs,level,regen,maxhp,frad,chars,mstack
        saved = gzip.open(save,"wb",-1)
        info = (gold,kills,score,x,y,rx,ry,fovblock,hp,maxhp,turns,regen,frad\
                ,chars,mstack)
        cPickle.dump((level,info,gamemap,levs), saved,2)
        self.addMsg("Saved...",1)
        if not wizmode:
            saved.close()
            self.end()    

    def getLine(self,x1, y1, x2, y2):
        """Bresenham's line algorithm"""
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

    def moveMob(self,x,y,mx,my,gamemap):
        """Moves mob"""
        if gamemap[mx][my].type[0] or gamemap[x][y].phasing:
            ucell = gamemap[mx][my]
            gamemap[mx][my] = gamemap[x][y]
            gamemap[x][y] = gamemap[x][y].undercell
            gamemap[mx][my].undercell = ucell
            gamemap[mx][my].lit = gamemap[mx][my].undercell.lit
            gamemap[mx][my].changed = True
            gamemap[x][y].changed = True
        
    def inLos(self,x1,y1,x,y):
        """Checks if point is in LOS"""
        global gamemap
        b = False
        ret = True
        line = self.getLine(y, x, y1, x1) 
        for j in line:
            if b:
                ret = False
            jx = j[1]
            jy = j[0]
            if not gamemap[jx][jy].type[1]:
                b = True
        gamemap[x1][y1].changed = True
        return ret

    def aStarPathfind(self,mx,my,yx,yy):
        """Pathfinding for monsters"""
        global gamemap
        (mx1,my1) = AStar.getPath(mx, my, yx, yy, gamemap, MAP_W, MAP_H)
        if (mx1,my1) == (9001, 9001):
            self.floodFill() 
            mx1, my1 = 0,0
        return mx1,my1
            

    def floodFill(self):
        """Floodfills map
            for reachability test"""
        global gamemap
        x = 1
        for mapx in xrange(MAP_W - 1,0,-1): 
            for mapy in xrange(MAP_H,0,-1):
                if not gamemap[mapx][mapy].type[0]:
                    gamemap[mapx][mapy].fval = -1
                if gamemap[mapx][mapy].type[0] and gamemap[mapx][mapy].fval\
                 == 0:
                    xl,yl = mapx,mapy
                    self.flood(xl,yl,0,x)
                    x += 1

    def flood(self,x,y,old,new):
        global gamemap
        seed_pos = (x,y)
        if old == new:
            return
        stack = []
    
        w, h = MAP_W, MAP_H
        max_x = max_y = 0
        min_x = w
        min_y = h
        stack.append(seed_pos)
        iterations = 0
        while(stack):
            iterations += 1
            x,y = stack.pop()
            y1 = y
            while y1 >= 0 and gamemap[x][y1].fval == old:
                y1 -= 1
            y1 += 1
            spanLeft = spanRight = False
            inner_iterations = 0
            while(y1 < h and gamemap[x][y1].fval == old):
                inner_iterations += 1
                gamemap[x][y1].fval = new
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y1)
                max_y = max(max_y, y1)
                if not spanLeft and x > 0 and gamemap[x - 1][y1].fval == old:
                    stack.append((x - 1, y1))
                    spanLeft = True
                elif spanLeft and x > 0 and gamemap[x - 1][y1].fval != old:
                    spanLeft = False
                if not spanRight and x < w - 1 and gamemap[x + 1][y1].fval ==\
                 old:
                    stack.append((x + 1, y1))
                    spanRight = True
                elif spanRight and x < w - 1 and gamemap[x + 1][y1].fval != old:
                    spanRight = False
                y1 += 1

    def spawnMobs(self):
        """Spawn mobs"""
        global gamemap,x,y
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):        
                if not random.randint(0,10000):
                    if gamemap[mapx][mapy].type[0] and not self.\
                    inLos(x, y, mapx, mapy) and gamemap[mapx][mapy].fval==\
                    gamemap[x][y].fval:
                        gamemap[mapx][mapy] = Cell.Newt("Newt",":",gamemap\
                                                        [mapx][mapy])
    def logWrite(self,name,score,hp,maxhp,version,death,gold,kills):
        """Write text to log"""
        global wizmode,levs,level
        mlev = 0
        for lev in levs:
            if lev == None:
                break
            mlev += 1
        if not wizmode:
            log = open("mainlog.log","a")
            log.write(("version=%1.2f:name=%s:score=%d:hp=%d:maxhp=%d:"
                    +"killer=%s:gold=%d:kills=%d:maxdlvl=%s:dlvl=%s\n") %
                      (version,name,score,hp,maxhp,death,gold,kills,mlev,level))
    def setChar(self,levl,x,y,char,attr):
        global chars
        for item in chars:
            if (item[1],item[2]) == (x,y):
                return False
        chars.append((level,x,y,char,attr))
                     
    def drawChar(self,x,y,level):
        global chars
        for char in chars:
            if (char[0],char[1],char[2]) == (level,x,y):
                io.printex(x,y,char[3],char[4],False)

    def mobTurn(self,mapx,mapy,gamemap):
        global levs,hp,killer
        ret = (mapx,mapy)
        if self.near(x,y,mapx,mapy):
                self.addMsg("%s hits!" %\
                        gamemap[mapx][mapy].name,2)
                hp -= random.randint(1,gamemap[mapx][mapy]\
                                    .damage)
                gamemap[mapx][mapy].energy -= 80
                if hp <= 0:
                    #Mob killed you.
                    killer = gamemap[mapx][mapy].name
        else:
            if gamemap[x][y].fval ==\
                gamemap[mapx][mapy].undercell.fval and\
                self.canSeeYou(mapx,mapy):
                    mx,my = self.aStarPathfind(mapx, mapy,\
                                                x, y)
                    if (mx,my) == (0,0):
                        self.rmove(mapx,mapy)
                        return (mapx + mx, mapy + my)
                    self.moveMob(mapx, mapy,mapx + mx,\
                                    mapy + my,gamemap)
                    if (mx,my) != (0,0):
                        gamemap[mapx + mx][mapy + my].\
                        energy -= 100
                    ret = (mapx + mx, mapy + my)
            elif gamemap[x][y].fval ==\
                    gamemap[mapx][mapy].undercell.fval and\
                    not random.randint(0,10):
                    mx,my = self.aStarPathfind(mapx,\
                                                mapy, x, y)
                    if (mx,my) == (0,0):
                        self.rmove(mapx,mapy)
                        return (mapx + mx, mapy + my)
                    self.moveMob(mapx, mapy,mapx + mx,\
                                            mapy + my,gamemap)
                    if (mx,my) != (0,0):
                        gamemap[mapx + mx][mapy + my].\
                        energy -= 110
                    ret = (mapx + mx, mapy + my)
                #Move randomly.
            elif self.hasSpaceAround(mapx,mapy):
                mx,my = 0,0
                list = [(0,0)]
                for x2 in xrange(-1,2):
                    for y2 in xrange(-1,2):
                        if gamemap[mapx + x2][mapy + y2].type[0]:
                            list.append((x2,y2))
                move = random.choice(list)
                mx,my = move
                if (mx,my) != (0,0):
                    self.moveMob(mapx, mapy,mapx +\
                                  mx,mapy+ my,gamemap)
                    gamemap[mapx + mx][mapy + my].\
                    energy -= 115
                ret = (mapx + mx, mapy + my)
        return ret

    def invMenu(self): #Shows your inventory and returns selected thing.
        global screen,gamemap,p1,x,y,state
        key = -1
        sx,sy = 4,4
        max = 4
        c = 1
        gold = 0
        while key != "q":
            screen.clear()
            for i in range(0,23):
                io.printex(i,0,'#' + " " * 10 + "#" + " " * 67 + "#",BLUE)
            io.printex(0,0,'#' * 80,BLUE)
            io.printex(23,0,'#' * 80,BLUE)
            io.printex(0,34,"[Inventory]",YELLOW)
            io.printex(sx,1,"[",RED)
            io.printex(sy,10,"]",RED)
            io.printex(4,4,"Armor",GREEN)
            io.printex(6,4,"Weapns",GREEN)
            io.printex(8,4,"Sack",GREEN)
            io.printex(10,4,"Gold",GREEN)
            gold = 0
            for item in p1.cont[0].inv:
                if item.item:
                    if item.name == "Gold":
                        gold += item.howmany
            if c == 4:
                io.printex(4,16,"You have %d gold." % gold,YELLOW)
            key = io.readkey()
            if key == "j" or key == "8":
                if not (c - 1) < 1:
                    sx -= 2
                    sy -= 2
                    c -= 1
            elif key == "k" or key == "2":
                if not (c + 1) > max:
                    sx += 2
                    sy += 2
                    c += 1

        screen.clear()
        for line in gamemap:
            for cell in line:
                cell.changed = True
        self.drawMap()
        io.printex(0,0," " * 60,refresh=False)
        if wizmode:
            io.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+\
                str(key)+";T:"+str(turns)+"; HP:"+str(hp)+"/"+\
                str(maxhp),refresh=False) #DEBUG 
        io.printex(4, 63, state, 2,refresh=False)
        io.printex(6, 63, " " * 10,refresh=False)            
        hpattr = GREEN
        if hp == maxhp:
            hpattr = GREEN
        if hp <= maxhp / 2:
            hpattr = YELLOW
        if hp <= 5:
            hpattr = RED
        io.printex(6, 63, "HP:%d/%d" % (hp, maxhp), hpattr,refresh=False)
        io.printex(8, 63, "T:%d" % (turns),refresh=False)
        io.printex(10, 63, "Score:%d" % (score),3,refresh=False)
        io.printex(12, 63, "Level:%d" % (level),3)
        self.resetFov()
        Fov.fieldOfView(x, y, MAP_W, MAP_H, frad, self.setVisible,\
                self.isBlocking)                        
        self.drawMap()
        io.printex(2, 63, name, 3)
        io.printex(x,y,p1.char(),1)

    def playerTurn(self):
        global x,y,gamemap,killer,x1,y1,mstack
        global turn,turn2,p1,level,score,kills,gold,mapchanged
        global rx,ry,fovblock,editmode,regen,hp,maxhp
        turn = False
        key = io.rkey()
        if key == "8" or key == "k" or key == 259:
            x1-=1
            turn = True
        elif key == "2" or key == "j" or key == 258:
            x1+=1
            turn = True
        elif key == "4" or key == "h" or key == 260:
            y1-=1
            turn = True
        elif key == "6" or key == "l" or key == 261:
            y1+=1
            turn = True
        elif key == "q":
            io.printex(0,0,"PRESS '!' TO QUIT:" + " " * 20,2) #Paranoid
            key = io.readkey()
            if key == "!":
                self.logWrite(name, score, hp, maxhp, VERSION,\
                              "Quit",gold,kills)
                self.end()
        elif key == "i": #Show inventory.
            self.invMenu()
        elif key == "m":  #Message (for ttyrecs)
            io.printex(23,0,"")
            screen.curs_set(1)
            screen.nocbreak()
            screen.echo()
            screen.getstr()
            screen.curs_set(0)
            screen.cbreak()
            screen.noecho()
            io.printex(23,0," " * 100,False)
        elif key == "s":
            regen = 0
            self.save()
        elif key == "r":
            if os.path.isfile(save) and wizmode:   #If there is savefile        
                self.load()                    
                x1,y1 = x,y
                self.resetFlood()
                self.floodFill()
                self.resetFov()
                self.drawMap()
                Fov.fieldOfView(x, y, MAP_W, MAP_H, frad, self.setVisible,\
                                self.isBlocking)                        
            io.printex(0,0,"")
        elif key == "=":  #Last messages
            i = 0
            screen.clear()
            messages = copy.copy(mstack)
            messages.reverse()
            oldmsg = ""
            mnum = 0
            for message in messages:
                msg = message[0]
                attr = message[1]
                if oldmsg == msg:
                    i -= 1
                    mnum += 1
                    io.printex(i,50,"(%sx)" % mnum,attr)
                else:
                    io.printex(i,0,msg,attr)
                oldmsg = msg
                i += 1
                if i == 22:
                    io.printex(23,0,"--More--",GREEN)
            io.readkey()
            screen.clear()
            for line in gamemap:
                for cell in line:
                    cell.changed = True
            self.drawMap()
            io.printex(0,0," " * 60,refresh=False)
            if wizmode:
                io.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+\
                    str(key)+";T:"+str(turns)+"; HP:"+str(hp)+"/"+\
                    str(maxhp),refresh=False) #DEBUG 
            io.printex(4, 63, state, 2,refresh=False)
            io.printex(6, 63, " " * 10,refresh=False)            
            hpattr = GREEN
            if hp == maxhp:
                hpattr = GREEN
            if hp <= maxhp / 2:
                hpattr = YELLOW
            if hp <= 5:
                hpattr = RED
            io.printex(6, 63, "HP:%d/%d" % (hp, maxhp), hpattr,refresh=False)
            io.printex(8, 63, "T:%d" % (turns),refresh=False)
            io.printex(10, 63, "Score:%d" % (score),3,refresh=False)
            io.printex(12, 63, "Level:%d" % (level),3)
            self.resetFov()
            Fov.fieldOfView(x, y, MAP_W, MAP_H, frad, self.setVisible,\
                    self.isBlocking)                        
            self.drawMap()
            io.printex(x,y ,p1.char())
            io.printex(x,y,p1.char(),1)
            io.printex(2, 63, name, 3)
        elif key == ";":  #Farlook
            io.printex(23, 0, "You")
            screen.curs_set(1)
            io.printex(x, y, "")
            cx1,cy1,cx,cy = x,y,x,y
            key = ""
            while key != ";":
                key = io.readkey()
                if key == "8" or key == "k" or key == 259:
                    cx1-=1
                elif key == "2" or key == "j" or key == 258:
                    cx1+=1
                elif key == "4" or key == "h" or key == 260:
                    cy1-=1
                elif key == "6" or key == "l" or key == 261:
                    cy1+=1
                elif key == "7" or key == "y" or key == 262:
                    cx1-=1
                    cy1-=1
                elif key == "9" or key == "u" or key == 339:
                    cx1-=1
                    cy1+=1
                elif key == "1" or key == "b" or key == 360:
                    cx1+=1
                    cy1-=1
                elif key == "3" or key == "n" or key == 338:
                    cx1+=1
                    cy1+=1
                if cx1 <= 22 and cx1 >= 1 and cy1 <= 61 and cy1 >= 1:
                    cx,cy = cx1,cy1
                else:
                    cx1,cy1 = cx,cy
    
                type = ""
                if gamemap[cx][cy].item and gamemap[cx][cy].explored:
                    type = gamemap[cx][cy].name
                elif gamemap[cx][cy].mob and (gamemap[cx][cy].visible or\
                self.inLos(x, y, cx, cy)):
                    type = gamemap[cx][cy].name
                elif gamemap[cx][cy].sdoor:
                    type = "Wall"
                elif gamemap[cx][cy].boulder and gamemap[cx][cy].explored:
                    type = "Boulder"
                elif gamemap[cx][cy].door and gamemap[cx][cy].explored:
                    if gamemap[cx][cy].opened:
                        type = "Open door"
                    else:
                        type = "Closed door"
                elif gamemap[cx][cy].stairs and gamemap[cx][cy].explored:
                    if gamemap[cx][cy].up:
                        type = "Staircase up"
                    else:
                        type = "Staircase down"
                else:
                    if gamemap[cx][cy].explored == False:
                        type = "Unexplored"
                        for char in chars:
                            if (char[0],char[1],char[2]) == (level,cx,cy):
                                type = "Something unseen and blocking way"
                    else:
                        if gamemap[cx][cy].type[0]:
                            type = "Ground"
                        else:
                            type = "Wall"
                if [cx,cy] == [x,y]:
                    type = "You"
                io.printex(23, 0, " " * 200, refresh = False)                                        
                io.printex(23, 0, type)
                io.printex(cx, cy, "")
            screen.curs_set(0)
        elif key == "o": #Open door
            d = self.askDirection()
            mnext = 0
            if d:
                dx = d[0]
                dy = d[1]
                if gamemap[dx][dy].door:
                    if gamemap[dx][dy].locked:
                        self.addMsg("This door is locked!",RED)
                    else:
                        gamemap[dx][dy].open()
                        turn = True
            mapchanged = True
        elif key == "K":
            turn = True
            xk, yk = self.askDirection()
            mnext = 0
            if xk == False:
                turn = False
            else:
                if not gamemap[xk][yk].type[0]:
                    if gamemap[xk][yk].mob:
                        gamemap[xk][yk].hp -= random.randint(3,5)
                        self.addMsg("You kicked %s!" % \
                                       gamemap[xk][yk].name,GREEN)
                        if gamemap[xk][yk].hp <= 0:
                            self.addMsg("You kill %s!" % gamemap\
                                           [xk][yk].name,GREEN)
                            gamemap[xk][yk] = gamemap[xk][yk].undercell
                    elif gamemap[xk][yk].door:
                        self.addMsg("You kicked the door!" %\
                                        gamemap[xk][yk],2)
                        if not random.randint(0,5):
                            self.addMsg("It breaks!" %\
                                            gamemap[xk][yk],2)
                            lit = gamemap[xk][yk].lit
                            gamemap[xk][yk] = Cell.Cell(True,True)
                            gamemap[xk][yk].lit = lit
                    elif gamemap[xk][yk].sdoor:
                        self.addMsg("You kicked the wall!" %\
                                        gamemap[xk][yk],2)
                        hp -= random.randint(3,5)
                        if hp<= 0:
                            killer = "Kicking hidden door"
                        if not random.randint(0,8):
                            self.addMsg("You found hidden door!" %\
                                            gamemap[xk][yk],2)
                            lit = gamemap[xk][yk].lit
                            gamemap[xk][yk] = Cell.Door(False,random.\
                                                    choice([True,False]))
                            gamemap[xk][yk].lit = lit
                            if random.randint(0,5):
                                self.addMsg("It breaks!" %\
                                                gamemap[xk][yk],2)
                                lit = gamemap[xk][yk].lit
                                gamemap[xk][yk] = Cell.Cell(True,True)
                                gamemap[xk][yk].lit = lit
                    elif gamemap[xk][yk].plain_cell:
                        self.addMsg("You kicked the wall!" %\
                                        gamemap[xk][yk],2)
                        hp -= random.randint(3,5)
                        if hp<= 0:
                            killer = "Kicking wall"
                    elif gamemap[xk][yk].boulder:
                        self.addMsg("You kicked the boulder!" %\
                                        gamemap[xk][yk],2)
                        hp -= random.randint(3,5)
                else:
                    if gamemap[xk][yk].item:
                        gamemap[xk][yk].changed = True
                        self.drawMap()
                        io.printex(x,y,p1.char(),1)
                        mx = xk - x
                        my = yk - y
                        for m in xrange(5):
                            io.printex(x,y,p1.char(),1)
                            if not gamemap[xk + mx][yk + my].type[0]:
                                if gamemap[xk + mx][yk + my].mob:
                                    self.addMsg("%s hits %s!" %\
                                        (gamemap[xk][yk].name,gamemap[xk + mx]
                                         [yk + my].name),2)
                                    gamemap[xk + mx][yk + my].hp -= random.\
                                        randint(1,4)
                                break
                            io.frkey()
                            gamemap[xk][yk].changed = True
                            self.moveMob(xk, yk,xk + mx,yk + my, gamemap)
                            xk += mx
                            yk += my
                            gamemap[xk][yk].changed = True
                            self.drawMap()
                    else:
                        self.addMsg("You kicked air!" %\
                                        gamemap[xk][yk],2)
                    
        elif key == "c": #Close door
            d = self.askDirection()
            mnext = 0
            if d:
                dx = d[0]
                dy = d[1]
                if gamemap[dx][dy].door:
                    gamemap[dx][dy].close()
            mapchanged = True
        elif key == "w": #Wait
            turn = True
            p1.energy -= 100
            mx,my = random.randint(-1,1),random.randint(-1,1)
            if gamemap[x+mx][y+my].sdoor:
                lit = gamemap[x+mx][y+my].lit
                gamemap[x+mx][y+my] = Cell.Door(False,random.choice([True\
                                                                     ,False]))
                gamemap[x+mx][y+my].lit = lit
        elif key == ">" or key == "<": #Move up or down
            if gamemap[x][y].stairs:
                moved = gamemap[x][y].up
                if level == 1 and gamemap[x][y].up:
                    io.printex(0, 0, "PRESS '!' IF YOU WANT TO ESCAPE:",2)
                    key = io.readkey()
                    if key == "!":
                        killer = "Escaped"
                        self.logWrite(name, score, hp, maxhp, VERSION,\
                                      killer,gold,kills)
                        self.end()
                else:
                    turn = True
                    screen.clear()
                    lnext = gamemap[x][y].move() + level
                    #restore or gen level:
                    if lnext <= len(levs):
                        levs.append(None)
                    if levs[lnext]:
                        levs[level] = copy.deepcopy(gamemap)
                        gamemap = copy.deepcopy(levs[lnext])
                        level = lnext
                    else:
                        levs[level] = copy.deepcopy(gamemap)
                        for mapx in xrange(MAP_W - 1):
                            for mapy in xrange(MAP_H):
                                gamemap[mapx][mapy] = Cell.\
                                Cell(False,False)
                        gen = Level.levGen()
                        (gamemap,y,x) = gen.generateLevel(gamemap)
                        levs[lnext] = copy.deepcopy(gamemap)
                        level = lnext
                        self.amnesia()
                    #end gen level
                    for mapx in xrange(MAP_W - 1):
                        for mapy in xrange(MAP_H):
                            if gamemap[mapx][mapy].mob:
                                if gamemap[mapx][mapy].undercell.stairs:
                                    gamemap[mapx][mapy] = gamemap[mapx]\
                                    [mapy].undercell
                            if gamemap[mapx][mapy].stairs and \
                            gamemap[mapx][mapy].up != moved:
                                x,y = mapx,mapy
                    x1,y1 = x,y
                    mapchanged = True
                    self.resetFov()
                    self.resetFlood()
                    Fov.fieldOfView(x, y, MAP_W, MAP_H, frad,\
                                     self.setVisible, self.isBlocking)
                    for mapx in xrange(MAP_W - 1):
                        for mapy in xrange(MAP_H):
                            gamemap[mapx][mapy].changed = True
            else:
                self.addMsg("There is no stairs!",2)
        elif key == "x" and wizmode and editmode:
            gamemap[x][y].type = [False,False]
            mapchanged = True
        elif key == "a" and wizmode and editmode:
            d = self.askDirection()
            mnext = 0
            if d:
                dx = d[0]
                dy = d[1]
                if dx <= 20 and dx >= 2 and dy <= 60 and dy >= 2:
                    gamemap[dx][dy] = Cell.Cell(True, True)
            mapchanged = True

        else:
            if wizmode and key == "#": #Debug commands.
                key = io.readkey()
                if key == "x":
                    editmode = True
                elif key == "S":
                    gamemap[x][y + 1] = Cell.item("Gold","$",gamemap[x][y + 1])
                elif key == "Z":
                    gamemap[x][y] = Cell.Stair(True)
                elif key == "z":
                    fovblock = not fovblock  
                elif key == "F":
                        for mapx in xrange(MAP_W - 1): 
                            for mapy in xrange(MAP_H):
                                if gamemap[mapx][mapy].stairs:
                                    if gamemap[mapx][mapy].up:
                                        c = "<"
                                    else:
                                        c = ">"
                                    io.printex(mapx,mapy,c,2)
                                    io.readkey()
                elif key == "R":
                    for mapx in xrange(MAP_W+1):
                        for mapy in xrange(MAP_H+1):
                            if mapx <= 20 and mapx >= 2 and mapy <= 60 and\
                             mapy >= 2:
                                gamemap[mapx][mapy] = Cell.Cell(True,True)
                            else:
                                gamemap[mapx][mapy] = Cell.Cell(False,False)
                elif key == "u":
                    gamemap[mapx][mapy]
                elif key == "d":
                    gamemap[x][y] = Cell.Door(True,False)
                    gamemap[x][y].close()
                    mapchanged = True
                elif key == "v":
                    gamemap[x][y].lit = not gamemap[x][y].lit
                elif key == "p":
                    d = self.askDirection()
                    mnext = 0
                    rx = d[0]
                    ry = d[1]
                elif key == "g":
                    gamemap[rx][ry] = Cell.Newt("Newt",":",gamemap[rx][ry])
                    mapchanged = True
                elif key == "!":
                    self.floodFill()
                elif key == "e":
                    d = self.askDirection()
                    mnext = 0
                    mapchanged = True
                    if d:
                        self.moveMob(d[0],d[1], x, y,gamemap)
                elif key == "@":
                    io.debug_message(gamemap[x][y].fval)
                elif key == "f":
                    d = self.askDirection()
                    mnext = 0
                    if d:
                        dx = d[0]
                        dy = d[1]
                        if gamemap[dx][dy].mob:
                            gamemap[dx][dy] = gamemap[dx][dy].undercell 
                elif key == "a":
                    self.amnesia()
                    self.addMsg(\
                        "Thinking of Maud you forget everything else.",1)
                        #NetHack reference
                elif key == "i":
                    d = self.askDirection()
                    mnext = 0
                    if d:
                        dx = d[0]
                        dy = d[1]
                        if dx <= 20 and dx >= 2 and dy <= 60 and dy >= 2:
                            gamemap[dx][dy] = Cell.Cell(True, True)
                    mapchanged = True
                elif key == "t":
                    ucell = gamemap[x][y]
                    gamemap[x][y] = Cell.Newt("Newt",":",ucell)
                    mapchanged = True
            if not gamemap[x][y].door:       #You can't use diagonal keys
                                            #while you are in door.
                if key == "7" or key == "y"  or key == 262: 
                    x1-=1
                    y1-=1
                    turn = True
                elif key == "9" or key == "u" or key == 339:
                    x1-=1
                    y1+=1
                    turn = True
                elif key == "1" or key == "b" or key == 360:
                    x1+=1
                    y1-=1
                    turn = True
                elif key == "3" or key == "n" or key == 338:
                    x1+=1
                    y1+=1
                    turn = True
                else:
                    turn = False # You haven't moved
                if gamemap[x1][y1].door:
                    x1,y1 = x,y
                    turn = False
            else:
                turn = False
        if gamemap[x1][y1].type[0]:
            x,y = x1,y1
            p1.energy -= 95
        else:
            turn = False                        
            if gamemap[x1][y1].door:
                if gamemap[x1][y1].locked:
                    self.addMsg("The door is locked!",RED)
                else:
                    gamemap[x1][y1].open()
                    turn = True
                    p1.energy -= 120
                    mapchanged = True
            elif gamemap[x1][y1].mob:
                self.addMsg("You hit %s!" % gamemap[x1][y1].name\
                               ,3)
                turn = True
                gamemap[x1][y1].hp -= random.randint(3,10)
                if gamemap[x1][y1].hp <= 0:
                    self.addMsg("You kill the %s!" %
                                gamemap[x1][y1].name ,3)
                    score += 5
                    kills += 1
                    gamemap[x1][y1] = gamemap[x1][y1]\
                        .undercell
                    gamemap[x1][y1].visible = True
                    if random.choice([True,False] + [False] * 10):
                        gamemap[x1][y1] = Cell.item("Gold",\
                                "$",gamemap[x1][y1])
                    mapchanged = True
                p1.energy -= 100
            if gamemap[x1][y1].boulder:
                nx = x1 - x
                ny = y1 - y
                if gamemap[x1 + nx][y1 + ny].type[0]:
                    self.moveMob(x1, y1, x1 + nx, y1 + ny,gamemap) #Not only mob 
                    self.addMsg("You moved the boulder.",1)
                    mapchanged = True
                    turn = True
                    p1.energy -= 150
                    x,y = x1,y1
                else:
                    if gamemap[x1 + nx][y1 + ny].explored and not gamemap[x1 +\
                     nx][y1 + ny].mob:
                        turn = False
                    else:
                        turn = True
                        p1.energy -= 90
                        self.setChar(level,x1 + nx,y1 + ny,"?",1)
                    self.addMsg("You can't move the boulder.",2)
                    x1,y1 = x,y
            else:
                x1,y1 = x,y
        if gamemap[x][y].item:
            if gamemap[x][y].name == "Gold":
                score += gamemap[x][y].howmany
                gold += gamemap[x][y].howmany
                p1.cont[0].inv.append(gamemap[x][y])
                self.addMsg("You found %d gold!" % gamemap[x][y].howmany,4)
                gamemap[x][y] = gamemap[x][y].undercell
        return key
    
    def canSeeYou(self,mapx,mapy):
        global x,y,gamemap
        if gamemap[mapx][mapy].infra:
            return self.inLos(mapx,mapy,x,y)
        else:
            return gamemap[mapx][mapy].visible

    def rmove(self,mapx,mapy):
        global gamemap
        list = [(0,0)]
        for x2 in xrange(-1,2):
            for y2 in xrange(-1,2):
                if gamemap[mapx + x2][mapy + y2].type[0]:
                    list.append((x2,y2))
        move = random.choice(list)
        mx,my = move
        if (mx,my) != (0,0):
            self.moveMob(mapx, mapy,mapx +\
                          mx,mapy+ my,gamemap)
            gamemap[mapx + mx][mapy + my].\
            energy -= 115

    def hasSpaceAround(self,x,y):
        """Checks if there is free cells
            around x,y"""
        global gamemap
        c = 0
        for x2 in xrange(-1,2):
            for y2 in xrange(-1,2):
                if not gamemap[x + x2][y + y2].type[0]:
                    c += 1
                else:
                    return True
        else:
            return False
    
    def near(self,x1,y1,x2,y2):
        """Checks if x1,y1 near x2,y2"""
        return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1

        
    def addMsg(self,msg,attr):
        global addmsg,mnext,mstack
        msg += " "
        if mnext == 0:
            io.printex(22,0," " * 100)
        mstack.append((msg,attr))
        io.printex(22,mnext,msg,attr)
        addmsg = True
        mnext += len(msg)
        if mnext > 40:
            io.printex(22,mnext,"--More--",GREEN)
            mnext = 0
            io.readkey()
            io.printex(22,0," " * 100)
    def messageStack(self):
        global mnext,addmsg
        if addmsg:
            addmsg = False
        else:
            io.printex(22,0," " * 100)
            addmsg = True
        if turn:
            io.printex(23,0," " * 100)
    def inCircle(self,center_x, center_y, radius, x, y):
        square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
        return square_dist <= radius ** 2

    def distance(self,x1,y1,x2,y2):
        return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )



if __name__ == "__main__":
    print "Please run main.py"
    raw_input()
    sys.exit()

#  __           _       _  _    ___    
# /        _/_  /  _   /  /   /   /  /
#/   /   / /   /  / // |  \  /___/  /
#\__ \__/ /_  /_ /_// _/ _/ /  \   /____