import pygame, sys, pickle
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_buttons
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load

from settings import *
from support import *

from menu import Menu
from timer import Timer

from random import choice, randint


class Editor:
	def __init__(self, land_tiles, switch):
		
		# main setup 
		self.display_surface = pygame.display.get_surface()
		self.canvas_data = {}
		self.switch = switch

		# imports 
		self.land_tiles = land_tiles
		self.imports()

		# clouds
		self.current_clouds = []
		self.cloud_surf = import_folder('../graphics/clouds')
		self.cloud_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.cloud_timer, 2000)
		self.startup_clouds()

		# navigation
		self.origin = vector()
		self.pan_active = False
		self.pan_offset = vector()

		# support lines 
		self.support_line_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
		self.support_line_surf.set_colorkey('green')
		self.support_line_surf.set_alpha(30)

		# selection
		self.selection_index = MIN_MENU_SELECTION_INDEX
		self.last_selected_cell = None

		# menu 
		self.menu = Menu()

		# objects
		self.canvas_objects = pygame.sprite.Group()
		self.background = pygame.sprite.Group()
		self.foreground = pygame.sprite.Group()
		self.object_drag_active = False
		self.object_timer = Timer(50)

		# hotkeys
		self.hotkey_general_timer = Timer(130)

		# timeline
		self.serialized_background = []
		self.serialized_foreground = []

		self.timeline_max_length = 11
		self.timeline = []
		self.timeline_index = 0

		self.initial_objects()
		self.undeletable_objects = ('player', 'sky', 'flag', 'death_line')

		self.timeline_append()
		self.editor_data_update()

	# support
	def initial_objects(self):
		# Player
		self.serialized_foreground.append(CanvasObject(
			pos = (200, WINDOW_HEIGHT / 2), 
			frames = self.animations[0]['frames'],
			tile_id =  0, 
			origin = self.origin, 
			groups = [self.foreground, self.canvas_objects],
			editor = self).serialize())

		# Sky Handle
		self.sky_handle = CanvasObject(
			pos = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
			frames = [self.sky_handle_surf],
			tile_id = 1,
			origin = self.origin,
			groups = [self.foreground, self.canvas_objects],
			editor = self)

		self.serialized_foreground.append(self.sky_handle.serialize())

		# Flag
		flag_surf = pygame.Surface((60,200))
		flag_surf.fill('green')

		self.serialized_foreground.append(CanvasObject(
			pos = (WINDOW_WIDTH * 4/5, WINDOW_HEIGHT / 2),
			frames = self.animations[19]['frames'],
			tile_id = 19,
			origin = self.origin,
			groups = [self.foreground, self.canvas_objects],
			editor = self).serialize())

		# Death Line
		self.death_cross = CanvasObject(
			pos = (WINDOW_WIDTH / 2, WINDOW_HEIGHT * 4/5),
			frames = [self.death_cross_surf],
			tile_id = 20,
			origin = self.origin,
			groups = [self.foreground, self.canvas_objects],
			editor = self)

		self.serialized_foreground.append(self.death_cross.serialize())

	def get_current_cell(self, obj=None):
		if obj:
			# distance_to_origin = vector(obj.distance_to_origin) - self.origin
			distance_to_origin = obj.distance_to_origin
		else:
			distance_to_origin = vector(mouse_pos()) - self.origin

		if distance_to_origin.x > 0:
			col = int(distance_to_origin.x / TILE_SIZE)
		else:
			col = int(distance_to_origin.x / TILE_SIZE) - 1

		if distance_to_origin.y > 0:
			row = int(distance_to_origin.y / TILE_SIZE)
		else:
			row = int(distance_to_origin.y / TILE_SIZE) - 1

		return col, row

	def check_neighbors(self, cell_pos):

		# create a local cluster
		cluster_size = 3
		local_cluster = [
			(cell_pos[0] + col - int(cluster_size / 2), cell_pos[1] + row - int(cluster_size / 2)) 
			for col in range(cluster_size) 
			for row in range(cluster_size)]

		# check neighbors
		for cell in local_cluster:
			if cell in self.canvas_data:
				self.canvas_data[cell].terrain_neighbors = []
				self.canvas_data[cell].water_on_top = False
				for name, side in NEIGHBOR_DIRECTIONS.items():
					neighbor_cell = (cell[0] + side[0],cell[1] + side[1])

					if neighbor_cell in self.canvas_data:
					# water top neighbor
						if self.canvas_data[neighbor_cell].has_water and self.canvas_data[cell].has_water and name == 'A':
							self.canvas_data[cell].water_on_top = True

					# terrain neighbors
						if self.canvas_data[neighbor_cell].has_terrain:
							self.canvas_data[cell].terrain_neighbors.append(name)

	def imports(self):
		self.water_bottom = load('../graphics/terrain/water/water_bottom.png').convert_alpha()
		self.sky_handle_surf = load('../graphics/cursors/handle.png').convert_alpha()
		self.death_cross_surf = load('../graphics/death/death_line.png').convert_alpha()

		# animations
		self.animations = {}
		for key, value in EDITOR_DATA.items():
			if value['graphics']:
				graphics = import_folder(value['graphics'])
				self.animations[key] = {
					'frame index': 0,
					'frames': graphics,
					'length': len(graphics)
				}

		# preview
		self.preview_surfs = {key: load(value['preview']) for key, value in EDITOR_DATA.items() if value['preview']}

	def animation_update(self, dt):
		for value in self.animations.values():
			value['frame index'] += ANIMATION_SPEED * dt
			if value['frame index'] >= value['length']:
				value['frame index'] = 0

	def mouse_on_object(self):
		for sprite in self.canvas_objects:
			if sprite.rect.collidepoint(mouse_pos()):
				return sprite

	def create_grid(self):
		'''
		Returns a dict with keys referencing tile and objects and dict values with pixel position keys,
		and some info value to build the level.
		'''

		# clean this cell tile objects
		for tile in self.canvas_data.values():
			tile.objects.clear()

		# add objects to the title
		for obj in self.canvas_objects:
			topleft_obj_cell = self.get_current_cell(obj)
			offset = vector(obj.distance_to_origin) - vector(topleft_obj_cell) * TILE_SIZE

			# if this cell has a tile
			if topleft_obj_cell in self.canvas_data:
				self.canvas_data[topleft_obj_cell].add_id(obj.tile_id, offset)
			else:
				self.canvas_data[topleft_obj_cell] = CanvasTile(obj.tile_id, offset)

		# create the layers data structure for level creation, now is empty
		# the order is important for 'z' axis
		layers = {
			'waters': {},
			'bg palms': {},
			'terrains': {},
			'coins': {},
			'fg objects': {},
			'enemies': {}}

		# grid offset - the most left and top cell with tile
		left = sorted(self.canvas_data.keys(), key=lambda cell: cell[0])[0][0]
		top = sorted(self.canvas_data.keys(), key=lambda cell: cell[1])[0][1]

		# fill the layers with tile data
		for cell, tile in self.canvas_data.items():
			col_adjusted = cell[0] - left  # cell pos, left is always lower or equal to cell[0]
			row_adjusted = cell[1] - top   # cell pos, top  is always lower or equal to cell[1]
			# which means that col and row adjusteds are >= 0, always

			x = col_adjusted * TILE_SIZE  # pixel pos
			y = row_adjusted * TILE_SIZE  # pixel pos

			# finally fill layers
			if tile.has_water:
				layers['waters'][(x,y)] = tile.get_water()

			if tile.has_terrain:
				neighbor = tile.get_terrain()         # terrain surfaces key names: 'ABCDEFGH'
				layers['terrains'][(x,y)] = neighbor if neighbor in self.land_tiles else 'X'

			if tile.coin:
				# the coin position is the center of the cell
				layers['coins'][(x+TILE_SIZE//2,y+TILE_SIZE//2)] = tile.coin

			if tile.enemy:
				# the enemy position is the midbottom of the cell
				layers['enemies'][(x+TILE_SIZE//2,y+TILE_SIZE)] = tile.enemy

			if tile.objects:
				# for the level creation is useful separate
				# 'bg palms' from 'fg objects' like fg palm, player and sky handle
				bg_palm_ids = [key for key, value in EDITOR_DATA.items() if value['style'] == 'palm_bg']

				for obj_id, offset in tile.objects:
					if obj_id in bg_palm_ids: # bg palms
										       # topleft pos
						layers['bg palms'][(int(x+offset.x), int(y+offset.y))] = obj_id
					else: # fg objects
									             # topleft pos
						layers['fg objects'][(int(x+offset.x), int(y+offset.y))] = obj_id

		return layers

	def timers(self):
		self.object_timer.update()
		self.hotkey_general_timer.update()

	def timeline_append(self):
		# timeline append
		self.timeline.append((
			self.serialized_background.copy(),
			self.canvas_data.copy(),
			self.serialized_foreground.copy()
			))

		# timeline adjustment
		while len(self.timeline) > self.timeline_max_length:
			del self.timeline[0]

		self.timeline_index = len(self.timeline)-1
		
		# editor data update
		self.editor_data_update()

		self.print_debug('APPEND')

	def editor_data_update(self):
		# for back, tile, fore in self.timeline:
		# 	print(back, tile, fore)

		self.serialized_background = self.timeline[self.timeline_index][0].copy()
		self.serialized_foreground = self.timeline[self.timeline_index][2].copy()

		self.canvas_objects_update()

		self.canvas_data = self.timeline[self.timeline_index][1].copy()

	def deserialize_canvas_object(self, objects):
		for obj in objects:
			attributes = {'tile_id': obj.tile_id, 'frames': deserialize_surfaces(obj.frames,obj.frame_sizes),
				'frame_index': obj.frame_index, 'image': obj.image, 'rect': pygame.Rect(*obj.rect),
				'distance_to_origin': vector(obj.distance_to_origin),
				'mouse_offset': vector(obj.mouse_offset), 'selected': obj.selected}

			groups = self.background if EDITOR_DATA[obj.tile_id]['style'] == 'palm_bg' else self.foreground

			canvas_obj = CanvasObject(
				attributes['rect'].center, 
				attributes['frames'], 
				attributes['tile_id'], 
				self.origin, 
				[self.canvas_objects]+[groups],
				self)

			for key, value in attributes.items():
				setattr(canvas_obj, key, value)

			if obj.tile_id == 1: # sky handle
				self.sky_handle = canvas_obj

			elif obj.tile_id == 20: # death line
				self.death_cross = canvas_obj

	def canvas_objects_update(self):
		# clean 
		self.canvas_objects = pygame.sprite.Group()
		self.background = pygame.sprite.Group()
		self.foreground = pygame.sprite.Group()

		# pos update
		for serie in self.serialized_background + self.serialized_foreground:
			serie.pan_pos((self.origin.x, self.origin.y))

		# CanvasObject creation
		self.deserialize_canvas_object(self.serialized_background.copy())
		self.deserialize_canvas_object(self.serialized_foreground.copy())

	def print_debug(self, text):
		pass

		# print('='* 100)
		# print(text)
		# print('='* 100)
		# print(f'Index: {self.timeline_index}')
		# print('-'* 100)

		# for i, data in enumerate(self.timeline):
		# 	print(f'{i}: {data}')

		# print('-'* 100)
		# print(self.canvas_data)
		# print('='* 100)


	# input
	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
				grid = self.create_grid()
				self.switch(grid)
			
			self.pan_input(event)
			self.selection_hotkeys(event)
			self.menu_click(event)

			self.object_drag(event)
			
			self.canvas_add()
			self.canvas_remove()

			self.create_clouds(event)

	def pan_input(self, event):

		# middle mouse button pressed / released 
		if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[1]:
			self.pan_active = True
			self.pan_offset = vector(mouse_pos()) - self.origin

		if not mouse_buttons()[1]:
			self.pan_active = False

		# mouse wheel 
		if event.type == pygame.MOUSEWHEEL:
			if pygame.key.get_pressed()[pygame.K_LSHIFT]:
				self.origin.x += event.y * 50
			else:
				self.origin.y += event.y * 50

			self.canvas_objects_update()


		# panning update
		if self.pan_active:
			self.origin = vector(mouse_pos()) - self.pan_offset

			self.canvas_objects_update()

	def selection_hotkeys(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RIGHT:
				self.selection_index += 1
			if event.key == pygame.K_LEFT:
				self.selection_index -= 1
		self.selection_index = max(MIN_MENU_SELECTION_INDEX,min(self.selection_index, MAX_MENU_SELECTION_INDEX))

	def menu_click(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_pos()):
			new_index = self.menu.click(mouse_pos(), mouse_buttons())
			prev_index = self.selection_index
			self.selection_index = new_index if new_index else prev_index

	def canvas_add(self):
		if mouse_buttons()[0] and not self.menu.rect.collidepoint(mouse_pos()) and not self.object_drag_active:
			current_cell = self.get_current_cell()
			if EDITOR_DATA[self.selection_index]['type'] == 'tile':

				if current_cell != self.last_selected_cell:
					if current_cell in self.canvas_data:
						self.canvas_data[current_cell] = self.canvas_data[current_cell].copy()
						self.canvas_data[current_cell].add_id(self.selection_index)
					else:
						self.canvas_data[current_cell] = CanvasTile(self.selection_index).copy()
			
					self.check_neighbors(current_cell)
					self.last_selected_cell = current_cell

					self.timeline_append()

			else: # object
				if not self.object_timer.active:
					serialized_list, groups = (self.serialized_background, self.background)\
					if EDITOR_DATA[self.selection_index]['style'] == 'palm_bg'\
					else (self.serialized_foreground, self.foreground)

					serialized_list.append(CanvasObject(
								pos = mouse_pos(),
								frames = self.animations[self.selection_index]['frames'],
								tile_id = self.selection_index,
								origin = self.origin,
								groups = [groups] + [self.canvas_objects],
								editor = self).serialize())

					self.object_timer.activate()

					self.timeline_append()

	def canvas_remove(self):
		if mouse_buttons()[2] and not self.menu.rect.collidepoint(mouse_pos()):

			# delete object
			selected_object = self.mouse_on_object()
			if selected_object:
				style = EDITOR_DATA[selected_object.tile_id]['style']
				if style not in self.undeletable_objects:
					serialized_list = self.serialized_background\
					 if style == 'palm_bg' else self.serialized_foreground
					

					for serialized in serialized_list:
						if serialized.tile_id == selected_object.tile_id\
						and serialized.distance_to_origin[0] == selected_object.distance_to_origin.x\
						and serialized.distance_to_origin[1] == selected_object.distance_to_origin.y:

							serialized_list.remove(serialized)

					self.timeline_append()

					selected_object.kill()

			# delete tiles
			if self.canvas_data:
				current_cell = self.get_current_cell()
				if current_cell in self.canvas_data:
					self.canvas_data[current_cell] = self.canvas_data[current_cell].copy()
					self.canvas_data[current_cell].remove_id(self.selection_index)

					if self.canvas_data[current_cell].is_empty:
						del self.canvas_data[current_cell]

					self.check_neighbors(current_cell)

					self.timeline_append()

					self.print_debug('REMOVE')

	def object_drag(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
			for sprite in self.canvas_objects:
				if sprite.rect.collidepoint(event.pos):
					sprite.start_drag()
					self.object_drag_active = True

		if event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
			for sprite in self.canvas_objects:
				if sprite.selected:
					sprite.drag_end(self.origin)
					self.object_drag_active = False

	def hotkeys(self):
		keys = pygame.key.get_pressed()

		if not self.hotkey_general_timer.active:
			if keys[pygame.K_LCTRL]:
				if keys[pygame.K_z]:
					self.control_z()
					self.hotkey_general_timer.activate()

				elif keys[pygame.K_y]:
					self.control_y()
					self.hotkey_general_timer.activate()

				elif keys[pygame.K_s]:
					self.control_s()
					self.hotkey_general_timer.activate()

				elif keys[pygame.K_l]:
					self.control_l()
					self.hotkey_general_timer.activate()

	def control_z(self):
		self.timeline_index -= 1
		self.timeline_index = max(0, self.timeline_index)
		self.editor_data_update()

		self.print_debug('CONTROL-Z')

	def control_y(self):
		self.timeline_index += 1
		self.timeline_index = min(self.timeline_index, len(self.timeline)-1)
		self.editor_data_update()

		self.print_debug('CONTROL-Y')

	def control_s(self):
		self.save(input('save as: '))

	def control_l(self):
		self.load(input('load filename: '))


	# drawing 
	def draw_tile_lines(self):
		cols = WINDOW_WIDTH // TILE_SIZE
		rows = WINDOW_HEIGHT// TILE_SIZE

		origin_offset = vector(
			x = self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE,
			y = self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE)

		self.support_line_surf.fill('green')

		for col in range(cols + 1):
			x = origin_offset.x + col * TILE_SIZE
			pygame.draw.line(self.support_line_surf,LINE_COLOR, (x,0), (x,WINDOW_HEIGHT))

		for row in range(rows + 1):
			y = origin_offset.y + row * TILE_SIZE
			pygame.draw.line(self.support_line_surf,LINE_COLOR, (0,y), (WINDOW_WIDTH,y))

		self.display_surface.blit(self.support_line_surf,(0,0))

	def draw_level(self):
		self.background.draw(self.display_surface)

		for cell_pos, tile in self.canvas_data.items():
			pos = self.origin + vector(cell_pos) * TILE_SIZE

			# water
			if tile.has_water:
				if tile.water_on_top:
					self.display_surface.blit(self.water_bottom, pos)
				else:
					frames = self.animations[3]['frames']
					index  = int(self.animations[3]['frame index'])
					surf = frames[index]
					self.display_surface.blit(surf, pos)

			if tile.has_terrain:
				terrain_string = ''.join(tile.terrain_neighbors)
				terrain_style = terrain_string if terrain_string in self.land_tiles else 'X'
				self.display_surface.blit(self.land_tiles[terrain_style], pos)

			# coins
			if tile.coin:
				frames = self.animations[tile.coin]['frames']
				index = int(self.animations[tile.coin]['frame index'])
				surf = frames[index]
				rect = surf.get_rect(center = (pos[0] + TILE_SIZE // 2,pos[1]+ TILE_SIZE // 2))
				self.display_surface.blit(surf, rect)

			# enemies
			if tile.enemy:
				frames = self.animations[tile.enemy]['frames']
				index = int(self.animations[tile.enemy]['frame index'])
				surf = frames[index]
				rect = surf.get_rect(midbottom = (pos[0] + TILE_SIZE // 2,pos[1]+ TILE_SIZE))
				self.display_surface.blit(surf, rect)

		self.foreground.draw(self.display_surface)

	def preview(self):
		selected_object = self.mouse_on_object()
		if not self.menu.rect.collidepoint(mouse_pos()):
			if selected_object:
				rect = selected_object.rect.inflate(10,10)
				color = 'black'
				width = 3
				size = 15

				# topleft
				pygame.draw.lines(self.display_surface, color, False, ((rect.left,rect.top + size), rect.topleft, (rect.left + size,rect.top)), width)
				#topright
				pygame.draw.lines(self.display_surface, color, False, ((rect.right - size,rect.top), rect.topright, (rect.right,rect.top + size)), width)
				# bottomright
				pygame.draw.lines(self.display_surface, color, False, ((rect.right - size, rect.bottom), rect.bottomright, (rect.right,rect.bottom - size)), width)
				# bottomleft
				pygame.draw.lines(self.display_surface, color, False, ((rect.left,rect.bottom - size), rect.bottomleft, (rect.left + size,rect.bottom)), width)
				
			else:
				type_dict = {key: value['type'] for key, value in EDITOR_DATA.items()}
				surf = self.preview_surfs[self.selection_index].copy()
				surf.set_alpha(200)
				
				# tile 
				if type_dict[self.selection_index] == 'tile':
					current_cell = self.get_current_cell()
					rect = surf.get_rect(topleft = self.origin + vector(current_cell) * TILE_SIZE)
				# object 
				else:
					rect = surf.get_rect(center = mouse_pos())
				self.display_surface.blit(surf, rect)

	def display_sky(self, dt):
		self.display_surface.fill(SKY_COLOR)
		y = self.sky_handle.rect.centery

		# horizon lines
		if y > 0:	
			horizon_rect1 = pygame.Rect(0,y - 10,WINDOW_WIDTH,10)
			horizon_rect2 = pygame.Rect(0,y - 16,WINDOW_WIDTH,4)
			horizon_rect3 = pygame.Rect(0,y - 20,WINDOW_WIDTH,2)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect1)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect2)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect3)

			self.display_clouds(dt, y)

		# sea 
		if 0 < y < WINDOW_HEIGHT:
			sea_rect = pygame.Rect(0,y,WINDOW_WIDTH,WINDOW_HEIGHT)
			pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)
			pygame.draw.line(self.display_surface, HORIZON_COLOR, (0,y), (WINDOW_WIDTH,y),3)
		if y < 0:
			self.display_surface.fill(SEA_COLOR)

	def display_clouds(self, dt, horizon_y):
		for cloud in self.current_clouds: # [{surf, pos, speed}]
			cloud['pos'][0] -= cloud['speed'] * dt
			x = cloud['pos'][0]
			y = horizon_y - cloud['pos'][1]
			self.display_surface.blit(cloud['surf'], (x,y))

	def create_clouds(self, event):
		if event.type == self.cloud_timer:
			surf = choice(self.cloud_surf)
			surf = pygame.transform.scale2x(surf) if randint(0,4) < 2 else surf
		
			pos = [WINDOW_WIDTH + randint(50,100),randint(0,WINDOW_HEIGHT)]
			self.current_clouds.append({'surf': surf, 'pos': pos, 'speed': randint(20,50)})

			# remove clouds
			self.current_clouds = [cloud for cloud in self.current_clouds if cloud['pos'][0] > -400]

	def startup_clouds(self):
		for i in range(20):
			surf = pygame.transform.scale2x(choice(self.cloud_surf)) if randint(0,4) < 2 else choice(self.cloud_surf)
			pos = [randint(0, WINDOW_WIDTH),randint(0, WINDOW_HEIGHT)]
			self.current_clouds.append({'surf': surf, 'pos': pos, 'speed': randint(20,50)})

	def draw_death_line(self):
		y = self.death_cross.rect.centery
		pygame.draw.line(self.display_surface, DEATH_LINE_COLOR, (0,y), (WINDOW_WIDTH,y), DEATH_LINE_WIDTH)


	# exporting/importing
	def save(self, filename):
		with open(filename, 'wb') as file:
			pickle.dump([self.timeline[-1]].copy(), file)
			print(f'Seu mapa {filename} foi exportado com sucesso!')

	def load(self, filename):
		with open(filename, 'rb') as file:
			self.timeline = pickle.load(file).copy()

		# print(self.timeline)

		while len(self.timeline) > self.timeline_max_length:
			del self.timeline[0]

		self.timeline_index = len(self.timeline)-1

		self.editor_data_update()


	# update
	def run(self, dt):
		self.hotkeys()

		self.event_loop()

		# updating
		self.animation_update(dt)
		self.canvas_objects.update(dt)
		self.timers()

		# drawing
		self.display_surface.fill('gray')
		self.display_sky(dt)
		self.draw_death_line()
		self.draw_level()
		self.draw_tile_lines()
		# pygame.draw.circle(self.display_surface, 'red', self.origin, 5)
		self.preview()
		self.menu.display(self.selection_index)


class CanvasTile:
	def __init__(self, tile_id, offset=vector()):

		# terrain
		self.has_terrain = False
		self.terrain_neighbors = []

		# water
		self.has_water = False
		self.water_on_top = False

		# coin
		self.coin = None

		# enemy
		self.enemy = None

		# objects
		self.objects = []

		self.add_id(tile_id, offset)
		self.is_empty = False

	def add_id(self, tile_id, offset=vector()):
		options = {key: value['style'] for key, value in EDITOR_DATA.items()}
		match options[tile_id]:
			case 'terrain': self.has_terrain = True
			case 'water': self.has_water = True
			case 'coin': self.coin = tile_id
			case 'enemy': self.enemy = tile_id
			case _: # else: objects
				if (tile_id, offset) not in self.objects:
					self.objects.append((tile_id, offset))

	def remove_id(self, tile_id):
		options = {key: value['style'] for key, value in EDITOR_DATA.items()}
		match options[tile_id]:
			case 'terrain': self.has_terrain = False
			case 'water': self.has_water = False
			case 'coin': self.coin = None
			case 'enemy': self.enemy = None
		self.check_content()

	def check_content(self):
		if not self.has_terrain and not self.has_water and not self.coin and not self.enemy:
			self.is_empty = True

	def get_water(self):
		return 'bottom' if self.water_on_top else 'top'

	def get_terrain(self):
		return ''.join(self.terrain_neighbors)

	def copy(self):
		return CanvasTileCopy(self.has_terrain, self.terrain_neighbors, self.has_water, self.water_on_top,
		self.coin, self.enemy, self.objects, self.is_empty)


class CanvasObject(pygame.sprite.Sprite):
	def __init__(self, pos, frames, tile_id, origin, groups, editor):
		super().__init__(groups)

		self.editor = editor
		self.tile_id = tile_id

		self.serialized_list =\
		 self.editor.serialized_background if EDITOR_DATA[self.tile_id]['style'] == 'palm_bg'\
		 else self.editor.serialized_foreground

		# animation
		self.frames = frames
		self.frame_index = 0

		# sprite
		self.image = self.frames[int(self.frame_index)]
		self.rect = self.image.get_rect(center = pos)

		# movement
		self.distance_to_origin = vector(self.rect.topleft) - origin
		self.mouse_offset = vector()

		# dragging
		self.selected = False

	def start_drag(self):
		self.selected = True
		self.mouse_offset = vector(mouse_pos()) - vector(self.rect.topleft)

	def drag(self):
		if self.selected:
			self.rect.topleft = mouse_pos() - self.mouse_offset

	def drag_end(self, origin):
		# print(self.serialized_list)
		for serialized in self.serialized_list:
			if serialized.tile_id == self.tile_id\
			and serialized.distance_to_origin[0] == self.distance_to_origin.x\
			and serialized.distance_to_origin[1] == self.distance_to_origin.y:

				self.serialized_list.remove(serialized)
		# print(self.serialized_list)

		self.selected = False
		self.distance_to_origin = vector(self.rect.topleft) - origin
		
		# print(self.serialized_list)

		self.serialized_list.append(self.serialize())

		# print(self.serialized_list)

		self.editor.timeline_append()

	def animate(self, dt):
		self.frame_index += ANIMATION_SPEED * dt
		self.frame_index = 0 if self.frame_index >= len(self.frames) else self.frame_index
		self.image = self.frames[int(self.frame_index)]
		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

	def pan_pos(self, origin):
		self.rect.topleft = origin + self.distance_to_origin

	def update(self, dt):
		self.animate(dt)
		self.drag()

	def serialize(self):
		tile_id = self.tile_id
		frames = serialize_surfaces(self.frames.copy())
		frame_sizes = get_surface_sizes(self.frames.copy())
		frame_index = self.frame_index

		rect = self.rect.copy()
		rect = [rect.left, rect.top, rect.width, rect.height]

		distance_to_origin = self.distance_to_origin.copy()
		distance_to_origin = (distance_to_origin.x, distance_to_origin.y)
		mouse_offset = self.mouse_offset.copy()
		mouse_offset = (mouse_offset.x, mouse_offset.y)

		selected = self.selected


		return CanvasObjectSerialized(tile_id, frames, frame_sizes, frame_index, rect,
					distance_to_origin, mouse_offset, selected)


class CanvasObjectSerialized:
	def __init__(self, tile_id, frames, frame_sizes, frame_index, rect, distance_to_origin,
		mouse_offset, selected):

		# animation
		self.tile_id = tile_id
		self.frames = frames
		self.frame_sizes = frame_sizes
		self.frame_index = frame_index

		# sprite
		self.image = self.frames[int(self.frame_index)]
		self.rect = rect

		# movement
		self.distance_to_origin = distance_to_origin
		self.mouse_offset = mouse_offset

		# dragging
		self.selected = selected

	def pan_pos(self, origin_tuple):
		x, y = origin_tuple
		a, b = self.distance_to_origin

		self.rect[0] = x + a
		self.rect[1] = y + b
		

class CanvasTileCopy(CanvasTile):
	def __init__(self, has_terrain, terrain_neighbors, has_water, water_on_top,
		coin, enemy, objects, is_empty):
		# terrain
		self.has_terrain = has_terrain
		self.terrain_neighbors = terrain_neighbors

		# water
		self.has_water = has_water
		self.water_on_top = water_on_top

		# coin
		self.coin = coin

		# enemy
		self.enemy = enemy

		# objects
		self.objects = objects

		self.is_empty = is_empty
