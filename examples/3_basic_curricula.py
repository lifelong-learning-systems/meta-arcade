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


# =======================================================
# Episode-based curriculum
# Create a curriculum to play pong for 10 episodes and then breakout for 10 episodes

# create schedule
schedule = [
	["pong", 10],
	["breakout", 10]
]

# get schedule wrapped up in a single gym environment, and the curriculum duration
env, total_duration = meta_arcade.make_curriculum(schedule, episodic=True, headless=False)

# run the curriculum
meta_arcade.random_agent(env, episodes=total_duration)




# =======================================================
# Step-based curriculum
# Do the same thing, but run each env for 2500 steps

# create schedule
schedule = [
	["pong", 2500],
	["breakout", 2500]
]

env, total_duration = meta_arcade.make_curriculum(schedule, episodic=False, headless=False)
meta_arcade.random_agent(env, steps=total_duration)




# =======================================================
# Config objects
# You can also pass config objects to have control over parameters
# or even a path to a custom game file (not demonstrated)

from meta_arcade import make_config

my_config_pink = make_config("pong")
my_config_pink["ball_settings"]["color"] = [0,0,0]
my_config_pink["display_settings"]["background_color"] = [255,160,160]

my_config_green = my_config_pink.copy()
my_config_green["display_settings"]["background_color"] = [160,255,160]

# create schedule
schedule = [
	[my_config_pink, 2500],
	[my_config_green, 2500]
]

env, total_duration = meta_arcade.make_curriculum(schedule, episodic=False, headless=False)
meta_arcade.random_agent(env, steps=total_duration)
