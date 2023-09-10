import pygame
from settings import *

class Laser(pygame.sprite.Sprite):
	def __init__(self, groups, pos, image, sounds):
		visible_sprites, asteroid_group = groups
		explosion_sound = sounds[0]

		super().__init__(visible_sprites)
		self.image = image
		self.rect = self.image.get_rect(midbottom=pos)
		self.mask = pygame.mask.from_surface(self.image)
		
		self.interpos = pygame.math.Vector2(self.rect.topleft)
		self.direction = pygame.math.Vector2(LASER_VECTOR_POS[0], LASER_VECTOR_POS[1])
		self.speed = LASER_SPEED

		self.asteroid_group = asteroid_group
		self.explosion_sound = explosion_sound

	def move(self, dt):
		self.interpos -= self.direction * self.speed * dt
		self.rect.topleft = round(self.interpos.x), round(self.interpos.y)


	def asteroid_collision(self):
		if pygame.sprite.spritecollide(self, self.asteroid_group, True, pygame.sprite.collide_mask):
			self.explosion_sound.play()
			self.kill()

	def autodestroy(self):
		if self.rect.bottom < LASER_AUTODESTRUCTION_HEIGHT:
			self.kill()


	def update(self, dt):
		self.move(dt)
		self.asteroid_collision()
		self.autodestroy()
