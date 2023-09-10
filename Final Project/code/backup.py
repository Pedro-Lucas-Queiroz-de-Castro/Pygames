import pygame

from support import *
from settings import *
from times import *
from vectors import *

from superclasses import *

class Player(Animated,pygame.sprite.Sprite):
	def __init__(self, level, pos, animations, joystick, scale_offset, groups, control_config,
		hand_animations):

		animation_keys = {''}
		super().__init__(
			animations=self.get_animations_copy(animations),
			animation_keys=animation_keys,
			
			groups=[groups['updatable'],groups['visible']])

		self.level = level

		self.set_speed_forces()

		self.my_groups = groups

		self.control_config = control_config

		self.scale_offset = scale_offset

		self.source_animations = self.get_animations_copy(animations)
		self.source_hand_animations = self.get_animations_copy(hand_animations)

		self.animations = self.get_animations_copy(animations)
		self.hand_animations = self.get_animations_copy(hand_animations)
		self.scale_graphics()

		self.animation_direction = 'right'
		self.animation_state = list(self.animations[self.animation_direction].keys())[0]

		self.frame_index = 0
		self.animation_speeds = PLAYER_ANIMATION_SPEEDS

		self.image = self.get_animation()[self.frame_index]
		self.rect = self.image.get_rect(**pos)
		self.hitbox = self.rect.copy()

		self.cooldowns = {}
		self.cooldowns['invulnerability'] = Cooldown(900)

		self.joystick = joystick

		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(list(pos.values())[0])
		self.walk_speed = 300
		self.input_acceleration_speed_on_floor = 3
		self.input_deacceleration_speed_on_floor = 3
		self.input_acceleration_speed_in_air = 1.8
		self.input_deacceleration_speed_in_air = 1.8

		self.jump_speed = 600
		self.max_direction_falling_speed = 800
		self.player_falling_animation_change_speeds = PLAYER_FALLING_ANIMATION_CHANGE_SPEEDS

		self.on_floor = False
		self.floor_rect = pygame.Rect(self.hitbox.x,self.hitbox.bottom,self.hitbox.width,2)

		self.on_wall = {'left': False, 'right': False}
		self.wall_rects = {}
		self.wall_rects['left'] = pygame.Rect(self.hitbox.x-2,self.hitbox.top,2,self.hitbox.height)
		self.wall_rects['right'] = pygame.Rect(self.hitbox.right,self.hitbox.top,2,self.hitbox.height)

		# health
		self.health = 10

		self.hands = {}
		self.create_hands()

	def set_speed_forces(self):
		forces = self.level.speed_forces
		self.gravity_speed = forces['gravity']
		self.wind_speed = forces['wind']


	def create_hands(self):
		self.hands['right'] = Hand(
			side='right',
			animations=self.hand_animations,
			animation_direction='right',
			pos={'midleft': self.rect.midright},
			groups=self.my_groups,
			player=self,
			anchor=('midleft','midright',
				(RIGHT_HAND_ANCHOR_OFFSET[0]*self.scale_offset,
				 RIGHT_HAND_ANCHOR_OFFSET[1]*self.scale_offset)))

		self.hands['left'] = Hand(
			side='left',
			animations=self.hand_animations,
			animation_direction='left',
			pos={'midright': self.rect.midleft},
			groups=self.my_groups,
			player=self,
			anchor=('midright','midleft',
				(LEFT_HAND_ANCHOR_OFFSET[0]*self.scale_offset,
				 LEFT_HAND_ANCHOR_OFFSET[1]*self.scale_offset)))

	def check_damage(self):
		for sprite in self.my_groups['damagable']:
			if sprite not in self.hands.values():
				if sprite.hitbox.colliderect(self.hitbox):
					self.get_damage(sprite.get_damage_amount())

	def get_damage(self, amount):
		if not self.cooldowns['invulnerability'].on:
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


	def scale_graphics(self):
		animations_list = [
		(self.animations,PLAYER_DEFAULT_SIZE),
		(self.hand_animations,HAND_DEFAULT_SIZE)]

		for animations, default_size in animations_list:
			for k1, sides in animations.items():
				for k2, frames in sides.items():
					animations[k1][k2] =\
					 scale_list_of_surfaces(frames,
					 	default_size[0]*self.scale_offset,
					 	default_size[1]*self.scale_offset)

	def get_animation(self):
		return self.animations[self.animation_direction][self.animation_state]


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


		return components, controls

	def input(self, components, controls, dt):
		if controls:
			# horizontal movement
			if 'hlaxis' in components:
				left_axis = controls['move'][0] < -DEADZONE
				right_axis = controls['move'][0] > DEADZONE
			else:
				left_axis = False
				right_axis = False

			if 'lhat' in components:
				left_hat = controls['move'][1][0] < 0
				right_hat = controls['move'][1][0] > 0
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

				self.direction.x = tend_to(self.direction.x, -1, speed)
				self.walking_input = -1

			elif right_axis or right_hat:
				speed = input_acceleration_speed + input_deacceleration_speed\
				if self.direction.x >= 0 else input_deacceleration_speed

				self.direction.x = tend_to(self.direction.x, 1, speed)
				self.walking_input = 1

			else:
				self.direction.x = tend_to(self.direction.x, 0, input_deacceleration_speed)

				self.walking_input = 0

			# jump
			if controls['jump']:
				self.jump()

			# hand actions
			if controls['right pick']:
				self.hands['right'].pick()
			elif controls['right poke']:
				self.hands['right'].poke() 

			if controls['left pick']:
				self.hands['left'].pick()
			elif controls['left poke']:
				self.hands['left'].poke()


	def jump(self):
		if self.on_floor:
			self.direction.y = -self.jump_speed

	def apply_gravity(self, dt):
		self.direction.y += self.gravity_speed * dt

	def move_vertical(self, dt):
		self.direction.y = min(self.direction.y,self.max_direction_falling_speed)
		self.pos.y += self.direction.y * dt * self.scale_offset
		self.rect.y = round(self.pos.y)

		self.hitbox.y = self.rect.y


	def move_horizontal(self, dt):
		speeds = self.walk_speed
		wind_speed = self.wind_speed

		if (self.on_wall['left'] and self.wind_speed < 0) or\
		   (self.on_wall['right'] and self.wind_speed > 0):
		   wind_speed = 0

		self.pos.x += (self.direction.x * dt * speeds * self.scale_offset) + wind_speed
		self.rect.x = round(self.pos.x)

		self.hitbox.x = self.rect.x


	def collisions(self, direction):
		sprites_on_floor = []
		sprites_on_wall = {'left': [], 'right': []}

		for sprite in self.my_groups['collidable']:
			match direction:
				case 'horizontal':
					if sprite.hitbox.colliderect(self.hitbox):
						if sprite.old_hitbox.left >= self.old_hitbox.right:
							self.hitbox.right = sprite.hitbox.left
							self.direction.x = 0

						elif sprite.old_hitbox.right <= self.old_hitbox.left:
							self.hitbox.left = sprite.hitbox.right
							self.direction.x = 0

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

						elif sprite.old_hitbox.bottom <= self.old_hitbox.top:
							self.hitbox.top = sprite.hitbox.bottom
							self.direction.y = 0

					self.floor_rect.topleft = self.hitbox.bottomleft

					sprites_on_floor.append(sprite.hitbox.colliderect(self.floor_rect))

					self.on_floor = any(sprites_on_floor)

					if self.on_floor:
						self.direction.y = 0


		self.rect.topleft = self.hitbox.topleft
		self.pos.x, self.pos.y = self.rect.x, self.rect.y


	def update_animation_direction(self):
		if self.walking_input > 0:
			self.animation_direction = 'right'
		elif self.walking_input < 0:
			self.animation_direction = 'left'

	def update_animation_state(self, controls):
		if self.on_floor:
			if self.walking_input != 0:
				self.animation_state = 'walk'
			else:
				self.animation_state = 'idle'
		else:
			if self.direction.y <= 0:
				self.animation_state = 'rising'
			else:
				if self.direction.y <= self.player_falling_animation_change_speeds[0]:
					self.animation_state = 'falling 0'
				elif self.direction.y <= self.player_falling_animation_change_speeds[1]:
					self.animation_state = 'falling 1'
				elif self.direction.y <= self.player_falling_animation_change_speeds[2]:
					self.animation_state = 'falling 2'
				else:
					self.animation_state = 'falling 3'

	def update_frame_index(self, dt):
		self.frame_index += self.animation_speeds[self.animation_state] * dt

		if self.animation_state != self.last_animation_state:
			self.frame_index = 0
		
		reseted = False
		if self.frame_index >= len(self.get_animation()):
			self.frame_index = 0
			reseted = True

		if reseted:
			pass

	def animate(self):
		self.image = self.get_animation()[int(self.frame_index)]


	def previous_variables(self):
		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.last_frame_index = self.frame_index
		self.last_animation_state = self.animation_state

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

		components, controls = self.get_controls()

		self.input(components, controls, dt)

		# if self.direction.magnitude() != 0:
		# 	self.direction.normalize_ip()

		self.move_horizontal(dt)
		self.collisions('horizontal')
		
		self.apply_gravity(dt)
		self.move_vertical(dt)
		self.collisions('vertical')

		self.check_damage()

		self.update_animation_direction()
		self.update_animation_state(controls)
		self.update_frame_index(dt)

		self.animate()
		self.blink()


	def get_display_info(self, key):
		self.info = {
		'on floor': f'on floor: {self.on_floor}',
		'on wall': f'on wall: l-{self.on_wall["left"]}, r-{self.on_wall["right"]}',
		'direction': (self.direction.x, self.direction.y),
		'position': self.rect.topleft,
		'scale offset': self.scale_offset,
		'damage sprites': f'damage sprites: {len(self.my_groups["damagable"].sprites())}',
		'gravity speed': f'gravity speed: {self.gravity_speed}',
		'wind speed': f'wind speed: {self.wind_speed}'}

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

	def get_animations_copy(self, animations):
		animations_copy = {}
		surfaces = []

		for k1, sides in animations.items():
			animations_copy[k1] = {}
			for k2, frames in sides.items():
				animations_copy[k1][k2] = [surface.copy() for surface in frames]				

		return animations_copy



