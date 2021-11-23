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


import curriculum_tools

def default_env_interpreter(env):
	return env

# returns an environment which runs through a preset curriculum

# schedule: a list of (env, duration) or (config, duration) with a provided interpreter

# episodic (default False) whether the durations are episodic or stepwise

# across_workers (default 1) divide durations across this many workers

def make_curriculum(schedule, primary_interpreter=None, key_readers={},
	episodic=False, across_workers=1, **kwargs):

	primary_interpreter = default_env_interpreter if primary_interpreter is None else primary_interpreter

	sch = []

	for entry in schedule:

		# special cases
		if isinstance(entry[0], dict):

			if "pool" in entry[0]:
				pool = entry[0]["pool"]
				envs = [primary_interpreter(env, **kwargs) for env in pool]
				env = curriculum_tools.MultiEnv(envs)
				dur = entry[1] // across_workers

				sch.append([env, dur])

			elif "repeat" in entry[0]:
				sub_sch = entry[0]["repeat"]

				times = entry[1]
				for t in range(times):
					env, dur = make_curriculum(sub_sch, primary_interpreter, key_readers,
						episodic, across_workers, **kwargs)
					sch.append([env, dur])

			else:
				key = list(entry[0].keys())[0] # get only key
				if key not in key_readers:
					raise ValueError(str(key)+" is not a supported scheduling key, add support with a custom interpreter.")

				else:
					interpreter = key_readers[key]
					contents = entry[0][key]
					duration = entry[1]
					sch += interpreter(contents, duration, episodic=episodic, across_workers=across_workers, **kwargs)

		#standard: [env, duration] or [config, duration]
		else:
			env, dur = entry
			dur = dur // across_workers
			env = primary_interpreter(env, **kwargs)
			sch.append([env, dur])

	total_duration = sum([e[1] for e in sch])
	return curriculum_tools.ScheduleEnv(sch, by_episode=episodic), total_duration