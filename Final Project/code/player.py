import pygame

from support import *
from settings import *
from times import *
from vector_actions import *
from items_data import *
from items import *

from superclasses import *

class Player(Animated,Collisor,Sprite):
	def __init__(self, level, pos, animations, animations_speeds, 
		joystick, groups, control_config, hand_animations):
		self.z = Z_AXIS['player']

		self.level = level

		animation_keys = {}
		animation_keys['direction'] = 'right'
		animation_keys['state'] = 'idle'

		super().__init__(
			animations=animations,
			animation_keys=animation_keys,
			animations_speeds=animations_speeds,
			frames_default_sizes=PLAYER_DEFAULT_SIZES,
			scale_offset=self.level.scale_offset,
			collidable_group=groups['collidable'],
			groups=[groups['updatable'],groups['visible'],groups['damageable']])

		self.set_speed_forces()

		self.my_groups = groups

		self.control_config = control_config

		self.source_animations = get_direction_state_animations_copy(animations)
		self.source_hand_animations = get_direction_state_animations_copy(hand_animations)

		self.hand_animations = get_direction_state_animations_copy(hand_animations)

		self.image = self.get_animation()[self.frame_index]
		self.rect = self.image.get_rect(**pos)
		self.hitbox = self.rect.copy()

		self.create_collision_rects()

		self.cooldowns = {}
		self.cooldowns['invulnerability'] = Cooldown(PLAYER_COOLDOWNS_MILLISECONDS['invulnerability'])
		self.cooldowns['switch'] = Cooldown(PLAYER_COOLDOWNS_MILLISECONDS['switch'])

		self.joystick = joystick

		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(list(pos.values())[0])
		self.walk_speed = 350

		self.jump_speed = 750
		self.max_direction_falling_speed = 900
		self.player_falling_animation_change_speeds = PLAYER_FALLING_ANIMATION_CHANGE_SPEEDS

		# health
		self.health = PLAYER_START_HEALTH

		# hands
		self.hands = {}
		self.create_hands()


		self.animation_direction_locked = False

	def set_speed_forces(self):
		forces = self.level.speed_forces
		self.gravity_speed = forces['gravity']
		self.wind_direction = forces['wind_direction']
		self.input_acceleration_speed_on_floor = forces['input_acceleration_speed_on_floor']
		self.input_deacceleration_speed_on_floor = forces['input_deacceleration_speed_on_floor']
		self.input_acceleration_speed_in_air = forces['input_acceleration_speed_in_air']
		self.input_deacceleration_speed_in_air = forces['input_deacceleration_speed_in_air']


	def create_hands(self):
		self.hands['right'] = Hand(
			side='right',
			animations=self.hand_animations,
			animation_keys={'direction': 'right', 'state': 'idle'},
			animations_speeds=HAND_ANIMATIONS_SPEEDS,
			pos={'midleft': self.rect.midright},
			groups=self.my_groups,
			player=self,
			anchor=('midleft','midright',
				(RIGHT_HAND_ANCHOR_OFFSET[0]*self.scale_offset,
				 RIGHT_HAND_ANCHOR_OFFSET[1]*self.scale_offset)))

		self.hands['left'] = Hand(
			side='left',
			animations=self.hand_animations,
			animation_keys={'direction': 'left', 'state': 'idle'},
			animations_speeds=HAND_ANIMATIONS_SPEEDS,
			pos={'midright': self.rect.midleft},
			groups=self.my_groups,
			player=self,
			anchor=('midright','midleft',
				(LEFT_HAND_ANCHOR_OFFSET[0]*self.scale_offset,
				 LEFT_HAND_ANCHOR_OFFSET[1]*self.scale_offset)))

	def check_damage(self):
		if not self.cooldowns['invulnerability'].on:
			for sprite in self.my_groups['damaging']:
				
				get_damage = False

				if sprite.hitbox.colliderect(self.hitbox):
					if isinstance(sprite, Hand):
						if sprite.player != self:
							get_damage = True

					elif isinstance(sprite, Projectile):
						if not sprite.in_shooter_item or sprite.being_destroyed:
							sprite.drilling_number += 1
							get_damage = True


				if get_damage:
					self.get_damage(sprite.get_damage_amount())


	def get_damage(self, amount):	
		self.health -= amount
		self.check_death()

		self.cooldowns['invulnerability'].start()


	def blink(self):
		if self.cooldowns['invulnerability'].on:
			if sin_wave(pygame.time.get_ticks()) >= 0:
				self.image = alphafill(self.image, GET_DAMAGE_BLIKING_COLOR)
				self.blinking = 1
			else:
				self.blinking = 0
		else:
			self.blinking = 0

	def check_death(self):
		if self.health <= 0:
			self.kill()
			for hand in self.hands.values():
				hand.kill()


	def get_controls(self):
		controls = {}
		components = get_joystick_components(self.joystick) if self.joystick else {}

		for action, controlkey in self.control_config.items():
			list_ = []
			if '|' in controlkey:
				for key in controlkey.split('|'):
					if key in components:
						list_.append(components[key])
					else:
						list_.append(None)
				controls[action] = any(list_)

			elif '+' in controlkey:
				for key in controlkey.split('+'):
					if key in components:
						list_.append(components[key])
					else:
						list_.append(None)
				controls[action] = list_

			elif '&' in controlkey:
				for key in controlkey.split('&'):
					if key in components:
						list_.append(components[key])
					else:
						list_.append(None)
				
				controls[action] = all(list_)

			else:
				controls[action] = components[controlkey] if controlkey in components else False


		self.components = components
		self.controls = controls

	def input(self, dt):
		if self.controls:
			# horizontal movement
			if 'hlaxis' in self.components:
				left_axis = self.controls['move'][0] < -DEADZONE
				right_axis = self.controls['move'][0] > DEADZONE
			else:
				left_axis = False
				right_axis = False

			if 'lhat' in self.components:
				left_hat = self.controls['move'][1][0] < 0
				right_hat = self.controls['move'][1][0] > 0
			else:
				left_hat = False
				right_hat = False

			if self.on_floor:
				input_acceleration_speed = self.input_acceleration_speed_on_floor * dt
				input_deacceleration_speed = self.input_deacceleration_speed_on_floor * dt
			else:
				input_acceleration_speed = self.input_acceleration_speed_in_air * dt
				input_deacceleration_speed = self.input_deacceleration_speed_in_air * dt

			if left_axis or left_hat:
				speed = input_acceleration_speed + input_deacceleration_speed\
				if self.direction.x <= 0 else input_deacceleration_speed

				self.direction.x = tend_to(self.direction.x, -self.walk_speed, speed)
				self.walking_input = -1

			elif right_axis or right_hat:
				speed = input_acceleration_speed + input_deacceleration_speed\
				if self.direction.x >= 0 else input_deacceleration_speed

				self.direction.x = tend_to(self.direction.x, self.walk_speed, speed)
				self.walking_input = 1

			else:
				self.direction.x = tend_to(self.direction.x, 0, input_deacceleration_speed)

				self.walking_input = 0

			# jump
			if self.controls['jump']:
				self.jump()

			# hand actions
			if not self.level.lobby:	
				if self.controls['right pick']:
					self.hands['right'].pick()
				elif self.controls['right action']:
					self.hands['right'].use_item() 

				if self.controls['left pick']:
					self.hands['left'].pick()
				elif self.controls['left action']:
					self.hands['left'].use_item()

				if self.controls['switch']:
					if not self.cooldowns['switch'].on:
						self.hands['left'].item, self.hands['right'].item =\
						self.hands['right'].item, self.hands['left'].item

						for hand in self.hands.values():
							hand.switch()

						self.cooldowns['switch'].start()

				if self.controls['pull/push']:
					self.hands['right'].pull_push()
					self.hands['left'].pull_push()

	def jump(self):
		if self.on_floor:
			self.direction.y = -self.jump_speed

	def apply_gravity(self, dt):
		self.direction.y += self.gravity_speed * dt

	def move_vertical(self, dt):
		wind_direction = pygame.math.Vector2() if self.on_floor else self.wind_direction

		self.direction.y = min(self.direction.y,self.max_direction_falling_speed)
		self.pos.y += ((self.direction.y + wind_direction.y) * dt * self.scale_offset)
		self.rect.y = round(self.pos.y)

		self.hitbox.y = self.rect.y


	def move_horizontal(self, dt):
		wind_direction = self.wind_direction

		if (self.on_wall['left'] and self.wind_direction.x < 0) or\
		   (self.on_wall['right'] and self.wind_direction.x > 0):
		   wind_direction = pygame.math.Vector2()

		self.pos.x += ((self.direction.x + wind_direction.x) * dt * self.scale_offset)
		self.rect.x = round(self.pos.x)

		self.hitbox.x = self.rect.x


	def collisions(self, direction):
		sprites_on_floor = []
		sprites_on_wall = {'left': [], 'right': []}

		for sprite in self.collidable_group:
			if not sprite in [h.holding_object for h in self.hands.values()]:
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



	def update_animation_direction(self):
		if not self.animation_direction_locked:
			if self.walking_input > 0:
				self.animation_keys['direction'] = 'right'
			elif self.walking_input < 0:
				self.animation_keys['direction'] = 'left'

	def update_animation_state(self):
		wind_direction = pygame.math.Vector2() if self.on_floor else self.wind_direction

		if self.on_floor:
			if self.walking_input != 0:
				self.animation_keys['state'] = 'walk'
			else:
				self.animation_keys['state'] = 'idle'
		else:
			if self.direction.y <= 0:
				self.animation_keys['state'] = 'rising'
			else:
				if self.direction.y + wind_direction.y <= self.player_falling_animation_change_speeds[0]:
					self.animation_keys['state'] = 'falling 0'
				elif self.direction.y + wind_direction.y <= self.player_falling_animation_change_speeds[1]:
					self.animation_keys['state'] = 'falling 1'
				elif self.direction.y + wind_direction.y <= self.player_falling_animation_change_speeds[2]:
					self.animation_keys['state'] = 'falling 2'
				else:
					self.animation_keys['state'] = 'falling 3'


	def previous_variables(self):
		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.last_frame_index = self.frame_index
		self.last_animation_state = self.animation_keys['state']

	def update_cooldowns(self):
		for cooldown_dict in self.cooldowns.values():
			if isinstance(cooldown_dict, dict):
				for cooldown in cooldown_dict.values():
					cooldown.update()
			else:
				cooldown_dict.update()

	def update(self, dt):
		self.previous_variables()
		self.update_cooldowns()

		self.get_controls()

		self.input(dt)

		# if self.direction.magnitude() != 0:
		# 	self.direction.normalize_ip()

		self.move_horizontal(dt)
		self.collisions('horizontal')
		
		self.apply_gravity(dt)
		self.move_vertical(dt)
		self.collisions('vertical')

		self.check_damage()

		self.update_animation_direction()
		self.update_animation_state()
		reseted = self.update_frame_index(dt)

		self.animate()
		self.blink()


	def get_display_info(self, key):
		self.info = {
		'on floor': f'on floor: {self.on_floor}',
		'on wall': f'on wall: l-{self.on_wall["left"]}, r-{self.on_wall["right"]}',
		'direction': (self.direction.x, self.direction.y),
		'position': self.rect.topleft,
		'scale offset': f'scale offset: {self.scale_offset}',
		'damage sprites': f'damaging sprites: {len(self.my_groups["damaging"].sprites())}',
		'gravity speed': f'gravity speed: {self.gravity_speed}',
		'wind direction': f'wind direction: {self.wind_direction}',
		'left item': f'left item: {self.hands["left"].item.name if self.hands["left"].item else None}',
		'right item': f'right item: {self.hands["right"].item.name if self.hands["right"].item else None}',
		'health': f'health: {self.health}'}

		return self.info[key]

	def change_color(self, color):
		for animations in (self.animations,self.hand_animations,
			self.source_animations, self.source_hand_animations):
			for k1, sides in animations.items():
				for k2, frames in sides.items():
					animations[k1][k2] = [alphafill(surface, color) for surface in frames]

		for hand in self.hands.values():
			hand.animations = self.hand_animations

		# self.image = alphafill(self.image, color)


