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
# Play pong, then (pong & breakout & duel randomly interwoven)

cfg_pong = make_config("pong")
cfg_breakout = make_config("breakout")
cfg_duel = make_config("duel")

# create schedule]
schedule = [
	[cfg_pong, 5000],
	[{"pool":[cfg_pong, cfg_breakout, cfg_duel]}, 5000] # games will be played for 5000 steps collectively
]

env, total_duration = meta_arcade.make_curriculum(schedule, episodic=False, headless=False)
meta_arcade.random_agent(env, steps=total_duration)

