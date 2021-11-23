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

import gym
import numpy as np
import cv2
import os

from meta_arcade.Elements import *
from meta_arcade.Config import MAConfig

import json


class MetaArcade(gym.Env):

    def __init__(self, config=None, headless=False, episode_as_gif_path=None, game_ticks_per_step=2,
        continuous=False, **kwargs):

        if isinstance(config, MAConfig):
            pass
        else:
            config = MAConfig(config)

        self.config = config
        self.episode_as_gif_path = episode_as_gif_path

        self.headless = headless
        self.has_display = False
        
        self.continuous = continuous
        if not continuous:
            self.action_space = gym.spaces.Discrete(6)
        else:
            self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(3,))
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(84, 84, 3), dtype=np.uint8)

        self.cum_score = 0.0
        self.cum_steps = 0.0

        self.game_ticks_per_step = game_ticks_per_step

        self.block_pool = []
        for i in range(200):
            b = Block(100,100,0,0)
            self.block_pool.append(b)

        self.barrier_pool = []
        for i in range(50):
            w = Wall(100,100,0,0)
            self.barrier_pool.append(w)

        self.prng = random.Random()


    def build_display(self):
        if not self.has_display:
            self.has_display = True

            if self.headless:
                os.environ['SDL_VIDEODRIVER'] = 'dummy'

            from meta_arcade.GameDisplay import GameDisplay
            self.display = GameDisplay(headless=self.headless, episode_as_gif_path=self.episode_as_gif_path)


    @property
    def unwrapped(self):
        return self

    def seed(self, s):
        random.seed(s)
        np.random.seed(s)
        self.prng.seed(s)

    def reset(self):

        # only build display when we actually need it... this way we can pickle the
        # environment if we havent used it yet :)
        self.build_display()

        config = self.config

        self.game_elements = []
        self.exterior_walls = []

        pcfg = config["player_settings"]
        player = Player(pcfg["width"], pcfg["height"], pcfg["speed"], pcfg["color"], 
            config["actions"]["fire"], pcfg["steering"], prng=self.prng)

        wall_width = 0.03
        wclr = config["static_barrier_settings"]["color"]
        left_wall = Wall(0.0, 0.0, wall_width, 1.0, wclr)
        right_wall = Wall(1.0-wall_width, 0.0, wall_width, 1.0, wclr)
        self.exterior_walls += [left_wall, right_wall]

        if config["game_elements"]["top_wall"]:
            self.game_elements.append(Wall(0.0, 0.07, 1.0, wall_width, wclr))
            self.exterior_walls.append(self.game_elements[-1])

        if config["game_elements"]["bottom_wall"]:
            self.game_elements.append(Wall(0.0, 0.93-wall_width, 1.0, wall_width, wclr))
            self.exterior_walls.append(self.game_elements[-1])

        if config["game_elements"]["ball"]:
            cfg = config["ball_settings"]
            self.game_elements.append(Ball(cfg["size"], cfg["speed"], cfg["color"], cfg["harmful"], prng=self.prng))
            self.ball = self.game_elements[-1]
            if "num_balls" in cfg:
                ball = self.game_elements[-1]
                by = ball.y
                for i in range(cfg["num_balls"]-1):
                    by -= 0.15
                    b = Ball(cfg["size"], cfg["speed"], cfg["color"], cfg["harmful"], prng=self.prng)
                    b.oy = by
                    # b.vx = ball.vx
                    # b.vy = ball.vy
                    self.game_elements.append(b)

        if config["game_elements"]["opponent"]:
            cfg = config["opponent_settings"]
            for i in range(1):
                self.game_elements.append(Opponent(cfg["width"], cfg["height"], cfg["speed"], cfg["color"], 
                    cfg["skill_level"], cfg["tracks_ball"], cfg["can_shoot"], prng=self.prng))
            self.opponent = self.game_elements[-1]

        if config["actions"]["fire"]:
            bbullet = BlueBullet(config["player_settings"]["color"])
            self.game_elements.append(bbullet)
            self.bbullet = bbullet

        if config["game_elements"]["opponent"]:
            if config["opponent_settings"]["can_shoot"]:
                rbullet = RedBullet(config["opponent_settings"]["color"])
                self.game_elements.append(rbullet)
                self.rbullet = rbullet

        self.game_elements += [player, left_wall, right_wall]
        self.player = player

        self.cum_steps = 0.0
        self.cum_score = 0.0

        self.bgclr = self.config["display_settings"]["background_color"]
        self.uiclr1 = self.config["display_settings"]["ui_color"]
        self.uiclr2 = self.config["display_settings"]["indicator_color_1"]
        self.uiclr3 = self.config["display_settings"]["indicator_color_2"]

        for b in self.block_pool:
            b.reset()
        for w in self.barrier_pool:
            w.reset()
        for e in self.game_elements:
            e.reset()

        #synchronize multi-ball velocity
        if config["game_elements"]["ball"]:
            for e in self.game_elements:
                if isinstance(e, Ball):
                    e.vx, e.vy = self.ball.vx, self.ball.vy

        #pull in the blocks we need
        bcfg = self.config["blocks_settings"].sample_constant_values()
        if self.config["game_elements"]["blocks"]:
            x, y, w, h = bcfg["creation_area"]
            r, c = bcfg["rows"], bcfg["cols"]
            block_nom_width = w / c
            block_true_width = block_nom_width * (1.0 - bcfg["spacing"])
            paddx = (block_nom_width-block_true_width)*0.5
            block_nom_height = h / r
            block_true_height = block_nom_height * (1.0 - bcfg["spacing"])
            paddy = (block_nom_height-block_true_height)*0.5

            count = 0
            block_locations = []
            for j in range(r):

                if isinstance(bcfg["per_row"], str):
                    idxs = list(range(c))
                else:
                    idxs = self.prng.sample(list(range(c)), bcfg["per_row"])

                for i in range(c):
                    if i not in idxs:
                        continue

                    block_locations.append([i,j])

            clear_path = []
            if "clear_path" in bcfg:
                if bcfg["clear_path"]:
                    loc = [self.prng.choice(list(range(c))), r]
                    clear_path = [loc]
                    while loc[1]>0:
                        loc = loc[:] # copy
                        rand = self.prng.random()
                        if rand<0.33:
                            loc[0] -= 1
                        elif rand<0.67:
                            loc[0] += 1
                        else:
                            loc[1] -= 1

                        if loc[0]<0:
                            loc[0]=0
                        if loc[0]>=c:
                            loc[0]=c-1

                        clear_path.append(loc)

            for (i,j) in block_locations:
                if [i,j] in clear_path:
                    continue

                bx = x + block_nom_width*i + paddx
                by = y + block_nom_height*j + paddy

                bvx, bvy = 0.0, 0.0
                if bcfg["static_weave_fall"] == "weave":
                    bvx = bcfg["speed"] if j%2==0 else -bcfg["speed"]
                elif bcfg["static_weave_fall"] == "fall":
                    bvy = bcfg["speed"]

                block = self.block_pool[count]
                count += 1
                bad = bcfg["harmful"]
                fallpts = -100.0 if "fall_points" not in bcfg else bcfg["fall_points"]
                block.configure(bx, by, block_true_width, block_true_height, vx=bvx, vy=bvy, worth=bcfg["points"],
                    bad=bad, fall_points=fallpts, color=bcfg["color"])
                self.game_elements.insert(0, block)

            if bcfg["points"]=="divide":
                worth = (100.0 / float(count)) + 0.001
                for i in range(count):
                    self.game_elements[i].worth = worth


        #pull in the walls we need
        bcfg = self.config["static_barrier_settings"].sample_constant_values()
        if self.config["game_elements"]["static_barriers"]:
            x, y, w, h = bcfg["creation_area"]
            r, c = bcfg["rows"], bcfg["cols"]
            block_nom_width = w / c
            block_true_width = block_nom_width * (1.0 - bcfg["spacing"])
            paddx = (block_nom_width-block_true_width)*0.5
            block_nom_height = h / r
            block_true_height = block_nom_height * (1.0 - bcfg["spacing"])
            paddy = (block_nom_height-block_true_height)*0.5

            count = 0
            block_locations = []
            for j in range(r):

                if isinstance(bcfg["per_row"], str):
                    idxs = list(range(c))
                else:
                    idxs = self.prng.sample(list(range(c)), bcfg["per_row"])

                for i in range(c):
                    if i not in idxs:
                        continue

                    block_locations.append([i,j])

            clear_path = []
            if "clear_path" in bcfg:
                if bcfg["clear_path"]:
                    loc = [self.prng.choice(list(range(c))), r]
                    clear_path = [loc]
                    while loc[1]>0:
                        loc = loc[:] # copy
                        rand = self.prng.random()
                        if rand<0.33:
                            loc[0] -= 1
                        elif rand<0.67:
                            loc[0] += 1
                        else:
                            loc[1] -= 1

                        if loc[0]<0:
                            loc[0]=0
                        if loc[0]>=c:
                            loc[0]=c-1

                        clear_path.append(loc)

            for (i,j) in block_locations:
                if [i,j] in clear_path:
                    continue

                bx = x + block_nom_width*i + paddx
                by = y + block_nom_height*j + paddy

                barrier = self.barrier_pool[count]
                count += 1
                barrier.configure(bx, by, block_true_width, block_true_height, color=bcfg["color"])
                self.game_elements.append(barrier)


        # image settings
        self.img_invert = False
        self.img_rot = 0
        self.img_hue_shift = 0.0
        self.img_sat_shift = 0.0
        self.img_val_shift = 0.0
        if "image_settings" in self.config:
            icfg = self.config["image_settings"]
            if "color_inversion" in icfg:   self.img_invert = icfg["color_inversion"]
            if "rotation" in icfg:          self.img_rot = icfg["rotation"]
            if "hue_shift" in icfg:         self.img_hue_shift = icfg["hue_shift"]
            if "saturation_shift" in icfg:  self.img_sat_shift = icfg["saturation_shift"]
            if "value_shift" in icfg:       self.img_val_shift = icfg["value_shift"]

        self.display.compute_wall_mask(self.game_elements, self.bgclr)
        return self.draw()


    def step(self, action):

        # apply actions to the paddle (the only thing we can control)
        if not self.continuous:
            if action==1 and self.config["actions"]["up"]:
                self.player.vy = -self.player.speed
            elif action==2 and self.config["actions"]["down"]:
                self.player.vy = self.player.speed
            elif action==3 and self.config["actions"]["left"]:
                self.player.vx = -self.player.speed
            elif action==4 and self.config["actions"]["right"]:
                self.player.vx = self.player.speed
            elif action==5 and self.config["actions"]["fire"]:
                if not self.bbullet.active:
                    self.bbullet.activate(self.player.x+(self.player.w*0.5), self.player.y)
        else:
            if action[2] <= 0.0:
                if self.config["actions"]["up"] or self.config["actions"]["down"]:
                    self.player.vy = self.player.speed*action[0]

                if self.config["actions"]["left"] or self.config["actions"]["right"]:
                    self.player.vx = self.player.speed*action[1]
            else:
                self.player.vx = 0.0
                self.player.vy = 0.0

            if self.config["actions"]["fire"]:
                if not self.bbullet.active and action[2]>0.0:
                    self.bbullet.activate(self.player.x+(self.player.w*0.5), self.player.y)

        # step forward calculation
        dscore = 0.0
        game_over = False
        for rep in range(self.game_ticks_per_step):
            if game_over:continue

            #compute velocities and rewards from interactions
            for i in range(1):
                if game_over: continue
                for e in self.game_elements:
                    if game_over: continue
                    edscore = e.subtick(self.game_elements)
                    if edscore >= 100.0:
                        dscore = 100.0
                        game_over = True
                    elif edscore <= -100.0:
                        dscore = -100.0
                        game_over = True
                    else:
                        dscore += edscore

            # execute the step forward
            for e in self.game_elements:
                e.tick()

        # zero out player velocity
        self.player.vx = 0.0
        self.player.vy = 0.0

        # check for end of game
        self.cum_score += dscore
        done = False
        self.cum_steps += 1

        timeout_steps = 5000.0
        if "max_episode_length" in self.config["meta"]:
            timeout_steps = self.config["meta"]["max_episode_length"]

        if self.cum_steps >= timeout_steps:
            done = True
        if abs(self.cum_score) >= 100.0:
            done = True
        if game_over:
            done = True

        # draw
        img = self.draw()

        # save a gif if desired
        if done:
            self.display.buffer_to_gif()

        return img, dscore, done, {}


    def draw(self):
        self.display.prepare_render(self.bgclr)
        for e in self.game_elements:
            e.render(self.display)
        self.display.complete_render(self.cum_score, self.config["actions"], self.uiclr1, self.uiclr2, self.uiclr3)
        return self.display.image_state(self.img_invert, self.img_rot, self.img_hue_shift, 
            self.img_sat_shift, self.img_val_shift)


    def render(self, mode):
        # the environment renders automatically if headless=False (default)
        pass





