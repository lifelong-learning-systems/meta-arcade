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

from multiprocessing import Process

# =======================================================
# Distributed curriculum
# Create a curriculum to play pong for 10000 steps, across 4 workers
# This is just a convenience function to manage worker-level durations for you.
# i.e. when creating the curriculum, specify "across_workers=4" to divide durations by 4

def run_env(workers):

    # define pong
    cfg_pong = make_config("pong")

    # create schedule irrespective of number of workers
    schedule = [
        [cfg_pong, 10000]
    ]

    # get schedule wrapped up in a single gym environment, 
    # and the total curriculum duration for this worker
    env, worker_duration = meta_arcade.make_curriculum(
    	schedule, 
        episodic=False, 
        across_workers=workers, # set workers here
        headless=False)

    # run the curriculum
    meta_arcade.random_agent(env, steps=worker_duration)



workers = 4

procs = []
for i in range(workers):
    p = Process(target=run_env, args=(workers,))
    p.start()
    procs.append(p)

for p in procs:
    p.join()