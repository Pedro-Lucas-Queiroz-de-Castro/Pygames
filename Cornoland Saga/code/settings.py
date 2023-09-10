WITH_OR_NOT_SWORD_ANIMAION_STATES = ('idle', 'idle crouch', 'run', 'jump prepare', 'jump', 'somersault', 'fall',
	'slide', 'death', 'death crouch')
SWORD_ON_OR_OFF_ANIMAION_STATES = ('idle sword', 'run sword')

ANIMATION_SLICE_INFO = {'player': {'idle sword sheathed': (0,3), 'idle crouch sword': (4,7), 'run sword sheathed': (8,13), 
'jump prepare sword': (14,15), 'jump sword': (16,16), 'somersault sword': (17,21), 'fall sword': (22,23), 'slide sword': (24,28),
'corner grab sword': (29,32), 'corner climb sword': (33,37), 'idle sword drawed': (38,41), 'sword attack 0': (42,49), 
'sword attack 1': (50,52), 'sword attack 2': (53,58), 'death sword': (59,68), 'death crouch sword': (66, 68),
'sword draw': (69,72), 'sword sheathe': (73,76), 'climb sword': (81,84), 'cast spell sword': (85,92),
'death fall': (141, 144), 'death fall floor hit': (145, 148), 'death fall floor hit up': (145, 145),
'death fall floor hit down': (144, 144), 'walk': (155,160), 'walk crouch': (161,166), 
'run crouch': (161,166), 'idle': (179, 182), 'run': (187,192), 'run sword drawed': (303,308)},

'melee attack hitboxes': {'slide': (0,4),
'sword attack 0': (5,12),'sword attack 1': (13,15),'sword attack 2': (16,21)}}

# ------------------------------------------------------------------------------------------------------ #

ANIMATION_SPEEDS = {'player': {'idle sword sheathed': 5, 'idle crouch sword': 5, 'run sword sheathed': 16, 'jump prepare sword': 60, 'jump sword': 5,
'somersault sword': 14, 'fall sword': 10, 'slide sword': 10, 'corner grab sword': 10, 'corner climb sword': 10, 'idle sword drawed': 7,
'sword attack 0': 22, 'sword attack 1': 22, 'sword attack 2': 22, 'death': 5, 'death crouch sword': 5,
'sword draw': 7, 'sword sheathe': 7, 'climb sword': 6, 'cast spell sword': 10, 'death fall': 5, 
'death fall floor hit': 5, 'death fall floor hit up': 0, 'death fall floor hit down': 0, 'walk': 10,
'walk crouch': 5, 'run crouch': 10, 'idle': 5, 'run': 16, 'run sword drawed': 16}}

# ------------------------------------------------------------------------------------------------------ #

# [(spritesheet_key,path,sprite_dimensions,superkey,animations_key,scale_value,erase_empty,source), ...]
SPRITESHEET_IMPORT_DATA = [
('sheet01','../graphics/player/sheet01.png',(50,37),'player',None,4,True,'image'),
('sheet02','../graphics/player/sheet02.png',(50,37),'player',None,4,True,'image'),
('sheet03','../graphics/player/sheet03.png',(50,37),'player',None,4,True,'image'),
('sheet04','../graphics/player/sheet04.png',(50,37),'player',None,4,True,'image'),
('sheet05','../graphics/player/sheet05.png',(50,37),'player',None,4,True,'image'),
('melee attack hitboxes','../graphics/player/melee_attack_hitboxes.png',(50,37),'melee attack hitboxes',None,4,True,'image'),
('menu hearts','../graphics/UI/hearts/hearts_spritesheet.png',(17,17),'UI','hearts',2,True,'image'),
('fire worm','../graphics/enemies/Fire Worm/Sprites/Worm',(90,90),'fire worm',None,4,True,'folder'),
('fire ball','../graphics/enemies/Fire Worm/Sprites/Fire Ball',(46,46),'fire ball',None,4,False,'folder')
]

# ------------------------------------------------------------------------------------------------------ #

# WINDOW
WINDOW_WIDTH, WINDOW_HEIGHT = 1366, 768
# WINDOW_WIDTH, WINDOW_HEIGHT = 16*50, 9*50

# MENU
MENU_LOGO_RELPOS = (0.5, 0.22)

MENU_BUTTONS_RELPOS = {'play': (0.5,0.5), 'exit': (0.5,0.61)}
MENU_BUTTONS_RELWIDTH = 0.3
MENU_BUTTONS_RELHEIGHT = 0.1
MENU_BUTTONS_FONT_SIZE = 45

MENU_BUTTONS_BORDER_COLORS = '#001c40'
MENU_BUTTONS_TEXT_COLORS = ('#fff9e5', '#ccc7b7', '#33322e')


# UI
# Hearts
HEARTS_START_NUMBER = 5

FIRST_HEART_POS = (30,30)
HEART_HORIZONTAL_THRESHOLD = 10
HEART_VERTICAL_THRESHOLD = 4
MAX_HEARTS_NUMBER = 30

# Stamina
STAMINA_START_AMOUNT = 100

STAMINA_WHEEL_START_DEGREE = 90
STAMINA_WHEEL_POS = (WINDOW_WIDTH//2-75,WINDOW_HEIGHT//2-75)
STAMINA_WHEEL_SIZE = (30,30)
MAIN_STAMINA_WHEEL_THICKNESS = 9
STAMINA_WHEEL_THICKNESS = 3
STAMINA_WHEEL_RADIUS_DISTANCE = 5

MAX_STAMINA_WHEELS = 3

MAX_STAMINA_WHEEL_COLOR = '#181a17'
LAST_STAMINA_WHEEL_COLOR = '#f52020'
STAMINA_WHEEL_COLOR = '#43f41f'
EXHAUSTED_STAMINA_WHEEL_COLOR = '#aa0a19'

FULL_STAMINA_WHEEL_UNITS = 100

STAMINA_COSTS = {'running': 20, 'climbing': 10}


# GAME OVER
GAME_OVER_FONT_SIZE = 100
DEATH_FADE_FILTER_COLOR = '#030211'
GAMEOVER_FADE_TEXT_COLOR = '#aa0a19'
