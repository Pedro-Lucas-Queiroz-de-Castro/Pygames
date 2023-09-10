import pygame

from support import *
from time_handling import *


class Entity(pygame.sprite.Sprite):
	def __init__(self, groups, animations, pos, collision_sprites):
		super().__init__(list(groups.values()))

		self.groups = groups

		# animation
		self.animations = animations
		self.animation_direction = 'right'
		self.animation_state = 'idle'
		self.animation_speed = 10
		self.frame_index = 0

		# sprite
		self.image = self.animations[self.animation_direction][self.animation_state][self.frame_index]
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect(topleft=pos)

		# collision
		self.collision_sprites = collision_sprites

		self.hitbox = max(self.mask.get_bounding_rects(), key=lambda rect: rect.width*rect.height)
		self.hitbox.topleft = self.get_hitbox_topleft()

		self.left_wall_rect = pygame.Rect(0,0,3,self.hitbox.height)
		self.right_wall_rect = pygame.Rect(0,0,3,self.hitbox.height)
		self.wall_colliding = False

		self.on_floor = False
		self.floor_rect = pygame.Rect(0,0,self.hitbox.width,3)

		# damage
		self.invulnerability_cooldown = Cooldown(0)
		self.blink_wave = TimeWave(60)

		# movement
		self.pos = pygame.math.Vector2(pos)
		self.direction = pygame.math.Vector2()

	# collisions
	def horizontal_collision(self):
		for sprite in self.collision_sprites:
			if self.hitbox.colliderect(sprite.hitbox):
				if self.old_hitbox.right <= sprite.old_hitbox.left:
					self.hitbox.right = sprite.hitbox.left

					self.rect.left = self.get_rect_topleft_from_hitbox()[0]
					self.pos.x = self.rect.left

				elif self.old_hitbox.left >= sprite.old_hitbox.right:
					self.hitbox.left = sprite.hitbox.right

					self.rect.left = self.get_rect_topleft_from_hitbox()[0]
					self.pos.x = self.rect.left

	def vertical_collision(self):
		for sprite in self.collision_sprites:
			if self.hitbox.colliderect(sprite.hitbox):
				if self.hitbox.bottom > sprite.hitbox.top:
					self.hitbox.bottom = sprite.hitbox.top

				if self.old_hitbox.top >= sprite.old_hitbox.bottom:
					self.hitbox.top = sprite.hitbox.bottom

					self.direction.y = 0
					
					self.rect.top = self.get_rect_topleft_from_hitbox()[1]
					self.pos.y = self.rect.top

				elif self.old_hitbox.bottom <= sprite.old_hitbox.top:
					self.hitbox.bottom = sprite.hitbox.top

					self.direction.y = 0

					self.rect.top = self.get_rect_topleft_from_hitbox()[1]
					self.pos.y = self.rect.top

	def check_on_floor(self, sprite):
		if self.floor_rect.colliderect(sprite.rect):
			self.on_floor = True

	def check_on_wall(self, sprite):
		for wall_rect in (self.right_wall_rect, self.left_wall_rect):
			if wall_rect.colliderect(sprite.rect):
				self.wall_colliding = True

	def check_wall_floor(self):
		self.floor_rect.width = self.hitbox.width
		self.floor_rect.topleft = self.hitbox.bottomleft

		self.on_floor = False

		self.left_wall_rect.height = self.hitbox.height
		self.right_wall_rect.height = self.hitbox.height
		self.left_wall_rect.midright = self.hitbox.midleft
		self.right_wall_rect.midleft = self.hitbox.midright

		self.wall_colliding = False

		for sprite in self.collision_sprites:
			if not self.on_floor:
				self.check_on_floor(sprite)

			if not self.wall_colliding:
				self.check_on_wall(sprite)

			if self.on_floor and self.wall_colliding:
				break

	def check_nocliff_wallcolliding(self):
		turn = False
		if self.wall_colliding:
			turn = True
		else:
			turn = True
			for sprite in self.collision_sprites:
				if self.walking and self.direction.x > 0: 
					if sprite.rect.collidepoint((self.hitbox.right+1,self.hitbox.bottom+1)):
						turn = False
				elif self.walking and self.direction.x < 0:
					if sprite.rect.collidepoint((self.hitbox.left-1,self.hitbox.bottom+1)):
						turn = False

		if turn:
			self.direction.x *= -1


	# last state
	def last_variables(self):
		self.last_image = self.image
		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()


	# hitbox
	def get_hitbox_topleft(self):
		left, top, right, bottom = get_basic_extreme_bits(self.mask)

		return (self.rect.left + left, self.rect.top + top)

	def get_rect_topleft_from_hitbox(self):
		left, top, right, bottom = get_basic_extreme_bits(self.mask)

		return (self.hitbox.left - left, self.hitbox.top - top)

	def update_mask_hitbox(self):
		if self.image != self.last_image:
			self.mask = pygame.mask.from_surface(self.image)
			self.hitbox = max(self.mask.get_bounding_rects(), key=lambda rect: rect.width*rect.height)
			self.hitbox.topleft = self.get_hitbox_topleft()
			
		return self.image != self.last_image

	def update_frame_index(self, dt, speed=None):
		speed = speed if speed else self.animation_speed

		self.frame_index += speed * dt

		if self.last_animation_state != self.animation_state:
			self.frame_index = 0

		self.frame_index_reset = False
		if self.frame_index >= len(self.animations[self.animation_direction][self.animation_state]):
			self.frame_index = 0
			self.frame_index_reset = True

	def animate(self):
		self.image = self.animations[self.animation_direction][self.animation_state][int(self.frame_index)]

	def blink(self):
		if self.invulnerability_cooldown.on:
			if self.blink_wave.boolean:
				mask_surf = self.mask.to_surface()
				mask_surf.set_colorkey('black')

				self.image = mask_surf

	def update_timers(self):
		self.invulnerability_cooldown.update()
		self.blink_wave.run()

