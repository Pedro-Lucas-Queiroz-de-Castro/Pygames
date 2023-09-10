import pygame

from support import *

from entity import Entity
from random import randint, choice

from time_handling import *


class Monster(Entity):
	def __init__(self, groups, animations, pos, collision_sprites, player):
		super().__init__(groups, animations, pos, collision_sprites)

		self.z = 5

		self.health = 100
		self.dying = False
		self.dead = False

		self.attack_power = 1
		self.knockback_power = 0

		self.player = player

		self.vector_to_player = pygame.math.Vector2(self.player.hitbox.center) - pygame.math.Vector2(self.hitbox.center)

		self.invulnerability_cooldown = Cooldown(1200)
		self.blink_wave = TimeWave(1200//16) # cooldown // 16

	def take_damage(self, amount):
		if not self.invulnerability_cooldown.on:
			self.health -= amount
			self.invulnerability_cooldown.start()

	def check_death(self):
		if self.health <= 0:
			self.dying = True


class FireWorm(Monster):
	def __init__(self, groups, animations, pos, collision_sprites, player, create_fireball):
		super().__init__(groups, animations, pos, collision_sprites, player)

		self.land_on_floor()

		# animation
		self.animation_speeds = {'idle': 10, 'walk': 10, 'attack': 10, 'get hit': 10, 'death': 5}

		# health
		self.health = 120

		# movement
		self.walk_idle_decision_milliseconds = 7000
		self.frenzy_walk_idle_decision_milliseconds = 500
		self.walk_idle_decision_cooldown = Cooldown(self.walk_idle_decision_milliseconds)
		self.idle_chance = choice([10,30,50,80])
		self.idling = True
		self.walking = False

		self.walk_speed = 450
		self.moving_frames = 0, 5 # excluding the last one

		# attack
		self.create_fireball = create_fireball

		self.attack_power = 0.5
		self.knockback_power = 800
		self.attacking = False
		self.attack_radius = 600

		self.attack_cooldown = Cooldown(3000)

		# damage
		self.invulnerability_cooldown = Cooldown(600)

		# nature
		self.frenzier = choice([True, False])

	def land_on_floor(self):
		beneath_rect = get_beneath_rect(self.hitbox,
			[sprite.rect for sprite in self.collision_sprites.sprites()])

		if beneath_rect:
			self.hitbox.bottom = beneath_rect.top

			self.rect.topleft = self.get_rect_topleft_from_hitbox()
			self.pos = pygame.math.Vector2(self.rect.topleft)

			self.on_floor = True

		else:
			self.kill()

	def update_vector_to_player(self):
		self.vector_to_player = pygame.math.Vector2(self.hitbox.center) - pygame.math.Vector2(self.player.hitbox.center)

	def check_radius(self):
		distance = self.vector_to_player.magnitude()
		
		if distance <= self.attack_radius:
			attack = (self.animation_direction == 'right' and self.vector_to_player.x <= 0)\
			 or (self.animation_direction == 'left' and self.vector_to_player.x >= 0)\
			  if self.player.noise_degree <= 50 else True
			
			if attack:
				player_top_below = self.player.hitbox.top >= self.hitbox.top
				player_bottom_above = self.player.hitbox.bottom <= self.hitbox.bottom

				if player_top_below and player_bottom_above:
					self.attack()

	def frenzy_mode(self):
		self.walk_idle_decision_cooldown.milliseconds = self.frenzy_walk_idle_decision_milliseconds\
		if self.attack_cooldown.on else self.walk_idle_decision_milliseconds

	def attack(self):
		if self.vector_to_player.x < 0:
			self.animation_direction = 'right'
		elif self.vector_to_player.x > 0:
			self.animation_direction = 'left'

		if not self.attack_cooldown.on:
			self.attacking = True
			self.direction.x = 0

	def launch_fireball(self):	
		if self.attacking and self.last_frame_index <= 10 and self.frame_index >= 10:
			offsetx = 10 if self.animation_direction == 'right' else -10
			offsety = -10
			x = self.hitbox.right if self.animation_direction == 'right' else self.hitbox.left
			y = self.hitbox.centery
			pos = (x+offsetx,y+offsety)
			direction = self.animation_direction
			self.create_fireball(pos, direction)

	def finish_attack(self):
		self.attacking = False
		self.attack_cooldown.start()

	def finish_death(self):
		self.dying = False
		self.dead = True

	def finish_actions(self):
		if self.dying and self.frame_index_reset:
			self.finish_death()
		elif self.attacking and self.frame_index_reset:
			self.finish_attack()

	def remove_from_groups_when_dying(self):
		if self.dying:
			self.groups['damage'].remove(self)
			self.groups['attackable'].remove(self)

	def decide_to_walk_or_idle(self):
		decide = True if self.frenzier else not self.attack_cooldown.on
		if decide:
			if not self.walk_idle_decision_cooldown.on and not self.attacking:
				self.idling = randint(1,100) > 100 - self.idle_chance
				self.walking = not self.idling

				if self.idling:
					self.direction.x = 0
				else:
					self.direction.x = choice([-1,1])

				self.walk_idle_decision_cooldown.start()
		else:
			self.idling = True
			self.walking = not self.idling
			self.direction.x = 0

	def walk(self, dt):	
		if self.walking and self.moving_frames[0] <= self.frame_index < self.moving_frames[1]:
			self.pos.x += self.walk_speed * dt * self.direction.x
			self.rect.x = round(self.pos.x)
			self.hitbox.topleft = self.get_hitbox_topleft()

	def update_animation(self):
		# DIRECTION
		if self.direction.x < 0:
			self.animation_direction = 'left'
		elif self.direction.x > 0:
			self.animation_direction = 'right'

		# STATE
		if self.dying:
			self.animation_state = 'death'
		elif self.attacking:
			self.animation_state = 'attack'
		elif self.idling:
			self.animation_state = 'idle'
		elif self.walking:
			self.animation_state = 'walk'

	def allcollisions(self):
		self.horizontal_collision()
		self.check_wall_floor()

		self.check_nocliff_wallcolliding()

	def last_variables(self):
		self.last_image = self.image

		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.last_animation_state = self.animation_state

		self.was_idling = self.idling

		self.last_frame_index = self.frame_index

	def update_timers(self):
		self.walk_idle_decision_cooldown.update()
		self.attack_cooldown.update()
		self.invulnerability_cooldown.update()
		self.blink_wave.run()

	def update(self, dt):
		if not self.dead:
			self.last_variables()
			self.update_timers()

			self.check_death()
			self.remove_from_groups_when_dying()

			self.update_vector_to_player()
			self.check_radius()

			self.frenzy_mode()
			self.decide_to_walk_or_idle()
			self.walk(dt)

			self.allcollisions()

			self.update_animation()
			self.update_frame_index(dt, self.animation_speeds[self.animation_state])
			self.finish_actions()

			if not self.dead:
				self.animate()
				self.blink()

				self.launch_fireball()

				if self.update_mask_hitbox():
					self.allcollisions()