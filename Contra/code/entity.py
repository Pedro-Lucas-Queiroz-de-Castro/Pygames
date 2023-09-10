import pygame
from settings import *
from math import sin

class Entity(pygame.sprite.Sprite):
	def __init__(self, pos, groups, animations, collision_sprites):
		super().__init__(groups)

		# Animation
		self.animation_speed = 1 # surfaces per second
		self.animations = animations
		self.state = 'right'
		self.frame_index = 0

		# Sprite
		self.image = self.animations[self.state][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		self.mask = pygame.mask.from_surface(self.image)
		self.z = LAYERS_Z_INDEXES['level']

		# Collision
		self.old_rect = self.rect.copy()
		self.collision_sprites = collision_sprites

		# Interactions
		self.health = 3
		self.vulnerable = True
		self.vulnerability_duration = 500
		self.hit_time = 0

		# Audio
		if hasattr(self, 'sounds'):
			for key, value in Entity.sounds.items():
				self.sounds[key] = value
		else:
			self.sounds = Entity.sounds

	def get_damage(self, amount):
		if self.vulnerable:
			self.sounds['hit'].play()
			self.health -= amount
			self.check_death()
			self.vulnerable = False
			self.hit_time = pygame.time.get_ticks()

	def blink(self):
		if not self.vulnerable and self.sin_function():
			mask = pygame.mask.from_surface(self.image)
			mask_surface = mask.to_surface()
			mask_surface.set_colorkey((0,0,0))

			self.image = mask_surface

	def sin_function(self):
		return sin(pygame.time.get_ticks()) >= 0

	def vulnerability_cooldown(self, current_time):
		if current_time - self.hit_time > self.vulnerability_duration:
			self.vulnerable = True

	def check_death(self):
		if self.health <= 0:
			self.kill()

	def animate(self, dt):
		# frame progress
		self.frame_index += self.animation_speed * dt
		if int(self.frame_index) >= len(self.animations[self.state]):
			self.frame_index = 0

		# image/mask update
		self.image = self.animations[self.state][int(self.frame_index)]
		self.mask = pygame.mask.from_surface(self.image)