class MetaArcadeInterpolate(MetaArcade):

    def __init__(self, config1=None, config2=None, duration=1, episodic=False, headless=False):
        self.config1, self.config2 = config1, config2

        if not isinstance(config1, MAConfig):
            config1 = MAConfig(config1)

        if not isinstance(config2, MAConfig):
            config2 = MAConfig(config2)

        self.target_duration = float(duration)
        self.duration = 0.0
        self.episodic = episodic
        super().__init__(config1, headless)

    def reset(self):
        if self.episodic:
            self.duration += 1.0

        progress = self.duration / self.target_duration
        if progress > 1.0:
            progress = 1.0

        self.config = self.config1.interpolate_towards(self.config2, progress)
        return super().reset()

    def step(self, a):
        if not self.episodic:
            self.duration += 1.0
        return super().step(a)

        






if __name__ == "__main__":

    import time

    # env = gym.make("MetaArcade-v0", config="./game_config.json")
    env = gym.make("MetaArcade-v0", config="sweeper")
    # env = gym.make("BreakoutNoFrameskip-v4")

    # play as a human
    from human_agent import human_agent
    human_agent(env)

    # #play with a random agent
    # from random_agent import random_agent
    # random_agent(env)


    # #play randomly and display state images
    # while True:
    #     env.reset()
    #     done = False
    #     while not done:
    #         a = env.action_space.sample()
    #         s, r, done, info = env.step(a)
    #         # print(np.mean(s[:,:,0]), np.mean(s[:,:,1]), np.mean(s[:,:,2]))

    #         #convert state to bgr for display
    #         s = s[:,:,[2,1,0]]

    #         cv2.namedWindow("state", cv2.WINDOW_NORMAL) 
    #         cv2.imshow("state", s)
    #         cv2.waitKey(1)

