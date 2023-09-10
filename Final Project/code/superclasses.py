import pygame

from support import *


class Sprite(pygame.sprite.Sprite):
	def __init__(self, groups):
		super().__init__(groups)


class Animated:
	def __init__(self, animations, animation_keys, animations_speeds, frames_default_sizes,
		scale_offset, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.scale_offset = scale_offset

		self.animations = get_direction_state_animations_copy(animations)
		self.animation_keys = animation_keys
		self.animations_speeds = animations_speeds

		self.frame_index = 0

		scale_graphics_with_direction_and_state(self.animations,self.scale_offset,frames_default_sizes)

		self.image = self.get_animation()[self.frame_index]

	def get_animation(self):
		keys = list(self.animation_keys.values())
		animation = self.animations

		for i in range(len(keys)):
			animation = animation[keys[i]]

		return animation

	def update_frame_index(self, dt=1):
		self.frame_index += self.animations_speeds[self.animation_keys['state']] * dt

		if self.animation_keys['state'] != self.last_animation_state:
			self.frame_index = 0
		
		reseted = False
		if self.frame_index >= len(self.get_animation()):
			self.frame_index = 0
			reseted = True

		return reseted

	def animate(self):
		self.image = self.get_animation()[int(self.frame_index)]

	def previous_variables(self):
		self.last_animation_state = self.animation_keys['state']


class Collisor:
	def __init__(self, collidable_group, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.collidable_group = collidable_group

		self.on_floor = False
		self.on_wall = {'left': False, 'right': False}
		
	def create_collision_rects(self):
		self.floor_rect = pygame.Rect(self.hitbox.x,self.hitbox.bottom,self.hitbox.width,2)

		self.wall_rects = {}
		self.wall_rects['left'] = pygame.Rect(self.hitbox.left-2,self.hitbox.top,2,self.hitbox.height)
		self.wall_rects['right'] = pygame.Rect(self.hitbox.right+2,self.hitbox.top,2,self.hitbox.height)

	def collisions(self, direction):
		sprites_on_floor = []
		sprites_on_wall = {'left': [], 'right': []}

		for sprite in self.collidable_group:
			match direction:
				case 'horizontal':
					if sprite.hitbox.colliderect(self.hitbox):
						if sprite.old_hitbox.left >= self.old_hitbox.right:
							self.hitbox.right = sprite.hitbox.left
							self.direction.x = 0

							self.rect.x = self.hitbox.x
							self.pos.x = self.rect.x

						elif sprite.old_hitbox.right <= self.old_hitbox.left:
							self.hitbox.left = sprite.hitbox.right
							self.direction.x = 0

							self.rect.x = self.hitbox.x
							self.pos.x = self.rect.x

					self.wall_rects['left'].topright = self.hitbox.topleft
					self.wall_rects['right'].topleft = self.hitbox.topright

					for side in ('left', 'right'):
						sprites_on_wall[side].append(sprite.hitbox.colliderect(self.wall_rects[side]))

					for side in ('left', 'right'):
						self.on_wall[side] = any(sprites_on_wall[side])

				case 'vertical':
					if sprite.hitbox.colliderect(self.hitbox):
						if sprite.old_hitbox.top >= self.old_hitbox.bottom:
							self.hitbox.bottom = sprite.hitbox.top
							self.direction.y = 0

							self.rect.y = self.hitbox.y
							self.pos.y = self.rect.y

						elif sprite.old_hitbox.bottom <= self.old_hitbox.top:
							self.hitbox.top = sprite.hitbox.bottom
							if self.direction.y < 0:
								self.direction.y = 0

							self.rect.y = self.hitbox.y
							self.pos.y = self.rect.y

					self.floor_rect.topleft = self.hitbox.bottomleft

					sprites_on_floor.append(sprite.hitbox.colliderect(self.floor_rect))

					self.on_floor = any(sprites_on_floor)

					if self.on_floor:
						self.direction.y = 0


class AlphaFade:
	def __init__(self, fade_speed, start_alpha=255, end_alpha=0, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.alpha = start_alpha

		self.fade_speed = fade_speed
		self.start_alpha = start_alpha
		self.end_alpha = end_alpha

	def fade(self, dt=1):
		self.alpha = tend_to(self.alpha, self.end_alpha, self.fade_speed*dt)

	def fade_image(self, surface):
		surface.set_alpha(self.alpha)