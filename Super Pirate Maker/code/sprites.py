import pygame

from pygame.math import Vector2 as vector

from settings import *
from timer import *

from random import choice
from math import sin


class Generic(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups, z=LEVEL_LAYERS['main']):
		super().__init__(groups)

		self.image = surf
		self.rect = self.image.get_rect(topleft=pos)
		self.old_rect = self.rect.copy()
		self.z = z


class Animated(Generic):
	def __init__(self, assets, pos, groups, state=None, z=LEVEL_LAYERS['main']):
		Generic_asset = assets[state] if state else assets
		super().__init__(pos, Generic_asset[0], groups, z)

		# animation
		self.state = state
		self.frames = assets
		self.frame_index = 0
		self.animation_speed = ANIMATION_SPEED # surfs per second

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt

		if self.state:
			length = len(self.frames[self.state])
		else:
			length = len(self.frames)

		if self.frame_index >= length:
			self.frame_index = 0

		if self.state:
			image = self.frames[self.state][int(self.frame_index)]
		else:
			image = self.frames[int(self.frame_index)]

		self.image = image

	def update(self, dt):
		self.animate(dt)


class Block(Generic):
	def __init__(self, pos, size, groups):
		super().__init__(pos, pygame.Surface(size), groups)
		self.old_rect = self.rect.copy()


class Cloud(Generic):
	def __init__(self, pos, surf, speed, groups, limits):
		super().__init__(pos, surf, groups, LEVEL_LAYERS['clouds'])

		self.limits = limits

		# movement
		self.pos = vector(pos)
		self.speed = speed

	def move(self, dt):
		self.pos.x -= self.speed * dt
		self.rect.x = round(self.pos.x)

	def autodestroy(self):
		if self.rect.right < self.limits['left']:
			self.kill()

	def update(self, dt):
		self.move(dt)
		self.autodestroy()


class Coin(Animated):
	def __init__(self, coin_type, assets, pos, groups):
		super().__init__(assets, pos, groups)

		self.coin_type = coin_type
		self.rect.center = pos


class Particle(Animated):
	def __init__(self, assets, pos, groups):
		super().__init__(assets, pos, groups)	

		self.rect.center = pos

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt
		if self.frame_index >= len(self.frames):
			self.kill()
		else:
			self.image = self.frames[int(self.frame_index)]


class Spikes(Generic):
	def __init__(self, surf, pos, groups):
		super().__init__(pos, surf, groups)

		self.rect.midbottom = pos

		self.mask = pygame.mask.from_surface(self.image)


class Tooth(Animated):
	def __init__(self, assets, pos, groups, collision_sprites):
		super().__init__(assets, pos, groups, 'run_right')

		# animation
		# if not 'idle_right' in self.frames:
		# 	self.get_right_idle_frames()
		self.state = 'run_right'

		# float based movement
		self.rect.midbottom = pos
		self.direction = vector(choice((-1,1)),0)
		self.pos = vector(self.rect.topleft)
		self.speed = 120

		# collision
		self.collision_sprites = collision_sprites
		self.mask = pygame.mask.from_surface(self.image)

		# adjust initial placement or destroy
		self.on_floor()

	def get_right_idle_frames(self):
		self.frames['idle_left'] = self.frames['idle']
		del self.frames['idle']

		frames = []
		for frame in self.frames['idle_left']:
			frames.append(pygame.transform.flip(frame,True,False))

		self.frames['idle_right'] = frames

	def on_floor(self):
		on_floor = False

		for sprite in self.collision_sprites:
			if sprite.rect.collidepoint(self.rect.midbottom + vector(0,10)):
				self.rect.bottom = sprite.rect.top
				self.pos = vector(self.rect.topleft)

				on_floor = True

		if not on_floor:
			self.kill()

	def update_state(self):
		self.state = 'run'
		if self.direction.x > 0:
			self.state += '_right'
		elif self.direction.x < 0:
			self.state += '_left'

	def move(self, dt):
		self.pos.x += self.direction.x * self.speed * dt
		self.rect.x = round(self.pos.x)

	def wall_floor_colliding(self, block_pos, cliff_pos):
		wall_sprites = []
		floor_sprites = []

		for sprite in self.collision_sprites:
			rect = sprite.rect if not hasattr(sprite, 'hitbox') else sprite.hitbox

			if rect.collidepoint(block_pos):
				wall_sprites.append(sprite)
			if rect.collidepoint(cliff_pos):
				floor_sprites.append(sprite)

		return wall_sprites, floor_sprites

	def collision(self):
		right_cliff = vector(self.rect.bottomright) + vector(1,1)
		right_block = vector(self.rect.midright) + vector(1,0)
		left_cliff = vector(self.rect.bottomleft) + vector(-1,1)
		left_block = vector(self.rect.midleft) + vector(-1,0)

		if self.direction.x > 0: # moving right
			wall_sprites, floor_sprites = self.wall_floor_colliding(right_block, right_cliff)

			if wall_sprites or not floor_sprites:
				self.direction.x *= -1

		elif self.direction.x < 0: # moving left
			wall_sprites, floor_sprites = self.wall_floor_colliding(left_block, left_cliff)

			if wall_sprites or not floor_sprites:
				self.direction.x *= -1

	def update(self, dt):
		self.old_rect = self.rect

		self.collision()
		self.move(dt)

		self.update_state()
		self.animate(dt)
		self.mask = pygame.mask.from_surface(self.image)


