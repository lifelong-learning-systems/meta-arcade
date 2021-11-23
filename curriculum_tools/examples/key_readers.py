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
from noisy_env import NoisyEnv

# Users may also want to create custom curriculum commands as well
# in this example, we will create a custom curriculum command called "noise"
# this will wrap a given environment in an image noise wrapper (noisy_env.py)

# this functionality can be useful for adding types of curriculum blocks, such as
# interpolation between environments

def primary_interpreter(env_name, **kwargs):
	return gym.make(env_name)

# the key reader takes data and a duration, as well as other curriculum kwargs
# it returns a block of one or more environments to be added to the curriculum
def noisy_key_reader(data, duration, **kwargs):
	env, noise = data
	env_object = primary_interpreter(env)
	env_object = NoisyEnv(env_object, noise)

	block = [
		[env_object, duration]
	]

	return block



# now we can build our schedule using the special key "noise"
# the format is [ {key:data}, duration ]

schedule = [

	["BreakoutNoFrameskip-v4", 3],

	[{"noise":["PongNoFrameskip-v4", 0.2]}, 1],
	[{"noise":["PongNoFrameskip-v4", 0.4]}, 1],
	[{"noise":["PongNoFrameskip-v4", 0.6]}, 1]
]

# wrap this schedule into a single environment
# we pass in the key reader under 'key_readers'
env, total_episodes = curriculum_tools.make_curriculum(
		schedule=schedule,
		primary_interpreter = primary_interpreter, ### tell curriculum_tools how to process names
		key_readers = {"noise":noisy_key_reader}, ### tell curriculum_tools how to process special keys
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
