from items import *

NORMAL_RESETABLE_ITEM_ACTIONS = ['hammer', 'pistol', 'bazuca', 'machinegun']
STOP_AT_THE_END_RESETABLE_ITEM_ACTIONS = ['flamethrower']
NORMAL_COOLDOWN_ITEMS_USE = {'hammer': 300, 'pistol': 180, 'bazuca': 1200, 'machinegun': 60,
'flamethrower': 25}

ITEMS_DATA = {
'flamethrower': {'class': Gun,
		'unpackable': {
			'name': 'flamethrower',
			'action': 'hold',
			'idling_hand_animation_state': 'idle',
			'acting_hand_animation_state': 'idle',
			'anchors': {
				'left': ['center',('center',(0,0))],
				'right': ['center',('center',(0,0))]},
			'projectile_parameters': {
				'class': SelfConsumableProjectile,
				'unpackable': {
					'name': 'flame',
					'animations_speeds': {'move': 7, 'destroy': 12},
					'frames_default_sizes': {'move': (12*2.5,12*2.5), 'destroy': (12*2.5,12*2.5)},
					'speed': 300,
					'on_contact_damage_amount': 1,
					'destruction_damage_amount': 0.5,
					'on_contact_damage_frames': 'all',
					'destruction_damage_frames': 'all',
					'anchors': {
						'left': ['midright',('topleft',(0,16))],
						'right': ['midleft',('topright',(0,16))]},
					'destruction_anchors': {
						'left': ['midleft',('midleft',(0,0))],
						'right': ['midright',('midright',(0,0))]},
					'drilling_potential': -1,
					'consumption_speed': 300*3/2,
					'consumable_energy': 300,
					'fade_speed': 255*2/3,
					'start_fade': 255,
					'end_fade': 0}},
			'animations_speeds': {'idle': 0},
			'frames_default_sizes': {'idle': (51*1.5,30*1.5)},
			'hand_actions_magnitudes': {},
			'hand_actions_animations_speeds': {}}},

'machinegun': {'class': Gun,
		'unpackable': {
			'name': 'machinegun',
			'action': 'rumble2',
			'idling_hand_animation_state': 'idle',
			'acting_hand_animation_state': 'idle',
			'anchors': {
				'left': ['center',('center',(0,0))],
				'right': ['center',('center',(0,0))]},
			'projectile_parameters': {
				'class': Projectile,
				'unpackable': {
					'name': 'bullet',
					'animations_speeds': {'move': 0, 'destroy': 13},
					'frames_default_sizes': {'move': (6*2,3*2), 'destroy': (10*2,13*2)},
					'speed': 900,
					'on_contact_damage_amount': 3,
					'destruction_damage_amount': None,
					'on_contact_damage_frames': 'all',
					'destruction_damage_frames': None,
					'anchors': {
						'left': ['midleft',('midleft',(0,2))],
						'right': ['midright',('midright',(0,2))]},
					'destruction_anchors': {
						'left': ['midleft',('midleft',(0,0))],
						'right': ['midright',('midright',(0,0))]},
					'drilling_potential': 2}},
			'animations_speeds': {'idle': 0},
			'frames_default_sizes': {'idle': (35*2,12*2)},
			'hand_actions_magnitudes': {},
			'hand_actions_animations_speeds': {}}}, 

'pistol': {'class': Gun,
		'unpackable': {
			'name': 'pistol',
			'action': 'rumble',
			'idling_hand_animation_state': 'idle',
			'acting_hand_animation_state': 'idle',
			'anchors': {
				'left': ['midright',('center',(0,0))],
				'right': ['midleft',('center',(0,0))]},
			'projectile_parameters': {
				'class': Projectile,
				'unpackable': {
					'name': 'bullet',
					'animations_speeds': {'move': 0, 'destroy': 10},
					'frames_default_sizes': {'move': (6*2,3*2), 'destroy': (10*1.5,13*1.5)},
					'speed': 700,
					'on_contact_damage_amount': 2,
					'destruction_damage_amount': None,
					'on_contact_damage_frames': 'all',
					'destruction_damage_frames': None,
					'anchors': {
						'left': ['midleft',('midleft',(0,-8))],
						'right': ['midright',('midright',(0,-8))]},
					'destruction_anchors': {
						'left': ['midleft',('midleft',(0,0))],
						'right': ['midright',('midright',(0,0))]},
					'drilling_potential': 1}},
			'animations_speeds': {'idle': 0},
			'frames_default_sizes': None,
			'hand_actions_magnitudes': {},
			'hand_actions_animations_speeds': {}}}, 

'bazuca': {'class': Gun,
		'unpackable': {
			'name': 'bazuca',
			'action': 'rumble',
			'idling_hand_animation_state': 'idle',
			'acting_hand_animation_state': 'idle',
			'anchors': {
				'left': ['midright',('center',(30,0))],
				'right': ['midleft',('center',(-30,0))]},
			'projectile_parameters': {
				'class': Projectile,
				'unpackable': {
					'name': 'rocket',
					'animations_speeds': {'move': 0, 'destroy': 12},
					'frames_default_sizes': {'move': (21*2,7*2), 'destroy': (520*0.3,520*0.3)},
					'speed': 300,
					'on_contact_damage_amount': 2,
					'destruction_damage_amount': 10,
					'on_contact_damage_frames': 'all',
					'destruction_damage_frames': list(range(4,9)),
					'anchors': {
						'left': ['midleft',('midleft',(0,0))],
						'right': ['midright',('midright',(0,0))]},
					'destruction_anchors': {
						'left': ['center',('center',(0,0))],
						'right': ['center',('center',(0,0))]},
					'drilling_potential': 0}},
			'animations_speeds': {'idle': 0},
			'frames_default_sizes': {'idle': (26*2,15*2)},
			'hand_actions_magnitudes': {'rumble': 240},
			'hand_actions_animations_speeds': {'rumble': 14}}}, 

'hammer': {'class': Hammer,
		'unpackable': {
		'name': 'hammer',
		'action': 'smash',
		'idling_hand_animation_state': 'idle',
		'acting_hand_animation_state': 'idle',
		'anchors': {
				'left': ['midright',('center',(0,0))],
				'right': ['midleft',('center',(0,0))]},
		'animations_speeds': {'idle': 0},
		'frames_default_size': None,
		'hand_actions_magnitudes': {'idle': 24, 'walk': 30},
		'hand_actions_animations_speeds': {'idle': 4, 'walk': 2}}}} 
