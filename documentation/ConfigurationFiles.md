### Documentation Pages:

1. [Game Mechanics](./GameMechanics.md)

2. [Configuration Files](./ConfigurationFiles.md)

3. [Parameter Distributions](./ParameterDistributions.md)

4. [Building Curricula](./BuildingCurricula.md)

5. [Additional Tools](./AdditionalTools.md)

6. [Meta Arcade Inner Workings](./InnerWorkings.md)




Configuration Files
===

Unlike many other gym environments, Meta Arcade only defines a single gym environment (MetaArcade-v0) which is configured by a set of parameters. All Meta Arcade games are defined by these configuration parameters, including the predefined games. You can create new games by simply creating a new configuration file.

The configuration parameters for a given game are defined a single JSON file, and are read in as MAConfig instances. From there, they can be manipulated within python. This document describes the basic names and values contained in a JSON config file. Defining distributions instead of constants is described in [Parameter Distributions](./documentation/ParameterDistributions.md), which provides examples in JSON and python. A more extensive explanation of manipulating configs from within python is described in [Building Curricula](./documentation/BuildingCurricula.md).

The parameters of a game are split into several categories which are distinct named entries in the JSON file. These are described in the sections below. See the bottom of this document for a complete example, or look at the config files in [meta_arcade/predefined_games](./meta_arcade/predefined_games/)


## Config File Overview

A JSON configuration file for Meta Arcade is split into several names, each of which has a corresponding value that is a dictionary of further parameters. The first four named objects are:

- meta
  - Provides a description of the game and game duration information
- actions
  - Describes which actions are available to the player in this game
- game_elements
  - Describes which game elements will be present in this game
- display_settings
  - Describes basic colors of the game interface



The next five named objects describe details about individual game elements, some of which may be enabled or disabled within the "game_elements" section above:

- player_settings
- opponent_settings
- ball_settings
- block_settings
- static_barrier_settings


Finally, an optional object at the end describes any alterations to the image state space, such as color shifting or rotations:

- image_settings



The parameters that may exist in each section and acceptable values are described below.



## Meta

**Example JSON:**

```json
"meta":{
		"description":"Make it to the top of the screen to win.",
		"max_episode_length":2000
	}
```



**Fields:**

| Parameter            | Acceptable Values | Description                                                  |
| -------------------- | ----------------- | ------------------------------------------------------------ |
| "description"        | string            | Description of the game.                                     |
| "max_episode_length" | integer           | Optional. Number of steps after which to terminate the game. Default value is 5000. |



## Actions

**Example JSON:**

```json
"actions":{
		"up":true,
		"down":true,
		"left":true,
		"right":true,
		"fire":false
	}
```



**Fields:**

| Parameter | Acceptable Values | Description                                                  |
| --------- | ----------------- | ------------------------------------------------------------ |
| "up"      | true or false     | Whether or not the player can move upwards in this game (action id 1). |
| "down"    | true or false     | Whether or not the player can move downwards in this game (action id 2). |
| "left"    | true or false     | Whether or not the player can move left in this game (action id 3). |
| "right"   | true or false     | Whether or not the player can move right in this game (action id 4). |
| "fire"    | true or false     | Whether or not the player will be able to shoot in this game (action id 5). |



## Game Elements

**Example JSON:**

```json
"game_elements":{
		"top_wall":true,
		"bottom_wall":true,
		"ball":true,
		"opponent":false,
		"blocks":false,
		"static_barriers":false
	}
```



**Fields:**

| Parameter         | Acceptable Values | Description                                                  |
| ----------------- | ----------------- | ------------------------------------------------------------ |
| "top_wall"        | true or false     | Should a wall block the top of the screen? This will prevent the player and a ball from leaving the top of the screen. Left and right walls are always present. |
| "bottom_wall"     | true or false     | Should a wall block the bottom of the screen? This will prevent the player and a ball from leaving the bottom of the screen. Left and right walls are always present. |
| "ball"            | true or false     | Whether or not a ball will be used in this game. If so, it will start in the middle of the screen, and defined by parameters in the "ball_settings" section. |
| "opponent"        | true or false     | Whether or not an opponent paddle will exist in the game. The opponent parameters are defined in the "opponent_settings" section. |
| "blocks"          | true or false     | Whether or not blocks will exist in the game, either as hazards or as things to collect (by the player directly or with the ball).  The specifics of how the blocks are used is defined in the "blocks_settings" section. |
| "static_barriers" | true or false     | Whether or not additional barriers (besides walls) will be used in the game. These are further described in the "static_barrier_settings" section. |



