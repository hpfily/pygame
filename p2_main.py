# -*- coding:utf-8 -*-
import pygame
from pygame import *
from sys import exit
from os import getcwd
import menu

import socket
import utils

from enum import Enum

SCREEN = None
SCREENSIZE = (1000, 600)
RESOURCEPATH = getcwd() + '/pic'
print(RESOURCEPATH)
MAPPATH = RESOURCEPATH + '/bg2.jpg'

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

_KEYUP = int(0)
_KEYDOWN = int(1)
_KEYLEFT = int(2)
_KEYRIGHT = int(3)
_KEYNUM = 4

KEY_MAP = []


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

        self.end=0

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
            self.end=1
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
        self.mov_vec = [0, 0]

    def addSprite(self, status, sprite):
        self.spriteDict[status] = sprite
        #self.sprite = sprite

    def getDirection(self, pressKey, mouse_move_pos):
        direction = None
        runKeyPress = False

        if pressKey[_KEYUP]:
            self.mov_vec[1] = -1
            runKeyPress = True
        if pressKey[_KEYDOWN]:
            self.mov_vec[1] = 1
            runKeyPress = True
        if pressKey[_KEYLEFT]:
            self.mov_vec[0] = -1
            runKeyPress = True
        if pressKey[_KEYRIGHT]:
            self.mov_vec[0] = 1
            runKeyPress = True

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
        self.position[0] = self.position[0] + dis*self.mov_vec[0]
        self.position[1] = self.position[1] + dis*self.mov_vec[1]
        self.mov_vec = [0, 0]

        self.clipPosition(self.position, SCREENSIZE)

    def get_srpite(self):
        return self.sprite

    def update(self, passTime, pressedKey, mouse_move_pos, health):
        self.health = health
        if(self.health <= 0):
            self.sprite.update_lose(passTime)
            return

        direction, runKeyPress = self.getDirection(pressedKey, mouse_move_pos)
        self.status = RoleStatus.IDLE
        if direction:
            self.direction = direction
        if runKeyPress:
            self.status = RoleStatus.RUN

        # if pressedKey[pygame.K_a]:
        #     self.status = RoleStatus.ATTACK

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
        self.flush_time = 100
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
        rect = pygame.Rect(0, 0, self.width, self.height)
        rect.center = self.pos

        pygame.draw.rect(SCREEN, RED, rect)
        self.health = health
        if health > 0:
            ratio = self.health/self.max_health
            rect.width *= ratio
            pygame.draw.rect(SCREEN, GREEN, rect)


