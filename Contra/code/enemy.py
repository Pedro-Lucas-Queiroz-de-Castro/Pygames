import pygame
from bullet import Shooter
from entity import Entity
from settings import WINDOW_WIDTH

class Enemy(Shooter, Entity):
	def __init__(self, pos, groups, animations, collision_sprites, bullet_groups, player):
		super().__init__(bullet_groups, # Shooter
			pos, groups, animations, collision_sprites) # Entity

		# OVERWRITINGS
		# Entity
		# animations
		self.animation_speed = 6

		# interactions
		self.health = 3

		self.collision()		
		self.old_rect = self.rect.copy()

		self.player = player

		# Shoot
		self.reload_duration = 3000
		self.full_bullets_num = 4
		self.duck = False
		self.shot_cooldown = 250
		self.shot_radius = WINDOW_WIDTH // 2
		self.y_shot_radius_offset = 20

	def collision(self):
		for sprite in self.collision_sprites.sprites():
			if sprite.rect.collidepoint(self.rect.midbottom):
				if self.rect.bottom > sprite.rect.top:
					self.rect.bottom = sprite.rect.top

				if self.rect.right > sprite.rect.left:
					self.rect.right = sprite.rect.left

	def cooldowns_manager(self):
		current_time = pygame.time.get_ticks()
		self.shot_cooldown_manager(current_time)
		self.vulnerability_cooldown(current_time)

	def update_state(self):
		if self.player.rect.centerx < self.rect.centerx:
			self.state = 'left'
		else:
			self.state = 'right'

	def shot_trigger(self):
		distance = abs(self.player.rect.centerx-self.rect.centerx)
		in_y_view = self.rect.top - self.y_shot_radius_offset <\
		 					self.player.rect.centery <\
		  			self.rect.bottom + self.y_shot_radius_offset

		return distance <= self.shot_radius and in_y_view

	def update(self, dt):
		self.cooldowns_manager()
		if self.shot_trigger():
			self.shoot()
		self.update_state()
		self.animate(dt)
		self.blink()

		self.reload()