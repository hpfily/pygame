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
        self.screen.blit(self.spritSurface, self.spritRect.topleft, self.curBlitSrcRect)


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
        

# Skill class
class Skill_Spirte(pygame.sprite.Sprite):
    def __init__(self, screen_surf, skill_surf, skill_rect, init_pos, direct_vec2):
        pygame.sprite.Sprite.__init__(self)
        #surface
        self.screen = screen_surf
        self.sprit_surf = skill_surf
        self.skill_rect = skill_rect
        #fps time 200 ms
        self.flush_time = 200
        #color key black
        self.transColor = pygame.Color(0, 0, 0)

        self.init_pos = list(init_pos)
        self.cur_pos= list(init_pos)
        self.speed = 200
        self.direct_vec2 = direct_vec2
        self.live_time = 0
        self.angle=Vector2().angle_to(self.direct_vec2)

        self.live_dis=0
    
    def move_pos(self, passtime):
        self.live_dis += self.speed*passtime/1000
        self.cur_pos[0]= self.init_pos[0]+self.live_dis*self.direct_vec2[0]
        self.cur_pos[1]= self.init_pos[1]-self.live_dis*self.direct_vec2[1]
        
        self.rect=self.image.get_rect()
        self.rect.move_ip(self.cur_pos[0], self.cur_pos[1])

    def update_image(self, passtime):       
        self.live_time=self.live_time+passtime       
        
        rect_index=int(self.live_time/self.flush_time % 4)
        sub_surf=self.sprit_surf.subsurface(self.skill_rect[rect_index])

        rotate_surf=pygame.transform.rotate(sub_surf,180+self.angle)
        rotate_surf.set_colorkey(self.transColor)
        
        self.image=rotate_surf



    def update(self, passtime):    
        self.update_image(passtime)
        self.move_pos(passtime)


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
#RoleSpirtPath   = RESOURCEPATH + '/spritZF_run.png'
RoleSpirtPath   = RESOURCEPATH + '/player_run.png'
roleIdleSpirt.load(RoleSpirtPath, 4, 4)

roleRunSprit    = Role_Sprit(screenSurface)
#RoleSpirtPath   = RESOURCEPATH + '/spritZF_run.png'
RoleSpirtPath   = RESOURCEPATH + '/player_run.png'
roleRunSprit.load(RoleSpirtPath, 4, 4)

roleAttackSpirt       = Role_Sprit(screenSurface)
roleAttackSpirtPath   = RESOURCEPATH + '/spritZF_attack.png'
roleAttackSpirt.load(roleAttackSpirtPath, 4, 4)

Player          = Role([200,200], Direction.UP)
Player.addSprite(RoleStatus.IDLE, roleIdleSpirt) 
Player.addSprite(RoleStatus.RUN,  roleRunSprit)
Player.addSprite(RoleStatus.ATTACK,  roleAttackSpirt)

transColor = pygame.Color(0, 0, 0)
surf_skill=pygame.image.load(RESOURCEPATH+'/skill.png').convert()

#Skill rect
skill_rect = [] 
skill_split_w=60
skill_split_h=50
skill_col=4
for i in range(0,skill_col):
    skill_rect.append(pygame.Rect(skill_split_w*i, 0, skill_split_w, skill_split_h))

print(skill_rect)

skill_pos=[200,200]


#pygame.sprite.remove()
#del(skill)
 

skills=pygame.sprite.Group()

while True:
    screenSurface.blit(bgSurface, (0,0))
    direction = None
    Passtime = clock.tick(60)
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
            
            mouse_pos_v=Vector2(event.pos)
            position_v=Vector2(Player.position)
            print(position_v,mouse_pos_v)

            direct_vec = mouse_pos_v-position_v
            direct_vec[1] = -direct_vec[1]
            direct_vec = direct_vec.normalize()
            angle=Vector2().angle_to(direct_vec)
            print(angle)
            
            shoot_skill=Skill_Spirte(screenSurface,surf_skill,skill_rect,Player.position, direct_vec)

            skills.add(shoot_skill)
    
    for skill in skills:
        if skill.live_dis >200:
              skills.remove(skill)
        skill.update(Passtime)
    
    skills.draw(screenSurface)
    
    Key  = pygame.key.get_pressed()
    Player.update(Passtime, Key)

    rect = Rect(300, 200 , 100, 100)
    pygame.draw.rect(screenSurface,(255,255,0),rect,1)
    Enemy=Skill_Spirte(screenSurface,surf_skill,skill_rect, [400,200], (1, 0))
    Enemy.update(Passtime)
    pygame.sprite.Group(Enemy).draw(screenSurface)

    skill_hit=pygame.sprite.spritecollide(Enemy,skills,0)
    if skill_hit:
        print("碰上啦")
    for sp in skill_hit:
        sp.kill()
        print(sp.rect)
        del(sp)

    #rect.center = (50,50)
    #pygame.draw.rect(screenSurface,(255,0,0),rect,1)
    #print(pygame.key.get_pressed())
    pygame.display.update()



