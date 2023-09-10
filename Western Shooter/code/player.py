import pygame
from sys import exit
from pygame.math import Vector2 as Vector
from entity import Entity

class Player(Entity):
	def __init__(self, name, pos, groups, animations, collision_objects, create_bullet):
		super().__init__(name, pos, groups, animations, collision_objects)

		# OVERWRITES
		# health
		self.health = 200

		# speed
		self.speed = 300

		# SPECIFICS
		# bullet
		self.shooting = False
		self.create_bullet = create_bullet

		# attack
		self.attack_power = 20

		# movement
		self.direction_factor = 1

	def input(self):
		keys = pygame.key.get_pressed()

		if not self.attacking:
			if keys[pygame.K_RIGHT]:
				self.direction.x = 1
			elif keys[pygame.K_LEFT]:
				self.direction.x = -1
			else:
				self.direction.x = 0

			if keys[pygame.K_UP]:
				self.direction.y = -1
			elif keys[pygame.K_DOWN]:
				self.direction.y = 1
			else:
				self.direction.y = 0

			if keys[pygame.K_SPACE]:
				self.attacking = True
				self.direction = Vector()
				self.frame_index = 0

				self.shoot()

	def update_state(self):
		if self.direction.x > 0:
			self.state = 'right'
		elif self.direction.x < 0:
			self.state = 'left'
		if self.direction.y < 0:
			self.state = 'up'
		elif self.direction.y > 0:
			self.state = 'down'

		if self.direction.magnitude() == 0 and not self.attacking and\
		 not 'idle' in self.state:
			self.state = self.state.split('_')[0] + '_idle'
			self.frame_index = 0

		if self.attacking and not 'attack' in self.state:
			self.state = self.state.split('_')[0] + '_attack'

	def shoot(self):
		match self.state.split('_')[0]:
			case 'left': 
				offsetx, offsety = -60, 3
				x, y = -1, 0
			case 'right': 
				offsetx, offsety = 60, 3
				x, y = 1, 0
			case 'up': 
				offsetx, offsety = 20, -60
				x, y = 0, -1
			case 'down': 
				offsetx, offsety = -20, 60
				x, y = 0, 1

		bullet_center_pos = (self.rect.centerx+offsetx,
								  self.rect.centery+offsety)
		bullet_direction = Vector(x,y)

		if int(self.frame_index) == 2 and self.attacking and not self.shooting:
			self.create_bullet(bullet_center_pos, bullet_direction, self, 500)
			self.shooting = True

	def check_death(self):
		if self.health <= 0:
			pygame.quit()
			exit()

	def update(self, dt):
		self.input()
		self.update_state()
		self.move(dt, self.direction_factor)
		self.update_overlap(self.overlap_value)
		self.animate(dt, lambda: setattr(self, 'shooting', False))
		self.shoot()
		self.vulnerability_timer()
		self.blink()

