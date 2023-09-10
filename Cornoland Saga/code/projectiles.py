import pygame
from support import *

class Projectile(pygame.sprite.Sprite):
	def __init__(self, groups, pos, direction, animations, initial_image, 
		initial_animation_state, animation_speed, speed):
		super().__init__(groups)

		self.z = 3

		self.animations = animations
		self.animation_speed = animation_speed
		self.frame_index = 0
		self.frame_index_reseted = False

		self.image = initial_image
		self.rect = self.image.get_rect(center=pos)
		self.mask = pygame.mask.from_surface(self.image)
		self.hitbox = max(self.mask.get_bounding_rects(), key=lambda rect: rect.width*rect.height)

		self.speed = speed
		self.pos = pygame.math.Vector2(pos)
		self.direction = direction

	def get_animations(self, direction, state):
		animations = self.animations
		if direction:
			animations = self.animations[direction]
		if state:
			animations = animations[state]

		return animations

	def update_frame_index(self, dt, direction=None, state=None, speed=None):
		animations = self.get_animations(direction, state)

		speed = speed if speed else self.animation_speed

		self.frame_index += speed * dt

		self.frame_index_reseted = False
		if self.frame_index >= len(animations):
			self.frame_index = 0
			self.frame_index_reseted = True

	def animate(self, direction=None, state=None):
		animations = self.get_animations(direction, state)

		self.image = animations[int(self.frame_index)]

	def move(self, dt):
		self.pos.x += self.speed * dt * self.direction.x
		self.rect.centerx = round(self.pos.x)
		self.hitbox.topleft = self.get_hitbox_topleft()

	def get_hitbox_topleft(self):
		left, top, right, bottom = get_basic_extreme_bits(self.mask)

		return (self.rect.left + left, self.rect.top + top)

	def get_rect_topleft_from_hitbox(self):
		left, top, right, bottom = get_basic_extreme_bits(self.mask)

		return (self.hitbox.left - left, self.hitbox.top - top)


class FireBall(Projectile):
	def __init__(self, groups, pos, animation_direction, animations, collision_sprites, player):
		initial_image = animations[animation_direction]['move'][0]
		direction = pygame.math.Vector2(-1,0) if animation_direction == 'left' else pygame.math.Vector2(1,0)
		super().__init__(groups,pos,direction,animations,initial_image,'move',animation_speed=30,speed=900)

		self.player = player

		self.animation_direction = animation_direction
		self.animation_state = 'move'

		self.animation_speeds = {'move': 20, 'explosion': 12}

		self.mask = pygame.mask.from_surface(self.image)

		# attack
		self.attack_power = 1.25
		self.knockback_power = 300

		# collision
		self.collision_sprites = collision_sprites
		self.exploding = False

	def check_collisions(self):
		if self.hitbox.colliderect(self.player.hitbox):
			offset = (self.player.rect.left - self.rect.left, self.player.rect.top - self.rect.top)

			if self.mask.overlap(self.player.mask, offset):
				if False:
					self.exploding = False
				else:
					self.exploding = True

		if not self.exploding:
			for sprite in self.collision_sprites:
				if self.hitbox.colliderect(sprite.hitbox):
					self.exploding = True
					break

	def update_animation(self):
		if self.exploding and not self.was_exploding:
			self.animation_state = 'explosion'
			self.frame_index = 0

	def finish_explosion(self):
		if self.exploding:
			if self.frame_index_reseted:
				self.kill()

	def last_variables(self):
		self.last_image = self.image
		self.last_frame_index = self.frame_index

		self.was_exploding = self.exploding


	def update(self, dt):
		self.last_variables()

		if not self.exploding:
			self.move(dt)

		if not self.exploding:
			self.check_collisions()

		self.update_animation()
		self.update_frame_index(dt, self.animation_direction, self.animation_state, self.animation_speeds[self.animation_state])
		self.animate(self.animation_direction, self.animation_state)

		if self.image != self.last_image:
			self.mask = pygame.mask.from_surface(self.image)

		self.finish_explosion()


		
