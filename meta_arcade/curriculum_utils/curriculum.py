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
import curriculum_tools

# tells curriculum tools how to convert a config into an environment object
def primary_interpreter(cfg, **kwargs):
	if isinstance(cfg, gym.Env):
		return cfg
	return gym.make("MetaArcade-v0", config=cfg, **kwargs)

# support for special "interpolate" key
def interpolate_key_reader(data, duration, episodic=False, across_workers=1, **kwargs):
	cfg1, cfg2 = data
	duration = duration // across_workers
	
	env = gym.make("MetaArcadeInterpolate-v0", config1=cfg1, config2=cfg2, 
					duration=duration, episodic=episodic, **kwargs)

	block = [
		[env, duration]
	]

	return block



def make_curriculum(schedule, episodic=False, across_workers=1, **kwargs):

	return curriculum_tools.make_curriculum(
			schedule = schedule,
			primary_interpreter = primary_interpreter,
			key_readers = {"interpolate":interpolate_key_reader},
			episodic = episodic,
			across_workers = across_workers,
			**kwargs
		)