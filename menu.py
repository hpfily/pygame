# -*- coding:utf-8 -*-
import pygame
from pgu import gui
#from main import Role
import main

# define the RGB value for white,
#  green, blue colour .
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
red = (255, 0, 0)

def game_main():
    print("Game Start!")
    pygame.init()

#    show_text_dialog("Info", "You Win!")
    show_option_dialog()

def show_text_dialog(caption, message, bg_color=white, font_front=red, font_back=blue):
    print("Show Dialog!")
 
    # assigning values to X and Y variable
    X = 400
    Y = 200
 
    # create the display surface object
    # of specific dimension..e(X, Y).
    display_surface = pygame.display.set_mode((X, Y))
 
    # set the pygame window name
    pygame.display.set_caption(caption)
 
    # create a font object.
    # 1st parameter is the font file
    # which is present in pygame.
    # 2nd parameter is size of the font
    font = pygame.font.Font('freesansbold.ttf', 32)
 
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

    def start_game():
        # handle the options
        print("Player name is %s" % player_name.value)
        print("Gender is %s" % gender.value)
        print("Animation is %s" % anime.value)

        app.quit()

        # call the play scene
        print("Call the play function!")
        main.game_start()
        

    btn = gui.Button("Start Game!")
    btn.connect(gui.CLICK, start_game)
    c.tr()
    c.td(btn,colspan=3)


    app.run(c)

if __name__ == "__main__":
    game_main()
