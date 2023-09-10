import pygame

from support import *
from settings import *
from times import *
from items import *

from player import Player
from pytmx.util_pygame import load_pygame
from debug import Display
from random import choice

from items_data import *
from groups import *


class LevelManager:
	def __init__(self, graphics):
		self.graphics = graphics

		self.levels_folder_path = '../levels'
		self.import_tmx_levels()

		self.level_index = 0

		self.players = {}
		self.joyids = []
		self.load_level()

		# cooldowns
		self.cooldowns = {}
		self.cooldowns['level_selection'] = Cooldown(220)


	def connect_disconnect_joysticks(self, joysticks, controls_config):
		self.joysticks = joysticks
		self.controls_config = controls_config

		setattr(self.current_level, 'last_joysticks', self.joysticks.copy())

		self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

		setattr(self.current_level, 'joysticks', self.joysticks)
		setattr(self.current_level, 'controls_config', self.controls_config)


	def import_tmx_levels(self):
		self.tmx_levels = []
		
		for file in get_filenames(self.levels_folder_path):
			self.tmx_levels.append(load_pygame(self.levels_folder_path+'/'+file))

	def load_level(self, joysticks=[], controls_config={}):
		lobby = True if self.level_index == 0 else False

		# getting current level
		self.current_level = Level(
			lobby=lobby,
			graphics=self.graphics,
			joysticks=joysticks,
			tmxmap=self.tmx_levels[self.level_index],
			level_index=self.level_index,
			players=self.players,
			joyids=self.joyids,
			controls_config=controls_config
			)
	
	def select_level(self):
		if self.last_level_index != self.level_index:
			self.players = self.current_level.players
			self.joyids = self.current_level.joyids
			self.load_level(self.joysticks,self.controls_config)

	def input(self):
		keys = pygame.key.get_pressed()

		if not self.cooldowns['level_selection'].on:
			if keys[pygame.K_RIGHT]:
				self.level_index = min(len(self.tmx_levels)-1, self.level_index+1)

				self.cooldowns['level_selection'].start()

			if keys[pygame.K_LEFT]:
				self.level_index = max(0, self.level_index-1)

				self.cooldowns['level_selection'].start()

	def previous_variables(self):
		self.last_level_index = self.level_index

	def update_cooldowns(self):
		for cooldown_dict in self.cooldowns.values():
			if isinstance(cooldown_dict, dict):
				for cooldown in cooldown_dict.values():
					cooldown.update()
			else:
				cooldown_dict.update()

	def update(self, dt):
		self.current_level.update(dt)

	def draw(self):
		self.current_level.draw()

	def run(self, dt):
		self.previous_variables()
		self.update_cooldowns()

		self.input()

		self.select_level()

		self.update(dt)
		self.draw()

		self.current_level.debug_display(self.last_level_index != self.level_index)


