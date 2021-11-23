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
import curriculum_tools
import cv2
import numpy as np

pong = gym.make("PongNoFrameskip-v4")
breakout = gym.make("BreakoutNoFrameskip-v4")

# play pong and breakout sampled randomly for 10 episodes
schedule = [
	[{"pool":[pong, breakout]}, 10]
]

# wrap this schedule into a single environment
env, total_episodes = curriculum_tools.make_curriculum(
		schedule=schedule,
		episodic=True
	)



# play this out with a random agent
for ep in range(total_episodes):
	env.reset()
	done = False
	while not done:
		a = env.action_space.sample()
		state, reward, done, info = env.step(a)

		#render the state
		state = np.asarray(state)[:,:,::-1] #bgr -> rgb
		cv2.namedWindow('state', cv2.WINDOW_NORMAL)
		cv2.imshow('state', state)
		cv2.waitKey(1)
