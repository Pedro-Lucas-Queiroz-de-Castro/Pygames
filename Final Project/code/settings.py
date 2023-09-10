from support import *

# General
s = 0.8
WINDOW_WIDTH, WINDOW_HEIGHT = 1366*s,720*s

Z_AXIS = {
'tile': 0,
'player': 1,
'projectile': 2,
'item': 3,
'hand': 4}


# Player
s = 1
PLAYER_DEFAULT_SIZES = {'all': (32*s, 32*s)}
HAND_DEFAULT_SIZES = {'all': (8*s, 8*s)}

PLAYER_COLORS = ['#F11A7B', '#0B666A', '#4E4FEB', '#862B0D', '#1A5D1A', '#E7B10A', '#A4907C',
'#98EECC', '#A2FF86', '#FFD0D0', '#F86F03', '#F24C3D', '#FFE79B', '#B6EAFA', '#E86A33']

PLAYER_ANIMATIONS_SPEEDS = {'idle': 20, 'basic sword attack': 12, 'rising': 0,
'falling 0': 0, 'falling 1': 0, 'falling 2': 0, 'falling 3': 0, 'walk': 10}

PLAYER_FALLING_ANIMATION_CHANGE_SPEEDS = [75, 400, 700]

GET_DAMAGE_BLIKING_COLOR = 'red'

PLAYER_COOLDOWNS_MILLISECONDS = {'switch': 300, 'invulnerability': 500}
PLAYER_START_HEALTH = 300

# Hand
LEFT_HAND_ANCHOR_OFFSET = (3,4)
RIGHT_HAND_ANCHOR_OFFSET = (-3,4)

HAND_ANIMATIONS_SPEEDS = {'idle': 0, 'punch': 0, 'pick': 0}


# Level
BG_COLOR = '#181425'

DEFAULT_DROPABLE_ITEM_SET = ['flamethrower', 'machinegun', 'pistol', 'bazuca']
ITEM_DROP_SECONDS_COOLDOWN = [5, 10, 20, 30]

DEFAULT_SPEED_FORCES = {
'gravity': 1800,
'wind_direction': "vector(0,0)",
'input_acceleration_speed_on_floor': 500,
'input_deacceleration_speed_on_floor': 1000,
'input_acceleration_speed_in_air': 360,
'input_deacceleration_speed_in_air': 750}

FORCES_TO_CONVERT = {'wind_direction': convert_str_tuple_to_vector}


# Controls
CONFIG_FOLDER_PATH = '../config'
CONFIG_FILENAMES = {'player controls': 'playercontrols.json'}

DEFAULT_CONTROL_CONFIG = {
'move': 'hlaxis+lhat',
'jump': 'cross',
'left action': 'L1',
'right action': 'R1',
'left pick': 'L1&triangle',
'right pick': 'R1&triangle',
'switch': 'L2',
'pull/push': 'circle'}

DEADZONE = 0.2