class Level:
	def __init__(self, lobby, graphics, joysticks, tmxmap, level_index, players, joyids, controls_config):
		self.window = pygame.display.get_surface()

		self.lobby = lobby

		self.level_index = level_index
		self.tmxmap = tmxmap
		self.graphics = graphics

		self.background_color = tmxmap.background_color

		# forces
		self.get_speed_forces()

		self.get_scales_and_offsets()

		# joysticks
		self.joysticks = joysticks
		self.last_joysticks = []
		self.connected_joystick_ids = []
		self.online_joystick_ids = []
		self.joyids = joyids

		self.controls = {}
		self.controls_config = controls_config

		self.player_start_positions = []
		self.used_positions = {}


		self.my_groups = {
		'visible': pygame.sprite.Group(),
		'updatable': pygame.sprite.Group(),
		'collidable': pygame.sprite.Group(),
		'damaging': pygame.sprite.Group(),
		'damageable': pygame.sprite.Group(),
		'pickable': pygame.sprite.Group(),
		'mobile': pygame.sprite.Group()
		}
		self.players = players

		# player personalization
		self.player_colors = PLAYER_COLORS
		self.player_color_indexes = {}

		# cooldowns
		self.cooldowns = {}
		self.cooldowns['enter/exit'] = {}
		self.cooldowns['color_selection'] = {}
		self.cooldowns['drop item'] = Cooldown(choice(ITEM_DROP_SECONDS_COOLDOWN))
		self.cooldowns['drop item'].start()

		self.setup_map()

		self.get_empty_space_rects()

		self.load_player_start_positions()
		if not self.level_index == 0:
			self.setup_players()

	def get_speed_forces(self):
		self.speed_forces = {}

		for speed in DEFAULT_SPEED_FORCES:
			self.speed_forces[speed] = self.tmxmap.properties[speed]\
			if speed in self.tmxmap.properties\
			else DEFAULT_SPEED_FORCES[speed]

		for force, value in self.speed_forces.items():
			if force in FORCES_TO_CONVERT.keys():
				self.speed_forces[force] = FORCES_TO_CONVERT[force](value)


	def get_scales_and_offsets(self):
		width, height = self.tmxmap.width, self.tmxmap.height
		twidth, theight = self.tmxmap.tilewidth, self.tmxmap.tileheight

		self.tilescale = self.get_window_scaled_tile_dimensions(width, height)
		self.start_x_offset = self.get_start_x_offset(self.tilescale[0]*width)
		self.scale_offset = self.get_scale_offset(
			(self.tilescale[0]*width, self.tilescale[1]*height),(twidth*width,theight*height))

	def get_empty_space_rects(self):
		self.empty_space_rects = []

		width, height = self.tmxmap.width, self.tmxmap.height

		scan_tiles = (4,3)
		scan_rect = pygame.Rect(
			self.start_x_offset,0,self.tilescale[0]*scan_tiles[0],self.tilescale[1]*scan_tiles[1])

		for y in range(
			0,
			round(height*self.tilescale[1]),
			round(self.tilescale[1])):

			for x in range(
				round(self.start_x_offset),
				round(self.start_x_offset+(width*self.tilescale[0])),
				round(self.tilescale[0])):

				scan_rect.x, scan_rect.y = x, y
				
				colliding = False
				for sprite in self.my_groups['collidable']:
					if sprite.hitbox.colliderect(scan_rect):
						colliding = True
						break

				if not colliding:
					self.empty_space_rects.append(scan_rect.copy())
		
	def setup_map(self):
		for x, y, surface in self.tmxmap.get_layer_by_name('BackgroundTiles').tiles():
			Tile({'topleft': (self.start_x_offset+x*self.tilescale[0], y*self.tilescale[1])},
				pygame.transform.scale(surface, self.tilescale),
				[self.my_groups['visible']])

		for x, y, surface in self.tmxmap.get_layer_by_name('CollisionTiles').tiles():
			Tile({'topleft': (self.start_x_offset+x*self.tilescale[0], y*self.tilescale[1])},
				pygame.transform.scale(surface, self.tilescale),
				[self.my_groups['visible']])

		for x, y, surface in self.tmxmap.get_layer_by_name('MobileTiles').tiles():
			MobileTile({'topleft': (self.start_x_offset+x*self.tilescale[0], y*self.tilescale[1])},
				pygame.transform.scale(surface, self.tilescale),
				[self.my_groups['visible'],self.my_groups['mobile'],self.my_groups['collidable'],
				self.my_groups['updatable']],
				self.my_groups['collidable'])			

		for hitbox in self.tmxmap.get_layer_by_name('Hitboxes'):
			Hitbox({'topleft':
				(self.start_x_offset+hitbox.x*self.scale_offset,hitbox.y*self.scale_offset)},
				hitbox.width*self.scale_offset, hitbox.height*self.scale_offset,
				[self.my_groups['collidable']])

	def get_window_scaled_tile_dimensions(self, tmx_width, tmx_height):
		height = self.window.get_height()
		width = height * tmx_width/tmx_height

		return (width / tmx_width, height / tmx_height)

	def get_start_x_offset(self, tmx_pixel_width):
		return (self.window.get_width()-tmx_pixel_width) / 2

	def get_scale_offset(self, in_game_tmx_pixel_dimensions, tiled_tmx_pixel_dimensions):
		x = in_game_tmx_pixel_dimensions[0] / tiled_tmx_pixel_dimensions[0]
		y = in_game_tmx_pixel_dimensions[1] / tiled_tmx_pixel_dimensions[1]
		return x


	def load_player_start_positions(self):
		for pos in self.tmxmap.get_layer_by_name('PlayerPositions'):
			self.player_start_positions.append((
			self.start_x_offset+pos.x*self.scale_offset, pos.y*self.scale_offset))

	def pick_start_position(self, joyid):
		i = 0
		while True:
			pos = self.player_start_positions[i]
			if not pos in self.used_positions.values():
				self.used_positions[joyid] = pos
				break
			i += 1

		return list(pos)

	def load_players(self):
		if self.joysticks:
			for joystick in self.joysticks:

				joyid = joystick.get_instance_id()
				controls = self.controls[joyid]

				if not joyid in self.cooldowns['enter/exit']:
					self.cooldowns['enter/exit'][joyid] = Cooldown(350)

				if not self.cooldowns['enter/exit'][joyid].on:
					if controls['start'] and joyid not in self.online_joystick_ids:

						pos = self.pick_start_position(joyid)
						pos[0] = pos[0] - PLAYER_DEFAULT_SIZES['all'][0]/2
						pos[1] = pos[1] - PLAYER_DEFAULT_SIZES['all'][1]/2

						self.players[joyid] = (Player(
							level=self,
							pos={'topleft': pos},
							animations=self.graphics['player individual shapes']['01'],
							animations_speeds=PLAYER_ANIMATIONS_SPEEDS,
							joystick=joystick,
							groups=self.my_groups,
							control_config=self.controls_config[joystick.get_guid()],
							hand_animations=self.graphics['hand']['01']))

						self.online_joystick_ids.append(joyid)
						self.joyids.append(joyid)
						self.player_color_indexes[joyid] = 0

						self.cooldowns['enter/exit'][joyid].start()

	def delete_players(self):
		self.connected_joystick_ids = [j.get_instance_id() for j in self.joysticks]

		for joyid in self.online_joystick_ids:
			controls = get_joystick_components(self.players[joyid].joystick)

			if not self.cooldowns['enter/exit'][joyid].on:
				if joyid not in self.connected_joystick_ids or controls['start']:

					self.players[joyid].kill()
					for hand in self.players[joyid].hands.values():
						hand.kill()

					del self.players[joyid]
					del self.used_positions[joyid]

					self.joyids.remove(joyid)
					self.online_joystick_ids.remove(joyid)

					self.cooldowns['enter/exit'][joyid].start()

	def setup_players(self):
		for joyid in self.joyids:
			pos = self.pick_start_position(joyid)
			pos[0] = pos[0] - PLAYER_DEFAULT_SIZES['all'][0]/2
			pos[1] = pos[1] - PLAYER_DEFAULT_SIZES['all'][1]/2

			joystick = [joystick for joystick in self.joysticks if joystick.get_instance_id()==joyid]

			animations = self.players[joyid].source_animations
			hand_animations = self.players[joyid].source_hand_animations

			# for k1, sides in self.players[joyid].animations.items():
			# 	for k2, frames in sides.items():
			# 		for surface in frames:
			# 			surface.set_colorkey('black')

			if joystick:
				control_config = self.controls_config[joystick[0].get_guid()]
			else:
				control_config = None

			self.players[joyid] = (Player(
				level=self,
				pos={'topleft': pos},
				animations=animations,
				animations_speeds=PLAYER_ANIMATIONS_SPEEDS,
				joystick=joystick[0] if joystick else None,
				groups=self.my_groups,
				control_config=control_config,
				hand_animations=hand_animations))

			self.online_joystick_ids.append(joyid)

	def connect_players(self):
		offline_ids = [joyid for joyid in self.connected_joystick_ids
		if joyid not in self.online_joystick_ids]

		for joyid in offline_ids:
			for player in self.players.copy().values():
				if player.joystick == None:
					offline_joystick = [j for j in self.joysticks
					if j.get_instance_id() not in self.online_joystick_ids]

					joystick = offline_joystick[0] if offline_joystick else None
					player.joystick = joystick
					player.control_config = self.controls_config[joystick.get_guid()]

					self.online_joystick_ids.append(joyid)
					self.players[joyid] = player
					key = key_from_value(self.players, player)
					del self.players[key]

	def disconnect_players(self):
		disconnected_ids = [joyid for joyid in self.online_joystick_ids
		if joyid not in self.connected_joystick_ids]

		for joyid in disconnected_ids:
			self.players[joyid].joystick = None
			self.online_joystick_ids.remove(joyid)


	def select_color(self):
		for joyid, controls in self.controls.items():
			if not joyid in self.cooldowns['color_selection']:
				self.cooldowns['color_selection'][joyid] = Cooldown(220)

			if not self.cooldowns['color_selection'][joyid].on:
				direction = 0
				if controls['R1']:
					direction = 1

				if controls['L1']:
					direction = -1

				if direction != 0:	
					self.player_color_indexes[joyid] = numloop(
						self.player_color_indexes[joyid], direction, 0, len(self.player_colors)-1)

					self.players[joyid].change_color(self.player_colors[self.player_color_indexes[joyid]])

					self.cooldowns['color_selection'][joyid].start()

	def get_controls(self):
		if self.joysticks:
			self.controls = {}
			for joystick in self.joysticks:
				self.controls[joystick.get_instance_id()] = get_joystick_components(joystick)


	def drop_item(self):
		if not self.cooldowns['drop item'].on:
			self.cooldowns['drop item'].start(choice(ITEM_DROP_SECONDS_COOLDOWN)*1000)

			i = ITEMS_DATA[choice(DEFAULT_DROPABLE_ITEM_SET)].copy()

			# Special Attributes
			if i['class'] is Gun:
				projectile_parameters = i['unpackable']['projectile_parameters']
				projectile_parameters['unpackable']['animations'] =\
				self.graphics['items'][projectile_parameters['unpackable']['name']]

			# Creating an Item
			i['class'](
				**i['unpackable'],
				level=self,
				pos={'center': choice(self.empty_space_rects).center},
				animations=self.graphics['items'][i['unpackable']['name']],
				groups=self.my_groups)


	def previous_variables(self):
		self.last_players = self.players.copy()
		self.last_connected_joystick_ids = self.connected_joystick_ids

	def update_cooldowns(self):
		for cooldown_dict in self.cooldowns.values():
			if isinstance(cooldown_dict, dict):
				for cooldown in cooldown_dict.values():
					cooldown.update()
			else:
				cooldown_dict.update()

	def update(self, dt):
		self.previous_variables()
		self.update_cooldowns()
		self.get_controls()

		if self.lobby:
			self.load_players()
			self.delete_players()

			self.select_color()
		else:
			self.connected_joystick_ids = [j.get_instance_id() for j in self.joysticks]
			if self.connected_joystick_ids != self.last_connected_joystick_ids:
				self.disconnect_players()
				self.connect_players()

		if not self.lobby:
			self.drop_item()

		self.my_groups['updatable'].update(dt)

	def draw(self):
		self.window.fill(self.background_color)
		sort_group(self.my_groups['visible'], lambda sprite: sprite.z)
		self.my_groups['visible'].draw(self.window)

		# for rect in self.empty_space_rects:
		# 	pygame.draw.rect(self.window,'green',rect)


	def debug_display(self, level_changed):
		if self.players != self.last_players or level_changed:
			if self.players.values():
				# P1
				self.p1_display = Display('../fonts/ThaleahFat.ttf',24,
					{'topleft':(0,0)},20,
					list(self.players.values())[0],'health')
				self.p1_display2 = Display('../fonts/ThaleahFat.ttf',24,
					{'topleft':(0, self.p1_display.rect.bottom)},20,
					list(self.players.values())[0],'direction')

				try:
					self.p2_display = Display('../fonts/ThaleahFat.ttf',24,
						{'topleft':(0, self.p1_display2.rect.bottom)},20,
						list(self.players.values())[1],'health')
				except IndexError:
					pass

		if hasattr(self, 'p1_display'):
			self.p1_display.run()
			self.p1_display2.run()
			try:
				self.p2_display.run()
			except AttributeError:
				pass


class Tile(pygame.sprite.Sprite):
	def __init__(self, pos, surface, groups, *args, **kwargs):
		super().__init__(groups, *args, **kwargs)
		self.z = Z_AXIS['tile']

		self.image = surface
		self.rect = self.image.get_rect(**pos)

		self.hitbox = self.rect.copy()

		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

	def get_hitbox_by_rect(self):
		self.hitbox = self.rect.copy()

	def get_rect_by_hitbox(self):
		self.rect = self.hitbox.copy()


class MobileTile(Tile, Collisor):
	def __init__(self, pos, surface, groups, collidable_group):
		super().__init__(pos, surface, groups, collidable_group)

		self.create_collision_rects()

	def get_player(self, player):
		self.player = player
		print(player)

	def update(self, dt):
		if hasattr(self, 'player'):
			print(self.player)


class Hitbox(pygame.sprite.Sprite):
	def __init__(self, pos, width, height, groups):
		super().__init__(groups)

		self.rect = pygame.Rect(0,0,width,height)

		key, value = list(pos.items())[0]
		setattr(self.rect, key, value)

		self.hitbox = self.rect.copy()

		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()