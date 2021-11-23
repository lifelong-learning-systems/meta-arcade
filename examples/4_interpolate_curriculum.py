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
# Config interpolation
# Create a curriculum to play pong (black background) -> pong (blue background)

# define pong
cfg_pong = make_config("pong")

# pong with blue background
cfg_pong_blue = cfg_pong.copy()
cfg_pong_blue["display_settings"]["background_color"] = [100,100,255]


# create schedule
# interpolate between configs by listing two configs instead of one
schedule = [

	# initial cfg for 5 episodes
	[cfg_pong, 5], 				  

	# interpolate for 10 episodes
	[{"interpolate":[cfg_pong, cfg_pong_blue]}, 10],	

	 # final cfg for 5 episodes
	[cfg_pong_blue, 5]			   
]

# get schedule wrapped up in a single gym environment, 
# and the total curriculum duration
env, total_duration = meta_arcade.make_curriculum(schedule, episodic=True, headless=False)

# run the curriculum, slowed down so we can actually see the changes
meta_arcade.random_agent(env, episodes=total_duration, delay=0.005)


