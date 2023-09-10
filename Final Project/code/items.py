import pygame

from random import choice

from superclasses import *
from settings import *
from times import *
from support import *


class Item(Animated,Collisor,Sprite):
	def __init__(self, name, action, idling_hand_animation_state, acting_hand_animation_state,
		anchors, level, pos, animations, animations_speeds, frames_default_sizes, groups,
		hand_actions_magnitudes, hand_actions_animations_speeds):

		self.z = z=Z_AXIS['item']

		self.name = name
		self.action = action
		self.idling_hand_animation_state = idling_hand_animation_state
		self.acting_hand_animation_state = acting_hand_animation_state

		self.anchors = anchors

		self.hand_actions_magnitudes = hand_actions_magnitudes
		self.hand_actions_animations_speeds = hand_actions_animations_speeds

		self.level = level
		self.hand = None

		self.my_groups = groups

		animation_keys = {}
		animation_keys['direction'] = choice(['right','left'])
		animation_keys['state'] = list(animations[animation_keys['direction']].keys())[0]

		super().__init__(
			animations=animations,
			animation_keys=animation_keys,
			animations_speeds=animations_speeds,
			frames_default_sizes=frames_default_sizes,
			scale_offset=self.level.scale_offset,
			collidable_group=groups['collidable'],
			groups=[groups['updatable'],groups['visible'],groups['pickable']])

		self.rect = self.image.get_rect(**pos)
		self.hitbox = self.rect.copy()

		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.create_collision_rects()

		self.set_speed_forces()

		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.direction = pygame.math.Vector2()

		self.max_direction_falling_speed = 600

	def get_hitbox_by_rect(self):
		self.hitbox = self.rect.copy()

	def set_speed_forces(self):
		forces = self.level.speed_forces
		self.gravity_speed = forces['gravity']
		self.wind_direction = forces['wind_direction']

	def apply_gravity(self, dt):
		self.direction.y += self.gravity_speed * dt

	def move_vertical(self, dt):
		wind_direction = pygame.math.Vector2() if self.on_floor else self.wind_direction

		self.direction.y = min(self.direction.y,self.max_direction_falling_speed)
		self.pos.y += ((self.direction.y + wind_direction.y) * dt * self.scale_offset)
		self.rect.y = round(self.pos.y)

		self.get_hitbox_by_rect()

	def move_horizontal(self, dt):
		wind_direction = self.wind_direction

		if (self.on_wall['left'] and self.wind_direction.x < 0) or\
		   (self.on_wall['right'] and self.wind_direction.x > 0):
		   wind_direction = pygame.math.Vector2()

		self.pos.x += wind_direction.x * dt
		self.rect.x = round(self.pos.x)

		self.get_hitbox_by_rect()

	def follow_hand(self):
		direction = self.animation_keys['direction']
		apply_anchor(
			set_rect=self.rect,
			get_rect=self.hand.rect,
			anchor=self.anchors[direction],
			scale_offset=self.level.scale_offset)

		self.get_hitbox_by_rect()

	def pick(self, hand):
		self.hand = hand
		self.animation_keys['direction'] = hand.side

	def previous_variables(self):
		self.last_animation_state = self.animation_keys['state']

	def update(self, dt):
		self.previous_variables()

		if self.hand:
			self.follow_hand()
		else:
			self.move_horizontal(dt)
			self.collisions('horizontal')

			self.apply_gravity(dt)
			self.move_vertical(dt)
			self.collisions('vertical')

		self.update_frame_index(dt)
		self.animate()

	def switch(self):
		self.animation_keys['direction'] = self.hand.animation_keys['direction']
		

class Hammer(Item):
	def __init__(self, name, action, idling_hand_animation_state, acting_hand_animation_state,
		anchors, level, pos, animations, animations_speeds, frames_default_sizes, groups,
		hand_actions_magnitudes={}, hand_actions_animations_speeds={}):
		super().__init__(name, action, idling_hand_animation_state, acting_hand_animation_state,
		anchors, level, pos, animations, animations_speeds, frames_default_sizes, groups,
		hand_actions_magnitudes, hand_actions_animations_speeds)

	def use(self):
		pass