## Display Settings

**Example JSON:**

```json
"display_settings":{
		"background_color":[0,0,0],
		"ui_color":[80,80,80],
		"indicator_color_1":[200,200,160],
		"indicator_color_2":[0,0,0]
	}
```



**Fields:**

| Parameter           | Acceptable Values | Description                                                  |
| ------------------- | ----------------- | ------------------------------------------------------------ |
| "background_color"  | rgb color [0-255] | The background color of the gameplay area.                   |
| "ui_color"          | rgb color [0-255] | The color of the top and bottom game border, which contains indicators about score and available actions. |
| "indicator_color_1" | rgb color [0-255] | The primary indicator color (score meter progress and valid actions) |
| "indicator_color_2" | rgb color [0-255] | The secondary indicator color (score meter background and border around action indicators) |



## Player Settings

**Example JSON:**

```json
"player_settings":{
		"width":0.2,
		"height":0.03,
		"speed":0.01,
		"color":[255,255,255],
		"steering":0.5
	}
```



**Fields:**

| Parameter  | Acceptable Values | Description                                                  |
| ---------- | ----------------- | ------------------------------------------------------------ |
| "width"    | 0.01 to 0.3       | The width of the player, as a fraction of the display width. |
| "height"   | 0.01 to 0.3       | The height of the player, as a fraction of the display height. |
| "speed"    | 0.001 to 0.1      | How far the player moves when taking an action as a fraction of the display side length. Will require some tuning for your game. Values around 0.01 seem reasonable. |
| "color"    | rgb color [0-255] | The display color of the player. This also is used as the color for any bullets shot by the player. |
| "steering" | 0.0 to 1.0        | The ability of the player to control the bounce direction of the ball. 0.0 indicates no ability; the ball bounces based only on its own direction. 1.0 indicates perfect ability; the ball bounces only based on the location that it hits the player.  In-between values average these effects. |



## Opponent Settings

**Example JSON:**

```json
"opponent_settings":{
		"width":0.2,
		"height":0.03,
		"speed":0.01,
		"color":[255,0,100],
		"skill_level":0.5,
		"can_shoot":true,
		"tracks_ball":false
	}
```



**Fields:**

| Parameter     | Acceptable Values | Description                                                  |
| ------------- | ----------------- | ------------------------------------------------------------ |
| "width"       | 0.01 to 0.3       | The width of the opponent, as a fraction of the display width. |
| "height"      | 0.01 to 0.3       | The height of the opponent, as a fraction of the display height. |
| "speed"       | 0.001 to 0.1      | How far the player opponent moves when trying to stay behind the ball or avoid bullets. Will require some tuning for your game. Values around 0.01 seem reasonable.  Opponent actions are noisy as described by "skill_level" below. |
| "color"       | rgb color [0-255] | The display color of the opponent. This is also used as the color of enemy bullets, if "can_shoot" below is set to true. |
| "skill_level" | 0.0 to 1.0        | A modifier on the opponent's ability to move purposefully, either toward the ball, away from bullets, or randomly if neither applies. This describes the fraction of movements that are purposeful. 0.0 indicates all movements are random, and 1.0 indicates all movements are perfect. Note that because the opponent has some width, it may track a ball perfectly even when this value is less than 1.0.  **A value around 0.4 to 0.6 is probably best** for a competent but defeatable opponent. |
| "can_shoot"   | true or false     | Whether or not the opponent will shoot bullets. If so, the opponent will fire randomly. |
| "tracks_ball" | true or false     | Whether or not the opponent will try to track the ball. The opponent also tries to avoid bullets if the player can shoot, with preference towards avoiding bullets. |



## Ball Settings

**Example JSON:**

