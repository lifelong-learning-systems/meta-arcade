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

# rectangluar game element with bounding box, position, velocity

class GameElement():

    def __init__(self, x=0, y=0, w=0, h=0, vx=0.0, vy=0.0, 
        fill=[255,255,255], stroke=[255,255,255], centered=False, 
        size_protection=True, prng=None):

        self.x = x
        self.y = y

        self.w = w
        self.h = h
        if size_protection:
            self.w = max(w, 0.01) #protection against bad sampling
            self.h = max(h, 0.01) #protection against bad sampling

        if centered:
            self.x -= self.w * 0.5
            self.y -= self.h * 0.5

        self.ox = self.x
        self.oy = self.y

        self.vx = vx
        self.vy = vy

        self.fill = fill
        self.stroke = stroke
        self.active = True

        self.collision_adjust = 0.0
        self.show_bbox = False

        if prng is None:
            self.prng = random.Random()
        else:
            self.prng = prng

    # updates this object's velocity and then returns any changes to reward
    # game over will be determined from this, i.e. -100 pts implies game over
    def subtick(self, game_elements):

        # for subclasses: iterate through game elements and check for collisions, 
        # then respond appropriately by changing velocity and/or destroying the other element
        # these should be check from only one side: ball should check for paddle collisions
        return 0.0


    def tick(self):
        self.x += self.vx
        self.y += self.vy


    def render(self, display):
        if not self.active: return
        self.draw(display)

        if self.show_bbox:
            pygame.draw.rect(display.display, [255,0,0], pygame.Rect(*display.cvtRect(self.x+self.collision_adjust, 
                self.y+self.collision_adjust, 
                self.w-self.collision_adjust-self.collision_adjust, 
                self.h-self.collision_adjust-self.collision_adjust)), 2)

    def draw(self, display):
        pygame.draw.rect(display.display, self.fill, pygame.Rect(*display.cvtRect(self.x, self.y, self.w, self.h)))
        
        # there's some sort of incompatability here for pygame 1 vs 2
        # pygame.draw.rect(display.display, self.stroke, pygame.Rect(*display.cvtRect(self.x, self.y, self.w, self.h)), 2)


    def reset(self):
        self.active = True
        self.x = self.ox
        self.y = self.oy
        self.vx, self.vy = 0.0, 0.0
        

    def destroy(self):
        self.active = False


    def check_collision(self, other, propogate_x=False, propogate_y=False):

        if not (self.active and other.active): return False

        l1 = [self.x + self.collision_adjust, self.y + self.collision_adjust]
        r1 = [self.x + self.w - self.collision_adjust, self.y + self.h - self.collision_adjust]
        l2 = [other.x + other.collision_adjust, other.y + other.collision_adjust]
        r2 = [other.x + other.w - other.collision_adjust, other.y + other.h - other.collision_adjust]

        if propogate_x:
            l1[0] += self.vx
            r1[0] += self.vx

        if propogate_y:
            l1[1] += self.vy
            r1[1] += self.vy

        # project the other object forward in time
        if propogate_x or propogate_y:
            l2[0] += other.vx
            l2[1] += other.vy
            r2[0] += other.vx
            r2[1] += other.vy

        # If one rectangle is on left side of other 
        if(l1[0] >= r2[0] or l2[0] >= r1[0]): 
            return False
      
        # If one rectangle is above other 
        if(l1[1] >= r2[1] or l2[1] >= r1[1]): 
            return False

        return True