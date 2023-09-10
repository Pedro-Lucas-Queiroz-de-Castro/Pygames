'''
X - Control-z e Control-y | ... | check_neighbors, save&load integration...
X - Water Physics with Dynamic sound and proper animations | V
X - Save and Load | ...
X - Game Over
'''

import pygame, sys
from settings import *
from support import *

from pygame.math import Vector2 as vector
from pygame.image import load

from editor import Editor
from level import Level

from sprites import Player
from transition import Transition

from gameover import *

class Main:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		self.clock = pygame.time.Clock()
		self.import_assets()

		self.game_over = False
		self.editor_active = True

		# Transitions
		self.transition = Transition(self.toggle)
		self.game_over_transition = Transition(self.game_over_escape)
		self.victory_transition = Transition(self.victory_escape)

		# State Classes
		self.editor = Editor(self.land_tiles, self.switch)
		self.victory_screen = VictoryScreen(self.victory_transition)
		self.fall_death_screen = GameDefeatScreen(self.game_over_transition, FALL_DEATH_START_TEXT_COLOR, animation_speed=1.003)
		self.damage_death_screen = GameDefeatScreen(self.game_over_transition, DAMAGE_DEATH_START_TEXT_COLOR, animation_speed=1.003)

		# cursor 
		surf = load('../graphics/cursors/mouse.png').convert_alpha()
		cursor = pygame.cursors.Cursor((0,0), surf)
		pygame.mouse.set_cursor(cursor)

		# musics
		self.editor_music = pygame.mixer.Sound('../audio/Explorer.ogg')
		self.editor_music.set_volume(0.5)

		self.editor_music.play(loops=-1)

		self.import_sounds()

	def import_sounds(self):
		coin = pygame.mixer.Sound('../audio/coin.wav')
		coin.set_volume(0.2)
		setattr(Level, 'coin_sound', coin)

		hit = pygame.mixer.Sound('../audio/hit.wav')
		hit.set_volume(0.4)
		setattr(Level, 'hit_sound', hit)

		jump = pygame.mixer.Sound('../audio/jump.wav')
		jump.set_volume(0.4)
		setattr(Player, 'jump_sound', jump)

	def import_assets(self):
		# terrain
		self.land_tiles = import_folder_dict('../graphics/terrain/land')
		water_bottom = load(
			'../graphics/terrain/water/water_bottom.png').convert_alpha()
		water_top_animation = import_folder('../graphics/terrain/water/animation')

		# coins
		gold = import_folder('../graphics/items/gold')
		silver = import_folder('../graphics/items/silver')
		diamond = import_folder('../graphics/items/diamond')
		particle = import_folder('../graphics/items/particle')

		# palms
		palms_animations = import_folder_animation('../graphics/terrain/palm')

		# enemies
		shell_left = import_folder_animation('../graphics/enemies/shell_left')
		spikes = import_folder('../graphics/enemies/spikes')[0]
		tooth = import_folder_animation('../graphics/enemies/tooth')

		pearl = load('../graphics/enemies/pearl/pearl.png').convert_alpha()

		# player
		player_animations = import_folder_animation('../graphics/player')
		player_animations['swim_left'] = flipped_assets(
			player_animations['swim_right'],True,False)

		# clouds
		clouds = import_folder('../graphics/clouds')

		# flag
		flag = import_folder('../graphics/flag')

		# # death
		# death_line = load('../graphics/death/death_line.png').convert_alpha()

		# HUD
		heart_container = load('../graphics/HUD/heart_container.png').convert_alpha()
		heart_container = pygame.transform.scale2x(heart_container)

		self.assets_dict = {
				'land': self.land_tiles,
				'water': {'top':water_top_animation, 'bottom':water_bottom},
				'coins': {'gold': gold, 'silver': silver, 'diamond': diamond},
				'particle': particle,
				'palms': palms_animations,
				'shell': {'left': shell_left},
				'spikes': spikes,
				'tooth': tooth,
				'player': player_animations,
				'pearl': pearl,
				'clouds': clouds,
				'flag': flag,
				'heart_container':heart_container}


	def toggle(self):
		self.editor_active = not self.editor_active

		if self.editor_active:
			self.editor_music.play(loops=-1)
		else:
			self.editor_music.stop()

	def switch(self, grid=None):
		self.transition.active = True
		self.grid = grid
		if grid:
			self.level = Level(grid, self.switch, self.assets_dict, self.end_game)

	def game_over_escape(self):
		self.game_over = False
		self.damage_death_screen.music_played = False
		self.fall_death_screen.music_played = False
		self.damage_death_screen.reset_RGB()
		self.fall_death_screen.reset_RGB()
		self.level = Level(self.grid, self.switch, self.assets_dict, self.end_game)		

	def victory_escape(self):
		self.game_over = False
		self.victory_screen.music_played = False
		self.editor_active = True
		self.editor_music.play(loops=-1)

	def end_game(self, status):
		self.game_over = True
		self.game_over_status = status

	def call_transitions(self, dt):
		self.transition.display(dt)
		self.game_over_transition.display(dt)
		self.victory_transition.display(dt)

	def run(self):
		while True:
			dt = self.clock.tick() / 1000
			
			if not self.game_over:
				if self.editor_active:
					self.editor.run(dt)
				else:
					self.level.run(dt)
			else:
				match self.game_over_status:
					case 'victory':
						self.victory_screen.run(dt)
					case 'death by fall':
						self.fall_death_screen.run(dt)
					case 'death by damage':
						self.damage_death_screen.run(dt)

			self.call_transitions(dt)

			pygame.display.update()


if __name__ == '__main__':
	main = Main()
	main.run() 