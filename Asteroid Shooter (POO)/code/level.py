import pygame
from settings import *
from ship import Ship
from laser import Laser
from asteroid import Asteroid
from score import Score
from random import randint


class Level:
	def __init__(self):
		self.screen = pygame.display.get_surface()
		self.ship_group = pygame.sprite.GroupSingle()
		self.visible_sprites = pygame.sprite.Group()
		self.asteroid_group = pygame.sprite.Group()
		self.background_surf = pygame.image.load('../images/background.png').convert()

		# images
		self.ship_image = pygame.image.load('../images/ship.png').convert_alpha()
		self.laser_image = pygame.image.load('../images/laser.png').convert_alpha()
		self.asteroid_image = pygame.image.load('../images/asteroid.png').convert_alpha()

		# sounds
		self.explosion_sound = pygame.mixer.Sound('../sounds/explosion.wav')
		self.laser_sound = pygame.mixer.Sound('../sounds/laser.ogg')
		self.music = pygame.mixer.Sound('../sounds/music.wav')
		self.music.play(loops=-1)

		self.ship = Ship([self.ship_group, self.visible_sprites, self.asteroid_group],
			(self.ship_image, self.laser_image), (self.explosion_sound, self.laser_sound))
		self.score = Score()

		# asteroid cooldown
		self.asteroid_cooldown = ASTEROID_COOLDOWN
		self.asteroid_time = 0


	def generate_asteroid(self):
		Asteroid([self.visible_sprites, self.asteroid_group],
			(randint(ASTEROID_START_XPOS_INTERVAL[0], ASTEROID_START_XPOS_INTERVAL[1]),
			 randint(ASTEROID_START_YPOS_INTERVAL[0], ASTEROID_START_YPOS_INTERVAL[1])),
			self.asteroid_image)


	def cooldowns(self):
		if pygame.time.get_ticks() - self.asteroid_time > self.asteroid_cooldown:
			self.generate_asteroid()
			self.asteroid_time = pygame.time.get_ticks()


	def update(self, dt):
		self.visible_sprites.update(dt)
		self.ship_group.update()
		self.score.update()


	def draw(self):
		self.screen.blit(self.background_surf, (0,0))
		self.score.draw()
		self.visible_sprites.draw(self.screen)
		self.ship_group.draw(self.screen)
		

	def run(self, dt):
		self.cooldowns()
		self.update(dt)
		self.draw()