class Hand(Animated, Sprite):
	def __init__(self, side, animations, animation_keys, animations_speeds, pos, groups, player, anchor):
		super().__init__(
			animations=animations,
			animation_keys=animation_keys,
			animations_speeds=animations_speeds,
			frames_default_sizes=HAND_DEFAULT_SIZES,
			scale_offset=player.scale_offset,
			groups=[groups['visible'],groups['updatable']])

		self.z = Z_AXIS['hand']

		self.side = side
		self.my_groups = groups

		self.player = player

		self.image = self.get_animation()[self.frame_index]
		self.rect = self.image.get_rect(**pos)
		self.backup_rect = self.rect.copy()
		self.hitbox = self.rect.copy()

		self.anchor = anchor

		self.vector_animation_direction = 1 if self.animation_keys['direction'] == 'right' else -1

		self.vector_animations = HAND_VECTOR_ANIMATIONS
		self.vector_animation_state = list(self.vector_animations.keys())[0]

		self.vector_index = 0
		self.default_vector_magnitudes = DEFAULT_HAND_VECTOR_MAGNITUDES
		self.default_vector_animations_speeds = DEFAULT_HAND_VECTOR_ANIMATIONS_SPEEDS
		self.animation_vectors_sum = pygame.math.Vector2()

		# ITEMS
		self.item = None

		# ACTIONS
		self.actions = {}
		for action in HAND_ACTIONS:
			self.actions[action] = False

		self.normal_resetable_item_actions = NORMAL_RESETABLE_ITEM_ACTIONS
		self.stop_at_the_end_resetable_item_actions = STOP_AT_THE_END_RESETABLE_ITEM_ACTIONS

		self.normal_cooldown_items_use = NORMAL_COOLDOWN_ITEMS_USE

		self.holding_object = None

		# COOLDOWNS
		self.cooldowns = {}
		self.cooldowns['pick'] = Cooldown(250)
		self.cooldowns['punch'] = Cooldown(250)
		self.cooldowns['pull/push'] = Cooldown(250)

		for item_name, milliseconds in self.normal_cooldown_items_use.items():
			self.cooldowns[item_name] = Cooldown(milliseconds)

		self.scales = HAND_SCALES
		self.rotations = HAND_ROTATIONS

	def get_vector_animation(self):
		return self.vector_animations[self.vector_animation_state]

	def get_vector_magnitude(self):
		try:
			magnitude = self.item.hand_actions_magnitudes[self.vector_animation_state]
		except KeyError:
			magnitude = self.default_vector_magnitudes[self.vector_animation_state]
		except AttributeError:
			magnitude = self.default_vector_magnitudes[self.vector_animation_state]

		return magnitude*self.player.scale_offset

	def get_vector_animation_speed(self):
		try:
			speed = self.item.hand_actions_animations_speeds[self.vector_animation_state]
		except KeyError:
			speed = self.default_vector_animations_speeds[self.vector_animation_state]
		except AttributeError:
			speed = self.default_vector_animations_speeds[self.vector_animation_state]

		return speed

	def get_player_pos(self):
		return getattr(self.player.rect, self.anchor[1])


	def switch(self):
		if self.item:
			self.item.hand = self
			self.item.switch()

	def use_item(self):
		if self.item:
			if self.item.name in self.normal_cooldown_items_use.keys():
				if not self.cooldowns[self.item.name].on:
					self.actions[self.item.action] = True
					self.item.use()
					self.cooldowns[self.item.name].start()
			else:
				self.actions[self.item.action] = True
				self.item.use()
		else:
			if not self.cooldowns['punch'].on:
				self.actions['poke'] = True
				self.my_groups['damaging'].add(self)

	def pull_push(self):
		player_hitbox = self.player.hitbox.inflate(16*self.scale_offset,16*self.scale_offset)

		if not self.cooldowns['pull/push'].on:
			if not self.holding_object:
				for sprite in self.my_groups['mobile']:
					if sprite.hitbox.colliderect(player_hitbox):
						self.holding_object = sprite
						break

				if self.holding_object:
					self.holding_object.get_player(self)
					self.player.animation_direction_locked = True

				self.cooldowns['pull/push'].start()
				

	def pick(self):
		if not self.cooldowns['pick'].on:
			if not self.item:
				self.actions['pick'] = True

	def picking(self):
		if self.actions['pick'] and not self.item:
			for sprite in self.my_groups['pickable']:
				if sprite.hitbox.colliderect(self.hitbox):
					self.item = sprite
					self.item.pick(self)
					self.my_groups['pickable'].remove(self.item)
					break


	def update_vector_animation_state(self):
		item_action = self.actions[self.item.action] if self.item else None

		if self.actions['pick'] and not self.item:
			self.vector_animation_state = 'pick'

		elif item_action:
			self.vector_animation_state = self.item.action

		elif self.actions['poke']:
			self.vector_animation_state = 'poke'

		else:
			if self.player.walking_input != 0:
				self.vector_animation_state = 'walk'
			else:
				self.vector_animation_state = 'idle'

	def update_vector_index(self, dt):
		self.vector_index += self.get_vector_animation_speed() * dt

		if self.vector_animation_state != self.last_vector_animation_state:
			self.vector_index = 0
			self.animation_vectors_sum = pygame.math.Vector2()
		
		reseted = False
		if self.vector_index >= len(self.get_vector_animation()):
			if self.item:
				if self.actions[self.item.action]:
					if self.item.name in self.normal_resetable_item_actions: 
						self.vector_index = 0
						reseted = True
					elif self.item.name in self.stop_at_the_end_resetable_item_actions:
						self.vector_index = len(self.get_vector_animation())-1
						self.control_reset_actions()
				else:
					self.vector_index = 0
					reseted = True
			else:
				self.vector_index = 0
				reseted = True

		if reseted:
			self.reset_actions()

	def reset_actions(self):
		self.animation_vectors_sum = pygame.math.Vector2()

		item_action = self.actions[self.item.action] if self.item else None

		if self.actions['pick']:
			self.actions['pick'] = False
			self.cooldowns['pick'].start()

		elif item_action:
			self.actions[self.item.action] = False
			if self.item.name in self.normal_cooldown_items_use:
				self.cooldowns[self.item.name].start()

		elif self.actions['poke']:
			self.actions['poke'] = False
			self.my_groups['damaging'].remove(self)

			self.cooldowns['punch'].start()

	def control_reset_actions(self):
		if not self.player.controls[self.side+' action']:
			self.actions[self.item.action] = False


	def move(self, dt):
		player_anchor = pygame.math.Vector2(self.get_player_pos())+pygame.math.Vector2(self.anchor[2])

		magnitude = self.get_vector_magnitude()
		vector = self.get_vector_animation()[int(self.vector_index)].copy()
		vector.x = vector.x * self.vector_animation_direction
		vector = vector.normalize() if vector.magnitude() != 0 else vector

		self.animation_vectors_sum += vector * magnitude * dt 

		resultant_vector = player_anchor + self.animation_vectors_sum

		setattr(self.rect, self.anchor[0], resultant_vector)
		setattr(self.backup_rect, self.anchor[0], resultant_vector)

		self.adjust_positionals_objects_by_rect()

	def adjust_positionals_objects_by_rect(self):
		self.hitbox.topleft = self.rect.topleft

	def adjust_dimensionals_objects_by_rect(self):
		self.hitbox.width = self.rect.width
		self.hitbox.height = self.rect.height


	def get_damage_amount(self):
		damage = 1

		return damage


	def update_animation_state(self):
		item_action = self.actions[self.item.action] if self.item else None

		if self.actions['pick'] and not self.item:
			self.animation_keys['state'] = 'pick'

		elif item_action:
			self.animation_keys['state'] = self.item.acting_hand_animation_state
		elif self.actions['poke']:
			self.animation_keys['state'] = 'punch'

		elif self.item:
			self.animation_keys['state'] = self.item.idling_hand_animation_state
		else:
			self.animation_keys['state'] = 'idle'

	def blink(self):
		if self.player.blinking == 1:
			self.image = alphafill(self.image, GET_DAMAGE_BLIKING_COLOR)

	def scale(self):
		try:
			sx, sy = self.scales[self.animation_keys['state']]
		except KeyError:
			sx, sy = None, None

		if sx and sy:
			self.image = relative_scaled_surface(self.image,sx,sy)

			self.rect.width = self.image.get_width()
			self.rect.height = self.image.get_height()

			self.rect.center = self.backup_rect.center

		else:
			if self.rect != self.backup_rect:
				self.rect = self.backup_rect.copy()

	def rotate(self):
		try:
			rotations = self.rotations[self.vector_animation_state]
		except KeyError:
			rotations = None

		if rotations:
			degrees = rotations[int(self.vector_index)]*self.vector_animation_direction*-1
			self.image = pygame.transform.rotate(self.image,degrees)

			self.rect.width = self.image.get_width()
			self.rect.height = self.image.get_height()

	def update_cooldowns(self):
		for cooldown_dict in self.cooldowns.values():
			if isinstance(cooldown_dict, dict):
				for cooldown in cooldown_dict.values():
					cooldown.update()
			else:
				cooldown_dict.update()

		if hasattr(self.item, 'cooldowns'):
			for c in self.item.cooldowns.values():
				if isinstance(c, dict):
					for cooldown in c.values():
						cooldown.update()
				else:
					c.update()

	def previous_variables(self):
		self.last_animation_state = self.animation_keys['state']
		self.last_vector_animation_state = self.vector_animation_state
		self.last_vector_index = self.vector_index

	def update(self, dt):
		self.previous_variables()
		self.update_cooldowns()

		self.update_vector_animation_state()
		self.update_vector_index(dt)
		self.move(dt)

		self.picking()

		self.update_animation_state()
		self.update_frame_index(dt)
		self.animate()
		self.blink()
		self.scale()
		self.rotate()

		self.adjust_positionals_objects_by_rect()
		self.adjust_dimensionals_objects_by_rect()