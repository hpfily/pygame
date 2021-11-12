#-*- coding:utf-8 -*-
import pygame
from pygame import Surface, Vector2, sprite
from pygame import image
from pygame.locals import *
from sys import exit
from os  import getcwd

from enum import Enum

RoleStatus    = Enum('RoleStatus', ('IDLE','RUN','ATTACK') )
Direction     = Enum('Direction', ('UP','DOWN','LEFT','RIGHT') )


class Role_Sprit(pygame.sprite.Sprite):    
    def __init__(self, surface, isIdleSprit=False):
        pygame.sprite.Sprite.__init__ (self)

        self.screen = surface
        self.isIdleSprit = isIdleSprit
        self.animationRow    = 0
        self.animationCol    = 0
        self.spritSurface = None
        self.direction = Direction.RIGHT
        
        self.allFrameRect = {}
        self.directRect = []
        self.curBlitSrcRect = []
        
        self.frame  = 0
        self._rate  = 200       # 200ms every frame 5pfs.
        self.passed_time = 0
        self.spritRect = None

    def splitRect(self,surface,row=None,col=None):
        self.frameHeight  = surface.get_height()/row
        self.frameWidth   = surface.get_width()/col
        if row == None:
            return surface
        directionlist = [Direction.DOWN, Direction.LEFT,Direction.RIGHT,Direction.UP]
        rect    = { }
        temp    = [ ]
        for y in range(row):
            for x in range(col):
                temp.append(Rect((x*self.frameWidth,y*self.frameHeight),(self.frameWidth,self.frameHeight)))
                if x== (col-1):
                    rect[directionlist[y]]=temp
                    temp = [] 
        return  rect
    
    def load(self,file,row,col):
        self.animationRow     = row
        self.animationCol     = col
        self.spritSurface = pygame.image.load(file).convert_alpha()
        self.allFrameRect = self.splitRect(self.spritSurface,self.animationRow,self.animationCol)


    def update(self, passed_time, curDirection, postion):
        #assert(self.allrect.has_key(direction))
        
        #self.positionBlitTopLeft = (postion[0]-self.frameWidth/2, postion[1]-self.frameHeight/2)
        #self.spritRect = Rect(self.positionBlitTopLeft, (self.frameWidth, self.frameHeight) )
        self.spritRect = Rect(postion, (self.frameWidth, self.frameHeight) )
        self.spritRect.center = postion 
        
        self.direction = curDirection
        
        if self.isIdleSprit:
            self.directRect  = self.allFrameRect[self.direction]
            self.curBlitSrcRect   = self.directRect[0]
            self.screen.blit(self.spritSurface, self.spritRect.topleft, self.curBlitSrcRect )
            return

        
        #print self.direction
        self.passed_time += passed_time
        self.frame  = (self.passed_time/self._rate)%self.animationCol
        if self.frame == 0 and self.passed_time > self._rate:
            self.passed_time = 0
        self.directRect  = self.allFrameRect[self.direction]
        self.curBlitSrcRect   = self.directRect[int(self.frame)]
        self.screen.blit(self.spritSurface, self.spritRect.topleft, self.curBlitSrcRect )
        #pygame.draw.rect(self.screen, (255,255,255), self.spritRect, 1)


class Role(object):
    def __init__(self, position, direction):
        #self.status     = [ RoleStatus.IDLE, RoleStatus.RUN, RoleStatus.ATTACK ]
        self.curStatus  = RoleStatus.IDLE
        self.position   = position
        self.speed      = 80
        self.direction  = direction
        self.spriteDict = { RoleStatus.IDLE:None, RoleStatus.RUN:None, RoleStatus.ATTACK:None }

    def addSprite(self, status, sprit):
       # assert status in RoleStatus, "No this status"
        self.spriteDict[status] = sprit

    def getDirection(self, pressKey):
        direction = None
        runKeyPress = False

        if pressKey[pygame.K_UP] :
            direction = Direction.UP
            runKeyPress = True
        if pressKey[pygame.K_DOWN] :
            direction = Direction.DOWN
            runKeyPress = True
        if pressKey[pygame.K_LEFT] :
            direction = Direction.LEFT
            runKeyPress = True
        if pressKey[pygame.K_RIGHT] :
            direction = Direction.RIGHT
            runKeyPress = True

        if pressKey[pygame.K_UP] and pressKey[pygame.K_DOWN] :
            direction = self.direction
        if pressKey[pygame.K_LEFT] and pressKey[pygame.K_RIGHT] :
            direction = self.direction
        return direction, runKeyPress   


    def updatePosition(self, passTime, pressedKey):
        dis = self.speed*passTime/1000
        if pressedKey[pygame.K_UP] :
            self.position[1] = self.position[1] - dis
        if pressedKey[pygame.K_DOWN] :
            self.position[1] = self.position[1] + dis        
        if pressedKey[pygame.K_LEFT] : 
            self.position[0] = self.position[0] - dis
        if pressedKey[pygame.K_RIGHT] :
            self.position[0] = self.position[0] + dis
        #print(self.position)

    def update(self, passed_time, pressedKey) :
        direction, runKeyPress = self.getDirection(pressedKey)
        self.updatePosition(passed_time, pressedKey)

        self.status = RoleStatus.IDLE
        if direction :
            self.direction = direction
        if runKeyPress :
            self.status = RoleStatus.RUN           
                    
        if pressedKey[pygame.K_a] :
            self.status = RoleStatus.ATTACK
        
        sprite = self.spriteDict[self.status]
        sprite.update(passed_time, self.direction, self.position)
        


