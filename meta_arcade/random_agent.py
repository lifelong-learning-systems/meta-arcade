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
import numpy as np

# =====================================================
# code to play randomly

def random_agent(env, episodes=1000000, steps=None, delay=0.0):

    stps = 0

    for _ in range(episodes):
        env.reset()
        done = False
        ep_steps = 0
        ep_score = 0.0
        while not done:
            stps += 1
            a = env.action_space.sample()
            s, r, done, info = env.step(a)
            ep_steps += 1
            ep_score += r

            if r != 0.0 or done:
                print("Cumulative score:", ep_score, "Steps:", ep_steps)

            if delay>0.0:
            	time.sleep(delay)

            if steps is not None:
                if stps >= steps:
                    return




# play randomly and compile the first frame of each episode into an image
# this is a useful utility for visualizing curriculums or domain randomization
def get_first_frames(env, episodes, rows=1, udlr=False, capture_wait=0):

    frames = []
    for e in range(episodes):
        print("Running episode", e, "of", episodes)
        s = env.reset()
        done = False
        timedown = capture_wait
        while not done:
            if timedown==0:
                frames.append(s)
            timedown -= 1
            a = env.action_space.sample()
            s, r, done, info = env.step(a)


    cols = int(np.ceil(episodes/rows))
    image = np.zeros((rows*84, cols*84, 3), dtype=np.uint8)

    r, c = 0,0
    for f in frames:

        image[r*84:(r+1)*84, c*84:(c+1)*84, :] = f

        if udlr:
            # move down, then left if needed
            r += 1
            if r>= rows:
                r = 0
                c += 1
        else:
            # move left, then down if needed
            c += 1
            if c>= cols:
                c = 0
                r += 1

    cv2.imshow("frames", image[:,:,::-1])
    cv2.waitKey(0)