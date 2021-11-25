# -*- coding:utf-8 -*-
import pygame
from pygame import *
from sys import exit
from os import getcwd

from enum import Enum

SCREEN = None
SCREENSIZE = (800, 600)
RESOURCEPATH = getcwd() + '/pic'
print(RESOURCEPATH)
MAPPATH = RESOURCEPATH + '/bg.jpg'

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


RoleStatus = Enum('RoleStatus', ('IDLE', 'RUN', 'ATTACK'))
Direction = Enum('Direction', ('UP', 'DOWN', 'LEFT', 'RIGHT'))


class Role_Sprit(pygame.sprite.Sprite):
    def __init__(self, surface, isIdleSprit=False):
        pygame.sprite.Sprite.__init__(self)

        self.screen = surface
        self.isIdleSprit = isIdleSprit
        self.animationRow = 0
        self.animationCol = 0
        self.spritSurface = None
        self.direction = Direction.RIGHT

        self.allFrameRect = {}
        self.directRect = []
        self.curBlitSrcRect = []

        self.frame = 0
        self._rate = 200       # 200ms every frame 5pfs.
        self.passed_time = 0
        self.spritRect = None

        self.angle = 0

    def splitRect(self, surface, row=None, col=None):
        self.frameHeight = surface.get_height()/row
        self.frameWidth = surface.get_width()/col
        if row == None:
            return surface
        directionlist = [Direction.DOWN, Direction.LEFT,
                         Direction.RIGHT, Direction.UP]
        rect = {}
        temp = []
        for y in range(row):
            for x in range(col):
                temp.append(Rect((x*self.frameWidth, y*self.frameHeight),
                            (self.frameWidth, self.frameHeight)))
                if x == (col-1):
                    rect[directionlist[y]] = temp
                    temp = []
        return rect

    def load(self, file, row, col):
        self.animationRow = row
        self.animationCol = col
        self.spritSurface = pygame.image.load(file)
        self.allFrameRect = self.splitRect(
            self.spritSurface, self.animationRow, self.animationCol)

    def update_pos(self, postion):
        self.rect = self.image.get_rect()
        # self.rect.move_ip(postion)
        self.rect.center = postion
        #pygame.draw.rect(self.screen, (255, 0, 0), self.rect, 1)

    def update_image(self, passtime,  curDirection):
        self.direction = curDirection

        if self.isIdleSprit:
            self.directRect = self.allFrameRect[self.direction]
            self.curBlitSrcRect = self.directRect[0]
            self.image = self.spritSurface.subsurface(self.curBlitSrcRect)
            return

        self.passed_time += passtime
        self.frame = (self.passed_time/self._rate) % self.animationCol
        if self.frame == 0 and self.passed_time > self._rate:
            self.passed_time = 0
        self.directRect = self.allFrameRect[self.direction]
        self.curBlitSrcRect = self.directRect[int(self.frame)]
        self.image = self.spritSurface.subsurface(self.curBlitSrcRect)

    def update_lose(self, postion):
        if self.angle > 90:
            #self.angle = 0
            return
        self.directRect = self.allFrameRect[self.direction]
        self.curBlitSrcRect = self.directRect[0]
        self.image = self.spritSurface.subsurface(self.curBlitSrcRect)

        self.angle += 2
        self.image = pygame.transform.rotate(self.image, self.angle)

    def update(self, passed_time, curDirection, postion):
        self.update_image(passed_time, curDirection)
        self.update_pos(postion)