pygame.init()

SCREENSIZE      = (800,600)

RESOURCEPATH    = getcwd() + '/pic'
print (RESOURCEPATH)
MAPPATH         = RESOURCEPATH + '/bg.jpg'

screenSurface   = pygame.display.set_mode(SCREENSIZE,0,32)
pygame.display.set_caption("hello game!")

bgSurface       = pygame.image.load(MAPPATH).convert()
clock           = pygame.time.Clock()

roleIdleSpirt   = Role_Sprit(screenSurface,isIdleSprit=True)
RoleSpirtPath   = RESOURCEPATH + '/spritZF_run.png'
roleIdleSpirt.load(RoleSpirtPath, 4, 4)

roleRunSprit    = Role_Sprit(screenSurface)
RoleSpirtPath   = RESOURCEPATH + '/spritZF_run.png'
roleRunSprit.load(RoleSpirtPath, 4, 4)

roleAttackSpirt       = Role_Sprit(screenSurface)
roleAttackSpirtPath   = RESOURCEPATH + '/spritZF_attack.png'
roleAttackSpirt.load(roleAttackSpirtPath, 4, 4)

Player          = Role([200,200], Direction.UP)
Player.addSprite(RoleStatus.IDLE, roleIdleSpirt) 
Player.addSprite(RoleStatus.RUN,  roleRunSprit)
Player.addSprite(RoleStatus.ATTACK,  roleAttackSpirt)

transColor = pygame.Color(0, 0, 0)
sprite_skill=pygame.image.load(RESOURCEPATH+'/skill.png').convert_alpha()
sprite_skill.set_colorkey(transColor)


totle_time=0
position=[100,150]
mouse_pos=[0,0]

while True:
    screenSurface.blit(bgSurface, (0,0))
    direction = None
#event loop
    for event in pygame.event.get():
        #print(event)
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos=event.pos
            mouse_pos_v=Vector2(mouse_pos)
            position_v=Vector2([200,200])
            print(position_v,mouse_pos_v)
            angle=Vector2().angle_to(mouse_pos_v-position_v)
            print(angle)


    Passtime = clock.tick()
    Key  = pygame.key.get_pressed()
    Player.update(Passtime, Key)

    skill_w=60
    skill_h=50
    rate=200
    
    totle_time=totle_time+Passtime
    f_numb=int(totle_time/rate % 4)+1
    w=f_numb*skill_w
    h=f_numb*skill_h
    
    rec=Rect(w-skill_w,0,skill_h,skill_h)

    sub_skill=sprite_skill.subsurface(rec)
    r_skill=pygame.transform.rotate(sub_skill,180)
    r_skill.set_colorkey(transColor)
    speed=60
    dis = speed*Passtime/1000
    position[0]+=dis
    screenSurface.blit(r_skill,position)
    
    # screenSurface.blit(sprite_skill,position, rec)
    # screenSurface.blit(sprite_skill,(100, 150), (0, 0, 60, 50))
    # screenSurface.blit(sprite_skill,(100, 200), (60, 0, 60, 50))
    # screenSurface.blit(sprite_skill,(100, 250), (120, 0, 60, 50))
    # screenSurface.blit(sprite_skill,(100, 300), (180, 0, 60, 50))

    # sub_skill=sprite_skill.subsurface(rec)
    
    # r_skill=pygame.transform.rotate(sub_skill,10)
    # r_skill.set_colorkey(transColor)
    # screenSurface.blit(r_skill,(100, 150))

    rect = Rect(0, 0 , 50, 50)
    pygame.draw.rect(screenSurface,(55,88,110),rect,1)

    rect.center = (50,50)
    pygame.draw.rect(screenSurface,(255,0,0),rect,1)
    #print(pygame.key.get_pressed())
    pygame.display.update()



