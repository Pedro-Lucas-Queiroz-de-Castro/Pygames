import pygame
from support import import_assets
from random import choice
from settings import *


class Car(pygame.sprite.Sprite):
	def __init__(self, groups, pos):
		super().__init__(groups)
		self.image = choice(import_assets('../graphics/cars'))
		self.rect = self.image.get_rect(center=pos)
		self.hitbox = self.rect.copy()

		# float based movement
		self.pos = pygame.math.Vector2(self.rect.center)
		self.direction = pygame.math.Vector2(1,0)
		self.speed = 350

		if pos[0] > 0:
			self.flip()


	def flip(self):
		self.direction.x *= -1
		self.image = pygame.transform.flip(self.image, True, False) # flip x: true, flip y: false


	def move(self, dt):
		self.pos += self.direction * self.speed * dt
		self.rect.center = (round(self.pos.x), round(self.pos.y))
		self.hitbox.center = self.rect.center


	def autodestroy(self):
		if not -200 < self.rect.x < MAP_WIDTH + 200:
			self.kill()


	def update(self, dt):
		self.autodestroy()
		self.move(dt)
		