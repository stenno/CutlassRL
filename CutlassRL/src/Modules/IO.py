import sys
try:
    from Modules import unicurses as curses               # Game will use curses to draw things
except ImportError:
    print "Curses library is missing."
    sys.exit()

class IO:
    def __init__(self):
        global screen
        screen = curses;

        screen.initscr()
        
        screen.curs_set(0)
        screen.cbreak()
        screen.start_color()
        screen.use_default_colors()

        #Color pairs
        screen.init_pair(1,-1,-1) #Default
        screen.init_pair(2,screen.COLOR_RED,-1) 
        screen.init_pair(3,screen.COLOR_GREEN,-1) 
        screen.init_pair(4,screen.COLOR_YELLOW,-1)
        screen.init_pair(5,screen.COLOR_BLUE,-1) 
        screen.init_pair(6,screen.COLOR_MAGENTA,-1)
        screen.init_pair(7,screen.COLOR_CYAN,-1) 
        screen.init_pair(8,screen.COLOR_WHITE,-1)

        screen.attron(screen.color_pair(1))
    def retSceen(self):
        global  screen
        return screen
    def debug_message(self,msg):
        """Debug message subroutine,
            Will say something like debugmsg: XXX
        """
        global screen
        screen.attron(screen.A_BOLD)
        self.printex(10,10,"debugmsg: %s" % msg,2)
        screen.attroff(screen.A_BOLD)
        self.readkey()

    def printex(self,x,y,text = "Someone had no words to say..." ,pair = None\
                ,refresh = True):
        """Print function.
            usage game.printex(<x of your text>,<y>,<Your text>,
            <color pair>,<refresh?>)
        """
        global screen
        if pair:
            screen.attron(screen.color_pair(pair))            
            
        screen.mvaddstr(x,y,text)
        
        if refresh:
            screen.refresh()
            
        if pair != None:
            screen.attroff(screen.color_pair(pair))

    def readkey(self):
        global screen
        """Readkey function.
            reads one key from stdin.
        """
        try:
            key = sys.stdin.read(1)
        except IOError:
            key = ""
            
        return key