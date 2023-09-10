import pygame, sys, support
from time import time
from os import walk

from camera import Camera
from level import Level
from menu import Menu

from settings import *
from UI import *
from filters import *
from texts import *
##########################################################################################
'''RODA DE STAMINA & EXTRA HEARTS/GOLDEN HEARTS'''
##########################################################################################


class Game:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		self.window_width = self.display_surface.get_width()
		self.window_height = self.display_surface.get_height()

		self.prev_time = time()
		self.clock = pygame.time.Clock()

		# joysticks
		self.joysticks = []
		self.get_joysticks()

		# groups
		self.collision_sprites = pygame.sprite.Group()
		self.camera = Camera()
		self.damage_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()
		self.monster_sprites = pygame.sprite.Group()
		self.hearts_group = pygame.sprite.Group()

		# graphics
		self.spritesheets = {}
		self.graphics = {}
		self.import_graphics()

		# game states
		self.state = 'menu'
		self.menu = Menu(self.graphics,
			self.switch)
		self.level = Level(self.graphics, self.camera, self.collision_sprites, self.damage_sprites,
			self.attackable_sprites, self.monster_sprites, self.hearts_group)

		# game over
		self.death_fade_filter = AlphaFadeFilter(
			display_surface=self.display_surface,
			color=DEATH_FADE_FILTER_COLOR,
			rect=pygame.Rect(0,0,WINDOW_WIDTH,WINDOW_HEIGHT),
			speed=70,
			direction=1)

		self.game_over_text = AlphaFadeText(
			display_surface=self.display_surface,
			color=GAMEOVER_FADE_TEXT_COLOR,
			speed=70,
			direction=1,
			font=pygame.font.Font('../fonts/Montaga-Regular.ttf', GAME_OVER_FONT_SIZE),
			text='GAME OVER',
			AA=True,
			pos={'center': (WINDOW_WIDTH//2,WINDOW_HEIGHT//2)}
			)

	# graphics imports
	def import_graphics(self):
		self.import_spritesheets()
		self.extract_subsurfaces_from_spritesheets()
		self.slice_animations()
		self.get_left_animations()


		# menu bg
		self.graphics['menu'] = {}

		self.graphics['menu']['background'] = {
			'bg': pygame.image.load('../graphics/menu/bg.png').convert_alpha(),
			'fg': pygame.image.load('../graphics/menu/fg.png').convert_alpha()}

		# menu buttons
		self.graphics['menu']['buttons'] = {
			'main': pygame.image.load('../graphics/UI/flat_button_main.png').convert_alpha(),
			'hover': pygame.image.load('../graphics/UI/flat_button_hover.png').convert_alpha(),
			'press': pygame.image.load('../graphics/UI/flat_button_press.png').convert_alpha()}

		# menu logo
		self.graphics['menu']['logo'] = pygame.image.load('../graphics/menu/transparent_logo.png').convert_alpha()

	def import_spritesheets(self):
		for spritesheet_key, path, sprite_dimensions, superkey, animations_key, scale_value, erase_empty, source in SPRITESHEET_IMPORT_DATA:
			match source:
				case 'image':
					self.spritesheets[spritesheet_key] =\
					 (pygame.image.load(path).convert_alpha(),
				 	 sprite_dimensions[0],
				 	 sprite_dimensions[1],
				 	 superkey,
				 	 animations_key,
				 	 scale_value,
				 	 erase_empty)

				case 'folder':
					for file_name in list(walk(path))[0][2]:
						animation_key = file_name.strip().split('.')[0].lower()

						value =\
						 (pygame.image.load(path+'/'+file_name).convert_alpha(),
						 sprite_dimensions[0],
						 sprite_dimensions[1],
						 superkey,
						 animation_key,
						 scale_value,
						 erase_empty)

						if spritesheet_key in self.spritesheets.keys():
							self.spritesheets[spritesheet_key][animation_key] = value
						else:
							self.spritesheets[spritesheet_key] =\
							 {animation_key: value}

	def extract_subsurfaces_from_spritesheets(self):
		for spritesheets_data in self.spritesheets.values():
			if isinstance(spritesheets_data, tuple): # image
				spritesheets_data = [spritesheets_data]
			elif isinstance(spritesheets_data, dict): # folder
				spritesheets_data = list(spritesheets_data.values())

			for surface, width, height, superkey, key, scale, erase_empty in spritesheets_data:
				frames = []
				full_width = surface.get_width()
				full_height = surface.get_height()

				for y in range(0,full_height,height):
					for x in range(0,full_width,width):

						rect = pygame.Rect(x,y,width,height)

						# get subsurface/frame
						if (full_width - x) / width >= 1 and (full_height - y) / height >= 1:
							frame = surface.subsurface(rect)
						else:
							frame = None

						# append subsurface/frame
						if frame:

							# transform frame
							if scale:
								frame = pygame.transform.scale(frame, (width*scale, height*scale))
							else:
								pass

							if erase_empty:
								if not support.is_surface_empty(frame):
									frames.append(frame)
							else:
								frames.append(frame)

				if key:
					if superkey in self.graphics.keys():
						self.graphics[superkey][key] = frames
					else:
						self.graphics[superkey] = {key: frames}
				else:
					if superkey in self.graphics.keys():
						self.graphics[superkey] += frames
					else:
						self.graphics[superkey] = frames

	def slice_animations(self):
		for superkey, data in ANIMATION_SLICE_INFO.items():

			dictionary = {}
			frames = self.graphics[superkey].copy()

			for animation_state, from_to in data.items():
				dictionary[animation_state] = frames[from_to[0]:from_to[1]+1]

			self.graphics[superkey] = dictionary

	def get_left_animations(self):
		for superkey, animations in self.graphics.items():

			if superkey in ('player', 'fire worm', 'fire ball', 'melee attack hitboxes'):
				self.graphics[superkey] = {'right': animations}
				left_animations = {}

				for key, animation in animations.items():
					left_animations[key] = [pygame.transform.flip(frame,True,False) for frame in animation]
					
				self.graphics[superkey]['left'] = left_animations


	# joystick
	def get_joysticks(self):
		for n in range(pygame.joystick.get_count()):
			self.joysticks.append(pygame.joystick.Joystick(n))

	def print_joystick_info(self):
		for i, joystick in enumerate(self.joysticks):
			print('='*100)
			print(f'{f"JOYSTICK {joystick.get_instance_id()}":^100}')
			print('='*100)

			print(f'LIST INDEX: {i}')
			print(f'NAME: {joystick.get_name()}')
			print(f'GUID: {joystick.get_guid()}')
			print(f'NUMAXES: {joystick.get_numaxes()}')
			print(f'NUMBALLS: {joystick.get_numballs()}')
			print(f'NUMBUTTONS: {joystick.get_numbuttons()}')
			print(f'NUMHATS: {joystick.get_numhats()}')

			print('='*100)

	def check_joysticks(self):
		if pygame.joystick.get_count() > 0:
			if not self.level.player.joystick:

				self.joysticks = [pygame.joystick.Joystick(0)]
				print(f'Joystick {self.joysticks[0].get_instance_id()} was conneted!')
				self.print_joystick_info()

				self.connect_joysticks()
				
		else:
			if self.level.player.joystick:

				print(f'Joystick {self.joysticks[0].get_instance_id()} was disconneted!')
				self.joysticks = []

				self.disconnect_joysticks()

	def connect_joysticks(self):
		self.level.player.joystick = self.joysticks[0]

		if not self.menu.joystick:
			self.menu.joystick = self.joysticks[0]

	def disconnect_joysticks(self):
		self.level.player.joystick = None
		if self.menu.joystick:
			self.menu.joystick = None


	# core
	def switch(self, state):
		self.state = state

	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

	def get_deltatime(self):
		dt = time() - self.prev_time
		self.prev_time = time()

		return dt

	def update(self, dt):
		self.check_joysticks()

		match self.state:
			case 'menu':
				self.menu.update(dt)
			case 'level':
				self.level.update(dt)

	def draw(self, dt):
		match self.state:
			case 'menu':
				self.menu.draw()
			case 'level':
				self.level.draw(dt)

				if self.level.player.deathing and self.level.player.on_floor:
					self.death_fade_filter.apply(dt)

					if self.death_fade_filter.alpha >= self.death_fade_filter.end_alpha:
						self.game_over_text.apply(dt)


	def run(self):
		while True:
			self.clock.tick(60)
			dt = self.get_deltatime()

			self.event_loop()

			self.update(dt)
			self.draw(dt)

			pygame.display.update()


if __name__ == '__main__':
	game = Game()
	game.run()
