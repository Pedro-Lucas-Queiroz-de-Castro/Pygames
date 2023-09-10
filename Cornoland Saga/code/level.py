import pygame

from pytmx.util_pygame import load_pygame

from settings import *
from map_elements import *
from enemies import *
from UI import *

from projectiles import FireBall
from player import Player


class Level:
	def __init__(self, graphics, camera_group, collision_sprites, damage_sprites, attackable_sprites, monster_sprites, hearts_group):
		self.display_surface = pygame.display.get_surface()
		self.window_width = self.display_surface.get_width()
		self.window_height = self.display_surface.get_height()

		self.graphics = graphics

		# groups
		self.camera = camera_group
		self.collision_sprites = collision_sprites
		self.damage_sprites = damage_sprites
		self.attackable_sprites = attackable_sprites
		self.monster_sprites = monster_sprites
		self.hearts_group = hearts_group

		self.setup()

		# UI
		self.UI = UI(self.hearts_group, self.monster_sprites)
		self.UIsetup()

	# setup
	def setup(self):
		tmxdata = load_pygame('../data/map.tmx')
		# self.setup_background(tmxdata)
		self.setup_map(tmxdata)
		self.setup_entities(tmxdata)

	def setup_background(self, tmxdata):
		tile_width, tile_height = tmxdata.tilewidth, tmxdata.tileheight

		for bg in tmxdata.get_layer_by_name('Backgrounds'):
			Background(bg.image, (bg.x,bg.y), [self.camera], bg.z)

		for x, y, surface in tmxdata.get_layer_by_name('BackgroundTiles').tiles():
			Tile(surface, (x*tile_height,y*tile_width), [self.camera])

	def setup_map(self, tmxdata):
		tile_width, tile_height = tmxdata.tilewidth, tmxdata.tileheight

		for x, y, surface in tmxdata.get_layer_by_name('Terrains').tiles():
			'''
			Tentar unir superficies conectadas em uma só,
			criando assim um sprite apenas ao invés de vários, a performance agradece!
			'''
			Tile(surface, (x*tile_height,y*tile_width), [self.camera, self.collision_sprites])

		# for decoration in tmxdata.get_layer_by_name('Decorations'):
		# 	Decoration(decoration.image, (decoration.x,decoration.y), [self.camera])

	def setup_entities(self, tmxdata):
		for entity in tmxdata.get_layer_by_name('Player'):
			if entity.name == 'Player':
				self.player = Player({'camera': self.camera}, self.graphics['player'],
					self.graphics['melee attack hitboxes'], (entity.x,entity.y), 
					(self.window_width, self.window_height),
					self.collision_sprites, self.damage_sprites, self.attackable_sprites, self.add_heart)

		for entity in tmxdata.get_layer_by_name('Monsters'):
			if entity.name == 'Fire Worm':
				FireWorm({'camera': self.camera, 'damage': self.damage_sprites,
					'attackable': self.attackable_sprites, 'monster': self.monster_sprites},
					self.graphics['fire worm'], (entity.x,entity.y), self.collision_sprites,
					self.player, self.create_fireball)


	# create stuff
	def create_fireball(self, pos, direction):
		FireBall([self.camera, self.damage_sprites], pos, direction, self.graphics['fire ball'],
			self.collision_sprites, self.player)


	# UI
	def UIsetup(self):
		self.set_hearts()

	def set_hearts(self):
		for n in range(self.player.max_hearts):
			x = FIRST_HEART_POS[0] + (FIRST_HEART_POS[0] + HEART_HORIZONTAL_THRESHOLD) * n
			y = FIRST_HEART_POS[1]

			Heart(self.graphics['UI']['hearts'], {'topleft': (x,y)}, [self.hearts_group], 1)

	def add_heart(self):
		if self.player.max_hearts <= 15:
			x = FIRST_HEART_POS[0] + (FIRST_HEART_POS[0] + HEART_HORIZONTAL_THRESHOLD) * (self.player.max_hearts-1)
			y = FIRST_HEART_POS[1]
		else:
			x = FIRST_HEART_POS[0] + (FIRST_HEART_POS[0] + HEART_HORIZONTAL_THRESHOLD) * (self.player.max_hearts-16)
			y = FIRST_HEART_POS[1] + self.graphics['UI']['hearts'][0].get_width() + HEART_VERTICAL_THRESHOLD

		Heart(self.graphics['UI']['hearts'], {'topleft': (x,y)}, [self.hearts_group], 0)



	# main
	def update(self, dt):
		self.camera.update(dt)

	def draw(self, dt):
		self.display_surface.fill('#073232')
		self.camera.custom_draw(self.player, dt)
		self.UI.custom_draw(self.player, dt)
