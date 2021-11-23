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

import numpy as np
import json
import os
import copy
import colorsys
import random

# class that behaves as a dict,
# but intercepts read calls so that distributions can be sampled

#convenience method
def make_config(cfg):
    return MAConfig(cfg)

class MAConfig:

    def __init__(self, config):

        # if config is string, load json into dict
        # otherwise it should be a dictionary
        if isinstance(config, str):

            # does config end in ".json"?
            if len(config)<5 or config[-5:] != ".json":
                config = config + ".json"

            # explicit path
            if "/" in config or "\\" in config:
                with open(config) as f:
                    config = json.load(f)
            
            # predefined game file in this package
            else:
                file_path = os.path.dirname(os.path.abspath(__file__))
                with open(file_path+"/predefined_games/"+config) as f:
                    config = json.load(f)

            self.original_dict = config

        elif isinstance(config, dict):
            self.original_dict = config

        else:
            raise ValueError("config accepts game name, json file path, or dictionary.")


    def parameter_dictionary(self):
        return self.original_dict

    # override bracket access operator: object[key]
    def __getitem__(self, key):
        value = self.original_dict[key]
        if isinstance(value, dict):

            if "distribution" in value:

                if value["distribution"]=="gaussian" or value["distribution"]=="normal":
                    mean = value["mean"]
                    std = value["std"]
                    return self.sample_normal(mean, std)
                elif value["distribution"]=="uniform":
                    low = value["low"]
                    high = value["high"]
                    return self.sample_uniform(low, high)
                elif value["distribution"]=="color":
                    #add defaults
                    if "hrange" not in value: value["hrange"]=[0.0, 1.0]
                    if "lrange" not in value: value["lrange"]=[0.0, 1.0]
                    if "srange" not in value: value["srange"]=[0.0, 1.0]

                    #sample
                    h = random.uniform(value["hrange"][0], value["hrange"][1])
                    if h<0.0:
                        h += 1.0
                    if h>1.0:
                        h -= 1.0

                    l = random.uniform(value["lrange"][0], value["lrange"][1])
                    s = random.uniform(value["srange"][0], value["srange"][1])
                    rgb = list(colorsys.hls_to_rgb(h, l, s))

                    for i in range(3):
                        rgb[i] = int(rgb[i]*255.0)

                    return rgb

                else:
                    raise ValueError("'distribution' must have type 'normal', 'uniform', or 'color'")
            else:
                value = MAConfig(value)

        return value

    # bracket assignment operator (config is read only)
    def __setitem__(self, key, value):
        self.original_dict[key] = value

    # in operator
    def __contains__(self, key):
        return key in self.original_dict


    def sample_constant_values(self):
        values = {}
        for k in self.original_dict:
            value = self.original_dict[k]
            if isinstance(value, dict):
                if "distribution" in value:
                    values[k] = self[k]
                else:
                    values[k] = self[k].sample_constant_values()
            else:
                values[k] = self[k]
        return values

    def copy(self):
        d = copy.deepcopy(self.original_dict)
        return MAConfig(d)

    # ======================================================================
    # Sampling and Interpolation ===========================================


    def sample_normal(self, mean, std):
        if isinstance(mean, list):
            values = []
            for i in range(len(mean)):
                values.append(self.sample_normal(mean[i], std[i]))

            #special case: colors
            if isinstance(mean[0], int) and len(mean)==3:
                values = [np.clip(v, 0, 255) for v in values]

            return values

        else:
            value = np.random.normal(mean, std)
            if isinstance(mean, int):
                value = int(value)
            return value


    def sample_uniform(self, low, high):
        interp = np.random.uniform(0.0, 1.0)
        return self.interpolate(low, high, interp)


    def interpolate(self, v1, v2, amt):
        if isinstance(v1, list):
            values = []
            for i in range(len(v1)):
                values.append(self.interpolate(v1[i], v2[i], amt))
            return values
        elif isinstance(v1, bool) or isinstance(v1, str):
            return v1
        elif isinstance(v1, float):
            return (v2 - v1)*amt + v1
        elif isinstance(v1, int):
            return int( round( (float(v2) - float(v1))*amt + v1 ) )


    def interpolate_towards(self, other, amt):
        interp_config = {}
        for k in self.original_dict:
            value = self.original_dict[k]
            otherv = other.original_dict[k]

            if isinstance(value, dict):
                if "distribution" in value:
                    new_dist = {"distribution":value["distribution"]}
                    for key in ["low", "high", "mean", "std", "hrange", "lrange", "srange"]:
                        if key in value: 
                            new_dist[key] = self.interpolate(value[key], otherv[key], amt)
                    interp_config[k] = new_dist

                else:
                    interp_config[k] = self[k].interpolate_towards(other[k], amt)
            else:
                interp_config[k] = self.interpolate(value, otherv, amt)

        return MAConfig(interp_config)