class Role(object):
    def __init__(self, position, direction):
        #self.status     = [ RoleStatus.IDLE, RoleStatus.RUN, RoleStatus.ATTACK ]
        self.curStatus = RoleStatus.IDLE
        self.position = position
        self.speed = 80
        self.direction = direction
        self.health = 100
        self.spriteDict = {RoleStatus.IDLE: None,
                           RoleStatus.RUN: None, RoleStatus.ATTACK: None}

    def addSprite(self, status, sprite):
        self.spriteDict[status] = sprite
        #self.sprite = sprite

    def getDirection(self, pressKey, mouse_move_pos):
        direction = None
        runKeyPress = False

        if pressKey[pygame.K_UP]:
            direction = Direction.UP
            runKeyPress = True
        if pressKey[pygame.K_DOWN]:
            direction = Direction.DOWN
            runKeyPress = True
        if pressKey[pygame.K_LEFT]:
            direction = Direction.LEFT
            runKeyPress = True
        if pressKey[pygame.K_RIGHT]:
            direction = Direction.RIGHT
            runKeyPress = True

        if pressKey[pygame.K_UP] and pressKey[pygame.K_DOWN]:
            direction = self.direction
        if pressKey[pygame.K_LEFT] and pressKey[pygame.K_RIGHT]:
            direction = self.direction

        if(mouse_move_pos[0] > self.position[0]):
            direction = Direction.RIGHT
        else:
            direction = Direction.LEFT

        return direction, runKeyPress

    def clipPosition(self, postion, threshold):
        if(postion[0] < 0):
            postion[0] = 0
        if(postion[1] < 0):
            postion[1] = 0
        if(postion[0] > threshold[0]):
            postion[0] = threshold[0]
        if(postion[1] > threshold[1]):
            postion[1] = threshold[1]

    def updatePosition(self, passTime, pressedKey):
        dis = self.speed*passTime/1000
        if pressedKey[pygame.K_UP]:
            self.position[1] = self.position[1] - dis
        if pressedKey[pygame.K_DOWN]:
            self.position[1] = self.position[1] + dis
        if pressedKey[pygame.K_LEFT]:
            self.position[0] = self.position[0] - dis
        if pressedKey[pygame.K_RIGHT]:
            self.position[0] = self.position[0] + dis
        # print(self.position)

        self.clipPosition(self.position, SCREENSIZE)

    def get_srpite(self):
        return self.sprite

    def update(self, passTime, pressedKey, mouse_move_pos):
        if(self.health <= 0):
            self.sprite.update_lose(passTime)
            return

        direction, runKeyPress = self.getDirection(pressedKey, mouse_move_pos)
        self.status = RoleStatus.IDLE
        if direction:
            self.direction = direction
        if runKeyPress:
            self.status = RoleStatus.RUN

        if pressedKey[pygame.K_a]:
            self.status = RoleStatus.ATTACK

        self.sprite = self.spriteDict[self.status]
        self.updatePosition(passTime, pressedKey)
        self.sprite.update(passTime, self.direction, self.position)


class Enemy(Role):
    def __init__(self, position, direction):
        Role.__init__(self, position, direction)

    def updatePosition(self, passTime):
        self.clipPosition(self.position, SCREENSIZE)

    def update(self, passTime):
        self.status = RoleStatus.RUN
        self.sprite = self.spriteDict[self.status]
        self.updatePosition(passTime)
        self.sprite.update(passTime, self.direction, self.position)

# Skill class


class Skill_Spirte(pygame.sprite.Sprite):
    def __init__(self, screen_surf, skill_surf, skill_rect, init_pos, dst_pos, transColor=None):
        pygame.sprite.Sprite.__init__(self)
        # surface
        self.screen = screen_surf
        self.sprit_surf = skill_surf
        self.skill_rect = skill_rect
        self.skill_numb = len(skill_rect)
        # fps time 200 ms
        self.flush_time = 200
        # color key black
        self.transColor = transColor

        self.init_pos = list(init_pos)
        self.cur_pos = list(init_pos)
        self.speed = 200

        direct_vec = Vector2(dst_pos)-Vector2(init_pos)
        direct_vec[1] = -direct_vec[1]
        self.direct_vec2 = direct_vec.normalize()
        self.angle = Vector2().angle_to(self.direct_vec2)

        self.live_time = 0
        self.live_dis = 0

    def update_pos(self, passtime):
        self.live_dis += self.speed*passtime/1000
        self.cur_pos[0] = self.init_pos[0]+self.live_dis*self.direct_vec2[0]
        self.cur_pos[1] = self.init_pos[1]-self.live_dis*self.direct_vec2[1]

        self.rect = self.image.get_rect()
        #self.rect.move_ip(self.cur_pos[0], self.cur_pos[1])
        self.rect.center = self.cur_pos

    def update_image(self, passtime):
        self.live_time = self.live_time+passtime

        rect_index = int(self.live_time/self.flush_time % self.skill_numb)
        sub_surf = self.sprit_surf.subsurface(self.skill_rect[rect_index])

        rotate_surf = pygame.transform.rotate(sub_surf, 180+self.angle)
        if(self.transColor != None):
            rotate_surf.set_colorkey(self.transColor)

        self.image = rotate_surf

    def update(self, passtime):
        self.update_image(passtime)
        self.update_pos(passtime)


class HealthBar():
    def __init__(self, pos, health, max_health):
        self.pos = pos
        self.health = health
        self.max_health = max_health
        self.width = 60
        self.height = 8

    def draw(self, pos, health):
        self.pos = pos
        self.health = health
        ratio = self.health/self.max_health
        rect = pygame.Rect(0, 0, self.width, self.height)
        rect.center = self.pos
        pygame.draw.rect(SCREEN, RED, rect)
        rect.width *= ratio
        pygame.draw.rect(SCREEN, GREEN, rect)


