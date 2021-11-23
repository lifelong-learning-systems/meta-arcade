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



# code to play a game as a human with arrow keys and spacebar
# could be wrapped up in a class in the future

from meta_arcade.MetaArcade import MetaArcade
import pygame
import time
import cv2

# =====================================================
# code to play as human

def human_agent(env):

    K_LEFT = False
    K_RIGHT = False
    K_UP = False
    K_DOWN = False
    K_SPACE = False

    while True:

        env.reset()
        delay = 8
        done = False
        score = 0.0
        steps = 0
        while not done:

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: K_LEFT = True
                    if event.key == pygame.K_RIGHT: K_RIGHT = True
                    if event.key == pygame.K_UP: K_UP = True
                    if event.key == pygame.K_DOWN: K_DOWN = True
                    if event.key == pygame.K_SPACE: K_SPACE = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT: K_LEFT = False
                    if event.key == pygame.K_RIGHT: K_RIGHT = False
                    if event.key == pygame.K_UP: K_UP = False
                    if event.key == pygame.K_DOWN: K_DOWN = False
                    if event.key == pygame.K_SPACE: K_SPACE = False

                    # reset override
                    if event.key == pygame.K_r: done=True

            a = 0
            if K_UP: a=1
            elif K_DOWN: a=2
            elif K_LEFT: a=3
            elif K_RIGHT: a=4
            elif K_SPACE: a=5


            s, r, d, info = env.step(a)
            if d:
                done=True
            score += r
            steps += 1

            if r != 0.0:
                print("Cumulative score:", score, "Steps:", steps)

            # cv2.namedWindow("state", cv2.WINDOW_NORMAL) 
            # cv2.imshow("state", s[:,:,::-1])
            # cv2.waitKey(1)

            time.sleep(0.015 + delay*0.005)
            if delay>0:
                delay -= 1

