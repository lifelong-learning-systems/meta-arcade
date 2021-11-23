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

# in this example we show how to replace explicit environment objects with configuration
# information. In this case, the config info will be the name of the desired environment.
# we construct a custom interpreter to build environments

def primary_interpreter(env_name, **kwargs):
	return gym.make(env_name)


# now we can build our schedule using environment names instead of objects:
# play pong for 3 episodes, then breakout for 3
schedule = [
	["PongNoFrameskip-v4", 3],
	["BreakoutNoFrameskip-v4", 3]
]

# wrap this schedule into a single environment
# we pass in the interpreter with turns environment names in environment objects
env, total_episodes = curriculum_tools.make_curriculum(
		schedule=schedule,
		primary_interpreter = primary_interpreter, ### tell curriculum_tools how to process names
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
