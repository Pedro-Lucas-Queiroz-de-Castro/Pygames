import pygame
from settings import *
from laser import Laser
from sys import exit


class Ship(pygame.sprite.Sprite):
	def __init__(self, groups, images, sounds):
		ship_group, visible_sprites, asteroid_group = groups
		ship_image, laser_image = images
		explosion_sound, laser_sound = sounds

		super().__init__(ship_group)
		self.image = ship_image
		self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*4//5))
		self.mask = pygame.mask.from_surface(self.image)

		self.visible_sprites = visible_sprites
		self.asteroid_group = asteroid_group
		self.laser_image = laser_image

		# sounds
		self.explosion_sound = explosion_sound
		self.laser_sound = laser_sound

		# cooldown
		self.can_shoot = True
		self.shoot_cooldown = SHOOT_COOLDOWN
		self.shoot_time = 0


	def move(self):
		self.rect.center = pygame.mouse.get_pos()


	def shoot(self):
		if pygame.mouse.get_pressed()[0] and self.can_shoot:
			self.laser_sound.play()
			Laser([self.visible_sprites, self.asteroid_group], self.rect.midbottom,
				self.laser_image, [self.explosion_sound])
			self.can_shoot = False
			self.shoot_time = pygame.time.get_ticks()


	def asteoroid_collision(self):
		if pygame.sprite.spritecollide(self, self.asteroid_group, False, pygame.sprite.collide_mask):
			self.explosion_sound.play()
			pygame.quit()
			exit()


	def cooldowns(self):
		# shoot
		if pygame.time.get_ticks() - self.shoot_time > self.shoot_cooldown:
			self.can_shoot = True


	def update(self):
		self.cooldowns()
		self.move()
		self.shoot()
		self.asteoroid_collision()