class Shell(Animated):
	def __init__(self, orientation, assets, pos, groups, pearl_surf,
		damage_sprites, collision_sprites, all_sprites):
		assets = self.set_assets_orientation(assets.copy(), orientation)
		super().__init__(assets, pos, groups, 'idle')
		
		self.state = 'idle'
		self.orientation = orientation
		self.rect.midbottom = pos

		# pearl attack
		self.pearl_surf = pearl_surf

		self.has_shot = False
		self.attack_cooldown = Timer(2000)

		self.attack_radius = 500
		self.attack_threshold = TILE_SIZE

		# pearl groups / collision
		self.damage_sprites = damage_sprites
		self.all_sprites = all_sprites

		self.collision_sprites = collision_sprites

		# collision
		self.top_inflate = {'attack': [-2,0,-12,-8,-4], 'idle': [-4]}
		self.hitbox = self.rect.inflate(
			0, self.top_inflate[self.state][int(self.frame_index)])
		self.hitbox.midbottom = self.rect.midbottom

		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

	def set_assets_orientation(self, assets, orientation):
		if orientation == 'right':
			assets = {key: [pygame.transform.flip(surf,True,False) for surf in value] 
			 for key, value in assets['left'].items()}
		else:
			assets = assets['left']

		return assets

	def direction_distance_to_player(self):
		direction = (vector(self.player.rect.center) - vector(self.rect.center))
		return direction, direction.magnitude()
		 	   
	def attack_conditions(self):
		direction, distance = self.direction_distance_to_player()

		match self.orientation:
			case 'right':
				facing = direction.x + self.rect.width/2 > 0
			case 'left':
				facing = direction.x - self.rect.width/2 < 0 

		return distance <= self.attack_radius and\
		 facing and\
		 self.rect.bottom + self.attack_threshold >\
		  self.player.rect.centery > self.rect.top - self.attack_threshold and\
		  not self.attack_cooldown.active
		    
	def update_state(self):
		if self.attack_conditions():
			self.state = 'attack'
			self.attack_cooldown.activate()

	def end_attack(self):
		if self.has_shot and self.frame_index == 0:
			self.state = 'idle'
			self.has_shot = False

	def shoot_pearl(self):
		if int(self.frame_index) == 2 and not self.has_shot:
			self.has_shot = True

			direction = vector(-1,0) if self.orientation == 'left' else vector(1,0)
			pos = (self.rect.centerx, self.rect.centery+7)

			Pearl(pos, self.pearl_surf, [self.all_sprites, self.damage_sprites],
				direction, self.collision_sprites, self)

	def update_hitbox(self):
		self.hitbox = self.rect.inflate(
			0,
			self.top_inflate[self.state][int(self.frame_index)])

		self.hitbox.midbottom = self.rect.midbottom

	def update(self, dt):
		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.update_state()
		self.animate(dt)
		self.update_hitbox()
		self.end_attack()

		if self.state == 'attack':
			self.shoot_pearl()

		self.attack_cooldown.update()


