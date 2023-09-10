import pygame, sys

from pygame.math import Vector2 as vector

from settings import *
from support import *
from sprites import *

from camera import CameraGroup
from music import MusicToggle
from HUD import HeartContainer, HUDGroup

from random import choice, randint

class Level:
	def __init__(self, grid, switch, assets_dict, end_game):
		self.display_surface = pygame.display.get_surface()

		# main methods
		self.switch = switch
		self.end_game = end_game

		# groups
		self.all_sprites = CameraGroup()
		self.coin_sprites = pygame.sprite.Group()
		self.damage_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()
		self.shell_sprites = pygame.sprite.Group()
		self.water_sprites = pygame.sprite.Group()

		self.assets_dict = assets_dict

		self.sprites_initial_position = self.build_level(grid)

		# additional stuff
		self.particle_surfs = assets_dict['particle']

		# clouds
		self.cloud_timer = pygame.USEREVENT + 2
		self.cloud_surfaces = assets_dict['clouds']
		pygame.time.set_timer(self.cloud_timer, 2000)

		self.cloud_limits = {
			'left':0-WINDOW_WIDTH,
			'right':sorted(self.sprites_initial_position,
				key=lambda pos: pos[0])[-1][0] + WINDOW_WIDTH}

		self.create_clouds(startup=True, loops=int(120*(self.cloud_limits['right']//WINDOW_WIDTH)))

		self.music_toggle = MusicToggle(
			music1='../audio/SuperHero.ogg',
			music2='../audio/MuffledSuperHero.ogg',
			length=69, # seconds
			loops=-1,
			volume=0.4)

		# HUD
		self.build_hud()

	def build_hud(self):
		self.hud_sprites = HUDGroup(self.player, self.assets_dict['heart_container'])

	def build_level(self, grid):
		for layer_name, layer in grid.items():
			for pos, data in layer.items():
				# terrains
				if layer_name == 'terrains':
					Generic(
						pos=pos,
						surf=self.assets_dict['land'][data], # data -> neighbors
						groups=[self.all_sprites, self.collision_sprites],
						z=LEVEL_LAYERS['terrain'])

				elif layer_name == 'waters':
					if data == 'top':
						Animated(
							assets=self.assets_dict['water'][data],
							pos=pos,
							groups=[self.all_sprites, self.water_sprites],
							z=LEVEL_LAYERS['water'])

					elif data == 'bottom':
						Generic(
							pos=pos,
							surf=self.assets_dict['water'][data],
							groups=[self.all_sprites, self.water_sprites],
							z=LEVEL_LAYERS['water'])

				elif layer_name == 'enemies':
					match data: # data -> EDITOR DATA ID
						case 7: Spikes(
							surf=self.assets_dict['spikes'],
							pos=pos,
							groups=[self.all_sprites, self.damage_sprites])
						case 8: Tooth(
							assets=self.assets_dict['tooth'],
							pos=pos,
							groups=[self.all_sprites, self.damage_sprites],
							collision_sprites=self.collision_sprites)
						
						case 9: Shell(
							orientation='left',
							assets=self.assets_dict['shell'],
							pos=pos,
							groups=[self.all_sprites, self.collision_sprites, self.shell_sprites],
							pearl_surf=self.assets_dict['pearl'],
							damage_sprites=self.damage_sprites,
							collision_sprites=self.collision_sprites,
							all_sprites=self.all_sprites)
							
						case 10:
							Shell(
							orientation='right',
							assets=self.assets_dict['shell'],
							pos=pos,
							groups=[self.all_sprites, self.collision_sprites, self.shell_sprites],
							pearl_surf=self.assets_dict['pearl'],
							damage_sprites=self.damage_sprites,
							collision_sprites=self.collision_sprites,
							all_sprites=self.all_sprites)

				elif layer_name == 'coins':
					match data:
						case 4:
							coin_type = 'gold'
						case 5:
							coin_type = 'silver'
						case 6:
							coin_type = 'diamond'

					Coin(coin_type=coin_type,
						assets=self.assets_dict['coins'][coin_type],
						pos=pos,
						groups=[self.all_sprites, self.coin_sprites])

				elif layer_name == 'fg objects':
					match data: # data -> EDITOR DATA ID
						case 0: # player
							self.player = Player(
								assets=self.assets_dict['player'],
								pos=pos, 
								groups=[self.all_sprites],
								collision_sprites=self.collision_sprites,
								water_sprites=self.water_sprites)

						case 1: # sky
							self.horizon_y = pos[1]
							self.all_sprites.horizon_y = pos[1]

						case 19: # flag
							self.flag = Flag(
								assets=self.assets_dict['flag'],
								pos=pos,
								groups=[self.all_sprites]
								)

						case 20: # death cross
							self.death_line_y = pos[1]
					
				# palms
				if isinstance(data, int):
					if 'palm' in EDITOR_DATA[data]['style']:
						palm = EDITOR_DATA[data]['graphics'].split('/')[-1]

						if 'bg' in palm:
							z = LEVEL_LAYERS['bg']
						else:
							z = LEVEL_LAYERS['fg palm']

						if 'fg' in palm:
							size = EDITOR_DATA[data]['block']['size']
							offset = EDITOR_DATA[data]['block']['offset']
							Block(pos+vector(offset), size, [self.collision_sprites])

						Animated(
							assets=self.assets_dict['palms'][palm],
							pos=pos,
							groups=[self.all_sprites],
							z=z)
		
		# delivering player to other objects
		for shell in self.shell_sprites:
			shell.player = self.player


		sprites_initial_position = []
		for layer, dictionary in grid.items():
			if dictionary:
				for pos in dictionary.keys():
					sprites_initial_position.append(pos)

		return sprites_initial_position

	def get_damage(self):
		damage_sprites_colliding_with_player = pygame.sprite.spritecollide(
			self.player, self.damage_sprites, False, pygame.sprite.collide_mask)

		for sprite in damage_sprites_colliding_with_player:
			if isinstance(sprite, Pearl):
				sprite.kill()
			self.player.damage()
			Level.hit_sound.play()

	def get_coins(self):
   		colliding_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)
   		for coin_sprite in colliding_coins:
   			pos = coin_sprite.rect.center
   			Particle(self.particle_surfs, pos, [self.all_sprites])
   			Level.coin_sound.play()

	def check_game_state(self):
		if self.flag.hitbox.colliderect(self.player.hitbox):
			self.music_toggle.stop()
			self.end_game('victory')

		if self.player.hitbox.top > self.death_line_y:
			self.music_toggle.stop()
			self.end_game('death by fall')

		if self.player.health <= 0:
			self.music_toggle.stop()
			self.end_game('death by damage')


	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				self.music_toggle.stop()
				self.switch()

			if event.type == self.cloud_timer:
				self.create_clouds()

	def create_clouds(self, startup=False, loops=1):
		for i in range(loops):
			surf = choice(self.cloud_surfaces)
			surf = pygame.transform.scale2x(surf) if randint(1,5) > 3 else surf

			if startup:
				x = randint(-(WINDOW_WIDTH//2+100),self.cloud_limits['right'])
			else:
				x = self.cloud_limits['right']

			y = randint(self.horizon_y-WINDOW_HEIGHT*4, self.horizon_y-100)

			speed = randint(20,50)

			Cloud((x,y), surf, speed, self.all_sprites, self.cloud_limits)

	def update(self, dt):
		head_on_water_in_last_frame = self.player.head_on_water

		self.all_sprites.update(dt)
		self.get_coins()
		self.get_damage()
		self.check_game_state()

		# sounds
		if self.player.head_on_water != head_on_water_in_last_frame:
			self.music_toggle.toggle()

		self.hud_sprites.update()

	def draw(self):
		self.display_surface.fill(SKY_COLOR)
		self.all_sprites.custom_draw(self.player)
		# pygame.draw.rect(self.display_surface, 'white', self.player.hitbox)
		# pygame.draw.rect(self.display_surface, 'brown', self.player.floor_rect)
		self.hud_sprites.custom_draw()

	def run(self, dt):
		if not self.music_toggle.active:
			self.music_toggle.start()

		self.event_loop()

		self.update(dt)
		self.draw()