class Gun(Item):
	def __init__(self, name, action, idling_hand_animation_state, acting_hand_animation_state, anchors,
		projectile_parameters, level, pos, animations, animations_speeds, frames_default_sizes, groups,
		hand_actions_magnitudes={}, hand_actions_animations_speeds={}):
		super().__init__(name, action, idling_hand_animation_state, acting_hand_animation_state,
		anchors, level, pos, animations, animations_speeds, frames_default_sizes, groups,
		hand_actions_magnitudes, hand_actions_animations_speeds)

		self.projectile_parameters = projectile_parameters
 
	def use(self):
		self.shoot()
		
	def shoot(self):
		match self.animation_keys['direction']:
			case 'right':
				direction = pygame.math.Vector2(1,0)
			case 'left':
				direction = pygame.math.Vector2(-1,0)

		self.projectile_parameters['class'](
			**self.projectile_parameters['unpackable'],
			scale_offset=self.level.scale_offset,
			animation_keys={'direction': self.animation_keys['direction'], 'state': 'move'},
			groups=self.my_groups,
			vector_direction=direction,
			shooter_item=self)


class Projectile(Animated, Collisor, Sprite):
	def __init__(self, name, animations, animation_keys, animations_speeds, frames_default_sizes,
		scale_offset, groups, anchors, destruction_anchors, vector_direction, speed,
		on_contact_damage_amount, destruction_damage_amount, on_contact_damage_frames,
		destruction_damage_frames, shooter_item, drilling_potential):
		super().__init__(
			animations=animations,
			animation_keys=animation_keys,
			animations_speeds=animations_speeds,
			frames_default_sizes=frames_default_sizes,
			scale_offset=scale_offset,
			collidable_group=groups['collidable'],
			groups=[groups['updatable'],groups['visible']])

		self.z = Z_AXIS['projectile']
		self.name = name

		self.my_groups = groups

		self.shooter_item = shooter_item
		self.in_shooter_item = True
		# self.shooter_item_horizontal_boundaries_points = {
		# 'left': get_points_between(shooter_item.hitbox.topleft,shooter_item.hitbox.bottomleft), 
		# 'right': get_points_between(shooter_item.hitbox.topright,shooter_item.hitbox.bottomright)}
		self.shooter_item_when_shot_hitbox = shooter_item.hitbox.copy()

		self.anchors = anchors
		self.destruction_anchors = destruction_anchors

		self.rect = self.image.get_rect()
		self.set_start_pos()
		self.get_hitbox()

		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.create_collision_rects()

		self.initial_direction = vector_direction.normalize()
		self.direction = self.initial_direction
		self.speed = speed

		self.pos = pygame.math.Vector2(self.rect.topleft)

		self.on_contact_damage_amount = on_contact_damage_amount
		self.destruction_damage_amount = destruction_damage_amount
		self.on_contact_damage_frames = on_contact_damage_frames
		self.destruction_damage_frames = destruction_damage_frames

		self.drilling_number = 0
		self.drilling_potential = drilling_potential

		self.being_destroyed = False

		self.set_speed_forces()

	def set_speed_forces(self):
		forces = self.shooter_item.level.speed_forces
		self.gravity_speed = forces['gravity']
		self.wind_direction = forces['wind_direction']

	def set_start_pos(self):
		direction = self.animation_keys['direction']
		apply_anchor(
			set_rect=self.rect,
			get_rect=self.shooter_item.rect,
			anchor=self.anchors[direction],
			scale_offset=self.scale_offset)

	def get_hitbox(self):
		self.hitbox = self.rect.copy()

	def move(self, dt):
		wind_direction = pygame.math.Vector2(self.wind_direction.x,0)

		self.pos += (self.direction*self.speed+wind_direction) * dt * self.scale_offset
		self.rect.x = round(self.pos.x)
		self.rect.y = round(self.pos.y)

		self.get_hitbox()

	def other_collisions(self):
		for sprite in self.my_groups['collidable']:
			if sprite.hitbox.colliderect(self.hitbox):
				self.being_destroyed = True

	def check_drilling(self):
		if self.drilling_potential != -1:
			if self.drilling_number > self.drilling_potential:
				self.being_destroyed = True

	def update_animation_state(self):
		if self.being_destroyed:
			self.animation_keys['state'] = 'destroy'
		else:
			self.animation_keys['state'] = 'move'

	def update_rect(self):
		direction = self.animation_keys['direction']

		get_rect = self.rect.copy()
		self.rect = self.image.get_rect()

		apply_anchor(
			set_rect=self.rect,
			get_rect=get_rect,
			anchor=self.destruction_anchors[direction],
			scale_offset=self.scale_offset)

		self.pos.x, self.pos.y = self.rect.x, self.rect.y
		self.get_hitbox()

	def update_damaging(self):
		index = int(self.frame_index)
		remove = False
		add = False

		if self.being_destroyed:
			if self.destruction_damage_amount == None or self.destruction_damage_frames == None:
				remove = True
			elif self.destruction_damage_frames == 'all':
				add = True
			else:
				if index in self.destruction_damage_frames:
					add = True
				else:
					remove = True
		else:
			if self.on_contact_damage_amount == None or self.on_contact_damage_frames == None:
				remove = True
			elif self.on_contact_damage_frames == 'all':
				add = True
			else:
				if index in self.on_contact_damage_frames:
					add = True
				else:
					remove = True

		if add:
			if not self in self.my_groups['damaging'].sprites():
				self.my_groups['damaging'].add(self)

		if remove:
			if self in self.my_groups['damaging'].sprites():
				self.my_groups['damaging'].remove(self)

	def get_damage_amount(self):
		if self.being_destroyed:
			damage_amount = self.destruction_damage_amount
		else:
			damage_amount = self.on_contact_damage_amount

		return damage_amount

	def check_in_shooter_item(self):
		if self.in_shooter_item:
			# print('='*100)
			# print(self.initial_direction.x, self.pos.x, self.last_pos.x)
			# print('='*100)
			if not self.hitbox.colliderect(self.shooter_item_when_shot_hitbox) or\
			not self.shooter_item.hand.player.hitbox.colliderect(self.shooter_item_when_shot_hitbox) or\
			((self.initial_direction.x > 0 and self.pos.x < self.last_pos.x) or\
			 (self.initial_direction.x < 0 and self.pos.x > self.last_pos.x)):
				self.in_shooter_item = False

	def previous_variables(self):
		self.last_animation_state = self.animation_keys['state']
		self.last_pos = self.pos.copy()

		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.was_being_destroyed = self.being_destroyed

	def update(self, dt):
		self.previous_variables()

		if not self.being_destroyed:
			self.move(dt)
			self.check_in_shooter_item()

			self.other_collisions()
			self.check_drilling()

			self.update_animation_state()

		if self.being_destroyed and not self.was_being_destroyed:
			self.frame_index = 0
			self.animate()

			self.collisions('horizontal')
			self.update_rect()

		reseted = self.update_frame_index(dt)
		if reseted and self.being_destroyed:
			self.kill()

		if self in self.my_groups['updatable']:
			self.animate()

			self.update_damaging()


