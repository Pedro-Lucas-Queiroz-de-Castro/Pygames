import pygame, sys
import support
from settings import * 
from pytmx.util_pygame import load_pygame
from tile import Tile, CollisionTile, MovingPlatform, PlatformBorder
from player import Player
from enemy import Enemy
from camera import AllSprites
from bullet import Bullet, Shooter, FireAnimation
from entity import Entity
from HUD import Cartridge, HealthIndicator

class Main:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption('Contra')
		self.clock = pygame.time.Clock()

		# Assets&Animation
		self.animations = {}
		self.import_assets()

		tmx_map = load_pygame('../data/map.tmx')

		# Sounds
		self.sounds = {}
		self.import_audio()
		self.audio_delivery()

		# Groups
		self.all_sprites = AllSprites(tmx_map)
		self.collision_sprites = pygame.sprite.Group()
		self.platform_border_sprites = pygame.sprite.Group()
		self.platform_sprites = pygame.sprite.Group()
		self.vulnerable_sprites = pygame.sprite.Group()

		self.setup(tmx_map)
		self.hud_setup()

	def import_audio(self):
		self.sounds = support.import_audio('../audio')

	def audio_delivery(self):
		setattr(Shooter, 'sounds', 
			{'bullet': self.sounds['bullet']})

		setattr(Bullet, 'sounds',
			{'hit': self.sounds['hit']})

		setattr(Entity, 'sounds',
			{'hit': self.sounds['hit']})

	def import_assets(self):
		for folder in ['player', 'enemy', 'fire']:
			self.animations[folder] = support.import_assets('../graphics/'+folder)

		setattr(Bullet, 'surface', pygame.image.load(
			'../graphics/bullet.png').convert_alpha())

		setattr(FireAnimation, 'animations', self.animations['fire'])

		self.health_image = pygame.image.load('../graphics/health.png').convert_alpha()

	def setup(self, tmx_map):
		tilewidth, tileheight = tmx_map.tilewidth, tmx_map.tileheight
		map_width, map_height = tmx_map.width * tilewidth,  tmx_map.height * tileheight

		# BULLET
		setattr(Bullet, 'map_boundaries', (map_width, map_height))
		setattr(Bullet, 'collision_sprites', self.collision_sprites)
		setattr(Bullet, 'vulnerable_sprites', self.vulnerable_sprites)

		# TILES
		# Level
		for x, y, surf in tmx_map.get_layer_by_name('Level').tiles():
			CollisionTile((x*tilewidth, y*tileheight), surf,
				[self.all_sprites, self.collision_sprites],
				LAYERS_Z_INDEXES['level'])

		# Others
		for layer in ['BG','BG Detail','FG Detail Bottom','FG Detail Top']:
			for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
				Tile((x*tilewidth, y*tileheight), surf, [self.all_sprites],
					LAYERS_Z_INDEXES[layer.lower()])

		# OBJECTS
		# Platforms
		for platform in tmx_map.get_layer_by_name('Platforms'):
			if 'Platform' in platform.name:
				MovingPlatform((platform.x, platform.y), platform.image,
					[self.all_sprites, self.collision_sprites, self.platform_sprites],
					LAYERS_Z_INDEXES['level'], platform.name)
			elif 'Border' in platform.name:
				PlatformBorder(platform.x,platform.y,platform.width,platform.height,
					platform.name, [self.platform_border_sprites])

		# Entities
		self.player = None
		for entity in tmx_map.get_layer_by_name('Entities'):
			# Player
			if entity.name == 'Player':
				self.player = Player((entity.x, entity.y),
					[self.all_sprites, self.vulnerable_sprites],
					self.animations['player'], self.collision_sprites,
					[self.all_sprites]) # bullet parameters
			# Enemy
			if entity.name == 'Enemy':
				Enemy((entity.x, entity.y),
					[self.all_sprites, self.vulnerable_sprites],
					self.animations['enemy'], self.collision_sprites,
					[self.all_sprites], # bullet parameters
					self.player) # enemy parameters

		# Platforms
		for platform in self.platform_sprites.sprites():
			platform.get_borders(self.platform_border_sprites)
			setattr(platform, 'player', self.player)

	def hud_setup(self):
		self.cartridge = Cartridge(self.player)
		self.health_indicator = HealthIndicator(self.health_image, self.player)

	def draw_hud(self):
		self.cartridge.draw(self.display_surface)
		self.health_indicator.draw(self.display_surface)

	def run(self):
		self.sounds['music'].play(loops=-1)
		while True:
			dt = self.clock.tick() / 1000

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()


			# Update
			self.all_sprites.update(dt)

			# Draw
			self.display_surface.fill((249,131,103))
			self.all_sprites.custom_draw(self.display_surface, self.player)
			self.draw_hud() 

			pygame.display.update()

if __name__ == '__main__':
	main = Main()
	main.run()
