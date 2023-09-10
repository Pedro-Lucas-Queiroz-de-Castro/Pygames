import pygame
from entity import Entity
from pygame.math import Vector2 as Vector

class Monster:
	def get_player_distance_direction(self):
		distance = (self.player.pos-self.pos).magnitude()
		if distance != 0:
			direction = (self.player.pos-self.pos).normalize()
		else:
			direction = Vector(0,0)

		return distance, direction

	def face_player(self, distance, direction):
		if distance < self.notice_radius:
			if -0.7 <= direction.y <= 0.7:
				if direction.x < 0: # player to the left
					self.state = 'left_idle'
				elif direction.x > 0: # player to the right
					self.state = 'right_idle'
			else:
				if direction.y < 0: # player to the top
					self.state = 'up_idle'
				elif direction.y > 0:
					self.state = 'down_idle'

	def walk_to_player(self, distance, direction):
		if self.attack_radius < distance <= self.walk_radius:
			self.direction = direction
			self.state = self.state.split('_')[0]
		else:
			self.direction.x = 0
			self.direction.y = 0

	def attack_player(self, distance, direction):
		if distance <= self.attack_radius and self.player.health > 0:
			self.attacking = True
			self.frame_index = 0
			self.state = self.state.split('_')[0]+'_attack'


class Coffin(Entity, Monster):
	def __init__(self, name, pos, groups, animations, collision_objects,
		player, entity_sprites):
		super().__init__(name, pos, groups, animations, collision_objects)

		# OVERWRITES
		# movement
		self.speed = 250

		# health
		self.health = 160

		# SPECIFICS
		# player interaction
		self.player = player
		self.notice_radius = 600
		self.walk_radius = 550
		self.attack_radius = 100

		# attack
		self.attack_power = 30
		self.entity_sprites = entity_sprites

		# collision
		self.rect = self.rect.inflate(0, -self.rect.height*0.2)
		self.hitbox = self.rect.inflate(-self.rect.width*0.7, -self.rect.height*0.6)
		self.hitbox.bottom = self.rect.bottom

	def shovelzada(self):
		if self.attacking and int(self.frame_index) == 4:
			for entity in self.entity_sprites.sprites():
				distance = (entity.pos-self.pos).magnitude()
				if distance < self.attack_radius:
					if entity != self:
						entity.get_damage(self.attack_power)

	def update(self, dt):
		distance, direction = self.get_player_distance_direction()
		if not self.attacking:
			self.face_player(distance, direction)
			self.walk_to_player(distance, direction)
			self.attack_player(distance, direction)
		self.move(dt)
		self.update_overlap(self.overlap_value)
		self.animate(dt)
		self.shovelzada()
		self.vulnerability_timer()
		self.blink()


class Cactus(Entity, Monster):
	def __init__(self, name, pos, groups, animations, collision_objects, create_bullet,
		player):
		super().__init__(name, pos, groups, animations, collision_objects)

		# OVERWRITES
		# movement
		self.speed = 150

		# health
		self.health = 90

		# SPECIFICS
		# player interaction
		self.player = player
		self.notice_radius = 800
		self.walk_radius = 600
		self.attack_radius = 550

		# shot
		self.shooting = False
		self.create_bullet = create_bullet

		# attack
		self.attack_power = 10

		# collision
		self.hitbox = self.rect.inflate(-self.rect.width*0.5, -self.rect.height*0.5)
		self.hitbox.bottom = self.rect.bottom

	def shoot(self):
		if int(self.frame_index) == 6:
			match self.state.split('_')[0]:
				case 'left': 
					offsetx, offsety = -60, 3
			# 		x, y = -1, 0
				case 'right': 
					offsetx, offsety = 60, 3
			# 		x, y = 1, 0
				case 'up': 
					offsetx, offsety = 20, -60
			# 		x, y = 0, -1
				case 'down': 
					offsetx, offsety = -20, 60
			# 		x, y = 0, 1

			# self.bullet_direction = Vector(x,y)

			bullet_center_pos = (self.rect.centerx+offsetx,
									  self.rect.centery+offsety)
			bullet_direction = self.get_player_distance_direction()[1]

			self.create_bullet(bullet_center_pos, bullet_direction, self, 700)
			self.shooting = True

	def update(self, dt):
		distance, direction = self.get_player_distance_direction()

		if not self.attacking:
			self.face_player(distance, direction)
			self.walk_to_player(distance, direction)
			self.attack_player(distance, direction)
		elif not self.shooting:
			self.shoot()

		self.move(dt)
		self.update_overlap(self.overlap_value)
		self.animate(dt, lambda: setattr(self, 'shooting', False))
		self.vulnerability_timer()
		self.blink()


class Cat(Entity, Monster):
	def __init__(self, name, pos, groups, animations, collision_objects,
		player, entity_sprites):
		super().__init__(name, pos, groups, animations, collision_objects)

		self.speed = 100
		self.health = 1000

		# player interaction
		self.player = player
		self.notice_radius = 600
		self.walk_radius = 400
		self.attack_radius = 70

		self.attack_power = 8
		self.entity_sprites = entity_sprites

	def axe_attack(self):
		if int(self.frame_index) == 1:
			for entity in self.entity_sprites.sprites():
				distance = (entity.pos-self.pos).magnitude()
				if distance < self.attack_radius:
					if entity != self:
						entity.get_damage(self.attack_power)

	def update(self, dt):
		distance, direction = self.get_player_distance_direction()
		if not self.attacking:
			self.face_player(distance, direction)
			self.walk_to_player(distance, direction)
			self.attack_player(distance, direction)
		else:
			self.axe_attack()

		self.move(dt)
		self.update_overlap(self.overlap_value)
		self.animate(dt)
		self.vulnerability_timer()
		self.blink()