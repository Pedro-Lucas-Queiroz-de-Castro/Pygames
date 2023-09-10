# general setup
TILE_SIZE = 64
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ANIMATION_SPEED = 8

# editor graphics 
EDITOR_DATA_SELECTABLES_START_INDEX = 2
EDITOR_DATA_SELECTABLES_END_INDEX = 18
EDITOR_DATA = {
	0: {'style': 'player', 'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': '../graphics/player/idle_right', 'animation speed': 8},
	1: {'style': 'sky',    'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': None, 'animation speed': None},
	
	2: {'style': 'terrain', 'type': 'tile', 'menu': 'terrain', 'menu_surf': '../graphics/menu/land.png',  'preview': '../graphics/preview/land.png',  'graphics': None, 'animation speed': None},
	3: {'style': 'water',   'type': 'tile', 'menu': 'terrain', 'menu_surf': '../graphics/menu/water.png', 'preview': '../graphics/preview/water.png', 'graphics': '../graphics/terrain/water/animation', 'animation speed': 8},
	
	4: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': '../graphics/menu/gold.png',    'preview': '../graphics/preview/gold.png',    'graphics': '../graphics/items/gold', 'animation speed': 8},
	5: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': '../graphics/menu/silver.png',  'preview': '../graphics/preview/silver.png',  'graphics': '../graphics/items/silver', 'animation speed': 8},
	6: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': '../graphics/menu/diamond.png', 'preview': '../graphics/preview/diamond.png', 'graphics': '../graphics/items/diamond', 'animation speed': 8},

	7:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/spikes.png',      'preview': '../graphics/preview/spikes.png',      'graphics': '../graphics/enemies/spikes', 'animation speed': 8},
	8:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/tooth.png',       'preview': '../graphics/preview/tooth.png',       'graphics': '../graphics/enemies/tooth/idle', 'animation speed': 8},
	9:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/shell_left.png',  'preview': '../graphics/preview/shell_left.png',  'graphics': '../graphics/enemies/shell_left/idle', 'animation speed': 8},
	10: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/shell_right.png', 'preview': '../graphics/preview/shell_right.png', 'graphics': '../graphics/enemies/shell_right/idle', 'animation speed': 8},
	
	11: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': '../graphics/menu/small_fg.png', 'preview': '../graphics/preview/small_fg.png', 'graphics': '../graphics/terrain/palm/small_fg', 'animation speed': 8},
	12: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': '../graphics/menu/large_fg.png', 'preview': '../graphics/preview/large_fg.png', 'graphics': '../graphics/terrain/palm/large_fg', 'animation speed': 8},
	13: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': '../graphics/menu/left_fg.png',  'preview': '../graphics/preview/left_fg.png',  'graphics': '../graphics/terrain/palm/left_fg', 'animation speed': 8},
	14: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': '../graphics/menu/right_fg.png', 'preview': '../graphics/preview/right_fg.png', 'graphics': '../graphics/terrain/palm/right_fg', 'animation speed': 8},

	15: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': '../graphics/menu/small_bg.png', 'preview': '../graphics/preview/small_bg.png', 'graphics': '../graphics/terrain/palm/small_bg', 'animation speed': 8},
	16: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': '../graphics/menu/large_bg.png', 'preview': '../graphics/preview/large_bg.png', 'graphics': '../graphics/terrain/palm/large_bg', 'animation speed': 8},
	17: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': '../graphics/menu/left_bg.png',  'preview': '../graphics/preview/left_bg.png',  'graphics': '../graphics/terrain/palm/left_bg', 'animation speed': 8},
	18: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': '../graphics/menu/right_bg.png', 'preview': '../graphics/preview/right_bg.png', 'graphics': '../graphics/terrain/palm/right_bg', 'animation speed': 8},
}

NEIGHBOR_DIRECTIONS = {
	'A': (0,-1),
	'B': (1,-1),
	'C': (1,0),
	'D': (1,1),
	'E': (0,1),
	'F': (-1,1),
	'G': (-1,0),
	'H': (-1,-1)
}

LEVEL_LAYERS = {
	'clouds': 1,
	'ocean': 2,
	'bg': 3,
	'water': 4,
	'main': 5
}

# colors 
SKY_COLOR = '#ddc6a1'
SEA_COLOR = '#92a9ce'
HORIZON_COLOR = '#f5f1de'
HORIZON_TOP_COLOR = '#d1aa9d'
LINE_COLOR = 'black'
BUTTON_BG_COLOR = '#33323d'
BUTTON_LINE_COLOR = '#f5f1de'

# menu
MENU_GENERAL_RECT_SIZE = 180
MENU_GENERAL_RECT_MARGIN = 6
MENU_BUTTON_MARGIN = 3

HIGHLIGHT_INFLATE = (4,4) 
HIGHLIGHT_WIDTH = 5
HIGHLIGHT_RADIUS = 4

# grid
GRID_LINE_WIDTH = 1