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

import numpy as np
import cv2
import pygame
import imageio
import copy
from meta_arcade.Elements import Wall

# this class handles rendering to the screen and creation of the gym image state

class GameDisplay():

    def __init__(self, headless=False, w=250, h=250, episode_as_gif_path=None):

        pygame.display.init()
        self.w, self.h = w, h
        self.display_size = [w,h]

        self.display = pygame.display.set_mode((int(self.display_size[0]),int(self.display_size[1])), 0, 32)
        self.episode_as_gif_path = episode_as_gif_path
        self.highres_frame_buffer = []

        #load the wall mask teture
        self.wall_texture_surf = pygame.surface.Surface((w, h), pygame.SRCALPHA)
        self.wall_texture_surf_masked = pygame.surface.Surface((w, h), pygame.SRCALPHA)

    def compute_wall_mask(self, game_elements, stripe_clr):

        # fill wall surf with transparency
        self.wall_texture_surf.fill([0,0,0,0])
        self.wall_texture_surf_masked.fill([0,0,0,0])

        # stripes!
        s = 40
        for i in range(s):
            p1 = [0,int((i/(s-1))*self.h*2)]
            p2 = [int((i/(s-1))*self.h*2), 0]
            pygame.draw.line(self.wall_texture_surf, stripe_clr+[255], p1, p2, 6)

        # draw the walls
        for g in game_elements:
            if isinstance(g, Wall):
                rect = self.cvtRect(g.x, g.y, g.w, g.h)
                self.wall_texture_surf_masked.blit(self.wall_texture_surf, rect, area=rect)


    def prepare_render(self, bg_color):
        pygame.draw.rect(self.display, bg_color, pygame.Rect(0.0, 0.0, self.display_size[0], self.display_size[1]))


    def complete_render(self, score, actions_config, ui1, ui2, ui3):

        #display the wall texture mask
        self.display.blit(self.wall_texture_surf_masked, (0,0))

        #display game progress
        pygame.draw.rect(self.display, ui1, 
            pygame.Rect(0.0, 0.0, self.display_size[0], self.display_size[1]*0.07))

        y = self.display_size[1]*0.02
        h = self.display_size[1]*0.03
        w = int(self.display_size[0]*abs(score)/100.0)*0.98

        pygame.draw.rect(self.display, ui3, pygame.Rect(*self.cvtRect(0.01,0.02,0.98,0.03)))

        if score>2.0:
            x = 0.01
            pygame.draw.rect(self.display, ui2, pygame.Rect(x, y, w, h))


        # display available actions
        pygame.draw.rect(self.display, ui1, 
            pygame.Rect(0.0, self.display_size[1]*0.93, self.display_size[0], self.display_size[1]*0.08))

        for i,a in enumerate(["up", "down", "left", "right", "fire"]):

            x = self.display_size[0]*((float(i)/5.0)+0.02)
            y = self.display_size[1]*0.95
            w = self.display_size[0]*(0.2 - 0.02*2)
            h = self.display_size[1]*0.03

            if actions_config[a]:
                pygame.draw.rect(self.display, ui2, pygame.Rect(x, y, w, h))
            pygame.draw.rect(self.display, ui3, pygame.Rect(x, y, w, h), 2)



        pygame.display.update()


    def image_state(self, invert=False, rotation=0, hshift=0.0, sshift=0.0, vshift=0.0):

        # get pixels and resize
        ra = pygame.surfarray.array3d(pygame.display.get_surface())
        ra = np.transpose(ra, (1,0,2))
        ra = np.flip(ra, axis=2)

        # resize here for efficiency of not saving high res imagery
        if self.episode_as_gif_path is None:
            ra = cv2.resize(ra, (84,84))

        # get normalized hsv
        image = ra
        hsv_image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV) #hsv image with values [0-179, 0-255, 0-255]
        h, s, v = hsv_image[:,:,0], hsv_image[:,:,1], hsv_image[:,:,2]
        h = h.astype(np.float32) / 179.0
        s = s.astype(np.float32) / 255.0
        v = v.astype(np.float32) / 255.0

        # apply hsv shifts
        h = np.mod(h + hshift, 1.0)
        s = np.clip(s + sshift, 0.0, 1.0)
        v = np.clip(v + vshift, 0.0, 1.0)

        #convert back to [0-255] rgb
        hsv_image = np.asarray([h*179.0,s*255.0,v*255.0])
        hsv_image = np.transpose(hsv_image, (1,2,0))
        ra = cv2.cvtColor(hsv_image.astype(np.uint8), cv2.COLOR_HSV2RGB)
        ra = ra.astype(np.float32)

        if invert:
            ra = 255.0 - ra

        if rotation!=0:
            ra = np.rot90(ra, rotation)

        ra = ra.astype(np.uint8)

        # save and resize
        if self.episode_as_gif_path is not None:
            self.highres_frame_buffer.append(copy.deepcopy(ra))
            ra = cv2.resize(ra, (84,84))

        return ra


    def cvtX(self, x):
        return int(x*self.display_size[0])

    def cvtY(self, y):
        return int(y*self.display_size[1])

    def cvtPoint(self, x, y):
        return (self.cvtX(x), self.cvtY(y))

    def cvtRect(self, x, y, w, h):
        x = int(x*self.display_size[0])
        y = int(y*self.display_size[1])
        w = int(w*self.display_size[0])
        h = int(h*self.display_size[1])
        w = max(w,1) #make sure size is at least 1 pixel
        h = max(h,1) #make sure size is at least 1 pixel
        return x, y, w, h

    # save the frames of this episode to a gif and clear buffer
    def buffer_to_gif(self):
        if self.episode_as_gif_path is not None:
            imageio.mimsave(self.episode_as_gif_path, self.highres_frame_buffer, duration=0.01)
            self.highres_frame_buffer = []