#-*- coding:utf-8 -*-
import pygame
#from gameobjects.vector2 import Vector2
from Vec2d import Vec2d
from pygame.locals import *
from sys import exit
from os  import getcwd
print('hello world')

class Role_Sprit(pygame.sprite.Sprite):    
    def __init__(self,surface,row,col):
        pygame.sprite.Sprite.__init__ (self)
        self.row    = row
        self.col    = col
        self.surface= surface
        self.allrect= self.getrect(surface,row,col)
        self.rect   = ()
        self.frame  = 0
        self._rate  = 100       # 100ms every frame 10pfs.
        self.passed_time = 0

    def getrect(self,surface,row=None,col=None):
        self.height  = surface.get_height()/row
        self.width   = surface.get_width()/col
        if row == None:
            return surface
        directionlist = ['DownLeft','UpLeft','DownRight','UpRight']
        rect    = { }
        temp    = [ ]
        for y in range(row):
            for x in range(col):
                temp.append(Rect((x*self.width,y*self.height),(self.width,self.height)))
                if x== (col-1):
                    rect[directionlist[y]]=temp
                    temp = [] 
 #     print   rect
        return  rect

    def update(self,direction,passed_time):
        #assert(self.allrect.has_key(direction))
        self.direction   = direction
        #print self.direction
        self.passed_time += passed_time
        self.frame  = (self.passed_time/self._rate)%self.col
        if self.frame == 0 and self.passed_time > self._rate:
            self.passed_time = 0
        self.rects  = self.allrect[self.direction]
        self.rect   = self.rects[int(self.frame)]


class Role(object):
    def __init__(self,staysprit,runsprit):
        self.staysprit  = staysprit
        self.runsprit   = runsprit
        self.sprit      = staysprit
#        self.surface    = surface
        self.location   = Vec2d(1584,1312)
        self.destination= Vec2d(0,0)
        self.direction  = 'DownLeft'
        self.state      = 'stay'
        self.speed      = 200  #
    def render(self,screen):
        if self.state == 'stay':
            self.sprit  = self.staysprit
        else:
            self.sprit  = self.runsprit
  #      x,y=self.location
        x,y=(400,300)
        screen.blit(self.sprit.surface,(x-self.sprit.width/2,y-self.sprit.height/2),self.sprit.rect)

    def process(self,destination,passed_time):
        self.destination   = destination
        self.vec           = self.destination - self.location
        #print self.vec
        self.vec_len       = self.vec.get_length()
        if self.vec_len > 10:
            self.state     = 'run'
            self.vec_eye   = self.vec.normalized()

            if self.vec[0] >0:
                if self.vec[1] >0:
                    self.direction = 'DownRight'
                elif self.vec[1]<0:
                    self.direction = 'UpRight'
            elif self.vec[0]<0:
                if self.vec[1] >0:
                    self.direction = 'DownLeft'
                elif self.vec[1]<0:
                    self.direction = 'UpLeft'
                    
            self.location = self.location+ self.vec_eye*self.speed*passed_time/1000
            self.runsprit.update(self.direction,passed_time)
        else:
            self.state    = 'stay'
            self.staysprit.update(self.direction,passed_time)
            
def main():
    pygame.init()
    disSize = (800,600)
    disRect = Rect((0,0),disSize)
    screen  = pygame.display.set_mode(disSize,0,32)
    pygame.display.set_caption("hello world!")
    homedir = getcwd()
    #print homedir
    bgSurface = pygame.image.load(homedir+'/pic/bg.jpg').convert()
    bgSurfaceRect  = bgSurface.get_rect()
    disRect.center = bgSurfaceRect.center
    #print disRect.center
    #print disRect
    
    spritSurface=pygame.image.load(homedir+'/pic/sprit.png').convert_alpha()

    spritRunSurface=pygame.image.load(homedir+'/pic/sprit_run.png').convert_alpha()
    stay    =  Role_Sprit(spritSurface,4,8)
    run     =  Role_Sprit(spritRunSurface,4,8)
    role    =  Role(stay,run)

    clock  =  pygame.time.Clock()
#    pos     =role.location
    bgPos =  bgSurfaceRect.center
    while True:
        for event in pygame.event.get():
            if event.type ==QUIT:
                pygame.quit()
                exit()
            if event.type == MOUSEBUTTONDOWN:
#                print event.pos
#                pos=event.pos
                #print disRect.topleft
                temp    = [1,1]
                temp[0] = event.pos[0]+disRect.topleft[0]
                temp[1] = event.pos[1]+disRect.topleft[1]
                bgPos   = temp
                #print bgPos
        time = clock.tick()
        
        screen.blit(bgSurface,(0,0),disRect)
#        role.process(pos,time)
        role.process(bgPos,time)
        role.render(screen)
        disRect.center  =  role.location

        pygame.display.update()

if __name__=='__main__':
    main()
    
    
