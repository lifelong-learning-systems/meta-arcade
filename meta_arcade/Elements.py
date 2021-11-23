"""
Copyright © 2021 The Johns Hopkins University Applied Physics Laboratory LLC
 
Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the “Software”), to 
deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR 
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pygame
import random
import math
import numpy as np
from meta_arcade.GameElement import GameElement



class Player(GameElement):

    def __init__(self, w, h, speed, color=[255,255,255], shoots=False, steering=0.0, prng=None):

        x = 0.5 - w*0.5
        y = 0.88 - h
        super().__init__(x, y, w, h, fill=color, stroke=color, prng=prng)
        self.speed = speed
        self.shoots = shoots
        self.steering = steering


    def draw(self, display):
        super().draw(display)

        if self.shoots:
            tw = 0.01
            x = self.x + self.w*0.5 - tw
            y = self.y - 0.02
            w = tw*2
            h = 0.03
            pygame.draw.rect(display.display, self.fill, pygame.Rect(*display.cvtRect(x, y, w, h)))


    def subtick(self, game_elements):

        for e in game_elements:

            # walls
            if isinstance(e, Wall):
                if self.check_collision(e, propogate_x=True): self.vx *= 0.0
                if self.check_collision(e, propogate_y=True): self.vy *= 0.0

            # enemy bullet
            if isinstance(e, RedBullet):
                if self.check_collision(e):
                    return -100.0


        #game over
        if self.y > 0.92:
            return -100.0
        elif self.y<(-self.h+0.08):
            return 100.0
        else:
            return 0.0


class Opponent(GameElement):

    def __init__(self, w, h, speed, color=[209, 46, 73], skill=0.5, tracks_ball=True, 
        shoots=False, prng=None):

        x = 0.5 - w*0.5
        y = 0.12
        super().__init__(x, y, w, h, fill=color, stroke=color, prng=prng)

        self.speed = speed
        self.skill = skill
        self.tracks_ball = tracks_ball
        self.shoots = shoots

        self.state = -1


    def draw(self, display):
        super().draw(display)

        if self.shoots:
            tw = 0.01
            x = self.x + self.w*0.5 - tw
            y = self.y + self.h - 0.01
            w = tw*2
            h = 0.03
            pygame.draw.rect(display.display, self.fill, pygame.Rect(*display.cvtRect(x, y, w, h)))


    def react_to_bullet(self, e):

        #bullet to the right, move left (not urgent)
        if e.x > self.x+self.w:
            return -1, False

        # bullet to the left, move right (not urgent)
        elif e.x+e.w < self.x:
            return 1, False

        # bullet on collision path, move to open space urgently
        else:
            if e.x + e.w*0.5 > 0.5:
                return -1, True
            else:
                return 1, True


    def subtick(self, game_elements):

        enemy_bullet = None
        ball = None
        for e in game_elements:
            if isinstance(e, BlueBullet):
                enemy_bullet = e
            if isinstance(e, Ball):
                ball = e

        if not self.tracks_ball:
            if self.prng.random() < 0.05:
                self.state = self.prng.choice([-1,0,1])

                # avoid bullets (no ball tracking case)
                if enemy_bullet is not None and enemy_bullet.active and self.prng.random()<self.skill:
                    self.state, _ = self.react_to_bullet(enemy_bullet)

            self.vx = self.speed * self.state


        for e in game_elements:

            # walls
            if isinstance(e, Wall):
                if self.check_collision(e, propogate_x=True): 
                    self.vx *= 0.0
                    break
                if self.check_collision(e, propogate_y=True): 
                    self.vy *= 0.0
                    break

            # track ball
            if self.tracks_ball:
                if isinstance(e, Ball):
                    if self.prng.random() < self.skill:
                        #move towards ball
                        if e.x+(e.w*0.5) > self.x+(self.w*0.5):
                            self.vx = self.speed
                        else:
                            self.vx = -self.speed
                    else:
                        #move randomly
                        self.vx = self.prng.choice([-1,1])*self.speed

            # avoid bullets with ball tracking
            if self.tracks_ball and isinstance(e, BlueBullet) and e.active:

                if self.prng.random() < self.skill and abs(e.y-self.y)<0.2:
                    #move away from bullet
                    state, urgent = self.react_to_bullet(e)

                    #if urgent or ball moving safely away, react to bullet
                    if urgent:
                        self.vx = self.speed*state
                    elif ball.vy > 0.0:
                        self.vx = self.speed*state

            if isinstance(e, RedBullet):
                if not e.active:
                    if self.prng.random() < 0.005:
                        e.activate(self.x + (self.w*0.5), self.y + self.h)

            if isinstance(e, BlueBullet):
                if self.check_collision(e):
                    return 100.0

        return 0.0


class Ball(GameElement):

    def __init__(self, w, speed, color=[255, 192, 56], harmful=False, prng=None):
        super().__init__(0.5, 0.5, w, w, fill=color, stroke=color, centered=True, prng=prng)
        self.speed = speed
        self.collision_adjust = 0.005
        self.harmful = harmful


    def reset(self):
        super().reset()
        angle = self.prng.choice([1.05, 2.1]) + self.prng.uniform(-0.25, 0.25)
        self.vx = self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)


    def draw(self, display):
        r = display.cvtX(self.w*0.5)

        if self.harmful:

            w = (2 if r>= 2 else 1)
            w = max(w, 1)
            pygame.draw.circle(display.display, self.stroke, display.cvtPoint(self.x+self.w*0.5, self.y+self.w*0.5), r, w)
            # pygame.draw.line(display.display, self.stroke, display.cvtPoint(p1x,p1y), display.cvtPoint(p2x,p2y), 1)
            # pygame.draw.line(display.display, self.stroke, display.cvtPoint(p3x,p3y), display.cvtPoint(p4x,p4y), 1)

        else:
            pygame.draw.circle(display.display, self.fill, display.cvtPoint(self.x+self.w*0.5, self.y+self.w*0.5), r)
            w = (2 if r>= 2 else 1)
            pygame.draw.circle(display.display, self.stroke, display.cvtPoint(self.x+self.w*0.5, self.y+self.w*0.5), r, w)


    def subtick(self, game_elements):

        block_collisions = 0.0
        for e in game_elements:

            # walls
            if isinstance(e, Wall):
                # if embedded in a wall we need to just keep moving to get out of it:
                if not self.check_collision(e):
                    if self.check_collision(e, propogate_x=True): self.vx *= -1.0
                    if self.check_collision(e, propogate_y=True): self.vy *= -1.0

            # blocks
            if isinstance(e, Block) and e.alive:
                # if embedded in a block we need to just keep moving to get out of it:
                if not self.check_collision(e):

                    cardinal_collision = False
                    if self.check_collision(e, propogate_x=True): 
                        self.vx *= -1.0
                        if not self.harmful and not e.bad:
                            cardinal_collision = True
                            e.alive = False
                            e.destroy()
                            block_collisions += e.worth
                    if self.check_collision(e, propogate_y=True): 
                        self.vy *= -1.0
                        if not self.harmful and not e.bad:
                            cardinal_collision = True
                            e.alive = False
                            e.destroy()
                            block_collisions += e.worth

                    #check diagonal collision
                    if not cardinal_collision and self.check_collision(e,propogate_x=True,propogate_y=True):
                        self.vx *= -1.0
                        self.vy *= -1.0
                        if not self.harmful and not e.bad:
                            cardinal_collision = True
                            e.alive = False
                            e.destroy()
                            block_collisions += e.worth
            # paddle
            if isinstance(e, Player):

                # check x-direction collisions if ball is harmful
                if self.check_collision(e, propogate_x=True) and self.harmful: 
                    return -100.0

                if self.check_collision(e, propogate_y=True) and self.vy>0.0: 

                    if self.harmful:
                        return -100.0

                    # what is the deflection angle?
                    # if 0% steering, the angle is:
                    zero_steer_angle = math.atan2(-self.vy, self.vx)

                    # if full steering, the angle is a function of the lateral position relative to paddle
                    delta = ((self.x+(self.w*0.5)) - (e.x))/e.w
                    delta = np.clip(delta, 0, 1)
                    cone = 3.141592 * 0.6
                    full_steer_angle = (delta-0.5)*cone - (3.141592*0.5)

                    # weighted average between the two directions
                    final_angle = full_steer_angle*e.steering + zero_steer_angle*(1.0-e.steering)
                    magnitude = math.sqrt(self.vx*self.vx + self.vy*self.vy)
                    self.vx = math.cos(final_angle)*magnitude
                    self.vy = math.sin(final_angle)*magnitude

            # opponent
            if isinstance(e, Opponent):
                if self.check_collision(e, propogate_y=True) and self.vy<0.0: self.vy *= -1.0

        #game over
        if self.y > 1.0:
            return -100.0
        elif self.y<(-self.w):
            return 100.0
        else:
            if block_collisions > 0.0:
                return block_collisions
            return 0.0


class Wall(GameElement):
    def __init__(self, x, y, w, h, color=[141, 165, 204], centered=False):
        super().__init__(x, y, w, h, fill=color, stroke=color, centered=centered)

    def reset(self):
        self.x, self.y = self.ox, self.oy
        self.vx = 0
        self.vy = 0

    def configure(self, x=0, y=0, w=1, h=1, color=[255,255,255]):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.ox, self.oy = x, y
        self.fill, self.stroke = color, color

    def draw(self, display):
        pygame.draw.rect(display.display, self.fill, pygame.Rect(*display.cvtRect(self.x, self.y, self.w, self.h)))


class Block(GameElement):
    def __init__(self, x, y, w, h, **kwargs):
        super().__init__(x, y, w, h, **kwargs)
        self.alive = True
        self.bad = False
        self.worth = 1.0

    def reset(self):
        self.active = True
        self.x, self.y, self.w, self.h = 100,100,0,0
        self.vx = 0
        self.vy = 0

    def configure(self, x=0, y=0, w=1, h=1, vx=0, vy=0, worth=1.0, bad=False, fall_points=-100, color=[255,255,255]):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.vx, self.vy = vx, vy
        self.ox, self.oy = x, y
        self.fill, self.stroke = color, color
        self.alive = True
        self.bad = bad
        self.worth = worth
        self.fall_points = fall_points

    def subtick(self, game_elements):

        if self.vx > 0.0 and self.x > 1.0:
            self.x = -self.w
            self.alive = True
        elif self.vx < 0.0 and self.x<-self.w:
            self.x = 1.0
            self.alive = True
        elif self.vy > 0.0 and self.y>1.0:
            self.y = 0.0 - self.h
            if self.alive:
                return self.fall_points
            self.alive = True

        if not self.alive:
            return 0.0

        for e in game_elements:

            # paddle
            if isinstance(e, Player):
                if self.check_collision(e):
                    self.alive = False
                    if self.bad:
                        return -100.0
                    return self.worth

            # bullet
            if isinstance(e, BlueBullet):
                if self.check_collision(e):
                    self.alive = False
                    e.active = False
                    return self.worth

            if isinstance(e, RedBullet):
                if self.check_collision(e):
                    self.alive = False
                    e.active = False
                    return 0.0



        return 0.0

    def draw(self, display):
        if self.alive:
            if self.bad:
                w = 3
                pygame.draw.rect(display.display, self.stroke, 
                    pygame.Rect(*display.cvtRect(self.x, self.y, self.w, self.h)), w)
                pygame.draw.line(display.display, self.stroke, 
                    display.cvtPoint(self.x, self.y), display.cvtPoint(self.x+self.w, self.y+self.h), w)
                pygame.draw.line(display.display, self.stroke, 
                    display.cvtPoint(self.x+self.w, self.y), display.cvtPoint(self.x, self.y+self.h), w)
            else:
                super().draw(display)


class BlueBullet(GameElement):
    
    def __init__(self, color):
        super().__init__(-0.5,0.5,0.02,0.04, fill=color, stroke=color)
        self.active = False
    
    def reset(self): 
        self.active = False
        self.x = 100.0
        self.vy = -0.01

    def activate(self, cx, cy):
        self.active = True
        self.x = cx - self.w*0.5
        self.y = cy - self.h*0.5

    def subtick(self, game_elements):
        if self.y < -self.h:
            self.active = False

        for e in game_elements:
            if isinstance(e, Wall):
                if self.check_collision(e):
                    self.active = False

        return 0.0



class RedBullet(GameElement):
    
    def __init__(self, color):
        super().__init__(-0.5,0.5,0.02,0.04, fill=color, stroke=color)
        self.active = False
    
    def reset(self):
        self.active = False
        self.x = 100.0
        self.vy = 0.01

    def activate(self, cx, cy):
        self.active = True
        self.x = cx - self.w*0.5
        self.y = cy - self.h*0.5

    def subtick(self, game_elements):
        if self.y > 1.0:
            self.active = False

        for e in game_elements:
            if isinstance(e, Wall):
                if self.check_collision(e):
                    self.active = False

        return 0.0