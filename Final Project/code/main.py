import pygame
import ctypes

from sys import exit
from levels import LevelManager
from debug import FPSDisplay
from time import time as current_time

from settings import *
from support import *
from importdata import *
from times import *
from displays import *

user32 = ctypes.windll.user32


class Game:
	def __init__(self, fps=0):
		pygame.joystick.init()
		pygame.font.init()

		self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		self.window_width = self.window.get_width()
		self.window_height = self.window.get_height()

		self.monitor_width = user32.GetSystemMetrics(0)
		self.monitor_height = user32.GetSystemMetrics(1)
		
		self.fps = fps
		self.clock = pygame.time.Clock()
		self.previous_time = current_time()

		self.joysticks = []

		self.import_graphics()

		self.level_manager = LevelManager(self.graphics)
		self.fps_display = FPSDisplay(
			'../fonts/ThaleahFat.ttf',40,{'topright':(self.window_width,0)},7,0.25)

		self.cooldowns = {}
		self.cooldowns['joystick (des)connection'] = Cooldown(500)

		self.joyconnection = None
		self.create_controller_messages()

	def create_controller_messages(self):
		scale = self.window_width / self.monitor_width

		self.controller_messages = FadeSurface(self.window,
			relative_scaled_surfaces(self.graphics['controller'],scale,scale),
			{'bottomright': (self.window_width-10, self.window_height-10)}, 100)

	def import_graphics(self):
		self.graphics = {}

		for key, path in SUBFOLDER_GRAPHICS.items():
			self.graphics[key] = get_animations_from_folder_with_subfolders(
				path,True,{'n':'right','h':'left'})

		for key, path in FOLDER_GRAPHICS.items():
			self.graphics[key] = get_surfaces_from_folder(path)

		# print(self.graphics)


	def connect_disconnect_joysticks(self):
		connected_joysticks = pygame.joystick.get_count()
		if len(self.joysticks) != connected_joysticks:

			self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

			self.show_joystick_info()

			self.subscribe_new_joysticks_control_config()

			self.get_controls_config()

			self.level_manager.connect_disconnect_joysticks(self.joysticks, self.controls_config)

	def subscribe_new_joysticks_control_config(self):
		path = CONFIG_FOLDER_PATH+'/'+CONFIG_FILENAMES['player controls']

		for joystick in self.joysticks:
			guid = joystick.get_guid()
			if guid not in read_json_file(path).keys():
				self.save_control_config(guid, DEFAULT_CONTROL_CONFIG)

	def save_control_config(self, guid, config):
		data = {guid: config}

		append_json_file(CONFIG_FOLDER_PATH, 'playercontrols', data)

	def get_controls_config(self):
		self.controls_config = read_json_file(CONFIG_FOLDER_PATH+'/'+CONFIG_FILENAMES['player controls'])

	def show_joystick_info(self):
		pass
		# for joystick in self.joysticks:
		# 	infodict = {'GUID': joystick.get_guid()}

		# 	print('='*100)
		# 	print(f'{joystick.get_name():^100}')
		# 	print('='*100)

		# 	print('-'*100)
		# 	for key, value in infodict.items():
		# 		print(f'{key}: {value}')
		# 	print('-'*100)


	def get_deltatime(self):
		dt = current_time() - self.previous_time

		self.previous_time = current_time()

		return dt

	def event_loop(self):
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			elif event.type == pygame.JOYDEVICEADDED:
				self.joyconnection = 1
				self.cooldowns['joystick (des)connection'].start()
			elif event.type == pygame.JOYDEVICEREMOVED:
				self.joyconnection = 0
				self.cooldowns['joystick (des)connection'].start()

			# elif event.type == pygame.ACTIVEEVENT:
			# 	if event.gain == 1:
			# 		print('Gain Focus')
			# 	elif event.gain == 0:
			# 		print('Lose Focus')
			# elif event.type == pygame.WINDOWMOVED:
			# 	print('WINDOWMOVED')
			# elif event.type == pygame.VIDEORESIZE:
			#  	print('VIDEORESIZE')

	def update_cooldowns(self):
		for cooldown_dict in self.cooldowns.values():
			if isinstance(cooldown_dict, dict):
				for cooldown in cooldown_dict.values():
					cooldown.update()
			else:
				cooldown_dict.update()

	def show_messages(self, dt):
		if self.joyconnection != None:
			if self.controller_messages.ended:
				self.controller_messages.reset()
				self.joyconnection = None
			else:
				self.controller_messages.update(dt)
				self.controller_messages.display(self.joyconnection, False)

	def run(self):
		while True:
			self.update_cooldowns()

			self.clock.tick(self.fps)
			dt = self.get_deltatime()

			self.event_loop()
			
			self.connect_disconnect_joysticks()

			if not self.cooldowns['joystick (des)connection'].on:
				self.level_manager.run(dt)
			else:
				self.level_manager.current_level.draw()
			
			self.show_messages(dt)

			self.fps_display.run(dt)

			pygame.display.update()


if __name__ == '__main__':
	game = Game(fps=60)
	game.run()
