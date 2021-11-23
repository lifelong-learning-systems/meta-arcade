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


# =======================================================
# Domain randomization on breakout

# define game
cfg = make_config("breakout")

# direct reference to parameter dictionary (as opposed to MAConfig object)
pdict = cfg.parameter_dictionary()

# every color (length 3 list) will be fully random
for category in pdict:

	subdict = pdict[category]

	if len(subdict) == 0:
		continue

	for k in subdict:
		# color
		if isinstance(subdict[k], list) and len(subdict[k])==3:
			cfg[category][k] = {"distribution":"color"}


# explicity set some other parameters
cfg["blocks_settings"]["rows"] = {"distribution":"uniform", "low":2, "high":7}
cfg["blocks_settings"]["cols"] = {"distribution":"uniform", "low":3, "high":8}

cfg["player_settings"]["width"] = {"distribution":"uniform", "low":0.1, "high":0.3}
cfg["player_settings"]["height"] = {"distribution":"uniform", "low":0.02, "high":0.05}

cfg["ball_settings"]["size"] = {"distribution":"uniform", "low":0.02, "high":0.08}
cfg["ball_settings"]["speed"] = {"distribution":"uniform", "low":0.008, "high":0.015}

# run the game, slowed down so we can actually see the changes
env = gym.make("MetaArcade-v0", config=cfg)
meta_arcade.random_agent(env, episodes=100, delay=0.01)