pygame.init()

screenSurface = pygame.display.set_mode(SCREENSIZE, 0, 32)
SCREEN = screenSurface
pygame.display.set_caption("hello game!")

bgSurface = pygame.image.load(MAPPATH).convert()
clock = pygame.time.Clock()

roleIdleSpirt = Role_Sprit(screenSurface, isIdleSprit=True)
#RoleSpirtPath   = RESOURCEPATH + '/spritZF_run.png'
RoleSpirtPath = RESOURCEPATH + '/player_run.png'
roleIdleSpirt.load(RoleSpirtPath, 4, 4)

roleRunSprit = Role_Sprit(screenSurface)
#RoleSpirtPath   = RESOURCEPATH + '/spritZF_run.png'
RoleSpirtPath = RESOURCEPATH + '/player_run.png'
roleRunSprit.load(RoleSpirtPath, 4, 4)

roleAttackSpirt = Role_Sprit(screenSurface)
roleAttackSpirtPath = RESOURCEPATH + '/spritZF_attack.png'
roleAttackSpirt.load(roleAttackSpirtPath, 4, 4)

Player = Role([200, 200], Direction.UP)
Player.addSprite(RoleStatus.IDLE, roleIdleSpirt)
Player.addSprite(RoleStatus.RUN,  roleRunSprit)
Player.addSprite(RoleStatus.ATTACK,  roleAttackSpirt)

heath_bar = HealthBar(Player.position, 0, Player.health)

enemyIdleSpirt = Role_Sprit(screenSurface)
enemySpirtPath = RESOURCEPATH + '/archer.png'
enemyIdleSpirt.load(enemySpirtPath, 4, 4)
enemy = Enemy([300, 200], Direction.LEFT)
enemy.addSprite(RoleStatus.RUN, enemyIdleSpirt)


# Skill rect
skill_rect = []
skill_split_w = 60
skill_split_h = 50
skill_col = 4
for i in range(0, skill_col):
    skill_rect.append(pygame.Rect(skill_split_w*i, 0,
                      skill_split_w, skill_split_h))

transColor = pygame.Color(0, 0, 0)
surf_skill = pygame.image.load(RESOURCEPATH+'/skill.png').convert()
# print(skill_rect)

enemy_skill_rect = []
enemy_skill_rect.append([0, 0, 50, 10])
enemy_skill_surf = pygame.image.load(RESOURCEPATH+'/arrow.png').convert()


Role_sprits = pygame.sprite.Group()
skills = pygame.sprite.Group()

enemy_sprits = pygame.sprite.Group()
enemy_skills = pygame.sprite.Group()

mouse_move_pos = SCREENSIZE

while True:
    screenSurface.blit(bgSurface, (0, 0))
    direction = None
    Passtime = clock.tick(60)

# event loop
    for event in pygame.event.get():
        # print(event)
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
        if event.type == MOUSEMOTION:
            mouse_move_pos = event.pos
            # print(mouse_move_pos)

        if event.type == MOUSEBUTTONDOWN:

            shoot_skill = Skill_Spirte(
                screenSurface, surf_skill, skill_rect, Player.position, event.pos, transColor)
            skills.add(shoot_skill)

            enemy_skill = Skill_Spirte(screenSurface, enemy_skill_surf, enemy_skill_rect,
                                       enemy.position, Player.position, pygame.Color(255, 255, 255))
            enemy_skills.add(enemy_skill)


# update
    Key = pygame.key.get_pressed()
    Player.update(Passtime, Key, mouse_move_pos)
    player_sprit = Player.get_srpite()
    Role_sprits.empty()
    Role_sprits.add(player_sprit)

    for skill in skills:
        if skill.live_dis > 200:
            skills.remove(skill)
        skill.update(Passtime)

    enemy.update(Passtime)
    enemy_sprits.add(enemy.get_srpite())

    for skill in enemy_skills:
        if skill.live_dis > 200:
            enemy_skills.remove(skill)
        enemy_skills.update(Passtime)


# render
    Role_sprits.draw(screenSurface)
    skills.draw(screenSurface)
    enemy_sprits.draw(screenSurface)
    enemy_skills.draw(screenSurface)

    skill_hit = pygame.sprite.spritecollide(
        Player.get_srpite(), enemy_skills, 0)
    if skill_hit:
        print("被射中啦")
        Player.health -= 10
        Player.health = max(Player.health, 0)
    for sp in skill_hit:
        sp.kill()
        print(sp.rect)
        del(sp)

    heath_bar.draw(Player.get_srpite().rect.midtop, Player.health)

    pygame.display.update()