class Hand(pygame.sprite.Sprite):
	def __init__(self, side, animations, animation_direction, pos, groups, player, anchor):
		super().__init__(groups['visible'],groups['updatable'])

		self.side = side
		self.my_groups = groups

		self.player = player

		self.animations = animations

		self.animation_direction = animation_direction
		self.animation_state = list(self.animations[self.animation_direction].keys())[0]

		self.frame_index = 0
		self.animation_speeds = HAND_ANIMATION_SPEEDS

		self.image = self.get_animation()[self.frame_index]
		self.rect = self.image.get_rect(**pos)
		self.backup_rect = self.rect.copy()
		self.hitbox = self.rect.copy()

		self.anchor = anchor

		self.vector_animation_direction = 1 if animation_direction == 'right' else -1

		self.vector_animations = HAND_VECTOR_ANIMATIONS
		self.vector_animation_state = list(self.vector_animations.keys())[0]

		self.vector_index = 0
		self.vector_magnitudes_speeds = HAND_VECTOR_MAGNITUDES_SPEEDS
		self.vector_animations_speeds = HAND_VECTOR_ANIMATIONS_SPEEDS
		self.animation_vectors_sum = pygame.math.Vector2()

		# ACTIONS
		self.poking = False
		self.picking = False

		# COOLDOWNS
		self.cooldowns = {}
		self.cooldowns['pick'] = Cooldown(300)

		self.scales = HAND_SCALES
		self.rotations = HAND_ROTATIONS

	def get_animation(self):
		return self.animations[self.animation_direction][self.animation_state]

	def get_vector_animation(self):
		return self.vector_animations[self.vector_animation_state]

	def get_vector_magnitude_speed(self):
		magnitude_speed = self.vector_magnitudes_speeds[self.vector_animation_state]
		return magnitude_speed*self.player.scale_offset

	def get_vector_animation_speed(self):
		return self.vector_animations_speeds[self.vector_animation_state]

	def get_player_pos(self):
		return getattr(self.player.rect, self.anchor[1])


	def poke(self):
		if not self.poking:
			self.poking = True
			self.my_groups['damagable'].add(self)

	def pick(self):
		if not self.cooldowns['pick'].on:
			self.picking = True


	def update_vector_animation_state(self):
		if self.picking:
			self.vector_animation_state = 'pick'
		elif self.poking:
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
			self.vector_index = 0
			reseted = True

		if reseted:
			self.reset_actions()

	def reset_actions(self):
		self.animation_vectors_sum = pygame.math.Vector2()

		if self.picking:
			self.picking = False
			self.cooldowns['pick'].start()

		if self.poking:
			self.poking = False
			self.my_groups['damagable'].remove(self)


	def move(self, dt):
		player_anchor = pygame.math.Vector2(self.get_player_pos())+pygame.math.Vector2(self.anchor[2])

		magnitude_speed = self.get_vector_magnitude_speed()
		vector = self.get_vector_animation()[int(self.vector_index)].copy()
		vector.x = vector.x * self.vector_animation_direction
		vector = vector.normalize() if vector.magnitude() != 0 else vector

		self.animation_vectors_sum += vector * magnitude_speed * dt 

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
		if self.picking:
			self.animation_state = 'pick'
		elif self.poking:
			self.animation_state = 'punch'
		else:
			self.animation_state = 'idle'

	def update_frame_index(self, dt):
		self.frame_index += self.animation_speeds[self.animation_state] * dt

		if self.animation_state != self.last_animation_state:
			self.frame_index = 0
		
		reseted = False
		if self.frame_index >= len(self.get_animation()):
			self.frame_index = 0
			reseted = True

		if reseted:
			pass

	def animate(self):
		self.image = self.get_animation()[int(self.frame_index)]

	def blink(self):
		if self.player.blinking == 1:
			self.image = alphafill(self.image, GET_DAMAGE_BLIKING_COLOR)

	def scale(self):
		try:
			sx, sy = self.scales[self.animation_state]
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

	def previous_variables(self):
		self.last_animation_state = self.animation_state
		self.last_vector_animation_state = self.vector_animation_state
		self.last_vector_index = self.vector_index

	def update(self, dt):
		self.previous_variables()
		self.update_cooldowns()

		self.update_vector_animation_state()
		self.update_vector_index(dt)
		self.move(dt)

		self.update_animation_state()
		self.update_frame_index(dt)
		self.animate()
		self.blink()
		self.scale()
		self.rotate()

		self.adjust_positionals_objects_by_rect()
		self.adjust_dimensionals_objects_by_rect()