import pygame
from support import import_assets
from car import Car
from sys import exit


class Player(pygame.sprite.Sprite):
	"""docstring for Player"""
	def __init__(self, groups, obstacle_sprites, pos):
		super().__init__(groups)

		# animation
		self.moving = False
		self.animation_surfaces = import_assets('../graphics/player')
		self.frame_index = 0
		self.animation_speed = 4 # surfaces per second
		self.animation_direction = 'down'
		self.image = self.animation_surfaces[self.animation_direction][self.frame_index]

		self.rect = self.image.get_rect(center=pos)
		# self.mask = pygame.mask.from_surface(self.image)
	
		# float based movement
		self.pos = pygame.math.Vector2(self.rect.center)
		self.direction = pygame.math.Vector2()
		self.speed = 220

		# collision
		self.obstacle_sprites = obstacle_sprites
		self.hitbox = self.rect.copy().inflate(-10,-60)
		self.car_collide = False


	def collision(self, direction):
		for sprite in self.obstacle_sprites.sprites():
			if sprite.hitbox.colliderect(self.hitbox):
				if isinstance(sprite, Car):
					self.car_collide = True
				else:
					match direction:
						case 'horizontal':
							if self.direction.x < 0: # moving left
								self.hitbox.left = sprite.hitbox.right
							elif self.direction.x > 0: # moving right
								self.hitbox.right = sprite.hitbox.left

							self.pos.x = self.hitbox.centerx
							self.rect.centerx = self.pos.x

						case 'vertical':				
							if self.direction.y < 0: # moving up
								self.hitbox.top = sprite.hitbox.bottom
							elif self.direction.y > 0: # moving down
								self.hitbox.bottom = sprite.hitbox.top

							self.pos.y = self.hitbox.centery
							self.rect.centery = self.pos.y


	def move(self, dt):
		if self.direction.magnitude() != 0:
			self.direction.normalize_ip()

		# horizontal movement
		self.pos.x += self.direction.x * self.speed * dt
		self.rect.centerx = round(self.pos.x)
		self.hitbox.centerx = self.rect.centerx

		# horizontal collision
		self.collision('horizontal')

		# vertical movement
		self.pos.y += self.direction.y * self.speed * dt
		self.rect.centery = round(self.pos.y)
		self.hitbox.centery = self.rect.centery

		# vertical collision
		self.collision('vertical')


	def animate(self, dt):
		if self.moving:
			self.frame_index += self.animation_speed * dt
			if self.frame_index >= len(self.animation_surfaces):
				self.frame_index = 0
		else:
			self.frame_index = 0

		self.image = self.animation_surfaces[self.animation_direction][int(self.frame_index)]


	def input(self, dt):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP]:
			self.direction.y = -1
			self.animation_direction = 'up'
		elif keys[pygame.K_DOWN]:
			self.direction.y = 1
			self.animation_direction = 'down'
		else:
			self.direction.y = 0

		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
			self.animation_direction = 'right'
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
			self.animation_direction = 'left'
		else:
			self.direction.x = 0

		if self.direction.magnitude() == 0:
			self.animate(dt)
			self.moving = False
		else:
			self.moving = True


	def restrict(self):
		if self.rect.left < 640:
			self.rect.left = 640
			self.pos.x = self.rect.centerx
			self.hitbox.left = 640
			self.hitbox.centerx = self.rect.centerx

		elif self.rect.right > 2560:
			self.rect.right = 2560
			self.pos.x = self.rect.centerx
			self.hitbox.right = 2560
			self.hitbox.centerx = self.rect.centerx

		if self.rect.bottom > 3500:
			self.rect.bottom = 3500
			self.pos.y = self.rect.centery
			self.hitbox.centery = self.rect.centery

		elif self.rect.top < 860:
			self.rect.top = 860
			self.pos.y = self.rect.centery
			self.hitbox.centery = self.rect.centery


	def update(self, dt):
		self.input(dt)
		self.move(dt)
		if self.moving:
			self.animate(dt)
		self.restrict()