def game_start(server_addr,player_name):

    pygame.init()

    #print(player_name)
    # network
    s = socket.socket()
    s.connect(server_addr)
    print(s.recv(1024).decode(encoding='utf8'))

    screenSurface = pygame.display.set_mode(SCREENSIZE, 0, 32)
    global SCREEN
    SCREEN = screenSurface
    pygame.display.set_caption("HongHu Smash! P1")

    bgSurface = pygame.image.load(MAPPATH).convert()
    clock = pygame.time.Clock()

    p1_SpirtPath = RESOURCEPATH + '/player_run.png'
    p1_IdleSpirt = Role_Sprit(screenSurface, isIdleSprit=True)
    p1_IdleSpirt.load(p1_SpirtPath, 4, 4)
    p1_RunSprit = Role_Sprit(screenSurface)
    p1_RunSprit.load(p1_SpirtPath, 4, 4)

    # roleAttackSpirt = Role_Sprit(screenSurface)
    # roleAttackSpirtPath = RESOURCEPATH + '/spritZF_attack.png'
    # roleAttackSpirt.load(roleAttackSpirtPath, 4, 4)

    p1_pos = [250, 300]
    p1_player = Role(p1_pos, Direction.RIGHT)
    p1_player.addSprite(RoleStatus.IDLE, p1_IdleSpirt)
    p1_player.addSprite(RoleStatus.RUN,  p1_RunSprit)
    #Player.addSprite(RoleStatus.ATTACK,  roleAttackSpirt)

    p2_SpirtPath = RESOURCEPATH + '/playe2.png'
    p2_IdleSpirt = Role_Sprit(screenSurface, isIdleSprit=True)
    p2_IdleSpirt.load(p2_SpirtPath, 4, 4)
    p2_RunSpirt = Role_Sprit(screenSurface)
    p2_RunSpirt.load(p2_SpirtPath, 4, 4)

    p2_pos = [800, 300]
    p2_player = Role(p2_pos, Direction.LEFT)
    p2_player.addSprite(RoleStatus.IDLE, p2_IdleSpirt)
    p2_player.addSprite(RoleStatus.RUN, p2_RunSpirt)

    p1_health_bar = HealthBar(p1_player.position, 0, p1_player.health)
    p2_health_bar = HealthBar(p2_player.position, 0, p2_player.health)

    # Skill
    transColor = pygame.Color(0, 0, 0)
    surf_skill = pygame.image.load(RESOURCEPATH+'/skill.png').convert()

    skill_split_w = 50
    skill_split_h = 45
    skill_col = 4
    p1_skill_rect = []
    for i in range(0, skill_col):
        p1_skill_rect.append(pygame.Rect(30+skill_split_w*i,
                                         305, skill_split_w, skill_split_h))

    skill_split_w = 60
    skill_split_h = 50
    p2_skill_rect = []
    for i in range(0, skill_col):
        p2_skill_rect.append(pygame.Rect(skill_split_w*i, skill_split_h,
                                         skill_split_w, skill_split_h))

    p1_role_group = pygame.sprite.Group()
    p1_skill_group = pygame.sprite.Group()

    p2_role_group = pygame.sprite.Group()
    p2_skill_group = pygame.sprite.Group()

    mouse_move_pos = SCREENSIZE

    # bgm
    pygame.mixer.init()
    pygame.mixer.music.load(RESOURCEPATH + '/bgm2.mp3')
    pygame.mixer.music.play(1, 0)

    while True:
        screenSurface.blit(bgSurface, (0, 0))
        direction = None
        Passtime = clock.tick(60)

        KEY_MAP = [0]*_KEYNUM
        mouse_down_pos = 0
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

            if event.type == MOUSEBUTTONDOWN:
                mouse_down_pos = event.pos

    # update
        Key = pygame.key.get_pressed()
        if Key[pygame.K_UP]:
            KEY_MAP[_KEYUP] = True
        if Key[pygame.K_DOWN]:
            KEY_MAP[_KEYDOWN] = True
        if Key[pygame.K_LEFT]:
            KEY_MAP[_KEYLEFT] = True
        if Key[pygame.K_RIGHT]:
            KEY_MAP[_KEYRIGHT] = True

        data = utils.packSocketData(
            {'id': 'p2', 'key': KEY_MAP, 'mouse_move_pos': mouse_move_pos, 'mouse_down_pos': mouse_down_pos, 'player_health': p2_player.health,'player_name':player_name})

        s.send(data)
        data_recv = utils.receiveAndReadSocketData(s)

        # print(data_recv)
        # Passtime=data_recv['passtime']
        p1_player.update(Passtime, data_recv['p1_key'],
                         data_recv['p1_mouse_move_pos'], data_recv['p1_player_health'])
        p2_player.update(
            Passtime, data_recv['p2_key'], data_recv['p2_mouse_move_pos'], data_recv['p2_player_health'])

        if data_recv['p1_mouse_down_pos'] != 0:
            p1_skill = Skill_Spirte(
                screenSurface, surf_skill, p1_skill_rect, p1_player.position, data_recv['p1_mouse_down_pos'], transColor)
            p1_skill_group.add(p1_skill)

        if data_recv['p2_mouse_down_pos'] != 0:
            p2_skill = Skill_Spirte(screenSurface, surf_skill, p2_skill_rect,
                                    p2_player.position, data_recv['p2_mouse_down_pos'], transColor)
            p2_skill_group.add(p2_skill)

        p1_role_group.empty()
        p1_role_group.add(p1_player.get_srpite())

        p2_role_group.empty()
        p2_role_group.add(p2_player.get_srpite())

        skill_range = 200
        for skill in p1_skill_group:
            if skill.live_dis > skill_range:
                p1_skill_group.remove(skill)
            skill.update(Passtime)
        for skill in p2_skill_group:
            if skill.live_dis > skill_range:
                p2_skill_group.remove(skill)
            skill.update(Passtime)

    # skill hit
        # p1 hit
        skill_hit = pygame.sprite.spritecollide(
            p1_player.get_srpite(), p2_skill_group, 0)
        if skill_hit:
            # print("p1被射中啦")
            p1_player.health -= 10
            p1_player.health = max(p1_player.health, 0)
        for sp in skill_hit:
            sp.kill()
            #print(sp.rect)
            del(sp)
        # p2 hit
        skill_hit = pygame.sprite.spritecollide(
            p2_player.get_srpite(), p1_skill_group, 0)
        if skill_hit:
            # print("p2被射中啦")
            p2_player.health -= 10
            p2_player.health = max(p2_player.health, 0)
        for sp in skill_hit:
            sp.kill()
            #print(sp.rect)
            del(sp)

    # render
        p1_role_group.draw(screenSurface)
        p1_skill_group.draw(screenSurface)
        p2_role_group.draw(screenSurface)
        p2_skill_group.draw(screenSurface)

        p1_health_bar.draw(
            p1_player.get_srpite().rect.midtop, p1_player.health)
        p2_health_bar.draw(
            p2_player.get_srpite().rect.midtop, p2_player.health)

        p1_name=data_recv['player_name1']
        p2_name=data_recv['player_name2']

        font1 = pygame.font.SysFont('Arial', 10)
        font1.set_bold(True)
        p1_text = font1.render(p1_name, True, GREEN)
        rect = p1_text.get_rect()
        rect.center = p1_player.get_srpite().rect.midbottom
        screenSurface.blit(p1_text, rect)

        p2_text = font1.render(p2_name, True, BLUE)
        rect = p2_text.get_rect()
        rect.center = p2_player.get_srpite().rect.midbottom
        screenSurface.blit(p2_text, rect)
        
        if(p2_player.get_srpite().end):
                menu.show_text_dialog('info','You Lose')
                break
        if(p1_player.get_srpite().end):
                menu.show_text_dialog('info','You Win')
                break

        pygame.display.update()


if __name__ == '__main__':
    game_start()
