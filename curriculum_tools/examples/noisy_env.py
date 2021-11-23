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

class NoisyEnv(gym.Env):

	def __init__(self, env, noise=0.1):
		self.env = env
		self.noise = noise

	@property
	def observation_space(self):
		return self.env.observation_space

	@property
	def action_space(self):
		return self.env.action_space

	def add_noise(self, state):
		state = np.asarray(state, dtype=np.float32)
		state = state + np.random.uniform(
			low=-128.0*self.noise,
			high=128.0*self.noise, 
			size=state.shape)

		state = np.clip(state, 0.0, 255.0)
		state = state.astype(np.uint8)

		return state

	def reset(self):
		return self.add_noise(self.env.reset())

	def step(self, action):
		state, r, d, info = self.env.step(action)
		return self.add_noise(state), r, d, info

	def render(self, mode=None):
		self.env.render(mode)
