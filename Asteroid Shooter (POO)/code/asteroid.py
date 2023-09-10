import pygame
from settings import *
from random import randint, uniform


class Asteroid(pygame.sprite.Sprite):
	def __init__(self, groups, pos, image):
		super().__init__(groups)

		self.scaled_image = pygame.transform.rotozoom(image, 0,
			uniform(ASTEROID_SIZE_INTERVAL[0], ASTEROID_SIZE_INTERVAL[1]))

		self.image = self.scaled_image
		self.rect = self.image.get_rect(topleft=pos)
		self.mask = pygame.mask.from_surface(self.image)

		self.interpos = pygame.math.Vector2(self.rect.topleft)
		self.direction = pygame.math.Vector2(
			uniform(ASTEROID_X_VECTOR_INTERVAL[0], ASTEROID_X_VECTOR_INTERVAL[1]), ASTEROID_Y_VECTOR)
		self.speed = randint(ASTEROID_SPEED_INTERVAL[0], ASTEROID_SPEED_INTERVAL[1])

		self.rotation = 0
		self.rotation_speed = randint(
			ASTEROID_ROTATION_SPEED_INTERVAL[0],
			ASTEROID_ROTATION_SPEED_INTERVAL[1])


	def rotate(self, dt):
		self.rotation += self.rotation_speed * dt
		self.image = pygame.transform.rotozoom(self.scaled_image, self.rotation, 1)
		self.rect = self.image.get_rect(topleft=self.rect.topleft)
		self.mask = pygame.mask.from_surface(self.image)


	def move(self, dt):
		self.interpos += self.direction * self.speed * dt
		self.rect.topleft = round(self.interpos.x), round(self.interpos.y)


	def autodestroy(self):
		if self.rect.top > ASTEROID_AUTODESTRUCTION_HEIGHT:
			self.kill()


	def update(self, dt):
		self.rotate(dt)
		self.move(dt)
		self.autodestroy()