```json
"ball_settings":{
		"size":0.08,
		"speed":0.011,
		"color":[255,180,0],
		"harmful":true,
		"num_balls":1
	}
```



**Fields:**

| Parameter   | Acceptable Values | Description                                                  |
| ----------- | ----------------- | ------------------------------------------------------------ |
| "size"      | 0.01 to 0.3       | The diameter of the ball as a fraction of the display side length. This also defines a square bounding box around the ball used for collision detection. |
| "speed"     | 0.001 to 0.2      | How far the ball moves each each environment step, as a fraction of display side length. A value of about 0.1 is reasonable. |
| "color"     | rgb color [0-255] | The display color of the ball. This will be a filled circle if not harmful, otherwise a circular outline. |
| "harmful"   | true or false     | Whether or not contacting the ball is a lose condition. If this is true, the ball no longer functions as a way to collect points, either by leaving the screen or hitting blocks. |
| "num_balls" | 1, 2, or 3        | Optional. Default is 1. Can be used to specify additional game balls. Extra balls are initialized above the normal ball and will match the initial speed and direction of the first ball. |



## Blocks Settings

Blocks are created in a (possibly sparse) grid over some rectangle in the playing area.  Only one grid of blocks can be defined.

**Example JSON:**

```json
"blocks_settings":{
		"creation_area":[0.05,0.15,0.9,0.2],
		"rows":4,
		"cols":5,
		"per_row":"full",
		"spacing":0.15,
		"color":[200,50,50],
		"static_weave_fall":"static",
		"speed":0.0,
		"harmful":false,
		"points":"divide",
		"clear_path":false
	}
```



**Fields:**

| Parameter           | Acceptable Values                                          | Description                                                  |
| ------------------- | ---------------------------------------------------------- | ------------------------------------------------------------ |
| "creation_area"     | List of 4 values each -1.0 to 1.0                          | Describes a rectangle (x,y,w,h) in the game display area where the blocks are initialized. Values are normalized to the side length of the display. Negative values are possible, i.e. to define blocks that start above the game area and fall vertically, the creation area could be [0,-1,1,1] with "static_weave_fall" set to "fall". |
| "rows"              | 1 or more                                                  | How many rows to break the grid into. The height of each block is computed from this value. |
| "cols"              | 1 or more                                                  | How many columns to break the grid into. The width of each block is computed from this value. |
| "per_row"           | Either "full" or some integer less than or equal to "cols" | The sparsity of the grid defined as the number of blocks to randomly place in each row. The key "full" can be used to additionally indicate no sparsity. This is equivalent to setting a value equal to "cols". |
| "spacing"           | -0.1 to 0.9                                                | Reduction on block size such that there are gaps between them when initialized. 0.0 indicates blocks are flush with each other with no visual edges. Sometimes a small negative value is needed to force this effect. 1.0 would correspond to margins that completely erase the blocks. |
| "color"             | rgb color [0-255]                                          | The color of the blocks. Currently they are all rendered with identical coloring. |
| "static_weave_fall" | One of "static", "weave", or "fall"                        | Behavior of the blocks during game play. See the description beneath this table. |
| "speed"             | 0.001 to 0.2                                               | If the blocks move, how fast the blocks move per frame, as a fraction of game display side length. |
| "harmful"           | true or false                                              | Whether or not the blocks harm the player (true), or act as collectable items either via the player directly or the ball (false). If false and blocks are falling, blocks need to be collected before leaving the bottom of the screen or the game will be lost. |
| "points"            | float value or "divide"                                    | If they are not harmful, the worth of collecting a block.  Any game is considered won when total points accumulate to 100, there a key of "divide" may be used to divide 100 points evenly among all collectible blocks. This can optionally be -100.0 to create a harmful block without changing the block visuals. |
| "fall_points"       | float value                                                | The value associated with the block leaving the bottom of the screen. By default this is -100.0, but a positive value could be used if, i.e., the objective is to avoid the blocks and let them fall. |
| "clear_path"        | true or false                                              | If true, forces a random path to be cleared from the bottom of the block grid to the top.  Useful to ensure that hazardous blocks or static walls are always navigable. |



**Specifics of Block Movement Types:**

