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

from Modules.constants import *  #Import constants

import sys
import cPickle  #Used for saves
import os.path
import random
import gzip
import copy

from Modules import AStar  #Pathfinding
from Modules import cell   #Cell class
from Modules import fov    #FOV algorithm
from Modules import Level  #Level generation
from Modules import IO     #Input/Output
from Modules import you    #Character.


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
        p1 = you.Player(name)
    def main_loop(self):
        """Main loop of game.
            Drawing things, generating map, playing
        """
        global gamemap,fovblock,turns,wizmode,editmode
        global x,y,rx,ry,x1,y1,turn
        global hp,regen,maxhp
        global score,gold
        global kills, killer
        global level,mapchanged
        global name,save,p1,frad
        global io,pstack,addmsg  
        global levs
        global chars
        
        maxhp = random.randint(20,40)  #Max hp always random
        hp = maxhp                     #Hp is at max
        regen = 0

        score = 0                       #Zero score
        gold  = 0
        kills = 0
        frad = 5
        
        editmode = False
        
        chars = []
        
        level = 1                       #Starting level
                
        pstack = []

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
                if mapx <= 21 and mapx >= 2 and mapy <= 60 and mapy >= 2:
                    gamemap[mapx].append(cell.Cell(True,True))
                else:
                    gamemap[mapx].append(cell.Cell(False,False))

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
        fov.fieldOfView(x, y, MAP_W, MAP_H, frad, self.setVisible,\
                         self.isBlocking)                        
        self.drawmap()
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
        addmsg = True
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
                    
            io.printex(x,y ,p1.char(),refresh = False)
            while p1.energy > 0:
                key = self.playerTurn() #Player's turn
                if len(pstack) > 1:
                    for line in pstack:
                        (mx,my,msg,attr) = line
                        io.printex(mx,my,msg + " --More--",attr)
                        io.readkey()
                        io.printex(23,0," " * 100)
                elif len(pstack) == 1:
                        (mx,my,msg,attr) = pstack[0]                
                        io.printex(mx,my,msg,attr)
                        addmsg = True
                pstack = []
                if mapchanged or turn:
                    self.resetFov()
                    fov.fieldOfView(x, y, MAP_W, MAP_H, frad, self.setVisible,\
                            self.isBlocking)                        
                if turn or mapchanged:
                    self.drawmap()
                io.printex(x,y ,p1.char(),refresh=True)
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
                                gamemap[mapx][mapy] = cell.Newt("Newt",\
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
                                gmap[mmx][mmy] = cell.Newt("Newt",\
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
                                    if hasSpaceAround(mapx,mapy):
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
                                if hasSpaceAround(mapx,mapy):
                                    (mvx,mvy) = self.mobTurn(mapx,mapy,gamemap)
                                    mobs[id] = (mvx,mvy) 
                        id += 1
                    i += 1        
            io.printex(x,y ,p1.char(),refresh=False)
            if turn:
                io.printex(0,0," " * 60,refresh=False)
            if wizmode:
                io.printex(0,0,"X:"+str(x)+", Y:"+str(y)+";key:"+str(key)+\
                           ";T:"+str(turns)+"; HP:"+str(hp)+"/"+str(maxhp),\
                             refresh=False) #DEBUG 
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
        else:
            io.printex(23, 0, "You died! --press any key--",2)
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
        
    def drawmap(self):  
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
                        gamemap[mapx][mapy].changed = True
                    if gamemap[mapx][mapy].lit and not gamemap[mapx][mapy].\
                    mob:
                        if self.inLos(mapx, mapy, x, y):
                            gamemap[mapx][mapy].visible = True
                    if gamemap[mapx][mapy].visible: #Visible always explored
                        gamemap[mapx][mapy].explored = True
                        if gamemap[mapx][mapy].mob:
                            gamemap[mapx][mapy].undercell.explored = True
                            gamemap[mapx][mapy].explored = False
                        screen.attron(screen.A_BOLD) #Visible is bold
                        if gamemap[mapx][mapy].type[0] and gamemap[mapx]\
                        [mapy].plain_cell:
                            color = 1 #Dots are white not yellow
                        else:
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

    def setVisible(self,x,y):
        """Sets tile as visible"""
        global gamemap,fovblock
        if not gamemap[x][y].visible:
            gamemap[x][y].visible = not fovblock
            gamemap[x][y].changed = True

    def resetFov(self):
        """Resets FOV"""
        global gamemap
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):
                if gamemap[mapx][mapy].visible:        
                    gamemap[mapx][mapy].visible = False
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
            io.printex(23, 0, "Wrong direction!")
            return False
        return x1,y1
    def load(self):
        """Load game from save"""
        global gamemap,x,y,hp,turns,fovblock,rx,ry,save,wizmode
        global gold,kills,score,levs,level,regen,maxhp,frad
        saved = gzip.open(save,"rb",-1)
        (level,info,gamemap,levs) = cPickle.load(saved)
        (gold,kills,score,x,y,rx,ry,fovblock,hp,maxhp,turns,regen,frad) = info
        saved.close()
        pstack.append((23,0,"Loaded...",1))
        for mapx in xrange(MAP_W - 1):
            for mapy in xrange(MAP_H):
                gamemap[mapx][mapy].changed = True
        if not wizmode:
            os.remove(save)
        
    def save(self):
        """Save game"""
        global gamemap,x,y,hp,turns,fovblock,rx,ry,save,wizmode
        global gold,kills,score,levs,level,regen,maxhp,frad
        saved = gzip.open(save,"wb",-1)
        info = (gold,kills,score,x,y,rx,ry,fovblock,hp,maxhp,turns,regen,frad)
        cPickle.dump((level,info,gamemap,levs), saved,2)
        pstack.append((23,0,"Saved...",1))
        if not wizmode:
            saved.close()
            self.end()    

    def get_line(self,x1, y1, x2, y2):
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
        line = self.get_line(y, x, y1, x1) 
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
        if (mx1,my1) != (0,0):
            return mx1,my1
        else:
            return 0,0
            

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
                        gamemap[mapx][mapy] = cell.Newt("Newt",":",gamemap\
                                                        [mapx][mapy])
    def logWrite(self,name,score,hp,maxhp,version,death,gold,kills):
        """Write text to log"""
        global wizmode
        if not wizmode:
            log = open("mainlog.log","a")
            log.write(("version=%f:name=%s:score=%d:hp=%d:maxhp=%d:killer=%s:"
                    + "gold=%d:kills=%d\n") %
                      (version,name,score,hp,maxhp,death,gold,kills))
    def setChar(self,levl,x,y,char,attr):
        global chars
        chars.append((level,x,y,char,attr))
                     
    def drawChar(self,x,y,level):
        global chars
        for char in chars:
            if (char[0],char[1],char[2]) == (level,x,y):
                io.printex(x,y,char[3],char[4])
                if gamemap[x][y].explored:
                    del char

    def mobTurn(self,mapx,mapy,gamemap):
        global levs, pstack,hp,killer
        ret = (mapx,mapy)
        if near(x,y,mapx,mapy):
                pstack.append((23, 0, "%s hits!" %\
                        gamemap[mapx][mapy].name,2))
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
                    self.moveMob(mapx, mapy,mapx + mx,\
                                            mapy + my,gamemap)
                    if (mx,my) != (0,0):
                        gamemap[mapx + mx][mapy + my].\
                        energy -= 110
                    ret = (mapx + mx, mapy + my)
                #Move randomly.
            elif hasSpaceAround(mapx,mapy):
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
        global screen

    def playerTurn(self):
        global x,y,gamemap,killer,addmsg,pstack,x1,y1
        global turn,p1,level,score,kills,gold,mapchanged
        global rx,ry,fovblock,editmode,regen
        key = -1
        
        if addmsg:
            addmsg = False
        else:
            if turn:
                io.printex(23, 0, " " * 60, refresh = False)
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
            if os.path.isfile(save):   #If there is savefile        
                self.load()                    
                x1,y1 = x,y
                self.resetFlood()
                self.floodFill()
                self.resetFov()
                self.drawmap()
                fov.fieldOfView(x, y, MAP_W, MAP_H, frad, self.setVisible,\
                                self.isBlocking)                        
            io.printex(0,0,"")
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
            if d:
                dx = d[0]
                dy = d[1]
                if gamemap[dx][dy].door:
                    gamemap[dx][dy].open()
            mapchanged = True
        elif key == "c": #Close door
            d = self.askDirection()
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
                gamemap[x+mx][y+my] = cell.Door(False)
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
                    screen.clear()
                    next = gamemap[x][y].move() + level
                    #restore or gen level:
                    if next <= len(levs):
                        levs.append(None)
                    if levs[next]:
                        levs[level] = copy.deepcopy(gamemap)
                        gamemap = copy.deepcopy(levs[next])
                        level = next
                    else:
                        levs[level] = copy.deepcopy(gamemap)
                        for mapx in xrange(MAP_W - 1):
                            for mapy in xrange(MAP_H):
                                gamemap[mapx][mapy] = cell.\
                                Cell(False,False)
                        gen = Level.levGen()
                        (gamemap,y,x) = gen.generateLevel(gamemap)
                        levs[next] = copy.deepcopy(gamemap)
                        level = next
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
                    fov.fieldOfView(x, y, MAP_W, MAP_H, frad,\
                                     self.setVisible, self.isBlocking)
                    for mapx in xrange(MAP_W - 1):
                        for mapy in xrange(MAP_H):
                            gamemap[mapx][mapy].changed = True
            else:
                pstack.append((23,0,"There is no stairs!",2))
        elif key == "x" and wizmode and editmode:
            gamemap[x][y].type = [False,False]
            mapchanged = True
        elif key == "a" and wizmode and editmode:
            d = self.askDirection()
            if d:
                dx = d[0]
                dy = d[1]
                if dx <= 21 and dx >= 2 and dy <= 60 and dy >= 2:
                    gamemap[dx][dy] = cell.Cell(True, True)
            mapchanged = True

        else:
            if wizmode and key == "#": #Debug commands.
                key = io.readkey()
                if key == "x":
                    editmode = True
                elif key == "S":
                    gamemap[x][y] = cell.altar("=")
                elif key == "Z":
                    gamemap[x][y] = cell.Stair(True)
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
                            if mapx <= 21 and mapx >= 2 and mapy <= 60 and\
                             mapy >= 2:
                                gamemap[mapx][mapy] = cell.Cell(True,True)
                            else:
                                gamemap[mapx][mapy] = cell.Cell(False,False)
                elif key == "u":
                    gamemap[mapx][mapy]
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
                    mapchanged = True
                    if d:
                        self.moveMob(d[0],d[1], x, y,gamemap)
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
                        "Thinking of Maud you forget everything else.",1))
                        #NetHack reference
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
                gamemap[x1][y1].open()
                turn = True
                p1.energy -= 120
                mapchanged = True
            elif gamemap[x1][y1].mob:
                pstack.append((23, 0, "You hit %s" % gamemap[x1][y1].name\
                               ,3))
                gamemap[x1][y1].hp -= random.randint(3,10)
                if gamemap[x1][y1].hp <= 0:
                    pstack.append((23, 0, "You kill the %s" %
                                gamemap[x1][y1].name ,3))
                    score += 5
                    kills += 1
                    gamemap[x1][y1] = gamemap[x1][y1]\
                        .undercell
                    gamemap[x1][y1].visible = True
                    if random.choice([True,False] + [False] * 10):
                        gamemap[x1][y1] = cell.item("Gold",\
                                "$",gamemap[x1][y1])
                    mapchanged = True
                p1.energy -= 100
                turn = True
            if gamemap[x1][y1].boulder:
                nx = x1 - x
                ny = y1 - y
                if gamemap[x1 + nx][y1 + ny].type[0]:
                    self.moveMob(x1, y1, x1 + nx, y1 + ny,gamemap) #Not only mob 
                    pstack.append((23,0,"You moved the boulder.",1))
                    mapchanged = True
                    turn = True
                    p1.energy -= 150
                    x,y = x1,y1
                else:
                    if gamemap[x1 + nx][y1 + ny].explored or gamemap\
                    [x1 + nx][y1 + ny].mob:
                        turn = False
                    else:
                        turn = True
                        p1.energy -= 90
                        self.setChar(level,x1 + nx,y1 + ny,"?",1)
                    pstack.append((23,0,"You can't move the boulder.",2))
                    x1,y1 = x,y
            else:
                x1,y1 = x,y
        if gamemap[x][y].item:
            if gamemap[x][y].name == "Gold":
                gamemap[x][y] = gamemap[x][y].undercell
                gold_ = random.randint(4,10)
                score += gold_
                gold += gold_
                pstack.append((23, 0, "You found some gold!",4))
        return key
    def canSeeYou(self,mapx,mapy):
        global x,y,gamemap
        if gamemap[mapx][mapy].infra:
            return self.inLos(mapx,mapy,x,y)
        else:
            return gamemap[mapx][mapy].visible

def hasSpaceAround(x,y):
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

def near(x1,y1,x2,y2):
    """Checks if x1,y1 near x2,y2"""
    if -1 <= (x1 - x2) <= 1 and -1 <= (y1 - y2) <= 1:
        return True
    else:
        return False

#  __           _       _  _    ___    
# /        _/_  /  _   /  /   /   /  /
#/   /   / /   /  / // |  \  /___/  /
#\__ \__/ /_  /_ /_// _/ _/ /  \   /____