class SelfConsumableProjectile(AlphaFade, Projectile):
	def __init__(self, name, animations, animation_keys, animations_speeds, frames_default_sizes,
		scale_offset, groups, anchors, destruction_anchors, vector_direction, speed,
		on_contact_damage_amount, destruction_damage_amount, on_contact_damage_frames,
		destruction_damage_frames, shooter_item, drilling_potential,
		consumption_speed, consumable_energy, fade_speed, start_fade=255, end_fade=0):

		super().__init__(fade_speed, start_fade, end_fade,
		name, animations, animation_keys, animations_speeds, frames_default_sizes,
		scale_offset, groups, anchors, destruction_anchors, vector_direction, speed,
		on_contact_damage_amount, destruction_damage_amount, on_contact_damage_frames,
		destruction_damage_frames, shooter_item, drilling_potential)

		self.consumption_speed = consumption_speed
		self.consumable_energy = consumable_energy

		self.fade_on = True if fade_speed else False

	def consume(self, dt):
		self.consumable_energy -= self.consumption_speed * dt

		if self.consumable_energy <= 0:
			self.kill()


	def update(self, dt):
		self.previous_variables()

		if not self.being_destroyed:
			self.move(dt)
			self.check_in_shooter_item()

			self.other_collisions()
			self.check_drilling()

			self.update_animation_state()

		if self.being_destroyed and not self.was_being_destroyed:
			self.frame_index = 0
			self.animate()

			self.collisions('horizontal')
			self.update_rect()

		reseted = self.update_frame_index(dt)
		if reseted and self.being_destroyed:
			self.kill()

		if self in self.my_groups['updatable']:
			self.animate()
			if self.fade_on:
				self.fade(dt)
				self.fade_image(self.image)

			self.update_damaging()

			self.consume(dt)