| Parameter String Value | Behavior                                                     |
| ---------------------- | ------------------------------------------------------------ |
| "static"               | The blocks do not move. Once collected or destroyed, they do not respawn. |
| "weave"                | The blocks move horizontally, with each row alternating in direction.  Blocks move until they leave the screen on either the left or right side, at which point they wrap around to the other side and enter from there.  If collected or destroyed, the block will respawn off-screen and then move on-screen, as though it had continued moving and wrapped around normally. |
| "fall"                 | The blocks move vertically downwards.  Blocks move until they leave the screen on the bottom (game loss) or are collected/destroyed.  If collected or destroyed, the block will respawn off-screen and then move on-screen, as though it had continued moving and wrapped around normally. |



## Static Barrier Settings

**Example JSON:**

```json
"static_barrier_settings":{
		"creation_area":[0.2,0.4,0.6,0.2],
		"rows":2,
		"cols":6,
		"per_row":2,
		"spacing":0.0,
		"color":[150,100,200],
		"clear_path":false
	}
```



**Fields:**

Identical to block settings in the above section.

Note that "color" also sets the wall colors, so this parameter can be used by itself to define the color of any walls in the game.



## Image Distortion Settings

**Example JSON:**

```json
"image_settings":{
		"color_inversion":false,
		"rotation":0,
		"hue_shift":0.0,
		"saturation_shift":0.0,
		"value_shift":0.0
	}
```



**Fields:**

| Parameter          | Acceptable Values | Description                                                  |
| ------------------ | ----------------- | ------------------------------------------------------------ |
| "color_inversion"  | true or false     | Whether or not to invert colors of the image (applied after shifts) |
| "rotation"         | 0,1,2, or 3       | Number of 90 degree rotations to apply to the image (counter-clockwise). |
| "hue_shift"        | -1.0 to 1.0       | Amount to shift the image hue in HSV space, where the spectrum of hues spans 0.0 to 1.0.  Hue values wrap around such that a shift of -a corresponds to (1-a).  i.e. a shift of -0.7 is the same as +0.3. |
| "saturation_shift" | -1.0 to 1.0       | Amount to shift the image saturation in HSV space, where saturation occupies 0.0 to 1.0. This shift is applied uniformly to all pixels and then the saturation of all pixels is clipped to [0.0, 1.0]. |
| "value_shift"      | -1.0 to 1.0       | Amount to shift the image value in HSV space, where value occupies 0.0 to 1.0. This shift is applied uniformly to all pixels and then the value of all pixels is clipped to [0.0, 1.0]. |


## Full JSON Example
The above fields are combined into a single config file that defines a game. A full example is given below for Breakout:

```json
{

	"meta":{
		"description":"Break as many blocks as you can by bouncing the ball off the paddle."
	},

	"actions":{
		"up":false,
		"down":false,
		"left":true,
		"right":true,
		"fire":false
	},

	"game_elements":{
		"top_wall":true,
		"bottom_wall":false,
		"ball":true,
		"opponent":false,
		"blocks":true,
		"static_barriers":false
	},

	"display_settings":{
		"background_color":[0,0,0],
		"ui_color":[80,80,80],
		"indicator_color_1":[200,200,160],
		"indicator_color_2":[0,0,0]
	},

	"player_settings":{
		"width":0.2,
		"height":0.03,
		"speed":0.01,
		"color":[255,255,255],
		"steering":0.5
	},

	"opponent_settings":{},

	"ball_settings":{
		"size":0.05,
		"speed":0.011,
		"color":[255,180,0],
		"harmful":false
	},

	"blocks_settings":{
		"creation_area":[0.05,0.15,0.9,0.2],
		"rows":4,
		"cols":5,
		"per_row":"full",
		"spacing":0.15,
		"color":[200,50,50],
		"static_weave_fall":"static",
		"speed":0.0,
		"harmful":false,
		"points":"divide"
	},

	"static_barrier_settings":{
		"color":[150,100,200]
	},


	"image_settings":{
		"color_inversion":false,
		"rotation":0,
		"hue_shift":0.0,
		"saturation_shift":0.0,
		"value_shift":0.0
	}

}
```
