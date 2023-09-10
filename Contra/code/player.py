import pygame
from settings import *
from tile import MovingPlatform
from bullet import Shooter
from entity import Entity
from sys import exit

class Player(Shooter, Entity):
	def __init__(self, pos, groups, animations, collision_sprites, bullet_groups):
		super().__init__(bullet_groups, # Shooter
			pos, groups, animations, collision_sprites) # Entity

		# OVERWRITINGS
		# Entity
		# animation
		self.state = 'right_idle'
		self.animation_speed = 12

		# interactions
		self.health = 10

		# Shooter
		# shoot
		self.shot_cooldown = 400
		self.full_bullets_num = 7
		self.reload_duration = 2000

		# Float Based Movement
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.direction = pygame.math.Vector2()
		self.speed = 500

		# Vertical Movement
		self.gravity = 60
		self.on_floor = False
		self.duck = False
		self.colliding_moving_platforms = []
		self.bateu_cabeca = False

		# jump
		self.jump_speed = 1200
		self.can_jump = True
		self.jump_cooldown = 100
		self.landing_time = 0
		self.landed = False

	def update_state(self):
		if self.direction.x > 0:
			self.state = 'right'
		elif self.direction.x < 0:
			self.state = 'left'

		if self.direction.magnitude() == 0 and self.on_floor:
			self.state = self.state.split('_')[0] + '_idle'

		elif not self.on_floor:
			self.state = self.state.split('_')[0] + '_jump'

		if self.duck:
			self.state = self.state.split('_')[0] + '_duck'

	def input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP] and self.on_floor and self.can_jump:
			self.direction.y = -self.jump_speed
			self.can_jump = False
			self.landed = False

		if keys[pygame.K_DOWN] and self.on_floor:
			self.duck = True
		else:
			self.duck = False

		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
		else:
			self.direction.x = 0

		if keys[pygame.K_SPACE]:
			self.shoot()

	def move(self, direction, dt):	
		match direction:
			case 'horizontal':
				if not self.duck:
					self.pos.x += self.direction.x * self.speed * dt
					self.rect.left = round(self.pos.x)
			case 'vertical':
				self.direction.y += self.gravity
				self.pos.y += self.direction.y * dt
				self.rect.top = round(self.pos.y)
				
	def collision(self, direction):
		for sprite in self.collision_sprites.sprites():
			if self.rect.colliderect(sprite.rect):
				match direction:
					case 'horizontal':
						# player right
						if self.old_rect.right <= sprite.old_rect.left: # before collision
							self.rect.right = sprite.rect.left
						# player left
						elif sprite.old_rect.right <= self.old_rect.left: # before collision
							self.rect.left = sprite.rect.right

						self.pos.x = self.rect.x

					case 'vertical':
						# player top
						if sprite.old_rect.bottom <= self.old_rect.top: # before collision
							self.rect.top = sprite.rect.bottom
							if not self.bateu_cabeca:
								self.direction.y = 0
								self.bateu_cabeca = True

						# player bottom
						elif self.old_rect.bottom <= sprite.old_rect.top: # before collision
							self.rect.bottom = sprite.rect.top
							self.on_floor = True
							self.direction.y = 0
							self.bateu_cabeca = False			

						self.pos.y = self.rect.y

		self.glue_to_moving_platform()

		if self.on_floor and self.direction.y != 0:
			self.on_floor = False

	def glue_to_moving_platform(self):
		upward_platforms = [platform for  platform in self.colliding_moving_platforms\
			 if platform.direction.y < 0 and self.direction.y > 0]

		if upward_platforms:
			platforms = sorted(upward_platforms,
				key=lambda platform: platform.rect.top,reverse=True)
		else:
			platforms = [platform for  platform in self.colliding_moving_platforms\
			 if platform.direction.y > 0 and self.direction.y > 0]

		if platforms:
			platform = platforms[-1]
			self.direction.y = 0
			self.rect.bottom = platform.rect.top
			self.pos.y = self.rect.top
			self.on_floor = True

	def check_contact(self):
		self.colliding_moving_platforms.clear()

		bottom_rect = pygame.Rect(0,0,self.rect.width,32)
		bottom_rect.midtop = self.rect.midbottom
		for sprite in self.collision_sprites.sprites():
			if bottom_rect.colliderect(sprite):
				if self.direction.y > 0:
					self.on_floor = True
					if not self.landed:
						self.landing_time = pygame.time.get_ticks()
						self.landed = True
				if isinstance(sprite, MovingPlatform):
					self.colliding_moving_platforms.append(sprite)

	def cooldowns_manager(self):
		current_time = pygame.time.get_ticks()

		# Jump
		self.can_jump = current_time - self.landing_time > self.jump_cooldown

		# Shot
		self.shot_cooldown_manager(current_time)

		# Vulnerability
		self.vulnerability_cooldown(current_time)

	def check_death(self):
		if self.health <= 0:
			self.kill()
			pygame.quit()
			exit()

	def update(self, dt):
		self.old_rect = self.rect.copy()

		self.input()

		self.move('horizontal', dt)
		self.collision('horizontal')
		self.move('vertical', dt)
		self.collision('vertical')
		self.check_contact()

		self.cooldowns_manager()

		self.update_state()
		self.animate(dt)
		self.blink()

		self.reload()
