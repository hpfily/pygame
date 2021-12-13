# -*- coding:utf-8 -*-
import pygame
from pgu import gui
import main
import p2_main
from server import start_server
import threading
import time
import socket

# define the RGB value for white,
#  green, blue colour .
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
red = (255, 0, 0)

def game_main():
    print("Game Start!")
    pygame.init()

    show_option_dialog()

def show_text_dialog(caption, message, bg_color=blue, font_front=red, font_back=blue):
    print("Show Dialog!")
 
    # assigning values to X and Y variable
    X = 450
    Y = 120
 
    # create the display surface object
    # of specific dimension..e(X, Y).
    display_surface = pygame.display.set_mode((X, Y))
 
    # set the pygame window name
    pygame.display.set_caption(caption)
 
    # create a font object.
    # 1st parameter is the font file
    # which is present in pygame.
    # 2nd parameter is size of the font
    font = pygame.font.Font('freesansbold.ttf', 96)
 
    # create a text surface object,
    # on which text is drawn on it.
    text = font.render(message, True, font_front, font_back)
 
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()
 
    # set the center of the rectangular object.
    textRect.center = (X // 2, Y // 2)
 
    # infinite loop
    while True:
 
        # completely fill the surface object
        # with white color
        display_surface.fill(bg_color)
 
        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
        display_surface.blit(text, textRect)
 
        # iterate over the list of Event objects
        # that was returned by pygame.event.get() method.
        for event in pygame.event.get():
 
            # if event object type is QUIT
            # then quitting the pygame
            # and program both.
            if event.type == pygame.QUIT:
                 # quit the program.
                return
 
            # Draws the surface object to the screen.
            pygame.display.update()

def show_option_dialog():
    dlg_surface = pygame.display.set_mode((800, 600))
    
    # set the pygame window name
    pygame.display.set_caption('Main Menu')

    app = gui.Desktop()
    app.connect(gui.QUIT,app.quit,None)

    c = gui.Table(width=400,height=300)

    c.tr()
    c.td(gui.Label("Game Config"),colspan=4)
    
    c.tr()
    c.td(gui.Label("Name"))
    player_name = gui.Input(value='Player 1',size=16)
    c.td(player_name,colspan=3)

    c.tr()
    c.td(gui.Label("Gender"))
    gender = gui.Group(value='male')
    c.td(gui.Tool(gender,gui.Label('Male'),value='male'))
    c.td(gui.Tool(gender,gui.Label('Female'),value='female'))

    c.tr()
    c.td(gui.Label("Animation"))
    anime = gui.Select(value='preset1')
    anime.add("Preset-1",'preset1')
    anime.add("Preset-2",'preset2')
    c.td(anime,colspan=3)

    # todo insert the area to show the animation
    c.tr()
    role = main.Role((100,100), 'LEFT')
    

    def start_host_game():
        # handle the options
        print("Player name is %s" % player_name.value)
        print("Gender is %s" % gender.value)
        print("Animation is %s" % anime.value)

        app.quit()

        # call the play scene
        print("Call the play function!")
        main.game_start()
        
    class HostDialog(gui.Dialog):
        def __init__(self, external_app):
            self.ex_app = external_app

            title = gui.Label("Host Game")
            table = gui.Table(width=200,height=200)
            
            table.tr()
            table.td(gui.Label("Server Address"), colspan=3)

            loop_addr = "127.0.0.1"
            local_addr = get_local_addr()
            table.tr()
            table.td(gui.Label("IP : "))
            self.ip = gui.Select(value=loop_addr)
            self.ip.add(loop_addr, loop_addr)
            self.ip.add(local_addr, local_addr)
            table.td(self.ip, colspan=3)

            self.port = gui.Input(value='6666',size=6)
            table.tr()
            table.td(gui.Label("port : "))
            table.td(self.port)

            button = gui.Button("Start Game")
            button.connect(gui.CLICK, self.start_server_and_game)
            table.tr()
            table.td(button)
            super(HostDialog, self).__init__(title, table)

        def start_server_and_game(self):
            # close the dialogs
            self.ex_app.quit()
            self.close()

            # start the server
            server_addr = (self.ip.value, int(self.port.value))
            print("start server %s:%s ..." % (self.ip.value, self.port.value))
            server_thread = threading.Thread(target=start_server, args=(server_addr,))
            server_thread.setDaemon(True)
            server_thread.start()

            # start the game after 2 sec
            time.sleep(2)
            main.game_start(server_addr,player_name.value)


    host_dialog = HostDialog(app)
    btn_host = gui.Button("Host Game!")
    btn_host.connect(gui.CLICK, host_dialog.open, None)
    c.tr()
    c.td(btn_host,colspan=3)

    class JoinDialog(gui.Dialog):
        def __init__(self, external_app):
            self.ex_app = external_app

            title = gui.Label("Join Game")
            table = gui.Table(width=200,height=200)
            
            self.server_ip = gui.Input(value='127.0.0.1',size=16)
            table.tr()
            table.td(gui.Label("Server Address"), colspan=3)
            table.tr()
            table.td(gui.Label("IP : "))
            table.td(self.server_ip)

            self.port = gui.Input(value='6666',size=6)
            table.tr()
            table.td(gui.Label("port : "))
            table.td(self.port)

            button = gui.Button("Connect")
            button.connect(gui.CLICK, self.connect_server)
            table.tr()
            table.td(button)
            super(JoinDialog, self).__init__(title, table)

        def connect_server(self):
            server_addr = (self.server_ip.value, int(self.port.value))
            print("try to connect server %s:%s" % (self.server_ip.value, self.port.value))
            self.ex_app.quit()
            self.close()
            p2_main.game_start(server_addr,player_name.value)


    join_dialog = JoinDialog(app)
    btn_join = gui.Button("Join Game!")
    btn_join.connect(gui.CLICK, join_dialog.open, None)
    c.td(btn_join,colspan=3)

    app.run(c)

def get_local_addr():
    return (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]

if __name__ == "__main__":
    game_main()
