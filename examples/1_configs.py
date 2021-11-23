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
import meta_arcade
import meta_arcade.random_agent
from meta_arcade import make_config
import time

# ================================================
# Basic examples: change config by writing to it as a dictionary

#create an environment config for breakout
cfg = make_config("breakout")
env = gym.make("MetaArcade-v0", config=cfg)
meta_arcade.random_agent(env, episodes=10)

#change the background color to blue
cfg["display_settings"]["background_color"] = [0,0,255]
meta_arcade.random_agent(env, episodes=10)

#change block color to a normal distribution around yellow
cfg["blocks_settings"]["color"] = {"distribution":"normal", "mean":[255,255,0], "std":[30,30,30]}
meta_arcade.random_agent(env, episodes=10)



# ==================================================
# Maintaining several environments

# to maintain the original config, just copy it with copy() before changing it
cfg2 = cfg.copy()
cfg2["display_settings"]["background_color"] = [50,0,0]

# make a separate environment with this config
env_2 = gym.make("MetaArcade-v0", config=cfg2)
meta_arcade.random_agent(env_2, episodes=10)

# the original env is preserved
meta_arcade.random_agent(env, episodes=10)