class Pearl(Generic):
	def __init__(self, pos, surf, groups, direction, collision_sprites, shooter):
		super().__init__(pos, surf, groups, LEVEL_LAYERS['pearl'])

		self.rect.center = pos

		# float based movement
		self.pos = vector(pos)
		self.direction = direction
		self.speed = 600

		# collisions
		self.collision_sprites = collision_sprites
		self.shooter = shooter
		self.mask = pygame.mask.from_surface(self.image)

	def move(self, dt):
		self.pos.x += self.direction.x * self.speed * dt
		self.rect.centerx = round(self.pos.x)

		self.collisions()

	def collisions(self):
		# collision sprites
		for sprite in self.collision_sprites:
			if sprite != self.shooter:
				if self.rect.colliderect(sprite.rect):
					self.kill()

	def update(self, dt):
		self.old_rect = self.rect.copy()
		self.move(dt)


class Player(Animated):
	def __init__(self, assets, pos, groups, collision_sprites, water_sprites):
		super().__init__(assets, pos, groups, 'idle_right')

		# health
		self.health = PLAYER_START_HEALTH

		# animation
		self.state = 'idle_right'

		# float based movement
		self.direction = vector()
		self.pos = vector(self.rect.center)
		self.speed = 300 

		# vertical movement
		self.gravity = 8.5
		self.on_floor = True
		self.jump_speed = 3.5

		# collision
		self.collision_sprites = collision_sprites
		self.hitbox = self.rect.inflate(-90,0)
		self.mask = pygame.mask.from_surface(self.image)

		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		# invulnerability
		self.invulnerability_timer = Timer(700)

		# water
		self.water_sprites = water_sprites

		self.on_water = False
		self.head_on_water = False
		self.hat_on_water = False

		self.swim_speed = 120

		self.water_up_aceleration = 0.12
		self.water_up_max_speed = -2.5

		self.water_deceleration = 6
		self.min_water_fall_speed = 1
		self.water_fall_speed_up = 2.5

		self.head_rect = self.hitbox.inflate(0,-20)
		self.hat_rect = self.hitbox.inflate(0,-57)

	def check_on_water(self):
		self.hat_on_water = bool(
			[sprite for sprite in self.water_sprites if sprite.rect.colliderect(self.hat_rect)])

		if self.hat_on_water:
			self.head_on_water = True
			self.on_water = True
		else:
			self.head_on_water = bool(
				[sprite for sprite in self.water_sprites if sprite.rect.colliderect(self.head_rect)])

		if self.head_on_water:
			self.on_water = True
		else:
			self.on_water = bool(
				[sprite for sprite in self.water_sprites if sprite.rect.colliderect(self.hitbox)])

	def input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
		else:
			self.direction.x = 0

		if keys[pygame.K_UP]:
			if self.hat_on_water:
				self.direction.y -= self.water_up_aceleration
				self.direction.y = max(self.water_up_max_speed, self.direction.y)

			elif self.on_floor:
				self.direction.y = -self.jump_speed
				Player.jump_sound.play()

		return keys

	def apply_gravity(self, dt, keys):

		if self.on_water:
			if not keys[pygame.K_UP]:
				self.water_fall_speed_up = 2 if keys[pygame.K_DOWN] else 1
				self.direction.y -= self.water_deceleration * dt / self.water_fall_speed_up
				self.direction.y = max(self.min_water_fall_speed*self.water_fall_speed_up, self.direction.y)
		else:
			self.direction.y += self.gravity * dt

	def check_on_floor(self, keys):
		self.floor_rect = pygame.Rect(self.hitbox.bottomleft,(self.hitbox.width,2))

		colliding_sprites = [sprite for sprite in self.collision_sprites
		 if sprite.rect.colliderect(self.floor_rect)]

		sprites_that_were_colliding = []
		for sprite in self.collision_sprites:
			old_rect = sprite.old_hitbox if hasattr(sprite, 'hitbox') else sprite.old_rect

			if old_rect.colliderect(self.old_hitbox) or old_rect.top == self.old_rect.bottom:
				sprites_that_were_colliding.append(sprite)

		sprites_that_were_colliding = sorted(sprites_that_were_colliding,
			key=lambda sprite: sprite.hitbox.top if hasattr(sprite, 'hitbox') else sprite.rect.top)


		if colliding_sprites:
			self.on_floor = True
		else:
			self.on_floor = False

		if sprites_that_were_colliding:
			if self.on_floor and not keys[pygame.K_UP]:
				sprite = sprites_that_were_colliding[0]
				rect = sprite.hitbox if hasattr(sprite, 'hitbox') else sprite.rect
				self.attach_floor(rect)

	def move(self, dt):
		speed = self.swim_speed if self.on_water else self.speed

		# horizontal
		self.pos.x += speed * self.direction.x * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx

		self.collision('horizontal')

		# vertical
		self.pos.y += speed * self.direction.y * dt 
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery

		self.collision('vertical')

	def collision(self, direction):
		for sprite in self.collision_sprites:
			if hasattr(sprite, 'hitbox'):
				old_rect = sprite.old_hitbox
				rect = sprite.hitbox
			else:
				old_rect = sprite.old_rect
				rect = sprite.rect

			if rect.colliderect(self.hitbox): # are colliding
				match direction:
					case 'horizontal':
						if self.old_hitbox.right <= old_rect.left:
							self.hitbox.right = rect.left
						elif self.old_hitbox.left >= old_rect.right:
							self.hitbox.left = rect.right

					case 'vertical':
						if self.old_hitbox.bottom <= old_rect.top:
							self.hitbox.bottom = rect.top
						elif self.old_hitbox.top >= old_rect.bottom:
							self.hitbox.top = rect.bottom

						self.direction.y = 0

				self.rect.center, self.pos = self.hitbox.center, vector(self.hitbox.center)

	def attach_floor(self, rect):
		self.hitbox.bottom = rect.top
		self.rect.center, self.pos = self.hitbox.center, vector(self.hitbox.center)

	def damage(self, amount=1):
		if not self.invulnerability_timer.active:
			self.invulnerability_timer.activate()
			self.direction.y = -1.5

			self.health -= amount
			self.check_death()

	def check_death(self):
		if self.health <= 0:
			self.kill()

	def blink(self):
		if self.invulnerability_timer.active:
			if sin(pygame.time.get_ticks()) > 0:
				self.image = self.mask.to_surface()
				self.image.set_colorkey('black')

	def update_state(self, keys):

		if self.direction.x > 0:
			self.state = self.state.split('_')[0] + '_right'
		elif self.direction.x < 0:
			self.state = self.state.split('_')[0] + '_left'
		else:
			self.state = self.state.split('_')[0] + '_' + self.last_state.split('_')[1]

		if self.on_floor:
			if self.direction.x != 0:
				self.state = 'run' + '_' + self.state.split('_')[1]
			else:
				self.state = 'idle' + '_' +  self.state.split('_')[1]

		elif self.on_water:
			self.state = 'swim' + '_' + self.state.split('_')[1]

			if keys[pygame.K_DOWN] and self.direction.y > 0:
				self.state = self.state.split('_')[0] + '_down'

		else:
			if self.direction.y <= 0:
				self.state = 'jump' + '_' + self.state.split('_')[1]
			else:
				self.state = 'fall' + '_' + self.state.split('_')[1]


		if 'run' in self.state:
			self.animation_speed = 2 * ANIMATION_SPEED

		elif 'swim' in self.state and keys[pygame.K_UP]:
			self.animation_speed = 2 * ANIMATION_SPEED
		else:
			self.animation_speed = ANIMATION_SPEED

	def update(self, dt):
		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		keys = self.input()

		self.check_on_water()
		self.apply_gravity(dt, keys)
		self.move(dt)
		self.check_on_floor(keys)
		self.head_rect.midtop = self.hitbox.midtop
		self.hat_rect.midtop = self.hitbox.midtop

		if not 'down' in self.state:
			self.last_state = self.state

		self.update_state(keys)
		self.animate(dt)
		self.mask = pygame.mask.from_surface(self.image)
		self.blink()

		self.invulnerability_timer.update()


class Flag(Animated):
	def __init__(self, assets, pos, groups):
		super().__init__(assets, pos, groups)

		self.hitbox = self.rect.inflate(-57, -33)
		self.hitbox.bottomleft = self.rect.bottomleft
