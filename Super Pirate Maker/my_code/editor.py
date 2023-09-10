import pygame, sys 
from settings import *
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_buttons
from pygame.mouse import get_pos as mouse_pos
from random import choice, randint
from menu import Menu
from timer import Timer
from support import *

class Editor:
	def __init__(self, land_tiles, water_bottom, animations, sky_handle_surface, previews, cloud_surfaces):

		# main setup 
		self.display_surface = pygame.display.get_surface()
		self.canvas_data = {}

		# imports
		self.land_tiles = land_tiles
		self.water_bottom = water_bottom
		self.animations = animations
		self.sky_handle_surface = sky_handle_surface
		self.preview_surfaces = previews
		self.cloud_surfaces = cloud_surfaces

		# clouds
		self.current_clouds = []
		self.cloud_generate_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.cloud_generate_timer, 2000)
		self.create_clouds(startup=True)

		# navigation
		self.screen_middle = (self.display_surface.get_width()//2,
			self.display_surface.get_height()//2)
		self.origin = vector()
		self.pan_active = False
		self.pan_offset = vector()

		self.scrolling_speed = 16

		# grid
		self.grid_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
		self.grid_surface.set_colorkey((0,255,0)) # gets rid of this green color
		self.grid_surface.set_alpha(100)

		# selection
		self.selection_index = EDITOR_DATA_SELECTABLES_START_INDEX

		# menu
		self.menu = Menu()

		# timeline
		self.general_state_timeline = []
		self.general_deleteds_timeline = []

		# hotkeys
		self.hotkeys_data = {
		'control-z': 
			{'presstime': 0,
			'current cooldown': 200,
			'start cooldown': 200,
			'speed': 1, 
			'keys': [pygame.K_LCTRL, pygame.K_z],
			'function': self.control_z},

		 'control-y':
		 	{'presstime': 0,
			'current cooldown': 200,
			'start cooldown': 200,
			'speed': 1, 
			'keys': [pygame.K_LCTRL, pygame.K_y],
			'function': self.control_y}}

		# objects
		self.canvas_objects = pygame.sprite.Group()
		self.object_drag_active = False
		self.object_timer = Timer(30)

		# player
		CanvasObject(
			pos=(200, WINDOW_HEIGHT/2),
			frames=self.animations[0]['frames'],
			tile_id=0,
			origin=self.origin,
			group=self.canvas_objects)
		
		# sky
		self.sky_handle = CanvasObject(
			pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2),
			frames=[self.sky_handle_surface],
			tile_id=1,
			origin=self.origin,
			group=self.canvas_objects)

	# support
	def get_current_cell(self, obj=None):
		vector_from_origin = vector(mouse_pos()) - self.origin if not obj\
		 else vector(obj.distance_to_origin) - self.origin

		if vector_from_origin.x > 0:
			col = int(vector_from_origin.x / TILE_SIZE)
		else:
			col = int(vector_from_origin.x / TILE_SIZE) - 1

		if vector_from_origin.y > 0:
			row = int(vector_from_origin.y / TILE_SIZE)
		else:
			row = int(vector_from_origin.y / TILE_SIZE) - 1

		return col, row

	def check_neighbors(self, cell):
		# create a local cluster
		cell_row, cell_col = cell
		cluster_size = 3
		local_cluster = [
			(cell_row+row-int(cluster_size/2), cell_col+col-int(cluster_size/2))
			for col in range(cluster_size)
			for row in range(cluster_size)]

		# check neighbors
		for cell in local_cluster:
			if cell in self.canvas_data:

				self.canvas_data[cell].terrain_neighbors = []
				self.canvas_data[cell].water_on_top = False

				for name, side in NEIGHBOR_DIRECTIONS.items():
					neighbor_cell = (cell[0]+side[0],cell[1]+side[1])

					if neighbor_cell in self.canvas_data:
						# water
						if self.canvas_data[neighbor_cell].has_water and name == 'A':
							self.canvas_data[cell].water_on_top = True

						# terrain
						if self.canvas_data[neighbor_cell].has_terrain:
							self.canvas_data[cell].terrain_neighbors.append(name)

	def mouse_on_object(self):
		for sprite in reversed(self.canvas_objects.sprites()):
			if sprite.rect.collidepoint(mouse_pos()):
				return sprite

	def create_grid(self):
		# adding objects to the tile system

		# reseting tile objects
		for tile in self.canvas_data.values():
			tile.objects = []

		for obj in self.canvas_objects:
			current_cell = self.get_current_cell(obj)
			offset = vector(obj.distance_to_origin) - vector(current_cell) * TILE_SIZE

			if current_cell in self.canvas_data: # tile exist in this cell
				self.canvas_data[current_cell].add_id(obj.tile_id, offset)
			else: # tile doesn't exist in this cell
				self.canvas_data[current_cell] = CanvasTile(
					obj.tile_id, self.general_state_timeline, self.general_deleteds_timeline, offset)

		# creating grid
		# empty grid
		layers = {
			'water': {},
			'bg palms': {},
			'terrain': {},
			'enemies': {},
			'coins': {},
			'fg objects': {}}

		# we only need the area that have tiles, for this we need the most top and left tile
		left = sorted(self.canvas_data.keys(), key=lambda tile: tile[0])[0][0]
		top = sorted(self.canvas_data.keys(), key=lambda tile: tile[1])[0][1]

		# filling the grid
		for tile_pos, tile in self.canvas_data.items():
			row_adjusted = tile_pos[1] - top
			col_adjusted = tile_pos[0] - left
			x = col_adjusted * TILE_SIZE
			y = row_adjusted * TILE_SIZE

			if tile.has_water:
				layers['water'][(x,y)] = tile.get_water()

			if tile.has_terrain:
				layers['terrain'][(x,y)] = tile.get_terrain()\
				if tile.get_terrain() in self.land_tiles else 'X'

			if tile.coin:
				layers['coins'][(x+TILE_SIZE//2,y+TILE_SIZE//2)] = tile.coin

			if tile.enemy:
				layers['enemies'][(x,y)] = tile.enemy

			if tile.objects:
				palm_bg_ids = [key for key, value in EDITOR_DATA.items() if value['style'] == 'palm_bg']
				for obj_id, offset in tile.objects:
					if obj_id in palm_bg_ids:
						layers['bg palms'][(int(x+offset.x),int(y+offset.y))] = obj
					else:
						layers['fg objects'][(int(x+offset.x),int(y+offset.y))] = obj

		return layers

	# input
	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
				print(self.create_grid())

			if event.type == self.cloud_generate_timer:
				self.create_clouds()

			self.pan_input(event)
			self.selection_hotkeys(event)
			self.menu_click(event)

			self.object_drag(event)

			if not self.menu.rect.collidepoint(mouse_pos()):
				if not self.object_drag_active:
					self.canvas_update()

	def hotkeys(self):
		keys = pygame.key.get_pressed()

		for hotkey, data in self.hotkeys_data.items():
			if all_true(keys, data['keys']):
				if self.hotkeys_cooldown(data):
					data['function']()
					self.hotkeys_data[hotkey]['presstime'] =\
					 pygame.time.get_ticks()

				self.increase_hotkey_speed(hotkey)

			else:
				self.hotkeys_data[hotkey]['current cooldown'] = data['start cooldown']

	def increase_hotkey_speed(self, hotkey):
		speed = self.hotkeys_data[hotkey]['speed']
		self.hotkeys_data[hotkey]['current cooldown'] -= speed
		self.hotkeys_data[hotkey]['current cooldown'] = max(
			0,self.hotkeys_data[hotkey]['current cooldown'])

	def hotkeys_cooldown(self, data):
		current_time = pygame.time.get_ticks()
		hotkey_time = data['presstime']
		hotkey_cooldown = data['current cooldown']

		return current_time - hotkey_time > hotkey_cooldown

	def control_z(self):
		if self.canvas_data and self.general_state_timeline:
			current_cell = reverse_dict(self.canvas_data)\
				[self.general_state_timeline[-1]]
	
			self.canvas_remove(current_cell)
			del self.general_state_timeline[-1]

	def control_y(self):
		if self.general_deleteds_timeline:
			if isinstance(self.general_deleteds_timeline[-1][0], tuple): 
			# if first tuple element is a cell
				cell, tile = self.general_deleteds_timeline.pop()
				self.canvas_data[cell] = tile
				self.general_state_timeline.append(tile)
				self.check_neighbors(cell)
			else:
				tile, timeline_state = self.general_deleteds_timeline.pop()
				tile.state_timeline.append(timeline_state)
				tile.update()
				
	def pan_input(self, event):
		# middle mouse button pressed / released
		if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[1]:
			self.pan_active = True
			self.pan_offset = vector(mouse_pos()) - self.origin
		elif not mouse_buttons()[1]:
			self.pan_active = False

		# mouse wheel
		if event.type == pygame.MOUSEWHEEL:
			movement_value = event.y * self.scrolling_speed
			if pygame.key.get_pressed()[pygame.K_LSHIFT]:
				self.origin.x += movement_value
			else:
				self.origin.y += movement_value

			self.wheel_movement = True
		else:
			self.wheel_movement = False

		# panning update
		if self.pan_active:
			self.origin = vector(mouse_pos()) - self.pan_offset

		if self.pan_active or self.wheel_movement:
			for sprite in self.canvas_objects:
				sprite.pan_pos(self.origin)

	def selection_hotkeys(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RIGHT:
				self.selection_index += 1
			if event.key == pygame.K_LEFT:
				self.selection_index -= 1

		self.selection_index = num_loop(self.selection_index,
			EDITOR_DATA_SELECTABLES_START_INDEX,
			EDITOR_DATA_SELECTABLES_END_INDEX)

	def menu_click(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.menu.rect.collidepoint(mouse_pos()):
				selection_index = self.menu.click(mouse_pos(),mouse_buttons())
				self.selection_index = self.selection_index if selection_index == None\
				 else selection_index

	def object_drag(self, event):
		sprite = self.mouse_on_object()
		if sprite:
			if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
				sprite.start_drag()
				self.object_drag_active = True
			if event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
				sprite.end_drag(self.origin)
				self.object_drag_active = False

		# object
		selected_object = self.mouse_on_object()

	# update
	def canvas_update(self):
		current_cell = self.get_current_cell()

		# add
		if mouse_buttons()[0]:
			if current_cell in self.canvas_data:
				if self.canvas_data[current_cell].state_timeline:
					if self.canvas_data[current_cell].add_id(self.selection_index,True)\
					 != self.canvas_data[current_cell].state_timeline[-1]:
						
						self.canvas_add(current_cell)

			else:
				self.canvas_add(current_cell)

		# del
		if mouse_buttons()[2]:
			self.canvas_remove(current_cell)

	def canvas_add(self, current_cell):
		if EDITOR_DATA[self.selection_index]['type'] == 'tile':
			if current_cell in self.canvas_data:
				self.canvas_data[current_cell].add_id(self.selection_index)
			else:
				self.canvas_data[current_cell] = CanvasTile(self.selection_index,
					self.general_state_timeline, self.general_deleteds_timeline)

			self.check_neighbors(current_cell)
		else:
			if not self.object_timer.active:
				CanvasObject(
					pos=mouse_pos(),
					frames=self.animations[self.selection_index]['frames'],
					tile_id=self.selection_index,
					origin=self.origin,
					group=self.canvas_objects)

				self.object_timer.activate()

	def canvas_remove(self, current_cell):
		selected_object = self.mouse_on_object()
		if selected_object:
			if EDITOR_DATA[selected_object.tile_id]['style'] not in ['player', 'sky']:
				selected_object.kill()

		# tile
		if current_cell in self.canvas_data:
			if len(self.canvas_data[current_cell].state_timeline) > 1:
				self.canvas_data[current_cell].recall('backward')
			else:
				self.general_deleteds_timeline.append(
					(current_cell, self.canvas_data[current_cell]))
				del self.canvas_data[current_cell]

			self.check_neighbors(current_cell)

	# drawing
	def draw_grid(self):
		cols = WINDOW_WIDTH // TILE_SIZE
		rows = WINDOW_HEIGHT // TILE_SIZE

		origin_offset = vector(
			x=self.origin.x - self.origin.x//TILE_SIZE * TILE_SIZE,
			y=self.origin.y - self.origin.y//TILE_SIZE * TILE_SIZE)

		self.grid_surface.fill('green')

		for col in range(cols+1):
			x = origin_offset.x + col * TILE_SIZE
			pygame.draw.line(self.grid_surface, LINE_COLOR,
				(x,0), (x,WINDOW_HEIGHT), GRID_LINE_WIDTH)

		for row in range(rows+1):
			y = origin_offset.y + row * TILE_SIZE
			pygame.draw.line(self.grid_surface, LINE_COLOR,
				(0,y), (WINDOW_WIDTH,y), GRID_LINE_WIDTH)

		self.display_surface.blit(self.grid_surface, (0,0))

		# DEBUG
		return origin_offset

	def draw_level(self):
		for cell, tile in self.canvas_data.items():
			cell_topleft = (self.origin + vector(cell) * TILE_SIZE)
			cell_center = cell_topleft + vector(TILE_SIZE/2,TILE_SIZE/2)
			cell_midbottom = cell_center + vector(0,TILE_SIZE/2)
			
			# terrain
			if tile.has_terrain:
				tile_string = ''.join(tile.terrain_neighbors)
				tile_style = tile_string if tile_string in self.land_tiles else 'X'

				surf = self.land_tiles[tile_style]

				self.display_surface.blit(surf, cell_topleft)

			# water
			if tile.has_water:
				if tile.water_on_top:
					surf = self.water_bottom 
				else:
					animation_data = self.animations[3]
					frames = animation_data['frames']
					index = int(animation_data['frame index'])

					surf = frames[index]

				self.display_surface.blit(surf, cell_topleft)

			# coin
			if tile.coin:
				animation_data = self.animations[tile.coin]
				frames = animation_data['frames']
				index = int(animation_data['frame index'])

				surf = frames[index]
				rect = surf.get_rect(center=cell_center)

				self.display_surface.blit(surf, rect)

			# enemy
			if tile.enemy:
				animation_data = self.animations[tile.enemy]
				frames = animation_data['frames']
				index = int(animation_data['frame index'])

				surf = frames[index]
				rect = surf.get_rect(midbottom=cell_midbottom)
				
				self.display_surface.blit(surf, rect)

		self.canvas_objects.draw(self.display_surface)

	def preview(self):
		if not self.menu.rect.collidepoint(mouse_pos()):
			selected_object = self.mouse_on_object()

			if selected_object:
				# draw a indicator around the object
				rect = selected_object.rect.inflate(10,10)
				color = 'black'
				width = 3
				size = 15
				rect_data = (
					[rect.topleft, (1,1)],
				 	[rect.topright, (1,-1)],
				 	[rect.bottomleft, (-1,1)], 
				 	[rect.bottomright, (-1,-1)])

				for vertex, direction in rect_data:
					points = [(vertex[0],vertex[1]+(size*direction[0])),
					           vertex,
					          (vertex[0]+(size*direction[1]),vertex[1])]

					pygame.draw.lines(self.display_surface, color, False, points, width)
			else:
				# draw the preview
				type_dict = {key: value['type'] for key, value in EDITOR_DATA.items()}
				surf = self.preview_surfaces[self.selection_index].copy()
				surf.set_alpha(150)

				# tile
				if type_dict[self.selection_index] == 'tile':
					current_cell = self.get_current_cell()
					rect = surf.get_rect(topleft=self.origin+vector(current_cell)*TILE_SIZE)

				# object
				elif type_dict[self.selection_index] == 'object':
					rect = surf.get_rect(center=mouse_pos())

				self.display_surface.blit(surf, rect)

	def display_sky(self, dt):
		self.display_surface.fill(SKY_COLOR)
		y = self.sky_handle.rect.centery

		# horizon line
		if 0 < y < WINDOW_HEIGHT+20:
			horizon_rects = []
			for y_offset, height in [(10,10),(16,4),(20,2)]:
				horizon_rects.append(pygame.Rect(0,y-y_offset,WINDOW_WIDTH,height))
			
			for rect in horizon_rects:
				pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, rect)

		# clouds
		if y > 0:
			self.display_clouds(dt, y)

		# sea
		sea_rect = pygame.Rect(0,max(0,y),WINDOW_WIDTH,WINDOW_HEIGHT)
		pygame.draw.rect(self.display_surface,SEA_COLOR,sea_rect)

		pygame.draw.line(self.display_surface,HORIZON_COLOR,(0,y),(WINDOW_WIDTH,y),3)

	def display_clouds(self, dt, horizon_y):
		for cloud in self.current_clouds:
			cloud['pos'][0] -= cloud['speed'] * dt
			x = cloud['pos'][0]
			y = horizon_y-cloud['pos'][1]
			self.display_surface.blit(cloud['surf'], (x,y))

	def create_clouds(self, startup=False):
		
		loops = 12 if startup else 1 
		
		for i in range(loops):
			surf = choice(self.cloud_surfaces)
			surf = pygame.transform.scale2x(surf) if randint(0,1) == 0 else surf

			x = randint(0,WINDOW_WIDTH) if startup else WINDOW_WIDTH+randint(50,100)
			y = randint(0,WINDOW_HEIGHT/1.5) if startup else randint(0,WINDOW_HEIGHT)
			pos = [x, y]

			speed = randint(20,70)

			self.current_clouds.append({'surf': surf, 'pos': pos, 'speed': speed})

		self.remove_clouds()

	def remove_clouds(self):
		self.current_clouds = [cloud for cloud in self.current_clouds
		if cloud['pos'][0]+cloud['surf'].get_width() > 0]

	# update
	def animate(self, dt):
		for animation_data in self.animations.values():
			index = animation_data['frame index']
			length = animation_data['length']

			# speed = animation_data['speed']
			speed = ANIMATION_SPEED

			index += speed * dt
			animation_data['frame index'] = num_loop(index,0,length-1)

	def run(self, dt):
		# checking input
		self.event_loop()
		# self.hotkeys()

		# updating
		self.animate(dt)
		self.canvas_objects.update(dt)
		self.object_timer.update()

		# drawing
		self.display_sky(dt)
		self.draw_level()
		self.draw_grid()
		self.preview()
		self.menu.display(self.selection_index)

		self.debug('point')

	def debug(self, flag='all'):
		match flag:
			case 'point':
				pygame.draw.circle(self.display_surface, 'red', self.origin, 10)

			case 'grid':
				# grid generation algorithymn
				origin_offset = self.draw_grid()
				origin_offset.y = self.screen_middle[1]
				pygame.draw.line(self.display_surface, 'purple', (0,self.screen_middle[1]),
					origin_offset, 10)

			case 'all':
				pygame.draw.circle(self.display_surface, 'red', self.origin, 10)
				# origin
				pygame.draw.line(self.display_surface, 'green', (0,0), self.origin, 4)
				# mouse pos
				pygame.draw.line(self.display_surface, 'blue', (0,0), vector(mouse_pos()), 4)
				# origin to mouse pos = offset
				pygame.draw.line(self.display_surface, 'orange', self.origin, vector(mouse_pos()), 4)
				pygame.draw.line(self.display_surface, 'orange', (0,0), self.pan_offset, 4)

				pygame.draw.line(self.display_surface, 'green', self.pan_offset, vector(mouse_pos()), 4)

				# grid generation algorithymn
				origin_offset = self.draw_grid()
				origin_offset.y = self.screen_middle[1]
				pygame.draw.line(self.display_surface, 'purple', (0,self.screen_middle[1]),
					origin_offset, 10)


class CanvasTile:
	def __init__(self, tile_id, general_state_timeline, general_deleteds_timeline, offset=vector()):

		# timeline
		self.general_state_timeline = general_state_timeline
		self.general_deleteds_timeline = general_deleteds_timeline

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

		self.options = {key: value['style'] for key, value in EDITOR_DATA.items()}

		self.state_timeline = []
		self.deleteds_timeline = []

		self.add_id(tile_id, offset=offset)

	def recall(self, direction):
		match direction:
			case 'backward':
				self.general_deleteds_timeline.append((self, self.state_timeline.pop()))
				
		self.update()

	def get_water(self):
		return 'bottom' if self.water_on_top else 'top'

	def get_terrain(self):
		return ''.join(self.terrain_neighbors)

	def add_id(self, tile_id, offset=vector(), silmulation=False):
		style = self.options[tile_id]

		has_terrain = self.has_terrain
		has_water = self.has_water
		coin = self.coin
		enemy = self.enemy

		match style:
			case 'terrain':
				has_terrain = True
			case 'water':
				has_water = True
			case 'coin':
				coin = tile_id
			case 'enemy': 
				enemy = tile_id
			case _:
				if (tile_id, offset) not in self.objects:
					self.objects.append((tile_id, offset))

		if not silmulation:
			self.state_timeline.append({'has_terrain': has_terrain,
				'has_water': has_water, 'coin': coin, 'enemy': enemy})

			self.general_state_timeline.append(self)

			self.update()
		else:
			return {'has_terrain': has_terrain, 'has_water': has_water,
			'coin': coin, 'enemy': enemy}

	def update(self):
		for name, value in self.state_timeline[-1].items():
			setattr(self, name, value)


class CanvasObject(pygame.sprite.Sprite):
	def __init__(self, pos, frames, tile_id, origin, group):
		super().__init__(group)

		self.tile_id = tile_id

		# animations
		self.frames = frames
		self.frame_index = 0
		self.animation_length = len(self.frames)
		self.animation_speed = ANIMATION_SPEED
		# speed = animation_data['speed']

		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center=pos) 

		# movement
		self.distance_to_origin = vector(self.rect.topleft) - origin
		self.selected = False
		self.mouse_offset = vector()

	def pan_pos(self, origin):
		self.rect.topleft = origin + self.distance_to_origin

	def start_drag(self):
		self.selected = True
		self.mouse_offset = vector(mouse_pos()) - vector(self.rect.topleft)

	def end_drag(self, origin):
		self.selected = False
		self.distance_to_origin = vector(self.rect.topleft) - origin

	def drag(self):
		self.rect.topleft = vector(mouse_pos()) - self.mouse_offset

	def animate(self, dt):		
		self.frame_index += self.animation_speed * dt
		self.frame_index = num_loop(self.frame_index,0,self.animation_length-1)
		self.image = self.frames[int(self.frame_index)]
		self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

	def update(self, dt):
		self.animate(dt)
		if self.selected:
			self.drag()
